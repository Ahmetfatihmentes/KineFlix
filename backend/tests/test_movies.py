from backend.schemas.movie import MovieDetailRead


def test_search_movies_returns_matching_titles(client) -> None:
    response = client.get("/movies/search", params={"query": "Inter"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Interstellar"


def test_recommendations_returns_related_movies(client) -> None:
    response = client.get("/movies/1/recommendations")

    assert response.status_code == 200
    body = response.json()
    assert len(body) > 0
    titles = {item["title"] for item in body}
    assert "The Martian" in titles or "Gravity" in titles


def test_movie_detail_read_converts_tv_show_rating_to_five_scale() -> None:
    detail = MovieDetailRead(
        id=1,
        title="Test Show",
        content_type="TV Show",
        letterboxd_rating=8.6,
    )
    assert detail.letterboxd_rating == 4.3


def test_movie_detail_read_keeps_movie_rating_on_five_scale() -> None:
    detail = MovieDetailRead(
        id=2,
        title="Test Movie",
        content_type="Movie",
        letterboxd_rating=4.5,
    )
    assert detail.letterboxd_rating == 4.5
