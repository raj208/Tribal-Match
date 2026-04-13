# Schemas for the discovery module will be added in later steps.
from uuid import UUID

from pydantic import BaseModel

from app.shared.enums import VerificationStatus


class DiscoverProfileCard(BaseModel):
    id: UUID
    full_name: str
    age: int | None
    community_or_tribe: str | None
    native_language: str | None
    location_city: str | None
    location_state: str | None
    occupation: str | None
    bio: str | None
    verification_status: VerificationStatus
    primary_photo_url: str | None


class DiscoverProfileListResponse(BaseModel):
    items: list[DiscoverProfileCard]
    total: int
    page: int
    size: int


class DiscoverProfilePhoto(BaseModel):
    id: UUID
    photo_url: str
    is_primary: bool
    sort_order: int


class PublicProfileRead(BaseModel):
    id: UUID
    full_name: str
    age: int | None
    gender: str | None
    community_or_tribe: str | None
    subgroup_or_clan: str | None
    native_language: str | None
    other_languages: list[str]
    location_city: str | None
    location_state: str | None
    location_country: str | None
    occupation: str | None
    education: str | None
    bio: str | None
    verification_status: VerificationStatus
    photos: list[DiscoverProfilePhoto]
    intro_video_url: str | None