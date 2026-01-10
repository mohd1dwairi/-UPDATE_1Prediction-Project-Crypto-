# هذا الملف يحدد شكل البيانات التي تدخل وتخرج من الـ API (Schemas)
from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional

class UserBase(BaseModel):
    User_Name: str = Field(..., min_length=3, max_length=50) 
    email: EmailStr = Field(..., max_length=255)
    role: Optional[str] = "user" 

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    user_id: int      
    created_at: date  

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str