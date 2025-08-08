from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from io import BytesIO
import uvicorn
import os
import time
from typing import Dict, Set
import hashlib

app = FastAPI(title="Image Converter API", version="1.0.0")

# Security configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.tif'}
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp', 'image/tiff'}

# Rate limiting storage (in production, use Redis)
request_timestamps: Dict[str, list] = {}
MAX_REQUESTS_PER_MINUTE = 30

# Add CORS middleware with more restrictive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000", 
        "https://your-domain.com"  # Replace with your actual domain
    ],
    allow_credentials=False,  # Changed to False for security
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

def validate_file(file: UploadFile) -> bool:
    """Validate uploaded file for security"""
    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        return False
    
    # Check file extension
    if file.filename:
        file_ext = os.path.splitext(file.filename.lower())[1]
        if file_ext not in ALLOWED_EXTENSIONS:
            return False
    
    # Check MIME type
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        return False
    
    return True

def check_rate_limit(client_ip: str) -> bool:
    """Simple rate limiting implementation"""
    current_time = time.time()
    
    if client_ip not in request_timestamps:
        request_timestamps[client_ip] = []
    
    # Remove timestamps older than 1 minute
    request_timestamps[client_ip] = [
        ts for ts in request_timestamps[client_ip] 
        if current_time - ts < 60
    ]
    
    # Check if too many requests
    if len(request_timestamps[client_ip]) >= MAX_REQUESTS_PER_MINUTE:
        return False
    
    # Add current request
    request_timestamps[client_ip].append(current_time)
    return True

def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Security middleware for all requests"""
    client_ip = get_client_ip(request)
    
    # Rate limiting
    if not check_rate_limit(client_ip):
        return HTTPException(
            status_code=429, 
            detail="Too many requests. Please try again later."
        )
    
    # Add security headers
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response

def adjust_image(img, target_size_kb):
    # Convert image to RGB mode to ensure compatibility with JPEG 
    print(f"Original image mode: {img.mode}")
    
    # Handle different image modes
    if img.mode == 'LA':
        # Convert LA (grayscale with alpha) to RGB
        img = img.convert('RGB')
    elif img.mode == 'RGBA':
        # Convert RGBA to RGB with white background
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1])
        img = background
    elif img.mode == 'P':
        # Convert palette mode to RGB
        img = img.convert('RGB')
    elif img.mode != 'RGB':
        # Convert any other mode to RGB
        img = img.convert('RGB')
    
    print(f"Converted image mode: {img.mode}")
    
    quality = 95
    output_io = BytesIO()

    while True:
        img.save(output_io, format="JPEG", quality=quality, optimize=True)
        size_kb = len(output_io.getvalue()) / 1024

        if abs(size_kb - target_size_kb) <= 2:
            break

        if size_kb > target_size_kb:
            if quality > 10:
                quality -= 5
            else:
                width, height = img.size
                img = img.resize((int(width * 0.9), int(height * 0.9)), Image.LANCZOS)
                quality = 95
        else:
            width, height = img.size
            img = img.resize((int(width * 1.1), int(height * 1.1)), Image.LANCZOS)
            quality = min(quality + 5, 95)

        output_io = BytesIO()  # reset buffer

    output_io.seek(0)
    return output_io

@app.post("/process-image/")
async def process_image(
    request: Request,
    file: UploadFile = File(...), 
    size: int = Form(100)
):
    """Process image with size optimization"""
    try:
        # Security validation
        if not validate_file(file):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type or size. Please upload a valid image file (max 10MB)."
            )
        
        # Validate size parameter
        if size < 10 or size > 1000:
            raise HTTPException(
                status_code=400, 
                detail="Target size must be between 10 and 1000 KB."
            )
        
        img = Image.open(file.file)
        processed_img = adjust_image(img, size)
        
        # Generate secure filename
        safe_filename = f"processed_{hashlib.md5(file.filename.encode()).hexdigest()[:8]}.jpg"
        
        return StreamingResponse(
            processed_img, 
            media_type="image/jpeg", 
            headers={
                "Content-Disposition": f"attachment; filename={safe_filename}",
                "Cache-Control": "no-cache, no-store, must-revalidate"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing image: {str(e)}"
        )

@app.post("/convert-image/")
async def convert_image(
    request: Request,
    file: UploadFile = File(...), 
    format: str = Form(...)
):
    """Convert image to different format"""
    try:
        # Security validation
        if not validate_file(file):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type or size. Please upload a valid image file (max 10MB)."
            )
        
        img = Image.open(file.file)
        
        # Map user-friendly format to PIL format
        format_map = {
            'jpg': 'JPEG', 'jpeg': 'JPEG',
            'png': 'PNG',
            'gif': 'GIF',
            'webp': 'WEBP',
            'bmp': 'BMP',
            'tiff': 'TIFF', 'tif': 'TIFF',
        }
        
        fmt = format_map.get(format.lower())
        if not fmt:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported format: {format}"
            )
        
        # Convert mode if needed
        if fmt in ['JPEG', 'BMP', 'WEBP'] and img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        output_io = BytesIO()
        img.save(output_io, format=fmt)
        output_io.seek(0)
        
        # Set correct media type
        media_types = {
            'JPEG': 'image/jpeg',
            'PNG': 'image/png',
            'GIF': 'image/gif',
            'WEBP': 'image/webp',
            'BMP': 'image/bmp',
            'TIFF': 'image/tiff',
        }
        
        media_type = media_types.get(fmt, 'application/octet-stream')
        ext = fmt.lower() if fmt != 'JPEG' else 'jpg'
        
        # Generate secure filename
        safe_filename = f"converted_{hashlib.md5(file.filename.encode()).hexdigest()[:8]}.{ext}"
        
        return StreamingResponse(
            output_io, 
            media_type=media_type, 
            headers={
                "Content-Disposition": f"attachment; filename={safe_filename}",
                "Cache-Control": "no-cache, no-store, must-revalidate"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error converting image: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)