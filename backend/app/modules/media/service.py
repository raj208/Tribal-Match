from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.modules.media.models import ProfilePhoto
from app.modules.media.providers import (
    MEDIA_PROVIDER_S3,
    LocalMediaStorageProvider,
    delete_media_object,
    get_s3_provider,
    resolve_media_url,
    validate_photo_upload_request,
)
from app.modules.media.repository import (
    clear_primary_for_profile,
    create_photo,
    delete_photo,
    get_photo_by_id_for_user,
    get_photo_by_profile_and_storage_key,
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


def _serialize_photo(photo: ProfilePhoto) -> dict:
    return {
        "id": photo.id,
        "user_id": photo.user_id,
        "profile_id": photo.profile_id,
        "photo_url": resolve_media_url(
            provider=photo.provider,
            stored_url=photo.photo_url,
            object_key=photo.object_key,
            bucket=photo.bucket,
        ),
        "sort_order": photo.sort_order,
        "is_primary": photo.is_primary,
        "moderation_status": photo.moderation_status,
        "created_at": photo.created_at,
    }


def _build_photo_create_data(
    *,
    current_user: User,
    profile_id,
    stored_photo,
    sort_order: int,
    is_primary: bool,
) -> dict:
    return {
        "user_id": current_user.id,
        "profile_id": profile_id,
        "provider": stored_photo.provider,
        "bucket": stored_photo.bucket,
        "object_key": stored_photo.object_key,
        "content_type": stored_photo.content_type,
        "size_bytes": stored_photo.size_bytes,
        "photo_url": stored_photo.stored_url,
        "sort_order": sort_order,
        "is_primary": is_primary,
    }


def _normalize_owned_photo_object_key(*, current_user: User, object_key: str) -> str:
    normalized_key = object_key.strip().lstrip("/")
    if not normalized_key or "\\" in normalized_key or ".." in normalized_key.split("/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid photo object key",
        )

    photos_prefix = get_s3_provider().photos_prefix
    expected_prefix = f"{photos_prefix}/{current_user.id}/"
    if not normalized_key.startswith(expected_prefix):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Photo object key does not belong to the current user",
        )

    return normalized_key


def list_my_photos(db: Session, current_user: User) -> list[dict]:
    profile = _get_profile_or_404(db, current_user)
    return [_serialize_photo(photo) for photo in list_photos_by_profile_id(db, profile.id)]


def create_my_photo_upload_intent(
    db: Session,
    current_user: User,
    *,
    filename: str,
    content_type: str,
) -> dict:
    profile = _get_profile_or_404(db, current_user)
    existing = list_photos_by_profile_id(db, profile.id)

    if len(existing) >= MAX_PROFILE_PHOTOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can upload a maximum of 6 profile photos",
        )

    return get_s3_provider().create_photo_upload_intent(
        user_id=current_user.id,
        filename=filename,
        content_type=content_type,
    )


def confirm_my_photo_upload(
    db: Session,
    current_user: User,
    *,
    object_key: str,
    content_type: str,
    sort_order: int,
    make_primary: bool,
) -> dict:
    profile = _get_profile_or_404(db, current_user)
    normalized_object_key = _normalize_owned_photo_object_key(current_user=current_user, object_key=object_key)
    _, normalized_content_type = validate_photo_upload_request(normalized_object_key, content_type)
    existing = list_photos_by_profile_id(db, profile.id)
    existing_photo = get_photo_by_profile_and_storage_key(
        db,
        profile_id=profile.id,
        provider=MEDIA_PROVIDER_S3,
        object_key=normalized_object_key,
    )

    if existing_photo:
        update_data = {"sort_order": sort_order}
        if make_primary and not existing_photo.is_primary:
            clear_primary_for_profile(db, profile.id)
            update_data["is_primary"] = True
        photo = update_photo(db, existing_photo, update_data) if update_data else existing_photo
        return _serialize_photo(photo)

    if len(existing) >= MAX_PROFILE_PHOTOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can upload a maximum of 6 profile photos",
        )

    stored_photo = get_s3_provider().inspect_uploaded_object(object_key=normalized_object_key)
    if stored_photo.content_type and stored_photo.content_type != normalized_content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded photo content type did not match the signed upload",
        )

    should_be_primary = make_primary or len(existing) == 0
    if should_be_primary:
        clear_primary_for_profile(db, profile.id)

    photo = create_photo(
        db,
        _build_photo_create_data(
            current_user=current_user,
            profile_id=profile.id,
            stored_photo=stored_photo,
            sort_order=sort_order,
            is_primary=should_be_primary,
        ),
    )
    return _serialize_photo(photo)


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
    stored_photo = storage.save_photo(file)

    should_be_primary = is_primary or len(existing) == 0

    if should_be_primary:
        clear_primary_for_profile(db, profile.id)

    return create_photo(
        db,
        _build_photo_create_data(
            current_user=current_user,
            profile_id=profile.id,
            stored_photo=stored_photo,
            sort_order=sort_order,
            is_primary=should_be_primary,
        ),
    )


def set_my_primary_photo(db: Session, current_user: User, photo_id: UUID) -> dict:
    profile = _get_profile_or_404(db, current_user)
    photo = get_photo_by_id_for_user(db, photo_id, current_user.id)

    if not photo or photo.profile_id != profile.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )

    clear_primary_for_profile(db, profile.id)
    return _serialize_photo(update_photo(db, photo, {"is_primary": True}))


def delete_my_photo(db: Session, current_user: User, photo_id: UUID) -> None:
    profile = _get_profile_or_404(db, current_user)
    photo = get_photo_by_id_for_user(db, photo_id, current_user.id)

    if not photo or photo.profile_id != profile.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )

    was_primary = photo.is_primary
    photo_provider = photo.provider
    photo_url = photo.photo_url
    object_key = photo.object_key
    bucket = photo.bucket
    delete_photo(db, photo)
    delete_media_object(
        provider=photo_provider,
        stored_url=photo_url,
        object_key=object_key,
        bucket=bucket,
    )

    if was_primary:
        remaining = list_photos_by_profile_id(db, profile.id)
        if remaining:
            first = remaining[0]
            update_photo(db, first, {"is_primary": True})


def serialize_photo(photo: ProfilePhoto) -> dict:
    return _serialize_photo(photo)
