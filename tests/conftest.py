import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SHORT_LINK_BASE"] = "https://short.io/r"
# Sentry не должен инициализироваться из .env во время тестов
os.environ["SENTRY_DSN"] = ""

import pytest
from fastapi.testclient import TestClient

from database import init_db, reset_engine


@pytest.fixture
def client() -> TestClient:
    from main import app

    return TestClient(app)


@pytest.fixture(autouse=True)
def fresh_db() -> None:
    reset_engine()
    init_db()
    yield
    reset_engine()
