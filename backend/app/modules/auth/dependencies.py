# Auth-related FastAPI dependencies will be added in later steps.
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.users.models import User
from app.modules.users.repository import create_user, get_user_by_email

DEV_USER_EMAIL = "demo@tribalmatch.local"


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    x_user_email: Annotated[str | None, Header()] = None,
) -> User:
    email = (x_user_email or DEV_USER_EMAIL).strip().lower()

    user = get_user_by_email(db, email)
    if user:
        return user

    return create_user(db, email)