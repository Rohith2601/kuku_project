# Kuku Cold-Viewer Promo Audit

**Problem chosen:** Problem 3 - Find your own problem

**Live app:** [rohith2601-kuku-project-app-kknezy.streamlit.app](https://rohith2601-kuku-project-app-kknezy.streamlit.app/)
**Repository:** [github.com/Rohith2601/kuku_project](https://github.com/Rohith2601/kuku_project)

## Problem

I built a pre-publish audit for microdrama promos. The user is a growth/promo editor deciding whether a candidate clip should be published, inspected, or replaced. A dramatic clip can still fail as acquisition creative if it spoils a payoff, assumes knowledge of a later character arc, or makes no sense to someone who has never seen the show.

This matters because discovery is feed-led: a Kantar/ShareChat/Moj study reported that 77% of viewers discover microdrama while scrolling, and 27% named curiosity about what happens next as the most important storytelling quality. [Source](https://indiantelevision.com/iworld/microdrama-matches-reels-as-86-per-cent-watch-it-for-15-minutes-daily/) AP reported executives saying some major platforms spend as much as 90% of budget on marketing. [Source](https://apnews.com/article/microdrama-issa-rae-kevin-hart-hollywood-087b042a6eac08e159410e29689606b9) The tool therefore extends simple clip selection with a cold-viewer safety check before media spend.

## Solution

The app reads timestamped English screenplays, normalizes dialogue and action into ordered beats, and produces only continuous 20-60 second candidates. It scores each clip using transparent rules:

- hook in the first 3 seconds (34%);
- cliffhanger/open tension in the final 6 seconds (38%);
- standalone clarity from relationship/context cues (20%);
- duration fit around 42 seconds (8%).

It separately calculates a cold-viewer risk score. It flags payoff terms such as `revealed`, `identity`, `dies`, or `pregnant`; later-series moments; endings that look resolved; and clips with thin speaker context. Risk below 25 is `SAFE`, 25-54 is `REVIEW`, and 55+ is `HIGH RISK`.

The editor sees exact timestamps, hook/cliffhanger evidence, score breakdown, and nearby context before and after the cut. They can sort by appeal or lowest risk, then approve, reject, or request a rewrite with a note. The app exports the full audit, editor decisions, and a Markdown presentation brief.

## What I added beyond the prompt

- Separate appeal and risk signals, so a strong but risky clip is escalated rather than hidden.
- Context windows to reveal missing setup or accidental payoff after the cut.
- Editorial decision logging and downloadable CSV handoff.
- A manual evaluation harness for Precision@5, good-clip rate, and spoiler-safety rate.
- A public Streamlit deployment with a synthetic demo and private in-memory `.txt` upload support; confidential Kuku scripts never enter GitHub.
- An optional OpenAI-compatible reviewer for the top 12 candidates. It is isolated behind an adapter and automatically falls back to the free deterministic rules pipeline if unavailable or invalid.

## Evidence, quality, and scale

The local run on the supplied confidential pack processed 50 episodes and evaluated 4,867 valid candidate windows. Nine automated tests cover parsing, timestamp and duration validity, overlap suppression, export, upload parsing, risk audit, evaluation metrics, presentation-brief generation, and model-failure fallback.

I do not claim a human accuracy rate yet. The repo includes a private label template for two editors to review 25-30 clips as `good`/`bad` and `safe`/`spoiler`/`unclear`; the evaluator then reports Precision@5 and spoiler-safety rate. In production I would compare audited promos with the current process on editor acceptance, time saved, first-three-second hold, click-through/install rate, episode-one completion, and viewer complaints about spoilers or misleading creative.

The rules pass has no API cost. Parsing is linear in beats; the simple candidate search is suitable for short episodes and can be optimized with sliding windows/parallel per-episode jobs at scale. The tool cannot see acting, music, pacing, or visual-only reveals. `SAFE` means no strong script-level warning, not automatic approval; final footage review remains human.

## Assumptions and AI use

I assumed the screenplay pack is confidential and excluded it from GitHub. AI-assisted coding helped implement and test the prototype. A known failure mode is that a dramatic word can be harmless setup, while a visual-only reveal can be missed. The UI exposes evidence and context so editors can override the tool.
