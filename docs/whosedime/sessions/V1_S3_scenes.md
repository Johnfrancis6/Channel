# Video 1, skill session 3 — Scenes and publication (Uber)

> Opened by session 2b (2026-11-08, `session_01Cw13LeV77hvzZuF2iSsKfA`). Step 3 is done:
> **Franco passed the 20 s sample on E1-E5** ("Oui, ça passe E1 à E5", 08/11, heard on a
> generic Google TTS preview, not the channel voice). This session does steps **4 and 5** of the
> `whosedime-maker` skill and stops at **Pause 5** (title and thumbnail trio).
> Changes since the plan: D20 (images and clips made by Franco by hand, so prompts must be ready
> to paste) and D21 (the narrator will be an ElevenLabs voice Franco picks; not this session's job).

## Setup

```bash
git fetch origin claude/affectionate-heisenberg-k7i85k
git checkout claude/affectionate-heisenberg-k7i85k   # or the branch STATE.md names
python3 -m unittest discover -s tests                # green before you start (count in STATE.md)
```

Fresh container: `apt-get update && apt-get install -y ffmpeg` and
`pip install opencv-python-headless pillow numpy` (needed by the tests only).
Model: Sonnet 5.5. Connector: Google Drive.

## Read (in this order)

1. `docs/whosedime/STATE.md`, then `docs/whosedime/DECISIONS.md` D12, D13, D16 (not for video 1), D20, D21.
2. The skill `whosedime-maker` (invoke it): `SKILL.md`, then `references/step4_scenes.md`,
   `references/step5_publication.md` and `references/memory.md`.
3. In Drive, `WhoseDime/Videos/01_uber/`: `00_state.md`, `02_script.md` (the words the scenes must
   hold, word for word), `02b_factcheck.md` (chart facts), `02_script_voice.txt`, `01_research.md`.
   Download them **raw** (`download_file_content`, base64) into a scratchpad folder: the checker needs
   the exact bytes. Drive file ids at the end of 2b: script `1x0wiwAYp1ViPBr7mt0C7VRbTh0MUMC65`,
   voice `1yWhsBaEvDiXlIXL8y_8LsJ6A0nJX-TUJ`, registry `1p3nkIhV_rAXNkeLuNNP_yPYwE-sHfsLR`
   (list the folder anyway: the folder wins over this list).

## First check (2 minutes)

- `python3 whosedime/common/checker.py fingerprint <folder>/02b_factcheck.md` prints `sha256:18adbeeab4a0`
  (the value on its `Signed:` line). If not, **stop** and tell Franco; never touch the signature line.
- `python3 whosedime/common/checker.py all <folder>` exits 0 (expected: 1 warning, `name-first`, common words).

## Do

1. **Step 4, scenes** (`03_scenes.md`), per `step4_scenes.md` and the `scenes` targets of
   `whosedime/common/settings.json` (85-95 scenes, 50-55 images, 25-30 charts, 4-5 clips, 6 chapter
   cards, 1 title card at the start of the setup). The spoken text of the scenes, put end to end, is
   `02_script.md` word for word: never fix a sentence in a scene, change the script first (then the
   voice version, then the checker). Every chart cites `verified` fact ids and shows only their numbers.
   Scene prompts stay **anonymous** (no person of the people block named: the checker blocks it).
   Since D20, the Gemini image prompts and Flow clip prompts must be **ready to paste** by Franco.
   Run `python3 whosedime/common/checker.py scenes <folder>/03_scenes.md` after each draft.
2. **Step 5, publication** (`04_publication.md`), per `step5_publication.md`: titles of 40 characters
   at most, a number in a title or thumbnail line carries its `[^Fnn]`, thumbnail trio (D12: the
   thumbnail may caricature Kalanick, never a realistic portrait), description with chapters and sources.
   Then `python3 whosedime/common/checker.py all <folder>` must exit 0.
3. **Pause 5**, as `step5_publication.md` says: one recommendation, one question.
4. After Franco's answer: grade question, one line each in `docs/whosedime/critique_log.jsonl`
   (`4_scenes`, `5_publication`), `00_state.md` and the `Memory/videos.md` row rewritten in Drive
   (new file, then the old one to the bin), STATE.md (60 lines at most: the guard warns), commit, push.
5. **Hand-off (D17, D19)**: write the next prompt. Two candidates, choose with STATE.md: the **voice
   session for D21** (ElevenLabs: how Franco makes the voice, `voice.wav` and `words.json`, cost asked,
   never assumed) and **S07c chart follow-ups** (before the assembly). Open it with `create_session`
   and report to the orchestrator `session_01Cw13LhWRZyGn7FWUAAzMb1` with `send_message`.

## What session 2b learned (keep it)

- **The orchestrator re-reads for invented detail.** It caught three: a gesture no source describes
  ("Kalanick doesn't blink"), a cause the registry does not hold (the $7.9 billion deficit spent
  "so your ride could stay cheap"), and a citation that did not say what the sentence said (F32 for
  "huge loans to buy one"). Image prompts and on-screen texts are held to the same rule: a scene may
  show a dashcam view, a snowy Paris street, a medallion; it may not show what no source says happened.
- **Words in the script that are not registered facts but are kept**: "riding in the back seat"
  (inferred from F17, the validated outline's wording) and Kamel's "We started with $20" (no unit in
  F19; framed only as his words). Do not add an on-screen unit or caption that turns either into a fact.
- **Checker behaviour measured in 2b**: the respelling of a name does not apply to its possessive in the
  voice check ("Kalanick's" drifts from "Kuh-LAN-ick's"), so the script avoids it; a price with a
  trailing zero ("$4.90") cannot be spelled to match, so it was left out; S7 (numbers) sits at 2.53 per
  100 words against 2.6: on-screen numbers belong to the scenes, but the spoken text cannot gain any.
- **Chart-ready facts the script says aloud**: F08 (41%), F05 (311 cities), F41 (26 million trips a
  day), F06 (34 percent, 15 other cities), F09 ($2 billion lost on $1.4 billion), F10, F11 ($3.5
  billion), F26 ($7.9 billion), F27 ($45), F14 ($90,000 vs $61,000), F15 ($140 vs $160), F13 ($20
  million), F20 (20 to 25 percent), F18 ($97,000, his claim: say so on screen), F28 ($1 million), F29
  (late 2014, 950), F31 (15-day), F32 ($200,000, $1,122), F35 (20%), F38 (40,000), F39 ($9.1 billion),
  F40 ($1.1 billion). F33 (Mamdani) and F43 (`[TO VERIFY]`) are not used.
- **The 20 s sample was heard on a generic TTS** (gTTS, slower than 149 wpm): the real speaking rate
  and timbre are unknown until the ElevenLabs voice exists (D21). Scene timings are estimates.
- Write Drive files with `create_file` (`text/markdown`, `disableConversionToGoogleType: true`), then
  compare the size Drive reports with the local file; never ask Franco to edit a `.md` in Drive's editor.

## Watch out

- Stop at Pause 5. Making images, clips, the voice and the render are not this session's.
- Several sessions push to the work branch: `git fetch` and rebase before every push; keep both sides of
  `STATE.md` and `critique_log.jsonl`.

## Hand-off

Per `ROADMAP.md`, "The hand-off" (D17-D19). Next: the voice session for D21 or S07c, model per the
session table.
