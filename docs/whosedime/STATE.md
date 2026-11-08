# Whose Dime — state

Short by rule (60 lines at most), updated at the end of every session. Plan: [`ROADMAP.md`](ROADMAP.md). Decisions: [`DECISIONS.md`](DECISIONS.md).

**Last update: 2026-11-08**, video 1 session 2a + automation (orchestrator `session_01Cw13LhWRZyGn7FWUAAzMb1`).

## Where we are

- **S01 to S09 and video 1's session 2a are in `main`** (Franco merged PR #9, 08/11). The GitHub merge had mixed two
  STATE.md versions and dropped D16 from DECISIONS.md: both rebuilt here.
- **Automation (D17-D19, Franco 08/11)**: a session that finishes opens the next one (`create_session`) and reports to the
  orchestrator session; technical choices are Claude's, content stays at Franco's pauses; Franco is told when images,
  clips, voice and render are made. Hand-off in `ROADMAP.md` and the `whosedime-maker` skill.
- **Video 1, "Uber Was Cheap. Who Paid?"**: fact check **signed** (`sha256:18adbeeab4a0` = fingerprint); outline
  `02a_outline.md` **validated** 08/11 (2,060 words planned; payers: investors, drivers, NY medallion owners).
  **Measured**: Drive's editor had re-escaped the signed file (hash `adbb19fb1ab6`); the exact S08 upload, equal once
  unescaped, hashes `18adbeeab4a0`: restored with Franco's signature line unchanged (old copy in the Drive bin).
- **S09**: weekly watch `python3 whosedime/watch/watch.py`; first report [`watch/2026-11-08.md`](watch/2026-11-08.md).
- **S07b**: colour by meaning (D13); charts and assembly measured on a 10-scene stub; not run with real voice or images.

## Branches

| Branch | Role |
|---|---|
| `claude/affectionate-heisenberg-k7i85k` | **work branch** for every session (fetch and rebase before each push: several run at once) |
| `main` | production (Colab launchers); has everything up to session 2a |
| `claude/zelan-studio-analysis-rws9f6` | old Zehon Drive launchers; leave it (Zehon frozen) |

## Tools

- Checker: `python3 whosedime/common/checker.py all FOLDER` (`scenes`, `voice SCRIPT VOICE`, `fingerprint FILE`). Skill sync:
  `python3 tools/sync_skills.py` (`--check`). Charts and assembly: `whosedime/whosedime-video/scripts/charts.py`, `assemble.py`.
- Watch: `python3 whosedime/watch/watch.py`; commit the report, `channels.csv` and `last_run.json` after each run.
- Tests: `python3 -m unittest discover -s tests` — **167 pass**, measured 08/11 (about 35 s). Fresh container: see `CLAUDE.md`.

## Sessions (opened by the orchestrator on 08/11, all on the work branch)

| # | Status |
|---|---|
| S01 to S09, video 1 session 2a | **done** |
| Video 1, session 2b | **at Pause 4** (`session_01Cw13LeV77hvzZuF2iSsKfA`): `02_script.md` (2,096 words), `02_script_voice.txt`, `02c_listen_20s.txt` in Drive; `checker.py all` exit 0, 1 warning (`name-first`, common words); waits for Franco's ear |
| S10 Live guard | **opened** (D15, Opus 5.5), [`sessions/S10_live_guard.md`](sessions/S10_live_guard.md) |
| S11 Generation pipeline | **opened** (D17-D19, Opus 5.5), [`sessions/S11_generation_pipeline.md`](sessions/S11_generation_pipeline.md): images, clips, voice, Drive transfer |
| Video 1, session 3 | opened by 2b after Pause 4: scenes and publication (Sonnet 5.5) |
| S07c Chart follow-ups | prompt [`sessions/S07c_chart_followups.md`](sessions/S07c_chart_followups.md); before video 1's assembly |
| Incoherence skill (meaning half) | waits for about 30 graded lines (37 lines, none graded) |

## Open issues

- **⏰ Reminder at video 2** (Franco, 08/11): remind him of D16, animated people blocks ([trial](trials/hyperframes_scene061/README.md)).
- **For Franco, video 1**: F33 (Mamdani) left out. Lexicon proposals: `UK` → U-K, `LeWeb` → Luh-WEB, `Rumayyan` →
  Roo-MY-yan, `Kamel` → Kuh-MEL, `Bhairavi Desai` → BY-ruh-vee Deh-SIGH. S05 choices (title card, palette) assumed.
- **Generation needs money**: images and clips by API need a paid Gemini key (S11 asks Franco with the price first).
- **Decision numbers**: S07c's prompt reserved D14-D15, since used by the watch and the guard: its answers take the next free numbers.
- **Drive editor** re-escapes a `.md` it saves (breaks the hash): never edit video files there; no checker warning built.
- **Watch, assumed**: 48 channels; hits from 10 K views over 28 days; medians frozen at 5 Nov; no schedule.
- **Voice / assembly, to check on video 1**: qwen-tts never run; 25 dB threshold; T4 time; Colab render time; clips x1.35;
  years said in pairs; no music, no `.srt`. **Charts → S07c**: scene 82 coral people, 61 block high, phone sizes.
- **Checker limits**: `chart-source` numbers only; `prompt-person` people block only; `name-first` noisy.
- Research tools: WebFetch never word for word; web.archive.org refused. Fixture `factcheck_clean.md` from memory. No setup script.
