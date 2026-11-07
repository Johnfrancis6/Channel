# Memory: where the videos are (audit C4)

A skill remembers nothing between conversations. Whose Dime's memory is
**files in Drive**, and they must say **the truth**: a step is done when
its files are in the folder and pass their check, not because a
conversation said so (the Zehon audit found states that stopped at the
script while the video was rendered: P2, P3).

```
WhoseDime/
  Memory/
    videos.md          the index: every video, its step, its next action
    lessons.md         results after publication, measured settings, the experiment in progress
  Videos/
    01_uber/
      00_state.md      the state of this video: every step, rewritten at the end of each step
      01_research.md ... 04_publication.md, images/, charts/, clips/, voice/, render/
```

(The tree is created by build session S08. Until then: the local work
folder only, and say so.) The pronunciation lexicon is **not** in Drive:
it is `whosedime/common/lexicon.tsv` in the repo, the one list the checker
and the voice read (audit C5); a proposed respelling waits in the video's
`00_state.md` until Franco agrees.

## "Where are the videos?"

Read `Memory/videos.md`, then the `00_state.md` of each video **in
progress**, then list the folder of the one you work on. Answer one line
per video: folder, step reached, next action, who does it (Franco or
Claude), date of the state. If `videos.md` and a `00_state.md` disagree,
the state file wins; if the state file and the folder disagree (a file it
calls done is missing, or a file is there that it does not list), **the
folder wins**: say so, and rewrite the state file from the folder.

## `00_state.md` (in each video folder)

Rewritten **whole** (never appended to) at the end of every step, and at
the start of a session when the folder shows that Franco did something
outside (images made, voice written, video published):

```markdown
# State — 01_uber "Uber Was Cheap. Who Paid?"

Updated: 2026-11-20, session <link>, after step 5
Next: Franco makes the images (batches 1-6) and the 5 Flow clips, then the voice in Colab
Waiting for Franco: title and thumbnail choice (Pause 5)
Pending proposals: lexicon `Rumayyan` -> `Roo-MY-yan` (not agreed yet)

| Step | Status | Date | Files | Proof |
|---|---|---|---|---|
| 1 Topic | done | 2026-11-16 | — | Franco chose Uber |
| 2 Research and fact check | done | 2026-11-17 | 01_research.md, 02b_factcheck.md | signed sha256:ab84cbd13362 = fingerprint |
| 3 Script and voice version | done | 2026-11-18 | 02a_outline.md, 02_script.md, 02_script_voice.txt, 02c_listen_20s.txt | checker all exit 0; Franco by ear 2026-11-18 |
| 4 Scenes and prompts | done | 2026-11-20 | 03_scenes.md | checker scenes exit 0 (91 scenes) |
| 5 Publication text | waiting for Franco | 2026-11-20 | 04_publication.md | checker all exit 0 |
| Pieces | in progress | 2026-11-21 | images/ 31 of 59, clips/ 0 of 5, charts/ 0 of 25 | counted in the folder |
| Voice | not started | — | voice/ | voice notebook: `voice/state.json` |
| Render | not started | — | render/ | assembly and its verdict (build S07) |
| Publication | not started | — | — | YouTube link, date |
```

- **Status**: `not started`, `in progress`, `waiting for Franco`, `done`,
  or `redo: <reason>` (for example, a registry edited after its signature).
- **Proof**: what shows the step is done: a checker result, a hash, a
  count of files, Franco's word with its date. "Done" without proof is not
  done.
- The **pieces, voice and render** rows are rewritten from what the folder
  holds (count the files; read the notebooks' own state files: for the
  voice, `voice/listen_20s.json` once the 20 s sample is made, then
  `voice/state.json`, `status` `running`, `ready` or `failed`, with its
  flagged dry endings; the render's comes with build session S07). The
  **publication** row is done when Franco gives the YouTube link and the
  date.
- A step redone (a new script) puts every later step back to `redo`, with
  the reason: scenes hold the script's words, the voice its text.

## `Memory/videos.md`

```markdown
# Videos

Updated: 2026-11-20, session <link>

## In progress
| Video | Folder | Step | Next action | Who | State of |
|---|---|---|---|---|---|
| 01 Uber Was Cheap. Who Paid? | Videos/01_uber | 5 publication text, waiting for Franco | choose title and thumbnails; make images | Franco | 2026-11-20 |

## Published
| Video | Date | Views 24 h | Views 72 h | Views 7 d |
|---|---|---|---|---|

## Proposed, not chosen
| Topic | Date | Why not (if Franco said) |
|---|---|---|

## Covered elsewhere (dated reading)
| Topic | Channel | Angle | Views | Date read |
|---|---|---|---|---|
```

**When to update it**: at step 1 (the topics proposed, the competitors
seen), and at the end of every session: copy each `00_state.md`'s step and
next action into its row. A video moves to *Published* when its state
says so. Keep it under one page: summarise old *Proposed* lines rather than
piling them up.

## `Memory/lessons.md`

```markdown
# Lessons

| Video | Views 7 d | Average view duration | Thumbnail click rate | Lesson (one sentence) |
|---|---|---|---|---|

## Measured settings
- Speaking rate: <words a minute, from the voice notebook, with the video and date>
- Words for 13-15 min: <recomputed from that rate>

## Experiment in progress
- <one change only, e.g. the thumbnail trio of video 1>, noted before publication
```

Franco fills in the YouTube Studio numbers; you write the speaking rate
read from the voice notebook's `voice/state.json`: `rate_total_wpm` (the
whole track, pauses included, the one comparable with the niche's 142-154)
with `rate_speech_wpm` beside it, and the word target that follows from it. **Number discipline** (kept from Zehon):
views at 24 h, 72 h and 7 days, separately; a late reading carries its real
delay ("9 days"); a value still processing is not replaced by 0; **no
conclusion before 3 videos** (until then a lesson is an observation); **one
experiment at a time**.

**What you do with it**: at step 1, prefer the topic shapes that worked;
at step 3, use the measured speaking rate for the word budget; say when a
lesson changes your recommendation.

## Writing in Drive

Write the file first in the local work folder, check it, then put it in
Drive: update the existing file in place when the connector can; else
create the new version, then move the old one to the bin, so a folder never
holds two versions of a file (the Zehon rule that worked: no duplicate
found by the audit). Without the Drive connector: say so in one line, give
Franco the new content of `00_state.md` and the `videos.md` row in code
blocks, and he pastes them.
