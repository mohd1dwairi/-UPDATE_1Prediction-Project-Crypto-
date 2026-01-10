from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session 
from sqlalchemy import func
import pandas as pd
import io
from datetime import datetime, timedelta, timezone
from typing import List

from app.db.session import get_db
from app.db import models
from app.services.inference_service import inference_engine
from app.core.security import get_current_user
from app.schemas.prediction_schema import PredictionResponse

# تعريف الـ router ببادئة /prices
router = APIRouter(prefix="/prices", tags=["Prices"])

# 1. جلب البطاقات العلوية (تم إعادتها لحل الـ 404)
@router.get("/top-assets")
def get_top_assets(db: Session = Depends(get_db)):
    subquery = db.query(
        models.Candle.asset_id,
        func.max(models.Candle.timestamp).label("max_ts")
    ).group_by(models.Candle.asset_id).subquery()

    latest_prices = db.query(models.Candle, models.CryptoAsset.symbol).join(
        subquery, (models.Candle.asset_id == subquery.c.asset_id) & 
                  (models.Candle.timestamp == subquery.c.max_ts)
    ).join(models.CryptoAsset, models.Candle.asset_id == models.CryptoAsset.asset_id).distinct(models.Candle.asset_id).all()

    return [{"id": r.Candle.asset_id, "name": r.symbol.upper(), "price": float(r.Candle.close), "change": 0.5} for r in latest_prices]

# 2. البيانات التاريخية (تم إعادتها لحل الـ 404)
@router.get("/{symbol}")
def get_historical_ohlcv(symbol: str, db: Session = Depends(get_db)):
    asset = db.query(models.CryptoAsset).filter(models.CryptoAsset.symbol == symbol.upper()).first()
    if not asset: raise HTTPException(status_code=404, detail="Asset not found")
    data = db.query(models.Candle).filter(models.Candle.asset_id == asset.asset_id).order_by(models.Candle.timestamp.desc()).limit(150).all()
    return sorted([{"x": c.timestamp, "y": [float(c.open), float(c.high), float(c.low), float(c.close)]} for c in data], key=lambda x: x['x'])

# 3. محرك التوقع الذكي (حل مشكلة الـ 500)
@router.get("/predict/{symbol}", response_model=List[PredictionResponse])
def get_ai_prediction(
    symbol: str, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        # 1. جلب المرجع للعملة
        asset = db.query(models.CryptoAsset).filter(models.CryptoAsset.symbol == symbol.upper()).first()
        if not asset: 
            raise HTTPException(status_code=404, detail="Asset not found")

        # 2. جلب البيانات (آخر 48 ساعة)
        query_results = db.query(models.Candle, models.Sentiment).join(
            models.Sentiment, 
            (models.Candle.asset_id == models.Sentiment.asset_id) & 
            (models.Candle.timestamp == models.Sentiment.timestamp)
        ).filter(models.Candle.asset_id == asset.asset_id).order_by(models.Candle.timestamp.desc()).limit(48).all()

        if len(query_results) < 48: 
            raise HTTPException(status_code=400, detail="Insufficient data (48h needed).")

        # 3. تجهيز البيانات
        feature_data = []
        for c, s in query_results:
            feature_data.append({
                "open": float(c.open), "high": float(c.high), "low": float(c.low), 
                "close": float(c.close), "volume": float(c.volume),
                "avg_sentiment": s.avg_sentiment if s.avg_sentiment else 0.0,
                "sent_count": s.sent_count if s.sent_count else 0,
                "pos_count": s.pos_count if s.pos_count else 0,
                "neg_count": s.neg_count if s.neg_count else 0,
                "neu_count": s.neu_count if s.neu_count else 0,
                "pos_ratio": s.pos_ratio if s.pos_ratio else 0.0,
                "neg_ratio": s.neg_ratio if s.neg_ratio else 0.0,
                "neu_ratio": s.neu_ratio if s.neu_ratio else 0.0,
                "has_news": s.has_news if s.has_news else 0
            })

        df_input = pd.DataFrame(feature_data)

        # 🚀 الخطوة السحرية: ملء أي NaN بـ 0 لضمان عدم انهيار الموديل
        df_input.fillna(0, inplace=True)

        # 4. استدعاء الموديل
        prediction_result = inference_engine.predict(df_input)

        # 5. حفظ التوقعات وتجهيز الرد
        last_candle = query_results[0][0]
        future_results = []
        for i in range(1, 6):
            simulated_time = last_candle.timestamp + timedelta(hours=i)
            predicted_val = float(last_candle.close) * (1 + (prediction_result["predicted_return"] * i / 5))
            
            db_prediction = models.Prediction(
                asset_id=asset.asset_id,
                asset=asset.symbol,
                user_id=current_user.user_id,
                timeframe_id=1,
                timestamp=simulated_time,
                predicted_price=round(predicted_val, 2),
                model_used="XGBoost_LSTM_Hybrid",
                confidence=float(str(prediction_result["confidence"]).replace('%','')) / 100,
                created_at=datetime.now(timezone.utc)
            )
            db.add(db_prediction)
            future_results.append(db_prediction)

        db.commit()
        for res in future_results: db.refresh(res)
        return future_results

    except Exception as e:
        db.rollback()
        # طباعة الخطأ الحقيقي في التيرمينال للمساعدة في التتبع
        print(f"❌ AI Prediction Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction Error: {str(e)}")