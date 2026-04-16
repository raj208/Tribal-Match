from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.media.models import IntroVideo
from app.modules.profiles.models import Profile
from app.modules.users.models import User
from app.shared.enums import VerificationStatus


@dataclass(frozen=True)
class IntroVideoWithContext:
    intro_video: IntroVideo
    profile: Profile
    user: User


def get_intro_video_by_profile_id(db: Session, profile_id: UUID) -> IntroVideo | None:
    stmt = select(IntroVideo).where(IntroVideo.profile_id == profile_id)
    return db.scalar(stmt)


def create_intro_video(db: Session, data: dict) -> IntroVideo:
    video = IntroVideo(**data)
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


def update_intro_video(db: Session, video: IntroVideo, data: dict) -> IntroVideo:
    for key, value in data.items():
        setattr(video, key, value)

    db.add(video)
    db.commit()
    db.refresh(video)
    return video


def list_intro_videos_for_review(
    db: Session,
    *,
    statuses: tuple[VerificationStatus, ...],
    limit: int = 50,
    offset: int = 0,
) -> list[IntroVideoWithContext]:
    stmt = (
        select(IntroVideo, Profile, User)
        .join(Profile, IntroVideo.profile_id == Profile.id)
        .join(User, IntroVideo.user_id == User.id)
        .where(IntroVideo.verification_status.in_(statuses))
        .order_by(IntroVideo.created_at.desc(), IntroVideo.id.desc())
        .limit(limit)
        .offset(offset)
    )

    rows = db.execute(stmt).all()
    return [
        IntroVideoWithContext(
            intro_video=intro_video,
            profile=profile,
            user=user,
        )
        for intro_video, profile, user in rows
    ]


def get_intro_video_with_context(
    db: Session,
    *,
    intro_video_id: UUID,
) -> IntroVideoWithContext | None:
    stmt = (
        select(IntroVideo, Profile, User)
        .join(Profile, IntroVideo.profile_id == Profile.id)
        .join(User, IntroVideo.user_id == User.id)
        .where(IntroVideo.id == intro_video_id)
    )
    row = db.execute(stmt).one_or_none()
    if row is None:
        return None

    intro_video, profile, user = row
    return IntroVideoWithContext(
        intro_video=intro_video,
        profile=profile,
        user=user,
    )
