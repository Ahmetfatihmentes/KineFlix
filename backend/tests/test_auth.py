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
