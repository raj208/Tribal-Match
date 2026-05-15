import re
from datetime import date, datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
    model_validator,
)

from app.shared.enums import ProfileStatus, VerificationStatus

SOCIAL_URL_FIELDS = ("instagram_url", "facebook_url", "linkedin_url")

_SOCIAL_URL_PATTERNS = {
    "instagram_url": re.compile(r"^https://(?:www\.)?instagram\.com/[^/?#\s][^\s]*$"),
    "facebook_url": re.compile(r"^https://(?:www\.)?facebook\.com/[^/?#\s][^\s]*$"),
    "linkedin_url": re.compile(r"^https://(?:www\.)?linkedin\.com/[^/?#\s][^\s]*$"),
}
_SOCIAL_URL_PLATFORM_LABELS = {
    "instagram_url": "Instagram",
    "facebook_url": "Facebook",
    "linkedin_url": "LinkedIn",
}


def _normalize_social_url(value: object, field_name: str) -> str | None:
    if value is None:
        return None

    if not isinstance(value, str):
        raise ValueError("Social links must be strings")

    normalized = value.strip()
    if not normalized:
        return None

    if not _SOCIAL_URL_PATTERNS[field_name].fullmatch(normalized):
        platform = _SOCIAL_URL_PLATFORM_LABELS[field_name]
        raise ValueError(f"{platform} URL must be a valid https URL for {platform}")

    return normalized


def _has_social_link(values: object) -> bool:
    return any(getattr(values, field_name) for field_name in SOCIAL_URL_FIELDS)


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


class SocialLinksMixin(BaseModel):
    instagram_url: str | None = Field(default=None, max_length=500)
    facebook_url: str | None = Field(default=None, max_length=500)
    linkedin_url: str | None = Field(default=None, max_length=500)

    @field_validator(*SOCIAL_URL_FIELDS, mode="before")
    @classmethod
    def normalize_social_url(cls, value: object, info: ValidationInfo) -> str | None:
        return _normalize_social_url(value, info.field_name)


class ProfileCreate(SocialLinksMixin):
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

    @model_validator(mode="after")
    def require_social_link(self) -> "ProfileCreate":
        if not _has_social_link(self):
            raise ValueError("At least one social link is required")
        return self


class ProfileUpdate(SocialLinksMixin):
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
    instagram_url: str | None
    facebook_url: str | None
    linkedin_url: str | None
    profile_visibility: str
    profile_status: ProfileStatus
    verification_status: VerificationStatus
    completion_percentage: int
    created_at: datetime
    updated_at: datetime
    preferences: PreferenceRead | None = None
