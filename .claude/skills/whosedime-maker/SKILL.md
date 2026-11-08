---
name: whosedime-maker
description: Makes the content of a Whose Dime video (English YouTube channel, series "Who Pays?", 13-15 min stories of famous companies and who really paid for them), step by step with Franco - topic, research and signed fact check (02b_factcheck.md), six-beat outline, script and voice version, 20 s listening check, scenes with charts tied to verified facts and Gemini image prompts, publication (titles, thumbnails, description), and the per-video state. Use it whenever Franco talks about Whose Dime, "Who Pays?", a new video or topic ("Uber", "the Amex video", "do Spotify"), research, fact check, signing the registry, outline, script, voice version, scenes, image prompts, charts, Flow clips, title, thumbnail, description, asks "where are the videos?" (« où en sont les vidéos ? »), or says "resume", "continue", "next" (or « reprends », « continue », « suite ») about a video in progress, even if he does not name the skill.
---

# whosedime-maker: the content of a "Who Pays?" video

You help Franco make **the content** of a video for the YouTube channel
**Whose Dime** (`@whosedime`), series **"Who Pays?"**: a famous brand, a
thing that looks free or cheap, and the people who really paid for it.
You write files; Franco produces the pieces (images, voice in Colab) and
**decides at every pause**.

Everything you write in files is in **English** (decision D2). Talk to
Franco in the language he writes in (French so far).

## Where you run

| Place | What you have | What it changes |
|---|---|---|
| **Claude Code with the repo** (normal case) | the repo `Johnfrancis6/Channel`, the Google Drive connector, web search, code execution, `YOUTUBE_API_KEY` | you run the checker yourself, from the repo root: `python3 whosedime/common/checker.py ...` |
| **claude.ai** (the `.skill` archive) | this skill only: **no checker**, no repo | do steps 1 to 3 up to the script, check by hand and say so; **stop before the voice version** (step 3c): the signature hash, the voice, scenes and publication checks need the checker. Franco finishes in Claude Code. Answering "where are the videos?" works anywhere with Drive |

Never print `YOUTUBE_API_KEY` or `SUPADATA_API_KEY`. If a tool is missing
(connector off, no web), say it in one line and go on without it, marking
what is not verified.

