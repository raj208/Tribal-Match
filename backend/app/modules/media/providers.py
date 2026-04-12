import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings


class LocalMediaStorageProvider:
    PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
    VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm", ".m4v"}

    def __init__(self) -> None:
        self.base_dir = Path(settings.media_upload_dir)
        self.photos_dir = self.base_dir / "photos"
        self.videos_dir = self.base_dir / "videos"

        self.photos_dir.mkdir(parents=True, exist_ok=True)
        self.videos_dir.mkdir(parents=True, exist_ok=True)

    def _get_extension(self, filename: str | None) -> str:
        if not filename:
            return ""
        return Path(filename).suffix.lower()

    def _build_public_url(self, bucket: str, filename: str) -> str:
        return f"{settings.media_public_base_url.rstrip('/')}/{bucket}/{filename}"

    def save_photo(self, file: UploadFile) -> str:
        ext = self._get_extension(file.filename)

        if ext not in self.PHOTO_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only jpg, jpeg, png, and webp images are allowed",
            )

        filename = f"{uuid.uuid4().hex}{ext}"
        target = self.photos_dir / filename

        with target.open("wb") as out:
            shutil.copyfileobj(file.file, out)

        return self._build_public_url("photos", filename)

    def save_video(self, file: UploadFile) -> str:
        ext = self._get_extension(file.filename)

        if ext not in self.VIDEO_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only mp4, mov, webm, and m4v videos are allowed",
            )

        filename = f"{uuid.uuid4().hex}{ext}"
        target = self.videos_dir / filename

        with target.open("wb") as out:
            shutil.copyfileobj(file.file, out)

        return self._build_public_url("videos", filename)