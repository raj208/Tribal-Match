from fastapi import APIRouter

router = APIRouter(prefix="/verification", tags=["verification"])


@router.get("/_health")
def verification_health() -> dict[str, str]:
    return {"module": "verification", "status": "ok"}
