# Whose Dime — state

Short by rule (60 lines at most), updated at the end of every session. Plan: [`ROADMAP.md`](ROADMAP.md). Decisions: [`DECISIONS.md`](DECISIONS.md).

**Last update: 2026-11-08**, **PAUSED by Franco (D24)** — orchestrator `session_01Cw13LhWRZyGn7FWUAAzMb1`.

**⏸ Paused until Franco says otherwise (D24).** No session to open, no check-in scheduled. To resume: Pause 5 of video 1
(session 3), then images and clips by hand, reference voice (D23), pull request to `main` (S10-S12 code), assembly.

## Where we are

- **S01 to S09 and video 1's session 2a are in `main`** (PR #9, 08/11); S10 is on the work branch only.
- **Automation (D17-D19)**: a finishing session opens the next and reports to the orchestrator; content stays Franco's.
- **Video 1, "Uber Was Cheap. Who Paid?"**: fact check **signed** (`sha256:18adbeeab4a0` = fingerprint, restored after Drive's
  editor re-escaped it); outline validated; **script and voice version done** (2,089 words, `checker all` exit 0; Franco by ear 08/11).
  **D21-D22 / S12 done**: Franco makes one reference clip in ElevenLabs, `MODE = "reference"` makes `Voice/ref.*`, Qwen clones it ([guide](voice_elevenlabs_guide.md)).
- **S09** watch ([report](watch/2026-11-08.md)); **S10 (D15)** live guard `tools/guard/guard.py`, log [`guard_log.jsonl`](guard_log.jsonl).
- **S11 (D18)**: `whosedime/generate/` + Drive launcher `generate_launcher.ipynb` (needs `main`). **Measured**: no GPU, voice
  on CPU x6.1 real time (stays in Colab), $7.13/video by API; parked by Franco (D20: images by hand). [Report](generation_report.md).

## Branches

| Branch | Role |
|---|---|
| `claude/affectionate-heisenberg-k7i85k` | **work branch** for every session (fetch and rebase before each push: several run at once) |
| `main` | production (Colab launchers); has everything up to session 2a |
| `claude/zelan-studio-analysis-rws9f6` | old Zehon Drive launchers; leave it (Zehon frozen) |

## Tools

- Checker: `python3 whosedime/common/checker.py all FOLDER` (`scenes`, `voice SCRIPT VOICE`, `fingerprint FILE`). Skill sync:
  `python3 tools/sync_skills.py` (`--check`). Charts and assembly: `whosedime/whosedime-video/scripts/charts.py`, `assemble.py`.
- Watch: `python3 whosedime/watch/watch.py` (`--force` to rerun a date); commit the report, `channels.csv`, `last_run.json`.
- Tests: `python3 -m unittest discover -s tests` — **221 pass**, measured 08/11 after S12 (about 61 s). Fresh container: see `CLAUDE.md`.

## Sessions (all on the work branch; none running at the pause)

| # | Status |
|---|---|
| S01 to S10, video 1 session 2a | **done** |
| Video 1, session 2b | **done** (`session_01Cw13LeV77hvzZuF2iSsKfA`): script, voice version, 20 s sample; Franco passed E1-E5 on a generic TTS preview |
| S11 Generation pipeline | **done** ([report](generation_report.md)); **S11b parked** (D20) · **S12** ElevenLabs reference: **done** |
| Video 1, session 3 | **done up to Pause 5** (`session_01Cw13LhBRZjDKFbLZmN9hSM`): `03_scenes.md` (94 scenes, checker 0/0) and `04_publication.md` in Drive; Franco picks title and thumbnails |
| S07c Chart follow-ups | prompt [`sessions/S07c_chart_followups.md`](sessions/S07c_chart_followups.md); before video 1's assembly |
| Incoherence skill (meaning half) | waits for about 30 graded lines (42 lines, none graded) |

## Open issues

- **⏰ Reminder at video 2** (Franco, 08/11): remind him of D16, animated people blocks ([trial](trials/hyperframes_scene061/README.md)).
- **For Franco, video 1**: F33 (Mamdani) left out. Lexicon proposals: `UK` → U-K, `LeWeb` → Luh-WEB, `Rumayyan` →
  Roo-MY-yan, `Kamel` → Kuh-MEL, `Bhairavi Desai` → BY-ruh-vee Deh-SIGH. S05 choices (title card, palette) assumed.
- **Generation by API parked (D20)**: if revived, merge to `main`, Colab secret `GEMINI_API_KEY`, `MODE = "test"` ($0.98) first.
- **Voice (S12, D23)**: PR to `main` needed; Franco chose the free plan (non-commercial terms, risk told); use policy § 12 unclear for a cloning reference (guide § 4). *Assumed*: clone pace follows the reference.
- **Drive editor** re-escapes a `.md` it saves (breaks the hash): never edit video files there; no checker warning built.
- **Watch, assumed**: 48 channels; hits from 10 K views over 28 days; medians frozen at 5 Nov; no schedule.
- **Voice / assembly, to check on video 1**: qwen-tts ran on CPU (S11, similarity 1.0), not on a T4; 25 dB threshold; T4 time; Colab render time; clips x1.35;
  years said in pairs; no music, no `.srt`. **Charts → S07c**: scene 82 coral people, 61 block high, phone sizes.
- **Checker limits**: `chart-source` numbers only; `prompt-person` people block only; `name-first` noisy. WebFetch not word for word.
- **Guard**: 5 false blocks in S10 (shell parsing), fixed, tested; ~50 ms a call. *Assumed*: hooks load in every cloud session.
  `critique-missing` passes if any file name of the commit is in the log (weak). S07c's answers: next free D numbers.
