from __future__ import annotations

import csv
import json
from collections import Counter
from io import StringIO
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from src.brief import build_presentation_brief
from src.parser import format_time
from src.pipeline import analyze, analyze_uploads, export
from src.reviewer import configured

load_dotenv()
st.set_page_config(page_title="Kuku | Cold-Viewer Promo Audit", page_icon="🎬", layout="wide", initial_sidebar_state="expanded")


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
        for field in ("evidence", "audit_notes", "context_before", "context_after"):
            record[field] = " | ".join(record[field])
        writer.writerow(record)
    return output.getvalue()


def decisions_csv() -> str:
    records = st.session_state.get("decisions", [])
    if not records:
        return ""
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)
    return output.getvalue()


def promo_id(promo) -> str:
    return f"{promo.episode}:{promo.start:.2f}:{promo.end:.2f}"


def record_decision(promo, decision: str, note: str) -> None:
    clip_id = promo_id(promo)
    decisions = [item for item in st.session_state.get("decisions", []) if item["clip_id"] != clip_id]
    decisions.append({
        "clip_id": clip_id,
        "episode": promo.episode,
        "start": format_time(promo.start),
        "end": format_time(promo.end),
        "appeal_score": promo.score,
        "spoiler_risk": promo.spoiler_risk,
        "audit_status": promo.cold_viewer_status,
        "editor_decision": decision,
        "editor_note": note.strip(),
    })
    st.session_state["decisions"] = decisions


def status_message(promo) -> tuple[str, str]:
    if promo.cold_viewer_status == "SAFE":
        return "success", "Low script-level risk. Confirm the visual cut before publishing."
    if promo.cold_viewer_status == "HIGH RISK":
        return "error", "Potential payoff or context problem. Do not publish without a senior-editor review."
    return "warning", "Promising candidate, but inspect the surrounding footage and the audit notes."


def render_promo_card(promo) -> None:
    decision_map = {item["clip_id"]: item for item in st.session_state.get("decisions", [])}
    current_decision = decision_map.get(promo_id(promo), {}).get("editor_decision", "not reviewed")
    label = f"Episode {promo.episode:02}  |  {format_time(promo.start)} - {format_time(promo.end)}  |  appeal {promo.score:.1f}  |  risk {promo.spoiler_risk:.0f}"
    with st.expander(label, expanded=promo.rank <= 2):
        left, right = st.columns([2, 1])
        with left:
            st.markdown(f"**Hook**  \\n+{promo.hook}")
            st.markdown(f"**Cliffhanger**  \\n+{promo.cliffhanger}")
            st.caption(promo.why_it_works)
        with right:
            st.metric("Promo appeal", f"{promo.score:.1f}/100")
            st.metric("Cold-viewer risk", f"{promo.spoiler_risk:.0f}/100")
            st.caption(f"Current decision: **{current_decision.replace('_', ' ')}**")

        message_type, message = status_message(promo)
        getattr(st, message_type)(f"{promo.cold_viewer_status}: {message}")
        detail, context = st.tabs(["Audit evidence", "Context window"])
        with detail:
            for note in promo.audit_notes:
                st.write(f"- {note}")
            with st.popover("Show score breakdown"):
                st.json(promo.score_breakdown)
        with context:
            st.caption("Ten seconds before and after the candidate; verify the final footage before publishing.")
            if promo.context_before:
                st.markdown("**Before**")
                for line in promo.context_before:
                    st.write(f"← {line}")
            else:
                st.caption("No preceding scripted beat in the ten-second window.")
            if promo.context_after:
                st.markdown("**After**")
                for line in promo.context_after:
                    st.write(f"→ {line}")
            else:
                st.caption("No following scripted beat in the ten-second window.")

        note = st.text_input("Editor note", key=f"note-{promo_id(promo)}", placeholder="Optional: why this should be used or rejected")
        approve, reject, rewrite = st.columns(3)
        if approve.button("Approve", key=f"approve-{promo_id(promo)}", use_container_width=True):
            record_decision(promo, "approved", note)
            st.success("Saved as approved.")
        if reject.button("Reject", key=f"reject-{promo_id(promo)}", use_container_width=True):
            record_decision(promo, "rejected", note)
            st.info("Saved as rejected.")
        if rewrite.button("Needs rewrite", key=f"rewrite-{promo_id(promo)}", use_container_width=True):
            record_decision(promo, "needs_rewrite", note)
            st.warning("Saved for a new promo cut.")


if "promos" not in st.session_state:
    st.session_state.promos = []
if "decisions" not in st.session_state:
    st.session_state.decisions = []

default_private_data = Path("I Married a Broken Soldier. He was a Duke-scripts (2)")
demo_data = Path("demo_data")

with st.sidebar:
    st.header("1. Load a screenplay")
    st.caption("Private uploads are analyzed in memory. They are not committed to GitHub.")
    with st.form("analysis_controls", border=False):
        source = st.text_input("Local script folder", str(default_private_data if default_private_data.exists() else demo_data))
        uploads = st.file_uploader("Or upload screenplay .txt files", type=["txt"], accept_multiple_files=True)
        limit = st.slider("Candidates to review", 5, 50, 20)
        use_reviewer = st.checkbox("Use optional semantic review", value=False, disabled=not configured())
        run = st.form_submit_button("Run promo audit", type="primary", use_container_width=True)
    if not configured():
        st.caption("Offline, rules-based review is active. Model review is optional.")
    st.divider()
    st.header("2. Presentation flow")
    st.caption("Show the run summary, expand the first SAFE candidate, inspect its context, approve it, then download the editorial brief.")

if run:
    try:
        with st.spinner("Parsing scripts and auditing candidate promo windows..."):
            if uploads:
                episodes, promos, info = analyze_uploads(uploads, limit=limit, use_reviewer=use_reviewer)
            else:
                episodes, promos, info = analyze(source, limit=limit, use_reviewer=use_reviewer)
            export(promos, "outputs/raw")
        st.session_state.promos = promos
        st.session_state.info = info
        st.session_state.decisions = []
        st.success(f"Audit complete: {info['episodes']} episode(s), {info['candidates']:,} valid windows, {len(promos)} editorial candidates.")
    except Exception as error:
        st.error(f"Could not run the audit: {error}")

st.title("Kuku | Cold-Viewer Promo Audit")
st.caption("Turn a screenplay into an editor-ready promo shortlist: high curiosity, low accidental spoiler risk, and visible evidence for every recommendation.")

promos = st.session_state.promos
if not promos:
    st.info("Start with the included public demo or upload your own timestamped screenplay files from the sidebar.")
    st.markdown("**What this demonstrates:** a growth editor can triage dozens of candidate clips into publish, inspect, or rewrite decisions—without treating a keyword score as an automatic answer.")
else:
    counts = Counter(promo.cold_viewer_status for promo in promos)
    safe = [promo for promo in promos if promo.cold_viewer_status == "SAFE"]
    best_safe = max(safe, key=lambda promo: promo.score) if safe else min(promos, key=lambda promo: promo.spoiler_risk)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Candidates", len(promos))
    m2.metric("SAFE clips", counts.get("SAFE", 0))
    m3.metric("Needs review", counts.get("REVIEW", 0) + counts.get("HIGH RISK", 0))
    m4.metric("Editor decisions", len(st.session_state.decisions))

    with st.container(border=True):
        st.subheader("Recommended presentation candidate")
        st.markdown(f"**Episode {best_safe.episode:02} · {format_time(best_safe.start)}–{format_time(best_safe.end)}**  \\n+Appeal **{best_safe.score:.1f}/100** · Cold-viewer risk **{best_safe.spoiler_risk:.0f}/100** · **{best_safe.cold_viewer_status}**")
        st.caption("This is the strongest lower-risk candidate. Expand it below to show the evidence and editor workflow.")

    shortlist_tab, risk_tab, decisions_tab, method_tab = st.tabs(["Shortlist", "Review queue", "Decision log", "How to present it"])
    with shortlist_tab:
        filters = st.columns([2, 1, 1])
        episode_options = sorted({promo.episode for promo in promos})
        selected_episodes = filters[0].multiselect("Episodes", episode_options, default=episode_options)
        minimum_appeal = filters[1].slider("Min appeal", 0, 100, 0)
        sort_by = filters[2].selectbox("Sort by", ["Promo appeal", "Lowest risk"])
        visible = [promo for promo in promos if promo.episode in selected_episodes and promo.score >= minimum_appeal]
        visible.sort(key=(lambda promo: promo.spoiler_risk) if sort_by == "Lowest risk" else (lambda promo: promo.score), reverse=sort_by == "Promo appeal")
        st.caption(f"Showing {len(visible)} candidate(s). Appeal and risk are deliberately separate signals.")
        for promo in visible:
            render_promo_card(promo)

    with risk_tab:
        st.warning("These clips need deliberate editorial attention; they may still be useful, but only after footage review or a revised cut.")
        review_queue = [promo for promo in promos if promo.cold_viewer_status != "SAFE"]
        review_queue.sort(key=lambda promo: (-promo.spoiler_risk, -promo.score))
        if review_queue:
            for promo in review_queue:
                render_promo_card(promo)
        else:
            st.success("No clips were flagged in this run.")

    with decisions_tab:
        decisions = st.session_state.decisions
        if decisions:
            st.dataframe(decisions, use_container_width=True, hide_index=True)
            st.download_button("Download editor decisions (CSV)", decisions_csv(), "editor_decisions.csv", "text/csv", use_container_width=True)
        else:
            st.info("Open a clip and use Approve, Reject, or Needs rewrite. Decisions stay in this browser session and can be downloaded as CSV.")
        brief = build_presentation_brief(promos, decisions)
        st.download_button("Download presentation brief (Markdown)", brief, "editorial_brief.md", "text/markdown", type="primary", use_container_width=True)
        st.download_button("Download full audit (JSON)", json.dumps([promo.to_dict() for promo in promos], indent=2), "promo_audit.json", "application/json", use_container_width=True)
        st.download_button("Download full audit (CSV)", to_csv(promos), "promo_audit.csv", "text/csv", use_container_width=True)

    with method_tab:
        st.markdown("""
        **What is automated:** timestamp parsing, valid 20–60 second windows, hook and cliffhanger signals, duplicate suppression, and script-level spoiler/context warnings.

        **What remains human:** whether the footage performs visually, whether a line spoils a payoff in context, and whether the edit represents the show honestly.

        **Presentation tip:** do not claim the model replaces editors. Show that it narrows a large screenplay pack into an auditable decision queue and captures the editor's final judgment for future evaluation.
        """)
