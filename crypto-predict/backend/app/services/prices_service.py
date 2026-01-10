from datetime import datetime
import requests
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.db import models

# تحسين الوظيفة لتجلب بيانات OHLCV حقيقية كما هو مطلوب في UC-06
def fetch_prices_from_api(asset_id: int, symbol: str, timeframe_id: int, timeframe_code: str, db: Session):
   
    # استخدام Binance للحصول على بيانات OHLCV كاملة (Open, High, Low, Close, Volume)
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol.upper()}USDT&interval={timeframe_code}&limit=100"

    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()

    values = []
    for item in data:
        ts = datetime.utcfromtimestamp(item[0] / 1000)

        values.append(
            {
                "asset_id": asset_id,        # ربط مع جدول CryptoAsset 
                "timeframe_id": timeframe_id, # ربط مع جدول Timeframe 
                "timestamp": ts,
                "open": float(item[1]),      # سعر الفتح 
                "high": float(item[2]),      # أعلى سعر 
                "low": float(item[3]),       # أدنى سعر 
                "close": float(item[4]),     # سعر الإغلاق [
                "volume": float(item[5]),    # الكمية 
            }
        )

    if not values:
        return 0

    # إدخال البيانات في جدول OHLCV_Candle  
    stmt = insert(models.OHLCV_Candle).values(values)
     #منع التكرار
    stmt = stmt.on_conflict_do_nothing(
        index_elements=["asset_id", "timeframe_id", "timestamp"]
    )

    db.execute(stmt)
    db.commit()

    return len(values)