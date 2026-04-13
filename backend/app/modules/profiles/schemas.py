from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.shared.enums import ProfileStatus, VerificationStatus


class PreferenceUpsert(BaseModel):
    preferred_min_age: int | None = Field(default=None, ge=18, le=100)
    preferred_max_age: int | None = Field(default=None, ge=18, le=100)
    preferred_locations: list[str] = Field(default_factory=list)
    preferred_communities: list[str] = Field(default_factory=list)
    preferred_languages: list[str] = Field(default_factory=list)


class PreferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    profile_id: UUID
    preferred_min_age: int | None
    preferred_max_age: int | None
    preferred_locations: list[str]
    preferred_communities: list[str]
    preferred_languages: list[str]
    created_at: datetime
    updated_at: datetime


class ProfileCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    age: int | None = Field(default=None, ge=18, le=100)
    gender: str | None = Field(default=None, max_length=32)
    date_of_birth: date | None = None
    community_or_tribe: str | None = Field(default=None, max_length=120)
    subgroup_or_clan: str | None = Field(default=None, max_length=120)
    native_language: str | None = Field(default=None, max_length=80)
    other_languages: list[str] = Field(default_factory=list)
    location_city: str | None = Field(default=None, max_length=120)
    location_state: str | None = Field(default=None, max_length=120)
    location_country: str | None = Field(default=None, max_length=120)
    occupation: str | None = Field(default=None, max_length=120)
    education: str | None = Field(default=None, max_length=120)
    bio: str | None = Field(default=None, max_length=2000)
    profile_visibility: str = Field(default="public", max_length=32)
    profile_status: ProfileStatus = ProfileStatus.DRAFT
    preferences: PreferenceUpsert | None = None


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    age: int | None = Field(default=None, ge=18, le=100)
    gender: str | None = Field(default=None, max_length=32)
    date_of_birth: date | None = None
    community_or_tribe: str | None = Field(default=None, max_length=120)
    subgroup_or_clan: str | None = Field(default=None, max_length=120)
    native_language: str | None = Field(default=None, max_length=80)
    other_languages: list[str] | None = None
    location_city: str | None = Field(default=None, max_length=120)
    location_state: str | None = Field(default=None, max_length=120)
    location_country: str | None = Field(default=None, max_length=120)
    occupation: str | None = Field(default=None, max_length=120)
    education: str | None = Field(default=None, max_length=120)
    bio: str | None = Field(default=None, max_length=2000)
    profile_visibility: str | None = Field(default=None, max_length=32)
    profile_status: ProfileStatus | None = None
    preferences: PreferenceUpsert | None = None


class ProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    full_name: str
    age: int | None
    gender: str | None
    date_of_birth: date | None
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
    profile_visibility: str
    profile_status: ProfileStatus
    verification_status: VerificationStatus
    completion_percentage: int
    created_at: datetime
    updated_at: datetime
    preferences: PreferenceRead | None = None