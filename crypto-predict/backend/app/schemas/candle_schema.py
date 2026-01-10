# هذا الملف يحدد شكل بيانات أسعار العملات (الشموع) عند الإدخال والإخراج
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional

class CandleBase(BaseModel):
    timestamp: datetime
    
    exchange: Optional[str] = Field(None, max_length=20)
    
    open: Decimal = Field(..., max_digits=18, decimal_places=8)
    high: Decimal = Field(..., max_digits=18, decimal_places=8)
    low: Decimal = Field(..., max_digits=18, decimal_places=8)
    close: Decimal = Field(..., max_digits=18, decimal_places=8)    
    volume: Decimal = Field(..., max_digits=20, decimal_places=8)
#RELATIONSHIPS    
    asset_id: int = Field(..., description="رقم العملة من جدول CryptoAsset")
    timeframe_id: int = Field(..., description="رقم الفترة من جدول Timeframe")

class CandleResponse(CandleBase):
    candle_id: int 

    class Config:
        from_attributes = True