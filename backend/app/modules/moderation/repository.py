from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, aliased

from app.modules.moderation.models import Block, Report
from app.modules.profiles.models import Profile
from app.modules.users.models import User
from app.shared.enums import ReportStatus


@dataclass(frozen=True)
class ReportWithContext:
    report: Report
    reporter_user: User
    reported_user: User
    reported_profile: Profile


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


def list_reports_with_context(
    db: Session,
    *,
    report_status: ReportStatus | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[ReportWithContext]:
    reporter_user = aliased(User)
    reported_user = aliased(User)

    stmt = (
        select(Report, reporter_user, reported_user, Profile)
        .join(reporter_user, Report.reporter_user_id == reporter_user.id)
        .join(reported_user, Report.reported_user_id == reported_user.id)
        .join(Profile, Report.reported_profile_id == Profile.id)
    )
    if report_status is not None:
        stmt = stmt.where(Report.status == report_status)

    stmt = stmt.order_by(Report.created_at.desc(), Report.id.desc()).limit(limit).offset(offset)

    rows = db.execute(stmt).all()
    return [
        ReportWithContext(
            report=report,
            reporter_user=reporter,
            reported_user=reported,
            reported_profile=profile,
        )
        for report, reporter, reported, profile in rows
    ]


def get_report_with_context(db: Session, report_id: UUID) -> ReportWithContext | None:
    reporter_user = aliased(User)
    reported_user = aliased(User)

    stmt = (
        select(Report, reporter_user, reported_user, Profile)
        .join(reporter_user, Report.reporter_user_id == reporter_user.id)
        .join(reported_user, Report.reported_user_id == reported_user.id)
        .join(Profile, Report.reported_profile_id == Profile.id)
        .where(Report.id == report_id)
    )
    row = db.execute(stmt).one_or_none()
    if row is None:
        return None

    report, reporter, reported, profile = row
    return ReportWithContext(
        report=report,
        reporter_user=reporter,
        reported_user=reported,
        reported_profile=profile,
    )


def update_report_status(db: Session, report: Report, report_status: ReportStatus) -> Report:
    report.status = report_status
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
