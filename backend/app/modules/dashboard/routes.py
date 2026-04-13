from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.dashboard.schemas import DashboardSummary
from app.modules.dashboard.service import get_dashboard_summary
from app.modules.users.models import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary_route(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> DashboardSummary:
    return get_dashboard_summary(db, current_user=current_user)
