from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.modules.media.providers import LocalMediaStorageProvider
from app.modules.profiles.repository import get_profile_by_user_id
from app.modules.users.models import User
from app.modules.verification.repository import (
    create_intro_video,
    get_intro_video_by_profile_id,
    update_intro_video,
)
from app.shared.enums import VerificationStatus


def _get_profile_or_404(db: Session, current_user: User):
    profile = get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Create your profile before managing verification",
        )
    return profile


def get_my_verification(db: Session, current_user: User) -> dict:
    profile = _get_profile_or_404(db, current_user)
    intro_video = get_intro_video_by_profile_id(db, profile.id)

    return {
        "profile_verification_status": profile.verification_status,
        "intro_video": intro_video,
    }


def upsert_my_intro_video_file(
    db: Session,
    current_user: User,
    *,
    file: UploadFile,
    duration_seconds: int,
) -> dict:
    if duration_seconds < 20 or duration_seconds > 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Intro video must be between 20 and 30 seconds",
        )

    profile = _get_profile_or_404(db, current_user)
    existing = get_intro_video_by_profile_id(db, profile.id)

    storage = LocalMediaStorageProvider()
    video_url = storage.save_video(file)

    data = {
        "user_id": current_user.id,
        "profile_id": profile.id,
        "video_url": video_url,
        "duration_seconds": duration_seconds,
        "upload_status": "uploaded",
        "verification_status": VerificationStatus.UPLOADED,
        "moderation_notes": None,
    }

    if existing:
        update_intro_video(db, existing, data)
    else:
        create_intro_video(db, data)

    profile.verification_status = VerificationStatus.UPLOADED
    db.add(profile)
    db.commit()
    db.refresh(profile)

    intro_video = get_intro_video_by_profile_id(db, profile.id)

    return {
        "profile_verification_status": profile.verification_status,
        "intro_video": intro_video,
    }