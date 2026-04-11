import json
from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

BASE_DIR = Path(__file__).resolve().parents[2]


class CorsOriginsEnvSettingsSource(EnvSettingsSource):
    def prepare_field_value(self, field_name, field, value, value_is_complex):
        if field_name == "backend_cors_origins":
            return value
        return super().prepare_field_value(field_name, field, value, value_is_complex)


class CorsOriginsDotEnvSettingsSource(DotEnvSettingsSource):
    def prepare_field_value(self, field_name, field, value, value_is_complex):
        if field_name == "backend_cors_origins":
            return value
        return super().prepare_field_value(field_name, field, value, value_is_complex)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    app_name: str = Field(default="Tribal Match API", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    database_url: str = Field(
        default="postgresql+psycopg://postgres:newpassword@localhost:5433/tribal_match",
        alias="DATABASE_URL",
    )
    supabase_jwt_secret: str = Field(default="", alias="SUPABASE_JWT_SECRET")
    sentry_dsn: str = Field(default="", alias="SENTRY_DSN")
    backend_cors_origins: list[str] = Field(default=["http://localhost:3000"], alias="BACKEND_CORS_ORIGINS")

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
            CorsOriginsEnvSettingsSource(settings_cls),
            CorsOriginsDotEnvSettingsSource(settings_cls),
            file_secret_settings,
        )

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        stripped_value = value.strip()
        if stripped_value.startswith("["):
            parsed_value = json.loads(stripped_value)
            if isinstance(parsed_value, list):
                return [str(item).strip() for item in parsed_value if str(item).strip()]
        return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
