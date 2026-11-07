# Step 3: Outline, script, voice version, listening

Three moves: **3a the outline** (`02a_outline.md`, Pause 3), **3b the
script** (`02_script.md`), **3c the voice version and the 20 s listening
sample** (`02_script_voice.txt`, `02c_listen_20s.txt`, Pause 4). The step
ends only when `python3 whosedime/common/checker.py all F` exits 0 (no
`BLOCK`) **and** Franco has validated by ear.

Before 3a: the registry must be **signed** with a hash that matches
(`fingerprint`). Every fact you use comes from a `verified` line of it.

## The six beats (PLAN_ACTION § 2)

Length: **2,000 to 2,250 words** (13-15 min at 149 words a minute, the
niche hits' median measured in S02). Budgets below are at that rate.

| # | Heading in the script | Time | Words | What it does | Its rule |
|---|---|---|---|---|---|
| 1 | `## Cold open` | 0:00-0:45 | 100-120 | A named person at one moment (place, gesture, line), the free or cheap thing as the customer saw it, then the result: how much someone paid, and a hint of who | A sourced number in the first 30 s (60 words; 1 to 4 numbers: S8). The title's question asked before 0:40 (about 100 words; S9: a "but" within 100 words). No logo, no intro |
| 2 | `## Setup` | 0:45-2:30 | 240-280 | The brand, its size, the market; the "WHO PAYS?" title card | 2 or 3 numbers a chart can show (charts come in S05-S07) |
| 3 | `## The decision` | 2:30-5:00 | 360-400 | The moment the brand chose to make the thing free or cheap: date, people, numbers | **The beat that carries the video**: a scene told, not a lecture; a quoted line if the registry has one |
| 4 | `## Follow the dollar` | 5:00-9:00 | 580-640 | The dollar in 3 steps (`### Step 1: <payer>` ...), each with **a payer, an amount and a source** | One YouTube chapter per step; each step ends on a small cliffhanger (E5) |
| 5 | `## Consequences` | 9:00-12:00 | 420-480 | Who won, who lost, what changed (rulings, laws, prices) | Facts, no political verdict; the "but" of the research's nuance |
| 6 | `## Lesson and next` | 12:00-13:30 | 200-240 | The general mechanism ("next time something is free..."), then the bridge to the next episode | The last 20 s announce the end-screen video (a phrase of `next_video_markers.txt`); the comment question: "What "free" thing should we follow next?" |

## 3a. The outline: `02a_outline.md`

```markdown
# Outline: <nn>_<topic>, "<title>"

| Beat | Words | What happens | Person / scene | Facts | Ends on (the pull) |
|---|---|---|---|---|---|
| Cold open | 110 | ... | Kalanick, Paris, 2008: "..." | F01, F04 | the title's question |
| Setup | 260 | ... | ... | ... | ... |
| The decision | 380 | ... | ... | ... | ... |
| Follow the dollar 1 | 200 | payer: ..., amount: ..., source: F.. | ... | ... | ... |
| Follow the dollar 2 | 200 | ... | ... | ... | ... |
| Follow the dollar 3 | 200 | ... | ... | ... | ... |
| Consequences | 450 | ... | ... | ... | ... |
| Lesson and next | 220 | ... | — | ... | next video: <title> |

**Total**: ... words. **End screen**: <video> (PLAN_ACTION § 3).
```

Check before showing it: the six beats in order; a person in the cold
open; 3 dollar steps, each with payer, amount and fact id; at least 3
scenes with a person (one in beat 3); every fact id is `verified` in the
registry; total 2,000-2,250. **A fact that is not in the registry does not
go in the outline**: drop it, or add it as `[TO VERIFY]` and tell Franco
(then the registry needs a new signature).

**Pause 3**: 3 lines (the arc, the 3 payers, the beat you are least sure
of), then one question: "Do you validate the outline?"

## 3b. The script: `02_script.md`

Write the text **as it will be said**, with a `## ` heading per beat
(exactly the headings above) and `### ` for the three dollar steps. Cite
the registry with Markdown footnote tags right after the claim: `[^F07]`.
A `## Sources` section at the end may list the footnote definitions
(`[^F07]: Fortune, 2016-06-01`): the checker does not read it for facts.

How it should sound (rules S1-S14 of
`whosedime/research/storytelling_rules.md`, all `warn`, measured on niche
hits; by-ear rules E1-E5; the before/after in
`whosedime/research/rewrite_uber_cold_open.md`):

- **People carry the story** (S1, S2): the decision maker named in the
  cold open; named people come back in every beat.
- **Two or three short scenes with spoken lines** (S3, E2): a quoted line
  is a verified quote of the people block, **word for word** (an ellipsis
  `...` may cut words out); 12 words at most is best for the second voice.
  A reconstructed moment is announced ("Picture the meeting.") and never
  put in quotation marks.
- **Vary sentence length** (S4, S6): short punches next to sentences that
  breathe; a few over 25 words are fine (no Zehon 25-word ceiling).
- **Fewer numbers** (S7): about one every 40 words at most. Tell the rest
  with people. Every amount says **who pays it and to whom** (E3).
- **Talk to the viewer** (S11): "you", "your ride", "your card".
- **Explain each finance term the first time** (S13, S14): "operating
  profit, which means..." or avoid the term.
- **The narrator reacts** once per beat (E4): surprised, amused, blunt.
- **No stock connector** to close a block (E5, audit C7): end on a pull,
  not a formula; vary openers (S12).
- **Nuance** (S10): a real "but" where the sources hesitate; never an
  absolute claim the registry does not hold.
- **Names**: every capitalised word inside a sentence must be in a
  registry line (the checker blocks otherwise). Avoid needless proper
  nouns ("Britain's top court" needs `Britain` registered).

Run `python3 whosedime/common/checker.py script F/02_script.md` after each
draft. Fix every `BLOCK`. For each `WARN`, fix it or say in one line why
it stays (the `name-first` list often holds common words such as "Fine":
check that none is a real name missing from the registry).

## 3c. The voice version: `02_script_voice.txt`

The **same words** as the script, prepared for the synthesis
(Qwen3-TTS, notebook of build session S06). The checker compares the two
word for word and blocks any other change.

- **Only these rewrites**: numbers in words (`$1.1 billion` → "one point
  one billion dollars", `2019` → "twenty nineteen", `41%` → "forty-one
  percent", `40,000` → "forty thousand", `May 31` → "May thirty-first");
  `$`, `%` and `&` spelled out; respellings from
  `whosedime/common/lexicon.tsv` (`Kalanick` → `Kuh-LAN-ick`, `10-K` →
  `ten-K`, `IPO` → `I-P-O`). Measured with the checker: "seven
  ninety-nine" for `$7.99` and "May thirty-one" for `May 31` are drifts.
  So write prices with cents in the script the way they sound best
  ("about $42 a share") only if the registry holds that rounded number.
- **Nothing else changes**: no word added, cut or reordered. If a sentence
  sounds wrong aloud, change it in `02_script.md` first, re-run the
  checker, then the voice.
- **No headings, no tags, no footnotes, no `## Sources`**: only what is
  said.
- **Layout** (audit C6): one sentence per line, never cut; a blank line
  between blocks of 2 to 4 sentences (one synthesis per block; pauses of
  250 ms after a full stop, 450 ms after a question or a quoted line,
  700 ms between blocks: `whosedime/research/voice_direction.md`).
- A new hard name: propose its respelling to Franco; it goes into
  `lexicon.tsv` (repo) only with his agreement.

Then run `python3 whosedime/common/checker.py all F`. It must exit 0. The
voice check blocks if the registry is unsigned or changed since it was
signed: ask Franco to sign again, never edit the signature line yourself
without his word. Digits or symbols left in the voice are warnings: fix
them.

## The 20 s listening sample: `02c_listen_20s.txt` (decision D6)

The first block(s) of `02_script_voice.txt`, copied unchanged, cut at a
sentence end: **about 50 words** (20 s at 149 words a minute), so it holds
the cold open's person, line and first number. Franco synthesises it with
the voice notebook (build session S06; until it exists, he reads it aloud
or listens with any text-to-speech) **before** any full synthesis.

## Validation by ear (E1-E5)

Before Pause 4, check the script yourself against the five by-ear rules,
one line each, with the place:

| Id | Question |
|---|---|
| E1 | In the cold open, can we picture one named person at one moment (a place, a gesture, a line)? |
| E2 | Does every quoted line sound spoken (short, said by a person in a room), not read from a filing? |
| E3 | Is every amount clear the first time: who pays it, to whom? Does any sentence need hearing twice? |
| E4 | In each beat, does the narrator react at least once (surprised, amused, blunt)? |
| E5 | Does each beat end on a pull, without a stock connector? |

**Pause 4**: 3 lines (words and estimated length at 149 wpm on the voice
version, the checker result with its warning count, the 2 passages you
are least sure of), the link to the listening sample, then one question:
"Listen to the 20 s sample: does it pass E1 to E5?" Franco's answer by ear
is the validation; a "no" on one rule sends you back to 3b for that
passage, then through the checker again.

Then the critique line for step 3 (`"step": "3b_script"` for the outline
and script, `"3c_voice"` for the voice version; one line per deliverable
group), after his grade question. Step 3 is the end of this skill for now:
**stop** (scenes and publication come with build session S05).
