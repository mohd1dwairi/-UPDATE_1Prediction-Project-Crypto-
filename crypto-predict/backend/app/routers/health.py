from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db

# تعريف المسار مع الوسوم المناسبة
router = APIRouter(prefix="/health", tags=["System Health"])

@router.get("/")
def check_system_health(db: Session = Depends(get_db)):
    """
    فحص شامل لحالة النظام (السيرفر وقاعدة البيانات)
    """

    try:
        # تنفيذ استعلام بسيط للتأكد من اتصال قاعدة البيانات
        
        db.execute(text("SELECT 1"))
        db_status = "Connected"
    except Exception as e:
        # في حال فشل الاتصال بالقاعدة
        #
        db_status = f"Disconnected: {str(e)}"

    return {
        "status": "online",
        "message": "Backend is pulsing!",
        "database": db_status,
        "version": "1.0.0"
    }