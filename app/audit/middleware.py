from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import AuditLog, User
from jose import JWTError, jwt
import os


SECRET_KEY = os.getenv("JWT_SECRET", "changeme")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Nur relevante Endpoints loggen
        if request.url.path.startswith("/auth/"):
            db: Session = SessionLocal()
            user_id = None
            ip = request.client.host

            # Versuche User aus Token zu extrahieren
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                try:
                    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                    if payload.get("type") == "access":
                        username = payload.get("sub")
                        user = db.query(User).filter(User.username == username).first()
                        if user:
                            user_id = user.id
                except JWTError:
                    pass

            log = AuditLog(
                user_id=user_id,
                action=f"{request.method} {request.url.path}",
                ip_address=ip,
            )
            db.add(log)
            db.commit()
            db.close()

        return response
