from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Sentiment Analysis API"
    APP_VERSION: str = "1.0.0"
    INSTANCE_ID: str = os.getenv("INSTANCE_ID", "unknown")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@postgres:5432/sentiment_db"
    )
    
    # Model
    MODEL_PATH: str = os.getenv("MODEL_PATH", "/app/models/sentiment_model.pkl")
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()