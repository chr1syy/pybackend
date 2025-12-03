from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserSchema, UserUpdateSchema
from app.models import User
from passlib.context import CryptContext

from app.utils.db import get_db
from app.utils.auth import require_role

router = APIRouter()

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Alle Benutzer abrufen (nur Admin)
@router.get("/", response_model=list[UserSchema])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    return db.query(User).all()

# Benutzer aktualisieren (z. B. Rolle oder Aktivstatus ändern)
@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    user_id: int,
    update: UserUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == "admin" and update.role and update.role != "admin":
        other_admins = db.query(User).filter(User.role == "admin", User.id != user.id).count()
        if other_admins == 0:
            raise HTTPException(status_code=400, detail="Es muss mindestens ein Admin im System bleiben")

    # Neue Felder berücksichtigen
    for field, value in update.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user

# Benutzer löschen
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == "admin":
        raise HTTPException(status_code=403, detail="Cannot delete admin user")
    db.delete(user)
    db.commit()
    return {"detail": f"User {user.email} deleted"}

