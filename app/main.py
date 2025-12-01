from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.routes import router as auth_router
from app.audit.routes import router as audit_router
from app.user.routes import router as user_router
import asyncio
import os
from app.cleanup import cleanup_expired_tokens
from app.audit.middleware import AuditMiddleware

app = FastAPI()

origins = os.getenv("CORS_ORIGINS", "").split(",")

@app.on_event("startup")
async def start_cleanup_task():
    async def run_cleanup():
        while True:
            cleanup_expired_tokens()
            await asyncio.sleep(3600)  # alle 60 Minuten
    asyncio.create_task(run_cleanup())

# Middleware aktivieren
app.add_middleware(AuditMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # oder ["*"] für alle
    allow_credentials=True,
    allow_methods=["*"],            # GET, POST, PUT, DELETE etc.
    allow_headers=["*"],            # z. B. Authorization
)

# Routen einbinden
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(audit_router, prefix="/audit", tags=["audit"])
app.include_router(user_router, prefix="/users", tags=["users"])

@app.get("/health")
def healthcheck():
    return {"status": "ok"}
