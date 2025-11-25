from datetime import datetime
import jwt
import os
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.password import ChangePasswordRequest, AdminChangePasswordRequest
from app.auth.utils import get_current_user, require_role
from passlib.context import CryptContext

from app.auth.utils import (
    create_access_token,
    create_refresh_token,
    get_db,
    oauth2_scheme,
    RefreshTokenRequest,
    RegisterRequest,
    require_role
)

from app.models import User, RefreshToken

SECRET_KEY = os.getenv("JWT_SECRET", "changeme")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

router = APIRouter()

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(user.username)
    refresh_token = create_refresh_token(user.username, db)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh")
def refresh(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    refresh_token = request.refresh_token

    # Token aus DB holen
    db_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Ablauf prüfen
    if db_token.expires_at < datetime.utcnow():
        db.delete(db_token)
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")

    # JWT prüfen
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        username = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Alten Refresh‑Token löschen (Rotation!)
    db.delete(db_token)
    db.commit()

    # Neuen Access‑Token + neuen Refresh‑Token erstellen
    new_access_token = create_access_token(username)
    new_refresh_token = create_refresh_token(username, db)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
def logout(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    refresh_token = request.refresh_token
    db_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if db_token:
        db.delete(db_token)
        db.commit()
    return {"msg": "Logout successful, refresh token revoked"}


@router.get("/me")
def read_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        username = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "username": user.username}

@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db), user: User = Depends(require_role("admin"))):
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        username=request.username,
        hashed_password=pwd_context.hash(request.password),
        role=request.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": f"User {request.username} created with role {request.role}"}

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int = Path(..., description="ID des zu löschenden Users"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin"))  # nur Admin darf löschen
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Admin selbst darf nicht gelöscht werden (optional)
    if user.username == "admin":
        raise HTTPException(status_code=403, detail="Cannot delete admin user")

    db.delete(user)
    db.commit()
    return {"msg": f"User {user.username} deleted successfully"}

@router.post("/change-password")
def change_password(
    req: ChangePasswordRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not pwd_context.verify(req.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid password or request")

    if pwd_context.verify(req.new_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="New password must differ from current")

    user.hashed_password = pwd_context.hash(req.new_password)
    db.add(user)
    db.commit()

    db.query(RefreshToken).filter(RefreshToken.user_id == user.id).delete()
    db.commit()

    return {"msg": "Password changed; all sessions invalidated"}

@router.post("/admin/change-password")
def admin_change_password(
    req: AdminChangePasswordRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin"))
):
    target = db.query(User).filter(User.id == req.user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    target.hashed_password = pwd_context.hash(req.new_password)
    db.add(target)
    db.commit()

    db.query(RefreshToken).filter(RefreshToken.user_id == target.id).delete()
    db.commit()

    return {"msg": f"Password updated for user_id={req.user_id}; sessions invalidated"}
