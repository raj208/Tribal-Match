# Service logic for the verification module will be added in later steps.
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.profiles.repository import get_profile_by_user_id
from app.modules.users.models import User
from app.modules.verification.repository import (
    create_intro_video,
    get_intro_video_by_profile_id,
    update_intro_video,
)
from app.modules.verification.schemas import IntroVideoUpsert
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


def upsert_my_intro_video(db: Session, current_user: User, payload: IntroVideoUpsert) -> dict:
    profile = _get_profile_or_404(db, current_user)
    existing = get_intro_video_by_profile_id(db, profile.id)

    data = payload.model_dump()
    data["user_id"] = current_user.id
    data["profile_id"] = profile.id
    data["upload_status"] = "uploaded"
    data["verification_status"] = VerificationStatus.UPLOADED
    data["moderation_notes"] = None

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