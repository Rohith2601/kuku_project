"""Print editorial quality metrics for a private manually-labelled promo review set."""
import json
from pathlib import Path

from src.evaluation import evaluate, load_labels
from src.schemas import Promo


if __name__ == "__main__":
    labels = load_labels("eval/labels.local.json")
    records = json.loads(Path("outputs/raw/promo_recommendations.json").read_text(encoding="utf-8"))
    promos = [Promo(**record) for record in records]
    print(json.dumps(evaluate(promos, labels), indent=2))
