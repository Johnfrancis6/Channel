# Voice direction for "Who Pays?"

How the Whose Dime narrator should sound, and how video 1 tests it. Every
number names its source; **measured** means recomputed in this session,
**assumed** means to be confirmed by ear. The S06 notebook implements this.

## The narrator

An **American English storyteller** (D8): built with Qwen3-TTS
**VoiceDesign**, then cloned on the **Base** model from a 20-30 s VoiceDesign
reference, as in `PLAN_ACTION.md` S1. One narrator voice for the whole
series; a second, contrasting VoiceDesign voice for the short dialogue
lines (Crayon report, recommendation 2).

### VoiceDesign description to try first

> Warm American male narrator in his mid-40s, General American accent.
> Conversational storyteller, as if telling a friend a story over coffee:
> relaxed, curious, a little wry. Medium-low pitch, clear consonants,
> natural rises on questions, lands the end of each sentence without
> trailing off. Not a newsreader, not a trailer voice, no hype.

Two variants for the S1 ranking (`PLAN_ACTION.md` S1 asks for 3 voices):
the same text with "female, late 30s", and with "male, early 30s, slightly
faster and drier". The words "conversational", "wry" and "not a
newsreader" carry the fix for Zehon's "announcement" tone (V1, S5); this
is **assumed**, to be heard.

## Speaking rate

| Setting | Value | Source |
|---|---|---|
| Whole-video rate (words ÷ full duration) | **142-154 wpm**, aim **149** | **Measured**: niche hits, interquartile range and median, n = 20 ([`corpus/metrics.csv`](corpus/metrics.csv), `wpm`) |
| Range not to leave | 138-161 wpm | **Measured**: hits' 10th-90th percentile, n = 20 |
| Flops, for reference | 147 wpm [140-152] | **Measured**, n = 10: the rate does not separate hits from flops |
| Script length that fits 13-15 min | 2,000-2,250 words → 13.4-15.1 min at 149 wpm | `PLAN_ACTION.md` § 7 (length) × the measured rate |
| Zehon, for contrast | 3.69 words/s **in speech only** (221 wpm), "rushed" | Zehon audit V6 (`lecons.md`). Not comparable as is: speech-only rate, in French. Compare after S06 measures Whose Dime the same way |

The niche rate includes music, pauses and the sponsor read, so the
narrator's speech-only rate is higher (**assumed**: 165-180 wpm). S06 sets
the model's speed so that the **whole** voice track lands at 142-154 wpm,
pauses included, and writes both rates down (ROADMAP S06).

## Pauses

Start from the audit values (C6), then tune by ear on the 20 s sample (D6).
The values are **assumed** starting points, not measured.

| After | Pause | Source |
|---|---|---|
| A full stop inside a block | **250 ms** | Zehon audit C6 |
| A question | **450 ms** | Zehon audit C6 |
| The end of a block (2-4 sentences) | **700 ms** | Zehon audit C6 |
| A quoted line, before the narrator resumes | 450 ms (as a question) | **Assumed**: a change of speaker needs the same breath as a question |
| A chapter card | the card's own length, no extra | **Assumed** |

A comma stays inside the synthesised block: the model phrases it (C6.1).

## Energy

- **Steady warmth, with reactions**: the narrator is surprised, amused or
  blunt at least once per beat (by-ear rule E4). **Assumed** from the
  Crayon report (mini-scenes, a wry tone) and from the Zehon audit S5 (a
  tone fixed to "calm" sounded flat).
- **Numbers slow down**: a sentence with a dollar amount is said a little
  slower than its neighbours. **Assumed**; the script rule S7 keeps them
  to about one per 40 words.
- **No hype ending**: the last 20 s bridge to the next episode in the
  same voice, not a louder "call to action" voice (PLAN_ACTION beat 6).

## The short dialogue lines

- **Who**: a second VoiceDesign voice, clearly different (age or gender),
  same for every character in a video unless two characters talk to each
  other. Crayon plays its mini-scenes with voices (Crayon report, "Des
  mini-scènes dialoguées jouées par des voix"); **assumed** that one extra
  voice is enough.
- **How long**: one line ≤ 12 words, 2-4 lines per scene, 2-3 scenes per
  video (S3: ≥ 1 quoted line per 1,000 words). The 12 words are
  **assumed** (a breath).
- **Only exact or invented-and-labelled**: a line in quotation marks is a
  real, sourced quote from the people registry (D4); a reconstructed
  scene is introduced as such ("Picture the meeting.") and never put in a
  real person's mouth as fact. Source: Zehon audit, "Ce qu'il faut
  adapter" (legal risk on real people).
- **Synthesis**: each dialogue line is its own clip, with 450 ms before
  and after (above).

## What made the Zehon voice robotic

From the Zehon audit § 2, symptom 2. "Measured" and "assumed" are the
audit's own labels.

| # | Cause | Status | Whose Dime answer |
|---|---|---|---|
| V1 | One synthesis per line, without the line before | **Assumed**, strongest hypothesis | Synthesise a block of 2-4 sentences (C6.1); tested blind on video 1 (D7) |
| V2 | 300 ms between every line | **Measured** (setting in the notebook) | Pauses by punctuation (table above) |
| V3 | "One sentence per line, cut long sentences" | **Measured** (rule in `etape3`) | Lines stay whole; long sentences are allowed (rule S6) |
| V4 | No end silence, no fade, no end check | **Measured** (setting); "1 sentence in 6 ends dry" **not reproducible** | Dry-ending detector (C6.3), goal below |
| V5 | 7.4 s reference of an ElevenLabs voice, cloned on Base | **Measured** (file); its effect **assumed** | VoiceDesign reference of 20-30 s with several intonations (C6, "hypothesis to test next") |
| V6 | 3.69 words/s in speech, 9 % faster than Zelan | **Measured** | Whole-track target 142-154 wpm (above) |
| V7 | First listening at assembly | **Measured** (no listening step) | 20 s sample before full synthesis (D6) |

## Blind test for video 1 (D7)

**Question**: does block synthesis (2-4 sentences) sound better than
sentence-by-sentence synthesis, with the Whose Dime voice?

1. **Material**: 20 sentences of the video 1 script (C6: "20 phrases"),
   taken as 6-7 blocks from the cold open, the decision beat and one
   gear-step, so questions, numbers and a dialogue line are all in.
2. **Two versions**: A = one clip per sentence, 300 ms between (the old
   way); B = one clip per block, pauses by punctuation (the new way). Same
   voice, same seed policy.
3. **Blind**: Claude shuffles the 20 pairs and labels them X / Y; the
   key stays in a file Franco opens only after voting (C6).
4. **Vote**: Franco picks the better of X and Y for each pair, and notes
   any ending that sounds cut.
5. **Measure** with the detector: a dry ending is a last transcribed word
   ending < 60 ms before the clip end, or sound still loud in the last
   30 ms (C6.3).

**Pass** (all from Zehon audit C6):

- fewer than **1 dry ending in 30** in version B;
- the old way (A) preferred **fewer than 1 time in 4** (≤ 4 of 20);
- the Whisper similarity of B **not lower** than A's.

**If it fails**: keep B if it wins the vote but has dry endings (fix the
detector and retries); go back to A only if A is preferred 5 times or more.
Then try the longer reference (V5). The voice choice itself (VoiceDesign
or Franco's own voice) is `PLAN_ACTION.md` decision 5, taken at the end of
S1 by the 4-clip ranking with 3 American or Canadian listeners.
