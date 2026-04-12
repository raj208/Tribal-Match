from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.media.models import ProfilePhoto


def list_photos_by_profile_id(db: Session, profile_id: UUID) -> list[ProfilePhoto]:
    stmt = (
        select(ProfilePhoto)
        .where(ProfilePhoto.profile_id == profile_id)
        .order_by(ProfilePhoto.is_primary.desc(), ProfilePhoto.sort_order.asc(), ProfilePhoto.created_at.asc())
    )
    return list(db.scalars(stmt).all())


def get_photo_by_id_for_user(db: Session, photo_id: UUID, user_id: UUID) -> ProfilePhoto | None:
    stmt = select(ProfilePhoto).where(
        ProfilePhoto.id == photo_id,
        ProfilePhoto.user_id == user_id,
    )
    return db.scalar(stmt)


def clear_primary_for_profile(db: Session, profile_id: UUID) -> None:
    photos = list_photos_by_profile_id(db, profile_id)
    changed = False

    for photo in photos:
        if photo.is_primary:
            photo.is_primary = False
            db.add(photo)
            changed = True

    if changed:
        db.commit()


def create_photo(db: Session, data: dict) -> ProfilePhoto:
    photo = ProfilePhoto(**data)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def update_photo(db: Session, photo: ProfilePhoto, data: dict) -> ProfilePhoto:
    for key, value in data.items():
        setattr(photo, key, value)

    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def delete_photo(db: Session, photo: ProfilePhoto) -> None:
    db.delete(photo)
    db.commit()