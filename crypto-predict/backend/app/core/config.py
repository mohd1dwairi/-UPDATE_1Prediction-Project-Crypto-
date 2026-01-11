from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    PROJECT_NAME: str = "Crypto Price Prediction System"
    VERSION: str = "1.0.0"
    ENV: str = "development" # يمكن تغييرها لـ production لاحقاً

    DATABASE_URL: str 
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 

    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = ConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding='utf-8',
        extra="ignore"  
    )
@lru_cache()
def get_settings():
    
    return Settings()