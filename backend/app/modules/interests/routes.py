from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.interests.schemas import (
    InterestActionRequest,
    InterestActionResponse,
    InterestCreate,
    InterestListItem,
    ShortlistCreate,
    ShortlistItem,
)
from app.modules.interests.service import (
    act_on_interest,
    add_to_shortlist,
    list_my_received_interests,
    list_my_sent_interests,
    list_my_shortlists,
    remove_from_shortlist,
    send_interest,
    withdraw_interest,
)
from app.modules.users.models import User

router = APIRouter(tags=["interests"])


@router.get("/interests/_health")
def interests_health() -> dict[str, str]:
    return {"module": "interests", "status": "ok"}


@router.post("/shortlist", response_model=ShortlistItem, status_code=status.HTTP_201_CREATED)
def add_to_shortlist_route(
    payload: ShortlistCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ShortlistItem:
    return add_to_shortlist(db, current_user=current_user, profile_id=payload.profile_id)


@router.get("/shortlist", response_model=list[ShortlistItem])
def list_shortlist_route(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[ShortlistItem]:
    return list_my_shortlists(db, current_user=current_user)


@router.delete("/shortlist/{shortlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shortlist_route(
    shortlist_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    remove_from_shortlist(db, current_user=current_user, shortlist_id=shortlist_id)
    return None


@router.post("/interests", response_model=InterestListItem, status_code=status.HTTP_201_CREATED)
def send_interest_route(
    payload: InterestCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> InterestListItem:
    return send_interest(
        db,
        current_user=current_user,
        receiver_profile_id=payload.receiver_profile_id,
    )


@router.get("/interests/sent", response_model=list[InterestListItem])
def list_sent_interests_route(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[InterestListItem]:
    return list_my_sent_interests(db, current_user=current_user)


@router.get("/interests/received", response_model=list[InterestListItem])
def list_received_interests_route(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[InterestListItem]:
    return list_my_received_interests(db, current_user=current_user)


@router.patch("/interests/{interest_id}", response_model=InterestActionResponse)
def act_on_interest_route(
    interest_id: UUID,
    payload: InterestActionRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> InterestActionResponse:
    return act_on_interest(
        db,
        current_user=current_user,
        interest_id=interest_id,
        action=payload.action,
    )


@router.delete("/interests/{interest_id}", status_code=status.HTTP_204_NO_CONTENT)
def withdraw_interest_route(
    interest_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    withdraw_interest(db, current_user=current_user, interest_id=interest_id)
    return None
