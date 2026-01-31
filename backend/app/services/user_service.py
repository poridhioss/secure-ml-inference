from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.db.models import User
from app.schemas.user import UserUpdate
from app.core.security import get_password_hash
from app.core.logging import logger


class UserService:
    """User service for user management operations"""
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
        """
        Update user information
        
        Args:
            db: Database session
            user_id: User ID to update
            user_update: Updated user data
            
        Returns:
            Updated User object
            
        Raises:
            HTTPException: If user not found or validation fails
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields
        update_data = user_update.model_dump(exclude_unset=True)
        
        # Hash password if provided
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"User updated: {db_user.username}")
        
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """
        Delete user (soft delete by deactivating)
        
        Args:
            db: Database session
            user_id: User ID to delete
            
        Returns:
            True if successful
            
        Raises:
            HTTPException: If user not found
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db_user.is_active = False
        db.commit()
        
        logger.info(f"User deactivated: {db_user.username}")
        
        return True