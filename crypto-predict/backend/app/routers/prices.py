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

router = APIRouter(prefix="/prices", tags=["Prices"])

# ==========================================
# 1. Fetch Top Assets Cards
# جلب أحدث الأسعار لعرضها في البطاقات العلوية (Dashboard)
# ==========================================
@router.get("/top-assets")
def get_top_assets(db: Session = Depends(get_db)):
    # العثور على أحدث توقيت (Timestamp) لكل عملة لضمان جلب السعر الحالي
    subquery = db.query(
        models.Candle.asset_id,
        func.max(models.Candle.timestamp).label("max_ts")
    ).group_by(models.Candle.asset_id).subquery()

    # جلب بيانات الشموع مع ربطها بجدول العملات للحصول على الرموز (Symbols)
    latest_prices = db.query(models.Candle, models.CryptoAsset.symbol).join(
        subquery, (models.Candle.asset_id == subquery.c.asset_id) & 
                  (models.Candle.timestamp == subquery.c.max_ts)
    ).join(models.CryptoAsset, models.Candle.asset_id == models.CryptoAsset.asset_id).all()

    return [
        {
            "id": row.symbol.upper(), 
            "name": row.symbol.upper(), 
            "price": float(row.Candle.close), 
            "change": 0.5  # يمكن ربطها بحساب نسبة التغير لاحقاً
        } for row in latest_prices
    ]

# ==========================================
# 2. Historical Data for Chart
# جلب البيانات التاريخية لرسم مخططات الـ Candlestick
# ==========================================
@router.get("/{symbol}")
def get_historical_ohlcv(symbol: str, db: Session = Depends(get_db)):
    # التحقق من وجود العملة في قاعدة البيانات أولاً
    asset = db.query(models.CryptoAsset).filter(models.CryptoAsset.symbol == symbol.upper()).first()
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {symbol} not found")

    # جلب آخر 150 نقطة بيانات مرتبطة بالعملة
    data = db.query(models.Candle).filter(
        models.Candle.asset_id == asset.asset_id
    ).order_by(models.Candle.timestamp.desc()).limit(150).all()
    
    return sorted([
        {"x": c.timestamp, "y": [float(c.open), float(c.high), float(c.low), float(c.close)]} 
        for c in data
    ], key=lambda x: x['x'])

# ==========================================
# 3. Bulk CSV Upload (Fast Import)
# رفع ملفات CSV الضخمة ومعالجة البيانات وربطها بالـ IDs تلقائياً
# ==========================================
@router.post("/upload-csv")
async def upload_csv_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    مسار مخصص لرفع البيانات التاريخية. 
    ملاحظة: اضغط على 'Try it out' في Swagger ليظهر زر اختيار الملف.
    """
    try:
        # قراءة محتوى الملف وتحويله لـ DataFrame
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        # توحيد أسماء الأعمدة لتجنب أخطاء حالة الأحرف (KeyError)
        df.columns = [c.lower().strip() for c in df.columns]

        # تحديد العمود الذي يحتوي على اسم العملة
        asset_col = 'asset' if 'asset' in df.columns else 'symbol' if 'symbol' in df.columns else None
        if not asset_col:
            raise HTTPException(status_code=400, detail="Missing 'asset' or 'symbol' column in CSV")

        # إنشاء خريطة سريعة للربط بين الرمز والـ ID لتجنب الاستعلامات المتكررة
        assets_map = {a.symbol.lower(): a.asset_id for a in db.query(models.CryptoAsset).all()}
        
        new_candles = []
        for _, row in df.iterrows():
            symbol_name = str(row[asset_col]).lower()
            asset_id = assets_map.get(symbol_name)
            
            if asset_id:
                new_candles.append(models.Candle(
                    asset_id=asset_id,
                    timeframe_id=1,  # 1 تعني إطار الساعة الواحدة (1h)
                    timestamp=pd.to_datetime(row['timestamp']),
                    open=row['open'],
                    high=row['high'],
                    low=row['low'],
                    close=row['close'],
                    volume=row['volume'],
                    exchange=row.get('exchange', 'Binance')
                ))

        # استخدام تقنية الحفظ بالجملة للتعامل مع آلاف السجلات بسرعة
        db.bulk_save_objects(new_candles)
        db.commit()
        
        return {"status": "success", "message": f"Imported {len(new_candles)} records successfully!"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Data Processing Error: {str(e)}")

# ==========================================
# 4. AI Smart Prediction Engine
# توليد توقعات مستقبلية باستخدام محرك الذكاء الاصطناعي
# ==========================================
@router.get("/predict/{symbol}")
def get_ai_prediction(symbol: str, db: Session = Depends(get_db)):
    try:
        # البحث عن مرجع العملة
        asset = db.query(models.CryptoAsset).filter(models.CryptoAsset.symbol == symbol.upper()).first()
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")

        # جلب البيانات التاريخية (شموع + مشاعر) اللازمة لعملية التنبؤ
        query_results = db.query(models.Candle, models.Sentiment).join(
            models.Sentiment, 
            (models.Candle.asset_id == models.Sentiment.asset_id) & 
            (models.Candle.timestamp == models.Sentiment.timestamp)
        ).filter(models.Candle.asset_id == asset.asset_id).order_by(models.Candle.timestamp.desc()).limit(48).all()

        if len(query_results) < 48:
            raise HTTPException(status_code=400, detail="Insufficient historical data for AI (48h required).")

        # تحضير البيانات لنموذج التوقع
        feature_data = [
            {
                "open": float(c.open), "high": float(c.high), "low": float(c.low), 
                "close": float(c.close), "volume": float(c.volume),
                "avg_sentiment": s.avg_sentiment, "sent_count": s.sent_count
            } for c, s in query_results
        ]
        
        df_input = pd.DataFrame(feature_data)
        prediction_result = inference_engine.predict(df_input)

        # حفظ النتائج المتوقعة لـ 5 فترات مستقبلية في قاعدة البيانات
        last_candle = query_results[0][0]
        future_results = []
        
        for i in range(1, 6):
            simulated_time = last_candle.timestamp + timedelta(hours=i)
            # تطبيق نسبة التغير المتوقعة من الموديل على آخر سعر إغلاق
            predicted_val = float(last_candle.close) * (1 + (prediction_result["predicted_return"] * i / 5))
            
            db_prediction = models.Prediction(
                asset_id=asset.asset_id,
                timeframe_id=1,
                timestamp=simulated_time,
                predicted_price=round(predicted_val, 2),
                model_used="XGBoost_LSTM_Hybrid",
                confidence=float(str(prediction_result["confidence"]).replace('%','')) / 100,
                created_at=datetime.now(timezone.utc)
            )
            db.add(db_prediction)
            future_results.append({
                "timestamp": simulated_time.isoformat(), 
                "predicted_value": round(predicted_val, 2)
            })

        db.commit()
        return future_results

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))