from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import (
    SupabaseAuthConfigurationError,
    SupabaseTokenVerificationError,
    verify_supabase_access_token,
)
from app.db.session import get_db
from app.modules.users.models import User
from app.modules.users.repository import (
    create_user,
    get_user_by_email,
    get_user_by_supabase_user_id,
    link_user_to_supabase_identity,
)

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
) -> User:
    claims = _verify_supabase_credentials(credentials, missing_detail="Authentication required")
    return _resolve_user_from_supabase_claims(db, claims)


def _verify_supabase_credentials(
    credentials: HTTPAuthorizationCredentials | None,
    missing_detail: str = "Bearer token required",
) -> dict[str, object]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=missing_detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials.strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=missing_detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return verify_supabase_access_token(token)
    except SupabaseAuthConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase token verification is not configured",
        ) from exc
    except SupabaseTokenVerificationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def _resolve_user_from_supabase_claims(db: Session, claims: dict[str, object]) -> User:
    supabase_user_id = _string_claim(claims, "sub")
    if not supabase_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token identity",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_supabase_user_id(db, supabase_user_id)
    if user:
        return user

    email = _string_claim(claims, "email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authenticated Supabase user is missing an email",
        )

    email = email.lower()
    user = get_user_by_email(db, email)
    if user:
        if user.supabase_user_id and user.supabase_user_id != supabase_user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User email is already linked to another Supabase identity",
            )

        if not user.supabase_user_id:
            return link_user_to_supabase_identity(db, user, supabase_user_id)

        return user

    return create_user(db, email, supabase_user_id=supabase_user_id)


def _string_claim(claims: dict[str, object], key: str) -> str | None:
    value = claims.get(key)
    if value is None:
        return None

    value = str(value).strip()
    if not value:
        return None

    return value


def get_verified_supabase_claims(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> dict[str, object]:
    return _verify_supabase_credentials(credentials)
