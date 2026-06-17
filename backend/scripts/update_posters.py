from __future__ import annotations

import argparse
import asyncio
import csv
import logging
from pathlib import Path

from sqlalchemy import text

from backend.core.database import AsyncSessionLocal


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_PATH = PROJECT_ROOT / "data" / "kineflix_posters.csv"
BATCH_SIZE = 1000

UPDATE_BATCH_SQL = text(
    """
    UPDATE movies AS m
    SET poster_url = v.link
    FROM unnest(CAST(:ids AS int[]), CAST(:links AS text[])) AS v(id, link)
    WHERE m.id = v.id
    """
)


def _load_rows(dataset_path: Path) -> list[dict]:
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    rows: list[dict] = []
    with dataset_path.open(encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            movie_id_raw = (row.get("id") or "").strip()
            link = (row.get("link") or "").strip()
            if not movie_id_raw or not link:
                continue

            try:
                movie_id = int(movie_id_raw)
            except ValueError:
                continue

            rows.append({"b_id": movie_id, "b_poster_url": link[:512]})

    return rows


async def update_posters(dataset_path: Path = DEFAULT_DATASET_PATH) -> int:
    poster_rows = _load_rows(dataset_path)
    if not poster_rows:
        logger.warning("No poster rows to update.")
        print("Güncellenecek poster kaydı bulunamadı.")
        return 0

    updated_total = 0
    async with AsyncSessionLocal() as db:
        for i in range(0, len(poster_rows), BATCH_SIZE):
            batch = poster_rows[i : i + BATCH_SIZE]
            ids = [row["b_id"] for row in batch]
            links = [row["b_poster_url"] for row in batch]
            result = await db.execute(UPDATE_BATCH_SQL, {"ids": ids, "links": links})
            batch_updated = result.rowcount or 0
            updated_total += batch_updated
            batch_number = i // BATCH_SIZE + 1
            logger.info("Batch %s güncellendi: %s film", batch_number, batch_updated)
            print(f"Batch {batch_number} güncellendi: {batch_updated} film")

        await db.commit()

    logger.info("Poster update completed. Updated: %s", updated_total)
    print(f"Tamamlandı: {updated_total} film güncellendi.")
    return updated_total


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update movie poster_url values from kineflix_posters.csv."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET_PATH,
        help="Path to kineflix_posters.csv",
    )
    args = parser.parse_args()
    asyncio.run(update_posters(dataset_path=args.dataset))


if __name__ == "__main__":
    main()
