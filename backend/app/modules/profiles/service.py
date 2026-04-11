# Service logic for the profiles module will be added in later steps.
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.profiles.models import Profile
from app.modules.profiles.repository import (
    create_profile,
    get_profile_by_user_id,
    update_profile,
)
from app.modules.profiles.schemas import ProfileCreate, ProfileUpdate
from app.modules.users.models import User

PROFILE_COMPLETION_FIELDS = [
    "full_name",
    "age",
    "gender",
    "community_or_tribe",
    "native_language",
    "location_city",
    "occupation",
    "education",
    "bio",
]


def _calculate_completion(data: dict) -> int:
    filled = 0
    total = len(PROFILE_COMPLETION_FIELDS)

    for field in PROFILE_COMPLETION_FIELDS:
        value = data.get(field)

        if value is None:
            continue

        if isinstance(value, str) and not value.strip():
            continue

        filled += 1

    return int((filled / total) * 100)


def create_my_profile(db: Session, current_user: User, payload: ProfileCreate) -> Profile:
    existing = get_profile_by_user_id(db, current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists for this user",
        )

    data = payload.model_dump()
    data["user_id"] = current_user.id
    data["completion_percentage"] = _calculate_completion(data)

    return create_profile(db, data)


def get_my_profile(db: Session, current_user: User) -> Profile:
    profile = get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return profile


def update_my_profile(db: Session, current_user: User, payload: ProfileUpdate) -> Profile:
    profile = get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    updates = payload.model_dump(exclude_unset=True)

    merged = {
        "full_name": updates.get("full_name", profile.full_name),
        "age": updates.get("age", profile.age),
        "gender": updates.get("gender", profile.gender),
        "community_or_tribe": updates.get("community_or_tribe", profile.community_or_tribe),
        "native_language": updates.get("native_language", profile.native_language),
        "location_city": updates.get("location_city", profile.location_city),
        "occupation": updates.get("occupation", profile.occupation),
        "education": updates.get("education", profile.education),
        "bio": updates.get("bio", profile.bio),
    }

    updates["completion_percentage"] = _calculate_completion(merged)

    return update_profile(db, profile, updates)