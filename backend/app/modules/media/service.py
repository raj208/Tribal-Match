from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.modules.media.models import ProfilePhoto
from app.modules.media.providers import LocalMediaStorageProvider
from app.modules.media.repository import (
    clear_primary_for_profile,
    create_photo,
    delete_photo,
    get_photo_by_id_for_user,
    list_photos_by_profile_id,
    update_photo,
)
from app.modules.profiles.repository import get_profile_by_user_id
from app.modules.users.models import User

MAX_PROFILE_PHOTOS = 6


def _get_profile_or_404(db: Session, current_user: User):
    profile = get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Create your profile before managing media",
        )
    return profile


def list_my_photos(db: Session, current_user: User) -> list[ProfilePhoto]:
    profile = _get_profile_or_404(db, current_user)
    return list_photos_by_profile_id(db, profile.id)


def upload_my_photo_file(
    db: Session,
    current_user: User,
    *,
    file: UploadFile,
    sort_order: int,
    is_primary: bool,
) -> ProfilePhoto:
    profile = _get_profile_or_404(db, current_user)
    existing = list_photos_by_profile_id(db, profile.id)

    if len(existing) >= MAX_PROFILE_PHOTOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can upload a maximum of 6 profile photos",
        )

    storage = LocalMediaStorageProvider()
    photo_url = storage.save_photo(file)

    should_be_primary = is_primary or len(existing) == 0

    if should_be_primary:
        clear_primary_for_profile(db, profile.id)

    data = {
        "user_id": current_user.id,
        "profile_id": profile.id,
        "photo_url": photo_url,
        "sort_order": sort_order,
        "is_primary": should_be_primary,
    }

    return create_photo(db, data)


def set_my_primary_photo(db: Session, current_user: User, photo_id: UUID) -> ProfilePhoto:
    profile = _get_profile_or_404(db, current_user)
    photo = get_photo_by_id_for_user(db, photo_id, current_user.id)

    if not photo or photo.profile_id != profile.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )

    clear_primary_for_profile(db, profile.id)
    return update_photo(db, photo, {"is_primary": True})


def delete_my_photo(db: Session, current_user: User, photo_id: UUID) -> None:
    profile = _get_profile_or_404(db, current_user)
    photo = get_photo_by_id_for_user(db, photo_id, current_user.id)

    if not photo or photo.profile_id != profile.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )

    was_primary = photo.is_primary
    delete_photo(db, photo)

    if was_primary:
        remaining = list_photos_by_profile_id(db, profile.id)
        if remaining:
            first = remaining[0]
            update_photo(db, first, {"is_primary": True})