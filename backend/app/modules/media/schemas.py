from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.shared.enums import ModerationStatus


class PhotoCreate(BaseModel):
    photo_url: str = Field(min_length=3, max_length=500)
    sort_order: int = Field(default=0, ge=0)
    is_primary: bool = False


class PhotoUploadIntentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filename: str = Field(min_length=3, max_length=255)
    content_type: str = Field(min_length=3, max_length=255)


class PhotoUploadIntentResponse(BaseModel):
    provider: str
    object_key: str
    upload_url: str
    expires_in: int


class PhotoConfirmRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_key: str = Field(min_length=3, max_length=1024)
    content_type: str = Field(min_length=3, max_length=255)
    sort_order: int = Field(default=0, ge=0)
    make_primary: bool = False


class PhotoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    profile_id: UUID
    photo_url: str
    sort_order: int
    is_primary: bool
    moderation_status: ModerationStatus
    created_at: datetime


class PhotoDeleteResponse(BaseModel):
    message: str
