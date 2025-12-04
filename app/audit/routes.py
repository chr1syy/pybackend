from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from typing import Optional, List
from datetime import datetime

from app.models import AuditLog, User
from app.utils.db import get_db
from app.utils.auth import require_role

router = APIRouter()

@router.get("/logs")
def get_audit_logs(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
    user_id: Optional[int] = Query(None, description="Filter nach User-ID"),
    action: Optional[str] = Query(None, description="Filter nach Aktion (Teilstring)"),
    ip_address: Optional[str] = Query(None, description="Filter nach IP-Adresse"),
    user_agent: Optional[str] = Query(None, description="Filter nach User-Agent"),
    success: Optional[bool] = Query(None, description="Filter nach Erfolg/Fehlschlag"),
    start: Optional[datetime] = Query(None, description="Startzeitpunkt"),
    end: Optional[datetime] = Query(None, description="Endzeitpunkt"),
    limit: int = Query(100, ge=1, le=1000, description="Maximale Anzahl Ergebnisse"),
):
    """
    Admin-Endpoint zum Abrufen von AuditLogs.
    Filterbar nach user_id, action, IP, UserAgent, Erfolg, Zeitraum.
    """
    query = db.query(AuditLog)

    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        # Escape special LIKE characters to prevent wildcard injection
        escaped_action = action.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        query = query.filter(AuditLog.action.ilike(f"%{escaped_action}%", escape='\\'))
    if ip_address:
        # Escape special LIKE characters to prevent wildcard injection
        escaped_ip = ip_address.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        query = query.filter(AuditLog.ip_address.ilike(f"%{escaped_ip}%", escape='\\'))
    if user_agent:
        # Escape special LIKE characters to prevent wildcard injection
        escaped_ua = user_agent.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        query = query.filter(AuditLog.user_agent.ilike(f"%{escaped_ua}%", escape='\\'))
    if success is not None:
        query = query.filter(AuditLog.success == success)
    if start:
        query = query.filter(AuditLog.timestamp >= start)
    if end:
        query = query.filter(AuditLog.timestamp <= end)

    logs: List[AuditLog] = (
        query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    )

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "success": log.success,
            "timestamp": log.timestamp.isoformat(),
            "details": log.details,
        }
        for log in logs
    ]
