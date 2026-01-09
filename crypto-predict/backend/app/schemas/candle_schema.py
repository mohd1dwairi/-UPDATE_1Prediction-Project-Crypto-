# هذا الملف يحدد شكل بيانات أسعار العملات (الشموع) عند الإدخال والإخراج
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional

# 1️⃣ المخطط الأساسي (يحتوي على تفاصيل الشمعة الخام)
class CandleBase(BaseModel):
    # التوقيت حسب الرسمة
    timestamp: datetime
    
    # حقل "البورصة" المذكور في الرسمة (Binance مثلاً)
    exchange: Optional[str] = Field(None, max_length=20)
    
    # دقة الأسعار 18,8 كما ورد في التقرير والرسمة
    open: Decimal = Field(..., max_digits=18, decimal_places=8)
    high: Decimal = Field(..., max_digits=18, decimal_places=8)
    low: Decimal = Field(..., max_digits=18, decimal_places=8)
    close: Decimal = Field(..., max_digits=18, decimal_places=8)
    
    # دقة الكمية 20,8
    volume: Decimal = Field(..., max_digits=20, decimal_places=8)
    
    # الربط بالمفاتيح الأجنبية كما تظهر الوصلات في الرسمة
    asset_id: int = Field(..., description="رقم العملة من جدول CryptoAsset")
    timeframe_id: int = Field(..., description="رقم الفترة من جدول Timeframe")

# 2️⃣ المخطط المستخدم عند استعادة البيانات من السيستم (Response)
class CandleResponse(CandleBase):
    # المسمى حرفياً حسب الرسمة (ERD)
    candle_id: int 

    class Config:
        # يسمح لـ FastAPI بتحويل بيانات SQLAlchemy إلى JSON تلقائياً
        from_attributes = True