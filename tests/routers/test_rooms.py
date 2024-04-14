from datetime import datetime, timedelta, timezone

from db.repositories.room_reservations import create_room_reservation
from routers.rooms import (
    ROOM_RESERVATION_CREATION_ALREADY_RESERVED_ERROR,
    ROOM_RESERVATION_CREATION_DATES_NOT_AWARE_ERROR,
    ROOM_RESERVATION_CREATION_INVALID_DATES_ERROR,
)


def test_get_all(default_room, default_user_token, client):
    response = client.get(
        "/rooms/",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {default_user_token.access_token}",
        },
    )
    assert 200 == response.status_code
    response_json = response.json()
    assert 1 == len(response_json)
    room = response_json[0]
    assert default_room.id == room["id"]
    assert default_room.name == room["name"]


# Create reservation :


def get_start_and_end_date():
    start_date = datetime.now(timezone.utc) + timedelta(days=1)
    start_date = start_date.replace(minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(hours=1)
    return start_date, end_date


def test_create_reservation(default_room, default_user, default_user_token, client):
    start_date, end_date = get_start_and_end_date()

    response = client.post(
        f"/rooms/{default_room.id}/create-reservation",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {default_user_token.access_token}",
        },
        json={"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
    )
    assert 201 == response.status_code
    response_json = response.json()
    assert default_room.id == response_json["room"]["id"]
    assert default_user.id == response_json["user"]["id"]
    assert start_date == datetime.fromisoformat(response_json["start_date"])
    assert end_date == datetime.fromisoformat(response_json["end_date"])


def test_create_reservation_without_token(default_room, client):
    start_date, end_date = get_start_and_end_date()

    response = client.post(
        f"/rooms/{default_room.id}/create-reservation",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json={"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
    )
    assert 401 == response.status_code


def test_create_reservation_without_aware_dates(
    default_room, default_user_token, client
):
    start_date, end_date = get_start_and_end_date()
    start_date = start_date.replace(tzinfo=None)
    end_date = end_date.replace(tzinfo=None)

    response = client.post(
        f"/rooms/{default_room.id}/create-reservation",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {default_user_token.access_token}",
        },
        json={"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
    )
    assert 400 == response.status_code
    assert ROOM_RESERVATION_CREATION_DATES_NOT_AWARE_ERROR == response.json()["detail"]


def test_create_reservation_start_date_after_end_date(
    default_room, default_user_token, client
):
    start_date, _ = get_start_and_end_date()
    end_date = start_date - timedelta(hours=1)

    response = client.post(
        f"/rooms/{default_room.id}/create-reservation",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {default_user_token.access_token}",
        },
        json={"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
    )
    assert 400 == response.status_code
    assert ROOM_RESERVATION_CREATION_INVALID_DATES_ERROR == response.json()["detail"]


def test_create_reservation_start_date_with_minutes_and_seconds(
    default_room, default_user_token, client
):
    start_date, end_date = get_start_and_end_date()
    start_date = start_date.replace(second=1)
    response = client.post(
        f"/rooms/{default_room.id}/create-reservation",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {default_user_token.access_token}",
        },
        json={"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
    )
    assert 400 == response.status_code
    assert ROOM_RESERVATION_CREATION_INVALID_DATES_ERROR == response.json()["detail"]


def test_create_reservation_already_reserved(
    db_session, default_user, default_room, default_user_token, client
):
    start_date, end_date = get_start_and_end_date()
    # Create the first reservation
    create_room_reservation(
        db_session, default_room, default_user, start_date, end_date
    )

    response = client.post(
        f"/rooms/{default_room.id}/create-reservation",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {default_user_token.access_token}",
        },
        json={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
    )
    assert 400 == response.status_code
    assert (
        f"{ROOM_RESERVATION_CREATION_ALREADY_RESERVED_ERROR}{start_date.hour}:00"
        == response.json()["detail"]
    )


def test_get_all_rooms_reservations(
    default_room, default_user, default_user_token, default_reservation, client
):
    start_date = default_reservation.start_date
    end_date = default_reservation.end_date
    url = f"/rooms/all-rooms-reservations?start_date={start_date}&end_date={end_date}"
    response = client.get(
        url,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {default_user_token.access_token}",
        },
    )
    assert 200 == response.status_code
    response_json = response.json()
    assert 1 == len(response_json)
    room_reservations = response_json[0]
    assert default_room.id == room_reservations["id"]
    assert default_room.name == room_reservations["name"]
    assert 1 == len(room_reservations["reservations"])
    reservation = room_reservations["reservations"][0]
    assert default_reservation.id == reservation["id"]
    assert default_user.id == reservation["user"]["id"]
    assert default_room.id == reservation["room"]["id"]


def get_available_rooms(default_room, client):
    start_date, end_date = get_start_and_end_date()
    url = f"/rooms/available-rooms?start_date={start_date}&end_date={end_date}"
    response = client.get(
        url,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    assert 200 == response.status_code
    response_json = response.json()
    assert 1 == len(response_json)
    room = response_json[0]
    assert default_room.id == room["id"]
    assert default_room.name == room["name"]


def get_available_rooms_no_rooms(client):
    start_date, end_date = get_start_and_end_date()
    url = f"/rooms/available-rooms?start_date={start_date}&end_date={end_date}"
    response = client.get(
        url,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    assert 200 == response.status_code
    response_json = response.json()
    assert 0 == len(response_json)


def get_available_rooms_not_authenticated(default_room, client):
    start_date, end_date = get_start_and_end_date()
    url = f"/rooms/available-rooms?start_date={start_date}&end_date={end_date}"
    response = client.get(
        url,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    assert 401 == response.status_code
