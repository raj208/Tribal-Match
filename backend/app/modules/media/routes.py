from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.media.schemas import (
    PhotoConfirmRequest,
    PhotoDeleteResponse,
    PhotoRead,
    PhotoUploadIntentRequest,
    PhotoUploadIntentResponse,
)
from app.modules.media.service import (
    confirm_my_photo_upload,
    create_my_photo_upload_intent,
    delete_my_photo,
    list_my_photos,
    serialize_photo,
    set_my_primary_photo,
    upload_my_photo_file,
)
from app.modules.users.models import User

router = APIRouter(prefix="/media", tags=["media"])


@router.get("/_health")
def media_health() -> dict[str, str]:
    return {"module": "media", "status": "ok"}


@router.get("/photos/me", response_model=list[PhotoRead])
def list_my_photos_route(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[PhotoRead]:
    return list_my_photos(db, current_user)


@router.post("/photos/upload-intent", response_model=PhotoUploadIntentResponse)
def create_photo_upload_intent_route(
    payload: PhotoUploadIntentRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PhotoUploadIntentResponse:
    return create_my_photo_upload_intent(
        db,
        current_user,
        filename=payload.filename,
        content_type=payload.content_type,
    )


@router.post("/photos/confirm", response_model=PhotoRead, status_code=status.HTTP_201_CREATED)
def confirm_photo_upload_route(
    payload: PhotoConfirmRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PhotoRead:
    return confirm_my_photo_upload(
        db,
        current_user,
        object_key=payload.object_key,
        content_type=payload.content_type,
        sort_order=payload.sort_order,
        make_primary=payload.make_primary,
    )


@router.post("/photos/upload", response_model=PhotoRead, status_code=status.HTTP_201_CREATED)
def upload_photo_route(
    file: UploadFile = File(...),
    sort_order: int = Form(0),
    is_primary: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PhotoRead:
    photo = upload_my_photo_file(
        db,
        current_user,
        file=file,
        sort_order=sort_order,
        is_primary=is_primary,
    )
    return serialize_photo(photo)


@router.patch("/photos/{photo_id}/primary", response_model=PhotoRead)
def set_primary_photo_route(
    photo_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PhotoRead:
    return set_my_primary_photo(db, current_user, photo_id)


@router.delete("/photos/{photo_id}", response_model=PhotoDeleteResponse)
def delete_photo_route(
    photo_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PhotoDeleteResponse:
    delete_my_photo(db, current_user, photo_id)
    return PhotoDeleteResponse(message="Photo deleted successfully")
