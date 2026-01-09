from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user_schema import UserCreate, UserResponse, LoginRequest
from app.services.auth_service import register_user, login_user
from app.core.security import get_current_user
from app.db import models 

router = APIRouter(prefix="/auth", tags=["Authentication"])

# 1. مسار التحقق من المستخدم الحالي (Get Me)
@router.get("/me", response_model=UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    """
    جلب بيانات المستخدم صاحب التوكن الحالي.
    يُستخدم في الفرونت إيند للتأكد أن الجلسة ما زالت قائمة.
    """
    return current_user

# 2. مسار تسجيل حساب جديد (Register)
@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    إنشاء حساب جديد وتخزينه في جدول users حسب مواصفات الـ ERD.
    """
    try:
        return register_user(user_data, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# 3. مسار تسجيل الدخول (Login)
@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    التحقق من البيانات وإرجاع الـ JWT Token مع بيانات المستخدم الأساسية.
    """
    try:
        # استدعاء الخدمة للتحقق من كلمة المرور وتوليد التوكن
        token = login_user(login_data.email, login_data.password, db)
        
        # جلب بيانات المستخدم من القاعدة لإرسالها للواجهة الأمامية
        user = db.query(models.User).filter(models.User.email == login_data.email).first()
        
        if not user:
            raise ValueError("المستخدم غير موجود")

        # إرسال استجابة كاملة تحتوي على التوكن والبيانات المطلوبة للـ React
        return {
            "access_token": token, 
            "token_type": "bearer",
            "user": {
                "id": user.user_id,      # استخدام user_id حسب الرسمة
                "name": user.User_Name,  # المسمى الصحيح من الموديل
                "email": user.email,
                "role": user.role        # ضروري للتحكم في صلاحيات الأدمن
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="البريد الإلكتروني أو كلمة المرور غير صحيحة"
        )