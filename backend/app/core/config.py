"""
Application Configuration
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "CallGuard AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENV: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./callguard.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI/ML Models
    WHISPER_MODEL: str = "base"
    SPACY_MODEL: str = "en_core_web_sm"
    FRAUD_MODEL_PATH: str = "./models/fraud_classifier.joblib"
    
    # Audio Settings
    MAX_AUDIO_DURATION_SECONDS: int = 600
    SUPPORTED_AUDIO_FORMATS: str = "wav,mp3,ogg,flac,m4a"
    SAMPLE_RATE: int = 16000
    
    # Detection Thresholds
    SPAM_THRESHOLD: float = 0.6
    FRAUD_THRESHOLD: float = 0.7
    PHISHING_THRESHOLD: float = 0.65
    ROBOCALL_THRESHOLD: float = 0.75
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    @property
    def supported_formats_list(self) -> List[str]:
        return self.SUPPORTED_AUDIO_FORMATS.split(",")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
