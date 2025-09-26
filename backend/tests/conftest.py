# tests/conftest.py
import importlib
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from common.models.model import Base
import common.db as db  # module that defines DatabaseManager


'''
NOTE: Using SQLite for integration tests, standing up postgres is a little much for running tests, behavior is nearly identical
'''


@pytest.fixture(scope="session")
def test_engine():
    
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def db_session(test_engine):
    SessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False, future=True)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(autouse=True)
def override_db(monkeypatch, db_session):
    
    from contextlib import contextmanager

    class TestDatabaseManager:
        @staticmethod
        @contextmanager
        def session_scope():
            try:
                yield db_session
                db_session.commit()
            except Exception:
                db_session.rollback()
                raise
    
    monkeypatch.setattr(db, "DatabaseManager", TestDatabaseManager, raising=False)
    monkeypatch.setattr("api.endpoints.solar_flare.DatabaseManager", TestDatabaseManager, raising=False)
    monkeypatch.setattr("api.endpoints.analysis.DatabaseManager",    TestDatabaseManager, raising=False)

    try:
        import api.endpoints.solar_flare as sf
        importlib.reload(sf)
    except ModuleNotFoundError:
        pass
    try:
        import api.endpoints.analysis as an
        importlib.reload(an)
    except ModuleNotFoundError:
        pass

    yield


@pytest.fixture
def client(override_db):
    
    import api.main as main_module
    importlib.reload(main_module)
    from fastapi.testclient import TestClient
    return TestClient(main_module.app)


@pytest.fixture(autouse=True)
def _clean_db(db_session):
    # Truncate all tables between tests so results are deterministic
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
