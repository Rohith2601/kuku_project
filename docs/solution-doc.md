# Kuku Cold-Viewer Promo Audit — Problem 3 Solution Note

## The problem

I chose Problem 3: **a growth editor needs to decide whether a promo is safe and legible before putting budget behind it**. A microdrama clip can have a strong hook yet accidentally reveal the payoff, rely on a later character arc, or confuse someone seeing the show for the first time. The narrow user is a performance-marketing/growth editor; the one decision is **publish, inspect, or replace this proposed clip**.

This is real because discovery happens in the feed: a Kantar study reported that 77% of Indian microdrama viewers discover titles while scrolling, and 27% prioritise curiosity about what happens next. [Indian Television report](https://indiantelevision.com/iworld/microdrama-matches-reels-as-86-per-cent-watch-it-for-15-minutes-daily/) The stakes are material: AP reported industry executives saying some large microdrama platforms spend up to 90% of their budgets on marketing. [AP News](https://apnews.com/article/microdrama-issa-rae-kevin-hart-hollywood-087b042a6eac08e159410e29689606b9) A public DramaBox viewer also described being taken out of the experience by choppy/inconsistent episode transitions. [Viewer post](https://www.reddit.com/r/dramabox/comments/1g4lk7i/why_are_dramabox_episodes_inconsistent/)

It matters beyond Problem 1 because finding exciting moments is only the first step; this tool catches whether an exciting moment is appropriate acquisition creative. It is deliberately more focused than a general legal assistant: it is one workflow where the output can be checked against the source screenplay before spending media budget.

## Working prototype

The app parses the supplied timestamped scripts and creates only continuous 20–60 second candidates. It scores hook, cliffhanger, context, and duration, then independently audits: plot-payoff wording, whether the clip comes from a later episode, whether the ending appears resolved, and whether there is thin character context. It outputs an exact timestamped card with a `SAFE`, `REVIEW`, or `HIGH RISK` label and reasons for the editor to inspect.

The rules pipeline is reproducible and costs nothing for every show. An optional OpenAI-compatible reviewer can refine the top candidates; invalid or unavailable model output falls back to rules. A human editor remains the publishing authority.

## Evidence, evaluation, and limits

The included run processes all 50 supplied episodes, evaluates 4,867 valid windows, and exports raw JSON/CSV. Automated tests verify timestamps, duration, parsing, diversity, export, and model-failure fallback. In a real team, I would A/B test audited versus current promos, tracking editor acceptance, first-three-second hold, click-through/install rate, episode-one completion, and viewer complaints about misleading/spoiler-heavy ads.

The tool can be wrong because a screenplay cannot show performance, music, visual reveals, or irony. It can flag a harmless word such as “wedding,” or miss a spoiler conveyed only by the image. Therefore `SAFE` means “no strong script-level warning,” not “safe without viewing footage.”

## Assumptions and AI use

I assumed the supplied input pack is confidential and kept it out of the public repository. I used AI-assisted coding to scaffold the prototype and to critique the scoring approach. One known failure of AI/rules is treating dramatic trope words as proof of a spoiler; every risky result displays its evidence so a human can overturn it.
