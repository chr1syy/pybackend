from datetime import datetime, timedelta
import jwt
import os
import uuid
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel

from app.db import get_db
from app.models import User, RefreshToken

SECRET_KEY = os.getenv("JWT_SECRET", "changeme")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "user"

def create_access_token(username: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": username,
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(username: str, db: Session):
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": username, 
        "exp": expire, 
        "type": "refresh",
        "jti": str(uuid.uuid4())  # eindeutige ID
       }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    # User sauber holen
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")

    db_token = RefreshToken(
        token=token,
        expires_at=expire,
        user_id=user.id,
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return token

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        username = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def require_role(required: str):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role != required:
            raise HTTPException(status_code=403, detail="Forbidden: insufficient role")
        return user
    return role_checker