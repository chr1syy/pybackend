# scripts/seed_admin.py
from sqlalchemy.orm import Session
import secrets
import string

from app.utils.db import SessionLocal, Base, engine
from app.models import User, RefreshToken

from passlib.hash import argon2

def generate_strong_password(length=16):
    """Generate a strong random password"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def seed_admin():
    # Tabellen sicherstellen
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    # Prüfen ob Admin existiert
    admin = db.query(User).filter_by(email="admin@example.com").first()
    if not admin:
        # Optional: alte Tokens/Users löschen (nur wenn gewünscht)
        db.query(RefreshToken).delete()
        db.query(User).delete()
        db.commit()

        # Generate strong random password
        admin_password = generate_strong_password(20)

        # Admin neu anlegen
        new_admin = User(
            username="admin",  # optional, für Anzeigezwecke
            email="admin@example.com",
            hashed_password=argon2.hash(admin_password),
            role="admin",
            is_active=True,
            email_verified=True
        )
        db.add(new_admin)
        db.commit()
        print("=" * 60)
        print("ADMIN USER CREATED")
        print("=" * 60)
        print(f"Email: admin@example.com")
        print(f"Password: {admin_password}")
        print("=" * 60)
        print("⚠️  IMPORTANT: Save this password securely and change it after first login!")
        print("=" * 60)
    else:
        print("Admin user already exists.")

    db.close()

if __name__ == "__main__":
    seed_admin()
