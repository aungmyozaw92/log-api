import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db


@pytest.fixture(scope="session")
def test_db_url():
    # Use a temporary SQLite file DB to persist across connections
    tmpdir = tempfile.TemporaryDirectory()
    path = os.path.join(tmpdir.name, "test.db")
    url = f"sqlite:///{path}"
    yield url
    tmpdir.cleanup()


@pytest.fixture(scope="session")
def engine(test_db_url):
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


