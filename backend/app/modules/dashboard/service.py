from sqlalchemy.orm import Session

from app.modules.dashboard.repository import (
    count_photos_for_profile,
    count_received_interests_for_user,
    count_sent_interests_for_user,
    count_shortlists_for_user,
    get_profile_by_user_id,
    has_intro_video_for_profile,
)
from app.modules.dashboard.schemas import DashboardSummary
from app.modules.users.models import User
from app.shared.enums import VerificationStatus


def get_dashboard_summary(db: Session, *, current_user: User) -> DashboardSummary:
    profile = get_profile_by_user_id(db, current_user.id)
    if not profile:
        return DashboardSummary(
            profile_exists=False,
            profile_status=None,
            completion_percentage=0,
            verification_status=VerificationStatus.NOT_STARTED,
            photo_count=0,
            has_intro_video=False,
            shortlist_count=0,
            sent_interests_count=0,
            received_interests_count=0,
        )

    return DashboardSummary(
        profile_exists=True,
        profile_status=profile.profile_status,
        completion_percentage=profile.completion_percentage,
        verification_status=profile.verification_status,
        photo_count=count_photos_for_profile(db, profile_id=profile.id),
        has_intro_video=has_intro_video_for_profile(db, profile_id=profile.id),
        shortlist_count=count_shortlists_for_user(db, user_id=current_user.id),
        sent_interests_count=count_sent_interests_for_user(db, user_id=current_user.id),
        received_interests_count=count_received_interests_for_user(db, user_id=current_user.id),
    )
