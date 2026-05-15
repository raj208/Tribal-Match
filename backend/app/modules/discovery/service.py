from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import is_admin_email
from app.modules.discovery.repository import (
    get_profile_detail_by_id,
    list_discoverable_profiles,
)
from app.modules.interests.repository import has_accepted_interest_between
from app.modules.media.providers import resolve_media_url
from app.modules.moderation.repository import is_blocked_between
from app.modules.profiles.models import Profile
from app.modules.profiles.schemas import SOCIAL_URL_FIELDS
from app.modules.users.models import User
from app.shared.enums import ProfileStatus


def _get_primary_photo_url(profile) -> str | None:
    if not profile.photos:
        return None

    for photo in profile.photos:
        if photo.is_primary:
            return resolve_media_url(
                provider=photo.provider,
                stored_url=photo.photo_url,
                object_key=photo.object_key,
                bucket=photo.bucket,
            )

    first_photo = profile.photos[0]
    return resolve_media_url(
        provider=first_photo.provider,
        stored_url=first_photo.photo_url,
        object_key=first_photo.object_key,
        bucket=first_photo.bucket,
    )


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


def _social_link_payload(profile: Profile, *, include_social_links: bool) -> dict:
    return {
        field_name: getattr(profile, field_name) if include_social_links else None
        for field_name in SOCIAL_URL_FIELDS
    }


def can_view_social_links(
    db: Session,
    *,
    viewer_user_id,
    target_user_id,
    is_admin: bool = False,
) -> bool:
    if is_admin or viewer_user_id == target_user_id:
        return True

    if is_blocked_between(db, user_a_id=viewer_user_id, user_b_id=target_user_id):
        return False

    return has_accepted_interest_between(
        db,
        user_a_id=viewer_user_id,
        user_b_id=target_user_id,
    )


def _can_view_profile_detail(
    db: Session,
    *,
    current_user: User,
    profile: Profile,
    is_admin: bool,
) -> bool:
    if is_admin or profile.user_id == current_user.id:
        return True

    if profile.profile_status != ProfileStatus.PUBLISHED:
        return False

    return not is_blocked_between(
        db,
        user_a_id=current_user.id,
        user_b_id=profile.user_id,
    )


def _serialize_detail(profile, *, include_social_links: bool) -> dict:
    detail = {
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
                "photo_url": resolve_media_url(
                    provider=photo.provider,
                    stored_url=photo.photo_url,
                    object_key=photo.object_key,
                    bucket=photo.bucket,
                ),
                "is_primary": photo.is_primary,
                "sort_order": photo.sort_order,
            }
            for photo in sorted(
                profile.photos,
                key=lambda p: (not p.is_primary, p.sort_order),
            )
        ],
        "intro_video_url": (
            resolve_media_url(
                provider=profile.intro_video.provider,
                stored_url=profile.intro_video.video_url,
                object_key=profile.intro_video.object_key,
                bucket=profile.intro_video.bucket,
            )
            if profile.intro_video
            else None
        ),
    }
    detail.update(_social_link_payload(profile, include_social_links=include_social_links))
    return detail


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
    profile = get_profile_detail_by_id(
        db,
        profile_id=profile_id,
    )

    current_user_is_admin = is_admin_email(current_user.email)
    if not profile or not _can_view_profile_detail(
        db,
        current_user=current_user,
        profile=profile,
        is_admin=current_user_is_admin,
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    include_social_links = can_view_social_links(
        db,
        viewer_user_id=current_user.id,
        target_user_id=profile.user_id,
        is_admin=current_user_is_admin,
    )
    return _serialize_detail(profile, include_social_links=include_social_links)
