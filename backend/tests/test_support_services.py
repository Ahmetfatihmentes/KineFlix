from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.api.error_handlers import register_exception_handlers
from backend.core import exceptions
from backend.core.security import create_access_token, get_password_hash, verify_password, verify_token
from backend.models.movie import Movie
from backend.services import user_service
from backend.services.ollama_service import (
    _finalize_recommendation_reason,
    apply_tr_fixes,
    generate_recommendation_reason,
    translate_genres,
)
from backend.services.tmdb_trailer import (
    _pick_trailer,
    _search_resource,
    _video_resource,
    fetch_trailer_key,
)


def test_translate_genres_maps_known_values() -> None:
    assert "Bilim Kurgu" in translate_genres("Science Fiction, Drama")


def test_translate_genres_returns_empty_for_blank() -> None:
    assert translate_genres("") == ""


def test_apply_tr_fixes_replaces_english_words() -> None:
    result = apply_tr_fixes("A powerful drama with deep emotion.")

    assert "güçlü" in result.lower()
    assert "dram" in result.lower()


def test_finalize_recommendation_reason_limits_body_sentences() -> None:
    body = "First sentence. Second sentence. Third sentence."
    closing = "Bu filmi beğenmeye değer."
    result = _finalize_recommendation_reason(body, closing, "A", "B")

    assert result.endswith(closing)
    assert "Third sentence" not in result


