from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.db import get_db
from app.models import AuditLog, User
from app.auth.utils import require_role

router = APIRouter()

@router.get("/logs")
def get_audit_logs(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    limit: int = 100
):
    """
    Admin-Endpoint zum Abrufen von AuditLogs.
    Filterbar nach user_id, action, Zeitraum.
    """
    query = db.query(AuditLog)

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    if start:
        query = query.filter(AuditLog.timestamp >= start)
    if end:
        query = query.filter(AuditLog.timestamp <= end)

    logs: List[AuditLog] = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "ip_address": log.ip_address,
            "timestamp": log.timestamp.isoformat(),
        }
        for log in logs
    ]
