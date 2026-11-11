# Kuku Cold-Viewer Promo Audit

**Problem chosen:** Problem 3 - Find your own problem

**Live prototype:** [rohith2601-kuku-project-app-kknezy.streamlit.app](https://rohith2601-kuku-project-app-kknezy.streamlit.app/)
**Repository:** [github.com/Rohith2601/kuku_project](https://github.com/Rohith2601/kuku_project)

## 1. Problem and why it matters

I chose a narrow promotional workflow: **before a growth editor publishes a microdrama promo, they need to know whether it creates curiosity for a cold viewer without spoiling the story or becoming confusing out of context.**

This is a real acquisition problem, not just clip discovery. The feed is the main discovery surface: a Kantar/ShareChat/Moj study reported that 77% of viewers discover microdrama while scrolling and 27% say curiosity about what happens next is the most important storytelling quality. [Source](https://indiantelevision.com/iworld/microdrama-matches-reels-as-86-per-cent-watch-it-for-15-minutes-daily/) AP also reported industry executives saying that some large microdrama platforms spend up to 90% of their budget on marketing. [Source](https://apnews.com/article/microdrama-issa-rae-kevin-hart-hollywood-087b042a6eac08e159410e29689606b9)

The user is a growth or promo editor. The output is one checkable decision per candidate: **publish, inspect, or replace**. This is more useful than simply finding dramatic moments because a high-drama clip can still expose a payoff, rely on a later character arc, or make no sense to a first-time viewer.

## 2. Working solution

The app reads timestamped screenplay text and produces only continuous 20-60 second candidates. A transparent offline scorer measures hook strength in the first three seconds, cliffhanger strength at the end, standalone clarity, and duration fit. A separate cold-viewer audit flags script-level payoff words, later-series clips, apparently resolved endings, and thin context.

Each recommendation contains exact timestamps, hook and cliffhanger evidence, a context window before and after the proposed cut, two separate scores (promo appeal and cold-viewer risk), and a `SAFE`, `REVIEW`, or `HIGH RISK` status. The editor can approve, reject, or request a rewrite, then download decisions and a presentation brief.

The full supplied input pack run processed 50 episodes and evaluated 4,867 valid windows. The public deployment uses a synthetic script; confidential Kuku material is excluded from GitHub. Private scripts can be uploaded to the deployed app and are analyzed in memory.

## 3. Additions beyond the prompt

- An explicit cold-viewer spoiler/context audit, rather than only a promo ranking.
- Separate appeal and risk signals, so risky but potentially valuable clips are escalated instead of hidden.
- Editor decision logging, downloadable CSV handoff, and a one-click Markdown presentation brief.
- A manual evaluation harness for Precision@5 and spoiler-safety rate using private human labels.
- A public hosted-demo path plus private in-memory upload support.
- An optional OpenAI-compatible reviewer. It is isolated behind an adapter and falls back to deterministic rules if unavailable or invalid.

## 4. Evaluation, scale, and limits

Nine automated tests cover timestamp parsing, duration limits, overlap suppression, exports, upload parsing, risk audit, evaluation metrics, and model-failure fallback. In a real team I would have two editors label 25-30 clips, report Precision@5 and disagreement rate, then A/B test audited versus existing promos on first-three-second hold, click-through/install rate, episode-one completion, and complaints about misleading ads.

The rules pass is linear in screenplay beats and has no API cost. At scale it can run as a job for each show, with only top candidates sent to a model or editor. It cannot see final footage, performance, music, or visual reveals; `SAFE` therefore means no strong script-level warning, not automatic approval. A human editor remains responsible for the final cut.

## Assumptions and AI use

I assumed the supplied screenplay pack is confidential and did not publish it. AI-assisted coding was used to implement and test the prototype. A known failure mode is that a dramatic word such as "wedding" can be harmless setup rather than a spoiler, while a visual-only reveal can be missed. The app shows evidence and context so a human can override either result.
