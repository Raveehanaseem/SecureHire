"""
Job & Application Models
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from database import Base


class Application(Base):
    __tablename__ = "applications"
    # To fix 'Table already defined' error on reload
    __table_args__ = {'extend_existing': True}  

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    applicant_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # AES-256 encrypted fields (sensitive data at rest)
    cover_letter_encrypted = Column(Text, nullable=True)   # Encrypted
    resume_filename_encrypted = Column(Text, nullable=True) # Encrypted
    phone_encrypted = Column(Text, nullable=True)           # Encrypted

    status = Column(
        SAEnum("pending", "reviewing", "shortlisted", "rejected", "hired", name="application_status"),
        nullable=False,
        default="pending"
    )
    notes = Column(Text, nullable=True)  # Employer notes
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    job = relationship("Job", back_populates="applications")
    applicant = relationship("User", back_populates="applications")
