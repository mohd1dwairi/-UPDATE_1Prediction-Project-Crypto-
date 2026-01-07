from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
import io
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.db.session import get_db
from app.db import models
from app.services.inference_service import inference_engine

router = APIRouter(prefix="/prices", tags=["Prices"])

# ==========================================
# 1. تعريف شكل البيانات المدخلة (Schemas) - [الأسهل]
# ==========================================
class MarketDataInput(BaseModel):
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    avg_sentiment: float
    sent_count: int = 0
    pos_count: int = 0
    neg_count: int = 0
    neu_count: int = 0
    pos_ratio: float = 0.0
    neg_ratio: float = 0.0
    neu_ratio: float = 0.0
    has_news: int = 0

# ==========================================
# 2. جلب البيانات التاريخية (GET) - [بسيط]
# ==========================================

@router.get("/top-assets")
def get_top_assets(db: Session = Depends(get_db)):
    """جلب أحدث سعر لكل عملة لعرض البطاقات العلوية"""
    subquery = db.query(
        models.Candle.asset,
        func.max(models.Candle.timestamp).label("max_ts")
    ).group_by(models.Candle.asset).subquery()

    latest_prices = db.query(models.Candle).join(
        subquery, (models.Candle.asset == subquery.c.asset) & (models.Candle.timestamp == subquery.c.max_ts)
    ).all()

    return [
        {"id": p.asset.upper(), "name": p.asset.upper(), "price": p.close, "change": 0.5} 
        for p in latest_prices
    ]

@router.get("/{symbol}")
def get_historical_ohlcv(symbol: str, db: Session = Depends(get_db)):
    """جلب البيانات التاريخية للرسم البياني"""
    target_asset = symbol.lower()
    data = db.query(models.Candle).filter(
        models.Candle.asset == target_asset
    ).order_by(models.Candle.timestamp.desc()).limit(150).all()
    
    if not data:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol}")

    return sorted([
        {"x": c.timestamp, "y": [c.open, c.high, c.low, c.close]} for c in data
    ], key=lambda x: x['x'])

# ==========================================
# 3. إدارة البيانات (Admin) - [متوسط]
# ==========================================

@router.post("/upload-csv")
async def upload_csv_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """رفع بيانات تاريخية ضخمة عبر CSV"""
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        new_candles = []
        for _, row in df.iterrows():
            new_candles.append(models.Candle(
                asset=str(row['asset']).lower(),
                timestamp=pd.to_datetime(row['timestamp']),
                open=float(row['open']), high=float(row['high']),
                low=float(row['low']), close=float(row['close']), volume=float(row['volume'])
            ))
        db.bulk_save_objects(new_candles)
        db.commit()
        return {"status": "success", "message": f"Successfully imported {len(new_candles)} records."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 4. محرك التوقع الذكي (AI Predict) - [الأصعب والأهم]
# ==========================================

@router.get("/predict/{symbol}")
def get_ai_prediction(symbol: str, db: Session = Depends(get_db)):
    """
    يقوم بعملية التوقع، تنظيف البيانات، وحفظها في قاعدة البيانات.
    يتم تخزين النتائج لتعكس دقة النظام في لوحة تحكم الأدمن.
    """
    try:
        target_asset = symbol.lower()
        
        # 1. جلب بيانات السعر والمشاعر لآخر 48 ساعة
        query_results = db.query(models.Candle, models.Sentiment).join(
            models.Sentiment, 
            (models.Candle.asset == models.Sentiment.asset) & 
            (models.Candle.timestamp == models.Sentiment.timestamp)
        ).filter(models.Candle.asset == target_asset).order_by(models.Candle.timestamp.desc()).limit(48).all()

        if len(query_results) < 48:
            raise HTTPException(status_code=400, detail="Incomplete data for 48h simulation.")

        # 2. تجهيز البيانات لموديل التوقع
        feature_data = []
        for candle, sentiment in query_results:
            feature_data.append({
                "timestamp": candle.timestamp, "open": candle.open, "high": candle.high, 
                "low": candle.low, "close": candle.close, "volume": candle.volume,
                "sent_count": sentiment.sent_count, "avg_sentiment": sentiment.avg_sentiment,
                "pos_count": sentiment.pos_count, "neg_count": sentiment.neg_count,
                "neu_count": sentiment.neu_count, "pos_ratio": sentiment.pos_ratio,
                "neg_ratio": sentiment.neg_ratio, "neu_ratio": sentiment.neu_ratio, "has_news": sentiment.has_news
            })
        
        df_input = pd.DataFrame(feature_data).sort_values("timestamp")
        feature_cols = ["open", "high", "low", "close", "volume", "sent_count", "avg_sentiment", 
                        "pos_count", "neg_count", "neu_count", "pos_ratio", "neg_ratio", "neu_ratio", "has_news"]

        # 3. تشغيل الموديل
        prediction_result = inference_engine.predict(df_input[feature_cols])

        # 4. معالجة وحفظ النتائج في قاعدة البيانات
        future_results = []
        last_price = df_input["close"].iloc[-1]
        last_timestamp = df_input["timestamp"].iloc[-1]

        # تنظيف نسبة الثقة (Confidence): تحويل "44%" إلى 0.44
        raw_conf = str(prediction_result["confidence"]).replace('%', '')
        conf_float = float(raw_conf)
        final_confidence = conf_float / 100 if conf_float > 1 else conf_float

        for i in range(1, 6):
            simulated_time = last_timestamp + timedelta(hours=i)
            predicted_val = round(last_price * (1 + (prediction_result["predicted_return"] * i / 5)), 2)
            
            # --- حفظ التوقع في PostgreSQL لتقرير الأدمن ---
            db_prediction = models.Prediction(
                asset=target_asset,
                timestamp=simulated_time,
                predicted_price=predicted_val,
                model_used="XGBoost_LSTM_Hybrid", 
                confidence=final_confidence,
                created_at=datetime.now() # لن يظهر الخطأ الآن إذا أضفته للموديل
            )
            db.add(db_prediction)

            future_results.append({
                "timestamp": simulated_time.isoformat(),
                "predicted_value": predicted_val,
                "trend": prediction_result["trend"],
                "confidence": prediction_result["confidence"] 
            })

        db.commit() # تأكيد الحفظ
        return future_results

    except Exception as e:
        db.rollback()
        print(f"Error in Predict: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI Engine Error: {str(e)}")