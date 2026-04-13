from __future__ import annotations

import logging
from pathlib import Path

from alembic import command
from alembic.config import Config

from app.core.config import settings

logger = logging.getLogger(__name__)


def _backend_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_alembic_config() -> Config:
    backend_root = _backend_root()
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "app" / "db" / "migrations"))
    config.set_main_option("prepend_sys_path", str(backend_root))
    config.set_main_option("sqlalchemy.url", settings.database_url)
    return config


def run_database_migrations() -> None:
    logger.info("Applying database migrations before serving requests")
    command.upgrade(build_alembic_config(), "head")
    logger.info("Database schema is up to date")
