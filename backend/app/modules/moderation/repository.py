from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.modules.moderation.models import Block, Report


def get_block_by_users(
    db: Session,
    *,
    blocker_user_id: UUID,
    blocked_user_id: UUID,
) -> Block | None:
    stmt = select(Block).where(
        Block.blocker_user_id == blocker_user_id,
        Block.blocked_user_id == blocked_user_id,
    )
    return db.scalar(stmt)


def is_blocked_between(
    db: Session,
    *,
    user_a_id: UUID,
    user_b_id: UUID,
) -> bool:
    stmt = select(Block.id).where(
        or_(
            and_(Block.blocker_user_id == user_a_id, Block.blocked_user_id == user_b_id),
            and_(Block.blocker_user_id == user_b_id, Block.blocked_user_id == user_a_id),
        )
    )
    return db.scalar(stmt) is not None


def create_block(db: Session, data: dict) -> Block:
    item = Block(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def delete_block(db: Session, item: Block) -> None:
    db.delete(item)
    db.commit()


def create_report(db: Session, data: dict) -> Report:
    item = Report(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item