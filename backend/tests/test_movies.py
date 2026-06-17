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
