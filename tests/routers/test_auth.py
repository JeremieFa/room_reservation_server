from tests.conftest import TEST_EMAIL, TEST_PASSWORD


def test_login(client, default_user):
    response = client.post(
        "/api/auth",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    assert 200 == response.status_code


def test_login_user_not_found(client):
    response = client.post(
        "/api/auth",
        json={"email": "email", "password": "password"},
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    assert 401 == response.status_code
