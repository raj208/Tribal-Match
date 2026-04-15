from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.security import SupabaseTokenVerificationError
from app.db import models  # noqa: F401
from app.db.base import Base
from app.db.session import get_db
from app.main import app

TEST_DATABASE_URL = "sqlite://"
TEST_AUTH_TOKEN_PREFIX = "test-token:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


@pytest.fixture(autouse=True)
def reset_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def stub_supabase_token_verification(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_verify_supabase_access_token(token: str) -> dict[str, object]:
        if not token.startswith(TEST_AUTH_TOKEN_PREFIX):
            raise SupabaseTokenVerificationError("invalid test token")

        email = token.removeprefix(TEST_AUTH_TOKEN_PREFIX).strip().lower()
        if not email:
            raise SupabaseTokenVerificationError("missing test token email")

        return {
            "sub": f"test-supabase:{email}",
            "email": email,
            "role": "authenticated",
            "aud": "authenticated",
            "iss": "https://project-ref.supabase.co/auth/v1",
            "exp": 1_800_000_000,
        }

    monkeypatch.setattr(
        "app.modules.auth.dependencies.verify_supabase_access_token",
        fake_verify_supabase_access_token,
    )


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    original_app_env = settings.app_env
    original_run_migrations = settings.run_db_migrations_on_startup

    settings.app_env = "test"
    settings.run_db_migrations_on_startup = False

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    settings.app_env = original_app_env
    settings.run_db_migrations_on_startup = original_run_migrations
