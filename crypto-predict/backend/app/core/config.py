from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache

# تحديد مسار المجلد الرئيسي للمشروع للوصول لملف .env
#
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    # --- معلومات المشروع ---
    PROJECT_NAME: str = "Crypto Price Prediction System"
    VERSION: str = "1.0.0"
    ENV: str = "development" # يمكن تغييرها لـ production لاحقاً

    # --- إعدادات قاعدة البيانات (PostgreSQL) ---
    #
    DATABASE_URL: str 
    
    # --- إعدادات الحماية والتشفير (JWT) ---
    #
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # يوم واحد

    # --- إعدادات محرك السرعة (Redis) ---
    # نضع قيمة افتراضية في حال لم تكن موجودة في .env
    #
    REDIS_URL: str = "redis://localhost:6379/0"

    # إعدادات Pydantic v2 للتعامل مع ملف البيئة
    model_config = ConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding='utf-8',
        extra="ignore"  # تجاهل أي متغيرات زائدة في ملف .env
    )

@lru_cache()
def get_settings():
    """
    استخدام lru_cache لضمان تحميل الإعدادات مرة واحدة فقط في الذاكرة
    لتحسين أداء النظام.
    """
    return Settings()