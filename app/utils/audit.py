from datetime import datetime
from sqlalchemy.orm import Session
from app.models import AuditLog

def log_action(
    db: Session,
    user_id: int | None,
    action: str,
    success: bool = True,
    ip_address: str | None = None,
    user_agent: str | None = None,
    details: dict | None = None,
):
    """
    Hilfsfunktion zum Schreiben eines AuditLogs.
    """
    log = AuditLog(
        user_id=user_id,
        action=action,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        details=details,
        timestamp=datetime.utcnow(),
    )
    db.add(log)
    db.commit()
    return log
