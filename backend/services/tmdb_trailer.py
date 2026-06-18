from __future__ import annotations

import httpx

from backend.models.movie import Movie

TMDB_BASE_URL = "https://api.themoviedb.org/3"


def _video_resource(content_type: str | None) -> str:
    return "tv" if content_type == "TV Show" else "movie"


def _search_resource(content_type: str | None) -> str:
    return "search/tv" if content_type == "TV Show" else "search/movie"


def _pick_trailer(videos: list[dict]) -> str | None:
    trailer = next(
        (
            video
            for video in videos
            if video.get("site") == "YouTube" and video.get("type") == "Trailer"
        ),
        None,
    )
    if trailer:
        return trailer.get("key")

    teaser = next(
        (
            video
            for video in videos
            if video.get("site") == "YouTube" and video.get("type") == "Teaser"
        ),
        None,
    )
    return teaser.get("key") if teaser else None


async def _fetch_trailer_for_tmdb_id(
    client: httpx.AsyncClient,
    *,
    tmdb_id: int,
    content_type: str | None,
    api_key: str,
) -> str | None:
    resource = _video_resource(content_type)
    for lang in ("tr-TR", "en-US"):
        response = await client.get(
            f"{TMDB_BASE_URL}/{resource}/{tmdb_id}/videos",
            params={"api_key": api_key, "language": lang},
        )
        if response.status_code != 200:
            continue
        trailer_key = _pick_trailer(response.json().get("results", []))
        if trailer_key:
            return trailer_key
    return None


async def _search_tmdb_id(
    client: httpx.AsyncClient,
    *,
    movie: Movie,
    api_key: str,
) -> int | None:
    if not movie.title:
        return None

    params: dict[str, str | int] = {
        "api_key": api_key,
        "query": movie.title,
        "language": "tr-TR",
    }
    if movie.release_year:
        params["year"] = movie.release_year

    response = await client.get(
        f"{TMDB_BASE_URL}/{_search_resource(movie.content_type)}",
        params=params,
    )
    if response.status_code != 200:
        return None

    results = response.json().get("results", [])
    if not results:
        return None

    if movie.release_year:
        for item in results:
            date = item.get("first_air_date") or item.get("release_date") or ""
            if date.startswith(str(movie.release_year)):
                return item.get("id")

    return results[0].get("id")


async def fetch_trailer_key(movie: Movie, api_key: str) -> str | None:
    tmdb_id = getattr(movie, "tmdb_id", None)
    async with httpx.AsyncClient(timeout=10.0) as client:
        if tmdb_id:
            return await _fetch_trailer_for_tmdb_id(
                client,
                tmdb_id=int(tmdb_id),
                content_type=movie.content_type,
                api_key=api_key,
            )

        trailer_key = await _fetch_trailer_for_tmdb_id(
            client,
            tmdb_id=movie.id,
            content_type=movie.content_type,
            api_key=api_key,
        )
        if trailer_key:
            return trailer_key

        resolved_id = await _search_tmdb_id(client, movie=movie, api_key=api_key)
        if not resolved_id:
            return None

        return await _fetch_trailer_for_tmdb_id(
            client,
            tmdb_id=resolved_id,
            content_type=movie.content_type,
            api_key=api_key,
        )
