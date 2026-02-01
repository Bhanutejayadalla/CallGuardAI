"""
Authentication Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import get_db
from app.core.config import settings
from app.api.schemas import UserCreate, UserResponse, Token, UserLogin
from app.models.user import User, UserRole

router = APIRouter()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current authenticated user"""
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require authenticated user"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not current_user.is_active:  # type: ignore[truthy-bool]
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require admin user"""
    if current_user.role != UserRole.ADMIN:  # type: ignore[truthy-bool]
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    # Check if user exists
    result = await db.execute(
        select(User).where(
            (User.email == user_data.email) | (User.username == user_data.username)
        )
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=UserRole.USER
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return UserResponse(
        id=int(user.id),  # type: ignore[arg-type]
        email=str(user.email),  # type: ignore[arg-type]
        username=str(user.username),  # type: ignore[arg-type]
        full_name=str(user.full_name) if user.full_name else None,  # type: ignore[arg-type]
        role=user.role.value,
        is_active=bool(user.is_active),  # type: ignore[arg-type]
        preferred_language=str(user.preferred_language),  # type: ignore[arg-type]
        dark_mode=bool(user.dark_mode),  # type: ignore[arg-type]
        created_at=user.created_at  # type: ignore[arg-type]
    )


@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login and get access token"""
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, str(user.hashed_password)):  # type: ignore[arg-type]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:  # type: ignore[truthy-bool]
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Update last login
    user.last_login = datetime.utcnow()  # type: ignore[assignment]
    await db.commit()
    
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value}
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=Token)
async def login_json(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login with JSON body"""
    result = await db.execute(
        select(User).where(User.username == credentials.username)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, str(user.hashed_password)):  # type: ignore[arg-type]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:  # type: ignore[truthy-bool]
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Update last login
    user.last_login = datetime.utcnow()  # type: ignore[assignment]
    await db.commit()
    
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value}
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user profile"""
    return UserResponse(
        id=int(current_user.id),  # type: ignore[arg-type]
        email=str(current_user.email),  # type: ignore[arg-type]
        username=str(current_user.username),  # type: ignore[arg-type]
        full_name=str(current_user.full_name) if current_user.full_name else None,  # type: ignore[arg-type]
        role=current_user.role.value,
        is_active=bool(current_user.is_active),  # type: ignore[arg-type]
        preferred_language=str(current_user.preferred_language),  # type: ignore[arg-type]
        dark_mode=bool(current_user.dark_mode),  # type: ignore[arg-type]
        created_at=current_user.created_at  # type: ignore[arg-type]
    )


@router.put("/me/preferences")
async def update_preferences(
    dark_mode: Optional[bool] = None,
    preferred_language: Optional[str] = None,
    notification_enabled: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user preferences"""
    if dark_mode is not None:
        current_user.dark_mode = dark_mode  # type: ignore[assignment]
    if preferred_language is not None:
        current_user.preferred_language = preferred_language  # type: ignore[assignment]
    if notification_enabled is not None:
        current_user.notification_enabled = notification_enabled  # type: ignore[assignment]
    
    current_user.updated_at = datetime.utcnow()  # type: ignore[assignment]
    await db.commit()
    
    return {"message": "Preferences updated successfully"}
