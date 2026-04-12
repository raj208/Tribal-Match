# Repository logic for the verification module will be added in later steps.
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.media.models import IntroVideo


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