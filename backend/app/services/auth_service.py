from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.db.models import User
from app.schemas.auth import UserLogin, UserRegister, Token
from app.core.logging import logger


class AuthService:
    """Authentication service for user login and registration"""
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User:
        """
        Authenticate user with username and password
        
        Args:
            db: Database session
            username: Username
            password: Plain password
            
        Returns:
            User object if authenticated
            
        Raises:
            HTTPException: If authentication fails
        """
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            logger.warning(f"Failed login attempt for username: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Invalid password for username: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            logger.warning(f"Inactive user login attempt: {username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        logger.info(f"User authenticated successfully: {username}")
        return user
    
    @staticmethod
    def create_token(user: User) -> Token:
        """
        Create JWT access token for user
        
        Args:
            user: User object
            
        Returns:
            Token object with access_token and token_type
        """
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )
        
        logger.info(f"Token created for user: {user.username}")
        
        return Token(
            access_token=access_token,
            token_type="bearer"
        )
    
    @staticmethod
    def register_user(db: Session, user_data: UserRegister) -> User:
        """
        Register a new user
        
        Args:
            db: Database session
            user_data: User registration data
            
        Returns:
            Created User object
            
        Raises:
            HTTPException: If username or email already exists
        """
        # Check if username exists
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            logger.warning(f"Registration failed - username exists: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email exists
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            logger.warning(f"Registration failed - email exists: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            is_active=True,
            is_superuser=False
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"New user registered: {user_data.username}")
        
        return db_user