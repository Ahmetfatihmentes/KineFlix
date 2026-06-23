"""AI özellik endpoint testleri: ai-review ve recommendation-reason."""

from unittest.mock import AsyncMock, patch


def test_ai_review_returns_200_for_movie_with_reviews(client) -> None:
    with patch(
        "backend.api.v1.endpoints.movies.generate_review_summary",
        new_callable=AsyncMock,
        return_value="Uzay ve zaman yolculuğunu konu alan etkileyici bir yapım.",
    ):
        response = client.get("/movies/1/ai-review")

    assert response.status_code == 200
    body = response.json()
    assert body["movie_id"] == 1
    assert body["movie_title"] == "Interstellar"
    assert body["has_reviews"] is True
    assert body["ai_review"] is not None


def test_ai_review_returns_404_for_nonexistent_movie(client) -> None:
    response = client.get("/movies/9999/ai-review")

    assert response.status_code == 404
    assert "bulunamadı" in response.json()["detail"].lower()


def test_recommendation_reason_returns_200_for_existing_movies(client) -> None:
    with patch(
        "backend.api.v1.endpoints.movies.generate_recommendation_reason",
        new_callable=AsyncMock,
        return_value="Her iki film de bilim kurgu türünde, uzay ve hayatta kalma temalarını işliyor.",
    ):
        response = client.get("/movies/1/recommendation-reason?recommended_id=2")

    assert response.status_code == 200
    body = response.json()
    assert body["source_movie"] == "Interstellar"
    assert body["recommended_movie"] == "The Martian"
    assert "reason" in body
    assert body["reason"]


def test_recommendation_reason_returns_404_when_source_missing(client) -> None:
    response = client.get("/movies/9999/recommendation-reason?recommended_id=1")

    assert response.status_code == 404
    assert "bulunamadı" in response.json()["detail"].lower()


def test_recommendation_reason_returns_404_when_recommended_missing(client) -> None:
    response = client.get("/movies/1/recommendation-reason?recommended_id=9999")

    assert response.status_code == 404
    assert "bulunamadı" in response.json()["detail"].lower()
