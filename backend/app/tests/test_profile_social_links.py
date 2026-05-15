import pytest
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.profiles.models import Profile
from app.modules.users.models import User

PROFILE_PATH = f"{settings.api_v1_prefix}/profile"
PROFILE_ME_PATH = f"{PROFILE_PATH}/me"


def _auth_headers(email: str) -> dict[str, str]:
    return {"Authorization": f"Bearer test-token:{email}"}


def _base_profile_payload(**overrides: object) -> dict[str, object]:
    payload = {
        "full_name": "Social User",
        "age": 30,
        "instagram_url": "https://instagram.com/social.user",
    }
    payload.update(overrides)
    return payload


def _create_user(db: Session, email: str) -> User:
    user = User(email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _create_profile(db: Session, *, user: User, full_name: str) -> Profile:
    profile = Profile(user_id=user.id, full_name=full_name)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def test_create_profile_accepts_and_normalizes_social_links(client) -> None:
    response = client.post(
        PROFILE_PATH,
        headers=_auth_headers("create-social@example.com"),
        json=_base_profile_payload(
            instagram_url="  https://www.instagram.com/social.user/  ",
            facebook_url="",
        ),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["instagram_url"] == "https://www.instagram.com/social.user/"
    assert body["facebook_url"] is None
    assert body["linkedin_url"] is None


def test_create_profile_requires_at_least_one_social_link(client) -> None:
    response = client.post(
        PROFILE_PATH,
        headers=_auth_headers("missing-social@example.com"),
        json=_base_profile_payload(
            instagram_url="",
            facebook_url=" ",
            linkedin_url=None,
        ),
    )

    assert response.status_code == 422
    assert "At least one social link is required" in str(response.json()["detail"])


@pytest.mark.parametrize(
    ("field_name", "url"),
    [
        ("instagram_url", "https://example.com/social.user"),
        ("instagram_url", "http://instagram.com/social.user"),
        ("instagram_url", "https://mobile.instagram.com/social.user"),
        ("facebook_url", "https://example.com/social.user"),
        ("facebook_url", "http://facebook.com/social.user"),
        ("facebook_url", "https://m.facebook.com/social.user"),
        ("linkedin_url", "https://example.com/in/social-user"),
        ("linkedin_url", "http://linkedin.com/in/social-user"),
        ("linkedin_url", "https://about.linkedin.com/in/social-user"),
    ],
)
def test_create_profile_rejects_invalid_social_link_domains(
    client,
    field_name: str,
    url: str,
) -> None:
    payload = _base_profile_payload()
    payload.update(
        {
            "instagram_url": None,
            "facebook_url": None,
            "linkedin_url": None,
            field_name: url,
        }
    )

    response = client.post(
        PROFILE_PATH,
        headers=_auth_headers(f"invalid-{field_name}-{len(url)}@example.com"),
        json=payload,
    )

    assert response.status_code == 422
    assert field_name in str(response.json()["detail"])


def test_update_profile_uses_existing_social_link_when_omitted(client) -> None:
    headers = _auth_headers("update-social@example.com")
    create_response = client.post(
        PROFILE_PATH,
        headers=headers,
        json=_base_profile_payload(instagram_url="https://instagram.com/current.user"),
    )
    assert create_response.status_code == 201

    update_response = client.patch(
        PROFILE_ME_PATH,
        headers=headers,
        json={"bio": "Updated profile bio"},
    )

    assert update_response.status_code == 200
    body = update_response.json()
    assert body["bio"] == "Updated profile bio"
    assert body["instagram_url"] == "https://instagram.com/current.user"


def test_legacy_profile_without_social_links_can_be_read_but_must_add_one_to_update(
    client,
    db_session: Session,
) -> None:
    user = _create_user(db_session, "legacy-social@example.com")
    _create_profile(db_session, user=user, full_name="Legacy Social")

    read_response = client.get(PROFILE_ME_PATH, headers=_auth_headers(user.email))

    assert read_response.status_code == 200
    assert read_response.json()["instagram_url"] is None
    assert read_response.json()["facebook_url"] is None
    assert read_response.json()["linkedin_url"] is None

    update_without_social_response = client.patch(
        PROFILE_ME_PATH,
        headers=_auth_headers(user.email),
        json={"bio": "Trying to edit legacy profile"},
    )

    assert update_without_social_response.status_code == 422
    assert update_without_social_response.json() == {"detail": "At least one social link is required"}

    update_with_social_response = client.patch(
        PROFILE_ME_PATH,
        headers=_auth_headers(user.email),
        json={"linkedin_url": "https://www.linkedin.com/in/legacy-social"},
    )

    assert update_with_social_response.status_code == 200
    assert update_with_social_response.json()["linkedin_url"] == "https://www.linkedin.com/in/legacy-social"
