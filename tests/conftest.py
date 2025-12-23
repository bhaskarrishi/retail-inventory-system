import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.db import Base, get_db
from app.main import app


# Use in-memory SQLite database for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Create a test engine that will be shared across fixtures
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Create tables once for all tests
Base.metadata.create_all(bind=test_engine)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db():
    """Provide a fresh database session for each test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    db_session = TestingSessionLocal(bind=connection)
    
    yield db_session
    
    db_session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db: Session):
    """Provide a test client for making HTTP requests."""
    
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    test_client = TestClient(app)
    yield test_client
    
    app.dependency_overrides.clear()
