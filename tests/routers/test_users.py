from datetime import datetime


def test_get_my_reservations(client, default_user_token, default_reservation):
    response = client.get(
        "/users/my-reservations",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {default_user_token.access_token}",
        },
    )
    assert 200 == response.status_code
    response_json = response.json()
    limit = response_json["limit"]
    page = response_json["page"]
    total = response_json["total"]
    reservations = response_json["reservations"]
    reservation = reservations[0]
    assert 10 == limit
    assert 0 == page
    assert 1 == total
    assert default_reservation.id == reservation["id"]
    assert default_reservation.room_id == reservation["room"]["id"]
    assert default_reservation.user_id == reservation["user"]["id"]
    assert default_reservation.start_date.isoformat() + "Z" == reservation["start_date"]
    assert default_reservation.end_date.isoformat() + "Z" == reservation["end_date"]


def test_get_my_reservations_without_auth(client):
    response = client.get(
        "/users/my-reservations",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    assert 401 == response.status_code
    response_json = response.json()
    assert "detail" in response_json
    assert "Not authenticated" == response_json["detail"]
