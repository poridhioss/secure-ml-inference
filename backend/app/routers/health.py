from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.core.config import settings
from app.core.logging import logger
import socket
from datetime import datetime

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


@router.get("/")
async def health_check():
    return {
        "status": "healthy",
        "instance_id": settings.INSTANCE_ID,
        "hostname": socket.gethostname(),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    status_info = {
        "status": "ready",
        "instance_id": settings.INSTANCE_ID,
        "hostname": socket.gethostname(),
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }

    # Check database
    try:
        db.execute(text("SELECT 1"))
        status_info["checks"]["database"] = "connected"
    except Exception as e:
        status_info["status"] = "not_ready"
        status_info["checks"]["database"] = f"error: {str(e)}"
        logger.error(f"Database health check failed: {str(e)}")

    # Check model
    from app.main import sentiment_model
    status_info["checks"]["model"] = "loaded" if sentiment_model else "not_loaded"

    return status_info


@router.get("/live")
async def liveness_check():
    return {
        "status": "alive",
        "instance_id": settings.INSTANCE_ID,
        "hostname": socket.gethostname(),
        "timestamp": datetime.utcnow().isoformat()
    }