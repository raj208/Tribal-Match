from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_admin_user, get_current_user
from app.modules.moderation.schemas import (
    BlockCreate,
    BlockResponse,
    ReportCreate,
    ReportResponse,
)
from app.modules.moderation.service import block_profile, report_profile, unblock_profile
from app.modules.users.models import User

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
