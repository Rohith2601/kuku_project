# Kuku Cold-Viewer Promo Audit

**Assignment:** Kuku AI Generalist - Problem 3: Find your own problem

**Live prototype:** [rohith2601-kuku-project-app-kknezy.streamlit.app](https://rohith2601-kuku-project-app-kknezy.streamlit.app/)
**Source code:** [github.com/Rohith2601/kuku_project](https://github.com/Rohith2601/kuku_project)

## 1. Problem selected

I chose a narrow problem in **promoting AI microdramas**: before publishing a paid or organic promo, a growth editor must decide whether the clip works for a *cold viewer* - someone who has never seen the show. A good promo should create curiosity in its first seconds and end with tension, but it must not reveal the payoff, rely on unexplained character history, or look like a resolved scene when isolated from the episode.

This matters because discovery happens in the feed. A Kantar/ShareChat/Moj study reported that 77% of viewers discover microdrama while scrolling; 27% named curiosity about what happens next as the most important storytelling quality. [Indian Television report](https://indiantelevision.com/iworld/microdrama-matches-reels-as-86-per-cent-watch-it-for-15-minutes-daily/) The economics make a bad promo costly: AP reported industry executives saying that some major microdrama platforms spend as much as 90% of their budgets on marketing. [AP News](https://apnews.com/article/microdrama-issa-rae-kevin-hart-hollywood-087b042a6eac08e159410e29689606b9)

The target user is a **growth/promo editor**. The product answers one operational question: **publish this clip, inspect it further, or ask for a different cut?** This extends Problem 1 meaningfully. Finding dramatic clips is useful, but a dramatic clip can still be damaging acquisition creative if it spoils the reveal or makes no sense to a first-time viewer.

## 2. Scope and assumptions

### In scope

- English screenplay text with episode, scene, action, dialogue, and timestamps.
- Continuous 20-60 second promo candidates from a single episode.
- Script-level assessment of hook, cliffhanger, standalone clarity, and cold-viewer risk.
- An explainable editor review workflow with timestamps, evidence, context, decisions, and exports.

### Deliberately out of scope

- Video editing, music, captions, thumbnails, or multi-segment montage creation.
- Automatic publication or a claim that text-only analysis can judge final footage.
- A universal spoiler detector; the tool is a triage assistant for an editor.

### Assumptions

- The supplied 50-screenplay pack is confidential. It is used locally, ignored by Git, and never included in the public deployment.
- The screenplays follow the supplied timestamped format closely enough to parse dialogue and action beats.
- A human editor reviews footage before a clip is published.

## 3. What I built

The prototype is a deployed Streamlit dashboard plus a reusable Python pipeline. A user can run the included public synthetic demo, select a local private folder, or upload private `.txt` scripts. Uploads are parsed in memory and are not stored in the GitHub repository.

For each recommended candidate the app shows:

- episode number and exact start/end timestamps;
- **Promo appeal** score out of 100;
- separate **Cold-viewer risk** score out of 100;
- `SAFE`, `REVIEW`, or `HIGH RISK` status;
- extracted hook, cliffhanger, score breakdown, audit notes, and nearby context before/after the cut;
- editor actions: `Approve`, `Reject`, or `Needs rewrite`, with an optional note.

The dashboard has four working areas:

1. **Shortlist** - filters and sorts candidates by promo appeal or lowest risk.
2. **Review queue** - surfaces every non-safe candidate for deliberate inspection instead of hiding it.
3. **Decision log** - stores editor judgments for the current session and exports CSV, JSON, and a Markdown editorial brief.
4. **How to present it** - states what is automated and what remains a human decision.

## 4. Implementation detail

### A. Parsing

`src/parser.py` reads each `.txt` screenplay and converts it into ordered **beats**. Each beat contains episode number, scene number, type (`dialogue` or `action`), speaker where available, text, start timestamp, and end timestamp. Camera-only records are excluded because the prototype needs narrative/action evidence. Timestamps are converted from `MM:SS.cc` to seconds, then formatted back into exact editor-facing timestamps.

The parser accepts local files and Streamlit upload objects, uses UTF-8 with replacement for malformed characters, and normalizes whitespace. A malformed timestamp is skipped rather than crashing the full show run.

### B. Candidate generation

`src/candidates.py` treats every dialogue or action beat as a possible start. For each start it considers valid later beat endings between 20 and 60 seconds and evaluates the last three valid end points. This produces multiple plausible cut points while keeping the result continuous and timestamp-auditable.

Candidates that overlap an already selected candidate by more than 55% of the shorter clip are suppressed. The final shortlist therefore covers more distinct moments rather than presenting three near-identical cuts from one scene.

### C. Explainable promo-appeal score

`src/scoring.py` uses editable phrases in `config/scoring_rules.json`. Phrase matching uses word boundaries, so a cue such as `stop` cannot accidentally match a larger unrelated word.

| Component | What is measured | Weight |
| --- | --- | ---: |
| Hook | Trigger phrases/actions inside the first 3 seconds | 34% |
| Cliffhanger | Unresolved/reveal/threat cues in the final 6 seconds | 38% |
| Standalone clarity | Relationship/context cues, sufficient beats, and speaker presence | 20% |
| Duration fit | Distance from a 42-second target within the 20-60 second constraint | 8% |

The output is a weighted appeal score, plus the actual hook and cliffhanger text that produced it. This makes the recommendation inspectable rather than a black-box label.

### D. Cold-viewer risk audit

Appeal and risk are intentionally independent. A strong but risky clip can still be useful after a new edit, so it is not silently removed.

The risk audit adds warnings for:

- possible payoff terms such as `revealed`, `identity`, `dies`, `married`, or `pregnant`;
- a clip from episode 10 or later, which may expose a character arc;
- an ending without question/stop/open-tension signals, which may be a resolved scene;
- a clip with one or no identified speakers, which may lack enough context.

Risk is capped at 100 and mapped to `SAFE` below 25, `REVIEW` from 25 to 54, and `HIGH RISK` at 55 or above. Every warning is shown in the UI so the editor can disagree with it.

### E. Optional model reviewer

The deterministic system works without any paid service. When `PROMO_API_BASE_URL`, `PROMO_API_KEY`, and `PROMO_MODEL` are configured, `src/reviewer.py` sends only the top 12 candidates to an OpenAI-compatible `/chat/completions` endpoint. It requests structured JSON containing a revised hook, cliffhanger, rationale, and score. The final score blends 55% rules score and 45% model score.

If configuration, network access, or the model response fails, the app keeps the rules-based results. This fallback is intentional: the prototype remains runnable and auditable without paid credentials.

## 5. Additions beyond the brief

The base prompt asks for a small working solution. I added the following practical capabilities because they make the output usable by an editorial/growth team:

- **Separate appeal and risk:** avoids a common ranking mistake where the safest option is assumed to be the best promo.
- **Context window:** shows nearby beats before and after a proposed cut so an editor can detect missing setup or an accidental payoff.
- **Editorial decision loop:** saves approve/reject/rewrite decisions and notes, then exports them as a handoff CSV.
- **Presentation brief:** generates a shareable Markdown summary of the shortlist, risk mix, and editor-approved clips.
- **Evaluation harness:** `eval/labels.example.json` and `evaluate.py` allow private human labels to calculate `precision_at_k`, good-clip rate, and spoiler-safety rate.
- **Public-safe deployment:** a synthetic demo screenplay lets anyone open the live app, while private scripts are uploaded in memory and remain outside GitHub.
- **Presentation UX:** a recommended lower-risk candidate, review queue, clear dashboard metrics, and a dark theme make the live workflow easy to explain in a short video.

## 6. Evaluation and quality checking

### Completed checks

The supplied 50-episode private input pack was processed successfully. The run found **4,867 valid 20-60 second candidate windows** and produced an editor shortlist. The repository has **nine automated tests** covering:

1. timestamp conversion/formatting;
2. parsing a real supplied episode;
3. processing all 50 input episodes and enforcing duration constraints;
4. JSON/CSV export;
5. overlap suppression;
6. model-review failure fallback;
7. cold-viewer risk detection;
8. uploaded-text parsing and evaluation metrics;
9. presentation-brief generation.

### Honest evaluation status

The project has not yet claimed a human precision number because no independently labelled editor set has been collected. Instead, it includes the evaluation mechanism needed to obtain one. The next validation step is to have two editors independently label 25-30 candidates as `good`/`bad` and `safe`/`spoiler`/`unclear`; those labels remain private. `evaluate.py` then reports Precision@5, good-clip rate, and spoiler-safety rate. Differences between the two editors should be reviewed as disagreement cases rather than treated as ground truth.

### Production success criteria

After offline quality is acceptable, compare audited promos with the existing editorial process using:

- editor acceptance rate and time saved per show;
- first-three-second hold rate;
- click-through or install rate for acquisition ads;
- episode-one completion and next-episode conversion;
- user complaints indicating spoilers, misleading creative, or confusing setup.

## 7. Scale, cost, and limitations

The offline rules pass has no API cost. Parsing itself is linear in the number of beats; the current simple candidate search checks later beat ends for each possible start, which is acceptable for 1-2 minute episodes but should be optimized with sliding windows for very large scripts. Episodes can be processed independently, so batch jobs can be parallelized per show.

At scale, I would retain only structured metadata and audit traces, send only the top candidates to a stronger model or an editor, collect editor decisions, and tune the rule list with those decisions. The optional model review adds cost only for the top 12 results.

The most important limitations are intentional and visible:

- screenplay text cannot measure acting, music, pacing, facial expressions, or a visual-only reveal;
- trope words can produce false spoiler warnings (`wedding` can be setup rather than payoff);
- subtle irony/subtext can be missed;
- later-episode placement is a warning, not proof of a spoiler;
- `SAFE` means no strong script-level warning, never automatic approval.

## 8. How to run and demonstrate it

### Public deployment

Open the live application at [rohith2601-kuku-project-app-kknezy.streamlit.app](https://rohith2601-kuku-project-app-kknezy.streamlit.app/). Run the synthetic demo, inspect the recommended candidate, show its evidence/context, approve or reject it, then download the presentation brief.

### Local/private run

```powershell
py -m pip install -r requirements.txt
py -m streamlit run app.py
py -m unittest discover -s tests -v
```

For the supplied private pack only:

```powershell
py run_analysis.py
```

The detailed 2.5-minute recording script, exact on-screen actions, and narration are in [`docs/demo-video-script.md`](demo-video-script.md).

## 9. AI use and integrity

I used AI-assisted coding to help scaffold, review, and test the prototype. The core product decisions, scoring approach, limitations, evaluation plan, and implementation were checked against the code and input format. One place where AI/rules can be wrong is treating a dramatic word as proof of a spoiler or missing a reveal conveyed only through visuals. That is why the tool shows evidence, surrounding context, and a human decision loop instead of claiming autonomous editorial judgment.
