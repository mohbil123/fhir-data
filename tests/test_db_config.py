import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from src.db_config import get_db_engine, get_session


@pytest.fixture
def engine():
    """Fixture to create a database engine."""
    return get_db_engine()


@pytest.fixture
def session(engine):
    """Fixture to create a session using the provided engine."""
    return get_session(engine)


def test_get_db_engine(engine):
    """Test that the database engine is created successfully."""
    assert engine is not None, "Engine creation failed"
    assert engine.dialect.name == 'mysql', "Engine should use MySQL as the database"


def test_get_session(session):
    """Test that a session is successfully created and can connect to the database."""
    try:
        # Use the `text()` function to execute raw SQL
        session.execute(text("SELECT 1"))
    except OperationalError:
        pytest.fail("Failed to connect to the database")
    finally:
        session.close()
