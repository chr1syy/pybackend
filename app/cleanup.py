from datetime import datetime
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import RefreshToken

def cleanup_expired_tokens():
    db: Session = SessionLocal()
    now = datetime.utcnow()
    deleted = db.query(RefreshToken).filter(RefreshToken.expires_at < now).delete()
    db.commit()
    db.close()
    print(f"Cleanup: {deleted} expired refresh tokens removed")
