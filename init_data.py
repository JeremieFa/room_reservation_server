import os
import sys

from sqlalchemy import create_engine

from auth_helpers import encode_password
from db.base_class import Base
from db.models.users import User
from db.repositories.rooms import create_room
from db.repositories.users import save_user
from db.session import SessionLocal
from settings import DB_URL

db_path = "../db.db"


def main() -> int:
    """
    This script is used to initialize the database with some data for testing purposes.
    Usage of sqlite is required for this script to work.

    ⚠️ This script will remove the local db file if it exists. ⚠️
    """
    # remove the local db files
    if os.path.exists(db_path):
        os.remove(db_path)

    # create the tables
    engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    db_session = SessionLocal()
    for i in range(1, 11):
        room_name = f"C{i:02d}"
        create_room(db_session, room_name)
        room_name = f"P{i:02d}"
        create_room(db_session, room_name)

    hashed_password = encode_password("test")
    for i in range(1, 10):
        user_email = f"user_{i:02d}@test.com"
        user = User(hashed_password=hashed_password, email=user_email)
        save_user(db_session, user)
    db_session.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
