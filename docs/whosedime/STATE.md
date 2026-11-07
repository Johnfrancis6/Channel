# Whose Dime — state

Short by rule (60 lines at most). Updated at the end of every session.
Plan: [`ROADMAP.md`](ROADMAP.md). Decisions: [`DECISIONS.md`](DECISIONS.md).

**Last update: 2026-11-07**, end of S05 Maker, scenes to publication
(session `session_01Cw13LdhzyiVU46zmJ1Yzvk`).

## Where we are

- **S01 done and merged** into `main` ([Johnfrancis6/Channel#2](https://github.com/Johnfrancis6/Channel/pull/2)).
  S02 rules, S03 checker, S04 skill steps 1-3: done (see the READMEs they link).
- **S05 done**: skill [`whosedime-maker`](../../whosedime/whosedime-maker/SKILL.md) steps 4-5,
  per-video `00_state.md` and Drive memory ([`memory.md`](../../whosedime/whosedime-maker/references/memory.md)),
  session table. Checker: new `scenes` target, new `title-source` rule (C2).
  Uber eval: 91 scenes, `checker.py all` exit 0 (measured). Haiku "where are the videos?" test passed once
  ([evals README](../../whosedime/whosedime-maker/evals/README.md)).
- **Merged into `main`**: [Johnfrancis6/Channel#3](https://github.com/Johnfrancis6/Channel/pull/3) (S02-S05). No Drive folder yet (S08).

## Branches

| Branch | Role |
|---|---|
| `claude/blissful-tesla-abtjgt` | **work branch** for build sessions (from S02; recreated from `main` after #3) |
| `main` | production (Colab launchers); has S01 to S05 |
| `claude/zelan-studio-analysis-rws9f6` | old Zehon Drive launchers; leave it (Zehon frozen) |

## Tools

- Checker: `python3 whosedime/common/checker.py all FOLDER` (`scenes`, `fingerprint FILE`).
- Skill sync: `python3 tools/sync_skills.py` (`--check` reports drift).
- Tests: `python3 -m unittest discover -s tests` — **100 pass**, measured 07/11. Fresh container: see `CLAUDE.md`.

## Sessions

| # | Status |
|---|---|
| S01 to S05 | **done** 07/11 |
| S06 Voice notebook | **next** — prompt ready: [`sessions/S06_voice_notebook.md`](sessions/S06_voice_notebook.md) |
| S07 to S09 | planned in `ROADMAP.md` |

## Open issues

- **For Franco** (S05 choices, assumed): a 5th scene type `title` (the "WHO PAYS?" card) so that
  `chapter` stays at 6; the channel palette (cream, dollar green, coral, mustard, navy).
- **D12** (Franco, 07/11): thumbnail prompts name the well-known executive: built in S06, task 0.
- **For Franco**: respellings for `lexicon.tsv`? `UK` → U-K, `LeWeb` → Luh-WEB, `Rumayyan` → Roo-MY-yan (not added).
- **Checker limits**: `chart-source` checks a chart's numbers, not its words; `prompt-person` sees only
  the people block (a person named only in a fact, e.g. Mr Aslam, is not caught); `name-first` stays
  noisy (script 10 words, publication 3, none a name); the scenes summary counts 2,103 words where the
  script check says 2,087 (two tokenisers); S1, S8, S9 on the whole script; numbers match by value.
- The palette lives in `step4_scenes.md` and each `03_scenes.md`: S07 should read one source (C5).
- Uber eval: beat 3 is the 2016 Saudi investment, not the cheap-fare decision; no named taxi owner;
  F05 (an estimate) is drawn in 3 of 25 charts. No image or thumbnail was generated: prompts untested.
- The hash covers comments; the skill may write the `Signed:` line on Franco's word (log says so).
- Step 1 uses `zehon/content-maker/scripts/youtube.py` (French output). Fixture `factcheck_clean.md`:
  facts from memory. Style rules weak evidence (n = 30). Stale: ROADMAP rule 2 branch name,
  `whosedime/README.md`. No setup script. No graded critique yet.
