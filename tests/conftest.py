"""Test setup. Tests ALWAYS use a throwaway database: a temporary SQLite file by default, or
TEST_DATABASE_URL (PostgreSQL) whose database name must end with '_test'. DATABASE_URL (your real/Supabase DB)
is overwritten here, so tests can never touch it."""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
_url = os.environ.get("TEST_DATABASE_URL") or f"sqlite:///{Path(tempfile.mkdtemp()).as_posix()}/test.db"
assert _url.startswith("sqlite") or _url.rsplit("/", 1)[-1].split("?")[0].endswith("_test"), \
    "TEST_DATABASE_URL must point at a database whose name ends with _test"
os.environ["DATABASE_URL"] = _url
os.environ["SECRET_KEY"] = "test-secret-key"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import manage  # noqa: E402
from database import SessionLocal, engine  # noqa: E402
from models import Base  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def database():
    Base.metadata.drop_all(engine)      # safe: this is the throwaway test database
    Base.metadata.create_all(engine)
    with SessionLocal() as s:
        manage.import_csv(s)
        manage.create_editor(s, "alice", "alice-password-1")
        manage.create_editor(s, "bob", "bob-password-22")
    yield


@pytest.fixture
def client():
    from main import app
    return TestClient(app)


def login(client, user="alice", pw="alice-password-1"):
    r = client.post("/api/auth/login", json={"username": user, "password": pw})
    assert r.status_code == 200, r.text
    return {"Authorization": "Bearer " + r.json()["token"]}


@pytest.fixture
def alice(client):
    return login(client)
