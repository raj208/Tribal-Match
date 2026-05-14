from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.shared.enums import ProfileStatus
from app.shared.enums import VerificationStatus


class IntroVideoUpsert(BaseModel):
    video_url: str = Field(min_length=3, max_length=500)
    duration_seconds: int = Field(ge=20, le=30)


class IntroVideoUploadIntentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filename: str = Field(min_length=3, max_length=255)
    content_type: str = Field(min_length=3, max_length=255)


class IntroVideoUploadIntentResponse(BaseModel):
    provider: str
    object_key: str
    upload_url: str
    expires_in: int


class IntroVideoConfirmRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_key: str = Field(min_length=3, max_length=1024)
    content_type: str = Field(min_length=3, max_length=255)
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


class AdminVerificationUserSummary(BaseModel):
    id: UUID
    email: str


class AdminVerificationProfileSummary(BaseModel):
    id: UUID
    user_id: UUID
    full_name: str
    profile_status: ProfileStatus
    verification_status: VerificationStatus


class AdminVerificationQueueItem(BaseModel):
    id: UUID
    user: AdminVerificationUserSummary
    profile: AdminVerificationProfileSummary
    verification_status: VerificationStatus
    video_url: str
    duration_seconds: int | None
    created_at: datetime


class AdminVerificationDetail(AdminVerificationQueueItem):
    upload_status: str
    moderation_notes: str | None
    updated_at: datetime


class AdminVerificationReviewUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: VerificationStatus
    reason: str | None = Field(default=None, max_length=1000)
