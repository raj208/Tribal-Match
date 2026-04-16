from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_admin_user, get_current_user
from app.modules.moderation.schemas import (
    AdminProfileModerationActionResponse,
    AdminReportDetail,
    AdminReportListItem,
    AdminReportStatusUpdate,
    BlockCreate,
    BlockResponse,
    ReportCreate,
    ReportResponse,
)
from app.modules.moderation.service import (
    block_profile,
    hide_admin_profile,
    get_admin_report_detail,
    list_admin_reports,
    report_profile,
    unhide_admin_profile,
    unblock_profile,
    update_admin_report_status,
)
from app.modules.users.models import User
from app.shared.enums import ReportStatus

router = APIRouter(tags=["moderation"])


@router.get("/moderation/_health")
def moderation_health() -> dict[str, str]:
    return {"module": "moderation", "status": "ok"}


@router.get("/moderation/admin/_health")
def moderation_admin_health(
    _current_admin_user: Annotated[User, Depends(get_current_admin_user)],
) -> dict[str, str]:
    return {
        "module": "moderation",
        "scope": "admin",
        "status": "ok",
    }


@router.get("/admin/reports", response_model=list[AdminReportListItem])
def list_admin_reports_route(
    db: Annotated[Session, Depends(get_db)],
    _current_admin_user: Annotated[User, Depends(get_current_admin_user)],
    report_status: Annotated[ReportStatus | None, Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[AdminReportListItem]:
    return list_admin_reports(
        db,
        report_status=report_status,
        limit=limit,
        offset=offset,
    )


@router.get("/admin/reports/{report_id}", response_model=AdminReportDetail)
def get_admin_report_detail_route(
    report_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    _current_admin_user: Annotated[User, Depends(get_current_admin_user)],
) -> AdminReportDetail:
    return get_admin_report_detail(db, report_id=report_id)


@router.patch("/admin/reports/{report_id}", response_model=AdminReportDetail)
def update_admin_report_status_route(
    report_id: UUID,
    payload: AdminReportStatusUpdate,
    db: Annotated[Session, Depends(get_db)],
    _current_admin_user: Annotated[User, Depends(get_current_admin_user)],
) -> AdminReportDetail:
    return update_admin_report_status(
        db,
        report_id=report_id,
        next_status=payload.status,
    )


@router.post("/admin/profiles/{profile_id}/hide", response_model=AdminProfileModerationActionResponse)
def hide_admin_profile_route(
    profile_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    _current_admin_user: Annotated[User, Depends(get_current_admin_user)],
) -> AdminProfileModerationActionResponse:
    return hide_admin_profile(
        db,
        profile_id=profile_id,
    )


@router.post("/admin/profiles/{profile_id}/unhide", response_model=AdminProfileModerationActionResponse)
def unhide_admin_profile_route(
    profile_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    _current_admin_user: Annotated[User, Depends(get_current_admin_user)],
) -> AdminProfileModerationActionResponse:
    return unhide_admin_profile(
        db,
        profile_id=profile_id,
    )


@router.post("/blocks", response_model=BlockResponse, status_code=status.HTTP_201_CREATED)
def block_profile_route(
    payload: BlockCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> BlockResponse:
    return block_profile(db, current_user=current_user, profile_id=payload.profile_id)


@router.delete("/blocks/{profile_id}", response_model=BlockResponse)
def unblock_profile_route(
    profile_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> BlockResponse:
    return unblock_profile(db, current_user=current_user, profile_id=profile_id)


@router.post("/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def report_profile_route(
    payload: ReportCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ReportResponse:
    return report_profile(
        db,
        current_user=current_user,
        profile_id=payload.profile_id,
        reason_code=payload.reason_code,
        notes=payload.notes,
    )
