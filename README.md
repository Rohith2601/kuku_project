# Kuku Cold-Viewer Promo Audit

> **Live app:** [rohith2601-kuku-project-app-kknezy.streamlit.app](https://rohith2601-kuku-project-app-kknezy.streamlit.app/)

An editor-facing prototype for **Kuku AI Generalist Assignment - Problem 3**. It audits short-form microdrama promo candidates before they are published: does the clip create curiosity for a first-time viewer, end with open tension, and avoid obvious story-payoff or context risks?

## The problem

Discovery happens in a social feed, where a viewer may see a promo before knowing any character or plot. A growth editor needs more than a list of dramatic moments: a clip can have a strong hook but spoil the payoff, begin too deep into a character arc, or confuse a cold viewer. This tool turns that judgement into a repeatable pre-publish workflow.

The prototype focuses on one narrow decision: **should an editor publish, inspect, or replace this promo clip?**

## Try the deployed app

Open the [live Streamlit app](https://rohith2601-kuku-project-app-kknezy.streamlit.app/). It starts with a public synthetic demo screenplay so the project is safe to view publicly.

To analyze a private screenplay pack, use **Upload screenplay .txt files** in the sidebar. Uploaded files are analyzed in memory and are not part of this repository.

## What it does

1. Parses timestamped dialogue, actions, and scenes from screenplay text.
2. Creates valid continuous 20-60 second promo candidates.
3. Scores each candidate for hook, cliffhanger, standalone clarity, and duration fit.
4. Separately audits cold-viewer risks: payoff/spoiler cues, later-series placement, a resolved ending, and thin character context.
5. Labels each candidate `SAFE`, `REVIEW`, or `HIGH RISK` with evidence for the editor.
6. Lets an editor record `Approve`, `Reject`, or `Needs rewrite`, then download the resulting handoff.

## Additions beyond the minimum assignment prompt

The assignment asks for a small working solution. This prototype also adds practical workflow features that make the output usable in a real growth/editing process:

- **Separate appeal and risk signals:** a compelling clip is not silently removed just because it is risky; the editor can sort by either metric.
- **Context window:** every clip shows nearby beats before and after the cut so the editor can check whether it opens clearly and truly ends on tension.
- **Decision log:** editorial decisions and notes are retained for the browser session and downloadable as CSV.
- **Presentation brief:** a one-click Markdown brief summarizes the shortlist, risk mix, and editor decisions.
- **Manual evaluation harness:** private reviewers can label 25-30 clips and calculate Precision@5, good-clip rate, and spoiler-safety rate.
- **Hosted-demo workflow:** the public app has a synthetic demo and accepts private file uploads, so confidential Kuku scripts never need to enter GitHub.
- **Optional model adapter:** an OpenAI-compatible reviewer can refine top results when configured; the deterministic rules pipeline remains the safe fallback.

## Presentation flow

For a short live walkthrough:

1. Run the public demo or upload a script pack.
2. Start at **Recommended presentation candidate** and explain that appeal and risk are deliberately different scores.
3. Expand the candidate, show its audit evidence and context window, then make an editorial decision.
4. Open **Review queue** to show how risky but potentially valuable clips are escalated instead of discarded.
5. Open **Decision log** and download the presentation brief or decision CSV.

Use [docs/demo-video-script.md](docs/demo-video-script.md) for a timed narration and on-screen actions.

## Local setup

```powershell
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

Run the private full-pack batch job only when the confidential input folder is available locally:

```powershell
py run_analysis.py
```

Run tests:

```powershell
py -m unittest discover -s tests -v
```

## Manual quality evaluation

Copy `eval/labels.example.json` to `eval/labels.local.json`, manually label 25-30 exported candidates, then run:

```powershell
py evaluate.py
```

The real labels stay private. The evaluator reports reviewed count, Precision@5, good-clip rate, and spoiler-safety rate.

## Project structure

```text
app.py                    Streamlit editor dashboard
src/                      Parsing, scoring, audit, export, and brief generation
config/                   Editable scoring cues and weights
demo_data/                Public synthetic screenplay for the deployed demo
eval/                     Private manual-evaluation template
docs/                     Solution note and demo-video script
tests/                    Automated parser, scoring, export, and evaluation tests
outputs/raw/              Local confidential outputs; ignored by Git
```

## Privacy and limitations

The supplied Kuku screenplays are confidential. They are ignored by Git, never included in the deployed demo, and should not be shared publicly. The tool reads screenplay text, not final video, so it cannot judge acting, music, visual reveals, or irony. `SAFE` means no strong script-level warning; a human editor still reviews footage before publication.

## Evidence for the framing

Microdrama discovery is strongly feed-led, and curiosity is a key viewing driver. [Indian Television report](https://indiantelevision.com/iworld/microdrama-matches-reels-as-86-per-cent-watch-it-for-15-minutes-daily/) Marketing competition is also material: industry executives told AP that some major platforms spend as much as 90% of budget on marketing. [AP News](https://apnews.com/article/microdrama-issa-rae-kevin-hart-hollywood-087b042a6eac08e159410e29689606b9)
