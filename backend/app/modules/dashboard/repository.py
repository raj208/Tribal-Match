from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.interests.models import Interest, Shortlist
from app.modules.media.models import IntroVideo, ProfilePhoto
from app.modules.profiles.models import Profile


def get_profile_by_user_id(db: Session, user_id: UUID) -> Profile | None:
    stmt = select(Profile).where(Profile.user_id == user_id)
    return db.scalar(stmt)


def count_photos_for_profile(db: Session, *, profile_id: UUID) -> int:
    stmt = select(func.count()).select_from(ProfilePhoto).where(ProfilePhoto.profile_id == profile_id)
    return db.scalar(stmt) or 0


def has_intro_video_for_profile(db: Session, *, profile_id: UUID) -> bool:
    stmt = select(func.count()).select_from(IntroVideo).where(IntroVideo.profile_id == profile_id)
    return (db.scalar(stmt) or 0) > 0


def count_shortlists_for_user(db: Session, *, user_id: UUID) -> int:
    stmt = select(func.count()).select_from(Shortlist).where(Shortlist.user_id == user_id)
    return db.scalar(stmt) or 0


def count_sent_interests_for_user(db: Session, *, user_id: UUID) -> int:
    stmt = select(func.count()).select_from(Interest).where(Interest.sender_user_id == user_id)
    return db.scalar(stmt) or 0


def count_received_interests_for_user(db: Session, *, user_id: UUID) -> int:
    stmt = select(func.count()).select_from(Interest).where(Interest.receiver_user_id == user_id)
    return db.scalar(stmt) or 0
