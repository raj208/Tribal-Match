from typing import Any

from pydantic import BaseModel


def _string_claim(claims: dict[str, Any], key: str) -> str | None:
    value = claims.get(key)
    if value is None:
        return None
    return str(value)


class SupabaseTokenIdentity(BaseModel):
    auth_source: str = "supabase_bearer"
    sub: str
    email: str | None = None
    phone: str | None = None
    role: str | None = None
    aud: str | list[str] | None = None
    iss: str | None = None
    exp: int | None = None
    iat: int | None = None
    session_id: str | None = None
    aal: str | None = None
    is_anonymous: bool | None = None

    @classmethod
    def from_claims(cls, claims: dict[str, Any]) -> "SupabaseTokenIdentity":
        return cls(
            sub=str(claims["sub"]),
            email=_string_claim(claims, "email"),
            phone=_string_claim(claims, "phone"),
            role=_string_claim(claims, "role"),
            aud=claims.get("aud"),
            iss=_string_claim(claims, "iss"),
            exp=claims.get("exp"),
            iat=claims.get("iat"),
            session_id=_string_claim(claims, "session_id"),
            aal=_string_claim(claims, "aal"),
            is_anonymous=claims.get("is_anonymous"),
        )
