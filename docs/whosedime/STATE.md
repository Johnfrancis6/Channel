# Whose Dime — state

Short by rule (60 lines at most). Updated at the end of every session.
Plan: [`ROADMAP.md`](ROADMAP.md). Decisions: [`DECISIONS.md`](DECISIONS.md).

**Last update: 2026-11-07**, end of S03 Shared checks (session
`session_01Cw13LczhHdcKVdn9P1C1H5`).

## Where we are

- **S01 done and merged** into `main` ([Johnfrancis6/Channel#2](https://github.com/Johnfrancis6/Channel/pull/2)).
- **S02 done**: 14 style rules (all `warn`), `measure.py`, voice direction, in
  [`whosedime/research/`](../../whosedime/research/README.md).
- **S03 done**: [`whosedime/common/`](../../whosedime/common/README.md): `checker.py`
  (`script`, `voice`, `publication`, `all`; exit 1 on a block), the registry
  format [`FACTCHECK_FORMAT.md`](../../whosedime/common/FACTCHECK_FORMAT.md), lists
  in files. Measured: each faulty fixture is blocked for its fault only; the
  clean Uber pair (2,011 words) has 0 blocks and 0 warnings.
- No skill yet (S04, S05); no Whose Dime Drive folder (S08). No PR needed
  (ROADMAP: PRs after S01, S05, S07).

## Branches

| Branch | Role |
|---|---|
| `claude/blissful-tesla-abtjgt` | **work branch** for build sessions (from S02) |
| `main` | production (Colab launchers); has S01 |
| `claude/zelan-studio-analysis-rws9f6` | old Zehon Drive launchers; leave it (Zehon frozen) |

## Tools

- Checker: `python3 whosedime/common/checker.py all FOLDER`; style metrics:
  `python3 whosedime/research/tools/measure.py FILE`.
- Skill sync: `python3 tools/sync_skills.py` (`--check` reports drift).
- Tests: `python3 -m unittest discover -s tests` — **70 pass** (46 + 24
  checker), measured 07/11. Fresh container: see `CLAUDE.md`.

## Sessions

| # | Status |
|---|---|
| S01 Foundations / S02 Storytelling rules / S03 Shared checks | **done** 07/11 |
| S04 Maker, topic to script | **next** — prompt ready: [`sessions/S04_maker_topic_to_script.md`](sessions/S04_maker_topic_to_script.md) |
| S05 to S09 | planned in `ROADMAP.md` |

## Open issues

- **Deviation from the S03 prompt**: S1, S8, S9 are measured on the whole
  script (they count from word one, i.e. the cold open), not on the cut cold
  open, where "no person found" reads as the extract's length and passes.
- **Checker limits** (stated in its docstring): a name used only as a
  sentence's first word is not checked; titles and thumbnails are checked
  for numbers, not names; a number matches by value, not unit ("20 minutes"
  passes because "$20 million" is registered).
- **Signature not bound to the content** (an edited registry stays signed);
  **C2 partial**: a title may cite its fact id (`[^Fnn]`), not required (S05).
- `tests/fixtures/whosedime/factcheck_clean.md`: facts from memory (labelled), never a source.
- **Style rules are weak evidence** (n = 30, all `warn`). Re-measure after video 10.
- Stale: ROADMAP rule 2 (old branch), `whosedime/README.md` ("Only this
  README exists today"). No container setup script. No graded critique line yet.