def test_get_password_hash_and_verify() -> None:
    hashed = get_password_hash("secret123")

    assert hashed != "secret123"
    assert verify_password("secret123", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_verify_token_roundtrip() -> None:
    token = create_access_token({"sub": "1", "email": "a@b.com"})
    payload = verify_token(token)

    assert payload is not None
    assert payload["sub"] == "1"


def test_verify_token_returns_none_for_invalid() -> None:
    assert verify_token("invalid") is None


def test_tmdb_video_resource_for_tv_show() -> None:
    assert _video_resource("TV Show") == "tv"
    assert _video_resource("Movie") == "movie"


def test_tmdb_search_resource_for_tv_show() -> None:
    assert _search_resource("TV Show") == "search/tv"
    assert _search_resource(None) == "search/movie"


def test_tmdb_pick_trailer_prefers_trailer_over_teaser() -> None:
    videos = [
        {"site": "YouTube", "type": "Teaser", "key": "teaser1"},
        {"site": "YouTube", "type": "Trailer", "key": "trailer1"},
    ]

    assert _pick_trailer(videos) == "trailer1"


def test_tmdb_pick_trailer_falls_back_to_teaser() -> None:
    videos = [{"site": "YouTube", "type": "Teaser", "key": "teaser1"}]

    assert _pick_trailer(videos) == "teaser1"


def test_tmdb_pick_trailer_returns_none_when_empty() -> None:
    assert _pick_trailer([]) is None


@pytest.mark.asyncio
async def test_fetch_trailer_key_uses_tmdb_id_when_present() -> None:
    movie = Movie(id=1, title="Test", content_type="Movie")
    movie.tmdb_id = 42

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [{"site": "YouTube", "type": "Trailer", "key": "key42"}]
    }

    with patch("backend.services.tmdb_trailer.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get.return_value = mock_response
        mock_client_cls.return_value = mock_client

        key = await fetch_trailer_key(movie, "api-key")

    assert key == "key42"


@pytest.mark.asyncio
async def test_fetch_trailer_key_searches_when_direct_lookup_fails() -> None:
    movie = Movie(id=5, title="Search Me", release_year=2020, content_type="Movie")

    empty_response = MagicMock()
    empty_response.status_code = 200
    empty_response.json.return_value = {"results": []}

    search_response = MagicMock()
    search_response.status_code = 200
    search_response.json.return_value = {
        "results": [{"id": 99, "release_date": "2020-01-01"}]
    }

    trailer_response = MagicMock()
    trailer_response.status_code = 200
    trailer_response.json.return_value = {
        "results": [{"site": "YouTube", "type": "Trailer", "key": "found99"}]
    }

    with patch("backend.services.tmdb_trailer.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get.side_effect = [
            empty_response,
            empty_response,
            search_response,
            trailer_response,
        ]
        mock_client_cls.return_value = mock_client

        key = await fetch_trailer_key(movie, "api-key")

    assert key == "found99"


@pytest.mark.asyncio
@patch("backend.services.ollama_service._is_ollama_available", new_callable=AsyncMock, return_value=True)
async def test_generate_recommendation_reason_with_ollama_mock(mock_available) -> None:
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.content = b'{"response": "Benzer temalar ve karakterler var."}'

    with patch("backend.services.ollama_service.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = await generate_recommendation_reason(
            source_movie_title="Film A",
            source_movie_genres="Drama, Thriller",
            source_movie_overview="A dramatic story about survival.",
            recommended_movie_title="Film B",
            recommended_movie_genres="Drama, Thriller",
            recommended_movie_overview="Another survival drama with tension.",
            source_movie_director="Director X",
            recommended_movie_director="Director X",
            source_movie_actors="Actor One, Actor Two",
            recommended_movie_actors="Actor One, Actor Three",
            source_movie_score=85.0,
            recommended_movie_score=90.0,
        )

    assert result is not None
    assert "beğen" in result.lower()


@pytest.mark.asyncio
async def test_generate_review_summary_returns_none_for_short_reviews() -> None:
    from backend.services.ollama_service import generate_review_summary

    result = await generate_review_summary(
        movie_title="Test",
        reviews=["short"],
    )

    assert result is None


@pytest.mark.asyncio
async def test_generate_review_summary_with_ollama_mock() -> None:
    from backend.services.ollama_service import generate_review_summary

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.content = (
        b'{"response": "1. Genel kanaat olumlu. 2. Gorsel efektler ovgu aldi. 3. Bilim kurgu severler icin."}'
    )

    with patch("backend.services.ollama_service.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = await generate_review_summary(
            movie_title="Interstellar",
            reviews=[
                "A stunning visual masterpiece with emotional depth and ambition.",
                "Nolan delivers an ambitious sci-fi epic worth watching again.",
            ],
            positive_pct=92.0,
        )

    assert result is not None
    assert "olumlu" in result.lower() or "gorsel" in result.lower()


@pytest.mark.asyncio
@patch("backend.services.ollama_service._is_ollama_available", new_callable=AsyncMock, return_value=False)
async def test_generate_recommendation_reason_returns_fallback_when_ollama_down(mock_available) -> None:
    result = await generate_recommendation_reason(
        source_movie_title="A",
        source_movie_genres="Drama",
        source_movie_overview="Overview A",
        recommended_movie_title="B",
        recommended_movie_genres="Drama",
        recommended_movie_overview="Overview B",
    )

    assert result is not None
    assert "beğenebilirsin" in result or "türünde" in result


@pytest.mark.asyncio
async def test_user_service_save_preferences(db_session) -> None:
    from backend.models.user import User

    user = User(email="pref@test.com", password_hash="hash", role="standard")
    db_session.add(user)
    await db_session.commit()

    await user_service.save_user_preferences(
        db_session, user_id=user.id, genres=[" Sci-Fi ", "", "Drama"]
    )

    from sqlalchemy import select
    from backend.models.user_preference import UserPreference

    result = await db_session.execute(
        select(UserPreference).where(UserPreference.user_id == user.id)
    )
    genres = {item.genre for item in result.scalars().all()}
    assert genres == {"Sci-Fi", "Drama"}


def test_error_handlers_map_business_exception() -> None:
    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/test-business-error")
    async def raise_business_error() -> None:
        raise exceptions.ValidationException("Is kurali hatasi")

    register_exception_handlers(app)

    with TestClient(app, raise_server_exceptions=False) as test_client:
        response = test_client.get("/test-business-error")

    assert response.status_code == 400
    assert response.json()["detail"] == "Is kurali hatasi"


def test_error_handlers_map_not_found_exception() -> None:
    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/test-not-found-error")
    async def raise_not_found_error() -> None:
        raise exceptions.NotFoundException("Kayit yok")

    register_exception_handlers(app)

    with TestClient(app, raise_server_exceptions=False) as test_client:
        response = test_client.get("/test-not-found-error")

    assert response.status_code == 404
    assert response.json()["detail"] == "Kayit yok"


def test_error_handlers_map_unhandled_exception() -> None:
    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/test-unhandled-error")
    async def raise_unhandled_error() -> None:
        raise RuntimeError("boom")

    register_exception_handlers(app)

    with TestClient(app, raise_server_exceptions=False) as test_client:
        response = test_client.get("/test-unhandled-error")

    assert response.status_code == 500
    assert "sunucu" in response.json()["detail"].lower()
