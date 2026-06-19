"""
Authentication API Router - FIXED (slowapi Response parameter added)
CYC386 - SecureHire
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr, field_validator
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
import logging

from database import get_db
from models.user import User
from auth.jwt_handler import create_access_token, create_refresh_token, decode_token, verify_token_type
from auth.dependencies import get_current_user
from cache.redis_client import get_redis
from middleware.security import sanitize_input
from middleware.rate_limit import limiter
from config import settings
from utils.metrics import failed_logins_total
from utils.anomaly_detection import detector as anomaly_detector

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "applicant"

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v):
        v = sanitize_input(v)
        if len(v) < 2 or len(v) > 100:
            raise ValueError("Name must be 2-100 characters")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain a digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in v):
            raise ValueError("Password must contain a special character")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        allowed = ["applicant", "employer"]
        if v not in allowed:
            raise ValueError(f"Role must be one of: {allowed}")
        return v


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    role: str
    full_name: str


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    response: Response,
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == body.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    hashed_pw = pwd_context.hash(body.password)
    user = User(
        email=body.email,
        hashed_password=hashed_pw,
        full_name=body.full_name,
        role=body.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    logger.info(f"New user registered | ID: {user.id} | Role: {user.role}")
    return {"message": "Registration successful", "user_id": str(user.id)}


@router.post("/login", response_model=LoginResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if user and user.locked_until:
        if datetime.now(timezone.utc) < user.locked_until:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account temporarily locked. Try again later."
            )
        else:
            user.locked_until = None
            user.failed_login_attempts = "0"

    if not user or not user.hashed_password or not pwd_context.verify(form_data.password, user.hashed_password):
        if user:
            attempts = int(user.failed_login_attempts or "0") + 1
            user.failed_login_attempts = str(attempts)
            if attempts >= MAX_FAILED_ATTEMPTS:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_MINUTES)
                logger.warning(f"Account locked | User: {user.id}")
            await db.commit()
        client_ip = request.client.host if request.client else "unknown"
        logger.warning(f"Failed login | IP: {client_ip}")
        failed_logins_total.labels(ip=client_ip).inc()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    user.failed_login_attempts = "0"
    user.locked_until = None
    await db.commit()

    # Feed the login into the anomaly detector (IP-switching / off-hours checks)
    anomaly_detector.record_login(str(user.id), request.client.host if request.client else "unknown")

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token(str(user.id))

    await redis.setex(
        f"refresh:{str(user.id)}",
        settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        refresh_token
    )

    logger.info(f"User logged in | ID: {user.id}")
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=str(user.id),
        role=user.role,
        full_name=user.full_name,
    )


@router.post("/refresh")
@limiter.limit("10/minute")
async def refresh_token(
    request: Request,
    response: Response,
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    payload = decode_token(body.refresh_token)
    if not verify_token_type(payload, "refresh"):
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = payload.get("sub")
    stored = await redis.get(f"refresh:{user_id}")
    if not stored or stored != body.refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token invalid or expired")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    new_access = create_access_token({"sub": str(user.id), "role": user.role})
    new_refresh = create_refresh_token(str(user.id))

    await redis.setex(
        f"refresh:{user_id}",
        settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        new_refresh
    )
    return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    redis=Depends(get_redis),
):
    await redis.delete(f"refresh:{str(current_user.id)}")
    logger.info(f"User logged out | ID: {current_user.id}")
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }
