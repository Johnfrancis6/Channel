# Whose Dime — decisions

Franco decides; Claude recommends. Newest first. Each line: date, decision,
where it came from. A session that changes a decision adds a new line; it
never edits an old one.

## 2026-11-08 — first new channel on the watch list (after S09)

Source: Franco's "Oui, ajoute How They Make Billions à la liste", session
`session_01Cw13LgvyfSBBRJdw5oChae`, after the first weekly report.

| # | Decision | Applies to |
|---|---|---|
| D14 | **How They Make Billions (`@howtheymakebillions`) joins the watch list** (48 channels). Measured 08/11: created 2026-09-02, 1,070 subscribers, 2 long videos, median 199,472 views (fragile: n = 2). | `whosedime/watch/channels.csv` |

## 2026-11-08 — chart colours by meaning (before S07b)

Source: Franco's "oui" to Claude's recommendation on S07's chart self-critique,
session `session_01Cw13Lf9vU36VbFFB3o3udA`; built in S07b.

| # | Decision | Applies to |
|---|---|---|
| D13 | **A chart figure is coloured by what it means**: gain green only for the company's money coming in (`profit`, `revenue`); loss coral only for money lost (`loss`, `losses`, `lost`, `deficit`, `bankrupt*`, `crash*`); every other figure navy ink. The word lists live in `whosedime-video/settings.json` (`charts`). | `charts.py` |

## 2026-11-07 — caricatures on thumbnails (after S05)

Source: Franco, session `session_01Cw13LdhzyiVU46zmJ1Yzvk`, after Claude's
answer on the legal limits of caricature (not legal advice).

| # | Decision | Applies to |
|---|---|---|
| D12 | **A thumbnail prompt names the well-known executive** it caricatures, for a recognisable cartoon. Limits kept: deliberately unrealistic cartoon, a person well known to the public, tied to the decision the video tells, no false fact (no crime, illness or intimate scene), no implied endorsement, no photo given to the tool, never a realistic portrait. **Scene prompts stay anonymous** (the checker's `prompt-person` block is unchanged): Claude's recommendation, Franco did not extend D12 to scenes. Built in S06, task 0 | `step5_publication.md`, thumbnails |

## 2026-11-07 — answers to the pipeline audit

Source: Franco's reply to [`reports/Audit pipeline de production.md`](../../reports/Audit%20pipeline%20de%20production.md)
(section 4, questions A to F), session `session_01Cw13LfHTQxQekv3rqzspUm`.

| # | Decision | Applies to |
|---|---|---|
| D1 | **Zehon is frozen.** All effort goes to Whose Dime. Leave the Zehon files as they are (repo and Drive), except for one freeze note in `docs/chaine2/CONTEXTE.md`. | A-3 |
| D2 | **The whole Whose Dime system is in English**: skills, scripts, notebooks, docs, session prompts, Drive files, critique log. Zehon stays in French. | Franco, 07/11 |
| D3 | **The audit corrections are approved** (C1 to C8), to be built **for Whose Dime only**, step by step, one session at a time, each session writing the prompt of the next one. | Franco, 07/11 |
| D4 | **Fact registry** (C1, C2): every number, date, name and quote in a script or a publication must match a sourced line of `02b_factcheck.md`. A `[TO VERIFY]` tag blocks the voice, the assembly and the publication. Franco signs the fact check; it blocks the voice. | B-4, B-5 (recommendation accepted), E-13 |
| D5 | **One production branch: `main`.** Colab launchers always point to `main`. Build sessions merge into `main` through a pull request that Franco merges. | A-1 (recommendation accepted), C3 |
| D6 | **Voice listening sample before each full synthesis: 20 s** (not 60 s). | C-9 |
| D7 | **The blind voice test** (paragraph synthesis against sentence-by-sentence synthesis) **happens on the first Whose Dime video**, not on a Zehon video. | C-8 |
| D8 | **The Whose Dime voice is an American English narrator** (VoiceDesign, then clone on the Base model, as in `PLAN_ACTION.md` S1). | E |
| D9 | **Writing corrections** (C7: no forced connector, varied sentence length, scenes with named people, validation by ear) **apply to Whose Dime only.** | D |
| D10 | **A separate skill, `whosedime-maker`**, sharing the checks and the voice notebook with a common module in the repo. | E-12 |
| D11 | **Critique grades (Accurate / Clear / Lively) are collected on Whose Dime deliverables**, in a new English log: [`critique_log.jsonl`](critique_log.jsonl). | F |

### Zehon decisions parked by the freeze (apply only if Zehon restarts)

| # | Decision | Source |
|---|---|---|
| Z1 | Salt video: **cut** the sentence « Toi, tu en manges environ 3 kilos par an » (8.1 g/day never verified). | B-6 |
| Z2 | Glass video: **keep** the title and the « NÉE EN 1959 ?! » thumbnail for now. | B-7 |
| Z3 | Glass video: still needs a re-render with the dark band under animated text (it was rendered from branch `claude/zelan-studio-analysis-rws9f6@15b0fe0`). | audit P1 |

## Earlier decisions still in force

From [`docs/finance/PLAN_ACTION.md`](../finance/PLAN_ACTION.md) § 7 (05/11/2026):
channel name **Whose Dime** (`@whosedime`), series **"Who Pays?"**, length
**13-15 min** (2,000 to 2,250 words), six-beat structure, title template
under 40 characters, fallback plan at videos 5, 10 and 20. Read § 7 of that
file for the exact wording; it is in French.
