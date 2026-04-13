from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.moderation.repository import (
    create_block,
    create_report,
    delete_block,
    get_block_by_users,
)
from app.modules.profiles.models import Profile
from app.modules.users.models import User


def _get_target_profile_or_404(db: Session, *, profile_id: UUID) -> Profile:
    stmt = select(Profile).where(Profile.id == profile_id)
    profile = db.scalar(stmt)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target profile not found",
        )

    return profile


def block_profile(db: Session, *, current_user: User, profile_id: UUID) -> dict:
    target_profile = _get_target_profile_or_404(db, profile_id=profile_id)

    if target_profile.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot block your own profile",
        )

    existing = get_block_by_users(
        db,
        blocker_user_id=current_user.id,
        blocked_user_id=target_profile.user_id,
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already blocked",
        )

    create_block(
        db,
        {
            "blocker_user_id": current_user.id,
            "blocked_user_id": target_profile.user_id,
        },
    )

    return {"message": "Profile blocked successfully"}


def unblock_profile(db: Session, *, current_user: User, profile_id: UUID) -> dict:
    target_profile = _get_target_profile_or_404(db, profile_id=profile_id)

    item = get_block_by_users(
        db,
        blocker_user_id=current_user.id,
        blocked_user_id=target_profile.user_id,
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Block record not found",
        )

    delete_block(db, item)
    return {"message": "Profile unblocked successfully"}


def report_profile(
    db: Session,
    *,
    current_user: User,
    profile_id: UUID,
    reason_code: str,
    notes: str | None,
) -> dict:
    target_profile = _get_target_profile_or_404(db, profile_id=profile_id)

    if target_profile.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot report your own profile",
        )

    create_report(
        db,
        {
            "reporter_user_id": current_user.id,
            "reported_user_id": target_profile.user_id,
            "reported_profile_id": target_profile.id,
            "reason_code": reason_code.strip().lower(),
            "notes": notes.strip() if notes else None,
        },
    )

    return {"message": "Report submitted successfully"}