"""
Eksik endpoint ve servis testleri — coverage %69 → %80 hedefi.

Kapsanan yeni alanlar:
  auth        : logout, upload-avatar
  movies      : stats
  likes       : toggle, unlike, status, liked-movies
  user_reviews: add, get, delete
  users       : update_profile
  watch_history: delete
  watchlist   : duplicate-add, status-not-in-list
  services    : movie_service edge-cases, personalized edge-cases
"""

import io
from unittest.mock import AsyncMock, patch

import pytest

from backend.services import movie_service


# ─── AUTH: Logout ─────────────────────────────────────────────────────────────

def test_logout_returns_204(client, auth_headers) -> None:
    response = client.post("/auth/logout", headers=auth_headers)
    assert response.status_code == 204


def test_logout_clears_cookie(client, auth_headers) -> None:
    response = client.post("/auth/logout", headers=auth_headers)
    assert response.status_code == 204


def test_logout_requires_auth(client) -> None:
    response = client.post("/auth/logout")
    assert response.status_code == 401


# ─── AUTH: Upload avatar ──────────────────────────────────────────────────────

def test_upload_avatar_returns_avatar_url(client, auth_headers) -> None:
    png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
    response = client.post(
        "/auth/upload-avatar",
        files={"file": ("avatar.png", io.BytesIO(png_bytes), "image/png")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert "avatar_url" in body
    assert body["avatar_url"].endswith(".png")


def test_upload_avatar_requires_auth(client) -> None:
    response = client.post(
        "/auth/upload-avatar",
        files={"file": ("avatar.png", io.BytesIO(b"fake"), "image/png")},
    )
    assert response.status_code == 401


def test_upload_avatar_accepts_jpg(client, auth_headers) -> None:
    jpg_bytes = b"\xff\xd8\xff\xe0" + b"\x00" * 64
    response = client.post(
        "/auth/upload-avatar",
        files={"file": ("photo.jpg", io.BytesIO(jpg_bytes), "image/jpeg")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert "avatar_url" in response.json()


# ─── MOVIES: Stats ────────────────────────────────────────────────────────────

def test_movie_stats_returns_correct_counts(client) -> None:
    response = client.get("/movies/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["movie_count"] == 4
    assert body["review_count"] == 2
    assert "avg_satisfaction_pct" in body


def test_movie_stats_redis_cache_hit(client) -> None:
    import json
    cached_payload = json.dumps(
        {"movie_count": 99, "review_count": 999, "avg_satisfaction_pct": 91}
    )
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=cached_payload)

    with patch(
        "backend.api.v1.endpoints.movies.get_redis",
        new_callable=AsyncMock,
        return_value=mock_redis,
    ):
        response = client.get("/movies/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["movie_count"] == 99


def test_movie_stats_skips_incomplete_cache(client) -> None:
    import json
    incomplete = json.dumps(
        {"movie_count": 10, "review_count": 5, "avg_satisfaction_pct": None}
    )
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=incomplete)
    mock_redis.delete = AsyncMock()
    mock_redis.setex = AsyncMock()

    with patch(
        "backend.api.v1.endpoints.movies.get_redis",
        new_callable=AsyncMock,
        return_value=mock_redis,
    ):
        response = client.get("/movies/stats")

    assert response.status_code == 200
    mock_redis.delete.assert_awaited_once()


# ─── LIKES ────────────────────────────────────────────────────────────────────

def test_toggle_like_creates_like(client, auth_headers) -> None:
    response = client.post("/likes/1", headers=auth_headers)

    assert response.status_code == 201
    assert response.json()["liked"] is True


def test_toggle_like_twice_removes_like(client, auth_headers) -> None:
    client.post("/likes/1", headers=auth_headers)
    response = client.post("/likes/1", headers=auth_headers)

    assert response.status_code == 201
    assert response.json()["liked"] is False


def test_get_like_status_not_liked(client, auth_headers) -> None:
    response = client.get("/likes/1/status", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["liked"] is False
    assert body["like_count"] == 0


def test_get_like_status_after_like(client, auth_headers) -> None:
    client.post("/likes/1", headers=auth_headers)
    response = client.get("/likes/1/status", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["liked"] is True
    assert response.json()["like_count"] == 1


def test_get_liked_movies_empty(client, auth_headers) -> None:
    response = client.get("/likes/my-liked-movies", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_get_liked_movies_returns_liked_film(client, auth_headers) -> None:
    client.post("/likes/1", headers=auth_headers)
    response = client.get("/likes/my-liked-movies", headers=auth_headers)

    assert response.status_code == 200
    titles = [m["title"] for m in response.json()]
    assert "Interstellar" in titles


def test_likes_require_auth(client) -> None:
    assert client.post("/likes/1").status_code == 401
    assert client.get("/likes/1/status").status_code == 401
    assert client.get("/likes/my-liked-movies").status_code == 401


# ─── USER REVIEWS ─────────────────────────────────────────────────────────────

@patch(
    "backend.api.v1.endpoints.user_reviews.analyze_sentiment",
    new_callable=AsyncMock,
    return_value="POSITIVE",
)
def test_add_user_review_returns_201(mock_sentiment, client, auth_headers) -> None:
    response = client.post(
        "/user-reviews/",
        json={"movie_id": 1, "review_text": "Harika bir film!"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["review_text"] == "Harika bir film!"
    assert body["sentiment"] == "POSITIVE"
    mock_sentiment.assert_awaited_once()


@patch(
    "backend.api.v1.endpoints.user_reviews.analyze_sentiment",
    new_callable=AsyncMock,
    return_value="NEGATIVE",
)
def test_add_user_review_negative_sentiment(mock_sentiment, client, auth_headers) -> None:
    response = client.post(
        "/user-reviews/",
        json={"movie_id": 2, "review_text": "Berbat bir filmdi."},
        headers=auth_headers,
    )

    assert response.status_code == 201
    assert response.json()["sentiment"] == "NEGATIVE"


def test_get_movie_user_reviews_returns_list(client) -> None:
    response = client.get("/user-reviews/1")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_movie_user_reviews_empty_for_new_movie(client) -> None:
    response = client.get("/user-reviews/3")

    assert response.status_code == 200
    assert response.json() == []


@patch(
    "backend.api.v1.endpoints.user_reviews.analyze_sentiment",
    new_callable=AsyncMock,
    return_value="POSITIVE",
)
def test_delete_user_review_returns_204(mock_sentiment, client, auth_headers) -> None:
    add_resp = client.post(
        "/user-reviews/",
        json={"movie_id": 1, "review_text": "Silinecek yorum"},
        headers=auth_headers,
    )
    review_id = add_resp.json()["id"]

    response = client.delete(f"/user-reviews/{review_id}", headers=auth_headers)

    assert response.status_code == 204


def test_delete_user_review_returns_404_for_missing(client, auth_headers) -> None:
    response = client.delete("/user-reviews/9999", headers=auth_headers)

    assert response.status_code == 404
    assert "bulunamadı" in response.json()["detail"]


def test_add_user_review_requires_auth(client) -> None:
    response = client.post(
        "/user-reviews/",
        json={"movie_id": 1, "review_text": "test"},
    )
    assert response.status_code == 401


# ─── USERS: Profil güncelleme ─────────────────────────────────────────────────

def test_update_profile_full_name(client, auth_headers) -> None:
    response = client.patch(
        "/users/me",
        json={"full_name": "Test Kullanıcı"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Test Kullanıcı"


def test_update_profile_avatar_url(client, auth_headers) -> None:
    response = client.patch(
        "/users/me",
        json={"avatar_url": "/static/avatars/test.png"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["avatar_url"] == "/static/avatars/test.png"


def test_update_profile_requires_auth(client) -> None:
    response = client.patch("/users/me", json={"full_name": "X"})
    assert response.status_code == 401


# ─── WATCH HISTORY: Delete ────────────────────────────────────────────────────

def test_remove_from_watch_history_returns_200(client, auth_headers) -> None:
    client.post("/watch-history/", json={"movie_id": 2}, headers=auth_headers)
    response = client.delete("/watch-history/2", headers=auth_headers)

    assert response.status_code == 200
    assert "çıkarıldı" in response.json()["message"]


def test_remove_from_watch_history_not_found_returns_message(client, auth_headers) -> None:
    response = client.delete("/watch-history/999", headers=auth_headers)

    assert response.status_code == 200
    assert "bulunamadı" in response.json()["message"]


def test_remove_from_watch_history_requires_auth(client) -> None:
    response = client.delete("/watch-history/1")
    assert response.status_code == 401


def test_remove_then_readd_watch_history(client, auth_headers) -> None:
    client.post("/watch-history/", json={"movie_id": 3}, headers=auth_headers)
    client.delete("/watch-history/3", headers=auth_headers)
    response = client.post("/watch-history/", json={"movie_id": 3}, headers=auth_headers)

    assert response.status_code == 201
    assert response.json()["already_exists"] is False


# ─── WATCHLIST: Ek senaryolar ─────────────────────────────────────────────────

def test_watchlist_duplicate_add_returns_already_exists(client, auth_headers) -> None:
    client.post("/watchlist/", json={"movie_id": 4}, headers=auth_headers)
    response = client.post("/watchlist/", json={"movie_id": 4}, headers=auth_headers)

    assert response.status_code == 201
    assert response.json()["already_exists"] is True


def test_watchlist_status_not_in_list(client, auth_headers) -> None:
    response = client.get("/watchlist/999/status", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["in_watchlist"] is False


# ─── MOVIE SERVICE: Edge-case'ler ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_movie_service_recommendations_when_recommender_not_ready(db_session) -> None:
    from backend.services.recommender import movie_recommender

    movie_recommender.reset()
    result = await movie_service.get_recommendations_for_movie(db_session, movie_id=1)

    assert result is None


@pytest.mark.asyncio
async def test_movie_service_search_with_content_type_and_query(db_session) -> None:
    results = await movie_service.search_movies(
        db_session, query="astronaut", content_type="Movie"
    )
    assert all(m.content_type == "Movie" for m in results)


@pytest.mark.asyncio
async def test_movie_service_search_returns_empty_for_no_match(db_session) -> None:
    results = await movie_service.search_movies(db_session, query="zzznomatch999")
    assert results == []


# ─── PERSONALIZED: Ek senaryolar ─────────────────────────────────────────────

@patch(
    "backend.api.v1.endpoints.personalized._get_high_rated_random",
    new_callable=AsyncMock,
    return_value={
        "type": "general",
        "source_movie_id": None,
        "source_movie_title": None,
        "recommended_movie": {
            "id": 1,
            "title": "Interstellar",
            "overview": None,
            "genres": None,
            "poster_url": None,
            "release_year": 2014,
            "letterboxd_rating": 4.5,
            "content_type": "Movie",
        },
    },
)
def test_personalized_no_history_returns_general_recommendation(
    mock_random, client, auth_headers
) -> None:
    response = client.get("/recommendations/personalized", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["type"] == "general"
    mock_random.assert_awaited_once()


@patch(
    "backend.api.v1.endpoints.personalized._get_high_rated_random",
    new_callable=AsyncMock,
    return_value=None,
)
def test_personalized_returns_404_when_completely_empty(
    mock_random, client, auth_headers
) -> None:
    response = client.get("/recommendations/personalized", headers=auth_headers)

    assert response.status_code == 404
    assert "Öneri" in response.json()["detail"]
