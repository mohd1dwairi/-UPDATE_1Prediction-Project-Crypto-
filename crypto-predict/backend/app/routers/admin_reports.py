from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db import models

router = APIRouter(prefix="/admin", tags=["Admin Reports"])

# --- أرقام النظام (سهل) ---
@router.get("/dashboard-stats")
def get_stats(db: Session = Depends(get_db)):
    return {
        "total_users": db.query(models.User).count(),
        "total_records": db.query(models.Candle).count(),
        "total_predictions": db.query(models.Prediction).count()
    }

# --- تقرير الدقة (Backtesting) ---
@router.get("/accuracy-analysis")
def get_accuracy(db: Session = Depends(get_db)):
    # مقارنة سعر الإغلاق الحقيقي بسعر التوقع المخزن سابقاً
    results = db.query(
        models.Prediction.timestamp,
        models.Prediction.predicted_price,
        models.Candle.close.label("actual_price")
    ).join(
        models.Candle, 
        (models.Prediction.asset == models.Candle.asset) & 
        (models.Prediction.timestamp == models.Candle.timestamp)
    ).limit(20).all()
    
    return results