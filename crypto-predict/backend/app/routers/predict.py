from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.prediction_schema import PredictionResponse
from app.db import models
from app.services.prediction_service import generate_predictions
from app.core.security import get_current_user

router = APIRouter(
    prefix="/predict",
    tags=["Prediction"],
)

@router.get("/{symbol}", response_model=List[PredictionResponse])
def get_prediction(
    symbol: str,
    timeframe: str = "1h",  # الإطار الزمني المطلوب (مثل 1h, 4h, 1d)
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    🔮 التنبؤ بأسعار عملة رقمية معينة بناءً على الهيكلية الجديدة (ERD)
    - يتم التحقق من وجود العملة والإطار الزمني في قاعدة البيانات أولاً.
    """
    
    # 1. التحقق من وجود العملة وجلب الـ asset_id (حسب الرسمة)
    asset = db.query(models.CryptoAsset).filter(
        models.CryptoAsset.symbol == symbol.upper()
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset '{symbol}' not supported.")

    # 2. التحقق من وجود الإطار الزمني وجلب الـ timeframe_id (حسب الرسمة)
    tf = db.query(models.Timeframe).filter(
        models.Timeframe.code == timeframe
    ).first()
    
    if not tf:
        raise HTTPException(status_code=404, detail=f"Timeframe '{timeframe}' not supported.")

    # 3. استدعاء الخدمة لتوليد التوقعات (تمرير الـ IDs والـ User)
    # ملاحظة: استبدلنا Mock بـ generate_predictions ليعكس الواقع
    predictions = generate_predictions(
        db=db, 
        asset_id=asset.asset_id, 
        timeframe_id=tf.timeframe_id, 
        user_id=current_user.user_id
    )
    
    if not predictions:
        raise HTTPException(status_code=500, detail="Failed to generate predictions.")

    return predictions