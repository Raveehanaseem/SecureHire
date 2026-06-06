"""
Authentication Dependencies & RBAC
- OAuth2 Bearer token extraction
- Role-Based Access Control (Admin, Employer, Applicant)
- OPA-style policy enforcement
CYC386 Requirement: RBAC/ABAC + OPA policies
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from enum import Enum
from typing import Optional
import logging

from database import get_db
from auth.jwt_handler import decode_token, verify_token_type
from cache.redis_client import get_redis
from models.user import User

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class Role(str, Enum):
    ADMIN = "admin"
    EMPLOYER = "employer"
    APPLICANT = "applicant"


# ─── OPA-style Policy Definitions ─────────────────────────────────────────────
ROLE_PERMISSIONS = {
    Role.ADMIN: {
        "users": ["read", "write", "delete"],
        "jobs": ["read", "write", "delete", "approve"],
        "applications": ["read", "write", "delete"],
        "dashboard": ["read"],
    },
    Role.EMPLOYER: {
        "jobs": ["read", "write", "delete"],
        "applications": ["read"],
        "dashboard": ["read"],
    },
    Role.APPLICANT: {
        "jobs": ["read"],
        "applications": ["read", "write"],
        "profile": ["read", "write"],
    },
}


def check_permission(role: Role, resource: str, action: str) -> bool:
    """OPA-style permission check"""
    permissions = ROLE_PERMISSIONS.get(role, {})
    allowed_actions = permissions.get(resource, [])
    return action in allowed_actions


async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
) -> User:
    """Extract and validate current user from JWT"""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode token
    payload = decode_token(token)

    if not verify_token_type(payload, "access"):
        raise credentials_exception

    user_id: Optional[str] = payload.get("sub")
    jti: Optional[str] = payload.get("jti")

    if user_id is None:
        raise credentials_exception

    # Check token blacklist (logout tokens)
    is_blacklisted = await redis.get(f"blacklist:token:{jti}")
    if is_blacklisted:
        raise credentials_exception

    # Fetch user from DB
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(*roles: Role):
    """Role-based access control decorator"""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in [r.value for r in roles]:
            logger.warning(
                f"Unauthorized access attempt | User: {current_user.id} | "
                f"Role: {current_user.role} | Required: {roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return role_checker


# Convenience dependencies
require_admin = require_role(Role.ADMIN)
require_employer = require_role(Role.EMPLOYER, Role.ADMIN)
require_applicant = require_role(Role.APPLICANT, Role.ADMIN)
