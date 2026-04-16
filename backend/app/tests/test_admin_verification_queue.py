from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.media.models import IntroVideo
from app.modules.profiles.models import Profile
from app.modules.users.models import User
from app.shared.enums import ProfileStatus, VerificationStatus

ADMIN_VERIFICATIONS_PATH = f"{settings.api_v1_prefix}/admin/verifications"


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
    verification_status: VerificationStatus = VerificationStatus.UPLOADED,
) -> Profile:
    profile = Profile(
        user_id=user.id,
        full_name=full_name,
        profile_status=profile_status,
        verification_status=verification_status,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def _create_intro_video(
    db: Session,
    *,
    user: User,
    profile: Profile,
    video_url: str = "https://example.com/intro.mp4",
    duration_seconds: int = 24,
    verification_status: VerificationStatus = VerificationStatus.UPLOADED,
    moderation_notes: str | None = None,
    created_at: datetime | None = None,
) -> IntroVideo:
    intro_video = IntroVideo(
        user_id=user.id,
        profile_id=profile.id,
        video_url=video_url,
        duration_seconds=duration_seconds,
        upload_status="uploaded",
        verification_status=verification_status,
        moderation_notes=moderation_notes,
    )
    if created_at is not None:
        intro_video.created_at = created_at
        intro_video.updated_at = created_at

    db.add(intro_video)
    db.commit()
    db.refresh(intro_video)
    return intro_video


def test_admin_verification_queue_requires_admin(client, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "admin_email_allowlist", ["admin@example.com"])

    response = client.get(
        ADMIN_VERIFICATIONS_PATH,
        headers=_auth_headers("normal@example.com"),
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Admin access required"}


def test_admin_verification_detail_requires_admin(
    client,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "admin_email_allowlist", ["admin@example.com"])
    target_user = _create_user(db_session, "detail-blocked@example.com")
    target_profile = _create_profile(
        db_session,
        user=target_user,
        full_name="Blocked Detail User",
        verification_status=VerificationStatus.UPLOADED,
    )
    intro_video = _create_intro_video(
        db_session,
        user=target_user,
        profile=target_profile,
        verification_status=VerificationStatus.UPLOADED,
    )

    response = client.get(
        f"{ADMIN_VERIFICATIONS_PATH}/{intro_video.id}",
        headers=_auth_headers("normal@example.com"),
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Admin access required"}


def test_admin_verification_patch_requires_admin(
    client,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "admin_email_allowlist", ["admin@example.com"])
    target_user = _create_user(db_session, "patch-blocked@example.com")
    target_profile = _create_profile(
        db_session,
        user=target_user,
        full_name="Blocked Patch User",
        verification_status=VerificationStatus.UNDER_REVIEW,
    )
    intro_video = _create_intro_video(
        db_session,
        user=target_user,
        profile=target_profile,
        verification_status=VerificationStatus.UNDER_REVIEW,
    )

    response = client.patch(
        f"{ADMIN_VERIFICATIONS_PATH}/{intro_video.id}",
        headers=_auth_headers("normal@example.com"),
        json={"status": "approved"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Admin access required"}


def test_admin_verification_queue_lists_uploaded_and_under_review_items_only(
    client,
    db_session: Session,
    admin_headers: dict[str, str],
) -> None:
    _create_user(db_session, "admin@example.com")

    uploaded_user = _create_user(db_session, "uploaded@example.com")
    uploaded_profile = _create_profile(
        db_session,
        user=uploaded_user,
        full_name="Uploaded User",
        verification_status=VerificationStatus.UPLOADED,
    )
    uploaded_video = _create_intro_video(
        db_session,
        user=uploaded_user,
        profile=uploaded_profile,
        verification_status=VerificationStatus.UPLOADED,
        created_at=datetime(2026, 4, 16, 9, 0, tzinfo=timezone.utc),
    )

    review_user = _create_user(db_session, "review@example.com")
    review_profile = _create_profile(
        db_session,
        user=review_user,
        full_name="Review User",
        verification_status=VerificationStatus.UNDER_REVIEW,
    )
    review_video = _create_intro_video(
        db_session,
        user=review_user,
        profile=review_profile,
        verification_status=VerificationStatus.UNDER_REVIEW,
        video_url="https://example.com/review.mp4",
        created_at=datetime(2026, 4, 16, 10, 0, tzinfo=timezone.utc),
    )

    approved_user = _create_user(db_session, "approved@example.com")
    approved_profile = _create_profile(
        db_session,
        user=approved_user,
        full_name="Approved User",
        verification_status=VerificationStatus.APPROVED,
    )
    _create_intro_video(
        db_session,
        user=approved_user,
        profile=approved_profile,
        verification_status=VerificationStatus.APPROVED,
    )

    response = client.get(ADMIN_VERIFICATIONS_PATH, headers=admin_headers)

    assert response.status_code == 200
    body = response.json()
    assert [item["id"] for item in body] == [str(review_video.id), str(uploaded_video.id)]
    assert body[0]["verification_status"] == "under_review"
    assert body[0]["video_url"] == "https://example.com/review.mp4"
    assert body[0]["profile"]["full_name"] == "Review User"
    assert body[0]["user"]["email"] == "review@example.com"


def test_admin_verification_detail_returns_review_context(
    client,
    db_session: Session,
    admin_headers: dict[str, str],
) -> None:
    _create_user(db_session, "admin@example.com")
    target_user = _create_user(db_session, "detail-video@example.com")
    target_profile = _create_profile(
        db_session,
        user=target_user,
        full_name="Detail Video User",
        verification_status=VerificationStatus.UNDER_REVIEW,
    )
    intro_video = _create_intro_video(
        db_session,
        user=target_user,
        profile=target_profile,
        verification_status=VerificationStatus.UNDER_REVIEW,
        moderation_notes="Previously flagged for recheck",
    )

    response = client.get(f"{ADMIN_VERIFICATIONS_PATH}/{intro_video.id}", headers=admin_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(intro_video.id)
    assert body["verification_status"] == "under_review"
    assert body["video_url"] == "https://example.com/intro.mp4"
    assert body["upload_status"] == "uploaded"
    assert body["moderation_notes"] == "Previously flagged for recheck"
    assert body["profile"]["id"] == str(target_profile.id)
    assert body["profile"]["verification_status"] == "under_review"
    assert body["user"]["email"] == "detail-video@example.com"


def test_admin_verification_detail_returns_404_when_item_missing(
    client,
    admin_headers: dict[str, str],
) -> None:
    response = client.get(f"{ADMIN_VERIFICATIONS_PATH}/{uuid4()}", headers=admin_headers)

    assert response.status_code == 404
    assert response.json() == {"detail": "Verification item not found"}


def test_admin_verification_patch_approves_video_and_profile(
    client,
    db_session: Session,
    admin_headers: dict[str, str],
) -> None:
    _create_user(db_session, "admin@example.com")
    target_user = _create_user(db_session, "approve-video@example.com")
    target_profile = _create_profile(
        db_session,
        user=target_user,
        full_name="Approve Video User",
        verification_status=VerificationStatus.UPLOADED,
    )
    intro_video = _create_intro_video(
        db_session,
        user=target_user,
        profile=target_profile,
        verification_status=VerificationStatus.UPLOADED,
        moderation_notes="Old note",
    )

    response = client.patch(
        f"{ADMIN_VERIFICATIONS_PATH}/{intro_video.id}",
        headers=admin_headers,
        json={"status": "approved"},
    )

    assert response.status_code == 200
    assert response.json()["verification_status"] == "approved"
    assert response.json()["profile"]["verification_status"] == "approved"
    assert response.json()["moderation_notes"] is None

    db_session.expire_all()
    refreshed_video = db_session.get(IntroVideo, intro_video.id)
    refreshed_profile = db_session.get(Profile, target_profile.id)
    assert refreshed_video is not None
    assert refreshed_profile is not None
    assert refreshed_video.verification_status == VerificationStatus.APPROVED
    assert refreshed_profile.verification_status == VerificationStatus.APPROVED
    assert refreshed_video.moderation_notes is None


def test_admin_verification_patch_rejects_video_and_stores_reason(
    client,
    db_session: Session,
    admin_headers: dict[str, str],
) -> None:
    _create_user(db_session, "admin@example.com")
    target_user = _create_user(db_session, "reject-video@example.com")
    target_profile = _create_profile(
        db_session,
        user=target_user,
        full_name="Reject Video User",
        verification_status=VerificationStatus.UNDER_REVIEW,
    )
    intro_video = _create_intro_video(
        db_session,
        user=target_user,
        profile=target_profile,
        verification_status=VerificationStatus.UNDER_REVIEW,
    )

    response = client.patch(
        f"{ADMIN_VERIFICATIONS_PATH}/{intro_video.id}",
        headers=admin_headers,
        json={"status": "rejected", "reason": "Video too short"},
    )

    assert response.status_code == 200
    assert response.json()["verification_status"] == "rejected"
    assert response.json()["profile"]["verification_status"] == "rejected"
    assert response.json()["moderation_notes"] == "Video too short"

    db_session.expire_all()
    refreshed_video = db_session.get(IntroVideo, intro_video.id)
    refreshed_profile = db_session.get(Profile, target_profile.id)
    assert refreshed_video is not None
    assert refreshed_profile is not None
    assert refreshed_video.verification_status == VerificationStatus.REJECTED
    assert refreshed_profile.verification_status == VerificationStatus.REJECTED
    assert refreshed_video.moderation_notes == "Video too short"


def test_admin_verification_patch_rejects_non_decision_status(
    client,
    db_session: Session,
    admin_headers: dict[str, str],
) -> None:
    _create_user(db_session, "admin@example.com")
    target_user = _create_user(db_session, "invalid-status@example.com")
    target_profile = _create_profile(
        db_session,
        user=target_user,
        full_name="Invalid Status User",
        verification_status=VerificationStatus.UPLOADED,
    )
    intro_video = _create_intro_video(
        db_session,
        user=target_user,
        profile=target_profile,
        verification_status=VerificationStatus.UPLOADED,
    )

    response = client.patch(
        f"{ADMIN_VERIFICATIONS_PATH}/{intro_video.id}",
        headers=admin_headers,
        json={"status": "under_review"},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Verification review status must be approved or rejected"
    }


def test_admin_verification_patch_rejects_already_reviewed_item(
    client,
    db_session: Session,
    admin_headers: dict[str, str],
) -> None:
    _create_user(db_session, "admin@example.com")
    target_user = _create_user(db_session, "already-approved@example.com")
    target_profile = _create_profile(
        db_session,
        user=target_user,
        full_name="Already Approved User",
        verification_status=VerificationStatus.APPROVED,
    )
    intro_video = _create_intro_video(
        db_session,
        user=target_user,
        profile=target_profile,
        verification_status=VerificationStatus.APPROVED,
    )

    response = client.patch(
        f"{ADMIN_VERIFICATIONS_PATH}/{intro_video.id}",
        headers=admin_headers,
        json={"status": "rejected", "reason": "Retry review"},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Verification item is not pending review"}
