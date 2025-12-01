from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserSchema, UserUpdateSchema
from app.models import User
from passlib.context import CryptContext

from app.utils.utils import (
    create_access_token,
    create_refresh_token,
    get_db,
    oauth2_scheme,
    RefreshTokenRequest,
    RegisterRequest,
    get_current_user,
    require_role
)

router = APIRouter()

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Alle Benutzer abrufen (nur Admin)
@router.get("/", response_model=list[UserSchema])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    return db.query(User).all()

# Benutzer aktualisieren (z. B. Rolle ändern)
@router.put("/{user_id}", response_model=UserSchema)
def update_user(user_id: int, update: UserUpdateSchema, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role == "admin" and update.role != "admin":
        # Prüfen ob noch andere Admins existieren
        other_admins = db.query(User).filter(User.role == "admin", User.id != user.id).count()
        if other_admins == 0:
            raise HTTPException(
                status_code=400,
                detail="Es muss mindestens ein Admin im System bleiben"
            )
        
    if update.role:
        user.role = update.role
    db.commit()
    db.refresh(user)
    return user

# Benutzer löschen
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        # Admin selbst darf nicht gelöscht werden (optional)
    if user.username == "admin":
        raise HTTPException(status_code=403, detail="Cannot delete admin user")
    db.delete(user)
    db.commit()
    return {"detail": f"User {user.username} deleted"}

@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db), user: User = Depends(require_role("admin"))):

    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins can create new users"
       )
    
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
    return {"detail": f"User {request.username} created with role {request.role}"}
