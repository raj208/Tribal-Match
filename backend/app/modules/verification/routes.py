from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.verification.schemas import VerificationRead
from app.modules.verification.service import get_my_verification, upsert_my_intro_video_file

router = APIRouter(prefix="/verification", tags=["verification"])


@router.get("/_health")
def verification_health() -> dict[str, str]:
    return {"module": "verification", "status": "ok"}


@router.get("/me", response_model=VerificationRead)
def get_my_verification_route(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> VerificationRead:
    return get_my_verification(db, current_user)


@router.post("/video/upload", response_model=VerificationRead, status_code=status.HTTP_201_CREATED)
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


@router.patch("/video/reupload", response_model=VerificationRead)
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