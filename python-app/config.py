import os
from typing import Optional

class Config:
    """Application configuration"""
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "4445"))
    
    # Whisper model settings
    WHISPER_DEVICE: str = os.getenv("WHISPER_DEVICE", "cpu")
    WHISPER_COMPUTE_TYPE: str = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
    
    # CORS settings
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Default language
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "en")
    DEFAULT_WHISPER_MODEL: str = os.getenv("DEFAULT_WHISPER_MODEL", "base")
    
    # Temp file settings
    TEMP_FILE_SUFFIX: str = os.getenv("TEMP_FILE_SUFFIX", ".wav")
    
    # API settings
    API_TITLE: str = os.getenv("API_TITLE", "WhisperX Assistant API")
    API_VERSION: str = os.getenv("API_VERSION", "1.0.0")
    
    # Model storage settings
    ENABLE_EXTERNAL_STORAGE: bool = os.getenv("ENABLE_EXTERNAL_STORAGE", "false").lower() in ("true", "1", "yes", "on")
    MODELS_CACHE_DIR: Optional[str] = os.getenv("MODELS_CACHE_DIR", None)
    MODELS_VOLUME_PATH: str = os.getenv("MODELS_VOLUME_PATH", "/app/models")
    
    # HuggingFace cache settings (enhanced)
    HF_HOME: Optional[str] = os.getenv("HF_HOME", None)
    TRANSFORMERS_CACHE: Optional[str] = os.getenv("TRANSFORMERS_CACHE", None)
    
    @classmethod
    def get_effective_cache_dir(cls) -> Optional[str]:
        """Get the effective cache directory based on configuration priority"""
        if cls.ENABLE_EXTERNAL_STORAGE:
            if cls.MODELS_CACHE_DIR:
                return cls.MODELS_CACHE_DIR
            elif cls.MODELS_VOLUME_PATH and os.path.exists(cls.MODELS_VOLUME_PATH):
                return cls.MODELS_VOLUME_PATH
        
        # Fallback to HuggingFace defaults
        return cls.HF_HOME or cls.TRANSFORMERS_CACHE

config = Config()