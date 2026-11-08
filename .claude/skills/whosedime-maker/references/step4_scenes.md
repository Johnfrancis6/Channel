# Step 4: Scenes and prompts

**Goal**: `03_scenes.md`, the file the assembly (skill `whosedime-video`) reads
to build the video, with the image prompts Franco pastes into Gemini and
the clip prompts for Flow. **The prompts are also shown in full in the
chat** (end of this file): Franco copies them from there.

Before you start: `python3 whosedime/common/checker.py all F` exits 0 on
the script and the voice version, and Franco validated the script by ear
(Pause 4). If the script changes later, step 4 is redone: the scenes hold
its words.

## Cut the script into scenes

- **One spoken scene = 9 to 10 s on screen**, about **25 words** at 149
  words a minute (the checker warns outside 10-40 words). For 2,000-2,250
  words: **78 to 88 spoken scenes**, plus 7 cards: **85 to 95 scenes**
  (Uber run: 84 spoken scenes of 25 words on average, 91 in all).
- **The spoken text is the script, word for word**: an exact, continuous
  extract of `02_script.md` without headings, `[^Fnn]` tags or
  `## Sources`. Put end to end, the scenes give back the whole script, in
  order, with no gap and no repeat. The assembly aligns this text on the
  voice's word timings: a changed or missing word breaks the alignment, so
  the checker blocks it (`scene-text`).
- **Cut at a sentence end**, else at a strong comma or a colon. Never cut a
  name, a number or a quotation in two. A quotation may be its own scene.
- **One visual idea per scene.** A sentence that carries two pictures
  makes two scenes.
- **Write the cut with a small script**, not by hand: a Python list of
  scenes, each naming the first words of its text (an anchor), its type and
  its prompt; the text runs to the next anchor and the numbers are
  computed. Continuity references ("Same setting as scene_014") are then
  computed too (`scene_{prev}`), so they stay right when a scene moves.
  The reference run is `evals/files/01_uber/03_scenes.md`.

## The scene types

| type | How many | What is on screen | `visual` column |
|---|---|---|---|
| `image` | **50 to 55** | a Gemini illustration, with a slow camera motion | `images/scene_NNN.png` |
| `chart` | **25 to 30** | a chart drawn by code from one or more `verified` facts of `02b_factcheck.md` (`whosedime-video/scripts/charts.py`) | `charts/scene_NNN.png` |
| `video` | **4 to 5** | a short Flow clip animated from the scene's own Gemini image | `clips/scene_NNN.mp4` |
| `title` | **1** | the "WHO PAYS?" title card, identical on every video, at the start of `## Setup` (about 0:45) | `—` |
| `chapter` | **6** | a chapter card: The decision, the three dollar steps, Consequences, Lesson and next | `—` |

`title` and `chapter` are **cards**: about 2.5 s, **not spoken** (spoken
text `—`), no image, no prompt; the assembly draws them from the
`on-screen text` column, and each one starts a YouTube chapter (step 5).
Tell Franco the card numbers when you give the prompts, so a gap in the
numbering does not look like a missing image.

## The chart scenes (audit C2, decision D4)

A chart shows **only verified numbers**, so the `chart` column says where
they come from:

```
F07 · compare · invested $3.5 billion; valuation $62.5 billion
```

- **The fact id(s) first**: `F07`, or `F11, F12` for a chart that draws
  two facts. Each must be a `verified` line of the registry.
- **The kind**: `number` (one big figure), `compare` (two to four values
  side by side), `split` (a part of a whole: 41%, 20%), `timeline` (dated
  steps), `icons` (a count as a grid of small figures), `scale` (a range,
  1 to 5), `shape` (a rise and a fall without other numbers), `map` (money
  moving between places).
- **What it shows**, in a few words, with every number written as the
  registry writes it. **Every number here must be in the facts cited**: the
  checker blocks a chart with no id, an id that is not `verified`, or a
  number its facts do not hold (`chart-source`). A number you would need
  but the registry lacks is not drawn: tell Franco, it needs a new fact
  line and a new signature.

Where to put them: on the sentence that says the number (the eye then
confirms the ear), never two charts saying the same thing in a row, and a
recap chart in the consequences or the lesson works well. 25 to 30 charts
means a registry rich in numbers: a fact may be drawn twice (another kind,
another moment), but if fewer than 25 charts are honest, stay under and
say why.

## Camera motion and on-screen text

- **Motion** (`image` scenes only): `zoom_in`, `zoom_out`, `pan_left`,
  `pan_right`. Alternate; never more than 3 times the same in a row.
  Charts, clips and cards: `—` (they carry their own motion).
- **On-screen text**: one keyword, a date or a number, **at most one
  spoken scene in three**: `PARIS, 2008`, `SUBSIDY`, `NOT A LOAN`. A
  number or a quotation there is checked like the script (registry, people
  block). Otherwise `—`.

## The file `03_scenes.md`

