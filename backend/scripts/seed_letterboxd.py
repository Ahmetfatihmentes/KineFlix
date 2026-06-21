from __future__ import annotations

import argparse
import asyncio
import csv
import logging
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert

from backend.core.database import AsyncSessionLocal
from backend.models.movie import Movie
from backend.models.movie_vector import MovieVector
from backend.models.review import Review
from backend.models.watch_history import WatchHistory
from backend.models.watchlist import Watchlist
from backend.services.recommender import TFIDF_CACHE_PATH


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_PATH = PROJECT_ROOT / "data" / "kineflix_final_dataset.csv"
DEFAULT_POSTERS_PATH = PROJECT_ROOT / "data" / "kineflix_posters.csv"
BATCH_SIZE = 500


def _parse_release_year(date_value: str | None) -> int | None:
    if not date_value:
        return None
    year_part = date_value.strip()[:4]
    if len(year_part) == 4 and year_part.isdigit():
        return int(year_part)
    return None


def _parse_int(value: str | None) -> int | None:
    if value is None or not str(value).strip():
        return None
    try:
        return int(float(str(value).strip()))
    except ValueError:
        return None


def _parse_float(value: str | None) -> float | None:
    if value is None or not str(value).strip():
        return None
    try:
        return float(str(value).strip())
    except ValueError:
        return None


def _clean_translation(value: str | None, max_len: int | None = None) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    if not cleaned or cleaned.lower() == "nan":
        return None
    if max_len is not None:
        return cleaned[:max_len]
    return cleaned


def _load_posters(posters_path: Path) -> dict[int, str]:
    if not posters_path.exists():
        logger.warning("Poster dataset not found: %s", posters_path)
        return {}

    posters: dict[int, str] = {}
    with posters_path.open(encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            movie_id_raw = (row.get("id") or "").strip()
            link = (row.get("link") or "").strip()
            if not movie_id_raw or not link:
                continue
            try:
                posters[int(movie_id_raw)] = link[:512]
            except ValueError:
                continue
    return posters


def _load_rows(dataset_path: Path, posters_path: Path = DEFAULT_POSTERS_PATH) -> list[dict]:
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    movies_by_id: dict[int, dict] = {}
    posters_by_id = _load_posters(posters_path)
    with dataset_path.open(encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            movie_id = row.get("id")
            title = (row.get("name") or "").strip()
            if not movie_id or not title:
                continue

            try:
                parsed_id = int(movie_id)
            except ValueError:
                continue

            overview = (row.get("description") or "").strip() or None
            overview_tr = _clean_translation(row.get("description_tr"))
            tagline = (row.get("tagline") or "").strip()[:512] or None
            tagline_tr = _clean_translation(row.get("tagline_tr"), max_len=512)
            content_type = (row.get("content_type") or "").strip() or "Movie"
            movies_by_id[parsed_id] = {
                "id": parsed_id,
                "title": title[:255],
                "overview": overview,
                "overview_tr": overview_tr,
                "genres": (row.get("genres") or "").strip()[:255] or None,
                "themes": (row.get("themes") or "").strip() or None,
                "poster_url": posters_by_id.get(parsed_id),
                "release_year": _parse_release_year(row.get("date")),
                "actors": (row.get("actors") or "").strip() or None,
                "director": (row.get("director") or "").strip()[:255] or None,
                "tagline": tagline,
                "tagline_tr": tagline_tr,
                "runtime": _parse_int(row.get("minute")),
                "letterboxd_rating": _parse_float(row.get("rating")),
                "audience_score": _parse_float(row.get("audienceScore")),
                "tomato_meter": _parse_float(row.get("tomatoMeter")),
                "total_reviews": _parse_int(row.get("total_reviews")),
                "positive_pct": _parse_float(row.get("positive_pct")),
                "content_type": content_type[:50],
            }

    return list(movies_by_id.values())


async def seed_letterboxd_dataset(
    dataset_path: Path = DEFAULT_DATASET_PATH,
    posters_path: Path = DEFAULT_POSTERS_PATH,
) -> int:
    movies_data = _load_rows(dataset_path, posters_path=posters_path)
    with_posters = sum(1 for movie in movies_data if movie.get("poster_url"))
    logger.info("Loaded %s movies, %s with poster URLs", len(movies_data), with_posters)

    if TFIDF_CACHE_PATH.exists():
        TFIDF_CACHE_PATH.unlink()
        logger.info("Removed stale TF-IDF cache: %s", TFIDF_CACHE_PATH)

    async with AsyncSessionLocal() as db:
        await db.execute(delete(WatchHistory))
        await db.execute(delete(Watchlist))
        await db.execute(delete(MovieVector))
        await db.execute(delete(Review))
        await db.execute(delete(Movie))

        for i in range(0, len(movies_data), BATCH_SIZE):
            batch = movies_data[i : i + BATCH_SIZE]
            stmt = insert(Movie).values(batch)
            await db.execute(stmt)
            batch_number = i // BATCH_SIZE + 1
            logger.info("Batch %s eklendi: %s film", batch_number, len(batch))
            print(f"Batch {batch_number} eklendi: {len(batch)} film")

        await db.commit()

    logger.info("Letterboxd seed completed. Loaded movies: %s", len(movies_data))
    return len(movies_data)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load Letterboxd dataset into PostgreSQL movies table."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET_PATH,
        help="Path to kineflix_final_dataset.csv",
    )
    parser.add_argument(
        "--posters",
        type=Path,
        default=DEFAULT_POSTERS_PATH,
        help="Path to kineflix_posters.csv",
    )
    args = parser.parse_args()
    asyncio.run(
        seed_letterboxd_dataset(dataset_path=args.dataset, posters_path=args.posters)
    )


if __name__ == "__main__":
    main()
