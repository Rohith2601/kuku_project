from __future__ import annotations

from .schemas import Episode, Promo
from .scoring import audit_cold_viewer_risk, score_window


def generate_candidates(episode: Episode, rules: dict) -> list[Promo]:
    beats = episode.beats
    candidates: list[Promo] = []
    min_duration, max_duration = rules["min_duration_seconds"], rules["max_duration_seconds"]
    for index, anchor in enumerate(beats):
        if anchor.kind not in {"dialogue", "action"}:
            continue
        start = anchor.start
        possible_ends = [beat.end for beat in beats[index:] if min_duration <= beat.end - start <= max_duration]
        for end in possible_ends[-3:]:
            score, breakdown, hook, cliff, why, evidence = score_window(beats, start, end, rules)
            risk, status, notes = audit_cold_viewer_risk(beats, start, end, episode.number)
            before = [beat.text for beat in beats if start - 10 <= beat.start < start][-2:]
            after = [beat.text for beat in beats if end < beat.end <= end + 10][:2]
            candidates.append(Promo(0, episode.number, start, end, round(end - start, 2), score, hook, cliff, why, breakdown, evidence, score < rules["min_score_for_editor_review"], spoiler_risk=risk, cold_viewer_status=status, audit_notes=notes, context_before=before, context_after=after))
    return candidates


def _overlap(a: Promo, b: Promo) -> float:
    if a.episode != b.episode:
        return 0
    intersection = max(0, min(a.end, b.end) - max(a.start, b.start))
    return intersection / min(a.duration, b.duration)


def select_diverse(candidates: list[Promo], limit: int = 30) -> list[Promo]:
    selected: list[Promo] = []
    # Appeal and risk are independent editorial signals; do not hide a compelling risky clip.
    for candidate in sorted(candidates, key=lambda item: item.score, reverse=True):
        if any(_overlap(candidate, existing) > 0.55 for existing in selected):
            continue
        selected.append(candidate)
        if len(selected) == limit:
            break
    for rank, promo in enumerate(selected, 1):
        promo.rank = rank
    return selected
