from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Beat:
    episode: int
    scene: int
    kind: str
    start: float
    end: float
    text: str
    speaker: str | None = None


@dataclass
class Episode:
    number: int
    logline: str
    continuity_notes: str
    source_file: str
    beats: list[Beat] = field(default_factory=list)


@dataclass
class Promo:
    rank: int
    episode: int
    start: float
    end: float
    duration: float
    score: float
    hook: str
    cliffhanger: str
    why_it_works: str
    score_breakdown: dict[str, float]
    evidence: list[str]
    needs_human_review: bool
    reviewer: str = "heuristic"
    spoiler_risk: float = 0.0
    cold_viewer_status: str = "REVIEW"
    audit_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
