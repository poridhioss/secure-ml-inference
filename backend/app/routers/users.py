from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.models import User
from app.schemas.user import UserResponse, UserUpdate
from app.dependencies.auth_dependencies import get_current_active_user
from app.services.user_service import UserService
from app.core.logging import logger

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information
    
    Requires: Valid JWT token
    """
    logger.info(f"User profile accessed: {current_user.username}")
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user information
    
    Requires: Valid JWT token
    """
    logger.info(f"User profile update requested: {current_user.username}")
    updated_user = UserService.update_user(db, current_user.id, user_update)
    return updated_user


@router.get("/", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get list of all users (paginated)
    
    Requires: Valid JWT token
    """
    logger.info(f"Users list requested by: {current_user.username}")
    users = UserService.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user by ID
    
    Requires: Valid JWT token
    """
    logger.info(f"User {user_id} info requested by: {current_user.username}")
    user = UserService.get_user_by_id(db, user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user