# Whose Dime — state

Short by rule (60 lines at most), updated at the end of every session. Plan: [`ROADMAP.md`](ROADMAP.md). Decisions: [`DECISIONS.md`](DECISIONS.md).

**Last update: 2026-11-18**, video 1 voice done and validated by Franco. **Orchestrator**: `session_01Cw13LeFBwzXQBL4SqwTyRi` (sessions report to it, D19).

## Where we are

- **One line of work again** ([S13 report](reconcile_report.md)): S11, S12, video 1 sessions 2b and 3, D16-D33 all in `main`
  ([PR 12](https://github.com/Johnfrancis6/Channel/pull/12), [PR 13](https://github.com/Johnfrancis6/Channel/pull/13), [PR 14](https://github.com/Johnfrancis6/Channel/pull/14), merged 16/11).
- **Guard (S10, D15)** and **watch**: `main`'s versions kept, 08/11 fixes ported (`2>&1` no longer a push target; list in the report).
- **16/11, Franco**: decision numbers unique (D30: S07c's are D26-D28, old language D29); answer in his language, pipeline in
  English (D31); **he uploads the voice clip and its text in Colab** (D32, built by S14); he only grants permissions and answers (D33).
- **S14 (D32)**: `MODE = "reference"` asks for the upload (clip + `.txt`), then the S12 import ([guide](voice_elevenlabs_guide.md) § 2-3); run in Colab 16/11, works.
- **S15**: both steps say "multiply your ElevenLabs Speed by F" (F = aim / measured); `listen_20s.json` keeps the clone/reference ratio (x1.12 on 16/11).
- **S11 (D18)** `whosedime/generate/` + `generate_launcher.ipynb`: $7.13/video by API, **parked** (D20: images by hand).
  [Report](generation_report.md). **S12 (D21-D23)**: Franco makes one ElevenLabs reference clip (free plan, risk told);
  `MODE = "reference"` turns it into `Voice/ref.*`, Qwen3-TTS clones it ([guide](voice_elevenlabs_guide.md)).
- **Video 1, "Uber Was Cheap. Who Paid?"** (Drive `WhoseDime/Videos/01_uber/`, its `00_state.md` rewritten 15/11):
  - Steps 1-5 written (fact check signed `sha256:18adbeeab4a0`; script 2,089 words; 94 scenes; publication).
  - **Measured 15/11**: `checker.py all` exit 0 on the raw Drive files; fingerprint = Signed line.
  - **Pause 5 answered 16/11**: title "Uber Lost $7.9 Billion. Uber's history" (F26; Franco's), thumbnails A, B, C, A first.
  - **Voice done 17/11** (narrator `d5211b92cf2b`): 13 min 47 s, 157.0 wpm total (near target), 0 low similarity; blocks 29, 43
    flagged, **Franco listened: OK** (18/11). Pieces: `miniatures/` 3 of 3, `images/` 0 of 55, `clips/` 0 of 5. Then assembly.

## Branches

| Branch | Role |
|---|---|
| `claude/s13-reconcile` | S13 + D30-D33, [PR 12](https://github.com/Johnfrancis6/Channel/pull/12) to `main`; holds `claude/affectionate-heisenberg-k7i85k` and `claude/v1-s2b-script-uber` (keep both until it merges) |
| `claude/v1-voice-done` | STATE only, video 1 voice done; PR to `main` |
| `main` | production (Colab launchers): S01-S14b and D30-D33 (PRs 12, 13, 14 merged 16/11) |
| `claude/zelan-studio-analysis-rws9f6` | old Zehon Drive launchers; leave it (Zehon frozen) |

## Tools

- Checker: `python3 whosedime/common/checker.py all FOLDER`. Skill sync: `python3 tools/sync_skills.py` (`--check`).
- Charts and assembly: `whosedime/whosedime-video/scripts/charts.py`, `assemble.py`. Generation (parked): `whosedime/generate/run.py`.
- Watch: `python3 whosedime/watch/watch.py` (`--no-search`, `--refresh-medians`, `--force`).
- Tests: `python3 -m unittest discover -s tests` — **252 pass, measured 17/11 after S15b** (250 after S15). Fresh container: see `CLAUDE.md`.

## Sessions

| # | Status |
|---|---|
| S01 to S13, S07c, video 1 sessions 2a, 2b, 3 and Pause 5 | **done**, in `main` (S13: PR 12) |
| Video 1 voice | **done** 17/11, validated 18/11 · next: Franco's 55 images, 5 clips (prompts in `03_scenes.md`), then the assembly session |
| S14-S15b Voice upload, CPU fallback, pace advice, GPU memory | **done**, merged (PRs 13-16); `full` ran 18 min on a T4 (17/11) |
| Incoherence skill (meaning half) | waits for about 30 graded lines |

## Open issues

- **For Franco, video 1**: F33 (Mamdani) left out. Lexicon: `UK` → U-K, `LeWeb` → Luh-WEB, `Rumayyan` → Roo-MY-yan,
  `Kamel` → Kuh-MEL, `Bhairavi Desai` → BY-ruh-vee Deh-SIGH. E1-E5 passed on a generic TTS, not the channel voice.
- **Guard**: false block on `git checkout -b NEW && git push -u origin NEW` (reads HEAD first); S15's fix was denied by
  the permission classifier (guard = oversight): Franco decides. Not ported from 08/11: French check of shell-made files,
  per-file critique match. Hooks reach only clones with `.claude/settings.json`. **Voice (D23)**: free plan non-commercial; § 12 unclear.
- **Voice notebook**: a ready voice gives "No video waiting for its voice" plus an IPython traceback (confusing). **Watch**: medians
  frozen at 5 Nov; no schedule. **Drive editor** re-escapes `.md` (breaks the hash). **Out of scope**:
  the old brief's "externalities"; ROADMAP rule 2 names a stale branch; no setup script.
