"""CSV storage with dedupe by handle."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
CSV_PATH = DATA_DIR / "prospects.csv"

FIELDS = [
    "handle", "full_name", "followers", "bio", "store_url", "platform",
    "language", "score", "score_reasons", "dm", "video_angles", "scraped_at",
]


def _ensure_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not CSV_PATH.exists():
        with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=FIELDS).writeheader()


def existing_handles() -> set[str]:
    _ensure_file()
    with CSV_PATH.open("r", encoding="utf-8") as f:
        return {row["handle"] for row in csv.DictReader(f) if row.get("handle")}


def append_prospects(rows: list[dict[str, Any]]) -> int:
    """Append rows, skipping handles already present. Returns number written."""
    _ensure_file()
    seen = existing_handles()
    new = [r for r in rows if r.get("handle") and r["handle"] not in seen]
    if not new:
        return 0
    with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        for r in new:
            w.writerow(r)
    return len(new)


def csv_path_str() -> str:
    return str(CSV_PATH)
