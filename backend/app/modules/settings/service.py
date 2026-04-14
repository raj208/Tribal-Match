from sqlalchemy.orm import Session

from app.modules.settings.repository import get_profile_by_user_id
from app.modules.settings.schemas import SettingsMeRead
from app.modules.users.models import User
from app.shared.enums import VerificationStatus


def get_my_settings_summary(db: Session, *, current_user: User) -> SettingsMeRead:
    profile = get_profile_by_user_id(db, user_id=current_user.id)
    if not profile:
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
