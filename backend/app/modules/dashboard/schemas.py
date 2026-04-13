from pydantic import BaseModel

from app.shared.enums import ProfileStatus, VerificationStatus


class DashboardSummary(BaseModel):
    profile_exists: bool
    profile_status: ProfileStatus | None
    completion_percentage: int
    verification_status: VerificationStatus
    photo_count: int
    has_intro_video: bool
    shortlist_count: int
    sent_interests_count: int
    received_interests_count: int
