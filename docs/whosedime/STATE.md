# Whose Dime — state

Short by rule (60 lines at most). Updated at the end of every session.
Plan: [`ROADMAP.md`](ROADMAP.md). Decisions: [`DECISIONS.md`](DECISIONS.md).

**Last update: 2026-11-07**, end of S04 Maker, topic to script (session
`session_01Cw13LfimAnv8wXEE8UGuDc`).

## Where we are

- **S01 done and merged** into `main` ([Johnfrancis6/Channel#2](https://github.com/Johnfrancis6/Channel/pull/2)).
- **S02 done**: 14 style rules (all `warn`), [`whosedime/research/`](../../whosedime/research/README.md).
  **S03 done**: [`whosedime/common/`](../../whosedime/common/README.md) `checker.py`,
  registry format [`FACTCHECK_FORMAT.md`](../../whosedime/common/FACTCHECK_FORMAT.md).
- **S04 done**: signature bound to the registry (`sha256:` hash), `name-first` warning;
  skill [`whosedime-maker`](../../whosedime/whosedime-maker/SKILL.md) steps 1-3. Uber eval,
  facts read on the web ([`evals/files/01_uber/`](../../whosedime/whosedime-maker/evals/files/01_uber/)):
  measured `checker.py all` exit 0, 0 blocks, 1 warning, 2,087 words.
- Steps 4-5: S05. No Drive folder (S08). Next PR after S05.

## Branches

| Branch | Role |
|---|---|
| `claude/blissful-tesla-abtjgt` | **work branch** for build sessions (from S02) |
| `main` | production (Colab launchers); has S01 |
| `claude/zelan-studio-analysis-rws9f6` | old Zehon Drive launchers; leave it (Zehon frozen) |

## Tools

- Checker: `python3 whosedime/common/checker.py all FOLDER` (`fingerprint FILE` to sign).
- Skill sync: `python3 tools/sync_skills.py` (`--check` reports drift).
- Tests: `python3 -m unittest discover -s tests` — **84 pass** (46 + 32
  checker + 6 skill), measured 07/11. Fresh container: see `CLAUDE.md`.

## Sessions

| # | Status |
|---|---|
| S01 Foundations / S02 Storytelling rules / S03 Shared checks / S04 Maker 1 | **done** 07/11 |
| S05 Maker, scenes to publication, and state | **next** — prompt ready: [`sessions/S05_maker_scenes_to_publication.md`](sessions/S05_maker_scenes_to_publication.md) |
| S06 to S09 | planned in `ROADMAP.md` |

## Open issues

- S1, S8, S9 are measured on the whole script (S03 deviation, see docstring).
- **Checker limits** (docstring): a sentence-first name only warns (`name-first`,
  one line; noisy: 8-10 common words on each Uber script, none a name); titles are
  checked for numbers, not names; a number matches by value, not unit.
  **C2 partial**: a title may cite its fact id (`[^Fnn]`), not required (S05).
- The hash covers comments too (a comment edit needs a new signature). The skill
  may write the `Signed:` line on Franco's word: the log must say so.
- **For Franco**: respellings to add to `lexicon.tsv`? `UK` → U-K, `LeWeb` →
  Luh-WEB, `Rumayyan` → Roo-MY-yan (assumed pronunciations; not added).
- **Uber eval gaps** (not video 1's registry): beat 3 is the 2016 Saudi investment
  (the decision that made rides cheap is unsourced); no named taxi owner.
- Step 1 uses `zehon/content-maker/scripts/youtube.py` (French output): an English tool would be cleaner.
- `tests/fixtures/whosedime/factcheck_clean.md`: facts from memory, never a source.
  Style rules are weak evidence (n = 30): re-measure after video 10. Stale: ROADMAP
  rule 2, `whosedime/README.md`. No setup script. No graded critique yet.
