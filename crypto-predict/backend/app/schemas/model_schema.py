
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ModelLogBase(BaseModel):
    records_count: int = Field(0, description="Number of records used for training")
    
    status: str = Field(..., max_length=20, description="Training status: Success or Failed")
    
    error_message: Optional[str] = Field(None, max_length=500, description="Error message if training failed")
    
    user_id: int = Field(..., description="ID of the admin who performed the training")

class ModelLogResponse(ModelLogBase):
    id: int               
    trained_at: datetime  
    class Config:
        from_attributes = True