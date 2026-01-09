# هذا الملف يحدد شكل بيانات التوقعات عند الإرسال والاستقبال
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# 1. المخطط الأساسي (يحتوي على المعطيات والنتائج الأساسية)
class PredictionBase(BaseModel):
    # الروابط حسب الرسمة (ERD)
    asset_id: int 
    timeframe_id: int
    
    # توقيت التوقع
    timestamp: datetime
    
    # القيم المطلوبة حسب صفحة 14 والرسمة
    predicted_value: float = Field(..., description="القيمة المتوقعة حسب التصميم المنطقي")
    confidence: Optional[float] = None
    model_used: str = Field(..., max_length=20)
    
    # حقل الحالة (status) حسب صفحة 14 (مثلاً: Pending, Completed)
    status: Optional[str] = "Completed"

# 2. المخطط الخاص باستجابة النظام (Response)
class PredictionResponse(PredictionBase):
    # المسميات حرفياً حسب الرسمة (ERD)
    id_Prediction: int
    user_id: int
    created_at: datetime

    class Config:
        # التحديث الجديد لـ orm_mode في Pydantic v2
        from_attributes = True