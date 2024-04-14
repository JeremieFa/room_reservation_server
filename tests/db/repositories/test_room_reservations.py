from datetime import datetime, timedelta

from auth_helpers import encode_password
from db.models.room_reservations import RoomReservation
from db.models.users import User
from db.repositories.room_reservations import (
    create_room_reservation,
    delete_room_reservation,
    get_all_reservation_by_user,
    get_all_reservation_on_room_between_dates,
    get_all_rooms_reservations_between_dates,
    get_room_reservation_by_id,
)
from db.repositories.rooms import create_room
from db.repositories.users import save_user
from tests.conftest import TEST_EMAIL, TEST_PASSWORD


def init_foreign_keys(db_session):
    user = User(email=TEST_EMAIL, hashed_password=encode_password(TEST_PASSWORD))
    user_from_db = save_user(db_session, user)
    room_from_db = create_room(db_session, name="Test Room")
    return user_from_db, room_from_db


def test_get_all_reservation_by_user(db_session):
    user_from_db, room_from_db = init_foreign_keys(db_session)
    # date should be at "perfect hours", but it's not important for this test
    start_date = datetime.now()
    end_date = start_date + timedelta(hours=1)
    for _ in range(50):
        create_room_reservation(
            db_session, room_from_db, user_from_db, start_date, end_date
        )

    limit_input = 10
    page_input = 0

    reservations, total, limit, page = get_all_reservation_by_user(
        db_session, user_from_db, limit=limit_input, page=page_input
    )
    assert len(reservations) == limit
    assert limit_input == limit
    assert total == 50
    assert page == page_input


def test_get_all_reservation_on_room_between_dates(db_session):
    user_from_db, room_from_db = init_foreign_keys(db_session)
    # date should be at "perfect hours", but it's not important for this test
    start_date = datetime.now()
    end_date = start_date + timedelta(hours=1)
    reservation = create_room_reservation(
        db_session, room_from_db, user_from_db, start_date, end_date
    )

    reservations = get_all_reservation_on_room_between_dates(
        db_session, user_from_db, start_date, end_date
    )
    assert len(reservations) == 1
    assert reservations[0].id == reservation.id
    assert reservations[0].room_id == room_from_db.id


def test_create_room_reservation(db_session):
    user_from_db, room_from_db = init_foreign_keys(db_session)
    # date should be at "perfect hours", but it's not important for this test
    start_date = datetime.now()
    end_date = start_date + timedelta(hours=1)
    reservation = create_room_reservation(
        db_session, room_from_db, user_from_db, start_date, end_date
    )

    reservation_from_db = db_session.get(RoomReservation, reservation.id)
    assert reservation_from_db is not None
    assert reservation_from_db.id == reservation.id
    assert reservation_from_db.start_date == start_date
    assert reservation_from_db.end_date == end_date
    assert reservation_from_db.user_id == user_from_db.id
    assert reservation_from_db.room_id == room_from_db.id


def test_delete_room_reservation(db_session):
    user_from_db, room_from_db = init_foreign_keys(db_session)

    # date should be at "perfect hours", but it's not important for this test
    start_date = datetime.now()
    end_date = start_date + timedelta(hours=1)
    reservation = create_room_reservation(
        db_session, room_from_db, user_from_db, start_date, end_date
    )

    delete_room_reservation(db_session, reservation)
    reservation_from_db = db_session.get(RoomReservation, reservation.id)
    assert reservation_from_db is None


def test_get_room_reservation_by_id(db_session):
    user_from_db, room_from_db = init_foreign_keys(db_session)
    # date should be at "perfect hours", but it's not important for this test
    start_date = datetime.now()
    end_date = start_date + timedelta(hours=1)
    reservation = create_room_reservation(
        db_session, room_from_db, user_from_db, start_date, end_date
    )

    reservation_from_db = get_room_reservation_by_id(db_session, reservation.id)
    assert reservation_from_db is not None
    assert reservation_from_db.id == reservation.id


def test_get_all_rooms_reservations_on_a_day(db_session):
    user_from_db, room_from_db = init_foreign_keys(db_session)
    start_of_day = datetime.combine(datetime.now(), datetime.min.time())
    start_date = start_of_day + timedelta(hours=1)
    end_date = start_date + timedelta(hours=1)
    reservation = create_room_reservation(
        db_session, room_from_db, user_from_db, start_date, end_date
    )

    reservations = get_all_rooms_reservations_between_dates(
        db_session, start_date=start_of_day, end_date=end_date
    )
    assert len(reservations) == 1
    assert reservations[0].id == reservation.id
