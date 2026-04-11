from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.modules.profiles.models import Preference, Profile


def get_profile_by_user_id(db: Session, user_id: str) -> Profile | None:
    stmt = (
        select(Profile)
        .options(joinedload(Profile.preferences))
        .where(Profile.user_id == user_id)
    )
    return db.scalar(stmt)


def get_preference_by_user_id(db: Session, user_id: str) -> Preference | None:
    stmt = select(Preference).where(Preference.user_id == user_id)
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


def create_preference(db: Session, data: dict) -> Preference:
    preference = Preference(**data)
    db.add(preference)
    db.commit()
    db.refresh(preference)
    return preference


def update_preference(db: Session, preference: Preference, data: dict) -> Preference:
    for key, value in data.items():
        setattr(preference, key, value)

    db.add(preference)
    db.commit()
    db.refresh(preference)
    return preference