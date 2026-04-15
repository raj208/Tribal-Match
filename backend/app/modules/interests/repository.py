from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.modules.interests.models import Interest, Shortlist
from app.modules.profiles.models import Profile


def get_shortlist_by_user_and_profile(
    db: Session,
    *,
    user_id: UUID,
    profile_id: UUID,
) -> Shortlist | None:
    stmt = select(Shortlist).where(
        Shortlist.user_id == user_id,
        Shortlist.shortlisted_profile_id == profile_id,
    )
    return db.scalar(stmt)


def create_shortlist(db: Session, data: dict) -> Shortlist:
    item = Shortlist(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_shortlists_for_user(db: Session, *, user_id: UUID) -> list[Shortlist]:
    stmt = (
        select(Shortlist)
        .options(joinedload(Shortlist.profile).selectinload(Profile.photos))
        .where(Shortlist.user_id == user_id)
        .order_by(Shortlist.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def get_shortlist_by_id_for_user(
    db: Session,
    *,
    shortlist_id: UUID,
    user_id: UUID,
) -> Shortlist | None:
    stmt = select(Shortlist).where(
        Shortlist.id == shortlist_id,
        Shortlist.user_id == user_id,
    )
    return db.scalar(stmt)


def delete_shortlist(db: Session, shortlist: Shortlist) -> None:
    db.delete(shortlist)
    db.commit()


def get_interest_by_sender_receiver(
    db: Session,
    *,
    sender_user_id: UUID,
    receiver_user_id: UUID,
) -> Interest | None:
    stmt = select(Interest).where(
        Interest.sender_user_id == sender_user_id,
        Interest.receiver_user_id == receiver_user_id,
    )
    return db.scalar(stmt)


def create_interest(db: Session, data: dict) -> Interest:
    item = Interest(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_interest_by_id(db: Session, *, interest_id: UUID) -> Interest | None:
    stmt = select(Interest).where(Interest.id == interest_id)
    return db.scalar(stmt)


def update_interest(db: Session, interest: Interest, data: dict) -> Interest:
    for key, value in data.items():
        setattr(interest, key, value)

    db.add(interest)
    db.commit()
    db.refresh(interest)
    return interest


def list_sent_interests_for_user(db: Session, *, user_id: UUID) -> list[Interest]:
    stmt = (
        select(Interest)
        .options(joinedload(Interest.receiver_profile).selectinload(Profile.photos))
        .where(Interest.sender_user_id == user_id)
        .order_by(Interest.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def list_received_interests_for_user(db: Session, *, user_id: UUID) -> list[Interest]:
    stmt = (
        select(Interest)
        .options(joinedload(Interest.sender_profile).selectinload(Profile.photos))
        .where(Interest.receiver_user_id == user_id)
        .order_by(Interest.created_at.desc())
    )
    return list(db.scalars(stmt).all())
