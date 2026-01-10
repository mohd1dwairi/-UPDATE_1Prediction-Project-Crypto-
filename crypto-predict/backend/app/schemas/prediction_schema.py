from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PredictionBase(BaseModel):
    asset_id: int 
    timeframe_id: int
    asset: Optional[str] = None 
    timestamp: datetime
    predicted_price: float = Field(..., description="السعر المتوقع") 
    confidence: Optional[float] = None
    model_used: str = Field(..., max_length=20)

# المخطط   (Response)
class PredictionResponse(PredictionBase):
    id_Prediction: int     
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True