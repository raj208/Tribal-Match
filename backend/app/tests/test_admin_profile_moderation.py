import pytest
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.profiles.models import Profile
from app.modules.users.models import User
from app.shared.enums import ProfileStatus

ADMIN_HIDE_PATH = f"{settings.api_v1_prefix}/admin/profiles/{{profile_id}}/hide"
ADMIN_UNHIDE_PATH = f"{settings.api_v1_prefix}/admin/profiles/{{profile_id}}/unhide"
BROWSE_PATH = f"{settings.api_v1_prefix}/profiles"
PROFILE_DETAIL_PATH = f"{settings.api_v1_prefix}/profiles/{{profile_id}}"


def _auth_headers(email: str) -> dict[str, str]:
    return {"Authorization": f"Bearer test-token:{email}"}


@pytest.fixture
def admin_headers(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    monkeypatch.setattr(settings, "admin_email_allowlist", ["admin@example.com"])
    return _auth_headers("admin@example.com")


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
) -> Profile:
    profile = Profile(
        user_id=user.id,
        full_name=full_name,
        profile_status=profile_status,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def test_admin_hide_profile_requires_admin(
    client,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "admin_email_allowlist", ["admin@example.com"])
    target_user = _create_user(db_session, "target-hidden@example.com")
    target_profile = _create_profile(
        db_session,
        user=target_user,
        full_name="Target Hidden",
    )

    response = client.post(
        ADMIN_HIDE_PATH.format(profile_id=target_profile.id),
        headers=_auth_headers("normal@example.com"),
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Admin access required"}


def test_admin_unhide_profile_requires_admin(
    client,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "admin_email_allowlist", ["admin@example.com"])
    target_user = _create_user(db_session, "target-unhide@example.com")
    target_profile = _create_profile(
        db_session,
        user=target_user,
        full_name="Target Unhide",
        profile_status=ProfileStatus.HIDDEN,
    )

    response = client.post(
        ADMIN_UNHIDE_PATH.format(profile_id=target_profile.id),
        headers=_auth_headers("normal@example.com"),
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Admin access required"}


def test_admin_hide_profile_sets_hidden_and_removes_profile_from_browse_and_detail(
    client,
    db_session: Session,
    admin_headers: dict[str, str],
) -> None:
    _create_user(db_session, "admin@example.com")
    viewer = _create_user(db_session, "viewer@example.com")
    target_user = _create_user(db_session, "discoverable@example.com")
    target_profile = _create_profile(
        db_session,
        user=target_user,
        full_name="Discoverable Profile",
        profile_status=ProfileStatus.PUBLISHED,
    )

    browse_before = client.get(BROWSE_PATH, headers=_auth_headers(viewer.email))
    detail_before = client.get(
        PROFILE_DETAIL_PATH.format(profile_id=target_profile.id),
        headers=_auth_headers(viewer.email),
    )

    assert browse_before.status_code == 200
    assert browse_before.json()["total"] == 1
    assert browse_before.json()["items"][0]["id"] == str(target_profile.id)
    assert detail_before.status_code == 200

    hide_response = client.post(
        ADMIN_HIDE_PATH.format(profile_id=target_profile.id),
        headers=admin_headers,
    )

    assert hide_response.status_code == 200
    assert hide_response.json() == {
        "success": True,
        "profile_id": str(target_profile.id),
        "profile_status": "hidden",
    }

    db_session.expire_all()
    refreshed_profile = db_session.get(Profile, target_profile.id)
    assert refreshed_profile is not None
    assert refreshed_profile.profile_status == ProfileStatus.HIDDEN

    browse_after = client.get(BROWSE_PATH, headers=_auth_headers(viewer.email))
    detail_after = client.get(
        PROFILE_DETAIL_PATH.format(profile_id=target_profile.id),
        headers=_auth_headers(viewer.email),
    )

    assert browse_after.status_code == 200
    assert browse_after.json()["total"] == 0
    assert browse_after.json()["items"] == []
    assert detail_after.status_code == 404
    assert detail_after.json() == {"detail": "Profile not found"}


def test_admin_unhide_profile_restores_published_and_discovery_access(
    client,
    db_session: Session,
    admin_headers: dict[str, str],
) -> None:
    _create_user(db_session, "admin@example.com")
    viewer = _create_user(db_session, "viewer-unhide@example.com")
    target_user = _create_user(db_session, "hidden-target@example.com")
    target_profile = _create_profile(
        db_session,
        user=target_user,
        full_name="Hidden Profile",
        profile_status=ProfileStatus.HIDDEN,
    )

    browse_before = client.get(BROWSE_PATH, headers=_auth_headers(viewer.email))
    detail_before = client.get(
        PROFILE_DETAIL_PATH.format(profile_id=target_profile.id),
        headers=_auth_headers(viewer.email),
    )

    assert browse_before.status_code == 200
    assert browse_before.json()["total"] == 0
    assert browse_before.json()["items"] == []
    assert detail_before.status_code == 404

    unhide_response = client.post(
        ADMIN_UNHIDE_PATH.format(profile_id=target_profile.id),
        headers=admin_headers,
    )

    assert unhide_response.status_code == 200
    assert unhide_response.json() == {
        "success": True,
        "profile_id": str(target_profile.id),
        "profile_status": "published",
    }

    db_session.expire_all()
    refreshed_profile = db_session.get(Profile, target_profile.id)
    assert refreshed_profile is not None
    assert refreshed_profile.profile_status == ProfileStatus.PUBLISHED

    browse_after = client.get(BROWSE_PATH, headers=_auth_headers(viewer.email))
    detail_after = client.get(
        PROFILE_DETAIL_PATH.format(profile_id=target_profile.id),
        headers=_auth_headers(viewer.email),
    )

    assert browse_after.status_code == 200
    assert browse_after.json()["total"] == 1
    assert browse_after.json()["items"][0]["id"] == str(target_profile.id)
    assert detail_after.status_code == 200
    assert detail_after.json()["id"] == str(target_profile.id)


def test_admin_hide_profile_rejects_non_published_profile(
    client,
    db_session: Session,
    admin_headers: dict[str, str],
) -> None:
    _create_user(db_session, "admin@example.com")
    draft_user = _create_user(db_session, "draft-target@example.com")
    draft_profile = _create_profile(
        db_session,
        user=draft_user,
        full_name="Draft Profile",
        profile_status=ProfileStatus.DRAFT,
    )

    response = client.post(
        ADMIN_HIDE_PATH.format(profile_id=draft_profile.id),
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Only published profiles can be hidden"}


def test_admin_unhide_profile_rejects_non_hidden_profile(
    client,
    db_session: Session,
    admin_headers: dict[str, str],
) -> None:
    _create_user(db_session, "admin@example.com")
    deleted_user = _create_user(db_session, "deleted-target@example.com")
    deleted_profile = _create_profile(
        db_session,
        user=deleted_user,
        full_name="Deleted Profile",
        profile_status=ProfileStatus.DELETED,
    )

    response = client.post(
        ADMIN_UNHIDE_PATH.format(profile_id=deleted_profile.id),
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Only hidden profiles can be restored to published"}
