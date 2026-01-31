from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import Token, UserLogin, UserRegister
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.core.logging import logger

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    - **email**: User email (must be unique)
    - **username**: Username (must be unique)
    - **password**: User password (will be hashed)
    - **full_name**: Optional full name
    """
    logger.info(f"Registration request for username: {user_data.username}")
    user = AuthService.register_user(db, user_data)
    return user


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with username and password
    
    - **username**: Username
    - **password**: Password
    
    Returns JWT access token
    """
    logger.info(f"Login request for username: {credentials.username}")
    
    # Authenticate user
    user = AuthService.authenticate_user(db, credentials.username, credentials.password)
    
    # Create access token
    token = AuthService.create_token(user)
    
    return token