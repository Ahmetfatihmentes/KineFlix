from __future__ import annotations

import argparse
import asyncio
import csv
import logging
import math
from pathlib import Path

from sqlalchemy import text

from backend.core.database import AsyncSessionLocal


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_PATH = PROJECT_ROOT / "data" / "kineflix_final_dataset.csv"
BATCH_SIZE = 1000

UPDATE_BATCH_SQL = text(
    """
    UPDATE movies AS m
    SET
        overview_tr = CASE
            WHEN v.overview_tr IS NOT NULL AND v.overview_tr <> '' THEN v.overview_tr
            ELSE m.overview_tr
        END,
        tagline_tr = CASE
            WHEN v.tagline_tr IS NOT NULL AND v.tagline_tr <> '' THEN v.tagline_tr
            ELSE m.tagline_tr
        END
    FROM unnest(
        CAST(:ids AS int[]),
        CAST(:overviews AS text[]),
        CAST(:taglines AS text[])
    ) AS v(id, overview_tr, tagline_tr)
    WHERE m.id = v.id
    """
)


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    if not cleaned or cleaned.lower() == "nan":
        return None
    return cleaned


def _load_rows(dataset_path: Path) -> list[dict]:
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    rows: list[dict] = []
    with dataset_path.open(encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            movie_id_raw = (row.get("id") or "").strip()
            if not movie_id_raw:
                continue

            try:
                movie_id = int(movie_id_raw)
            except ValueError:
                continue

            overview_tr = _clean_text(row.get("description_tr"))
            tagline_tr = _clean_text(row.get("tagline_tr"))
            if overview_tr is None and tagline_tr is None:
                continue

            rows.append(
                {
                    "id": movie_id,
                    "overview_tr": overview_tr,
                    "tagline_tr": tagline_tr[:512] if tagline_tr else None,
                }
            )

    return rows


async def update_translations(dataset_path: Path = DEFAULT_DATASET_PATH) -> int:
    translation_rows = _load_rows(dataset_path)
    if not translation_rows:
        logger.warning("No translation rows to update.")
        print("Güncellenecek çeviri kaydı bulunamadı.")
        return 0

    updated_total = 0
    async with AsyncSessionLocal() as db:
        for i in range(0, len(translation_rows), BATCH_SIZE):
            batch = translation_rows[i : i + BATCH_SIZE]
            ids = [row["id"] for row in batch]
            overviews = [row["overview_tr"] or "" for row in batch]
            taglines = [row["tagline_tr"] or "" for row in batch]
            result = await db.execute(
                UPDATE_BATCH_SQL,
                {"ids": ids, "overviews": overviews, "taglines": taglines},
            )
            batch_updated = result.rowcount or 0
            updated_total += batch_updated
            batch_number = i // BATCH_SIZE + 1
            logger.info("Batch %s güncellendi: %s kayıt", batch_number, batch_updated)
            print(f"Batch {batch_number} güncellendi: {batch_updated} kayıt")

        await db.commit()

    logger.info("Translation update completed. Updated: %s", updated_total)
    print(f"{updated_total} kayıt güncellendi.")
    return updated_total


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update Turkish overview and tagline fields from kineflix_final_dataset.csv."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET_PATH,
        help="Path to kineflix_final_dataset.csv",
    )
    args = parser.parse_args()
    asyncio.run(update_translations(dataset_path=args.dataset))


if __name__ == "__main__":
    main()
