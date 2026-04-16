from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_admin_user, get_current_user
from app.modules.users.models import User
from app.modules.verification.schemas import (
    AdminVerificationDetail,
    AdminVerificationQueueItem,
    AdminVerificationReviewUpdate,
    VerificationRead,
)
from app.modules.verification.service import (
    get_admin_verification_item,
    get_my_verification,
    list_admin_verification_queue,
    review_admin_verification_item,
    upsert_my_intro_video_file,
)

user_router = APIRouter(prefix="/verification", tags=["verification"])
admin_router = APIRouter(tags=["verification"])
router = APIRouter()


@user_router.get("/_health")
def verification_health() -> dict[str, str]:
    return {"module": "verification", "status": "ok"}


@user_router.get("/me", response_model=VerificationRead)
def get_my_verification_route(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> VerificationRead:
    return get_my_verification(db, current_user)


@user_router.post("/video/upload", response_model=VerificationRead, status_code=status.HTTP_201_CREATED)
def upload_intro_video_route(
    file: UploadFile = File(...),
    duration_seconds: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VerificationRead:
    return upsert_my_intro_video_file(
        db,
        current_user,
        file=file,
        duration_seconds=duration_seconds,
    )


@user_router.patch("/video/reupload", response_model=VerificationRead)
def reupload_intro_video_route(
    file: UploadFile = File(...),
    duration_seconds: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VerificationRead:
    return upsert_my_intro_video_file(
        db,
        current_user,
        file=file,
        duration_seconds=duration_seconds,
    )


@admin_router.get("/admin/verifications", response_model=list[AdminVerificationQueueItem])
def list_admin_verifications_route(
    db: Annotated[Session, Depends(get_db)],
    _current_admin_user: Annotated[User, Depends(get_current_admin_user)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[AdminVerificationQueueItem]:
    return list_admin_verification_queue(
        db,
        limit=limit,
        offset=offset,
    )


@admin_router.get("/admin/verifications/{item_id}", response_model=AdminVerificationDetail)
def get_admin_verification_item_route(
    item_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    _current_admin_user: Annotated[User, Depends(get_current_admin_user)],
) -> AdminVerificationDetail:
    return get_admin_verification_item(
        db,
        item_id=item_id,
    )


@admin_router.patch("/admin/verifications/{item_id}", response_model=AdminVerificationDetail)
def review_admin_verification_item_route(
    item_id: UUID,
    payload: AdminVerificationReviewUpdate,
    db: Annotated[Session, Depends(get_db)],
    _current_admin_user: Annotated[User, Depends(get_current_admin_user)],
) -> AdminVerificationDetail:
    return review_admin_verification_item(
        db,
        item_id=item_id,
        next_status=payload.status,
        reason=payload.reason,
    )


router.include_router(user_router)
router.include_router(admin_router)
