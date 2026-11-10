from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

from .candidates import generate_candidates, select_diverse
from .parser import parse_directory, parse_text
from .reviewer import review
from .scoring import load_rules


def analyze(directory: str | Path, rules_path: str | Path = "config/scoring_rules.json", limit: int = 30, use_reviewer: bool = False):
    rules = load_rules(rules_path)
    episodes = parse_directory(directory)
    candidates = [promo for episode in episodes for promo in generate_candidates(episode, rules)]
    promos = select_diverse(candidates, limit)
    reviewer_name = "heuristic"
    if use_reviewer:
        promos, reviewer_name = review(promos)
        for rank, promo in enumerate(promos, 1):
            promo.rank = rank
    return episodes, promos, {"episodes": len(episodes), "candidates": len(candidates), "reviewer": reviewer_name}


def analyze_uploads(files, rules_path: str | Path = "config/scoring_rules.json", limit: int = 30, use_reviewer: bool = False):
    """Analyze Streamlit UploadedFile objects without retaining the private input pack."""
    rules = load_rules(rules_path)
    episodes = [parse_text(upload.getvalue().decode("utf-8", errors="replace"), upload.name) for upload in files]
    candidates = [promo for episode in episodes for promo in generate_candidates(episode, rules)]
    promos = select_diverse(candidates, limit)
    reviewer_name = "heuristic"
    if use_reviewer:
        promos, reviewer_name = review(promos)
        for rank, promo in enumerate(promos, 1):
            promo.rank = rank
    return episodes, promos, {"episodes": len(episodes), "candidates": len(candidates), "reviewer": reviewer_name}


def export(promos, directory: str | Path) -> tuple[Path, Path]:
    directory = Path(directory); directory.mkdir(parents=True, exist_ok=True)
    json_path, csv_path = directory / "promo_recommendations.json", directory / "promo_recommendations.csv"
    records = [promo.to_dict() for promo in promos]
    json_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    if records:
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=records[0].keys()); writer.writeheader()
            for record in records:
                record = record.copy(); record["score_breakdown"] = json.dumps(record["score_breakdown"]); record["evidence"] = " | ".join(record["evidence"]); writer.writerow(record)
    return json_path, csv_path
