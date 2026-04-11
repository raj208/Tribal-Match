from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.profiles.schemas import ProfileCreate, ProfileRead, ProfileUpdate
from app.modules.profiles.service import (
    create_my_profile,
    get_my_profile,
    update_my_profile,
)
from app.modules.users.models import User

router = APIRouter(prefix="/profile", tags=["profiles"])


@router.get("/_health")
def profiles_health() -> dict[str, str]:
    return {"module": "profiles", "status": "ok"}


@router.post("", response_model=ProfileRead, status_code=status.HTTP_201_CREATED)
def create_profile_route(
    payload: ProfileCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProfileRead:
    return create_my_profile(db, current_user, payload)


@router.get("/me", response_model=ProfileRead)
def get_my_profile_route(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProfileRead:
    return get_my_profile(db, current_user)


@router.patch("/me", response_model=ProfileRead)
def update_my_profile_route(
    payload: ProfileUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProfileRead:
    return update_my_profile(db, current_user, payload)