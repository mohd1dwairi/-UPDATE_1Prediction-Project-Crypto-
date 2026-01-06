import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings

# استيراد أدوات قاعدة البيانات والجدولة
from app.db.session import engine
from app.db.models import Base
from app.workers.scheduler import start_scheduler

settings = get_settings()

app = FastAPI(
    title="Crypto Price Prediction API",
    description="Backend for crypto prediction & sentiment analysis project",
    version="1.0.0",
)
origins = [    
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173", # أضف هذا إذا كنت تستخدم Vite  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # استخدام القائمة المحددة بدلاً من "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

# ========================
# Routers
# ========================
from app.routers import auth_router, prices, sentiment, predict, health

app.include_router(auth_router.router, prefix="/api")
app.include_router(prices.router, prefix="/api")
app.include_router(sentiment.router, prefix="/api")
app.include_router(predict.router, prefix="/api")
app.include_router(health.router, prefix="/api")

@app.on_event("startup")
def on_startup():
    """
    تنفيذ العمليات المطلوبة عند بدء تشغيل السيرفر
    """
    # 1. إنشاء الجداول تلقائياً إذا لم تكن موجودة
    Base.metadata.create_all(bind=engine)
    
    # 2. تشغيل الـ Scheduler لجلب البيانات (مع التحقق لتجنب التكرار)
    if os.getenv("RUN_MAIN") == "true" or os.getenv("TESTING") != "true":
        start_scheduler()

# ========================
# Root
# ========================
@app.get("/")
def root():
    return {
        "message": "🚀 Backend is running successfully!",
        "environment": settings.ENV,
        "database": "Connected",
    }

    from app.routers.admin_reports import admin_reports # استيراد الراوتر الجديد
# ...
app.include_router(admin_reports.router, prefix="/api")