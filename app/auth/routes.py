import secrets
import jwt

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm

from datetime import datetime, timedelta

from passlib.context import CryptContext

from app.schemas.password import ChangePasswordRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.schemas.registration import CompleteRegistrationRequest
from app.schemas.auth import RefreshTokenRequest, LoginRequest

from app.models import User, RefreshToken, AccessCode

from app.core.settings import settings
from app.utils.mail import send_email
from app.utils.audit import log_action
from app.utils.token import (
    create_access_token,
    create_refresh_token
)
from app.utils.db import get_db
from app.utils.auth import (
    oauth2_scheme,
    get_current_user,
    require_role
)


router = APIRouter()

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    # Suche nach E-Mail statt Username
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not pwd_context.verify(req.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Tokens mit E-Mail als subject
    access_token = create_access_token(user.email)
    refresh_token = create_refresh_token(user.email, db)

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
        payload = jwt.decode(refresh_token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        email = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Alten Refresh‑Token löschen (Rotation!)
    db.delete(db_token)
    db.commit()

    # Neuen Access‑Token + neuen Refresh‑Token erstellen
    new_access_token = create_access_token(email)
    new_refresh_token = create_refresh_token(email, db)

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
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True}  # <--- Ablaufzeit prüfen
        )
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        email = payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
    }

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

@router.post("/invite")
def invite_user(
    email: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin"))
):
    # Prüfen ob Mail schon existiert
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    # Zugangscode erstellen
    code = secrets.token_urlsafe(16)
    access_code = AccessCode(
        code=code,
        purpose="registration",
        expires_at=datetime.utcnow() + timedelta(hours=24),
        user_id=None
    )
    db.add(access_code)
    db.commit()

    # Mailversand als BackgroundTask
    background_tasks.add_task(
        send_email,
        to=email,
        subject="Einladung zur Registrierung",
        body=f"Bitte registriere dich mit folgendem Code: {code}"
    )

    # Audit
    log_action(db, admin.id, "invite_sent", details={"email": email})

    return {"detail": f"Invitation sent to {email}"}

@router.post("/complete-registration")
def complete_registration(
    req: CompleteRegistrationRequest,
    db: Session = Depends(get_db)
):
    # Code prüfen
    access_code = db.query(AccessCode).filter(
        AccessCode.code == req.code,
        AccessCode.purpose == "registration",
        AccessCode.expires_at > datetime.utcnow(),
        AccessCode.used == False
    ).first()
    if not access_code:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    # Prüfen ob Mail schon existiert
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    # User anlegen
    new_user = User(
        email=req.email,
        username=req.username,
        hashed_password=pwd_context.hash(req.password),
        role="user",
        is_active=True,
        email_verified=True,  # da Einladung über Mail
        created_at=datetime.utcnow()
    )
    db.add(new_user)

    # Code als benutzt markieren
    access_code.used = True
    db.commit()
    db.refresh(new_user)

    # Audit
    log_action(db, new_user.id, "registration_completed")

    return {"detail": f"User {req.email} registered successfully"}

@router.post("/forgot-password")
def forgot_password(
    req: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Reset‑Token erstellen
    code = secrets.token_urlsafe(16)
    reset_token = AccessCode(
        code=code,
        purpose="password_reset",
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(hours=1),
        used=False
    )
    db.add(reset_token)
    db.commit()

    # Mail verschicken
    background_tasks.add_task(
        send_email,
        to=req.email,
        subject="Passwort zurücksetzen",
        body=f"Ihr Reset‑Code lautet: {code}"
    )

    log_action(db, user.id, "password_reset_requested", details={"email": req.email})
    return {"detail": "Password reset email sent"}

@router.post("/reset-password")
def reset_password(
    req: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    token = db.query(AccessCode).filter(
        AccessCode.code == req.code,
        AccessCode.purpose == "password_reset",
        AccessCode.expires_at > datetime.utcnow(),
        AccessCode.used == False
    ).first()

    if not token:
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")

    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Passwort setzen
    user.hashed_password = pwd_context.hash(req.new_password)
    token.used = True
    db.commit()

    log_action(db, user.id, "password_reset_completed")
    return {"detail": "Password has been reset successfully"}
