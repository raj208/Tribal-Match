from typing import Annotated

from fastapi import APIRouter, Depends

from app.modules.auth.dependencies import get_current_user, get_verified_supabase_claims
from app.modules.auth.schemas import SupabaseTokenIdentity
from app.modules.users.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/_health")
def auth_health() -> dict[str, str]:
    return {"module": "auth", "status": "ok"}


@router.get("/me")
def auth_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str | None]:
    return {
        "auth_source": "supabase_bearer",
        "id": str(current_user.id),
        "supabase_user_id": current_user.supabase_user_id,
        "email": current_user.email,
        "role": current_user.role,
        "account_status": current_user.account_status,
    }


@router.get("/_debug/me", response_model=SupabaseTokenIdentity)
def auth_debug_me(
    claims: Annotated[dict[str, object], Depends(get_verified_supabase_claims)],
) -> SupabaseTokenIdentity:
    return SupabaseTokenIdentity.from_claims(claims)
