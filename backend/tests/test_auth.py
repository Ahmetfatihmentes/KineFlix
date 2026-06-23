from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from jose import jwt

from backend.core.config import get_settings
from backend.core.deps import get_current_user_id
from backend.core.security import create_access_token


def _register_and_login(client, email: str = "api@example.com", password: str = "supersecret") -> str:
    client.post("/auth/register", json={"email": email, "password": password})
    response = client.post("/auth/login", json={"email": email, "password": password})
    return response.json()["access_token"]


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


def test_auth_me_returns_current_user(client, auth_headers) -> None:
    response = client.get("/auth/me", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["email"] == "testuser@example.com"


def test_auth_me_returns_401_without_token(client) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert "Yetkilendirme" in response.json()["detail"]


def test_auth_me_returns_401_with_invalid_token(client) -> None:
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert "Geçersiz" in response.json()["detail"]


def test_auth_me_returns_404_for_missing_user(client) -> None:
    token = create_access_token({"sub": "99999", "email": "ghost@example.com"})
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert "Kullanıcı" in response.json()["detail"]


def test_watch_history_list_returns_200(client, auth_headers) -> None:
    response = client.get("/watch-history/", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_watch_history_list_returns_401_without_auth(client) -> None:
    response = client.get("/watch-history/")

    assert response.status_code == 401


def test_watch_history_add_returns_201(client, auth_headers) -> None:
    response = client.post(
        "/watch-history/",
        json={"movie_id": 1},
        headers=auth_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["already_exists"] is False
    assert "eklendi" in body["message"].lower()


def test_watch_history_add_returns_401_without_auth(client) -> None:
    response = client.post("/watch-history/", json={"movie_id": 1})

    assert response.status_code == 401


def test_watch_history_add_returns_400_without_movie_id(client, auth_headers) -> None:
    response = client.post("/watch-history/", json={}, headers=auth_headers)

    assert response.status_code == 422


def test_watch_history_add_returns_already_exists(client, auth_headers) -> None:
    client.post("/watch-history/", json={"movie_id": 1}, headers=auth_headers)
    response = client.post(
        "/watch-history/",
        json={"movie_id": 1},
        headers=auth_headers,
    )

    assert response.status_code == 201
    assert response.json()["already_exists"] is True


def test_watch_history_status_returns_watched(client, auth_headers) -> None:
    client.post("/watch-history/", json={"movie_id": 1}, headers=auth_headers)
    response = client.get("/watch-history/1/status", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["watched"] is True


def test_watch_history_status_returns_not_watched(client, auth_headers) -> None:
    response = client.get("/watch-history/2/status", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["watched"] is False


def test_watch_history_status_returns_401_without_auth(client) -> None:
    response = client.get("/watch-history/1/status")

    assert response.status_code == 401


def test_watchlist_list_returns_200(client, auth_headers) -> None:
    response = client.get("/watchlist/", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_watchlist_list_returns_items_after_add(client, auth_headers) -> None:
    client.post("/watchlist/", json={"movie_id": 1}, headers=auth_headers)
    response = client.get("/watchlist/", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Interstellar"
    assert "added_at" in body[0]


def test_watch_history_list_returns_items_after_add(client, auth_headers) -> None:
    client.post("/watch-history/", json={"movie_id": 3}, headers=auth_headers)
    response = client.get("/watch-history/", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Inception"
    assert "watched_at" in body[0]


def test_watchlist_list_returns_401_without_auth(client) -> None:
    response = client.get("/watchlist/")

    assert response.status_code == 401


def test_watchlist_add_returns_201(client, auth_headers) -> None:
    response = client.post(
        "/watchlist/",
        json={"movie_id": 2},
        headers=auth_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["already_exists"] is False
    assert "eklendi" in body["message"].lower()


def test_watchlist_add_returns_401_without_auth(client) -> None:
    response = client.post("/watchlist/", json={"movie_id": 2})

    assert response.status_code == 401


def test_watchlist_add_returns_400_without_movie_id(client, auth_headers) -> None:
    response = client.post("/watchlist/", json={}, headers=auth_headers)

    assert response.status_code == 422


def test_watchlist_status_returns_in_watchlist(client, auth_headers) -> None:
    client.post("/watchlist/", json={"movie_id": 2}, headers=auth_headers)
    response = client.get("/watchlist/2/status", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["in_watchlist"] is True


def test_watchlist_remove_returns_200(client, auth_headers) -> None:
    client.post("/watchlist/", json={"movie_id": 2}, headers=auth_headers)
    response = client.delete("/watchlist/2", headers=auth_headers)

    assert response.status_code == 200
    assert "çıkarıldı" in response.json()["message"].lower()


def test_watchlist_remove_returns_404_when_not_in_list(client, auth_headers) -> None:
    response = client.delete("/watchlist/999", headers=auth_headers)

    assert response.status_code == 404
    assert "Listede" in response.json()["detail"]


def test_watchlist_remove_returns_401_without_auth(client) -> None:
    response = client.delete("/watchlist/1")

    assert response.status_code == 401


def test_personalized_recommendation_returns_200(client, auth_headers) -> None:
    response = client.get("/recommendations/personalized", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["type"] in {"general", "personalized"}
    assert body["recommended_movie"]["title"]


def test_personalized_recommendation_returns_401_without_auth(client) -> None:
    response = client.get("/recommendations/personalized")

    assert response.status_code == 401


def test_personalized_recommendation_uses_watch_history(client, auth_headers) -> None:
    client.post("/watch-history/", json={"movie_id": 1}, headers=auth_headers)
    response = client.get("/recommendations/personalized", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "personalized"
    assert body["source_movie_id"] == 1


@patch(
    "backend.api.v1.endpoints.personalized._get_high_rated_random",
    new_callable=AsyncMock,
    return_value=None,
)
def test_personalized_recommendation_returns_404_when_no_candidates(
    mock_random, client, auth_headers
) -> None:
    response = client.get("/recommendations/personalized", headers=auth_headers)

    assert response.status_code == 404
    assert "Öneri" in response.json()["detail"]


def test_user_preferences_returns_200(client, auth_headers) -> None:
    response = client.post(
        "/users/preferences",
        json={"genres": ["Sci-Fi", "Drama"]},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert "kaydedildi" in response.json()["message"].lower()


def test_user_preferences_returns_401_without_auth(client) -> None:
    response = client.post(
        "/users/preferences",
        json={"genres": ["Sci-Fi"]},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_id_rejects_missing_header() -> None:
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_id(authorization=None, access_token=None)

    assert exc_info.value.status_code == 401
    assert "Yetkilendirme" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_id_rejects_invalid_bearer_format() -> None:
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_id(authorization="Token abc", access_token=None)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_id_rejects_invalid_token() -> None:
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_id(authorization="Bearer not-a-valid-jwt")

    assert exc_info.value.status_code == 401
    assert "Geçersiz" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_id_rejects_non_numeric_sub() -> None:
    token = create_access_token({"sub": "not-a-number", "email": "x@example.com"})
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_id(authorization=f"Bearer {token}")

    assert exc_info.value.status_code == 401
    assert "Geçersiz token" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_id_returns_user_id() -> None:
    token = create_access_token({"sub": "42", "email": "x@example.com"})
    user_id = await get_current_user_id(authorization=f"Bearer {token}")

    assert user_id == 42


def test_expired_token_returns_401(client) -> None:
    expired_token = jwt.encode(
        {
            "sub": "1",
            "email": "expired@example.com",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        },
        get_settings().SECRET_KEY,
        algorithm="HS256",
    )
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {expired_token}"})

    assert response.status_code == 401


def test_invalid_token_returns_401_on_watchlist(client) -> None:
    response = client.get(
        "/watchlist/",
        headers={"Authorization": "Bearer bu-token-gecersiz"},
    )

    assert response.status_code == 401


def test_watchlist_remove_returns_404_for_deleted_movie_entry(client, auth_headers) -> None:
    # Movie 888 has no watchlist entry — simulates a deleted movie whose entry was cleaned up.
    response = client.delete("/watchlist/888", headers=auth_headers)

    assert response.status_code == 404
    assert "bulunamadı" in response.json()["detail"].lower()
