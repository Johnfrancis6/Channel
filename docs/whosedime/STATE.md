# Whose Dime — state

Short by rule (60 lines at most), updated at the end of every session. Plan: [`ROADMAP.md`](ROADMAP.md). Decisions: [`DECISIONS.md`](DECISIONS.md).

**Last update: 2026-11-16**, S13 reconcile (session `session_01Cw13LeFBwzXQBL4SqwTyRi`). **D25: pause lifted.**

## Where we are

- **One line of work again** on `claude/s13-reconcile` ([report](reconcile_report.md)): `main` (S01-S10, S07c, D17 language,
  French market report) + the 08/11 branch (S11, S12, video 1 sessions 2b and 3, D16-D24) + the 15-16/11 STATE. Pull request
  to `main` open; **Franco merges it** (the S12 voice notebook and the S11 launcher need `main`).
- **Guard (S10, D15)** and **watch**: `main`'s versions kept, 08/11 fixes ported (`2>&1` no longer a push target; list in the report).
- **S11 (D18)** `whosedime/generate/` + `generate_launcher.ipynb`: $7.13/video by API, **parked** (D20: images by hand).
  [Report](generation_report.md). **S12 (D21-D23)**: Franco makes one ElevenLabs reference clip (free plan, risk told);
  `MODE = "reference"` turns it into `Voice/ref.*`, Qwen3-TTS clones it ([guide](voice_elevenlabs_guide.md)).
- **Video 1, "Uber Was Cheap. Who Paid?"** (Drive `WhoseDime/Videos/01_uber/`, its `00_state.md` rewritten 15/11):
  - Steps 1-5 written (fact check signed `sha256:18adbeeab4a0`; script 2,089 words; 94 scenes; publication).
  - **Measured 15/11**: `checker.py all` exit 0 on the raw Drive files; fingerprint = Signed line.
  - **Pause 5 answered 16/11**: title "Uber Lost $7.9 Billion. Uber's history" (F26; Franco's), thumbnails A, B, C, A first.
  - Pieces: `miniatures/` 3 of 3, `images/` 0 of 55, `clips/` 0 of 5. Then voice (D23), assembly. Stale prompt: `V1_S2b_script.md`.

## Branches

| Branch | Role |
|---|---|
| `claude/s13-reconcile` | **work branch** (S13), pull request to `main` |
| `main` | production (Colab launchers): S01-S10, S07c; gets S11, S12 with the S13 pull request |
| `claude/affectionate-heisenberg-k7i85k`, `claude/v1-s2b-script-uber` | merged into the work branch; keep until the PR merges |
| `claude/zelan-studio-analysis-rws9f6` | old Zehon Drive launchers; leave it (Zehon frozen) |

## Tools

- Checker: `python3 whosedime/common/checker.py all FOLDER`. Skill sync: `python3 tools/sync_skills.py` (`--check`).
- Charts and assembly: `whosedime/whosedime-video/scripts/charts.py`, `assemble.py`. Generation (parked): `whosedime/generate/run.py`.
- Watch: `python3 whosedime/watch/watch.py` (`--no-search`, `--refresh-medians`, `--force`).
- Tests: `python3 -m unittest discover -s tests` — **measured 16/11 after S13** (see the report). Fresh container: see `CLAUDE.md`.

## Sessions

| # | Status |
|---|---|
| S01 to S12, S07c, video 1 sessions 2a, 2b, 3 and Pause 5 | **done**; in `main` once the S13 pull request is merged |
| S13 Reconcile branches | **done** 16/11, pull request waits for Franco |
| Video 1 pieces | Franco: 55 images, 5 clips, reference voice (ElevenLabs, D23) |
| Voice session (S12 notebook, `MODE = "reference"`) | **next** after the merge (prompt to write) |
| Incoherence skill (meaning half) | waits for about 30 graded lines |

## Open issues

- **Decision numbers used twice or three times** (three branches on 08/11): D14 (watch list / money-only colour), D15 (live
  guard / one value line), D16 (animated people / palette kept), D17 (sessions chain themselves / English with Franco).
  S13 kept every section as written. Recommended: renumber S07c's three to D26-D28 and the language one to D29; Franco picks.
- **Language with Franco**: D17 (08/11) says English; Franco wrote French on 15-16/11 and was answered in French. CLAUDE.md now
  says "the language he writes in"; Franco to confirm.
- **For Franco, video 1**: F33 (Mamdani) left out. Lexicon: `UK` → U-K, `LeWeb` → Luh-WEB, `Rumayyan` → Roo-MY-yan,
  `Kamel` → Kuh-MEL, `Bhairavi Desai` → BY-ruh-vee Deh-SIGH. E1-E5 passed on a generic TTS, not the channel voice.
- **Guard**: not ported from 08/11: French check of files made by shell, per-file critique match. Hooks reach only clones
  with `.claude/settings.json`. **Voice (D23)**: free-plan terms non-commercial; § 12 unclear for a cloning reference.
- **Watch**: medians frozen at 5 Nov; no schedule. **Drive editor** re-escapes `.md` (breaks the hash). **Out of scope**:
  the old brief's "externalities"; ROADMAP rule 2 names a stale branch; no setup script.
