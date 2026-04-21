from app.core.config import settings
from app.main import _should_run_migrations_on_startup


def test_remote_database_does_not_auto_run_migrations_in_development() -> None:
    original_app_env = settings.app_env
    original_run_migrations = settings.run_db_migrations_on_startup
    original_database_url = settings.database_url

    settings.app_env = "development"
    settings.run_db_migrations_on_startup = False
    settings.database_url = "postgresql+psycopg://postgres:secret@db.example.supabase.co:5432/postgres"

    try:
        assert _should_run_migrations_on_startup() is False
    finally:
        settings.app_env = original_app_env
        settings.run_db_migrations_on_startup = original_run_migrations
        settings.database_url = original_database_url


def test_local_database_still_auto_runs_migrations_in_development() -> None:
    original_app_env = settings.app_env
    original_run_migrations = settings.run_db_migrations_on_startup
    original_database_url = settings.database_url

    settings.app_env = "development"
    settings.run_db_migrations_on_startup = False
    settings.database_url = "postgresql+psycopg://postgres:newpassword@localhost:5433/tribal_match"

    try:
        assert _should_run_migrations_on_startup() is True
    finally:
        settings.app_env = original_app_env
        settings.run_db_migrations_on_startup = original_run_migrations
        settings.database_url = original_database_url
