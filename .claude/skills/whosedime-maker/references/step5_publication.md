# Step 5: Publication

**Goal**: `04_publication.md`, everything Franco pastes into YouTube
Studio, plus the thumbnail prompts. It comes right after step 4, in the
same session. The checker reads it; Franco picks the title and the
thumbnail trio (**Pause 5**).

## The format the checker reads

Sections in this order, with these exact headings (`settings.json`):

| Section | What | Checked |
|---|---|---|
| `## Titles` | a numbered list of **3 titles**, nothing else on the line but the title and its tag | length ≤ 40 characters (tags not counted); every number in the registry **and** cited as `[^Fnn]` of a fact that holds it (`title-source`, audit C2); names not checked (title case) |
| `## Thumbnail` | a list: **3 variants** `A: <TEXT> [^Fnn] · <picture>`, then the badge line | same as titles: a number needs the tag of its fact |
| `## Description` | what YouTube shows under the video | like the script: numbers, dates, names, quotations against the registry, forbidden phrases |
| `## Sources` | the sources read, with links | skipped (but `[TO VERIFY]` anywhere blocks) |
| `## Notes` | recommendation, thumbnail prompts, chapters note, checklist | skipped |

Inside `## Notes`, use bold labels, **not** `###` headings: a heading
starts a new section, and a section named "Thumbnail prompt" would be
checked as a thumbnail.

## Titles: 3, one recommended

- The series template (PLAN_ACTION § 2): `[Brand] [free or cheap thing]:
  Who Pays?`, or `Who Paid?` for a closed story. **40 characters at most**,
  a number if one is strong and verified.
- **Title 1 is the plan's title** if the plan has one (PLAN_ACTION § 3),
  unless the research changed the story; titles 2 and 3 try another angle:
  a verified number, the viewer ("Your ...").
- **A number cites its fact**: `Uber Lost $7.9 Billion. Who Paid? [^F13]`.
  Not an estimate presented as a fact: if the number is one analyst's
  estimate (Horan's 41 percent), it goes in the description with its
  author, not alone in a title.
- The title promises what the video shows: the payers it names are the
  payers of the dollar steps.
- Nothing else on the line: no count, no "recommended" (the checker would
  count it). The counts and the recommendation go in `## Notes`.

## Thumbnail (PLAN_ACTION § 2)

Three variants, **one idea each** (the number, the paradox, the payer),
so the test teaches something:

| Rule | Detail |
|---|---|
| Text | **1 to 3 words, or one number** (`$7.9 BILLION`, `NOT YOU`). A number carries its `[^Fnn]` in the file (not in the image) |
| Badge | **"WHO PAYS?"** in the top right corner, same font and colour on every video |
| Subject | the product big, and a **cartoon caricature, deliberately unrealistic** (thick outlines, exaggerated proportions) of the executive **only if he or she is well known to the public**; otherwise the payer: a rider, a driver, a shopkeeper |
| Colours | warm and bright, light background, the channel palette (as in `03_scenes.md`) |
| Never | an exact brand logo (keep the colours and the shape of the product), a realistic portrait of a real person, more than 3 words, an infographic, a dark background |

**Each prompt is complete** (Franco pastes it alone in a new Gemini
conversation) and follows this model:

> YouTube thumbnail, 16:9. Bold cartoon illustration with thick black outlines, flat saturated warm colours, light cream background, bright and high contrast, very simple composition readable at small size. <the scene: who, doing what, the exaggerated emotion>. <no logo line>. Big bold text <where> in thick white (or yellow) capital letters with a heavy black outline: "<TEXT>". A small round mustard badge in the top right corner with navy capital letters: "WHO PAYS?". Write the texts exactly as given. No other text, no logos, no watermark.

The text is asked of Gemini directly (the only exception to "no text in
images": it makes testing fast). Franco checks the spelling; if wrong, he
regenerates or sets the text himself. **The text must be true**: the
number of a `verified` fact, rounded only as the registry rounds it. Do not
name the real person in the prompt: describe the caricature (age, clothes,
a gesture). Recommend the trio to test and the first one to show; note it
as the current experiment in `lessons.md` (see `memory.md`).

## Description

```markdown
## Description

<2-3 sentences: the free or cheap thing, the payer hint, the question; numbers with [^Fnn]>

0:00 Cold open
--:-- Who pays?
--:-- The decision
--:-- The investors
...
--:-- The lesson

Next: <next video's title, short>

Nothing is free. Every bargain, perk and "free" app is paid for by someone. Twice a week, we follow the dollar to find out whose dime it is.

The sources are listed below. The illustrations are machine-made; every chart is drawn from a source on this list. Nothing in this video is advice to buy or sell anything.
```

- **Chapters** come from the cards of `03_scenes.md`: `0:00 Cold open`,
  then one line per `title` and `chapter` scene, in order, labelled with
  the card's text in sentence case (shortened: "The investors" for "PAYER
  ONE: THE INVESTORS"; a capitalised word after `--:--` reads as a name to
  the checker). Times stay `--:--`: the assembly writes `chapters.txt`
  (build session S07) and Franco copies the times. YouTube needs 0:00
  first, at least 3 chapters, each at least 10 s.
- **No name the registry does not hold**, no "AI" or tool names (the
  checker reads them as names): "machine-made" says it.
- The channel promise line (PLAN_ACTION § 2) closes every description.

## Sources

The sources of the facts the video says, one line each: author or
outlet, title, date, link (from the registry's `source` column). Never a
source that was not read.

## Notes: recommendation, prompts, checklist

In `## Notes`, in this order: the recommended title with its character
count and the reason in one sentence; the thumbnail trio and the first to
show; the three thumbnail prompts (`**Thumbnail prompt A**` then the
prompt as a `>` quote); the chapters note; end screen and playlist
(PLAN_ACTION § 3); then the checklist:

```markdown
**Before publishing** (Franco ticks):

- [ ] Chapter times filled from `chapters.txt`
- [ ] YouTube's "altered or synthetic content" box: the voice is synthetic and the images are generated; tick it when in doubt
- [ ] The three thumbnails loaded in Test & Compare
- [ ] Every link of the Sources section opens
- [ ] End screen and playlist set
```

## Check

```bash
python3 whosedime/common/checker.py all F
```

It must exit 0 (script, voice, scenes, publication). Typical blocks seen
on the Uber run, fixed in the file: a thumbnail text written in quotation
marks (read as a quotation: write it bare), a capitalised word in a
chapter label (read as a name). `name-first` warnings on the description's
first words are expected; check none is a real name.

## Pause 5

Three lines: the recommended title and why, the thumbnail trio, the
checker result. The Drive link of `04_publication.md`. Then show the three
thumbnail prompts in the chat, one code block each, and ask one question:
"Which title and which three thumbnails do we keep?" (in French: « Quel
titre et quelles trois miniatures on garde ? »).

After his answer: the self-critique, his grade question, the critique
line (`"step": "5_publication"`); then rewrite `00_state.md` and the line
of `videos.md` (see `memory.md`), and end the session: Franco now makes
the pieces (images, clips) and the voice.
