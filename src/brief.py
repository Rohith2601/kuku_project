from __future__ import annotations

from collections import Counter

from .parser import format_time
from .schemas import Promo


def build_presentation_brief(promos: list[Promo], decisions: list[dict]) -> str:
    """Create a concise, downloadable handoff for an editor or presentation."""
    by_id = {item["clip_id"]: item for item in decisions}
    status_counts = Counter(promo.cold_viewer_status for promo in promos)
    approved = [item for item in decisions if item["editor_decision"] == "approved"]
    lines = [
        "# Cold-Viewer Promo Audit — Editorial Brief",
        "",
        "## Run summary",
        f"- Candidates reviewed: {len(promos)}",
        f"- SAFE: {status_counts.get('SAFE', 0)} | REVIEW: {status_counts.get('REVIEW', 0)} | HIGH RISK: {status_counts.get('HIGH RISK', 0)}",
        f"- Editor-approved clips: {len(approved)}",
        "",
        "## Recommended shortlist",
    ]
    shortlist = sorted(promos, key=lambda promo: (promo.cold_viewer_status != "SAFE", -promo.score, promo.spoiler_risk))[:5]
    for promo in shortlist:
        clip_id = f"{promo.episode}:{promo.start:.2f}:{promo.end:.2f}"
        decision = by_id.get(clip_id, {}).get("editor_decision", "not reviewed")
        lines.extend([
            f"### Episode {promo.episode:02} · {format_time(promo.start)}–{format_time(promo.end)}",
            f"- Appeal: {promo.score:.1f}/100 | Cold-viewer risk: {promo.spoiler_risk:.0f}/100 ({promo.cold_viewer_status}) | Decision: {decision}",
            f"- Hook: {promo.hook}",
            f"- Cliffhanger: {promo.cliffhanger}",
            f"- Why: {promo.why_it_works}",
        ])
    lines.extend(["", "## Editorial guardrail", "SAFE means no strong script-level warning, not automatic approval. Review footage before publishing."])
    return "\n".join(lines)
