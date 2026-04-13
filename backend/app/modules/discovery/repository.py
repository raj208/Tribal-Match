from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.modules.profiles.models import Profile
from app.shared.enums import ProfileStatus


def _build_conditions(
    *,
    current_user_id: UUID,
    q: str | None = None,
    min_age: int | None = None,
    max_age: int | None = None,
    community: str | None = None,
    native_language: str | None = None,
    city: str | None = None,
) -> list:
    conditions = [
        Profile.profile_status == ProfileStatus.PUBLISHED,
        Profile.user_id != current_user_id,
    ]

    if q:
        needle = f"%{q.strip()}%"
        conditions.append(
            or_(
                Profile.full_name.ilike(needle),
                Profile.community_or_tribe.ilike(needle),
                Profile.native_language.ilike(needle),
                Profile.location_city.ilike(needle),
                Profile.location_state.ilike(needle),
                Profile.occupation.ilike(needle),
            )
        )

    if min_age is not None:
        conditions.append(Profile.age >= min_age)

    if max_age is not None:
        conditions.append(Profile.age <= max_age)

    if community:
        conditions.append(Profile.community_or_tribe.ilike(f"%{community.strip()}%"))

    if native_language:
        conditions.append(Profile.native_language.ilike(f"%{native_language.strip()}%"))

    if city:
        conditions.append(Profile.location_city.ilike(f"%{city.strip()}%"))

    return conditions


def list_discoverable_profiles(
    db: Session,
    *,
    current_user_id: UUID,
    q: str | None,
    min_age: int | None,
    max_age: int | None,
    community: str | None,
    native_language: str | None,
    city: str | None,
    page: int,
    size: int,
) -> tuple[list[Profile], int]:
    conditions = _build_conditions(
        current_user_id=current_user_id,
        q=q,
        min_age=min_age,
        max_age=max_age,
        community=community,
        native_language=native_language,
        city=city,
    )

    total_stmt = select(func.count()).select_from(Profile).where(*conditions)
    total = db.scalar(total_stmt) or 0

    stmt = (
        select(Profile)
        .options(
            selectinload(Profile.photos),
            selectinload(Profile.intro_video),
        )
        .where(*conditions)
        .order_by(Profile.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )

    items = list(db.scalars(stmt).all())
    return items, total


def get_discoverable_profile_by_id(
    db: Session,
    *,
    profile_id: UUID,
    current_user_id: UUID,
) -> Profile | None:
    stmt = (
        select(Profile)
        .options(
            selectinload(Profile.photos),
            selectinload(Profile.intro_video),
        )
        .where(
            Profile.id == profile_id,
            Profile.profile_status == ProfileStatus.PUBLISHED,
            Profile.user_id != current_user_id,
        )
    )
    return db.scalar(stmt)