"""
Applications API Router - FIXED
CYC386 - SecureHire
"""

from fastapi import APIRouter, Response, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel, field_validator
from typing import Optional
import logging

from database import get_db
from models.application import Application
from models.job import Job
from models.user import User
from auth.dependencies import get_current_user, require_employer, Role
from middleware.security import sanitize_input, validate_no_xss, validate_no_sqli
from middleware.rate_limit import limiter
from utils.encryption import encrypt_data, decrypt_data
from kafka.producer import emit_application_submitted, emit_application_status_changed

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/applications", tags=["Applications"])


class ApplicationCreate(BaseModel):
    job_id: str
    cover_letter: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("cover_letter")
    @classmethod
    def validate_cover_letter(cls, v):
        if v:
            v = sanitize_input(v)
            validate_no_xss(v)
            if len(v) > 5000:
                raise ValueError("Cover letter too long (max 5000 chars)")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v:
            import re
            if not re.match(r"^\+?[\d\s\-]{7,15}$", v):
                raise ValueError("Invalid phone number format")
        return v


class StatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        allowed = ["pending", "reviewing", "shortlisted", "rejected", "hired"]
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v


@router.post("/", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def apply_to_job(
    request: Request,
    response: Response,
    body: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in [Role.APPLICANT.value]:
        raise HTTPException(status_code=403, detail="Only applicants can apply")

    validate_no_sqli(body.job_id)

    result = await db.execute(
        select(Job).where(and_(Job.id == body.job_id, Job.is_approved == True))
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or not accepting applications")

    existing = await db.execute(
        select(Application).where(
            and_(Application.job_id == body.job_id, Application.applicant_id == current_user.id)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already applied to this job")

    cover_letter_enc = encrypt_data(body.cover_letter) if body.cover_letter else None
    phone_enc = encrypt_data(body.phone) if body.phone else None

    application = Application(
        job_id=body.job_id,
        applicant_id=current_user.id,
        cover_letter_encrypted=cover_letter_enc,
        phone_encrypted=phone_enc,
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)

    try:
        await emit_application_submitted(str(application.id), str(body.job_id), str(current_user.id))
    except Exception as e:
        logger.warning(f"Kafka skipped: {e}")

    logger.info(f"Application submitted | ID: {application.id} | Job: {body.job_id}")
    return {"message": "Application submitted successfully", "application_id": str(application.id)}


@router.get("/my")
async def my_applications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Application).where(Application.applicant_id == current_user.id)
    )
    apps = result.scalars().all()

    out = []
    for a in apps:
        job_res = await db.execute(select(Job).where(Job.id == a.job_id))
        job = job_res.scalar_one_or_none()
        out.append({
            "id": str(a.id),
            "job_id": str(a.job_id),
            "job_title": job.title if job else "Unknown",
            "company": job.company if job else "",
            "status": a.status,
            "created_at": a.created_at.isoformat(),
        })
    return out


@router.get("/job/{job_id}")
async def job_applications(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_employer),
):
    validate_no_sqli(job_id)

    job_result = await db.execute(select(Job).where(Job.id == job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if current_user.role != Role.ADMIN.value and str(job.employer_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not your job")

    result = await db.execute(
        select(Application).where(Application.job_id == job_id)
    )
    apps = result.scalars().all()

    out = []
    for a in apps:
        user_res = await db.execute(select(User).where(User.id == a.applicant_id))
        applicant = user_res.scalar_one_or_none()
        out.append({
            "id": str(a.id),
            "applicant_id": str(a.applicant_id),
            "applicant_name": applicant.full_name if applicant else "Unknown",
            "applicant_email": applicant.email if applicant else "",
            "status": a.status,
            "cover_letter": decrypt_data(a.cover_letter_encrypted) if a.cover_letter_encrypted else None,
            "phone": decrypt_data(a.phone_encrypted) if a.phone_encrypted else None,
            "created_at": a.created_at.isoformat(),
        })
    return out


@router.patch("/{application_id}/status")
async def update_application_status(
    application_id: str,
    body: StatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_employer),
):
    validate_no_sqli(application_id)
    result = await db.execute(select(Application).where(Application.id == application_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    app.status = body.status
    if body.notes:
        app.notes = sanitize_input(body.notes)
    await db.commit()

    try:
        await emit_application_status_changed(application_id, body.status)
    except Exception as e:
        logger.warning(f"Kafka skipped: {e}")

    return {"message": f"Status updated to {body.status}"}