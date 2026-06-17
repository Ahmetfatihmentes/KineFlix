def test_register_endpoint_returns_created_user(client) -> None:
    response = client.post(
        "/auth/register",
        json={"email": "api@example.com", "password": "supersecret"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "api@example.com"
    assert body["role"] == "standard"
    assert "password" not in body


def test_register_endpoint_rejects_duplicate_email(client) -> None:
    client.post(
        "/auth/register",
        json={"email": "dup@example.com", "password": "supersecret"},
    )
    response = client.post(
        "/auth/register",
        json={"email": "dup@example.com", "password": "supersecret"},
    )

    assert response.status_code == 400
    assert "kayıtlı" in response.json()["detail"].lower() or "kayitli" in response.json()["detail"].lower()


def test_login_endpoint_returns_token(client) -> None:
    client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "supersecret"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "supersecret"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["email"] == "login@example.com"
    assert body["role"] == "standard"
    assert isinstance(body["access_token"], str)
    assert len(body["access_token"]) > 0
    assert isinstance(body["user_id"], int)


def test_login_endpoint_rejects_invalid_credentials(client) -> None:
    client.post(
        "/auth/register",
        json={"email": "wrongpass@example.com", "password": "supersecret"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "wrongpass@example.com", "password": "notthepassword"},
    )

    assert response.status_code == 400
    assert "hatalı" in response.json()["detail"].lower() or "hatali" in response.json()["detail"].lower()
