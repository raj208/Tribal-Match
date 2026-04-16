from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.moderation.repository import (
    ReportWithContext,
    create_block,
    create_report,
    delete_block,
    get_report_with_context,
    get_block_by_users,
    list_reports_with_context,
    update_report_status,
)
from app.modules.moderation.schemas import (
    AdminProfileModerationActionResponse,
    AdminReportDetail,
    AdminReportListItem,
    AdminReportProfileSummary,
    AdminReportUserSummary,
)
from app.modules.profiles.models import Profile
from app.modules.profiles.repository import update_profile
from app.modules.users.models import User
from app.shared.enums import ProfileStatus, ReportStatus


_ALLOWED_REPORT_STATUS_TRANSITIONS: dict[ReportStatus, set[ReportStatus]] = {
    ReportStatus.OPEN: {ReportStatus.OPEN, ReportStatus.REVIEWED, ReportStatus.RESOLVED},
    ReportStatus.REVIEWED: {ReportStatus.REVIEWED, ReportStatus.RESOLVED},
    ReportStatus.RESOLVED: {ReportStatus.RESOLVED},
}


def _get_target_profile_or_404(db: Session, *, profile_id: UUID) -> Profile:
    stmt = select(Profile).where(Profile.id == profile_id)
    profile = db.scalar(stmt)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target profile not found",
        )

    return profile


def block_profile(db: Session, *, current_user: User, profile_id: UUID) -> dict:
    target_profile = _get_target_profile_or_404(db, profile_id=profile_id)

    if target_profile.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot block your own profile",
        )

    existing = get_block_by_users(
        db,
        blocker_user_id=current_user.id,
        blocked_user_id=target_profile.user_id,
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already blocked",
        )

    create_block(
        db,
        {
            "blocker_user_id": current_user.id,
            "blocked_user_id": target_profile.user_id,
        },
    )

    return {"message": "Profile blocked successfully"}


def unblock_profile(db: Session, *, current_user: User, profile_id: UUID) -> dict:
    target_profile = _get_target_profile_or_404(db, profile_id=profile_id)

    item = get_block_by_users(
        db,
        blocker_user_id=current_user.id,
        blocked_user_id=target_profile.user_id,
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Block record not found",
        )

    delete_block(db, item)
    return {"message": "Profile unblocked successfully"}


def report_profile(
    db: Session,
    *,
    current_user: User,
    profile_id: UUID,
    reason_code: str,
    notes: str | None,
) -> dict:
    target_profile = _get_target_profile_or_404(db, profile_id=profile_id)

    if target_profile.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot report your own profile",
        )

    create_report(
        db,
        {
            "reporter_user_id": current_user.id,
            "reported_user_id": target_profile.user_id,
            "reported_profile_id": target_profile.id,
            "reason_code": reason_code.strip().lower(),
            "notes": notes.strip() if notes else None,
        },
    )

    return {"message": "Report submitted successfully"}


def list_admin_reports(
    db: Session,
    *,
    report_status: ReportStatus | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[AdminReportListItem]:
    records = list_reports_with_context(
        db,
        report_status=report_status,
        limit=limit,
        offset=offset,
    )
    return [_build_admin_report_list_item(record) for record in records]


def get_admin_report_detail(db: Session, *, report_id: UUID) -> AdminReportDetail:
    record = get_report_with_context(db, report_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    return _build_admin_report_detail(record)


def update_admin_report_status(
    db: Session,
    *,
    report_id: UUID,
    next_status: ReportStatus,
) -> AdminReportDetail:
    record = get_report_with_context(db, report_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    current_status = _coerce_report_status(record.report.status)
    if next_status not in _ALLOWED_REPORT_STATUS_TRANSITIONS[current_status]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invalid report status transition",
        )

    update_report_status(db, record.report, next_status)
    refreshed_record = get_report_with_context(db, report_id)
    if refreshed_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    return _build_admin_report_detail(refreshed_record)


def hide_admin_profile(
    db: Session,
    *,
    profile_id: UUID,
) -> AdminProfileModerationActionResponse:
    profile = _get_target_profile_or_404(db, profile_id=profile_id)
    current_status = _coerce_profile_status(profile.profile_status)

    if current_status == ProfileStatus.HIDDEN:
        return _build_admin_profile_action_response(profile)

    if current_status != ProfileStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only published profiles can be hidden",
        )

    updated_profile = update_profile(db, profile, {"profile_status": ProfileStatus.HIDDEN})
    return _build_admin_profile_action_response(updated_profile)


def unhide_admin_profile(
    db: Session,
    *,
    profile_id: UUID,
) -> AdminProfileModerationActionResponse:
    profile = _get_target_profile_or_404(db, profile_id=profile_id)
    current_status = _coerce_profile_status(profile.profile_status)

    if current_status == ProfileStatus.PUBLISHED:
        return _build_admin_profile_action_response(profile)

    if current_status != ProfileStatus.HIDDEN:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only hidden profiles can be restored to published",
        )

    updated_profile = update_profile(db, profile, {"profile_status": ProfileStatus.PUBLISHED})
    return _build_admin_profile_action_response(updated_profile)


def _coerce_report_status(value: ReportStatus | str) -> ReportStatus:
    if isinstance(value, ReportStatus):
        return value

    return ReportStatus(str(value))


def _coerce_profile_status(value: ProfileStatus | str) -> ProfileStatus:
    if isinstance(value, ProfileStatus):
        return value

    return ProfileStatus(str(value))


def _build_user_summary(user: User) -> AdminReportUserSummary:
    return AdminReportUserSummary(
        id=user.id,
        email=user.email,
    )


def _build_profile_summary(profile: Profile) -> AdminReportProfileSummary:
    return AdminReportProfileSummary(
        id=profile.id,
        user_id=profile.user_id,
        full_name=profile.full_name,
        profile_status=profile.profile_status,
    )


def _build_admin_report_list_item(record: ReportWithContext) -> AdminReportListItem:
    return AdminReportListItem(
        id=record.report.id,
        reporter=_build_user_summary(record.reporter_user),
        reported_user=_build_user_summary(record.reported_user),
        reported_profile=_build_profile_summary(record.reported_profile),
        reason_code=record.report.reason_code,
        status=record.report.status,
        created_at=record.report.created_at,
    )


def _build_admin_report_detail(record: ReportWithContext) -> AdminReportDetail:
    return AdminReportDetail(
        **_build_admin_report_list_item(record).model_dump(),
        notes=record.report.notes,
        updated_at=record.report.updated_at,
    )


def _build_admin_profile_action_response(
    profile: Profile,
) -> AdminProfileModerationActionResponse:
    return AdminProfileModerationActionResponse(
        success=True,
        profile_id=profile.id,
        profile_status=profile.profile_status,
    )
