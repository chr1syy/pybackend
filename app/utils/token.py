import jwt
import uuid

from sqlalchemy.orm import Session
from fastapi import HTTPException

from datetime import datetime, timedelta
from app.models import User, RefreshToken

from app.core.settings import settings

def create_access_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": email,
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)

def create_refresh_token(email: str, db: Session):
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": email, 
        "exp": expire, 
        "type": "refresh",
        "jti": str(uuid.uuid4())  # eindeutige ID
       }
    
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)

    # User sauber holen
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{email}' not found")

    db_token = RefreshToken(
        token=token,
        expires_at=expire,
        user_id=user.id,
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return token