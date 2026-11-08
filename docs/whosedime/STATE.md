# Whose Dime — state

Short by rule (60 lines at most), updated at the end of every session. Plan: [`ROADMAP.md`](ROADMAP.md). Decisions: [`DECISIONS.md`](DECISIONS.md).

**Last update: 2026-11-08**, end of S08 Drive and pilot (session `session_01Cw13LgoA7ycfqFg8H2KvhJ`).

## Where we are

- **S01 to S07b in `main`** (merged 08/11). S08's docs (this file, the log, the S09 prompt) are on the work branch.
- **S08 done.** Drive tree `WhoseDime/` made, exactly as `memory.md` draws it: `Memory/` (`videos.md`, `lessons.md`),
  `Videos/01_uber/`, `Voice/candidates/`, and at the root `voice_launcher.ipynb` and `assembly_launcher.ipynb` (copied from
  `main` @ e6b9a64). **Measured**: tree listed back from Drive, no duplicate; launchers and video files the same size in
  bytes as the local copies (hash recomputed locally only).
- **Video 1, "Uber Was Cheap. Who Paid?"**: step 1 done (Franco: "Oui", 08/11); step 2 done, **waiting for Franco's signature**
  (Pause 2). `01_research.md`, `02b_factcheck.md` (43 facts: 42 verified, all read this session; 1 `[TO VERIFY]`; 19 people
  rows; fingerprint `sha256:18adbeeab4a0`), `00_state.md`. New against the eval: the decision is Kalanick's UberX price cut of
  January 9, 2014 ("all-in on being the cheapest ride in town"); the cold open is driver Fawzi Kamel's dashcam argument
  with Kalanick (Feb 2017); a named New York voice (Bhairavi Desai, 2021 hunger strike).

## Branches

| Branch | Role |
|---|---|
| `claude/great-planck-7hqn59` | **work branch**: S08 docs and the S09 prompt, on top of `main` |
| `main` | production (Colab launchers); has S01 to S07b |
| `claude/funny-dijkstra-js9xbz` | S07c prompt (its STATE is older) |
| `claude/zelan-studio-analysis-rws9f6` | old Zehon Drive launchers; leave it (Zehon frozen) |

## Tools

- Checker: `python3 whosedime/common/checker.py all FOLDER` (`scenes`, `voice SCRIPT VOICE`, `fingerprint FILE`). Skill sync:
  `python3 tools/sync_skills.py` (`--check`). Charts and assembly: `whosedime/whosedime-video/scripts/charts.py`, `assemble.py`.
- Tests: `python3 -m unittest discover -s tests` — **155 pass**, measured 08/11 (about 39 s). Fresh container: see `CLAUDE.md`.

## Sessions

| # | Status |
|---|---|
| S01 to S07b | **done**, merged 08/11 |
| S07c Chart follow-ups | prompt ready on `claude/funny-dijkstra-js9xbz`; before video 1's assembly |
| S08 Drive and pilot | **done** 08/11; video 1 waits for Franco's signature |
| S09 Competitor watch | **next** — prompt ready: [`sessions/S09_competitor_watch.md`](sessions/S09_competitor_watch.md) (Sonnet 5.5) |
| Video 1, skill session 2 | Script (Opus 5.5), once the fact check is signed |

## Open issues

- **For Franco, video 1**: sign `02b_factcheck.md`; F33 (Zohran Mamdani joined the 2021 hunger strike): use it or not
  (Claude: leave it out, political risk). Lexicon proposals: `UK` → U-K, `LeWeb` → Luh-WEB, `Rumayyan` → Roo-MY-yan,
  `Kamel` → Kuh-MEL, `Bhairavi Desai` → BY-ruh-vee Deh-SIGH (last two assumed).
- **For Franco, S05 choices** (assumed): the `title` card ("WHO PAYS?", navy); the palette in `palette.json` (gain green, loss coral, highlight mustard).
- **Research tools**: WebFetch's summariser never returns a page word for word (quotes asked as short exact quotes: a word could
  differ); web.archive.org refused; uber.com answers 406 to curl. Step 1 uses Zehon's `youtube.py` (French output).
- **Voice, to check on video 1**: the qwen-tts calls (never run); the 25 dB "still loud" threshold; stitched pauses; the T4 run
  time; narrator design in `Voice/`, 20 s sample, blind test (D7). **Not built**: a second voice for quoted lines; a speed lever.
- **Assembly, to check on video 1**: render time on Colab (30-45 min assumed); clips slowed x1.35 then frozen; band size.
  Years said in pairs ("twenty ten") do not match "2010". Not built: music bed, `.srt` subtitles.
- **Charts → S07c**: scene 82 colours people coral; scene 61's block floats high; phone sizes unchecked. **D12**: thumbnail A
  puts Kalanick by "$7.9 BILLION" (deficit to end 2018); he left in June 2017. Untested.
- **Checker limits**: `chart-source` checks numbers, not words; `prompt-person` sees only the people block; `name-first` noisy.
- **S09 scope cut**: the old brief's "externalities" (news, competitors' weaknesses) are planned nowhere. Fixture `factcheck_clean.md`: facts from memory. Stale: ROADMAP rule 2 branch. No setup script. Critique log: 33 lines, none graded.
