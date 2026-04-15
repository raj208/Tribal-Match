from functools import lru_cache
from typing import Any

from app.core.config import Settings, settings


class SupabaseAuthConfigurationError(RuntimeError):
    pass


class SupabaseTokenVerificationError(RuntimeError):
    pass


def _load_pyjwt() -> Any:
    try:
        import jwt
    except ImportError as exc:
        raise SupabaseAuthConfigurationError(
            "PyJWT is required for Supabase token verification. Install backend requirements."
        ) from exc

    return jwt


def _supabase_auth_issuer(config: Settings) -> str:
    configured_issuer = config.supabase_jwt_issuer.strip().rstrip("/")
    if configured_issuer:
        return configured_issuer

    supabase_url = config.supabase_url.strip().rstrip("/")
    if not supabase_url:
        raise SupabaseAuthConfigurationError(
            "SUPABASE_URL or SUPABASE_JWT_ISSUER must be configured for token verification."
        )

    if supabase_url.endswith("/auth/v1"):
        return supabase_url

    return f"{supabase_url}/auth/v1"


def _supabase_jwks_url(config: Settings, issuer: str) -> str:
    configured_jwks_url = config.supabase_jwks_url.strip()
    if configured_jwks_url:
        return configured_jwks_url

    return f"{issuer}/.well-known/jwks.json"


def _allowed_algorithms(config: Settings) -> list[str]:
    return [
        algorithm.strip()
        for algorithm in config.supabase_jwt_algorithms.split(",")
        if algorithm.strip()
    ]


@lru_cache(maxsize=8)
def _get_jwks_client(jwks_url: str) -> Any:
    jwt = _load_pyjwt()
    return jwt.PyJWKClient(jwks_url, cache_keys=True, timeout=5)


def verify_supabase_access_token(
    token: str,
    config: Settings = settings,
) -> dict[str, Any]:
    jwt = _load_pyjwt()
    issuer = _supabase_auth_issuer(config)
    audience = config.supabase_jwt_audience.strip() or "authenticated"
    allowed_algorithms = _allowed_algorithms(config)

    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.PyJWTError as exc:
        raise SupabaseTokenVerificationError("Invalid bearer token header.") from exc

    algorithm = str(unverified_header.get("alg") or "")
    if algorithm not in allowed_algorithms:
        raise SupabaseTokenVerificationError("Bearer token uses an unsupported signing algorithm.")

    decode_options = {
        "require": ["aud", "exp", "iss", "sub"],
    }

    try:
        if algorithm.startswith("HS"):
            jwt_secret = config.supabase_jwt_secret.strip()
            if not jwt_secret:
                raise SupabaseAuthConfigurationError(
                    "SUPABASE_JWT_SECRET must be configured to verify symmetric Supabase tokens."
                )

            claims = jwt.decode(
                token,
                jwt_secret,
                algorithms=[algorithm],
                audience=audience,
                issuer=issuer,
                options=decode_options,
            )
        else:
            jwks_url = _supabase_jwks_url(config, issuer)
            signing_key = _get_jwks_client(jwks_url).get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=[algorithm],
                audience=audience,
                issuer=issuer,
                options=decode_options,
            )
    except SupabaseAuthConfigurationError:
        raise
    except jwt.PyJWTError as exc:
        raise SupabaseTokenVerificationError("Invalid or expired bearer token.") from exc

    subject = claims.get("sub")
    if not isinstance(subject, str) or not subject.strip():
        raise SupabaseTokenVerificationError("Bearer token is missing a subject.")

    return claims
