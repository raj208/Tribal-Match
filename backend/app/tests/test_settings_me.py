from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.profiles.models import Profile
from app.modules.users.models import User
from app.shared.enums import ProfileStatus, VerificationStatus

SETTINGS_ME_PATH = f"{settings.api_v1_prefix}/settings/me"


def _auth_headers(email: str) -> dict[str, str]:
    return {"Authorization": f"Bearer test-token:{email}"}


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


def test_patch_settings_me_requires_auth(client) -> None:
    response = client.patch(
        SETTINGS_ME_PATH,
        json={"profile_visibility": "private"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_patch_settings_me_returns_404_when_profile_is_missing(client) -> None:
    response = client.patch(
        SETTINGS_ME_PATH,
        headers=_auth_headers("missing-profile-update@example.com"),
        json={"profile_visibility": "private"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Profile not found"}


def test_patch_settings_me_updates_profile_visibility_and_returns_summary(client, db_session: Session) -> None:
    user = _create_user(db_session, "settings-update@example.com")
    profile = _create_profile(
        db_session,
        user=user,
        full_name="Settings Update User",
        profile_visibility="public",
        profile_status=ProfileStatus.PUBLISHED,
        verification_status=VerificationStatus.APPROVED,
        completion_percentage=90,
    )

    response = client.patch(
        SETTINGS_ME_PATH,
        headers=_auth_headers(user.email),
        json={"profile_visibility": "private"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "email": "settings-update@example.com",
        "profile_exists": True,
        "profile_visibility": "private",
        "profile_status": "published",
        "verification_status": "approved",
        "completion_percentage": 90,
    }

    db_session.expire_all()
    refreshed_profile = db_session.get(Profile, profile.id)
    assert refreshed_profile is not None
    assert refreshed_profile.profile_visibility == "private"
