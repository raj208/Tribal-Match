from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.discovery.repository import (
    get_discoverable_profile_by_id,
    list_discoverable_profiles,
)
from app.modules.users.models import User


def _get_primary_photo_url(profile) -> str | None:
    if not profile.photos:
        return None

    for photo in profile.photos:
        if photo.is_primary:
            return photo.photo_url

    return profile.photos[0].photo_url


def _serialize_card(profile) -> dict:
    return {
        "id": profile.id,
        "full_name": profile.full_name,
        "age": profile.age,
        "community_or_tribe": profile.community_or_tribe,
        "native_language": profile.native_language,
        "location_city": profile.location_city,
        "location_state": profile.location_state,
        "occupation": profile.occupation,
        "bio": profile.bio,
        "verification_status": profile.verification_status,
        "primary_photo_url": _get_primary_photo_url(profile),
    }


def _serialize_detail(profile) -> dict:
    return {
        "id": profile.id,
        "full_name": profile.full_name,
        "age": profile.age,
        "gender": profile.gender,
        "community_or_tribe": profile.community_or_tribe,
        "subgroup_or_clan": profile.subgroup_or_clan,
        "native_language": profile.native_language,
        "other_languages": profile.other_languages,
        "location_city": profile.location_city,
        "location_state": profile.location_state,
        "location_country": profile.location_country,
        "occupation": profile.occupation,
        "education": profile.education,
        "bio": profile.bio,
        "verification_status": profile.verification_status,
        "photos": [
            {
                "id": photo.id,
                "photo_url": photo.photo_url,
                "is_primary": photo.is_primary,
                "sort_order": photo.sort_order,
            }
            for photo in sorted(
                profile.photos,
                key=lambda p: (not p.is_primary, p.sort_order),
            )
        ],
        "intro_video_url": profile.intro_video.video_url if profile.intro_video else None,
    }


def browse_profiles(
    db: Session,
    *,
    current_user: User,
    q: str | None,
    min_age: int | None,
    max_age: int | None,
    community: str | None,
    native_language: str | None,
    city: str | None,
    page: int,
    size: int,
) -> dict:
    items, total = list_discoverable_profiles(
        db,
        current_user_id=current_user.id,
        q=q,
        min_age=min_age,
        max_age=max_age,
        community=community,
        native_language=native_language,
        city=city,
        page=page,
        size=size,
    )

    return {
        "items": [_serialize_card(item) for item in items],
        "total": total,
        "page": page,
        "size": size,
    }


def get_profile_detail(
    db: Session,
    *,
    current_user: User,
    profile_id,
) -> dict:
    profile = get_discoverable_profile_by_id(
        db,
        profile_id=profile_id,
        current_user_id=current_user.id,
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return _serialize_detail(profile)