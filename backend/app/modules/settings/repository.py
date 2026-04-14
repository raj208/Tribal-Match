from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.profiles.models import Profile


def get_profile_by_user_id(db: Session, *, user_id: UUID) -> Profile | None:
    stmt = select(Profile).where(Profile.user_id == user_id)
    return db.scalar(stmt)
