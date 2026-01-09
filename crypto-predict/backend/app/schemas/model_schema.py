from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# 1. المخطط الأساسي (يحتوي على تفاصيل عملية التدريب)
class ModelLogBase(BaseModel):
    records_count: int = Field(0, description="عدد السجلات التي تم التدريب عليها")
    status: str = Field(..., max_length=20, description="حالة التدريب: Success أو Failed")
    error_message: Optional[str] = Field(None, max_length=500)
    user_id: int = Field(..., description="رقم الأدمن الذي قام بالتدريب")

# 2. المخطط الخاص بالاستجابة (ما يظهر للأدمن في لوحة التحكم)
class ModelLogResponse(ModelLogBase):
    id: int
    trained_at: datetime # وقت تنفيذ العملية كما في الرسمة

    class Config:
        from_attributes = True