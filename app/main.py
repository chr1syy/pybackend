from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.audit.routes import router as audit_router
import asyncio
from app.cleanup import cleanup_expired_tokens
from app.audit.middelware import AuditMiddleware

app = FastAPI()

@app.on_event("startup")
async def start_cleanup_task():
    async def run_cleanup():
        while True:
            cleanup_expired_tokens()
            await asyncio.sleep(3600)  # alle 60 Minuten
    asyncio.create_task(run_cleanup())

# Middleware aktivieren
app.add_middleware(AuditMiddleware)

# Routen einbinden
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(audit_router, prefix="/audit", tags=["audit"])

@app.get("/health")
def healthcheck():
    return {"status": "ok"}