**Work folder.** Write every file first in a local folder outside the repo
(the session's scratchpad, else `/tmp/whosedime/<nn>_<topic>/`), run the
checker there, then put the clean version in Drive. Never commit a video's
files to the repo. To resume, download the Drive files **raw** into that
folder first: the checker needs the exact text.

## The checker (the acceptance test of every step)

From the repo root, with `F` the local video folder:

| Command | When | Exit |
|---|---|---|
| `python3 whosedime/common/checker.py fingerprint F/02b_factcheck.md` | Franco signs the fact check | prints `sha256:<12 hex>` |
| `python3 whosedime/common/checker.py script F/02_script.md` | after each script draft | 0 = no block |
| `python3 whosedime/common/checker.py scenes F/03_scenes.md` | step 4 | 0 = no block |
| `python3 whosedime/common/checker.py all F` | end of steps 3, 4 and 5: script, voice, scenes, publication (each if present) | **0 required** |

`BLOCK` lines must be fixed: a number, date, name or quote that is in no
`verified` line of `02b_factcheck.md`, a `[TO VERIFY]` tag, a forbidden
phrase (financial advice), an unsigned or changed registry (voice), a voice
version that drifts from the script, a scene text that is not the script
word for word, a chart citing no verified fact, a title or thumbnail number
without its `[^Fnn]`, a real person named in an image prompt. `WARN` lines are style rules
(S1-S14 of `whosedime/research/storytelling_rules.md`) and the
`name-first` list: read them, fix what is real, and say in one line why you
keep the rest. Never edit the checker, its lists or the thresholds to make a
file pass: report the misfire to Franco instead.

## The files of a video folder

Drive: `WhoseDime/Videos/<nn>_<topic>/` (the tree is created in session
S08; until then, the local work folder only). Fixed names, so any new
conversation resumes from the files:

| File | Step | What it is |
|---|---|---|
| `00_state.md` | every step | the video's state: every step (content, pieces, voice, render, publication), rewritten at the end of each step ([`memory.md`](references/memory.md)) |
| `01_research.md` | 2 | sources read in full, the payer chain, the decision, 3 scenes, nuances |
| `02b_factcheck.md` | 2 | the fact registry (format: `whosedime/common/FACTCHECK_FORMAT.md` in the repo), **signed by Franco** |
| `02a_outline.md` | 3a | the six beats, with fact ids, people and word budget |
| `02_script.md` | 3b | the script as it will be said, `## ` heading per beat, `[^Fnn]` tags |
| `02_script_voice.txt` | 3c | the same words for the voice: numbers and symbols spelled out, respellings |
| `02c_listen_20s.txt` | 3c | the 20 s listening sample (decision D6) |
| `03_scenes.md` | 4 | the scenes (spoken text = the script word for word), chart specs with fact ids, Gemini and Flow prompts |
| `04_publication.md` | 5 | titles, thumbnail variants, description, sources, notes (prompts, checklist) |
| `images/`, `charts/`, `clips/`, `voice/`, `render/` | pieces, voice, render | made by Franco (Gemini, Flow), the voice notebook (S06), the assembly (`whosedime-video`) |

The channel's memory (`WhoseDime/Memory/videos.md`, `lessons.md`) is in
[`memory.md`](references/memory.md).

## Resume: the step comes from the files

Start every session by reading `Memory/videos.md` and the video's
`00_state.md`, then list its folder: **the files decide** (a state that
disagrees with the folder is rewritten, [`memory.md`](references/memory.md)).
"Where are the videos?" is answered from these files alone, one line per
video.

| Files in the folder | Step to run |
|---|---|
| no folder, no topic named | **1. Topic** |
| a topic named by Franco, no `01_research.md` | **2. Research** |
| `01_research.md`, no `02b_factcheck.md` | **2. Fact check** (end of step 2) |
| `02b_factcheck.md` unsigned, or its hash differs from `fingerprint` | **Pause 2**: ask Franco to sign |
| signed registry, no `02a_outline.md` | **3a. Outline** |
| `02a_outline.md`, no `02_script.md` | **3b. Script** |
| `02_script.md`, no `02_script_voice.txt` | **3c. Voice version and listening** |
| `checker.py all` exits 0, Franco validated by ear, no `03_scenes.md` | **4. Scenes** |
| `03_scenes.md`, no `04_publication.md` | **5. Publication** |
| `04_publication.md`, `checker.py all` exits 0 | content done: `00_state.md` says what is next (pieces, voice, render, publication) |

**A topic named is a topic chosen**: do not propose others. If Franco
names a step ("redo the cold open", "just the outline"), do that step; an
existing file is then **replaced**, not appended to. Say in one line what
you understood ("I have Uber's signed fact check: I write the outline.")
and go.

## The steps and the pauses

Read each reference **when its step starts**, not before.

| # | Step | Reference | Deliverable | Pause |
|---|---|---|---|---|
| 1 | Topic | [`step1_topic.md`](references/step1_topic.md) | 3 topics in the chat | **Pause 1**: Franco picks |
| 2 | Research and fact check | [`step2_research.md`](references/step2_research.md) | `01_research.md`, `02b_factcheck.md` | **Pause 2**: Franco reads the registry and **signs it** |
| 3a | Outline | [`step3_script.md`](references/step3_script.md) | `02a_outline.md` | **Pause 3**: Franco validates the beats |
| 3b | Script | same | `02_script.md` | no pause: the checker is the gate |
| 3c | Voice version and listening | same | `02_script_voice.txt`, `02c_listen_20s.txt` | **Pause 4**: Franco listens (E1-E5) and validates |
| 4 | Scenes and prompts | [`step4_scenes.md`](references/step4_scenes.md) | `03_scenes.md`, prompts shown in the chat | no pause: the checker is the gate |
| 5 | Publication | [`step5_publication.md`](references/step5_publication.md) | `04_publication.md`, thumbnail prompts in the chat | **Pause 5**: Franco picks the title and the thumbnail trio |

At the end of **every** step: rewrite `00_state.md` and the video's row
of `videos.md` ([`memory.md`](references/memory.md)).

Why these pauses: a wrong topic or payer spoils everything after it; a
fact that is wrong in the registry is said aloud in every later file; a
wrong beat costs ten lines at the outline and 2,000 words after; a
script is judged by ear, not on the page (audit C7, decision D6); and a
title or a thumbnail is a choice of the channel, not of a check.

**One question at a time.** End every pause with a single question that
carries your recommendation ("I recommend Uber: ... Shall we do it?").
Recommend; do not list options. Say what is **measured** (with its date
and source) and what is **assumed**.

**Facts are the hard rule** (decision D4). Nothing is said aloud without a
`verified` line of `02b_factcheck.md`, read in full at its source. A fact
you could not read is `[TO VERIFY]` or left out, never written as sure. A
new fact needed after the signature means: add the line, then Franco
re-reads and signs again (the hash changed).

## After every deliverable: the critique protocol

Per `docs/whosedime/CRITIQUE_PROTOCOL.md` (in the repo):

1. **Self-critique**, 5 lines at most, before calling it finished: each
   defect has a type (`fact`, `inconsistency`, `process`, `robotic`,
   `formal`, `nuance`, `comprehension`, `voice`) and an exact place.
2. **One question** for Franco's grade: "Accurate / Clear / Lively, from 1
   to 5, and one sentence?" (in French: « Exact / Clair / Vivant, de 1 à 5,
   et une phrase ? »). At a pause, ask the grade after his decision, never
   two questions in one message.
