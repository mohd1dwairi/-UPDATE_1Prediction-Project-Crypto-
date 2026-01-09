import sys
import os

# إضافة مسار المشروع الحالي لبيئة بايثون لحل مشكلة ModuleNotFoundError
#
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.db import models

def quick_seed():
    db = SessionLocal()
    try:
        print("⏳ Starting to seed database...")
        
        # 1. إضافة العملات (Assets) المذكورة في ملف الـ CSV الخاص بك
        #
        assets_data = [
            {"symbol": "BTC", "name": "Bitcoin"},
            {"symbol": "ETH", "name": "Ethereum"},
            {"symbol": "BNB", "name": "Binance Coin"},
            {"symbol": "SOL", "name": "Solana"},
            {"symbol": "DOGE", "name": "Dogecoin"}
        ]

        for item in assets_data:
            exists = db.query(models.CryptoAsset).filter(models.CryptoAsset.symbol == item["symbol"]).first()
            if not exists:
                db.add(models.CryptoAsset(symbol=item["symbol"], name=item["name"]))
                print(f"➕ Added asset: {item['symbol']}")

        # 2. إضافة الإطار الزمني (Timeframe) - ضروري جداً لعمل الـ Join
        #
        if not db.query(models.Timeframe).filter(models.Timeframe.code == "1h").first():
            db.add(models.Timeframe(code="1h", description="Hourly Data"))
            print("➕ Added timeframe: 1h")

        db.commit()
        print("✅ Success: Database is now ready for CSV upload!")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    quick_seed()