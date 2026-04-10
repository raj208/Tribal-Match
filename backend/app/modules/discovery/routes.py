from fastapi import APIRouter

router = APIRouter(prefix="/profiles", tags=["discovery"])


@router.get("/_health")
def discovery_health() -> dict[str, str]:
    return {"module": "discovery", "status": "ok"}
