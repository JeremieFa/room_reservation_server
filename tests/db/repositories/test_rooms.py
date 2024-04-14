from datetime import datetime

from db.models.rooms import Room
from db.repositories.room_reservations import create_room_reservation
from db.repositories.rooms import (
    create_room,
    get_all_rooms,
    get_all_rooms_without_reservations_between_dates,
    get_room_by_id,
)


def test_get_all_rooms(db_session):
    room_db = create_room(db_session, name="Test Room")
    rooms = get_all_rooms(db_session)
    assert len(rooms) == 1
    assert rooms[0].id == room_db.id
    assert rooms[0].name == "Test Room"


def test_get_room_by_id(db_session):
    room_db = create_room(db_session, name="Test Room")
    room_id = room_db.id
    room_db = get_room_by_id(db_session, room_id)
    assert room_db is not None
    assert room_db.id == room_id
    assert room_db.name == "Test Room"


def test_create_room(db_session):
    room_db = create_room(db_session, name="Test Room")
    assert room_db.id is not None
    assert room_db.name == "Test Room"
    assert db_session.get(Room, room_db.id) is not None


def test_get_all_rooms_without_reservations_between_dates(
    db_session, default_room, default_user
):
    start_date = datetime.fromisoformat("2022-01-01T00:00:00Z")
    end_date = datetime.fromisoformat("2022-01-02T00:00:00Z")

    rooms = get_all_rooms_without_reservations_between_dates(
        db_session, start_date, end_date
    )
    assert len(rooms) == 1
    assert rooms[0].id == default_room.id
    assert rooms[0].name == default_room.name

    create_room_reservation(
        db_session,
        user=default_user,
        room=default_room,
        start_date=start_date,
        end_date=end_date,
    )

    rooms = get_all_rooms_without_reservations_between_dates(
        db_session, start_date, end_date
    )
    assert len(rooms) == 0
