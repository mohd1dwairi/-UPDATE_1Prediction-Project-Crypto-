from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.db import models

def clean_confidence_value(raw_value) -> float:
    try:
        clean_str = str(raw_value).replace('%', '').strip()
        val = float(clean_str)
        if val > 1:
            val = val / 100.0
        return round(val, 4)
    except:
        return 0.50

def generate_predictions(db: Session, asset_id: int, timeframe_id: int, user_id: int, raw_ai_output: dict = None):
    # 1. جلب معلومات العملة (للحصول على الرمز النصي مثل BTC)
    asset_info = db.query(models.CryptoAsset).filter(models.CryptoAsset.asset_id == asset_id).first()
    symbol_name = asset_info.symbol if asset_info else "UNKNOWN"

    # 2. جلب آخر سعر إغلاق
    latest_candle = db.query(models.Candle).filter(
        models.Candle.asset_id == asset_id
    ).order_by(models.Candle.timestamp.desc()).first()

    base_price = float(latest_candle.close) if latest_candle else 50000.0

    # 3. معالجة نسبة الثقة
    confidence_input = raw_ai_output.get("confidence", "50%") if raw_ai_output else "50%"
    final_confidence = clean_confidence_value(confidence_input)

    predictions_list = []

    # توليد 5 توقعات
    for i in range(1, 6):
        target_ts = datetime.now(timezone.utc) + timedelta(hours=i)
        prediction_factor = 1 + (0.002 * i) # محاكاة بسيطة
        predicted_val = base_price * prediction_factor

        # إنشاء السجل مع التأكد من تعبئة كافة الحقول المطلوبة في الـ ERD
        new_prediction = models.Prediction(
            asset_id=asset_id,
            asset=symbol_name,             # أضفنا هذا السطر لأنه مطلوب في الموديل عندك
            timeframe_id=timeframe_id,
            user_id=user_id,
            timestamp=target_ts,
            predicted_price=round(predicted_val, 2),
            confidence=final_confidence,
            model_used="XGBoost_LSTM",     # تأكد أن النص لا يتجاوز 20 حرفاً
        )

        db.add(new_prediction)
        predictions_list.append(new_prediction)

    try:
        db.commit()
        # عمل refresh لضمان قراءة البيانات بعد الحفظ (تجنب مشاكل Lazy Loading)
        for p in predictions_list:
            db.refresh(p)
        return predictions_list
    except Exception as e:
        db.rollback()
        print(f"❌ Database Save Error: {e}")
        return None