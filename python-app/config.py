import os
from typing import Optional

class Config:
    """Application configuration"""
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "4445"))
    
    # Whisper model settings
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
    WHISPER_DEVICE: str = os.getenv("WHISPER_DEVICE", "cpu")
    WHISPER_COMPUTE_TYPE: str = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
    
    # CORS settings
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Default language
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "en")
    
    # Temp file settings
    TEMP_FILE_SUFFIX: str = os.getenv("TEMP_FILE_SUFFIX", ".wav")
    
    # API settings
    API_TITLE: str = os.getenv("API_TITLE", "WhisperX Assistant API")
    API_VERSION: str = os.getenv("API_VERSION", "1.0.0")

config = Config()