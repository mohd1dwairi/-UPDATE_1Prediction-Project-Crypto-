from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.db import models

# ==========================================
# دالة تنظيف ومعالجة نسبة الثقة (Sanitization)
# ==========================================
def clean_confidence_value(raw_value) -> float:
    """
    تحويل القيمة من نص (مثل '44%') إلى رقم عشري نقي (0.44).
    هذا يضمن توافق البيانات مع نوع double precision في PostgreSQL.
    """
    try:
        # إزالة الرموز النصية والمسافات
        clean_str = str(raw_value).replace('%', '').strip()
        val = float(clean_str)
        
        # تحويل القيم المئوية (مثل 44) إلى كسر عشري (0.44)
        if val > 1:
            val = val / 100.0
            
        return round(val, 4)
    except (ValueError, TypeError):
        return 0.50 # قيمة افتراضية في حال الخطأ

# ==========================================
# محرك التوقعات (Prediction Engine)
# ==========================================
def generate_predictions(
    db: Session,
    asset_id: int,
    timeframe_id: int,
    user_id: int,
    raw_ai_output: dict = None
):
    """
    🔮 محرك التوقعات المحدث بناءً على الرسمة (ERD).
    يقوم بربط التوقع بالعملة، الإطار الزمني، والمستخدم.
    """

    # 1. جلب آخر سعر إغلاق من جدول OHLCV_Candle (Anchor Price)
    # نستخدم asset_id للبحث لضمان سلامة العلاقات (Normalization)
    latest_candle = db.query(models.Candle).filter(
        models.Candle.asset_id == asset_id
    ).order_by(models.Candle.timestamp.desc()).first()

    base_price = float(latest_candle.close) if latest_candle else 50000.0

    # 2. معالجة نسبة الثقة (حل مشكلة Mismatch النوع)
    confidence_input = raw_ai_output.get("confidence", "50%") if raw_ai_output else "50%"
    final_confidence = clean_confidence_value(confidence_input)

    predictions_list = []

    # توليد 5 توقعات مستقبلية (Hourly)
    for i in range(1, 6):
        target_ts = datetime.now(timezone.utc) + timedelta(hours=i)
        
        # محاكاة لنتيجة الموديل الهجين (Hybrid XGB-LSTM)
        prediction_factor = 1 + (0.005 * i) 
        predicted_val = base_price * prediction_factor

        # 3. إنشاء سجل التوقع (مطابق للرسمة حرفياً)
        #
        new_prediction = models.Prediction(
            asset_id=asset_id,               # الربط بجدول CryptoAsset
            timeframe_id=timeframe_id,       # الربط بجدول Timeframe
            user_id=user_id,                 # الربط بجدول User
            timestamp=target_ts,             # نوعه timestamp with time zone
            predicted_price=round(predicted_val, 2), # نوعه double precision
            confidence=final_confidence,     # نوعه double precision
            model_used="XGBoost_LSTM_Hybrid",# نوعه var(20)
            created_at=datetime.now(timezone.utc)
        )

        db.add(new_prediction)
        predictions_list.append(new_prediction)

    # 4. حفظ البيانات في PostgreSQL
    #
    db.commit()
    
    return predictions_list