import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

try:
    import boto3
    from botocore.config import Config as BotoConfig
    from botocore.exceptions import (
        BotoCoreError,
        ClientError,
        NoCredentialsError,
        PartialCredentialsError,
    )
    S3_CREDENTIAL_ERROR_TYPES = (NoCredentialsError, PartialCredentialsError)
    S3_CLIENT_ERROR_TYPES = (ClientError,)
    S3_CORE_ERROR_TYPES = (BotoCoreError,)
except ImportError:  # pragma: no cover - exercised only when dependency is missing at runtime
    boto3 = None
    BotoConfig = None
    S3_CREDENTIAL_ERROR_TYPES = ()
    S3_CLIENT_ERROR_TYPES = ()
    S3_CORE_ERROR_TYPES = ()


MEDIA_PROVIDER_LOCAL = "local"
MEDIA_PROVIDER_S3 = "s3"

PHOTO_CONTENT_TYPES_BY_EXTENSION = {
    ".jpg": {"image/jpeg"},
    ".jpeg": {"image/jpeg"},
    ".png": {"image/png"},
    ".webp": {"image/webp"},
}
VIDEO_CONTENT_TYPES_BY_EXTENSION = {
    ".mp4": {"video/mp4"},
    ".mov": {"video/quicktime"},
    ".webm": {"video/webm"},
    ".m4v": {"video/x-m4v", "video/mp4"},
}
CONTENT_TYPE_ALIASES = {
    "image/jpg": "image/jpeg",
    "video/m4v": "video/x-m4v",
}
S3_LOCATOR_PREFIX = "s3://"


@dataclass(frozen=True)
class StoredMediaObject:
    provider: str
    stored_url: str
    bucket: str | None
    object_key: str | None
    content_type: str | None
    size_bytes: int | None


def _get_extension(filename: str | None) -> str:
    if not filename:
        return ""
    return Path(filename).suffix.lower()


def _normalize_content_type(content_type: str | None) -> str | None:
    if content_type is None:
        return None

    normalized = content_type.split(";", maxsplit=1)[0].strip().lower()
    if not normalized:
        return None
    return CONTENT_TYPE_ALIASES.get(normalized, normalized)


def _validate_upload_request(
    *,
    filename: str | None,
    content_type: str | None,
    allowed_types_by_extension: dict[str, set[str]],
    unsupported_detail: str,
) -> tuple[str, str]:
    extension = _get_extension(filename)
    normalized_content_type = _normalize_content_type(content_type)

    if extension not in allowed_types_by_extension:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=unsupported_detail,
        )

    allowed_types = allowed_types_by_extension[extension]
    if normalized_content_type is None:
        normalized_content_type = sorted(allowed_types)[0]

    if normalized_content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=unsupported_detail,
        )

    return extension, normalized_content_type


def validate_photo_upload_request(filename: str | None, content_type: str | None) -> tuple[str, str]:
    return _validate_upload_request(
        filename=filename,
        content_type=content_type,
        allowed_types_by_extension=PHOTO_CONTENT_TYPES_BY_EXTENSION,
        unsupported_detail="Only jpg, jpeg, png, and webp images are allowed",
    )


def validate_video_upload_request(filename: str | None, content_type: str | None) -> tuple[str, str]:
    return _validate_upload_request(
        filename=filename,
        content_type=content_type,
        allowed_types_by_extension=VIDEO_CONTENT_TYPES_BY_EXTENSION,
        unsupported_detail="Only mp4, mov, webm, and m4v videos are allowed",
    )


def _clean_prefix(prefix: str, *, default_value: str) -> str:
    cleaned = prefix.strip().strip("/")
    return cleaned or default_value


def build_s3_locator(bucket: str, object_key: str) -> str:
    return f"{S3_LOCATOR_PREFIX}{bucket}/{object_key.lstrip('/')}"


def parse_s3_locator(value: str | None) -> tuple[str, str] | None:
    if not value or not value.startswith(S3_LOCATOR_PREFIX):
        return None

    remainder = value.removeprefix(S3_LOCATOR_PREFIX)
    bucket, separator, object_key = remainder.partition("/")
    if not separator or not bucket or not object_key:
        return None

    return bucket, object_key


