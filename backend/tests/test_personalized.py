"""Personalized recommendation endpoint testleri."""

import pytest


def test_personalized_with_watch_history_returns_200(client, auth_headers) -> None:
    client.post("/watch-history/", json={"movie_id": 1}, headers=auth_headers)

    response = client.get("/recommendations/personalized", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "personalized"
    assert body["source_movie_id"] == 1
    assert "recommended_movie" in body
    assert body["recommended_movie"]["title"]


def test_personalized_without_token_returns_401(client) -> None:
    response = client.get("/recommendations/personalized")

    assert response.status_code == 401
