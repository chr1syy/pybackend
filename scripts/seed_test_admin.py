from sqlalchemy.orm import Session
from app.db import SessionLocal, Base, engine
from app.models import User, RefreshToken
from passlib.hash import argon2

def seed_admin():
    Base.metadata.create_all(bind=engine)  # falls Tabellen fehlen
    db: Session = SessionLocal()

    # Alle RefreshTokens löschen
    deleted_tokens = db.query(RefreshToken).delete()
    db.commit()
    print(f"Deleted {deleted_tokens} refresh tokens")

    # Alle User löschen
    deleted_users = db.query(User).delete()
    db.commit()
    print(f"Deleted {deleted_users} users")

    # Admin neu anlegen
    admin = User(
        username="admin",
        hashed_password=argon2.hash("admin"),
        role="admin"
    )
    db.add(admin)
    db.commit()
    print("Admin user created")

    db.close()

if __name__ == "__main__":
    seed_admin()
