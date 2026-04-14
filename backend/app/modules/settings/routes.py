from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.settings.schemas import (
    SettingsDeactivateResponse,
    SettingsMeRead,
    SettingsMeUpdate,
)
from app.modules.settings.service import (
    deactivate_my_profile,
    get_my_settings_summary,
    update_my_settings_summary,
)
from app.modules.users.models import User

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/_health")
def settings_health() -> dict[str, str]:
    return {"module": "settings", "status": "ok"}


@router.get("/me", response_model=SettingsMeRead)
def get_my_settings_route(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SettingsMeRead:
    return get_my_settings_summary(db, current_user=current_user)


@router.patch("/me", response_model=SettingsMeRead)
def update_my_settings_route(
    payload: SettingsMeUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SettingsMeRead:
    return update_my_settings_summary(db, current_user=current_user, payload=payload)


@router.post("/deactivate", response_model=SettingsDeactivateResponse)
def deactivate_my_profile_route(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SettingsDeactivateResponse:
    return deactivate_my_profile(db, current_user=current_user)
