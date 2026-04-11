# Repository logic for the profiles module will be added in later steps.
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.profiles.models import Profile


def get_profile_by_user_id(db: Session, user_id: str) -> Profile | None:
    stmt = select(Profile).where(Profile.user_id == user_id)
    return db.scalar(stmt)


def create_profile(db: Session, data: dict) -> Profile:
    profile = Profile(**data)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_profile(db: Session, profile: Profile, data: dict) -> Profile:
    for key, value in data.items():
        setattr(profile, key, value)

    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile