from unittest.mock import AsyncMock, patch

import pytest

from backend.schemas.movie import MovieDetailRead
from backend.services import movie_service


def test_search_movies_returns_matching_titles(client) -> None:
    response = client.get("/movies/search", params={"query": "Inter"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Interstellar"


def test_search_movies_returns_all_when_query_empty(client) -> None:
    response = client.get("/movies/search", params={"query": ""})

    assert response.status_code == 200
    assert len(response.json()) == 4


def test_search_movies_filters_by_content_type(client) -> None:
    response = client.get(
        "/movies/search",
        params={"query": "", "content_type": "Movie"},
    )

    assert response.status_code == 200
    assert all(item["content_type"] == "Movie" for item in response.json())


def test_get_movie_returns_detail(client) -> None:
    response = client.get("/movies/1")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "Interstellar"


def test_get_movie_returns_404_for_missing_id(client) -> None:
    response = client.get("/movies/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Film bulunamadı"


def test_get_movie_reviews_returns_reviews(client) -> None:
    response = client.get("/movies/1/reviews")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["review_text"]


def test_get_movie_reviews_returns_404_for_missing_movie(client) -> None:
    response = client.get("/movies/999/reviews")

    assert response.status_code == 404
    assert response.json()["detail"] == "Film bulunamadı"


def test_recommendations_returns_related_movies(client) -> None:
    response = client.get("/movies/1/recommendations")

    assert response.status_code == 200
    body = response.json()
    assert len(body) > 0
    titles = {item["title"] for item in body}
    assert "The Martian" in titles or "Gravity" in titles


def test_recommendations_returns_404_for_missing_movie(client) -> None:
    response = client.get("/movies/999/recommendations")

    assert response.status_code == 404
    assert response.json()["detail"] == "Film bulunamadı"


@patch("backend.api.v1.endpoints.recommendations.movie_recommender")
def test_recommendations_returns_loading_status_when_not_ready(mock_recommender, client) -> None:
    mock_recommender.is_ready = False
    mock_recommender.is_loading = False
    mock_recommender.start_background_initialization = AsyncMock()

    response = client.get("/movies/1/recommendations")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "loading"


@patch(
    "backend.api.v1.endpoints.movies.generate_recommendation_reason",
    new_callable=AsyncMock,
    return_value="Benzer bilim kurgu temaları paylaşıyorlar.",
)
def test_recommendation_reason_returns_200(mock_reason, client) -> None:
    response = client.get(
        "/movies/1/recommendation-reason",
        params={"recommended_id": 2},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["source_movie"] == "Interstellar"
    assert body["recommended_movie"] == "The Martian"
    assert "reason" in body
    mock_reason.assert_awaited_once()


@patch(
    "backend.api.v1.endpoints.movies.generate_recommendation_reason",
    new_callable=AsyncMock,
    return_value=None,
)
def test_recommendation_reason_uses_fallback_when_ollama_empty(mock_reason, client) -> None:
    response = client.get(
        "/movies/1/recommendation-reason",
        params={"recommended_id": 2},
    )

    assert response.status_code == 200
    assert "benzer türde" in response.json()["reason"].lower()


def test_recommendation_reason_returns_404_for_missing_movie(client) -> None:
    response = client.get(
        "/movies/1/recommendation-reason",
        params={"recommended_id": 999},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Film bulunamadı"


@patch(
    "backend.api.v1.endpoints.movies.generate_review_summary",
    new_callable=AsyncMock,
    return_value="Genel olarak olumlu eleştiriler almış bir yapım.",
)
def test_ai_review_returns_summary_when_reviews_exist(mock_summary, client) -> None:
    response = client.get("/movies/1/ai-review")

    assert response.status_code == 200
    body = response.json()
    assert body["movie_id"] == 1
    assert body["has_reviews"] is True
    assert body["review_count"] == 2
    assert body["ai_review"] is not None
    mock_summary.assert_awaited_once()


def test_ai_review_returns_null_when_no_reviews(client) -> None:
    response = client.get("/movies/2/ai-review")

    assert response.status_code == 200
    body = response.json()
    assert body["has_reviews"] is False
    assert body["ai_review"] is None
    assert body["review_count"] == 0


def test_ai_review_returns_404_for_missing_movie(client) -> None:
    response = client.get("/movies/999/ai-review")

    assert response.status_code == 404
    assert response.json()["detail"] == "Film bulunamadı"


def test_trailer_returns_cached_key(client) -> None:
    response = client.get("/movies/1/trailer")

    assert response.status_code == 200
    body = response.json()
    assert body["youtube_key"] == "abc123"
    assert body["cached"] is True
    assert "youtube.com" in body["youtube_url"]


def test_trailer_returns_404_for_missing_movie(client) -> None:
    response = client.get("/movies/999/trailer")

    assert response.status_code == 404
    assert response.json()["detail"] == "Film bulunamadı"


@patch("backend.api.v1.endpoints.movies.get_settings")
def test_trailer_returns_503_when_tmdb_key_missing(mock_settings, client) -> None:
    mock_settings.return_value.TMDB_API_KEY = None

    response = client.get("/movies/2/trailer")

    assert response.status_code == 503
    assert "TMDB" in response.json()["detail"]


@patch("backend.api.v1.endpoints.movies.fetch_trailer_key", new_callable=AsyncMock, return_value=None)
@patch("backend.api.v1.endpoints.movies.get_settings")
def test_trailer_returns_404_when_not_found(mock_settings, mock_fetch, client) -> None:
    mock_settings.return_value.TMDB_API_KEY = "test-key"

    response = client.get("/movies/2/trailer")

    assert response.status_code == 404
    assert "fragman" in response.json()["detail"].lower()


@patch(
    "backend.api.v1.endpoints.movies.fetch_trailer_key",
    new_callable=AsyncMock,
    return_value="xyz789",
)
@patch("backend.api.v1.endpoints.movies.get_settings")
def test_trailer_fetches_and_caches_key(mock_settings, mock_fetch, client) -> None:
    mock_settings.return_value.TMDB_API_KEY = "test-key"

    response = client.get("/movies/2/trailer")

    assert response.status_code == 200
    body = response.json()
    assert body["youtube_key"] == "xyz789"
    assert body["cached"] is False


def test_movie_detail_read_tv_show_rating_unchanged() -> None:
    detail = MovieDetailRead(
        id=1,
        title="Test Show",
        content_type="TV Show",
        letterboxd_rating=8.6,
    )
    assert detail.letterboxd_rating == 8.6


def test_movie_detail_read_movie_rating_unchanged() -> None:
    detail = MovieDetailRead(
        id=2,
        title="Test Movie",
        content_type="Movie",
        letterboxd_rating=7.4,
    )
    assert detail.letterboxd_rating == 7.4


@pytest.mark.asyncio
async def test_movie_service_search_by_overview(db_session) -> None:
    results = await movie_service.search_movies(db_session, query="Mars")

    assert len(results) == 1
    assert results[0].title == "The Martian"


@pytest.mark.asyncio
async def test_movie_service_get_movie_by_id(db_session) -> None:
    movie = await movie_service.get_movie_by_id(db_session, movie_id=1)

    assert movie is not None
    assert movie.title == "Interstellar"


@pytest.mark.asyncio
async def test_movie_service_get_movie_by_id_returns_none(db_session) -> None:
    movie = await movie_service.get_movie_by_id(db_session, movie_id=999)

    assert movie is None


@pytest.mark.asyncio
async def test_movie_service_get_reviews_for_movie(db_session) -> None:
    reviews = await movie_service.get_reviews_for_movie(db_session, movie_id=1)

    assert reviews is not None
    assert len(reviews) == 2


@pytest.mark.asyncio
async def test_movie_service_get_reviews_returns_none_for_missing_movie(db_session) -> None:
    reviews = await movie_service.get_reviews_for_movie(db_session, movie_id=999)

    assert reviews is None


@pytest.mark.asyncio
async def test_movie_service_get_recommendations_for_movie(db_session) -> None:
    from backend.services.recommender import movie_recommender

    await movie_recommender.initialize(db_session)
    recommendations = await movie_service.get_recommendations_for_movie(
        db_session, movie_id=1, limit=2
    )

    assert recommendations is not None
    assert len(recommendations) <= 2


@pytest.mark.asyncio
async def test_movie_service_get_recommendations_returns_none_for_missing_movie(db_session) -> None:
    recommendations = await movie_service.get_recommendations_for_movie(
        db_session, movie_id=999
    )

    assert recommendations is None


@pytest.mark.asyncio
async def test_movie_service_to_movie_detail_read(db_session) -> None:
    movie = await movie_service.get_movie_by_id(db_session, movie_id=1)

    detail = movie_service.to_movie_detail_read(movie)

    assert detail.id == 1
    assert detail.title == "Interstellar"
