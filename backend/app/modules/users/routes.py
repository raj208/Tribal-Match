from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/_health")
def users_health() -> dict[str, str]:
    return {"module": "users", "status": "ok"}
