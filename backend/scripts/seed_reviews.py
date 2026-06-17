from __future__ import annotations

import argparse
import asyncio
import csv
import logging
from pathlib import Path

from sqlalchemy.dialects.postgresql import insert

from backend.core.database import AsyncSessionLocal
from backend.models.review import Review


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_PATH = PROJECT_ROOT / "data" / "kineflix_reviews.csv"
BATCH_SIZE = 500
MAX_REVIEW_TEXT_LEN = 2700


def _load_rows(dataset_path: Path) -> list[dict]:
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    reviews: list[dict] = []
    seen: set[tuple[int, str, str | None]] = set()

    with dataset_path.open(encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            movie_id_raw = (row.get("lb_id") or "").strip()
            review_text = (row.get("reviewText") or "").strip()
            if not movie_id_raw or not review_text:
                continue
            if len(review_text) > MAX_REVIEW_TEXT_LEN:
                review_text = review_text[:MAX_REVIEW_TEXT_LEN]

            try:
                movie_id = int(movie_id_raw)
            except ValueError:
                continue

            sentiment = (row.get("scoreSentiment") or "").strip() or None
            critic_name = (row.get("criticName") or "").strip() or None

            dedupe_key = (movie_id, review_text, critic_name)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            reviews.append(
                {
                    "movie_id": movie_id,
                    "review_text": review_text,
                    "sentiment": sentiment,
                    "critic_name": critic_name,
                }
            )

    return reviews


async def seed_reviews(dataset_path: Path = DEFAULT_DATASET_PATH) -> int:
    reviews_data = _load_rows(dataset_path)
    inserted_total = 0

    async with AsyncSessionLocal() as db:
        for i in range(0, len(reviews_data), BATCH_SIZE):
            batch = reviews_data[i : i + BATCH_SIZE]
            stmt = insert(Review).values(batch)
            result = await db.execute(stmt)
            inserted_total += result.rowcount
            batch_number = i // BATCH_SIZE + 1
            logger.info("Batch %s eklendi: %s inceleme", batch_number, result.rowcount)
            print(f"Batch {batch_number} eklendi: {len(batch)} inceleme")

        await db.commit()

    skipped = len(reviews_data) - inserted_total
    logger.info(
        "Review seed completed. Inserted: %s, skipped (conflict): %s",
        inserted_total,
        skipped,
    )
    return inserted_total


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load Letterboxd reviews into PostgreSQL."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET_PATH,
        help="Path to kineflix_reviews.csv",
    )
    args = parser.parse_args()
    asyncio.run(seed_reviews(dataset_path=args.dataset))


if __name__ == "__main__":
    main()
