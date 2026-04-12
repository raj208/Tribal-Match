# Schemas for the verification module will be added in later steps.
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.shared.enums import VerificationStatus


class IntroVideoUpsert(BaseModel):
    video_url: str = Field(min_length=3, max_length=500)
    duration_seconds: int = Field(ge=20, le=30)


class IntroVideoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    profile_id: UUID
    video_url: str
    duration_seconds: int | None
    upload_status: str
    verification_status: VerificationStatus
    moderation_notes: str | None
    created_at: datetime
    updated_at: datetime


class VerificationRead(BaseModel):
    profile_verification_status: VerificationStatus
    intro_video: IntroVideoRead | None