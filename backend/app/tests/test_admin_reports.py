from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.moderation.models import Report
from app.modules.profiles.models import Profile
from app.modules.users.models import User
from app.shared.enums import ProfileStatus, ReportStatus

ADMIN_REPORTS_PATH = f"{settings.api_v1_prefix}/admin/reports"


def _auth_headers(email: str) -> dict[str, str]:
    return {"Authorization": f"Bearer test-token:{email}"}


@pytest.fixture
def admin_headers(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    monkeypatch.setattr(settings, "admin_email_allowlist", ["admin@example.com"], ["rajendrafcb3087@gmail.com"])
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


def _create_report(
    db: Session,
    *,
    reporter_user: User,
    reported_user: User,
    reported_profile: Profile,
    reason_code: str = "spam",
    notes: str | None = "Unsafe profile content",
    report_status: ReportStatus = ReportStatus.OPEN,
    created_at: datetime | None = None,
) -> Report:
    report = Report(
        reporter_user_id=reporter_user.id,
        reported_user_id=reported_user.id,
        reported_profile_id=reported_profile.id,
        reason_code=reason_code,
        notes=notes,
        status=report_status,
    )
    if created_at is not None:
        report.created_at = created_at
        report.updated_at = created_at

    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def _create_report_fixture(
    db: Session,
    *,
    reporter_email: str = "reporter@example.com",
    reported_email: str = "reported@example.com",
    reported_name: str = "Reported User",
    reason_code: str = "spam",
    notes: str | None = "Unsafe profile content",
    report_status: ReportStatus = ReportStatus.OPEN,
    created_at: datetime | None = None,
) -> tuple[Report, User, User, Profile]:
    reporter = _create_user(db, reporter_email)
    reported = _create_user(db, reported_email)
    profile = _create_profile(db, user=reported, full_name=reported_name)
    report = _create_report(
        db,
        reporter_user=reporter,
        reported_user=reported,
        reported_profile=profile,
        reason_code=reason_code,
        notes=notes,
        report_status=report_status,
        created_at=created_at,
    )
    return report, reporter, reported, profile


def test_admin_reports_list_requires_admin(client, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "admin_email_allowlist", ["admin@example.com"], ["rajendrafcb3087@gmail.com"])

    response = client.get(
        ADMIN_REPORTS_PATH,
        headers=_auth_headers("normal@example.com"),
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Admin access required"}


def test_admin_reports_list_returns_queue_items(client, db_session: Session, admin_headers: dict[str, str]) -> None:
    report, reporter, reported, profile = _create_report_fixture(
        db_session,
        reporter_email="queue-reporter@example.com",
        reported_email="queue-reported@example.com",
        reported_name="Queue Reported User",
        reason_code="harassment",
        notes="Repeated unwanted messages",
    )

    response = client.get(ADMIN_REPORTS_PATH, headers=admin_headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == str(report.id)
    assert body[0]["reason_code"] == "harassment"
    assert body[0]["status"] == "open"
    assert body[0]["created_at"]
    assert body[0]["reporter"] == {
        "id": str(reporter.id),
        "email": "queue-reporter@example.com",
    }
    assert body[0]["reported_user"] == {
        "id": str(reported.id),
        "email": "queue-reported@example.com",
    }
    assert body[0]["reported_profile"] == {
        "id": str(profile.id),
        "user_id": str(reported.id),
        "full_name": "Queue Reported User",
        "profile_status": "published",
    }


def test_admin_reports_list_filters_by_status(client, db_session: Session, admin_headers: dict[str, str]) -> None:
    open_report, _, _, _ = _create_report_fixture(
        db_session,
        reporter_email="open-reporter@example.com",
        reported_email="open-reported@example.com",
        report_status=ReportStatus.OPEN,
        created_at=datetime(2026, 4, 15, 9, 0, tzinfo=timezone.utc),
    )
    _create_report_fixture(
        db_session,
        reporter_email="resolved-reporter@example.com",
        reported_email="resolved-reported@example.com",
        report_status=ReportStatus.RESOLVED,
        created_at=datetime(2026, 4, 15, 10, 0, tzinfo=timezone.utc),
    )

    response = client.get(
        ADMIN_REPORTS_PATH,
        headers=admin_headers,
        params={"status": "open"},
    )

    assert response.status_code == 200
    body = response.json()
    assert [item["id"] for item in body] == [str(open_report.id)]


def test_admin_report_detail_returns_review_context(
    client,
    db_session: Session,
    admin_headers: dict[str, str],
) -> None:
    report, reporter, reported, profile = _create_report_fixture(
        db_session,
        reporter_email="detail-reporter@example.com",
        reported_email="detail-reported@example.com",
        reported_name="Detail Reported User",
        reason_code="fake_profile",
        notes="Profile appears to impersonate someone.",
    )

    response = client.get(f"{ADMIN_REPORTS_PATH}/{report.id}", headers=admin_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(report.id)
    assert body["reason_code"] == "fake_profile"
    assert body["notes"] == "Profile appears to impersonate someone."
    assert body["created_at"]
    assert body["updated_at"]
    assert body["reporter"] == {
        "id": str(reporter.id),
        "email": "detail-reporter@example.com",
    }
    assert body["reported_user"] == {
        "id": str(reported.id),
        "email": "detail-reported@example.com",
    }
    assert body["reported_profile"]["id"] == str(profile.id)
    assert body["reported_profile"]["full_name"] == "Detail Reported User"


def test_admin_report_detail_returns_404_for_missing_report(client, admin_headers: dict[str, str]) -> None:
    response = client.get(f"{ADMIN_REPORTS_PATH}/{uuid4()}", headers=admin_headers)

    assert response.status_code == 404
    assert response.json() == {"detail": "Report not found"}


def test_admin_report_patch_updates_status(client, db_session: Session, admin_headers: dict[str, str]) -> None:
    report, _, _, _ = _create_report_fixture(db_session)

    response = client.patch(
        f"{ADMIN_REPORTS_PATH}/{report.id}",
        headers=admin_headers,
        json={"status": "reviewed"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "reviewed"

    db_session.expire_all()
    refreshed_report = db_session.get(Report, report.id)
    assert refreshed_report is not None
    assert refreshed_report.status == ReportStatus.REVIEWED


def test_admin_report_patch_rejects_backward_transition(
    client,
    db_session: Session,
    admin_headers: dict[str, str],
) -> None:
    report, _, _, _ = _create_report_fixture(db_session, report_status=ReportStatus.RESOLVED)

    response = client.patch(
        f"{ADMIN_REPORTS_PATH}/{report.id}",
        headers=admin_headers,
        json={"status": "reviewed"},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Invalid report status transition"}

    db_session.expire_all()
    refreshed_report = db_session.get(Report, report.id)
    assert refreshed_report is not None
    assert refreshed_report.status == ReportStatus.RESOLVED
