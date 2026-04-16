from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.modules.media.providers import LocalMediaStorageProvider
from app.modules.media.models import IntroVideo
from app.modules.profiles.models import Profile
from app.modules.profiles.repository import update_profile
from app.modules.profiles.repository import get_profile_by_user_id
from app.modules.users.models import User
from app.modules.verification.repository import (
    create_intro_video,
    get_intro_video_with_context,
    get_intro_video_by_profile_id,
    list_intro_videos_for_review,
    update_intro_video,
)
from app.modules.verification.schemas import (
    AdminVerificationDetail,
    AdminVerificationProfileSummary,
    AdminVerificationQueueItem,
    AdminVerificationUserSummary,
)
from app.shared.enums import VerificationStatus


_REVIEW_QUEUE_STATUSES = (
    VerificationStatus.UPLOADED,
    VerificationStatus.UNDER_REVIEW,
)
_ADMIN_REVIEW_DECISION_STATUSES = {
    VerificationStatus.APPROVED,
    VerificationStatus.REJECTED,
}


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


def list_admin_verification_queue(
    db: Session,
    *,
    limit: int = 50,
    offset: int = 0,
) -> list[AdminVerificationQueueItem]:
    records = list_intro_videos_for_review(
        db,
        statuses=_REVIEW_QUEUE_STATUSES,
        limit=limit,
        offset=offset,
    )
    return [_build_admin_verification_queue_item(record.intro_video, record.profile, record.user) for record in records]


def get_admin_verification_item(
    db: Session,
    *,
    item_id,
) -> AdminVerificationDetail:
    record = get_intro_video_with_context(db, intro_video_id=item_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification item not found",
        )

    return _build_admin_verification_detail(record.intro_video, record.profile, record.user)


def review_admin_verification_item(
    db: Session,
    *,
    item_id,
    next_status: VerificationStatus,
    reason: str | None,
) -> AdminVerificationDetail:
    if next_status not in _ADMIN_REVIEW_DECISION_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Verification review status must be approved or rejected",
        )

    record = get_intro_video_with_context(db, intro_video_id=item_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification item not found",
        )

    moderation_notes = _resolve_review_moderation_notes(
        current_notes=record.intro_video.moderation_notes,
        next_status=next_status,
        reason=reason,
    )

    updated_intro_video = update_intro_video(
        db,
        record.intro_video,
        {
            "verification_status": next_status,
            "moderation_notes": moderation_notes,
        },
    )
    updated_profile = update_profile(
        db,
        record.profile,
        {"verification_status": next_status},
    )

    return _build_admin_verification_detail(updated_intro_video, updated_profile, record.user)


def _resolve_review_moderation_notes(
    *,
    current_notes: str | None,
    next_status: VerificationStatus,
    reason: str | None,
) -> str | None:
    cleaned_reason = reason.strip() if reason and reason.strip() else None

    if next_status == VerificationStatus.APPROVED:
        return None

    return cleaned_reason if cleaned_reason is not None else current_notes


def _build_admin_verification_user_summary(user: User) -> AdminVerificationUserSummary:
    return AdminVerificationUserSummary(
        id=user.id,
        email=user.email,
    )


def _build_admin_verification_profile_summary(profile: Profile) -> AdminVerificationProfileSummary:
    return AdminVerificationProfileSummary(
        id=profile.id,
        user_id=profile.user_id,
        full_name=profile.full_name,
        profile_status=profile.profile_status,
        verification_status=profile.verification_status,
    )


def _build_admin_verification_queue_item(
    intro_video: IntroVideo,
    profile: Profile,
    user: User,
) -> AdminVerificationQueueItem:
    return AdminVerificationQueueItem(
        id=intro_video.id,
        user=_build_admin_verification_user_summary(user),
        profile=_build_admin_verification_profile_summary(profile),
        verification_status=intro_video.verification_status,
        video_url=intro_video.video_url,
        duration_seconds=intro_video.duration_seconds,
        created_at=intro_video.created_at,
    )


def _build_admin_verification_detail(
    intro_video: IntroVideo,
    profile: Profile,
    user: User,
) -> AdminVerificationDetail:
    return AdminVerificationDetail(
        **_build_admin_verification_queue_item(intro_video, profile, user).model_dump(),
        upload_status=intro_video.upload_status,
        moderation_notes=intro_video.moderation_notes,
        updated_at=intro_video.updated_at,
    )
