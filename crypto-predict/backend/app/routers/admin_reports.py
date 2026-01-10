from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db import models
from app.core.security import get_current_user
from datetime import datetime, timezone

router = APIRouter(prefix="/admin", tags=["Admin Reports"])

# ============================================================
# 1. إحصائيات لوحة التحكم (Dashboard Stats)
# المسار: /api/admin/stats
# ============================================================
@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # التأكد أن المستخدم "Admin" فقط
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    return {
        "total_users": db.query(models.User).count(),
        "total_predictions": db.query(models.Prediction).count(),
        "total_candles": db.query(models.Candle).count(),
        "total_sentiments": db.query(models.Sentiment).count(),
    }

# ============================================================
# 2. محاكاة إعادة تدريب الموديل (Retrain)
# المسار: /api/admin/retrain
# ============================================================
@router.post("/retrain")
def retrain_model(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        # 1. تسجيل عملية التدريب في جدول ModelLog (حسب الـ ERD)
        new_log = models.ModelLog(
            trained_at=datetime.now(timezone.utc),
            records_count=db.query(models.Candle).count(),
            status="Success",
            user_id=current_user.user_id
        )
        db.add(new_log)
        
        # 2. في المشاريع الحقيقية، هنا يتم استدعاء سكريبت التدريب
        # لغايات مشروع التخرج، سنقوم بعمل محاكاة ناجحة
        
        db.commit()
        return {
            "status": "success",
            "message": "Model retraining triggered successfully! High accuracy achieved."
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))