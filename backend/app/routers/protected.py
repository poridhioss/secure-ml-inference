from fastapi import APIRouter, Depends, Request
from app.db.models import User
from app.dependencies.auth_dependencies import get_current_active_user
from app.core.config import settings
from app.core.logging import logger
import socket

router = APIRouter(
    prefix="/protected",
    tags=["Protected Routes"]
)


@router.get("/")
async def protected_root(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """
    Protected endpoint - requires JWT authentication
    
    Returns instance information and user details
    """
    logger.info(f"Protected root accessed by: {current_user.username}")
    
    return {
        "message": f"Hello {current_user.username} from {settings.INSTANCE_ID}!",
        "instance_id": settings.INSTANCE_ID,
        "hostname": socket.gethostname(),
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name
        },
        "client_ip": request.headers.get("X-Real-IP", request.client.host if request.client else "unknown"),
    }


@router.get("/data")
async def protected_data(
    current_user: User = Depends(get_current_active_user)
):
    """
    Protected data endpoint - requires JWT authentication
    
    Returns sample data with instance information
    """
    logger.info(f"Protected data accessed by: {current_user.username}")
    
    return {
        "data": [
            {"id": 1, "value": "Protected Item 1", "owner": current_user.username},
            {"id": 2, "value": "Protected Item 2", "owner": current_user.username},
            {"id": 3, "value": "Protected Item 3", "owner": current_user.username}
        ],
        "served_by": settings.INSTANCE_ID,
        "hostname": socket.gethostname(),
        "user_id": current_user.id
    }


@router.get("/admin")
async def admin_only(
    current_user: User = Depends(get_current_active_user)
):
    """
    Admin-only endpoint - requires superuser privileges
    
    Demonstrates role-based access control
    """
    if not current_user.is_superuser:
        logger.warning(f"Unauthorized admin access attempt by: {current_user.username}")
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    logger.info(f"Admin endpoint accessed by: {current_user.username}")
    
    return {
        "message": "Welcome to admin area",
        "instance_id": settings.INSTANCE_ID,
        "user": current_user.username,
        "privileges": "superuser"
    }