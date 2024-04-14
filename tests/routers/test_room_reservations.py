from datetime import datetime, timedelta

from db.repositories.room_reservations import create_room_reservation
from tests.conftest import create_test_user


def test_delete_reservation(
    db_session, client, default_user, default_user_token, default_room
):

    start_date = datetime.now() + timedelta(days=1)
    end_date = start_date + timedelta(hours=1)

    futur_reservation = create_room_reservation(
        db_session, default_room, default_user, start_date, end_date
    )

    response = client.delete(
        f"/room-reservations/{futur_reservation.id}",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {default_user_token.access_token}",
        },
    )
    assert 200 == response.status_code
    response_json = response.json()
    assert "Reservation deleted" == response_json["message"]


def test_delete_reservation_passed(client, default_user_token, default_reservation):
    response = client.delete(
        f"/room-reservations/{default_reservation.id}",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {default_user_token.access_token}",
        },
    )
    assert 400 == response.status_code
    response_json = response.json()
    assert "You can't delete a past reservation" == response_json["detail"]


def test_delete_reservation_not_creator(
    db_session, client, default_user_token, default_reservation
):

    _, other_user_token = create_test_user("email@email.fr", "pass", db_session)

    response = client.delete(
        f"/room-reservations/{default_reservation.id}",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {other_user_token.access_token}",
        },
    )
    assert 400 == response.status_code
    response_json = response.json()
    assert "You are not allowed to delete this reservation" == response_json["detail"]
