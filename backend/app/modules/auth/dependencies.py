from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.users.models import User
from app.modules.users.repository import create_user, get_user_by_email


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    x_user_email: Annotated[str | None, Header()] = None,
) -> User:
    if not x_user_email or not x_user_email.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    email = x_user_email.strip().lower()

    user = get_user_by_email(db, email)
    if user:
        return user

    return create_user(db, email)