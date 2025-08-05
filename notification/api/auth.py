from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from services.auth import (
    authenticate_user, 
    create_access_token, 
    get_current_active_user
)
from config.settings import settings
from models import get_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """Login endpoint to get JWT token."""
    user = await authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(
        minutes=settings.access_token_expire_minutes
    )
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user = Depends(get_current_active_user)
):
    """Get current user information."""
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser
    }


@router.post("/register")
async def register_user(
    username: str,
    email: str,
    password: str,
    full_name: str = None
):
    """Register new user (for development/testing)."""
    User = get_user()
    
    # Check if user already exists
    existing_user = await User.find_one(
        {"$or": [{"username": username}, {"email": email}]}
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new user
    from services.auth import get_password_hash
    hashed_password = get_password_hash(password)
    
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        full_name=full_name or username
    )
    await user.commit()
    
    return {"message": "User created successfully", "user_id": str(user.id)} 