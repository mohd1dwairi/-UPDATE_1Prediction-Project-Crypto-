# هذا الملف يحدد شكل البيانات التي تدخل وتخرج من الـ API (Schemas)
from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional

# 1. المخطط الأساسي (يحتوي على البيانات المشتركة بين كل العمليات)
class UserBase(BaseModel):
    # اسم المستخدم بين 3 و 50 حرفاً
    User_Name: str = Field(..., min_length=3, max_length=50) 
    # البريد الإلكتروني بحد أقصى 255 حرفاً
    email: EmailStr = Field(..., max_length=255)
    # إضافة حقل الرتبة (role) ليكون متاحاً في العرض
    role: Optional[str] = "user" 

# 2. المخطط الخاص بعملية التسجيل (يُرسل من Frontend إلى Backend)
class UserCreate(UserBase):
    # كلمة المرور الخام المطلوبة عند إنشاء الحساب فقط
    password: str = Field(..., min_length=8)

# 3. المخطط الخاص باستجابة النظام (يُرسل من Backend إلى Frontend)
class UserResponse(UserBase):
    user_id: int      # الرقم التعريفي الفريد
    created_at: date  # تاريخ الإنشاء

    class Config:
        # يسمح لـ Pydantic بقراءة البيانات مباشرة من كائنات SQLAlchemy (Models)
        from_attributes = True

# 4. المخطط الخاص بطلب تسجيل الدخول
class LoginRequest(BaseModel):
    email: EmailStr
    password: str