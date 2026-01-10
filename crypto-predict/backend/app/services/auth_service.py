#3. ملف app/services/auth_service.py (المنطق البرمجي)
from sqlalchemy.orm import Session
from app.db.models import User
from app.schemas.user_schema import UserCreate
from passlib.context import CryptContext
from datetime import date, datetime, timedelta  
from jose import jwt
from app.core.config import get_settings
###############
#- تشفير كلمة المرور

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def register_user(user_data: UserCreate, db: Session) -> User:
    if db.query(User).filter(User.email == user_data.email).first():
        raise ValueError("Email already registered.")

    hashed_pw = hash_password(user_data.password)
    
    new_user = User(
        User_Name=user_data.User_Name, 
        email=user_data.email,
        password_hash=hashed_pw,
        created_at=date.today() 
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def login_user(email: str, password: str, db: Session) -> str:
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not verify_password(password, user.password_hash):
        raise ValueError("Invalid email or password.")  

    return create_access_token({"sub": user.email})