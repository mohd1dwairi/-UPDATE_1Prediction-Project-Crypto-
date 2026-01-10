import os
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

# استيراد إعدادات قاعدة البيانات والموديلات
from app.db import models
from app.db.session import engine, SessionLocal, get_db
from app.core.config import get_settings
from app.routers import auth_router, prices, sentiment, predict, health, admin_reports

app = FastAPI(title="Crypto Prediction System - Data Porter")

# --- إعدادات CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

# --- تسجيل المسارات ---
app.include_router(auth_router.router, prefix="/api")
app.include_router(prices.router, prefix="/api")

# ============================================================
# 📥 الوظيفة الكبرى: رفع بيانات الأسعار والمشاعر معاً
# ============================================================

@app.post("/api/admin/upload-dataset", tags=["Data Import Tool"])
async def upload_full_dataset(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    ارفع ملف CSV (dataset_ohlcv_with_market_sentiment)
    سيقوم الكود بتوزيعه على جدولي Candles و Sentiments تلقائياً
    """
    try:
        # 1. قراءة الملف باستخدام pandas
        df = pd.read_csv(file.file)
        
        # التأكد من وجود الأعمدة المطلوبة
        required_cols = ['open_time', 'symbol', 'open', 'close', 'avg_sentiment']
        if not all(col in df.columns for col in required_cols):
            raise HTTPException(status_code=400, detail="الملف ينقصه أعمدة أساسية!")

        # 2. تجهيز العملات والفترات (Lookups)
        # سنجلب ID الـ Timeframe الخاص بالساعة '1h'
        tf = db.query(models.Timeframe).filter(models.Timeframe.code == "1h").first()
        if not tf:
            tf = models.Timeframe(code="1h", description="Hourly")
            db.add(tf)
            db.commit()
            db.refresh(tf)

        # 3. معالجة البيانات وتحويلها لتنسيق قاعدة البيانات
        candles_to_add = []
        sentiments_to_add = []

        # تحويل الرموز (Symbols) لـ IDs
        symbol_map = {s.symbol.lower(): s.asset_id for s in db.query(models.CryptoAsset).all()}

        for _, row in df.iterrows():
            sym = str(row['symbol']).lower()
            
            # إذا العملة مش موجودة بجدول CryptoAsset، بنضيفها
            if sym not in symbol_map:
                new_asset = models.CryptoAsset(symbol=sym.upper(), name=sym.upper())
                db.add(new_asset)
                db.commit()
                db.refresh(new_asset)
                symbol_map[sym] = new_asset.asset_id

            asset_id = symbol_map[sym]

            # تجهيز بيانات الشموع (Candles)
            candles_to_add.append({
                "asset_id": asset_id,
                "timeframe_id": tf.timeframe_id,
                "timestamp": row['open_time'],
                "open": row['open'],
                "high": row['high'],
                "low": row['low'],
                "close": row['close'],
                "volume": row['volume'],
                "exchange": "Binance" # افتراضي
            })

            # تجهيز بيانات المشاعر (Sentiments)
            if row['sent_count'] > 0: # بنضيف مشاعر فقط إذا كان في داتا
                sentiments_to_add.append({
                    "asset_id": asset_id,
                    "timestamp": row['open_time'],
                    "avg_sentiment": row['avg_sentiment'],
                    "sent_count": row['sent_count'],
                    "pos_count": row['pos_count'],
                    "neg_count": row['neg_count'],
                    "source": "Market Data"
                })

        # 4. الحفظ الجماعي (Bulk Insert) للسرعة
        db.bulk_insert_mappings(models.Candle, candles_to_add)
        db.bulk_insert_mappings(models.Sentiment, sentiments_to_add)
        
        db.commit()
        return {
            "status": "Success",
            "message": f"تم رفع {len(candles_to_add)} سجل أسعار و {len(sentiments_to_add)} سجل مشاعر بنجاح!"
        }

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"حدث خطأ أثناء المعالجة: {str(e)}")

# --- باقي كود الـ Startup والـ Root كما هو ---
@app.get("/")
def root():
    return {"message": "Server is running, go to /docs to upload your file"}