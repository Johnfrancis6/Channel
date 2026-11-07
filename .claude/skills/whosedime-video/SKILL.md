---
name: whosedime-video
description: Assembles a Whose Dime video (English YouTube channel, series "Who Pays?") from its Drive folder - 03_scenes.md, images/, clips/, the voice (voice/voice.wav, voice/words.json) and the fact registry 02b_factcheck.md - into render/video.mp4, with charts drawn from verified facts only, title and chapter cards, chapters.txt for the description and a verdict named after its output. Use it whenever Franco talks about the Whose Dime assembly, render, charts, chapter times, an extract, "assemble Uber", video.mp4, the verdict, or asks whether a Whose Dime video is ready to publish, even if he does not name the skill. Not for Zehon (French channel, its own video-maker).
---

# whosedime-video — the assembly of a Whose Dime video

You assemble a video **whose content is finished** (skill `whosedime-maker`,
steps 1 to 5) and whose pieces Franco made (Gemini images, Flow clips, the
voice notebook). You write neither the script nor the prompts. Everything
goes through two scripts; read their docstrings to go further.

| Script | What it does |
|---|---|
| `scripts/charts.py FOLDER` | one 1920x1080 PNG per `chart` scene, `charts/scene_NNN.png`, drawn from `02b_factcheck.md` |
| `scripts/assemble.py FOLDER` | gate, charts, timing, render, technical check, verdict |

Every number is in [`settings.json`](settings.json); the colours in
`whosedime/common/palette.json` (the one source: the image prompts, the
charts and the cards read it). Both scripts need the repo
(`whosedime/common/checker.py`, `whosedime/notebooks/voice_whosedime.py`).

## The charts: never a number typed by hand (D4)

The `chart` cell of `03_scenes.md` (`F07 · compare · invested $3.5 billion;
valuation $62.5 billion`) says which facts, which kind and what to show.
Before drawing, `charts.py` refuses the chart if a cited fact is not
`verified` (a `[TO VERIFY]` fact blocks), if no fact is cited, or if a
number of the cell is not held by its facts. It adds no number of its own:
no axis, no tick, no "rest" of a percentage, no "one figure = 1,000". Bars
only when the values share a unit and are less than 50x apart; otherwise the
figures stand side by side. The source line under each chart is the
registry's source, without its URL. A refused chart is not drawn and an old
PNG of it is deleted: the assembly then stops.

Kinds: `number`, `compare` (2-4 items), `split` (a percentage), `timeline`
(each step has a date), `icons` (a count, people or days), `scale` ("from 1
to 5"), `shape` (rose ..., then crashed ...), `map` ("<amount> from <place>
to <place>"). A cell the tool cannot read is refused with the reason: fix
the cell in `03_scenes.md` (and run the checker again), never the drawing.

## What assemble.py does

| Step | What happens |
|---|---|
| Gate (D4) | `checker.py scenes` and `voice` must pass: no `[TO VERIFY]` fact used, the registry unchanged since Franco signed it, the scenes equal to the script word for word; `voice/state.json` says `ready` |
| Charts | all redrawn from the registry (never a stale chart) |
| Files | an image for every `image` and `video` scene (stops if one is missing); a missing clip is replaced by its image (warning) |
| Timing | each spoken scene is found in `voice/words.json` (numbers said in words and respellings matched back); it starts 0.25 s before its first word, in the pause. A `title` or `chapter` card adds 2.5 s of silence |
| Render | 1920x1080, 30 fps; images zoom or pan slowly (`zoom_in`, `zoom_out`, `pan_left`, `pan_right`), charts and cards push in 2 %, clips slowed (x1.35 at most) then frozen if short; on-screen keyword lower left on a navy band; 0.5 s crossfades; sound at -14 LUFS, peaks at -1.5 dBTP |
| Check | size, an audio track, no silence (mean > -60 dB), no clipping (peak <= -0.5 dB), duration within 0.5 s. **A render is finished only if this check passes** |

Outputs in `render/`, **named after the output** (audit P3): `video.mp4`,
`report_video.json`, `verdict_video.json`, `preview_video/` (six frames:
start, title, chart, clip, on-screen keyword, end); an extract writes
`extract_001-010.mp4` with its own `verdict_extract_001-010.json`,
`report_`, `preview_`, and **never touches the whole video's files**. The
whole video and `--plan` also write `chapters.txt` (`0:00 Cold open`, then
one line per card; labels from `04_publication.md` when its chapter lines
match the cards) and `plan.json`. The verdict carries the code it ran,
`main@<commit>` in Colab (C3).

## In Claude Code: the plan, then reading the verdict

Images, clips and the voice stay in Drive: every render, extract included,
runs in Colab. Here you make the plan and read what Colab wrote.

1. **The plan**: download the small files of the video folder
   (`03_scenes.md`, `02_script.md`, `02_script_voice.txt`,
   `02b_factcheck.md`, `04_publication.md`, `voice/words.json`,
   `voice/state.json`) into a work folder with the same layout, then
   `python3 whosedime/whosedime-video/scripts/assemble.py <work> --plan --no-files`.
   Then `python3 whosedime/whosedime-video/scripts/charts.py <work>` to see
   the charts (look at a few PNGs yourself). Tell Franco in 5 lines: length,
   chapter times, scenes found at less than 60 % in the voice (the scenes and
   the voice differ: fix before rendering), stills over 12 s, refused charts.
2. **An extract**: Franco runs the assembly launcher with `MODE = "extract"`,
   `SCENES = "1-10"` (about 5 min). Then read as below.
3. **The whole video**: `MODE = "full"` (about 30-45 min, assumed). Then
   read `render/verdict_video.json` (under 1 KB: `ready`, `check`,
   `warnings`, `duration_s`, `render_s`, `code`) and look at the six frames
   of `preview_video/`. If `"ready": false`, the video is not published.
   Copy `render/chapters.txt` into the description's chapter lines.

## Colab: a fixed launcher, the real notebook in the repo

In Drive, `WhoseDime/assembly_launcher.ipynb` is a copy of
`whosedime/notebooks/assembly_launcher.ipynb`: a form (`VIDEO`, `MODE`
`plan`/`extract`/`full`, `SCENES`, `ROOT`), then it clones `main`, prints the
commit it runs and runs `assembly_whosedime.ipynb` (decision D5). No GPU. The
render is written on the Colab disk, then copied to `render/`.

## What to tell Franco

- Recommendations, not options; what is measured apart from what is
  assumed; one question at a time.
- A refused chart names its scene and its reason: the fix is in
  `03_scenes.md` or in the registry (a new fact line means a new signature),
  never in the drawing.
- A still over 12 s: propose to cut the scene in two in `03_scenes.md` (one
  more image prompt, shown in full in the chat).
- After every render read: the critique protocol (5-line self-critique,
  Franco's grade, one line in `docs/whosedime/critique_log.jsonl`).
