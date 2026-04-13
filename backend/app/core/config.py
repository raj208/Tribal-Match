import json
from functools import lru_cache
from json import JSONDecodeError
from typing import Any

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


def _parse_cors_origins(value: Any) -> Any:
    if not isinstance(value, str):
        return value

    raw_value = value.strip()
    if not raw_value:
        return []

    # Accept a single URL or comma-separated URLs from `.env` without requiring JSON syntax.
    try:
        parsed_value = json.loads(raw_value)
    except JSONDecodeError:
        return [origin.strip() for origin in raw_value.split(",") if origin.strip()]

    if isinstance(parsed_value, str):
        return [parsed_value]

    if isinstance(parsed_value, list):
        return [str(origin).strip() for origin in parsed_value if str(origin).strip()]

    return parsed_value


class FlexibleEnvSettingsSource(EnvSettingsSource):
    def prepare_field_value(self, field_name: str, field: Any, value: Any, value_is_complex: bool) -> Any:
        if field_name == "backend_cors_origins":
            return _parse_cors_origins(value)

        return super().prepare_field_value(field_name, field, value, value_is_complex)


class FlexibleDotEnvSettingsSource(DotEnvSettingsSource):
    def prepare_field_value(self, field_name: str, field: Any, value: Any, value_is_complex: bool) -> Any:
        if field_name == "backend_cors_origins":
            return _parse_cors_origins(value)

        return super().prepare_field_value(field_name, field, value, value_is_complex)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="Tribal Match API", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")

    backend_cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        alias="BACKEND_CORS_ORIGINS",
    )

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/tribal_match",
        alias="DATABASE_URL",
    )
    run_db_migrations_on_startup: bool = Field(
        default=False,
        alias="RUN_DB_MIGRATIONS_ON_STARTUP",
    )

    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_server_key: str = Field(default="", alias="SUPABASE_SERVER_KEY")

    media_upload_dir: str = Field(default="./storage/uploads", alias="MEDIA_UPLOAD_DIR")
    media_public_base_url: str = Field(
        default="http://localhost:8000/uploads",
        alias="MEDIA_PUBLIC_BASE_URL",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            FlexibleEnvSettingsSource(
                settings_cls,
                case_sensitive=getattr(env_settings, "case_sensitive", None),
                env_prefix=getattr(env_settings, "env_prefix", None),
                env_nested_delimiter=getattr(env_settings, "env_nested_delimiter", None),
                env_ignore_empty=getattr(env_settings, "env_ignore_empty", None),
                env_parse_none_str=getattr(env_settings, "env_parse_none_str", None),
                env_parse_enums=getattr(env_settings, "env_parse_enums", None),
            ),
            FlexibleDotEnvSettingsSource(
                settings_cls,
                env_file=getattr(dotenv_settings, "env_file", None),
                env_file_encoding=getattr(dotenv_settings, "env_file_encoding", None),
                case_sensitive=getattr(dotenv_settings, "case_sensitive", None),
                env_prefix=getattr(dotenv_settings, "env_prefix", None),
                env_nested_delimiter=getattr(dotenv_settings, "env_nested_delimiter", None),
                env_ignore_empty=getattr(dotenv_settings, "env_ignore_empty", None),
                env_parse_none_str=getattr(dotenv_settings, "env_parse_none_str", None),
                env_parse_enums=getattr(dotenv_settings, "env_parse_enums", None),
            ),
            file_secret_settings,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
