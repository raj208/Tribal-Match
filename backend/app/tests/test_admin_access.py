from app.core.config import settings

ADMIN_HEALTH_PATH = f"{settings.api_v1_prefix}/moderation/admin/_health"


def _auth_headers(email: str) -> dict[str, str]:
    return {"Authorization": f"Bearer test-token:{email}"}


def test_moderation_admin_health_requires_authentication(client) -> None:
    response = client.get(ADMIN_HEALTH_PATH)

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_moderation_admin_health_rejects_authenticated_non_admin(client, monkeypatch) -> None:
    monkeypatch.setattr(settings, "admin_email_allowlist", ["admin@example.com"], ["rajendrafcb3087@gmail.com"])

    response = client.get(
        ADMIN_HEALTH_PATH,
        headers=_auth_headers("normal@example.com"),
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Admin access required"}


def test_moderation_admin_health_allows_configured_admin_email(client, monkeypatch) -> None:
    monkeypatch.setattr(settings, "admin_email_allowlist", [" Admin@Example.com "], ["rajendrafcb3087@gmail.com"])

    response = client.get(
        ADMIN_HEALTH_PATH,
        headers=_auth_headers("admin@example.com"),
    )

    assert response.status_code == 200
    assert response.json()["module"] == "moderation"
    assert response.json()["scope"] == "admin"
    assert response.json()["status"] == "ok"
