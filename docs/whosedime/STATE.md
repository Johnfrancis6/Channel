# Whose Dime — state

Short by rule (60 lines at most), updated at the end of every session. Plan: [`ROADMAP.md`](ROADMAP.md). Decisions: [`DECISIONS.md`](DECISIONS.md).

**Last update: 2026-11-16**, S14b Whisper CPU fallback after S14 (upload, D32). **Orchestrator**: `session_01Cw13LeFBwzXQBL4SqwTyRi` (sessions report to it, D19).

## Where we are

- **One line of work again** on `claude/s13-reconcile` ([report](reconcile_report.md)): `main` (S01-S10, S07c, D29 language,
  French market report) + the 08/11 branch (S11, S12, video 1 sessions 2b and 3, D16-D24) + the 15-16/11 STATE. [PR 12](https://github.com/Johnfrancis6/Channel/pull/12)
  **merged into `main` 16/11** (S11, S12 now in `main`); D30-D33 (`9cf657f`) came after it and ride in [PR 13](https://github.com/Johnfrancis6/Channel/pull/13).
- **Guard (S10, D15)** and **watch**: `main`'s versions kept, 08/11 fixes ported (`2>&1` no longer a push target; list in the report).
- **16/11, Franco**: decision numbers unique (D30: S07c's are D26-D28, old language D29); answer in his language, pipeline in
  English (D31); **he uploads the voice clip and its text in Colab** (D32, built by S14); he only grants permissions and answers (D33).
- **S14 (D32)**: `MODE = "reference"` asks for the upload (clip + `.txt` or `REFERENCE_TEXT`; old clip to `Voice/old/`; nothing
  uploaded = Drive clip), then the S12 import ([guide](voice_elevenlabs_guide.md) § 2-3). [PR 13](https://github.com/Johnfrancis6/Channel/pull/13). Not run in Colab (Cancel = empty, assumed).
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
| `claude/s13-reconcile` | S13 + D30-D33, [PR 12](https://github.com/Johnfrancis6/Channel/pull/12) to `main`; holds `claude/affectionate-heisenberg-k7i85k` and `claude/v1-s2b-script-uber` (keep both until it merges) |
| `claude/s14b-whisper-cpu-fallback` | **work branch**: Whisper falls back to the CPU when Colab lacks CUDA 12's `libcublas.so.12` |
| `main` | production (Colab launchers): S01-S14 and D30-D33 (PRs 12, 13 merged 16/11) |
| `claude/zelan-studio-analysis-rws9f6` | old Zehon Drive launchers; leave it (Zehon frozen) |

## Tools

- Checker: `python3 whosedime/common/checker.py all FOLDER`. Skill sync: `python3 tools/sync_skills.py` (`--check`).
- Charts and assembly: `whosedime/whosedime-video/scripts/charts.py`, `assemble.py`. Generation (parked): `whosedime/generate/run.py`.
- Watch: `python3 whosedime/watch/watch.py` (`--no-search`, `--refresh-medians`, `--force`).
- Tests: `python3 -m unittest discover -s tests` — **246 pass, measured 16/11 after S14b** (244 after S14). Fresh container: see `CLAUDE.md`.

## Sessions

| # | Status |
|---|---|
| S01 to S12, S07c, video 1 sessions 2a, 2b, 3 and Pause 5 | **done**, in `main` |
| S13 Reconcile branches | **done** 16/11, PR 12 merged |
| S14, S14b Voice upload (D32), Whisper CPU fallback | S14 merged; Colab 16/11: upload OK, Whisper crashed (no `libcublas.so.12`): S14b PR waits |
| Video 1 voice (Franco's, not a session) | once PR 13 is merged: launcher `MODE = "reference"` (upload clip + text), `"sample"`, listen (D6), `"full"` |
| S15 Voice pace advice, launcher output | **open** 16/11: [`sessions/S15_voice_rate_advice.md`](sessions/S15_voice_rate_advice.md); Franco remakes the reference slower |
| Incoherence skill (meaning half) | waits for about 30 graded lines |

## Open issues

- **For Franco, video 1**: F33 (Mamdani) left out. Lexicon: `UK` → U-K, `LeWeb` → Luh-WEB, `Rumayyan` → Roo-MY-yan,
  `Kamel` → Kuh-MEL, `Bhairavi Desai` → BY-ruh-vee Deh-SIGH. E1-E5 passed on a generic TTS, not the channel voice.
- **Guard**: not ported from 08/11: French check of files made by shell, per-file critique match. Hooks reach only clones
  with `.claude/settings.json`. **Voice (D23)**: free-plan terms non-commercial; § 12 unclear for a cloning reference.
- **Watch**: medians frozen at 5 Nov; no schedule. **Drive editor** re-escapes `.md` (breaks the hash). **Out of scope**:
  the old brief's "externalities"; ROADMAP rule 2 names a stale branch; no setup script.
