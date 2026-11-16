# The narrator from ElevenLabs — Franco's guide (one page)

Decisions D21, D22: ElevenLabs makes **one reference clip** of the narrator; Qwen3-TTS (free, in
Colab) clones it for the 20 s sample and the full voice. Once per channel, not once per video.

## 1. In the ElevenLabs app (Text to Speech)

1. **Pick the voice** you want for "Who Pays?": a warm, relaxed American narrator, not a trailer
   voice. Prefer a voice made with ElevenLabs' **Voice Design** over a Voice Library voice of a
   real person (see § 4).
2. **Paste this text, exactly** (about 70 words, 20-30 s; a statement, two questions, a number,
   an aside: the clone learns several intonations from it):

   > So here's a question nobody asks at the checkout. If the thing is free, who's paying for it? Usually, it's not who you think. Picture an app that loses a million dollars a day. A million! And the people covering it have never even opened the app. Strange, right? Stick around. We're going to follow the money, one dollar at a time, and see where it lands.

   Another text is fine: then save it as a `.txt` with the same name as the audio file.
3. **Settings**: Multilingual v2 (or Eleven v4), Stability about 50 %, Similarity about 75 %,
   Style 0, **Speed 0.9** to start (the clone tends to speak faster than its reference: S11
   measured x1.2). Generate two or three takes and keep the one that sounds most like a story
   told over coffee: no clipped ending, no breath noise, no music.
4. **Download** it (MP3 is fine; WAV if your plan offers it).

## 2. In Drive

Put the file **alone** in `WhoseDime/Voice/elevenlabs/` (any name, e.g. `brian.mp3`; and
`brian.txt` only if you pasted another text). Other takes go to `WhoseDime/Voice/old/`.

## 3. In Colab (voice launcher; needs the pull request merged into `main` first)

1. `MODE = "reference"`, Run all. It trims the clip, converts it to 24 kHz, checks with Whisper that
   it says the text, writes `Voice/ref.wav`, `ref.txt`, `ref.json` (the old ones go to `Voice/old/`)
   and prints the reference's **words a minute**. Aim: 135-155. If it says *too fast*, lower Speed by
   0.1 in ElevenLabs and redo steps 1-3.
2. `MODE = "sample"` (decision D6): listen to `voice/listen_20s.wav`. The run prints the sample's
   rate on the whole sample (target 142-154) and what to change if it is off.
3. `MODE = "full"`, tick `I_LISTENED`. T4 GPU as before.

## 4. What ElevenLabs' terms say (read 2026-11-08; your decision, not Claude's)

| Question | What the text says | Source |
|---|---|---|
| Free plan, monetised channel | Free users "may only use the Services for non-commercial purposes"; the free plan "does not include a commercial license and cannot be used for any commercial purpose". Content made outside a paid subscription stays non-commercial, even after you subscribe | Terms of Use § 1(c) (updated 09 Oct 2026); help centre "Can I publish the content I generate" |
| Paid plan (Starter, $6/month) | "All paid plans include a commercial license" (not for Beta Services); content made during a paid subscription can be used commercially "and indefinitely". You keep the rights in your Output (§ 4(c)) | same |
| Attribution | Free plan: "elevenlabs.io" or "11.ai" in the title. Paid plans: no attribution line in the terms | help centre |
| Using an output as the reference of another model | Not named. The Prohibited Use Policy (updated 09 Oct 2026) § 12 forbids "Using our Services or Output to develop, train, fine-tune, or improve any AI model or service". Cloning by reference changes no model weights, but whether it counts as "develop ... any AI ... service" is **not settled by the text** | elevenlabs.io/use-policy |
| A Voice Library voice | § 3 forbids "Cloning, synthesizing, or impersonating the voice ... of any living individual"; § 9 a voice "without authorization". A Library voice is often a real person's: cloning it in Qwen may fall there. A Voice Design voice is synthetic | same |

*Measured*: the quotes above, read on the pages on 2026-11-08. *Not checked*: the Service-Specific
Terms and the Voice Library's own terms (not opened). Ask ElevenLabs support if in doubt.
