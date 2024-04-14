import os
import sys
from datetime import datetime, timezone
from typing import Any, Generator

import pytest
from auth_helpers import Token, create_access_token_from_user, encode_password
from db import Base
from db.models.users import User
from db.repositories.room_reservations import create_room_reservation
from db.repositories.users import save_user
from db.session import get_db
from fastapi import FastAPI
from fastapi.testclient import TestClient
from routers import auth_router, room_reservations_router, rooms_router, users_router
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# this is to include backend dir in sys.path so that we can import from db,main.py

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


TEST_EMAIL = "test@test.com"
TEST_PASSWORD = "password"


def start_application():
    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(users_router, prefix="/users")
    app.include_router(rooms_router, prefix="/rooms")
    app.include_router(room_reservations_router, prefix="/room-reservations")

    return app


SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
# Use connect_args parameter only with sqlite
SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def app() -> Generator[FastAPI, Any, None]:
    """
    Create a fresh database on each test case.
    """
    Base.metadata.create_all(engine)  # Create the tables.
    _app = start_application()
    yield _app
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(app: FastAPI) -> Generator[Session, Any, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionTesting(bind=connection)
    yield session  # use the session in tests.
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(app: FastAPI, db_session: Session) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """

    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def default_user(db_session):
    return save_user(
        db_session,
        User(email=TEST_EMAIL, hashed_password=encode_password(TEST_PASSWORD)),
    )


@pytest.fixture(scope="function")
def default_user_token(default_user):
    return create_access_token_from_user(default_user)


@pytest.fixture(scope="function")
def default_room(db_session):
    from db.repositories.rooms import create_room

    return create_room(db_session, name="Room 1")


@pytest.fixture(scope="function")
def default_reservation(db_session, default_user, default_room):
    start_date = datetime.fromisoformat("2021-01-01T08:00").replace(tzinfo=timezone.utc)
    end_date = datetime.fromisoformat("2021-01-01T10:00").replace(tzinfo=timezone.utc)

    return create_room_reservation(
        db_session, default_room, default_user, start_date, end_date
    )


def create_test_user(
    email: str, password: str, db_session: Session
) -> tuple[User, Token]:
    user = save_user(
        db_session, User(email=email, hashed_password=encode_password(password))
    )
    token = create_access_token_from_user(user)
    return user, token
