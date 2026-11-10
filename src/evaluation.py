from __future__ import annotations

import json
from pathlib import Path

from .schemas import Promo


def promo_key(episode: int, start: float, end: float) -> str:
    return f"{episode}:{start:.2f}:{end:.2f}"


def load_labels(path: str | Path) -> dict[str, dict]:
    """Load private editor labels keyed by episode/start/end; no screenplay text is required."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {promo_key(item["episode"], item["start"], item["end"]): item for item in data["labels"]}


def evaluate(promos: list[Promo], labels: dict[str, dict], k: int = 5) -> dict[str, float | int]:
    reviewed = [(promo, labels[promo_key(promo.episode, promo.start, promo.end)]) for promo in promos if promo_key(promo.episode, promo.start, promo.end) in labels]
    top_k = reviewed[:k]
    good = sum(item[1].get("verdict") == "good" for item in reviewed)
    safe = sum(item[1].get("spoiler_verdict") == "safe" for item in reviewed)
    return {
        "reviewed": len(reviewed),
        "precision_at_k": round(sum(item[1].get("verdict") == "good" for item in top_k) / len(top_k), 3) if top_k else 0.0,
        "good_rate": round(good / len(reviewed), 3) if reviewed else 0.0,
        "spoiler_safety_rate": round(safe / len(reviewed), 3) if reviewed else 0.0,
    }
