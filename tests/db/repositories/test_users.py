from auth_helpers import encode_password
from db.models.users import User
from db.repositories.users import find_user_by_email, save_user
from tests.conftest import TEST_EMAIL, TEST_PASSWORD


def test_save_user(db_session):
    user = User(email=TEST_EMAIL, hashed_password=encode_password(TEST_PASSWORD))
    save_user(db_session, user)
    assert user.id is not None
    assert user.email == TEST_EMAIL
    assert user.hashed_password != TEST_PASSWORD
    # check the user is in the database
    assert db_session.get(User, user.id) is not None


def test_find_user_by_email(db_session):
    user = User(email=TEST_EMAIL, hashed_password=encode_password(TEST_PASSWORD))
    db_session.add(user)
    db_session.commit()
    db_user = find_user_by_email(db_session, TEST_EMAIL)
    assert db_user is not None
    assert db_user.email == TEST_EMAIL
    assert db_user.hashed_password == user.hashed_password
