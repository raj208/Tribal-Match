from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.profiles.models import Profile
from app.modules.users.models import User
from app.shared.enums import ProfileStatus, VerificationStatus

SETTINGS_ME_PATH = f"{settings.api_v1_prefix}/settings/me"


def _auth_headers(email: str) -> dict[str, str]:
    return {"X-User-Email": email}


def _create_user(db: Session, email: str) -> User:
    user = User(email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _create_profile(
    db: Session,
    *,
    user: User,
    full_name: str,
    profile_visibility: str = "public",
    profile_status: ProfileStatus = ProfileStatus.DRAFT,
    verification_status: VerificationStatus = VerificationStatus.NOT_STARTED,
    completion_percentage: int = 0,
) -> Profile:
    profile = Profile(
        user_id=user.id,
        full_name=full_name,
        profile_visibility=profile_visibility,
        profile_status=profile_status,
        verification_status=verification_status,
        completion_percentage=completion_percentage,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def test_settings_me_requires_auth(client) -> None:
    response = client.get(SETTINGS_ME_PATH)

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_settings_me_returns_defaults_when_profile_is_missing(client) -> None:
    response = client.get(
        SETTINGS_ME_PATH,
        headers=_auth_headers("no-profile-settings@example.com"),
    )

    assert response.status_code == 200
    assert response.json() == {
        "email": "no-profile-settings@example.com",
        "profile_exists": False,
        "profile_visibility": None,
        "profile_status": None,
        "verification_status": "not_started",
        "completion_percentage": 0,
    }


def test_settings_me_returns_existing_profile_summary(client, db_session: Session) -> None:
    user = _create_user(db_session, "settings-user@example.com")
    _create_profile(
        db_session,
        user=user,
        full_name="Settings User",
        profile_visibility="public",
        profile_status=ProfileStatus.PUBLISHED,
        verification_status=VerificationStatus.UPLOADED,
        completion_percentage=80,
    )

    response = client.get(
        SETTINGS_ME_PATH,
        headers=_auth_headers(user.email),
    )

    assert response.status_code == 200
    assert response.json() == {
        "email": "settings-user@example.com",
        "profile_exists": True,
        "profile_visibility": "public",
        "profile_status": "published",
        "verification_status": "uploaded",
        "completion_percentage": 80,
    }
