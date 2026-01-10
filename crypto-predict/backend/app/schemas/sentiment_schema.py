from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class SentimentBase(BaseModel):
    timestamp: datetime
    asset_id: int 
    sentiment_score: float = Field(..., description="sentiment score ranging from -1 to 1")
    avg_sentiment: float = 0.0
    sent_count: int = 0
    pos_count: int = 0
    neg_count: int = 0
    
    source: Optional[str] = Field(None, max_length=100)
    sentiment_id: Optional[int] = None

class SentimentResponse(SentimentBase):
    id: int  
    class Config:
        from_attributes = True