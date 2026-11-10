from __future__ import annotations

import json
import os
from urllib import request

from .schemas import Promo


def configured() -> bool:
    return all(os.getenv(key) for key in ("PROMO_API_BASE_URL", "PROMO_API_KEY", "PROMO_MODEL"))


def review(promos: list[Promo]) -> tuple[list[Promo], str]:
    """Best-effort OpenAI-compatible review; caller retains heuristic output on any failure."""
    if not configured() or not promos:
        return promos, "heuristic"
    payload = {"model": os.environ["PROMO_MODEL"], "temperature": 0.2, "response_format": {"type": "json_object"}, "messages": [{"role": "system", "content": "Return JSON {promos:[{rank,hook,cliffhanger,why_it_works,score}]}. Score 0-100. Do not invent events."}, {"role": "user", "content": json.dumps([promo.to_dict() for promo in promos[:12]])}]}
    try:
        req = request.Request(os.environ["PROMO_API_BASE_URL"].rstrip("/") + "/chat/completions", data=json.dumps(payload).encode(), headers={"Authorization": f"Bearer {os.environ['PROMO_API_KEY']}", "Content-Type": "application/json"})
        with request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read())
        updates = json.loads(data["choices"][0]["message"]["content"])["promos"]
        by_rank = {item["rank"]: item for item in updates if isinstance(item.get("score"), (int, float))}
        for promo in promos:
            update = by_rank.get(promo.rank)
            if update:
                promo.score = round((promo.score * 0.55) + (float(update["score"]) * 0.45), 1)
                promo.hook, promo.cliffhanger = str(update.get("hook", promo.hook)), str(update.get("cliffhanger", promo.cliffhanger))
                promo.why_it_works, promo.reviewer = str(update.get("why_it_works", promo.why_it_works)), "llm+heuristic"
        return sorted(promos, key=lambda item: item.score, reverse=True), "llm+heuristic"
    except Exception:
        return promos, "heuristic (model review unavailable)"
