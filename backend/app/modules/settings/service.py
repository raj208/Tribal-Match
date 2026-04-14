from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.profiles.models import Profile
from app.modules.settings.repository import get_profile_by_user_id, update_profile
from app.modules.settings.schemas import (
    SettingsDeactivateResponse,
    SettingsDeleteResponse,
    SettingsMeRead,
    SettingsMeUpdate,
)
from app.modules.users.models import User
from app.shared.enums import ProfileStatus, VerificationStatus


def _build_settings_summary(*, current_user: User, profile: Profile | None) -> SettingsMeRead:
    if profile is None:
        return SettingsMeRead(
            email=current_user.email,
            profile_exists=False,
            profile_visibility=None,
            profile_status=None,
            verification_status=VerificationStatus.NOT_STARTED,
            completion_percentage=0,
        )

    return SettingsMeRead(
        email=current_user.email,
        profile_exists=True,
        profile_visibility=profile.profile_visibility,
        profile_status=profile.profile_status,
        verification_status=profile.verification_status,
        completion_percentage=profile.completion_percentage,
    )


def get_my_settings_summary(db: Session, *, current_user: User) -> SettingsMeRead:
    profile = get_profile_by_user_id(db, user_id=current_user.id)
    return _build_settings_summary(current_user=current_user, profile=profile)


def update_my_settings_summary(
    db: Session,
    *,
    current_user: User,
    payload: SettingsMeUpdate,
) -> SettingsMeRead:
    profile = get_profile_by_user_id(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    updates = payload.model_dump(exclude_unset=True)
    if updates:
        profile = update_profile(db, profile, updates)

    return _build_settings_summary(current_user=current_user, profile=profile)


def deactivate_my_profile(
    db: Session,
    *,
    current_user: User,
) -> SettingsDeactivateResponse:
    profile = get_profile_by_user_id(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    if profile.profile_status != ProfileStatus.DEACTIVATED:
        profile = update_profile(
            db,
            profile,
            {"profile_status": ProfileStatus.DEACTIVATED},
        )

    return SettingsDeactivateResponse(
        success=True,
        profile_status=profile.profile_status,
        message="Profile deactivated successfully.",
    )


def soft_delete_my_profile(
    db: Session,
    *,
    current_user: User,
) -> SettingsDeleteResponse:
    profile = get_profile_by_user_id(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    if profile.profile_status != ProfileStatus.DELETED:
        profile = update_profile(
            db,
            profile,
            {"profile_status": ProfileStatus.DELETED},
        )

    return SettingsDeleteResponse(
        success=True,
        profile_status=profile.profile_status,
        message="Profile deleted successfully.",
    )
