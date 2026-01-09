import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.db.session import engine, SessionLocal
from app.db import models 
from app.workers.scheduler import start_scheduler

# استيراد الـ Routers الأساسية للنظام
#
from app.routers import auth_router, prices, sentiment, predict, health, admin_reports

settings = get_settings()

app = FastAPI(
    title="Crypto Price Prediction API",
    description="Backend for crypto prediction & sentiment analysis project",
    version="1.1.0",
)

# إعدادات الـ CORS لضمان اتصال الـ React (Frontend) بالسيرفر
#
origins = [    
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173", # Vite
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

# تسجيل جميع المسارات في النظام تحت بادئة /api
#
app.include_router(auth_router.router, prefix="/api")
app.include_router(prices.router, prefix="/api")
app.include_router(sentiment.router, prefix="/api")
app.include_router(predict.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(admin_reports.router, prefix="/api")

@app.on_event("startup")
def on_startup():
    """
    حدث بداية التشغيل: يقوم بتهيئة قاعدة البيانات وحقن البيانات الأساسية.
   
    """
    # 1. إنشاء الجداول بناءً على الموديلات المحدثة (ERD)
    #
    models.Base.metadata.create_all(bind=engine)
    
    # 2. حقن البيانات الأساسية (Seeding) لضمان عمل الروابط (Foreign Keys)
    #
    db = SessionLocal()
    try:
        # فحص وإضافة العملات إذا كان الجدول فارغاً
        if not db.query(models.CryptoAsset).first():
            print("🚀 Initializing Crypto Assets in database...")
            assets = [
                models.CryptoAsset(symbol="BTC", name="Bitcoin"),
                models.CryptoAsset(symbol="ETH", name="Ethereum"),
                models.CryptoAsset(symbol="BNB", name="Binance Coin"),
                models.CryptoAsset(symbol="SOL", name="Solana"),
                models.CryptoAsset(symbol="DOG", name="Dogecoin")
            ]
            db.add_all(assets)
            
            # إضافة الإطار الزمني 1h اللازم لربط الشموع والتوقعات
            #
            if not db.query(models.Timeframe).filter(models.Timeframe.code == "1h").first():
                db.add(models.Timeframe(code="1h", description="Hourly Timeframe"))
            
            db.commit()
            print("✅ Database Seeding completed successfully!")
    except Exception as e:
        print(f"⚠️ Seeding Error: {e}")
        db.rollback()
    finally:
        db.close()

    # 3. تشغيل المجدول (Scheduler) للمهام الخلفية
    #
    if os.getenv("RUN_MAIN") == "true" or os.getenv("TESTING") != "true":
        start_scheduler()

@app.get("/")
def root():
    """
    نقطة النهاية الرئيسية للتأكد من حالة السيرفر.
    """
    return {
        "status": "Online",
        "message": "🚀 Backend is running with the updated ERD structure",
        "database": "Connected & Seeded"
    }