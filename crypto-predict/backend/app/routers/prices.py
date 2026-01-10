from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session 
from sqlalchemy import func
from pydantic import BaseModel
import pandas as pd
import io
from datetime import datetime, timezone
from typing import List, Optional

from app.db.session import get_db
from app.db import models
from app.services.prediction_service import generate_predictions # استيراد الخدمة الحقيقية
from app.core.security import get_current_user
from app.schemas.prediction_schema import PredictionResponse

router = APIRouter(prefix="/prices", tags=["Prices"])

# 1. نموذج استلام البيانات يدوياً
class ManualDataInput(BaseModel):
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    avg_sentiment: Optional[float] = 0.0

# ============================================================
# 1. جلب البطاقات العلوية (Top Assets)
# ============================================================
@router.get("/top-assets")
def get_top_assets(db: Session = Depends(get_db)):
    subquery = db.query(
        models.Candle.asset_id,
        func.max(models.Candle.timestamp).label("max_ts")
    ).group_by(models.Candle.asset_id).subquery()

    latest_prices = db.query(models.Candle, models.CryptoAsset.symbol).join(
        subquery, (models.Candle.asset_id == subquery.c.asset_id) & 
                  (models.Candle.timestamp == subquery.c.max_ts)
    ).join(models.CryptoAsset, models.Candle.asset_id == models.CryptoAsset.asset_id).all()

    return [
        {
            "id": r.Candle.asset_id, 
            "name": r.symbol.upper(), 
            "price": float(r.Candle.close), 
            "change": 0.5
        } for r in latest_prices
    ]

# ============================================================
# 2. البيانات التاريخية (Historical OHLCV)
# ============================================================
@router.get("/{symbol}")
def get_historical_ohlcv(symbol: str, db: Session = Depends(get_db)):
    asset = db.query(models.CryptoAsset).filter(func.lower(models.CryptoAsset.symbol) == symbol.lower()).first()
    if not asset: 
        raise HTTPException(status_code=404, detail="Asset not found")
    
    data = db.query(models.Candle).filter(models.Candle.asset_id == asset.asset_id).order_by(models.Candle.timestamp.desc()).limit(150).all()
    return sorted([{"x": c.timestamp, "y": [float(c.open), float(c.high), float(c.low), float(c.close)]} for c in data], key=lambda x: x['x'])

# ============================================================
# 3. محرك التوقع الذكي (استدعاء الخدمة الحقيقية)
# ============================================================
@router.get("/predict/{symbol}", response_model=List[PredictionResponse])
def get_ai_prediction(
    symbol: str, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. جلب المرجع للعملة
    asset = db.query(models.CryptoAsset).filter(func.lower(models.CryptoAsset.symbol) == symbol.lower()).first()
    if not asset: 
        raise HTTPException(status_code=404, detail="Asset not found")

    # 2. استدعاء خدمة التوقعات التي ترتبط بموديل XGB-LSTM
    # قمنا بنقل كل التعقيد داخل هذه الدالة
    predictions = generate_predictions(
        db=db,
        asset_id=asset.asset_id,
        timeframe_id=1, # 1h
        user_id=current_user.user_id
    )

    if not predictions:
        raise HTTPException(
            status_code=400, 
            detail="Insufficient data for AI prediction. Please upload more historical data (48h required)."
        )

    return predictions

# ============================================================
# 4. إضافة البيانات يدوياً (حل مشكلة الـ 405)
# ============================================================
@router.post("/add-data")
def add_manual_data(data: ManualDataInput, db: Session = Depends(get_db)):
    try:
        sym = data.symbol.upper()
        if sym == "DOGE": sym = "DOG"

        asset = db.query(models.CryptoAsset).filter(func.lower(models.CryptoAsset.symbol) == sym.lower()).first()
        if not asset: raise HTTPException(status_code=404, detail="Asset not found")

        current_time = datetime.now(timezone.utc)

        # إضافة السعر والمشاعر معاً لضمان وجود بيانات للموديل
        new_candle = models.Candle(asset_id=asset.asset_id, timeframe_id=1, timestamp=current_time, open=data.open, high=data.high, low=data.low, close=data.close, volume=data.volume, exchange="Manual_Input")
        db.add(new_candle)

        new_sentiment = models.Sentiment(asset_id=asset.asset_id, timestamp=current_time, avg_sentiment=data.avg_sentiment, sent_count=1, source="Manual", pos_count=1, neg_count=0, neu_count=0, pos_ratio=1.0, neg_ratio=0.0, neu_ratio=0.0, has_news=0)
        db.add(new_sentiment)
        
        db.commit()
        return {"status": "success", "message": "Signal injected!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))