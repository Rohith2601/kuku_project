# Kuku Cold-Viewer Promo Audit

An explainable local prototype for **Kuku AI Generalist Assignment — Problem 3**. It helps a growth editor audit a promo before publishing: does it hook a cold viewer, retain an unresolved question, and avoid obvious plot-payoff/spoiler risk? It returns exact timestamps, a publish status, evidence, and reasons for editor review.

> Confidentiality: the supplied scripts are assignment input. Keep them local; do not commit, publish, or share them. Generated sample outputs intentionally contain no screenplay excerpts.

## Quick start

Install Python 3.11+ (the current machine has the `py` launcher but no installed interpreter), then from this folder:

```powershell
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

Set the Script folder to `I Married a Broken Soldier. He was a Duke-scripts (2)` and select **Audit all episodes**. The full unedited JSON and CSV handoff will be written to `outputs/raw/`. If the confidential input pack is absent—as it will be on a hosted deployment—the included synthetic `demo_data/` example runs by default. You can also upload one or more private `.txt` scripts; uploads are analyzed in memory.

For a reproducible, UI-free full-pack run:

```powershell
py run_analysis.py
```

Run validation with:

```powershell
py -m unittest discover -s tests -v
```

## Why this is a Problem 3 solution

Microdrama discovery is social-feed-led: 77% of respondents in a Kantar/ShareChat/Moj study said they discover it while scrolling, while 27% named curiosity about what happens next as the desired storytelling quality. [Indian Television report](https://indiantelevision.com/iworld/microdrama-matches-reels-as-86-per-cent-watch-it-for-15-minutes-daily/) The problem is not merely locating dramatic clips (Problem 1); it is deciding whether a dramatic clip is safe to run as acquisition creative for a person who has never seen the show.

This matters to a growth editor and paid-acquisition team because marketing competition is expensive—industry executives told AP some large platforms spend up to 90% of their budgets on marketing. [AP News](https://apnews.com/article/microdrama-issa-rae-kevin-hart-hollywood-087b042a6eac08e159410e29689606b9) A spoiler-heavy or contextless ad can waste a hard-won impression even if it has a strong opening. The solution is intentionally narrow: one editor, one pre-publish decision, one auditable output.

## How it works

1. `src/parser.py` turns every scene’s timestamped dialogue and action into normalized beats.
2. `src/candidates.py` starts a clip at a potential hook and creates only valid 20–60 second continuous windows.
3. `src/scoring.py` scores hook cues in the first 3 seconds, cliffhanger cues near the last 6 seconds, standalone context, and duration fit; it separately audits payoff terms, later-series placement, ending resolution, and thin character context.
4. Overlapping alternatives are suppressed. Promo appeal and cold-viewer risk remain separate signals, and the editor can sort by either one. Every recommendation is labelled `SAFE`, `REVIEW`, or `HIGH RISK`; this is not an auto-publish verdict.
5. The editor can inspect nearby context, mark a clip approved/rejected/needs rewrite, and download that feedback as CSV.

## Measure quality before claiming accuracy

Copy `eval/labels.example.json` to `eval/labels.local.json` and manually label 25–30 exported clips as `good`/`bad` and `safe`/`spoiler` (ideally with a second reviewer). Then run:

```powershell
py evaluate.py
```

It reports `precision_at_k`, overall good rate, and spoiler-safety rate only for reviewed clips. Keep the real label file private alongside the confidential scripts.
5. If configured, `src/reviewer.py` asks an OpenAI-compatible model to review the top candidates. It validates the result and falls back to the deterministic result on any failure.

## Folder guide

| Folder/file | Purpose |
| --- | --- |
| `app.py` | Streamlit pre-publish audit interface and export controls. |
| `src/` | Parsing, candidate generation, scoring, optional model review, and batch orchestration. |
| `config/` | Editable scoring rules; adjust it without code changes. |
| `tests/` | Dataset, timestamp, duration, diversity, and export regression tests. |
| `outputs/raw/` | Full machine outputs produced locally; do not commit if they contain confidential excerpts. |
| `outputs/samples/` | Shareable output summaries that omit script text. |
| `docs/` | Submission-ready solution narrative. |

## Optional model reviewer

Copy `.env.example` to `.env` and fill in its values (or set the same environment variables); do not commit your key. The reviewer uses the OpenAI-compatible `/chat/completions` interface and is intentionally isolated in `src/reviewer.py`, so the model vendor can be swapped without changing parsing or scoring. The offline pipeline is always available and is the source of truth if the API fails.

## Quality and limits

The tool has deterministic checks for duration and timestamps, plus tests against all 50 input files. It cannot see acting, music, pacing, or final footage. It can overvalue melodramatic words, flag harmless setup language as a spoiler, or miss a visual reveal. Editors should inspect all `REVIEW` and `HIGH RISK` results before posting.

## Scaling and cost

The offline pass is linear in screenplay beats and has no API cost. At larger volume it can run in a background job per show, store structured results, and send only the top candidates to a model or editor—controlling cost and preserving an auditable rules-based baseline.