```markdown
# Scenes — 01_uber "Uber Was Cheap. Who Paid?"

**91 scenes**: 54 image, 25 chart, 5 video, 1 title, 6 chapter. ...
Palette (channel, every image and chart): <prompt_line of whosedime/common/palette.json>.

## Scenes

| n | type | spoken text | visual | motion | on-screen text | chart |
|---|---|---|---|---|---|---|
| 1 | video | "In 2008, on a snowy night in Paris, ..." That's how Travis Kalanick tells it. | clips/scene_001.mp4 | — | PARIS, 2008 | — |
| 2 | image | Two friends, one cold street, no taxi. ... | images/scene_002.png | zoom_in | — | — |
| 5 | chart | Passengers were paying only 41 percent of what their trips actually cost. | charts/scene_005.png | — | — | F05 · split · riders paid 41% of what each trip cost (Hubert Horan's estimate) |
| 7 | title | — | — | — | WHO PAYS? | — |
```

The column names are fixed (`whosedime/common/settings.json`,
`scenes.columns`). The spoken text keeps the script's digits (`$3.5
billion`), not the voice version's words.

## The image prompts (after the table)

`## Gemini prompts`, then the **how to use** paragraph, the **preamble**,
then **batches of 10** (`### Batch 1: scenes 1 to 14`): one new Gemini
conversation per batch keeps the style steady (measured on Zehon,
30/09). For each `image` and `video` scene:

```markdown
**scene_009** — *A tech conference in Paris; one friend sketches a limousine on a napkin.*
> A busy tech conference hall in Paris in winter, late 2000s: ...
```

The one-line summary in italics tells Franco what the image shows. The
**preamble** (copy it from the reference run; adapt nothing but the
palette: its `Palette:` sentence is the `prompt_line` of
[`whosedime/common/palette.json`](../../common/palette.json), the one source
of the channel colours, which the charts and the cards also read) tells Gemini to
reply "OK", then make **one image per message with no text**, in the
channel style: flat 2D editorial illustration, warm light, cream
background, the palette, simple stylised people, generic products. Without
the "one image, no story" lines, Gemini chats and adds images nobody
asked for (measured on Zehon, 30/09).

Rules of a prompt:

- **A concrete action and place**: who does what, where, which light,
  which framing (close-up, wide shot, seen from behind).
- **No real person drawn realistically**: real people appear as simple
  stylised figures, from behind, in silhouette, or by their hands, an
  empty chair, an object. **Never name a real person** in a prompt: a
  name pulls Gemini towards a likeness, so the checker blocks any person of
  the people block named in a prompt (`prompt-person`). Decision D12
  (a named caricature) is for **thumbnails only**, in `## Notes` of
  `04_publication.md` (step 5): a scene prompt never names a real person.
- **No exact brand logo**: a black sedan, a ride app on a phone with a
  plain screen, a yellow taxi with no number. Colours and shapes of a
  product are fine; marks, names and logos are not.
- **No text in the image**: say it for every surface that calls for
  writing (sign, screen, paper, bill, filing, flag, clock): "blank",
  "unreadable lines", "no numbers". The preamble is not enough (measured
  on Zehon: 4 images in 76 had English text).
- **Continuity**: two scenes in the same place say "Same setting and
  lighting as scene_NNN" (computed, see above).
- A `video` scene has **two** prompts: its image (`scene_NNN`, in its
  batch) and its clip (`anim_NNN`). No prompt for `chart` and cards.

## Flow clips (4 to 5)

Spread over the video, never two in a row, where motion is natural: snow,
rain, traffic, a car on a road, a crowd walking. Avoid faces and hands in
close-up (the animation deforms them). Each clip starts from its scene's
image: Franco makes `scene_NNN.png` in its batch, then in **Google Flow**
(image to video) or the Gemini video tool he attaches it and pastes
`anim_NNN`. He saves `clips/scene_NNN.mp4` and keeps the image: if the clip
fails, the assembly uses the image. The clip's sound is not used.

```markdown
## Flow clips

**anim_001** — *A snowy Paris street at night ...* (from scene_001.png)
> Animate this illustration with a slow, subtle motion: <one sentence: snow falls, the car rolls forward>. Keep exactly the same drawing style, colours, people and composition as the image; every person keeps exactly two arms. No new objects or people, no cuts, no text, no talking, no music.
```

The motion is one slow sentence, never a new action (nobody enters,
nothing appears).

## Check, then show

```bash
python3 whosedime/common/checker.py scenes F/03_scenes.md
```

It must exit 0. It **blocks**: a spoken text that is not the script word
for word (it names the first scene that differs), a chart without a
verified id or with a number its facts do not hold, a bad table, type,
file name or motion, a card with spoken text or without its text, an image
or clip without its prompt, a real person named in a prompt, an on-screen
number or quotation that is not in the registry. It **warns** on the mix
(counts per type, words per scene, motions, on-screen share). Fix every
block; for a warning, fix it or say in one line why it stays.

Then show the prompts **in the chat**, in this order, without cutting
anything (it is long; it is the only part of step 4 written in full in
the chat):

1. the preamble, in a code block;
2. each batch under its own heading, then for each scene
   `**scene_009** — *summary*` and the prompt **in its own code block**,
   so it copies in one click;
3. the clip prompts the same way (`**anim_001**`);
4. one line naming the chart and card scenes, which have no prompt.

Then the self-critique of the scenes (5 lines at most, with scene
numbers) and its line in `critique_log.jsonl` (`"step": "4_scenes"`),
Franco's fields `null` for now: he grades the scenes once he has seen the
images, at the start of the next session (one question then). No pause
here: go on to step 5 (publication) in the same session.
