from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.media.models import IntroVideo, ProfilePhoto
from app.modules.media.providers import StoredMediaObject, build_s3_locator
from app.modules.profiles.models import Profile
from app.modules.users.models import User
from app.shared.enums import ProfileStatus, VerificationStatus

MEDIA_PHOTOS_BASE_PATH = f"{settings.api_v1_prefix}/media/photos"
VERIFICATION_BASE_PATH = f"{settings.api_v1_prefix}/verification"
ADMIN_VERIFICATIONS_PATH = f"{settings.api_v1_prefix}/admin/verifications"


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


def _create_photo(
    db: Session,
    *,
    user: User,
    profile: Profile,
    photo_url: str,
    sort_order: int = 0,
    is_primary: bool = True,
) -> ProfilePhoto:
    photo = ProfilePhoto(
        user_id=user.id,
        profile_id=profile.id,
        photo_url=photo_url,
        sort_order=sort_order,
        is_primary=is_primary,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


class FakeS3Provider:
    bucket = "test-private-media"
    photos_prefix = "photos"
    videos_prefix = "videos"
    upload_expires_in = 900

    def create_photo_upload_intent(self, *, user_id, filename: str, content_type: str) -> dict[str, str | int]:
        del filename, content_type
        object_key = f"{self.photos_prefix}/{user_id}/{uuid4().hex}.jpg"
        return {
            "provider": "s3",
            "object_key": object_key,
            "upload_url": f"https://uploads.example/{object_key}",
            "expires_in": self.upload_expires_in,
        }

    def create_video_upload_intent(self, *, user_id, filename: str, content_type: str) -> dict[str, str | int]:
        del filename, content_type
        object_key = f"{self.videos_prefix}/{user_id}/{uuid4().hex}.mp4"
        return {
            "provider": "s3",
            "object_key": object_key,
            "upload_url": f"https://uploads.example/{object_key}",
            "expires_in": self.upload_expires_in,
        }

    def inspect_uploaded_object(self, *, object_key: str) -> StoredMediaObject:
        if object_key.endswith((".jpg", ".jpeg")):
            content_type = "image/jpeg"
            size_bytes = 2048
        else:
            content_type = "video/mp4"
            size_bytes = 8192

        return StoredMediaObject(
            provider="s3",
            stored_url=build_s3_locator(self.bucket, object_key),
            bucket=self.bucket,
            object_key=object_key,
            content_type=content_type,
            size_bytes=size_bytes,
        )

    def resolve_url(self, *, stored_url: str | None, object_key: str | None, bucket: str | None = None) -> str:
        del bucket
        resolved_key = object_key
        if resolved_key is None and stored_url is not None:
            resolved_key = stored_url.removeprefix(f"s3://{self.bucket}/")
        assert resolved_key is not None
        return f"https://signed.example/{resolved_key}"

    def delete_object(self, *, object_key: str | None, stored_url: str | None = None, bucket: str | None = None) -> None:
        del object_key, stored_url, bucket


@pytest.fixture
def fake_s3_provider(monkeypatch: pytest.MonkeyPatch) -> FakeS3Provider:
    provider = FakeS3Provider()
    monkeypatch.setattr("app.modules.media.providers.get_s3_provider", lambda: provider)
    monkeypatch.setattr("app.modules.media.service.get_s3_provider", lambda: provider)
    monkeypatch.setattr("app.modules.verification.service.get_s3_provider", lambda: provider)
    return provider


def test_media_photos_me_keeps_existing_local_photo_url(client, db_session: Session) -> None:
    user = _create_user(db_session, "legacy-photo@example.com")
    profile = _create_profile(db_session, user=user, full_name="Legacy Photo User")
    legacy_url = "http://localhost:8000/uploads/photos/legacy.jpg"
    _create_photo(db_session, user=user, profile=profile, photo_url=legacy_url)

    response = client.get(f"{MEDIA_PHOTOS_BASE_PATH}/me", headers=_auth_headers(user.email))

    assert response.status_code == 200
    assert response.json()[0]["photo_url"] == legacy_url


def test_photo_upload_intent_and_confirm_store_s3_metadata(
    client,
    db_session: Session,
    fake_s3_provider: FakeS3Provider,
) -> None:
    user = _create_user(db_session, "s3-photo@example.com")
    profile = _create_profile(db_session, user=user, full_name="S3 Photo User")

    intent_response = client.post(
        f"{MEDIA_PHOTOS_BASE_PATH}/upload-intent",
        headers=_auth_headers(user.email),
        json={"filename": "avatar.jpg", "content_type": "image/jpeg"},
    )

    assert intent_response.status_code == 200
    intent_body = intent_response.json()
    assert intent_body["provider"] == "s3"
    assert intent_body["object_key"].startswith(f"{fake_s3_provider.photos_prefix}/{user.id}/")
    assert intent_body["expires_in"] == 900

    confirm_response = client.post(
        f"{MEDIA_PHOTOS_BASE_PATH}/confirm",
        headers=_auth_headers(user.email),
        json={
            "object_key": intent_body["object_key"],
            "content_type": "image/jpeg",
            "sort_order": 2,
            "make_primary": True,
        },
    )

    assert confirm_response.status_code == 201
    confirm_body = confirm_response.json()
    assert confirm_body["profile_id"] == str(profile.id)
    assert confirm_body["is_primary"] is True
    assert confirm_body["photo_url"] == f"https://signed.example/{intent_body['object_key']}"

    saved_photo = db_session.scalar(select(ProfilePhoto).where(ProfilePhoto.profile_id == profile.id))
    assert saved_photo is not None
    assert saved_photo.provider == "s3"
    assert saved_photo.bucket == fake_s3_provider.bucket
    assert saved_photo.object_key == intent_body["object_key"]
    assert saved_photo.content_type == "image/jpeg"
    assert saved_photo.size_bytes == 2048
    assert saved_photo.photo_url == build_s3_locator(fake_s3_provider.bucket, intent_body["object_key"])

    list_response = client.get(f"{MEDIA_PHOTOS_BASE_PATH}/me", headers=_auth_headers(user.email))
    assert list_response.status_code == 200
    assert list_response.json()[0]["photo_url"] == f"https://signed.example/{intent_body['object_key']}"


def test_verification_confirm_and_admin_detail_resolve_s3_video_url(
    client,
    db_session: Session,
    fake_s3_provider: FakeS3Provider,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "admin_email_allowlist", ["admin@example.com"])

    admin_user = _create_user(db_session, "admin@example.com")
    del admin_user

    user = _create_user(db_session, "s3-video@example.com")
    profile = _create_profile(db_session, user=user, full_name="S3 Video User")

    intent_response = client.post(
        f"{VERIFICATION_BASE_PATH}/video/upload-intent",
        headers=_auth_headers(user.email),
        json={"filename": "intro.mp4", "content_type": "video/mp4"},
    )

    assert intent_response.status_code == 200
    intent_body = intent_response.json()
    assert intent_body["provider"] == "s3"
    assert intent_body["object_key"].startswith(f"{fake_s3_provider.videos_prefix}/{user.id}/")

    confirm_response = client.post(
        f"{VERIFICATION_BASE_PATH}/video/confirm",
        headers=_auth_headers(user.email),
        json={
            "object_key": intent_body["object_key"],
            "content_type": "video/mp4",
            "duration_seconds": 24,
        },
    )

    assert confirm_response.status_code == 200
    confirm_body = confirm_response.json()
    assert confirm_body["profile_verification_status"] == "uploaded"
    assert confirm_body["intro_video"]["video_url"] == f"https://signed.example/{intent_body['object_key']}"
    assert confirm_body["intro_video"]["duration_seconds"] == 24

    saved_video = db_session.scalar(select(IntroVideo).where(IntroVideo.profile_id == profile.id))
    assert saved_video is not None
    assert saved_video.provider == "s3"
    assert saved_video.bucket == fake_s3_provider.bucket
    assert saved_video.object_key == intent_body["object_key"]
    assert saved_video.content_type == "video/mp4"
    assert saved_video.size_bytes == 8192
    assert saved_video.video_url == build_s3_locator(fake_s3_provider.bucket, intent_body["object_key"])

    verification_response = client.get(f"{VERIFICATION_BASE_PATH}/me", headers=_auth_headers(user.email))
    assert verification_response.status_code == 200
    assert verification_response.json()["intro_video"]["video_url"] == f"https://signed.example/{intent_body['object_key']}"

    admin_detail_response = client.get(
        f"{ADMIN_VERIFICATIONS_PATH}/{saved_video.id}",
        headers=_auth_headers("admin@example.com"),
    )
    assert admin_detail_response.status_code == 200
    assert admin_detail_response.json()["video_url"] == f"https://signed.example/{intent_body['object_key']}"
