# scripts/reset_test_db.py
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.utils.db import SessionLocal, Base, engine
from app.models import User, RefreshToken, AuditLog, AccessCode, PasswordResetToken

def reset_db():
    # Schema komplett leeren
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE;"))
        conn.execute(text("CREATE SCHEMA public;"))
        conn.commit()

    # Tabellen neu anlegen
    Base.metadata.create_all(bind=engine)

    # Optional: sicherstellen, dass keine alten Daten übrig sind
    db: Session = SessionLocal()
    db.query(RefreshToken).delete()
    db.query(User).delete()
    db.query(AuditLog).delete()
    db.query(AccessCode).delete()
    db.query(PasswordResetToken).delete()
    db.commit()
    db.close()

if __name__ == "__main__":
    reset_db()
