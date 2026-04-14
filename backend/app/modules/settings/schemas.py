from pydantic import BaseModel

from app.shared.enums import ProfileStatus, VerificationStatus


class SettingsMeRead(BaseModel):
    email: str
    profile_exists: bool
    profile_visibility: str | None
    profile_status: ProfileStatus | None
    verification_status: VerificationStatus | None
    completion_percentage: int
