import os
from datetime import timedelta
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API Configuration
    API_TITLE: str = "Cheque Tally Agent"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Production-grade Cheque Reconciliation System"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    
    # Supabase
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # LLM
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL: str = "mixtral-8x7b-32768"
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_TOKENS: int = 4000
    
    # Application
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
