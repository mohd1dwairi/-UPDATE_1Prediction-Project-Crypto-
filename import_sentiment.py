"""
import pandas as pd
from sqlalchemy import create_engine, text
import os

# بيانات الاتصال
DB_URL = "postgresql://postgres:admin@localhost:5433/crypto_db"
engine = create_engine(DB_URL)

def run_import():
    file_name = "dataset_ohlcv_with_market_sentiment_hourly1.csv"
    
    if not os.path.exists(file_name):
        print(f"❌ Error: File '{file_name}' not found!")
        return

    print(f"⏳ Reading file: {file_name}...")
    df = pd.read_csv(file_name)
    df['open_time'] = pd.to_datetime(df['open_time'])
    
    # اختيار الأعمدة
    sentiment_data = df[[
        'symbol', 'open_time', 'sent_count', 'avg_sentiment', 
        'pos_count', 'neg_count', 'neu_count', 
        'pos_ratio', 'neg_ratio', 'neu_ratio', 'has_news'
    ]].copy()

    sentiment_data.columns = [
        'asset', 'timestamp', 'sent_count', 'avg_sentiment', 
        'pos_count', 'neg_count', 'neu_count', 
        'pos_ratio', 'neg_ratio', 'neu_ratio', 'has_news'
    ]

    # --- الخطوة الجديدة والمهمة جداً: حذف التكرار من الداتا قبل الرفع ---
    print("🧹 Removing duplicate rows from the CSV data...")
    sentiment_data.drop_duplicates(subset=['asset', 'timestamp'], inplace=True)
    # -------------------------------------------------------------

    try:
        print("🗑️ Clearing old sentiment data...")
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE sentiments RESTART IDENTITY CASCADE;"))
            conn.commit()

        print(f"🚀 Uploading {len(sentiment_data)} unique records to 'sentiments' table...")
        sentiment_data.to_sql(
            'sentiments', 
            engine, 
            if_exists='append', 
            index=False, 
            chunksize=500
        )
        print("✅ Sentiment data imported successfully without duplicates!")
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    run_import()
    """
