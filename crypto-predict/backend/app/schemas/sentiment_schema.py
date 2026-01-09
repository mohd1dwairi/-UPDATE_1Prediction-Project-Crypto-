from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# 1. المخطط الأساسي (يحتوي على البيانات المستخرجة من تحليل المشاعر)
class SentimentBase(BaseModel):
    timestamp: datetime
    # نستخدم asset_id ليتوافق مع المفتاح الأجنبي في الرسمة
    asset_id: int 
    
    # تفاصيل المشاعر (مطابقة للأعمدة الـ 9 في الموديل)
    sentiment_score: float = Field(..., description="السكور الكلي للمشاعر")
    avg_sentiment: float = 0.0
    sent_count: int = 0
    pos_count: int = 0
    neg_count: int = 0
    
    # اختيارية حسب الرسمة والموديل
    source: Optional[str] = Field(None, max_length=100)
    sentiment_id: Optional[int] = None

# 2. المخطط الخاص باستجابة النظام (Response)
class SentimentResponse(SentimentBase):
    id: int  # المعرف الفريد في قاعدة البيانات

    class Config:
        # يسمح للقالب بقراءة البيانات من كائنات SQLAlchemy
        from_attributes = True