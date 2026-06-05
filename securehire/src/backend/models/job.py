"""
Job Model
CYC386 - SecureHire
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=False)
    location = Column(String(255), nullable=False)
    salary_range = Column(String(100), nullable=True)
    job_type = Column(
        SAEnum("full_time", "part_time", "contract", "remote", name="job_type"),
        nullable=False,
        default="full_time"
    )
    status = Column(
        SAEnum("active", "closed", "draft", name="job_status"),
        nullable=False,
        default="active"
    )
    employer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
    deadline = Column(DateTime(timezone=True), nullable=True)

    employer = relationship("User", back_populates="jobs")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
