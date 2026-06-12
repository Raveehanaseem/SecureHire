"""
task_service/schemas.py
-----------------------
Pydantic v2 request and response models for the SecureHire Task Service.

The Task Service manages job listings and candidate applications.
Every field arriving from an external caller is validated here before
any database operation.

Satisfies:
  - SRD requirement INPUT-01 (all input validated via Pydantic)
  - SRD requirement INPUT-03 (field-level maximum length constraints)
  - OWASP ASVS v5.0 V5.1.1, V5.1.3, V5.3.4
"""

import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Printable ASCII only -- prevents injection of control characters.
SAFE_STRING_PATTERN = re.compile(r"^[\x20-\x7E\n\r]+$")

# Printable ASCII, no newlines -- suitable for single-line fields like titles.
SAFE_LINE_PATTERN = re.compile(r"^[\x20-\x7E]+$")

# Allowed characters in phone numbers: digits, spaces, +, (, ), -.
PHONE_PATTERN = re.compile(r"^[0-9\s\+\(\)\-]{7,20}$")


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class ApplicationStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    SHORTLISTED = "shortlisted"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    REJECTED = "rejected"
    OFFER_MADE = "offer_made"
    WITHDRAWN = "withdrawn"


class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"


# ---------------------------------------------------------------------------
# Job Listing schemas
# ---------------------------------------------------------------------------

class JobListingCreate(BaseModel):
    """
    Body model for POST /jobs.
    Used by Hiring Managers to create a new job listing.
    """

    title: str = Field(
        min_length=3,
        max_length=150,
        description="Job title, e.g. 'Senior Python Developer'.",
    )
    department: str = Field(
        min_length=2,
        max_length=100,
        description="Organisational department, e.g. 'Engineering'.",
    )
    location: str = Field(
        min_length=2,
        max_length=150,
        description="Office location or 'Remote'.",
    )
    description: str = Field(
        min_length=20,
        max_length=5000,
        description="Full job description including responsibilities and requirements.",
    )
    salary_range: Optional[str] = Field(
        default=None,
        max_length=60,
        description="Optional salary range, e.g. '40,000 - 55,000 GBP'.",
    )
    employment_type: EmploymentType = Field(
        description="Employment type for this position.",
    )

    @field_validator("title", "department", "location")
    @classmethod
    def validate_single_line(cls, v: str) -> str:
        if not SAFE_LINE_PATTERN.match(v):
            raise ValueError("Field must contain printable characters only, with no newlines.")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        if not SAFE_STRING_PATTERN.match(v):
            raise ValueError("Description contains invalid characters.")
        return v

    @field_validator("salary_range")
    @classmethod
    def validate_salary_range(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not SAFE_LINE_PATTERN.match(v):
            raise ValueError("Salary range must contain printable characters only.")
        return v


class JobListingUpdate(BaseModel):
    """
    Body model for PATCH /jobs/{job_id}.
    All fields are optional; only provided fields are updated.
    """

    title: Optional[str] = Field(default=None, min_length=3, max_length=150)
    department: Optional[str] = Field(default=None, min_length=2, max_length=100)
    location: Optional[str] = Field(default=None, min_length=2, max_length=150)
    description: Optional[str] = Field(default=None, min_length=20, max_length=5000)
    salary_range: Optional[str] = Field(default=None, max_length=60)
    employment_type: Optional[EmploymentType] = Field(default=None)
    is_open: Optional[bool] = Field(default=None, description="Set to false to close the listing.")

    @field_validator("title", "department", "location", "salary_range")
    @classmethod
    def validate_single_line_optional(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not SAFE_LINE_PATTERN.match(v):
            raise ValueError("Field must contain printable characters only, with no newlines.")
        return v

    @field_validator("description")
    @classmethod
    def validate_description_optional(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not SAFE_STRING_PATTERN.match(v):
            raise ValueError("Description contains invalid characters.")
        return v


class JobListingResponse(BaseModel):
    """Public-facing job listing representation."""

    id: int
    title: str
    department: str
    location: str
    description: str
    salary_range: Optional[str]
    employment_type: EmploymentType
    is_open: bool
    owner_id: int

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Application schemas
# ---------------------------------------------------------------------------

class ApplicationCreate(BaseModel):
    """
    Body model for POST /applications.
    Submitted by Candidates applying for a job listing.
    """

    job_id: int = Field(
        gt=0,
        description="ID of the job listing being applied for.",
    )
    cover_letter: str = Field(
        min_length=50,
        max_length=3000,
        description="Cover letter text.",
    )
    phone_number: Optional[str] = Field(
        default=None,
        description="Contact phone number.",
    )
    linkedin_url: Optional[str] = Field(
        default=None,
        max_length=200,
        description="LinkedIn profile URL.",
    )
    portfolio_url: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Portfolio or personal website URL.",
    )

    @field_validator("cover_letter")
    @classmethod
    def validate_cover_letter(cls, v: str) -> str:
        if not SAFE_STRING_PATTERN.match(v):
            raise ValueError("Cover letter contains invalid characters.")
        return v

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not PHONE_PATTERN.match(v):
            raise ValueError(
                "Phone number must be 7-20 characters containing only digits, "
                "spaces, +, (, ), and -."
            )
        return v

    @field_validator("linkedin_url", "portfolio_url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not (v.startswith("https://") or v.startswith("http://")):
                raise ValueError("URL must begin with http:// or https://")
            if not SAFE_LINE_PATTERN.match(v):
                raise ValueError("URL contains invalid characters.")
        return v


class ApplicationStatusUpdate(BaseModel):
    """
    Body model for PATCH /applications/{application_id}/status.
    Used by Hiring Managers to progress an application through the pipeline.
    """

    status: ApplicationStatus = Field(
        description="New pipeline status for this application.",
    )
    interviewer_note: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional note from the interviewer or hiring manager.",
    )

    @field_validator("interviewer_note")
    @classmethod
    def validate_note(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not SAFE_STRING_PATTERN.match(v):
            raise ValueError("Note contains invalid characters.")
        return v


class ApplicationResponse(BaseModel):
    """Public-facing application representation."""

    id: int
    job_id: int
    applicant_id: int
    cover_letter: str
    phone_number: Optional[str]
    linkedin_url: Optional[str]
    portfolio_url: Optional[str]
    status: ApplicationStatus
    interviewer_note: Optional[str]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Pagination / query parameter schema
# ---------------------------------------------------------------------------

class PaginationParams(BaseModel):
    """
    Query parameter model for paginated list endpoints.
    Validated using FastAPI's Depends() injection.
    """

    page: int = Field(default=1, ge=1, description="Page number, starting from 1.")
    page_size: int = Field(default=20, ge=1, le=100, description="Results per page, max 100.")
