"""Batch entry point: analyze the supplied input pack and write raw editor handoff files."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.pipeline import analyze, export


if __name__ == "__main__":
    source = Path("I Married a Broken Soldier. He was a Duke-scripts (2)")
    episodes, promos, info = analyze(source, limit=30, use_reviewer=False)
    json_path, csv_path = export(promos, "outputs/raw")
    print(f"Analyzed {len(episodes)} episodes / {info['candidates']} candidate windows.")
    print(f"Wrote {json_path} and {csv_path}")
