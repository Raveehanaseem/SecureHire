"""
auth_service/schemas.py
-----------------------
Pydantic v2 request and response models for the SecureHire Auth Service.

Every field that arrives from an external caller is validated here before
any business logic runs.  This satisfies:
  - SRD requirement AUTH-06 (email format, minimum password length)
  - SRD requirement INPUT-01 (all input validated via Pydantic)
  - OWASP ASVS v5.0 V2.1.1, V2.1.2, V5.1.3
"""

import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Regex: printable ASCII only, no control characters.
SAFE_STRING_PATTERN = re.compile(r"^[\x20-\x7E]+$")

# Regex: basic username -- letters, digits, hyphens, underscores.
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_\-]+$")


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class UserRole(str, Enum):
    CANDIDATE = "candidate"
    HIRING_MANAGER = "hiring_manager"
    ADMINISTRATOR = "administrator"


# ---------------------------------------------------------------------------
# Authentication schemas
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    """
    Body model for POST /auth/register.

    Validation rules applied (all enforced before any database call):
      - username:  3-50 characters, letters/digits/hyphens/underscores only
      - email:     valid RFC 5322 email address
      - password:  12-128 characters (ASVS V2.1.1 and V2.1.2)
                   must contain at least one uppercase letter,
                   one lowercase letter, one digit, and one special character
      - full_name: 1-120 printable ASCII characters; optional
    """

    username: str = Field(
        min_length=3,
        max_length=50,
        description="Unique username for the account.",
    )
    email: EmailStr = Field(
        description="Valid email address used for login.",
    )
    password: str = Field(
        min_length=12,
        max_length=128,
        description="Password must be 12-128 characters and meet complexity rules.",
    )
    full_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=120,
        description="Optional display name.",
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not USERNAME_PATTERN.match(v):
            raise ValueError(
                "Username may only contain letters, digits, hyphens, "
                "and underscores."
            )
        return v

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        errors = []
        if not any(c.isupper() for c in v):
            errors.append("at least one uppercase letter")
        if not any(c.islower() for c in v):
            errors.append("at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            errors.append("at least one digit")
        if not any(c in r"!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in v):
            errors.append("at least one special character")
        if errors:
            raise ValueError(
                "Password must contain " + ", ".join(errors) + "."
            )
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not SAFE_STRING_PATTERN.match(v):
            raise ValueError("Full name must contain printable ASCII characters only.")
        return v


class LoginRequest(BaseModel):
    """
    Body model for POST /auth/login.

    Both fields are deliberately kept simple here; granular error messages
    are intentionally suppressed at the handler level to prevent user
    enumeration (ASVS V2.9.1, SRD AUTH-05).
    """

    email: EmailStr = Field(
        description="Registered email address.",
    )
    password: str = Field(
        min_length=1,
        max_length=128,
        description="Account password.",
    )


class ChangePasswordRequest(BaseModel):
    """
    Body model for POST /auth/change-password.

    Requires both the current password and the new password to prevent
    session-hijacking-based password changes (ASVS V2.1.6).
    """

    current_password: str = Field(
        min_length=1,
        max_length=128,
        description="The user's existing password.",
    )
    new_password: str = Field(
        min_length=12,
        max_length=128,
        description="Replacement password; must meet all complexity rules.",
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password_complexity(cls, v: str) -> str:
        errors = []
        if not any(c.isupper() for c in v):
            errors.append("at least one uppercase letter")
        if not any(c.islower() for c in v):
            errors.append("at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            errors.append("at least one digit")
        if not any(c in r"!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in v):
            errors.append("at least one special character")
        if errors:
            raise ValueError(
                "New password must contain " + ", ".join(errors) + "."
            )
        return v

    @model_validator(mode="after")
    def passwords_must_differ(self) -> "ChangePasswordRequest":
        if self.current_password == self.new_password:
            raise ValueError(
                "New password must be different from the current password."
            )
        return self


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class TokenResponse(BaseModel):
    """
    Response returned by /auth/login and /auth/refresh.
    The access_token is a signed JWT.  The token_type is always 'bearer'.
    """

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(
        description="Token lifetime in seconds.",
    )


class UserResponse(BaseModel):
    """
    Public-facing user representation.  Password hash and internal IDs
    are never included in this model.
    """

    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole

    class Config:
        from_attributes = True
