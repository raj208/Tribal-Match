from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.profiles.models import Profile
from app.modules.users.models import User
from app.shared.enums import ProfileStatus, VerificationStatus

SETTINGS_DELETE_PATH = f"{settings.api_v1_prefix}/settings/me"


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
    profile_status: ProfileStatus = ProfileStatus.PUBLISHED,
    verification_status: VerificationStatus = VerificationStatus.NOT_STARTED,
    completion_percentage: int = 0,
) -> Profile:
    profile = Profile(
        user_id=user.id,
        full_name=full_name,
        profile_status=profile_status,
        verification_status=verification_status,
        completion_percentage=completion_percentage,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def test_settings_delete_requires_auth(client) -> None:
    response = client.delete(SETTINGS_DELETE_PATH)

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_settings_delete_returns_404_when_profile_is_missing(client) -> None:
    response = client.delete(
        SETTINGS_DELETE_PATH,
        headers=_auth_headers("missing-delete@example.com"),
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Profile not found"}


def test_settings_delete_sets_profile_status_to_deleted(client, db_session: Session) -> None:
    user = _create_user(db_session, "delete@example.com")
    profile = _create_profile(
        db_session,
        user=user,
        full_name="Delete User",
        profile_status=ProfileStatus.PUBLISHED,
        verification_status=VerificationStatus.APPROVED,
        completion_percentage=90,
    )

    response = client.delete(
        SETTINGS_DELETE_PATH,
        headers=_auth_headers(user.email),
    )

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "profile_status": "deleted",
        "message": "Profile deleted successfully.",
    }

    db_session.expire_all()
    refreshed_profile = db_session.get(Profile, profile.id)
    assert refreshed_profile is not None
    assert refreshed_profile.profile_status == ProfileStatus.DELETED


def test_settings_delete_is_idempotent_for_already_deleted_profile(client, db_session: Session) -> None:
    user = _create_user(db_session, "already-deleted@example.com")
    _create_profile(
        db_session,
        user=user,
        full_name="Already Deleted User",
        profile_status=ProfileStatus.DELETED,
    )

    response = client.delete(
        SETTINGS_DELETE_PATH,
        headers=_auth_headers(user.email),
    )

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "profile_status": "deleted",
        "message": "Profile deleted successfully.",
    }
