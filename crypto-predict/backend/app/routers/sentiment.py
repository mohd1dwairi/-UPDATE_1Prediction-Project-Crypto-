from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.sentiment_schema import SentimentResponse
from app.db import models
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/sentiment", tags=["Sentiment"])

@router.get("/{symbol}", response_model=List[SentimentResponse])
def get_sentiment_data(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    📊 جلب بيانات تحليل المشاعر التفصيلية للعملة المطلوبة.
    يتم الربط بين اسم العملة (Symbol) ورقمها (Asset_ID) لضمان دقة البيانات.
    """
    
    # 1. البحث عن العملة في جدول الأصول (حسب الرسمة المحدثة)
    asset = db.query(models.CryptoAsset).filter(
        models.CryptoAsset.symbol == symbol.upper()
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail=f"العملة {symbol} غير مدعومة حالياً.")

    # 2. جلب سجلات المشاعر المرتبطة بهذا الـ asset_id
    # نأخذ آخر 100 سجل لعرض التطور الزمني للمشاعر
    sentiment_records = db.query(models.Sentiment).filter(
        models.Sentiment.asset_id == asset.asset_id
    ).order_by(models.Sentiment.timestamp.desc()).limit(100).all()

    if not sentiment_records:
        raise HTTPException(status_code=404, detail="لا توجد بيانات مشاعر متوفرة لهذه العملة.")

    return sentiment_records