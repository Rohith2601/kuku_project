# Demo Video Script (about 2 minutes 30 seconds)

Use the deployed app: [rohith2601-kuku-project-app-kknezy.streamlit.app](https://rohith2601-kuku-project-app-kknezy.streamlit.app/). Keep the video focused on one editorial decision, not every feature.

## Before recording

1. Open the deployed app in a clean browser tab.
2. In the sidebar, keep the included `demo_data` folder selected, set **Candidates to review** to 20, and click **Run promo audit**.
3. Wait until the audit completes. Expand the first candidate in the **Shortlist** tab.
4. If you can safely use the private input pack locally, run it before recording. Do not show, upload, or publish the confidential screenplay text in a public video.

## Narration and on-screen actions

### 0:00-0:15 - Problem

**On screen:** App title and the sidebar.

**Say:**

> This is Kuku Cold-Viewer Promo Audit. I chose Problem 3. The problem is not only finding dramatic moments in a microdrama. Before a growth editor spends budget on a promo, they need to know whether a new viewer will understand it, stay curious, and not see the payoff too early.

### 0:15-0:35 - Run the workflow

**On screen:** Point to the local folder/upload control, then click **Run promo audit**. Show the completion message.

**Say:**

> The tool accepts timestamped screenplay files. For this public demo I use a synthetic script, while the deployed app also supports private file uploads in memory. It parses dialogue and actions, creates only 20 to 60 second continuous clips, and audits the valid candidates.

### 0:35-0:55 - Explain the dashboard

**On screen:** Point to the four summary metrics and **Recommended presentation candidate**.

**Say:**

> The dashboard separates promo appeal from cold-viewer risk. That is important: a dramatic clip should not be silently removed because it is risky. Instead, the editor sees the tradeoff and can decide whether to use it, inspect it, or request a different cut.

### 0:55-1:30 - Explain one candidate

**On screen:** Expand the recommended candidate. Point to hook, cliffhanger, appeal score, risk score, and status.

**Say:**

> Here is one candidate. The tool gives exact start and end timestamps, identifies the hook and the intended cliffhanger, and assigns an appeal score. Separately, it assigns a cold-viewer risk score and a SAFE, REVIEW, or HIGH RISK label. These are explanations for an editor, not a claim that AI should publish automatically.

### 1:30-1:50 - Show evidence and context

**On screen:** Click **Audit evidence**, then **Context window**.

**Say:**

> The audit evidence explains why a clip was flagged. The context window shows nearby beats before and after the proposed edit. This is useful because a clip can sound exciting in isolation but either spoil the next moment or be confusing without setup.

### 1:50-2:10 - Human decision loop

**On screen:** Enter a short note such as `Clear conflict; verify final visual cut`, then click **Approve**. Open **Review queue** briefly.

**Say:**

> The human editor makes the final call. I can approve, reject, or request a rewrite and add a reason. The Review queue keeps risky but potentially useful moments visible for deliberate review instead of hiding them.

### 2:10-2:25 - Concrete output and quality checking

**On screen:** Open **Decision log**, show the decision table, then click the presentation-brief download button.

**Say:**

> The output is not just a score. The editor can download a decision CSV and a concise presentation brief. I also added a manual evaluation workflow: editors can label a small set of clips and measure Precision at five and spoiler-safety rate before trusting the ranking.

### 2:25-2:35 - Close honestly

**On screen:** Return to the method tab or the app header.

**Say:**

> The current version reads screenplay text, so it cannot judge acting, music, or a visual-only reveal. SAFE means no strong script-level warning, not automatic approval. The value is reducing a large script pack to an auditable editor decision queue.

## Recording checklist

- Keep the video under three minutes.
- Mention the live app link and repository in your submission form.
- Show the workflow, not source code.
- Do not show confidential Kuku screenplay text, raw outputs, API keys, or local file paths.
- Speak naturally; understand the tradeoffs instead of reading every word exactly.
