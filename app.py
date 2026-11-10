from __future__ import annotations

import json
import csv
from io import StringIO
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from src.parser import format_time
from src.pipeline import analyze, export
from src.reviewer import configured

load_dotenv()


def to_csv(promos) -> str:
    records = [promo.to_dict() for promo in promos]
    if not records:
        return ""
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=records[0].keys())
    writer.writeheader()
    for record in records:
        record = record.copy()
        record["score_breakdown"] = json.dumps(record["score_breakdown"])
        record["evidence"] = " | ".join(record["evidence"])
        writer.writerow(record)
    return output.getvalue()

st.set_page_config(page_title="Kuku Cold-Viewer Promo Audit", page_icon="🎬", layout="wide")
st.title("🎬 Kuku Cold-Viewer Promo Audit")
st.caption("A pre-publish guardrail for promo clips: preserve the hook, avoid obvious spoilers, and stay understandable to a first-time viewer.")

default_data = Path("I Married a Broken Soldier. He was a Duke-scripts (2)")
with st.sidebar:
    st.header("Run analysis")
    source = st.text_input("Script folder", str(default_data if default_data.exists() else ""), help="Path may be absolute or relative to this project.")
    limit = st.slider("Audit candidates", 5, 50, 30)
    use_reviewer = st.checkbox("Use optional semantic review", value=False, disabled=not configured(), help="Requires PROMO_API_BASE_URL, PROMO_API_KEY and PROMO_MODEL.")
    if not configured():
        st.caption("Optional model review is not configured; offline scoring is active.")
    run = st.button("Audit all episodes", type="primary", use_container_width=True)

if run:
    try:
        with st.spinner("Parsing scripts, scoring promo windows, and selecting diverse moments..."):
            episodes, promos, run_info = analyze(source, limit=limit, use_reviewer=use_reviewer)
            export(promos, "outputs/raw")
        st.session_state["promos"], st.session_state["info"] = promos, run_info
        st.success(f"Audited {run_info['episodes']} episodes and evaluated {run_info['candidates']:,} valid promo windows.")
    except Exception as error:
        st.error(f"Could not analyze scripts: {error}")

promos = st.session_state.get("promos", [])
if promos:
    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Audited clips", len(promos)); col2.metric("Top hook score", f"{promos[0].score:.1f}/100"); col3.metric("Review mode", st.session_state["info"]["reviewer"])
    episodes = sorted({promo.episode for promo in promos})
    selected_episodes = st.multiselect("Episodes", episodes, default=episodes)
    minimum = st.slider("Minimum score", 0, 100, 0)
    statuses = st.multiselect("Cold-viewer status", ["SAFE", "REVIEW", "HIGH RISK"], default=["SAFE", "REVIEW", "HIGH RISK"])
    visible = [promo for promo in promos if promo.episode in selected_episodes and promo.score >= minimum and promo.cold_viewer_status in statuses]
    json_data = json.dumps([promo.to_dict() for promo in visible], indent=2)
    st.download_button("Download visible recommendations (JSON)", json_data, "promo_recommendations.json", "application/json")
    st.download_button("Download visible recommendations (CSV)", to_csv(visible), "promo_recommendations.csv", "text/csv")
    for promo in visible:
        title = f"#{promo.rank} · {promo.cold_viewer_status} · Episode {promo.episode:02} · {format_time(promo.start)}–{format_time(promo.end)} ({promo.duration:.1f}s) · {promo.score:.1f}"
        with st.expander(title, expanded=promo.rank <= 3):
            st.markdown(f"**Hook:** {promo.hook}\n\n**Cliffhanger:** {promo.cliffhanger}\n\n**Why it works:** {promo.why_it_works}")
            st.caption("Evidence from the screenplay")
            for line in promo.evidence: st.code(line, language=None)
            st.json(promo.score_breakdown)
            st.markdown(f"**Cold-viewer spoiler risk:** {promo.spoiler_risk:.0f}/100")
            for note in promo.audit_notes:
                st.caption(f"Audit note: {note}")
            if promo.needs_human_review: st.warning("Low-confidence recommendation — editor review required.")
else:
    st.info("Choose the supplied script folder and click **Analyze all episodes** to generate editor-ready recommendations.")

with st.expander("Why this Problem 3 extension matters"):
    st.markdown("""
    **The problem:** a growth editor needs more than a list of dramatic moments. A clip can win a scroll but spoil the payoff, start too far into a character arc, or make no sense to a cold viewer. That risks wasting paid acquisition and undermining the promise made in an ad.

    **What the auditor checks:** a dramatic opening within the first three seconds, an unresolved ending, duration, cold-viewer clarity, later-series placement, and script-level payoff/spoiler cues. It returns a publish status—**SAFE**, **REVIEW**, or **HIGH RISK**—with the exact reasons an editor should inspect.

    **Where it can pick badly:** the tool cannot see final footage, acting, music, or irony. A word such as “wedding” can be a spoiler or merely setup. Treat it as a triage guardrail; an editor makes the final publish decision.
    """)
