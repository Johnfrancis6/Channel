# Whose Dime — state

Short by rule (60 lines at most). Updated at the end of every session.
Plan: [`ROADMAP.md`](ROADMAP.md). Decisions: [`DECISIONS.md`](DECISIONS.md).

**Last update: 2026-11-07**, end of S06 Voice notebook
(session `session_01Cw13LfRa4GCC21GBnVChJV`).

## Where we are

- **S01 to S05 done and merged** into `main` ([Johnfrancis6/Channel#2](https://github.com/Johnfrancis6/Channel/pull/2),
  [Johnfrancis6/Channel#3](https://github.com/Johnfrancis6/Channel/pull/3)). No Drive folder yet (S08).
- **S06 done, on the work branch, not in `main`** (no PR: S07 ends with one).
  - Task 0, D12: thumbnail prompts name the well-known executive (checklist, model, fallback in
    [`step5_publication.md`](../../whosedime/whosedime-maker/references/step5_publication.md)); Uber prompt A names Kalanick. `checker.py all` exit 0.
  - Voice notebook [`whosedime/notebooks/`](../../whosedime/notebooks/README.md): blocks of 2-4 sentences, pauses
    250/450/700 ms, dry-ending detector (2 retries, then flag), `words.json`, `state.json` with both rates,
    20 s sample gate (D6), checker gate (D4), VoiceDesign then clone (D8), blind test (D7), launcher on `main`.
  - **Measured**: runs end to end on the Uber eval text with a stub model; detector flags a cut clip, passes a clean one.
    **Not run**: the real models (no GPU here). First real run: S08, by Franco.

## Branches

| Branch | Role |
|---|---|
| `claude/blissful-tesla-abtjgt` | **work branch** for build sessions (S06 commits on top of `main`) |
| `main` | production (Colab launchers); has S01 to S05, not S06 yet |
| `claude/zelan-studio-analysis-rws9f6` | old Zehon Drive launchers; leave it (Zehon frozen) |

## Tools

- Checker: `python3 whosedime/common/checker.py all FOLDER` (`scenes`, `voice SCRIPT VOICE`, `fingerprint FILE`).
- Skill sync: `python3 tools/sync_skills.py` (`--check` reports drift).
- Tests: `python3 -m unittest discover -s tests` — **125 pass**, measured 07/11. Fresh container: see `CLAUDE.md`.

## Sessions

| # | Status |
|---|---|
| S01 to S06 | **done** 07/11 (S06 waits for the S07 pull request) |
| S07 Charts and assembly | **next** — prompt ready: [`sessions/S07_charts_and_assembly.md`](sessions/S07_charts_and_assembly.md) |
| S08, S09 | planned in `ROADMAP.md` |

## Open issues

- **For Franco** (S05 choices, assumed): a 5th scene type `title` (the "WHO PAYS?" card); the channel
  palette (cream, dollar green, coral, mustard, navy). Lexicon: `UK` → U-K, `LeWeb` → Luh-WEB, `Rumayyan` → Roo-MY-yan?
- **Voice, to check on video 1 (S08)**: the qwen-tts calls (read from 0.1.1's source, never run); the 25 dB "still loud"
  threshold; whether lengthened pauses sound stitched (`stretch_inner_pauses`); the T4 run time.
- **Voice, not built**: the second VoiceDesign voice for quoted lines (`voice_direction.md`); a speed lever if
  `rate_total_wpm` leaves 142-154 (qwen-tts has no speed argument). Blind test = 7 block pairs (20 sentences),
  not 20 sentence pairs: pass rule becomes "A preferred at most 1 of 7".
- **Drive (S08)**: the narrator lives in `WhoseDime/Voice/` (`ref.wav`, `candidates/`); create it with the tree.
- **D12**: thumbnail A puts Kalanick by "$7.9 BILLION" (deficit to end 2018, F13); he left in June 2017 (F11). Untested.
- **Checker limits**: `chart-source` checks numbers, not words; `prompt-person` sees only the people block;
  `name-first` noisy (script 10 words, publication 3); two tokenisers (2,103 vs 2,087 words); numbers match by value.
- The palette lives in `step4_scenes.md` and each `03_scenes.md`: S07 should read one source (C5).
- Uber eval: beat 3 is the 2016 Saudi investment; no named taxi owner; F05 (an estimate) in 3 of 25 charts.
- Step 1 uses Zehon's `youtube.py` (French output). Fixture `factcheck_clean.md`: facts from memory. Stale: ROADMAP rule 2 branch name,
  `whosedime/README.md`. No setup script. No graded critique yet.
