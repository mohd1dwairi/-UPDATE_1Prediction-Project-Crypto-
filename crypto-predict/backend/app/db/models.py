from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Boolean, JSON, UniqueConstraint, Index, func
from sqlalchemy.orm import relationship
from datetime import date
from app.db.session import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    User_Name = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(Date, default=date.today)
    predictions = relationship("Prediction", back_populates="creator")
    role = Column(String, default="user") # إضافة هذا السطر (القيمة الافتراضية مستخدم عادي)

class Candle(Base):
    __tablename__ = "candle_ohlcv"
    iid = Column(Integer, primary_key=True)
    asset = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    __table_args__ = (UniqueConstraint("asset", "timestamp", name="uq_candle_asset_ts"),)

class Sentiment(Base):
    __tablename__ = "sentiments"

    id = Column(Integer, primary_key=True)
    asset = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # الأعمدة الـ 9 الخاصة بالمشاعر (مطابقة تماماً لملف CSV)
    sent_count = Column(Integer, default=0)
    avg_sentiment = Column(Float, default=0.0)
    pos_count = Column(Integer, default=0)
    neg_count = Column(Integer, default=0)
    neu_count = Column(Integer, default=0)
    pos_ratio = Column(Float, default=0.0)
    neg_ratio = Column(Float, default=0.0)
    neu_ratio = Column(Float, default=0.0)
    has_news = Column(Integer, default=0)

    # لمنع تكرار نفس الساعة لنفس العملة
    __table_args__ = (
        UniqueConstraint("asset", "timestamp", name="uq_sent_asset_ts"),
    )

class Prediction(Base):
    __tablename__ = "prediction"
    id = Column(Integer, primary_key=True)
    asset = Column(String(20), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    predicted_price = Column(Float, nullable=False)
    model_used = Column(String(50))
    confidence = Column(String(10))
    created_by_user_id = Column(Integer, ForeignKey("users.user_id"))
    creator = relationship("User", back_populates="predictions")