class LocalMediaStorageProvider:
    def __init__(self) -> None:
        self.base_dir = Path(settings.media_upload_dir)
        self.photos_dir = self.base_dir / "photos"
        self.videos_dir = self.base_dir / "videos"

        self.photos_dir.mkdir(parents=True, exist_ok=True)
        self.videos_dir.mkdir(parents=True, exist_ok=True)

    def _build_public_url(self, object_key: str) -> str:
        return f"{settings.media_public_base_url.rstrip('/')}/{object_key.lstrip('/')}"

    def save_photo(self, file: UploadFile) -> StoredMediaObject:
        extension, content_type = validate_photo_upload_request(file.filename, file.content_type)
        filename = f"{uuid.uuid4().hex}{extension}"
        object_key = f"photos/{filename}"
        target = self.photos_dir / filename

        with target.open("wb") as out:
            shutil.copyfileobj(file.file, out)

        return StoredMediaObject(
            provider=MEDIA_PROVIDER_LOCAL,
            stored_url=self._build_public_url(object_key),
            bucket=None,
            object_key=object_key,
            content_type=content_type,
            size_bytes=target.stat().st_size,
        )

    def save_video(self, file: UploadFile) -> StoredMediaObject:
        extension, content_type = validate_video_upload_request(file.filename, file.content_type)
        filename = f"{uuid.uuid4().hex}{extension}"
        object_key = f"videos/{filename}"
        target = self.videos_dir / filename

        with target.open("wb") as out:
            shutil.copyfileobj(file.file, out)

        return StoredMediaObject(
            provider=MEDIA_PROVIDER_LOCAL,
            stored_url=self._build_public_url(object_key),
            bucket=None,
            object_key=object_key,
            content_type=content_type,
            size_bytes=target.stat().st_size,
        )

    def resolve_url(
        self,
        *,
        stored_url: str | None,
        object_key: str | None,
        bucket: str | None = None,
    ) -> str | None:
        del bucket
        if stored_url and not stored_url.startswith(S3_LOCATOR_PREFIX):
            return stored_url
        if object_key:
            return self._build_public_url(object_key)
        return stored_url

    def delete_object(self, *, object_key: str | None, stored_url: str | None = None, bucket: str | None = None) -> None:
        del stored_url, bucket
        if not object_key:
            return

        relative_path = Path(*[segment for segment in object_key.split("/") if segment])
        target = self.base_dir / relative_path
        if target.exists() and target.is_file():
            target.unlink()


