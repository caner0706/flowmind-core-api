from datetime import datetime
import socket

from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    """Basit sağlık kontrolü endpoint'i."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"}


@router.get("/info")
async def info():
    """Uygulama hakkında temel bilgi."""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "env": settings.ENV,
        "hostname": socket.gethostname(),
    }
