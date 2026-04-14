from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.settings.schemas import SettingsMeRead
from app.modules.settings.service import get_my_settings_summary
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
