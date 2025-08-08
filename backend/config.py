import os
from typing import List

class Config:
    """Configuration class for security and application settings"""
    
    # API Settings
    API_TITLE = "Image Converter API"
    API_VERSION = "1.0.0"
    
    # Security Settings
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB default
    MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", 30))
    
    # Allowed file types
    ALLOWED_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.tif'
    }
    
    ALLOWED_MIME_TYPES = {
        'image/jpeg', 'image/png', 'image/gif', 'image/webp', 
        'image/bmp', 'image/tiff'
    }
    
    # CORS Settings
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:10000",
        # Add your production domain here
        os.getenv("FRONTEND_URL", "https://your-domain.com")
    ]
    
    # Rate Limiting
    RATE_LIMIT_WINDOW = 60  # seconds
    RATE_LIMIT_MAX_REQUESTS = MAX_REQUESTS_PER_MINUTE
    
    # Security Headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Cache-Control": "no-cache, no-store, must-revalidate"
    }
    
    # File Processing
    MAX_IMAGE_DIMENSIONS = (8000, 8000)  # Maximum width/height
    MIN_QUALITY = 10
    MAX_QUALITY = 95
    
    # Validation
    MIN_SIZE_KB = 10
    MAX_SIZE_KB = 1000
    
    @classmethod
    def get_cors_origins(cls) -> List[str]:
        """Get CORS origins based on environment"""
        if os.getenv("ENVIRONMENT") == "development":
            return cls.ALLOWED_ORIGINS + ["*"]
        return cls.ALLOWED_ORIGINS

# Environment-specific configurations
class DevelopmentConfig(Config):
    DEBUG = True
    ALLOW_CREDENTIALS = True

class ProductionConfig(Config):
    DEBUG = False
    ALLOW_CREDENTIALS = False

# Get current config based on environment
def get_config():
    env = os.getenv("ENVIRONMENT", "development")
    if env == "production":
        return ProductionConfig()
    return DevelopmentConfig()