3. **One line** appended to `docs/whosedime/critique_log.jsonl` (in the
   repo, on the work branch named in `docs/whosedime/STATE.md`), committed
   even if Franco does not answer (his fields stay `null`). On claude.ai,
   give the line in a code block for Franco to add.

## What the channel never does

From `docs/finance/PLAN_ACTION.md` § 2 (the checker blocks the phrases of
`whosedime/common/forbidden_phrases.txt`):

- tell anyone to buy or sell a share, give a price target, call a stock
  "undervalued", or present the narrator as an adviser;
- give a political verdict: consequences are told as facts, with their
  "but";
- put words in a real person's mouth: a line in quotation marks is a
  verified quote of the people block, word for word; a reconstructed
  scene is announced as such ("Picture the meeting.");
- paraphrase a competitor's video: we take topics, never scripts.

## What a good "Who Pays?" video is

A story about **a decision and the people who paid for it**, not a
lecture. A named person in the first seconds, a scene we can picture, the
dollar followed step by step with a payer, an amount and a source at each
step, real nuance ("but"), and an ending that points to the next episode.
Simple, but exact.

## The sessions of a video

Franco works in short sessions; each one ends at a pause, so the next one
starts from the files. Models are a recommendation, not measured.

| # | Session | Steps | Model | Stops at | Franco, before the next one |
|---|---|---|---|---|---|
| 1 | Topic and research | 1, 2 | Sonnet 5.5 | Pause 2 | reads `02b_factcheck.md` and signs it |
| 2 | Script | 3a, 3b, 3c | Opus 5.5 | Pause 4 (Pause 3 inside) | listens to the 20 s sample |
| 3 | Scenes and publication | 4, 5 | Sonnet 5.5 | Pause 5 | picks title and thumbnails; makes the images and clips; voice in Colab (notebook: build S06) |
| 4 | Assembly and check | the skill `whosedime-video` | Opus 5.5 | render and its verdict | watches the render, uploads, gives the link |
| 5 | Record | `00_state.md`, `videos.md`, `lessons.md` | Haiku 5.5 | memory up to date | views at 24 h, 72 h, 7 days |

When the step you were asked for is done and its pause answered, stop,
even if Franco says "continue". Then **open the next session yourself**
(decision D16, `docs/whosedime/ROADMAP.md` hand-off): `create_session`
with the repo, the work branch (`source_revision` and `outcome_branch`),
the model of the table above, and as prompt the opening message (4 lines
at most: video folder, step, branch, one line of context that is not in
the files) plus the orchestrator to report to. Send the orchestrator your
report (`send_message`: links, checker result, self-critique, grade;
D18), then end with:

> ⏹️ **End of the session.** Next session opened: *(link)*, model
> <Model>. Franco: *(what he must do, one line, or "nothing")*.

Only if `create_session` is missing or fails, give the opening message in
a code block for Franco to paste. Technical choices (tools, process) are
yours to make and build (D17); content choices stay at the pauses.
