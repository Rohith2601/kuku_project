from __future__ import annotations

import json
import re
from pathlib import Path

from .schemas import Beat


def load_rules(path: str | Path = "config/scoring_rules.json") -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _hits(text: str, cues: list[str]) -> list[str]:
    lower = text.lower()
    matches: list[str] = []
    for cue in cues:
        if cue == "?":
            if "?" in text:
                matches.append(cue)
        elif re.search(rf"(?<!\w){re.escape(cue.lower())}(?!\w)", lower):
            matches.append(cue)
    return matches


def _scale(hits: list[str], cap: int = 3) -> float:
    return min(len(hits), cap) / cap * 100


def score_window(beats: list[Beat], start: float, end: float, rules: dict) -> tuple[float, dict[str, float], str, str, str, list[str]]:
    clip = [beat for beat in beats if beat.end > start and beat.start < end]
    hook_beats = [beat for beat in clip if beat.start < start + 3]
    final_beats = [beat for beat in clip if beat.end >= end - 6]
    hook_text = " ".join(beat.text for beat in hook_beats)
    final_text = " ".join(beat.text for beat in final_beats)
    all_text = " ".join(beat.text for beat in clip)
    hook_hits = _hits(hook_text, rules["hook_cues"])
    cliff_hits = _hits(final_text, rules["cliffhanger_cues"])
    context_hits = _hits(all_text, rules["context_cues"])
    hook = _scale(hook_hits) + (15 if any(beat.kind == "action" for beat in hook_beats) else 0)
    cliff = _scale(cliff_hits) + (12 if "?" in final_text else 0)
    clarity = min(100, _scale(context_hits) + (25 if len(clip) >= 4 else 0) + (15 if any(beat.speaker for beat in clip) else 0))
    duration = end - start
    duration_fit = max(0, 100 - abs(duration - 42) * 2)
    breakdown = {"hook": round(min(100, hook), 1), "cliffhanger": round(min(100, cliff), 1), "standalone_clarity": round(clarity, 1), "duration_fit": round(duration_fit, 1)}
    weights = rules["weights"]
    score = sum(breakdown[key] * weights[{"standalone_clarity": "clarity", "duration_fit": "duration"}.get(key, key)] for key in breakdown)
    hook_line = hook_beats[0].text if hook_beats else "Opening action establishes immediate conflict."
    cliff_line = final_beats[-1].text if final_beats else "The ending leaves the conflict unresolved."
    opening_reason = f"opening cue(s): {', '.join(hook_hits[:2])}" if hook_hits else ("a visible action beat" if any(beat.kind == "action" for beat in hook_beats) else "an immediate confrontation")
    ending_reason = f"ending cue(s): {', '.join(cliff_hits[:2])}" if cliff_hits else ("an open question" if "?" in final_text else "an unresolved beat")
    why = f"The clip opens with {opening_reason} and closes on {ending_reason}; review its surrounding context before publishing."
    evidence = [f"HOOK: {hook_line}", f"CLIFFHANGER: {cliff_line}"]
    return round(score, 1), breakdown, hook_line, cliff_line, why, evidence


def audit_cold_viewer_risk(beats: list[Beat], start: float, end: float, episode_number: int) -> tuple[float, str, list[str]]:
    """Flag likely plot-payoff and context risks without pretending to know final footage."""
    clip = [beat for beat in beats if beat.end > start and beat.start < end]
    text = " ".join(beat.text for beat in clip).lower()
    ending = " ".join(beat.text for beat in clip if beat.end >= end - 6).lower()
    notes: list[str] = []
    risk = 0.0
    payoff_terms = ["the truth", "confess", "confessed", "revealed", "identity", "killer", "dies", "dead", "wedding", "married", "divorce", "pregnant", "is my father"]
    found = [term for term in payoff_terms if term in text]
    if found:
        risk += min(45, 12 * len(found))
        notes.append(f"Possible payoff/spoiler cue: {', '.join(found[:3])}.")
    if episode_number >= 10:
        risk += 15
        notes.append("Later-series moment: verify it does not reveal a character arc or outcome.")
    if not any(mark in ending for mark in ("?", "don't", "stop", "cut to black", "what", "why")):
        risk += 18
        notes.append("Ending may resolve rather than defer the central tension.")
    speakers = {beat.speaker for beat in clip if beat.speaker}
    if len(speakers) <= 1:
        risk += 8
        notes.append("Limited character context; check that a new viewer can identify the conflict.")
    risk = min(100, risk)
    status = "SAFE" if risk < 25 else "REVIEW" if risk < 55 else "HIGH RISK"
    if not notes:
        notes.append("No strong script-level spoiler or cold-viewer risk detected; visual/editor review still required.")
    return risk, status, notes
