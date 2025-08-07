from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from io import BytesIO
import uvicorn

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
async def process_image(file: UploadFile = File(...), size: int = Form(100)):
    try:
        img = Image.open(file.file)
        processed_img = adjust_image(img, size)
        return StreamingResponse(processed_img, media_type="image/jpeg", headers={
            "Content-Disposition": f"attachment; filename=processed_{file.filename}"
        })
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)