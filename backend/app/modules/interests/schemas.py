# Schemas for the interests module will be added in later steps.
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.shared.enums import InterestStatus, VerificationStatus


class ShortlistCreate(BaseModel):
    profile_id: UUID


class ShortlistItem(BaseModel):
    id: UUID
    profile_id: UUID
    full_name: str
    age: int | None
    community_or_tribe: str | None
    native_language: str | None
    location_city: str | None
    occupation: str | None
    bio: str | None
    verification_status: VerificationStatus
    primary_photo_url: str | None
    created_at: datetime


class InterestCreate(BaseModel):
    receiver_profile_id: UUID


class InterestListItem(BaseModel):
    id: UUID
    profile_id: UUID
    full_name: str
    age: int | None
    community_or_tribe: str | None
    native_language: str | None
    location_city: str | None
    occupation: str | None
    bio: str | None
    verification_status: VerificationStatus
    primary_photo_url: str | None
    status: InterestStatus
    direction: str
    created_at: datetime