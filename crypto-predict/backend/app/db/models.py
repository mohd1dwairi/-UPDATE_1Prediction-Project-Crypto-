from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, DECIMAL, func
from sqlalchemy.orm import relationship
from datetime import date
from app.db.session import Base

# جدول   (CryptoAsset)
class CryptoAsset(Base):
    __tablename__ = "crypto_assets"
    asset_id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    name = Column(String(100))

    # علاقات (Relationships)
    sentiments = relationship("Sentiment", back_populates="asset_ref")
    predictions = relationship("Prediction", back_populates="asset_ref")
    candles = relationship("Candle", back_populates="asset_ref")

# 2) جدول   (Timeframe)
class Timeframe(Base):
    __tablename__ = "timeframes"
    timeframe_id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False) # مثل 1h, 4h
    description = Column(String(255))

    predictions = relationship("Prediction", back_populates="timeframe_ref")
    candles = relationship("Candle", back_populates="timeframe_ref")

# 3) جدول المستخدمين (User)
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    User_Name = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    created_at = Column(Date, default=date.today)

    predictions = relationship("Prediction", back_populates="creator")
    model_logs = relationship("ModelLog", back_populates="user_ref")


# 4) جدول المشاعر (Sentiments)

class Sentiment(Base):
    __tablename__ = "sentiments"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    avg_sentiment = Column(Float)
    sent_count = Column(Integer)
    pos_count = Column(Integer)
    neg_count = Column(Integer)
    # الحقول الجديدة المطلوبة للموديل
    neu_count = Column(Integer, default=0)
    pos_ratio = Column(Float, default=0.0)
    neg_ratio = Column(Float, default=0.0)
    neu_ratio = Column(Float, default=0.0)
    has_news = Column(Integer, default=0)
    
    asset_id = Column(Integer, ForeignKey("crypto_assets.asset_id"))
    asset_ref = relationship("CryptoAsset", back_populates="sentiments")


# 5) جدول   (OHLCV_Candle)

class Candle(Base):
    __tablename__ = "candle_ohlcv"
    candle_id = Column(Integer, primary_key=True)
    exchange = Column(String(20)) # من الرسمة
    timestamp = Column(DateTime, nullable=False)
    open = Column(DECIMAL(18, 8), nullable=False)
    high = Column(DECIMAL(18, 8), nullable=False)
    low = Column(DECIMAL(18, 8), nullable=False)
    close = Column(DECIMAL(18, 8), nullable=False)
    volume = Column(DECIMAL(20, 8), nullable=False)
    
    asset_id = Column(Integer, ForeignKey("crypto_assets.asset_id"))
    timeframe_id = Column(Integer, ForeignKey("timeframes.timeframe_id"))
    
    asset_ref = relationship("CryptoAsset", back_populates="candles")
    timeframe_ref = relationship("Timeframe", back_populates="candles")

# 6) جدول  (Prediction)

class Prediction(Base):
    __tablename__ = "prediction"
    id_Prediction = Column(Integer, primary_key=True) # الاسم حسب الرسمة
    asset = Column(String(20)) 
    timestamp = Column(DateTime(timezone=True))
    predicted_price = Column(Float, nullable=False)
    confidence = Column(Float)
    model_used = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())
    
    # الروابط الثلاثية حسب الرسمة
    user_id = Column(Integer, ForeignKey("users.user_id"))
    asset_id = Column(Integer, ForeignKey("crypto_assets.asset_id"))
    timeframe_id = Column(Integer, ForeignKey("timeframes.timeframe_id"))

    creator = relationship("User", back_populates="predictions")
    asset_ref = relationship("CryptoAsset", back_populates="predictions")
    timeframe_ref = relationship("Timeframe", back_populates="predictions")

# 7) جدول   (Model_Log)
class ModelLog(Base):
    __tablename__ = "model_logs"
    id = Column(Integer, primary_key=True)
    trained_at = Column(DateTime, default=func.now())
    records_count = Column(Integer)
    status = Column(String(20))
    error_message = Column(String(500))
    # ربط السجل بالمستخدم
    user_id = Column(Integer, ForeignKey("users.user_id"))
    user_ref = relationship("User", back_populates="model_logs")