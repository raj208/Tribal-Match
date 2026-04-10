from fastapi import APIRouter

router = APIRouter(prefix="/interests", tags=["interests"])


@router.get("/_health")
def interests_health() -> dict[str, str]:
    return {"module": "interests", "status": "ok"}
