# scripts/seed_admin.py
from sqlalchemy.orm import Session

from app.utils.db import SessionLocal, Base, engine
from app.models import User, RefreshToken

from passlib.hash import argon2

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

        # Admin neu anlegen
        new_admin = User(
            username="admin",  # optional, für Anzeigezwecke
            email="admin@example.com",
            hashed_password=argon2.hash("admin"),
            role="admin",
            is_active=True,
            email_verified=True
        )
        db.add(new_admin)
        db.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")

    db.close()

if __name__ == "__main__":
    seed_admin()
