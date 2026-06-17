from __future__ import annotations

import argparse
import asyncio
import logging

import httpx
from sqlalchemy.dialects.postgresql import insert

from backend.core.config import get_settings
from backend.core.database import AsyncSessionLocal
from backend.models.movie import Movie


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

TMDB_BASE_URL = "https://api.themoviedb.org/3"


def _auth_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }


def _get_genre_map(client: httpx.Client, token: str) -> dict[int, str]:
    response = client.get(
        f"{TMDB_BASE_URL}/genre/movie/list",
        headers=_auth_headers(token),
        params={"language": "en-US"},
        timeout=20.0,
    )
    response.raise_for_status()
    data = response.json()
    return {genre["id"]: genre["name"] for genre in data.get("genres", [])}


def _fetch_popular_movies(
    client: httpx.Client, token: str, pages: int
) -> list[dict]:
    movies: list[dict] = []
    for page in range(1, pages + 1):
        response = client.get(
            f"{TMDB_BASE_URL}/movie/popular",
            headers=_auth_headers(token),
            params={"language": "en-US", "page": page},
            timeout=20.0,
        )
        response.raise_for_status()
        payload = response.json()
        batch = payload.get("results", [])
        logger.info("Fetched %s popular movies from page %s", len(batch), page)
        movies.extend(batch)
    return movies


def _build_movie_row(item: dict, genre_map: dict[int, str]) -> dict | None:
    tmdb_movie_id = item.get("id")
    title = item.get("title")
    if not tmdb_movie_id or not title:
        return None

    overview = item.get("overview")
    release_date = item.get("release_date") or ""
    release_year = (
        int(release_date[:4])
        if len(release_date) >= 4 and release_date[:4].isdigit()
        else None
    )
    poster_path = item.get("poster_path")
    poster_url = (
        f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
    )

    genre_ids = item.get("genre_ids", [])
    genres = (
        ", ".join(
            genre_map[genre_id] for genre_id in genre_ids if genre_id in genre_map
        )
        or None
    )

    return {
        "id": int(tmdb_movie_id),
        "title": title,
        "overview": overview,
        "genres": genres,
        "poster_url": poster_url,
        "release_year": release_year,
    }


async def seed_tmdb_popular_movies(pages: int = 1) -> int:
    settings = get_settings()
    token = settings.TMDB_READ_ACCESS_TOKEN
    if not token:
        raise RuntimeError("TMDB_READ_ACCESS_TOKEN is missing in environment/.env")

    with httpx.Client() as client:
        genre_map = _get_genre_map(client, token)
        popular_movies = _fetch_popular_movies(client, token, pages)

    movies_data: list[dict] = []
    for item in popular_movies:
        row = _build_movie_row(item, genre_map)
        if row is not None:
            movies_data.append(row)

    if not movies_data:
        logger.info("Seed completed. No movies to insert.")
        return 0

    async with AsyncSessionLocal() as db:
        stmt = insert(Movie).values(movies_data)
        stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
        result = await db.execute(stmt)
        await db.commit()
        inserted_count = result.rowcount

    skipped_count = len(movies_data) - inserted_count
    logger.info(
        "Seed completed. Inserted: %s, skipped (already exist): %s",
        inserted_count,
        skipped_count,
    )
    return inserted_count


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed popular movies from TMDB.")
    parser.add_argument("--pages", type=int, default=1, help="How many TMDB pages to fetch")
    args = parser.parse_args()

    if args.pages < 1:
        raise ValueError("--pages must be >= 1")

    asyncio.run(seed_tmdb_popular_movies(pages=args.pages))


if __name__ == "__main__":
    main()
