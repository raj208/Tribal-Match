from typing import Annotated

from fastapi import APIRouter, Depends

from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/_health")
def auth_health() -> dict[str, str]:
    return {"module": "auth", "status": "ok"}


@router.get("/me")
def auth_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role,
        "account_status": current_user.account_status,
    }