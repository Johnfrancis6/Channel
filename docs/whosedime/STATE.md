# Whose Dime — state

Short by rule (60 lines at most). Updated at the end of every session.
Plan: [`ROADMAP.md`](ROADMAP.md). Decisions: [`DECISIONS.md`](DECISIONS.md).

**Last update: 2026-11-07**, end of S01 Foundations (session
`session_01Cw13Lf58VEKf76zGZT5j1e`).

## Where we are

- **S01 done.** The latest Zehon pipeline (`claude/optimistic-bohr-5f78k4`)
  is merged into the work branch; Zehon is frozen (note at the top of
  `docs/chaine2/CONTEXTE.md`); `CLAUDE.md` is in English;
  `whosedime/README.md` lays out the folders to come.
- **Pull request to `main` open, not merged**: PR_LINK. Until
  Franco merges it, `main` is still the 30/09 state (`f5ceed8`).
- Nothing of the Whose Dime content pipeline is built yet (S02 onwards).
- No Whose Dime Drive folder exists yet (S08).

## Branches

| Branch | Role |
|---|---|
| `claude/admiring-ramanujan-k2uiqe` | **work branch** for build sessions |
| `main` | production (Colab launchers); updated by Franco merging the S01 PR |
| `claude/optimistic-bohr-5f78k4` | merged into the work branch in S01; no longer needed |
| `claude/zelan-studio-analysis-rws9f6` | old branch of the Zehon Drive launchers; leave it (Zehon frozen) |

## Tools

- Skill sync, both channels: `python3 tools/sync_skills.py` (`--check`
  reports drift, exit 1). Each mirror and `.skill` carries a `VERSION`
  (12 hex of a SHA-256 of the source): content-maker `a591260cd5a4`,
  video-maker `46af448aa034`. `zehon/synchroniser_skills.py` is a wrapper.
- Tests: `python3 -m unittest discover -s tests` — **33 pass** (26 merged
  + 7 sync), measured 07/11. A fresh container needs
  `apt-get update && apt-get install -y ffmpeg` and
  `pip install opencv-python-headless pillow numpy` (also in `CLAUDE.md`).

## Sessions

| # | Status |
|---|---|
| S01 Foundations | **done** 07/11 |
| S02 Storytelling rules | **next** — prompt ready: [`sessions/S02_storytelling_rules.md`](sessions/S02_storytelling_rules.md) |
| S03 to S09 | planned in `ROADMAP.md` |

## Open issues

- **No container setup script.** This session runs on the Default
  environment (unrestricted network, the two API keys as variables). The
  environment rules forbid a repository setup script on the Default, and a
  new personal environment is always network-limited and would not carry
  the keys, which breaks web research and the API calls. Not proposed;
  commands written in `CLAUDE.md` instead. Franco can add the script by
  hand in the environment settings if he wants it.
- The critique log has no graded line yet.
- `docs/chaine2/CONTEXTE.md` still names `claude/optimistic-bohr-5f78k4`
  as the Zehon work branch: left as is (Zehon frozen; only the state
  block was to change).
