from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db import models

router = APIRouter(prefix="/admin", tags=["Admin Reports"])

@router.get("/accuracy-report")
def get_accuracy_report(db: Session = Depends(get_db)):
    """
    هذا المسار يحل المشكلة من جذورها عبر ربط التوقع بالسعر الحقيقي 
    الموجود في بياناتك التاريخية (125 ألف سجل).
    """
    # عملية الربط (Join) بناءً على العملة والوقت تماماً
    query_results = db.query(
        models.Prediction.asset,
        models.Prediction.timestamp,
        models.Prediction.predicted_price,
        models.Candle.close.label("actual_price")
    ).join(
        models.Candle, 
        (models.Prediction.asset == models.Candle.asset) & 
        (models.Prediction.timestamp == models.Candle.timestamp)
    ).order_by(models.Prediction.timestamp.desc()).limit(20).all()

    report_data = []
    for row in query_results:
        # حساب الدقة باستخدام المعادلة الرياضية
        # Accuracy = 100 - (|Actual - Predicted| / Actual * 100)
        error = abs(row.actual_price - row.predicted_price)
        accuracy_val = 100 - ((error / row.actual_price) * 100)
        
        report_data.append({
            "asset": row.asset.upper(),
            "timestamp": row.timestamp,
            "predicted_price": round(row.predicted_price, 2),
            "actual_price": round(row.actual_price, 2),
            "accuracy": round(max(0, accuracy_val), 2) # ضمان عدم ظهور قيمة سالبة
        })

    return report_data