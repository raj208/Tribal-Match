from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.discovery.schemas import DiscoverProfileListResponse, PublicProfileRead
from app.modules.discovery.service import browse_profiles, get_profile_detail
from app.modules.users.models import User

router = APIRouter(prefix="/profiles", tags=["discovery"])


@router.get("/_health")
def discovery_health() -> dict[str, str]:
    return {"module": "discovery", "status": "ok"}


@router.get("", response_model=DiscoverProfileListResponse)
def browse_profiles_route(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    q: str | None = Query(default=None),
    min_age: int | None = Query(default=None, ge=18, le=100),
    max_age: int | None = Query(default=None, ge=18, le=100),
    community: str | None = Query(default=None),
    native_language: str | None = Query(default=None),
    city: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=12, ge=1, le=50),
) -> DiscoverProfileListResponse:
    return browse_profiles(
        db,
        current_user=current_user,
        q=q,
        min_age=min_age,
        max_age=max_age,
        community=community,
        native_language=native_language,
        city=city,
        page=page,
        size=size,
    )


@router.get("/{profile_id}", response_model=PublicProfileRead)
def profile_detail_route(
    profile_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PublicProfileRead:
    return get_profile_detail(
        db,
        current_user=current_user,
        profile_id=profile_id,
    )