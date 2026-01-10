import pandas as pd
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import models
from app.services.inference_service import inference_engine # استدعاء المحرك الحقيقي

# ==========================================
# دالة تنظيف نسبة الثقة (للتوافق مع النوع double في Postgres)
# ==========================================
def clean_confidence_value(raw_value) -> float:
    try:
        # إذا كانت القيمة نصية مثل "85%"
        clean_str = str(raw_value).replace('%', '').strip()
        val = float(clean_str)
        if val > 1:
            val = val / 100.0
        return round(val, 4)
    except:
        return 0.50

# ==========================================
# محرك التوقعات الحقيقي (AI Prediction Engine)
# ==========================================
def generate_predictions(db: Session, asset_id: int, timeframe_id: int, user_id: int):
    """
    🔮 يقوم بسحب البيانات الحقيقية من DB وتمريرها لموديل XGB-LSTM
    """
    
    # 1. جلب معلومات العملة
    asset_info = db.query(models.CryptoAsset).filter(models.CryptoAsset.asset_id == asset_id).first()
    symbol_name = asset_info.symbol if asset_info else "UNKNOWN"

    # 2. سحب آخر 48 سجل (ساعة) من البيانات التاريخية والمشاعر (Join Query)
    # الموديل يحتاج بيانات متسلسلة (Sequence) ليعمل الـ LSTM صح
    query_results = db.query(models.Candle, models.Sentiment).join(
        models.Sentiment, 
        (models.Candle.asset_id == models.Sentiment.asset_id) & 
        (models.Candle.timestamp == models.Sentiment.timestamp)
    ).filter(
        models.Candle.asset_id == asset_id
    ).order_by(models.Candle.timestamp.desc()).limit(48).all()

    # إذا كانت البيانات غير كافية (أقل من 48 ساعة) لن نستطيع تشغيل الـ LSTM
    if len(query_results) < 48:
        print(f"⚠️ بيانات غير كافية لعملة {symbol_name}. المتوفر: {len(query_results)} سجل.")
        return None

    # عكس النتائج لتكون من الأقدم للأحدث (كما يتوقع الموديل)
    query_results.reverse()

    # 3. تحويل البيانات إلى DataFrame بنفس ميزات (Features) الموديل
    data_list = []
    for candle, sentiment in query_results:
        data_list.append({
            "open": float(candle.open),
            "high": float(candle.high),
            "low": float(candle.low),
            "close": float(candle.close),
            "volume": float(candle.volume),
            "avg_sentiment": sentiment.avg_sentiment if sentiment.avg_sentiment else 0.0,
            "sent_count": sentiment.sent_count if sentiment.sent_count else 0,
            "pos_count": sentiment.pos_count if sentiment.pos_count else 0,
            "neg_count": sentiment.neg_count if sentiment.neg_count else 0,
            "neu_count": sentiment.neu_count if sentiment.neu_count else 0,
            "pos_ratio": sentiment.pos_ratio if sentiment.pos_ratio else 0.0,
            "neg_ratio": sentiment.neg_ratio if sentiment.neg_ratio else 0.0,
            "neu_ratio": sentiment.neu_ratio if sentiment.neu_ratio else 0.0,
            "has_news": sentiment.has_news if sentiment.has_news else 0
        })

    df_input = pd.DataFrame(data_list)

    # 4. استدعاء الموديل الحقيقي للتوقع
    # سيعيد لنا: predicted_return, trend, confidence
    ai_output = inference_engine.predict(df_input)

    if "error" in ai_output:
        print(f"❌ خطأ في محرك الذكاء الاصطناعي: {ai_output['error']}")
        return None

    # 5. حساب السعر المستقبلي بناءً على الـ Return المتوقع من XGBoost
    # المعادلة: السعر الجديد = السعر الحالي * (1 + العائد المتوقع)
    current_price = float(query_results[-1][0].close)
    predicted_return = ai_output["predicted_return"]
    final_confidence = clean_confidence_value(ai_output["confidence"])

    predictions_to_save = []

    # توليد 5 توقعات مستقبلية (لكل ساعة قادمة)
    for i in range(1, 6):
        target_ts = datetime.now(timezone.utc) + timedelta(hours=i)
        
        # توزيع العائد على الساعات (بشكل تراكمي بسيط للمحاكاة المستقبلية)
        hourly_return = (predicted_return * i) / 5 
        predicted_val = current_price * (1 + hourly_return)

        new_pred = models.Prediction(
            asset_id=asset_id,
            asset=symbol_name,
            timeframe_id=timeframe_id,
            user_id=user_id,
            timestamp=target_ts,
            predicted_price=round(predicted_val, 2),
            confidence=final_confidence,
            model_used="XGB-LSTM_Hybrid",
            created_at=datetime.now(timezone.utc)
        )
        db.add(new_pred)
        predictions_to_save.append(new_pred)

    try:
        db.commit()
        for p in predictions_to_save:
            db.refresh(p)
        print(f"✅ تم توليد توقعات حقيقية لـ {symbol_name} بناءً على الموديل الهجين.")
        return predictions_to_save
    except Exception as e:
        db.rollback()
        print(f"❌ خطأ أثناء حفظ التوقعات: {e}")
        return None