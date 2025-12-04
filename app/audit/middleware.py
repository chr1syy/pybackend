from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from jose import JWTError, jwt
from datetime import datetime

from app.utils.db import SessionLocal
from app.models import AuditLog, User
from app.core.settings import settings



class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Defaultwerte
        user_id = None
        ip = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent")
        success = True
        details = {}

        # Versuche User aus Token zu extrahieren
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
                if payload.get("type") == "access":
                    email = payload.get("sub")  # JWT contains email, not username
                    db: Session = SessionLocal()
                    user = db.query(User).filter(User.email == email).first()
                    if user:
                        user_id = user.id
                    db.close()
            except JWTError as e:
                success = False
                details["jwt_error"] = str(e)

        # Request ausführen
        response = await call_next(request)

        # Nur relevante Endpoints loggen
        if request.url.path.startswith("/auth/"):
            db: Session = SessionLocal()

            log = AuditLog(
                user_id=user_id,
                action=f"{request.method} {request.url.path}",
                ip_address=ip,
                user_agent=user_agent,
                success=success and response.status_code < 400,
                details={
                    **details,
                    "status_code": response.status_code,
                    "query_params": dict(request.query_params),
                },
                timestamp=datetime.utcnow(),
            )
            db.add(log)
            db.commit()
            db.close()

        return response
