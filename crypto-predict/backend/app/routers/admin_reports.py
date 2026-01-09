from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.db.session import get_db
from app.db import models
from app.services.trainer import retrain_model_logic
from app.core.security import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin Operations"])

# ==========================================
# 1. تقرير الدقة (Accuracy Report)
# ==========================================
@router.get("/accuracy-report")
def get_accuracy_report(db: Session = Depends(get_db)):
    """
    يقوم بربط التوقعات بالأسعار الحقيقية بناءً على asset_id و timestamp.
    """
    # الربط الثلاثي بين التوقعات والشموع وأسماء العملات
    query_results = db.query(
        models.CryptoAsset.symbol,
        models.Prediction.timestamp,
        models.Prediction.predicted_price,
        models.Candle.close.label("actual_price")
    ).join(
        models.Candle, 
        (models.Prediction.asset_id == models.Candle.asset_id) & 
        (models.Prediction.timestamp == models.Candle.timestamp)
    ).join(
        models.CryptoAsset, models.Prediction.asset_id == models.CryptoAsset.asset_id
    ).order_by(models.Prediction.timestamp.desc()).limit(30).all()

    report_data = []
    for row in query_results:
        actual = float(row.actual_price)
        predicted = float(row.predicted_price)
        
        # حساب نسبة الخطأ والدقة
        error = abs(actual - predicted)
        accuracy_val = 100 - ((error / actual) * 100) if actual != 0 else 0
        
        report_data.append({
            "asset": row.symbol.upper(),
            "timestamp": row.timestamp,
            "predicted_price": round(predicted, 2),
            "actual_price": round(actual, 2),
            "accuracy": round(max(0, accuracy_val), 2)
        })

    return report_data

# ==========================================
# 2. إعادة التدريب (Retraining)
# ==========================================
@router.post("/retrain")
async def trigger_retraining(
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    تشغيل التدريب في الخلفية مع توثيق من قام بالعملية (user_id).
    """
    # التأكد أن الشخص هو أدمن فعلياً
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="غير مسموح إلا للمديرين")

    # إرسال المهمة للخلفية وتمرير ID الأدمن للتوثيق في ModelLog
    background_tasks.add_task(retrain_model_logic, db, current_user.user_id)
    
    return {
        "status": "started",
        "admin": current_user.User_Name,
        "message": "بدأت عملية إعادة تدريب الموديل بناءً على أحدث بيانات السوق."
    }

# ==========================================
# 3. سجلات التدريب (Training Logs)
# ==========================================
@router.get("/training-logs")
def get_training_logs(db: Session = Depends(get_db)):
    """جلب سجلات التدريب مع أسماء المديرين الذين قاموا بها"""
    logs = db.query(
        models.ModelLog, 
        models.User.User_Name
    ).join(
        models.User, models.ModelLog.user_id == models.User.user_id
    ).order_by(models.ModelLog.trained_at.desc()).limit(10).all()
    
    return [
        {
            "id": log.ModelLog.id,
            "trained_at": log.ModelLog.trained_at,
            "records": log.ModelLog.records_count,
            "status": log.ModelLog.status,
            "admin": log.User_Name
        } for log in logs
    ]