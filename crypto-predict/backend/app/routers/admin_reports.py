from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db import models

router = APIRouter(prefix="/admin", tags=["Admin Reports"])

# --- 1. إحصائيات النظام العامة ---
@router.get("/stats")
def get_system_overview(db: Session = Depends(get_db)):
    """جلب أرقام ملخصة عن حالة قاعدة البيانات"""
    return {
        "total_users": db.query(models.User).count(),
        "total_data_points": db.query(models.Candle).count(),
        "total_predictions": db.query(models.Prediction).count()
    }

# --- 2. تحليل دقة التوقع (Backtesting) ---
@router.get("/accuracy-analysis")
def get_accuracy_report(db: Session = Depends(get_db)):
    """
    مقارنة السعر المتوقع بالسعر الحقيقي الفعلي.
    نبحث عن التوقعات التي مر وقتها وأصبح سعرها الحقيقي متاحاً.
    """
    results = db.query(
        models.Prediction.timestamp,
        models.Prediction.predicted_price,
        models.Candle.close.label("actual_price"),
        models.Prediction.asset
    ).join(
        models.Candle, 
        (models.Prediction.asset == models.Candle.asset) & 
        (models.Prediction.timestamp == models.Candle.timestamp)
    ).limit(50).all()
    
    return results