class S3MediaStorageProvider:
    def __init__(self) -> None:
        self.region = settings.aws_region.strip()
        self.bucket = settings.aws_s3_bucket.strip()
        self.photos_prefix = _clean_prefix(settings.aws_s3_photos_prefix, default_value="photos")
        self.videos_prefix = _clean_prefix(settings.aws_s3_videos_prefix, default_value="videos")
        self.upload_expires_in = settings.aws_s3_upload_url_expires_seconds
        self.view_expires_in = settings.aws_s3_view_url_expires_seconds

    def _require_configuration(self) -> None:
        if boto3 is None or BotoConfig is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="S3 support is unavailable because boto3 is not installed",
            )

        required_values = {
            "AWS_REGION": self.region,
            "AWS_S3_BUCKET": self.bucket,
        }
        missing = [name for name, value in required_values.items() if not value]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"S3 media storage is not configured ({', '.join(missing)} missing)",
            )

        access_key_id = settings.aws_access_key_id.strip()
        secret_access_key = settings.aws_secret_access_key.strip()
        if bool(access_key_id) != bool(secret_access_key):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="S3 media storage is not configured (set both AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY)",
            )

    @property
    def client(self):
        self._require_configuration()
        client_kwargs = {
            "region_name": self.region,
            "endpoint_url": f"https://s3.{self.region}.amazonaws.com",
            "config": BotoConfig(
                signature_version="s3v4",
                s3={"addressing_style": "virtual"},
            ),
        }
        access_key_id = settings.aws_access_key_id.strip()
        secret_access_key = settings.aws_secret_access_key.strip()
        session_token = settings.aws_session_token.strip()
        if access_key_id and secret_access_key:
            client_kwargs["aws_access_key_id"] = access_key_id
            client_kwargs["aws_secret_access_key"] = secret_access_key
            if session_token:
                client_kwargs["aws_session_token"] = session_token

        return boto3.client("s3", **client_kwargs)

    def _raise_credentials_error(self, exc: Exception) -> None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "S3 media storage is not configured "
                "(set AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY or attach an IAM role)"
            ),
        ) from exc

    def _build_object_key(self, *, prefix: str, user_id: Any, extension: str) -> str:
        return f"{prefix}/{user_id}/{uuid.uuid4().hex}{extension}"

    def create_photo_upload_intent(self, *, user_id: Any, filename: str, content_type: str) -> dict[str, Any]:
        extension, normalized_content_type = validate_photo_upload_request(filename, content_type)
        object_key = self._build_object_key(prefix=self.photos_prefix, user_id=user_id, extension=extension)
        return self._create_upload_intent(object_key=object_key, content_type=normalized_content_type)

    def create_video_upload_intent(self, *, user_id: Any, filename: str, content_type: str) -> dict[str, Any]:
        extension, normalized_content_type = validate_video_upload_request(filename, content_type)
        object_key = self._build_object_key(prefix=self.videos_prefix, user_id=user_id, extension=extension)
        return self._create_upload_intent(object_key=object_key, content_type=normalized_content_type)

    def _create_upload_intent(self, *, object_key: str, content_type: str) -> dict[str, Any]:
        try:
            upload_url = self.client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": self.bucket,
                    "Key": object_key,
                    "ContentType": content_type,
                },
                ExpiresIn=self.upload_expires_in,
                HttpMethod="PUT",
            )
        except S3_CREDENTIAL_ERROR_TYPES as exc:
            self._raise_credentials_error(exc)
        except (*S3_CLIENT_ERROR_TYPES, *S3_CORE_ERROR_TYPES) as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unable to create an S3 upload URL",
            ) from exc

        return {
            "provider": MEDIA_PROVIDER_S3,
            "object_key": object_key,
            "upload_url": upload_url,
            "expires_in": self.upload_expires_in,
        }

    def inspect_uploaded_object(self, *, object_key: str) -> StoredMediaObject:
        try:
            response = self.client.head_object(Bucket=self.bucket, Key=object_key)
        except S3_CREDENTIAL_ERROR_TYPES as exc:
            self._raise_credentials_error(exc)
        except S3_CLIENT_ERROR_TYPES as exc:
            error_code = str(exc.response.get("Error", {}).get("Code", "")).strip()
            if error_code in {"404", "NoSuchKey", "NotFound"}:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Uploaded media object was not found in S3",
                ) from exc

            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unable to verify the uploaded S3 object",
            ) from exc
        except S3_CORE_ERROR_TYPES as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unable to verify the uploaded S3 object",
            ) from exc

        size_bytes = int(response.get("ContentLength") or 0)
        if size_bytes <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded media object is empty",
            )

        normalized_content_type = _normalize_content_type(response.get("ContentType"))
        return StoredMediaObject(
            provider=MEDIA_PROVIDER_S3,
            stored_url=build_s3_locator(self.bucket, object_key),
            bucket=self.bucket,
            object_key=object_key,
            content_type=normalized_content_type,
            size_bytes=size_bytes,
        )

    def resolve_url(
        self,
        *,
        stored_url: str | None,
        object_key: str | None,
        bucket: str | None = None,
    ) -> str | None:
        resolved_bucket = bucket or self.bucket
        resolved_key = object_key
        if not resolved_key:
            parsed_locator = parse_s3_locator(stored_url)
            if parsed_locator:
                resolved_bucket, resolved_key = parsed_locator

        if not resolved_bucket or not resolved_key:
            return stored_url

        try:
            return self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": resolved_bucket, "Key": resolved_key},
                ExpiresIn=self.view_expires_in,
            )
        except S3_CREDENTIAL_ERROR_TYPES as exc:
            self._raise_credentials_error(exc)
        except (*S3_CLIENT_ERROR_TYPES, *S3_CORE_ERROR_TYPES) as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unable to create an S3 media view URL",
            ) from exc

    def delete_object(self, *, object_key: str | None, stored_url: str | None = None, bucket: str | None = None) -> None:
        resolved_bucket = bucket or self.bucket
        resolved_key = object_key
        if not resolved_key:
            parsed_locator = parse_s3_locator(stored_url)
            if parsed_locator:
                resolved_bucket, resolved_key = parsed_locator

        if not resolved_bucket or not resolved_key:
            return

        try:
            self.client.delete_object(Bucket=resolved_bucket, Key=resolved_key)
        except (*S3_CLIENT_ERROR_TYPES, *S3_CORE_ERROR_TYPES):
            return


def get_local_provider() -> LocalMediaStorageProvider:
    return LocalMediaStorageProvider()


def get_s3_provider() -> S3MediaStorageProvider:
    return S3MediaStorageProvider()


def resolve_media_url(
    *,
    provider: str | None,
    stored_url: str | None,
    object_key: str | None,
    bucket: str | None,
) -> str | None:
    provider_name = (provider or MEDIA_PROVIDER_LOCAL).strip().lower()
    if provider_name == MEDIA_PROVIDER_S3:
        return get_s3_provider().resolve_url(stored_url=stored_url, object_key=object_key, bucket=bucket)
    return get_local_provider().resolve_url(stored_url=stored_url, object_key=object_key, bucket=bucket)


def delete_media_object(
    *,
    provider: str | None,
    stored_url: str | None,
    object_key: str | None,
    bucket: str | None,
) -> None:
    provider_name = (provider or MEDIA_PROVIDER_LOCAL).strip().lower()
    if provider_name == MEDIA_PROVIDER_S3:
        try:
            get_s3_provider().delete_object(stored_url=stored_url, object_key=object_key, bucket=bucket)
        except HTTPException:
            return
