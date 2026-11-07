# Production system for a long-form (8-20 min) English/US faceless finance channel: stack, time budget, automation path

Researched 2026-11-05. "Repo" sources are files in this repository (Zehon pipeline). Some Zehon measurements exist only on the branch `origin/claude/optimistic-bohr-5f78k4` (latest Zehon state, 01/10/2026). The working branch's `docs/chaine2/CONTEXTE.md` stops at 30/09 and is out of date. Web sources were fetched on 2026-11-05 unless another date is given.

## 1. Zehon audit: what works, what slows it, what to reuse, what must change

### Takeaway
Zehon already has a working end-to-end chain that has been measured on 2 real videos. Content runs in Claude Code and writes to Drive. Images come from the Gemini app by hand, the voice from Qwen3-TTS on a Colab T4, and the assembly from a Python/OpenCV + FFmpeg render in Colab. The slow, manual part is generating and checking images in the Gemini app, one image per message. Rendering takes about 5 min of compute per minute of video. Most of the code can be reused for English finance. The parts to change are scene count and visual mix (charts), a line-by-line finance fact-check step, an English voice/lexicon, and thumbnails produced without a watermark.

### Cited Findings
**Pipeline shape (repo)**
- Zehon runs 5 content steps with 4 human pauses: topic, research, outline, script, then scenes/prompts and publication. State lives in fixed-name files in Drive (`01_recherche.md`, `02_script.md`, `02_script_voix.txt`, `03_scenes.md`, `04_publication.md`), so any session or account can resume. Franco makes the images (Gemini), the animated clips (Veo/Flow) and the thumbnails himself — [repo: zehon/content-maker/SKILL.md](zehon/content-maker/SKILL.md).
- One video = **5 Claude sessions, one per phase**, each with its own model: Sonnet for topic/research, Opus for outline/script, Sonnet for scenes/publication, Sonnet for pieces/image review, Haiku for the assembly verdict. The goal was to save tokens. This was a recommendation, not a measurement (30/09/2026) — [repo: content-maker SKILL.md on branch optimistic-bohr, "Les sessions"].
- `content-maker` passed **96% of checks with the skill vs 26% without** on 3 test cases, at a cost of about **450 s and 47,000 extra tokens per task** (measured 29/09/2026) — [repo: docs/chaine2/nouveau_systeme.md §10](docs/chaine2/nouveau_systeme.md).
- The scene file (`03_scenes.md`) is the contract between script and render. Each scene holds an exact, continuous excerpt of the script. The renderer aligns it to word timestamps from Whisper, so durations are never written by hand — [repo: nouveau_systeme.md §6; content-maker/references/etape4_scenes.md](zehon/content-maker/references/etape4_scenes.md).

**Measured on the first real video ("le sel", 30/09/2026) — [repo: docs/chaine2/historique.md, branch optimistic-bohr]**
- 1,551 words → **80 scenes (76 Gemini images, 8 animated clips, 4 title cards), 7 min 55 s**.
- Voice: 461.8 s of audio, **synthesised in 22 min on a T4**, at 3.36 words/s including pauses. The reference was an ElevenLabs voice sample of 7.4 s.
- Render in Colab: **2,536 s (42 min) for a 7:55 video**, 287 MB, 1080p. The earlier estimate of 20-30 min was wrong. A 10-scene test extract takes about 5 min. The second video ("le verre", 8:02) rendered in **44 min**.
- Image QA: **4 of 76 images (≈5%) had unwanted English text** (e.g., "SALT" on sacks) and 1 more had minor text. Franco accepted them as is.
- The Drive connector downloads **at most 10 MB per file** and cannot upload large binaries. So the full video is rendered and stored in Colab, and Claude only reads a <1 KB `verdict.json` and 6 small preview JPEGs.
- The raw voice came out at −22 LUFS (too quiet) and was normalised to about −15/−16 LUFS. Audio QA runs automatically (silence, clipping, resolution, duration).
- **Failure points logged** — [repo: CONTEXTE.md / historique.md, branch optimistic-bohr; etape4_scenes.md]:
  - Gemini drew an **extra arm on 2 of 2 character sheets**.
  - In chat mode Gemini narrates and chains unrequested images. The fix is an "image generator" preamble that asks for one image per message.
  - Gemini **copied the reference sheet into a scene** (01/10/2026).
  - faster-whisper crashed on Colab because of a PyAV incompatibility. The fix passes the audio in memory.
  - Whisper writing numbers as digits triggered **19 false "re-listen" alerts out of 140 sentences**. Fixed: numbers are converted back to words before comparison.
  - **About 1 sentence in 6 of Qwen3-TTS output ends abruptly**, cutting off the last sound (measured on "le verre", 01/10/2026).
  - FFmpeg is missing from the Claude Code container unless installed with `apt-get update && apt-get install ffmpeg`.
  - YouTube blocks transcript fetching (yt-dlp, youtube-transcript-api) from cloud IPs.
- The renderer is Python (OpenCV, Pillow) + FFmpeg, chosen over HyperFrames/Chromium. The same script runs in Claude Code and in Colab and can be tested. It does slow zoom/pan, crossfades, title cards, animated keyword text, burned-in word-highlight subtitles plus a `.srt`, and music ducking (default −26 dB). Drive notebooks are fixed "launchers" that clone the repo — [repo: historique.md, branch optimistic-bohr].

**Finance-channel requirements (from the earlier report)**
- Winning formats: **simulations ("Your Life at Every Level of…", POV) of 12-20 min**, where none of the 24 videos under 12 min reached 3× the channel median. **Business explainers work at 8-13 min.** Script length is about 2,300-2,500 words for 15-17 min. Thumbnails use **one recurring mascot**, a contrast, 0-3 words and warm colours — [repo: reports/Croissance chaînes YouTube finance.md](reports/Croissance%20cha%C3%AEnes%20YouTube%20finance.md).
- The same report recommends a **line-by-line fact-check with a source per claim** (Bille Finance advertises "fact-checked line by line") and **charts built from real figures**, which also vary the visuals away from "image slideshow" content. It cites a figure of **16-28 h per faceless documentary in classic solo production** ([OutlierKit](https://outlierkit.com/resources/faceless-business-documentary-channels/), as cited in the report).

### Inferences
- **Reusable as is:** the Drive file contract, the resume-from-files logic, `verifier.py` checks (with English thresholds), the voice notebook (switch `language="English"` and Whisper `"en"`), `monter.py` (render, subtitles, music, QA), and the session-per-phase model split.
- **Scene count for 15 min:** at Zehon's 6 s per scene, 15 min ≈ 150 scenes. At 8-10 s ≈ 90-110. Recommended mix for a 15-min simulation (inference):
  - 70-90 Gemini images;
  - 20-30 code-rendered visuals (charts, number cards, "level" counters, made with matplotlib/Pillow from the fact-check sheet);
  - 6-10 animated clips;
  - level title cards.
  This cuts manual image work by about 40% and adds the "real data" layer.
- **Render time scales linearly:** about 80-85 min for 15 min of video and about 55 min for 10 min, on a Colab CPU runtime. This fits a free session but must run unattended (see Q4).
- **Mascot across 150-300 images:** the Zehon method (sheet + preamble + batches of 10 per conversation + an extra-arm check) is proven at 76 images per video. At 150 images that means about 15 Gemini conversations per video, each needing the sheet re-attached.
- **New step needed:** `02b_factcheck.md`, a table of claim → value → source URL → date retrieved, written by Claude and checked by Franco. Chart scenes read their numbers from it.
- **Thumbnails:** Zehon thumbnails come from the free Gemini app (see Q3 on the watermark). A finance channel needs 3 thumbnail templates built around the mascot (progression triptych, hidden wealth, conflict), per the report.

### Gaps
- **No measured human hours per Zehon video** are recorded anywhere in the repo. The time per video in Q6 is therefore an estimate. Git timestamps show both videos were produced while the system was being built, so they are not representative.
- Franco's time to generate and check 76 images in the Gemini app was not measured.

## 2. Qwen3-TTS: versions, quality, Colab feasibility, licence, and the legal risk of cloning a "commercial AI voice"

### Takeaway
Qwen3-TTS (released 22 Jan 2026, Apache-2.0) runs on a free T4 at about 3× slower than real time. Zehon measured 22 min for 7.7 min of audio, so 15 min of narration takes about 45 min. Vendor benchmarks claim it matches or beats ElevenLabs. Independent users find ElevenLabs more natural over long passages, and Zehon measured clipped sentence endings. The model licence is not the problem; the **source voice** is. A voice designed from a text prompt (Qwen VoiceDesign, or ElevenLabs Voice Design on a paid plan) or Franco's own voice is safe. Cloning a real person's voice, or a Voice Library voice actor's voice, without a licence is a right-of-publicity risk.

### Cited Findings
- **Releases:** 0.6B and 1.7B models came out on **22 Jan 2026** (tech report arXiv 2601.15621). Variants: **Base** (3-second voice clone, fine-tunable), **CustomVoice** (preset speakers with instruction style control) and **VoiceDesign** (creates a voice from a text description). The repo documents this workflow: VoiceDesign → reference clip → `create_voice_clone_prompt` on Base → reuse for every line. Batch inference is supported, and vLLM-Omni has day-0 offline support — [QwenLM/Qwen3-TTS GitHub](https://github.com/QwenLM/Qwen3-TTS); [HF model card](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base).
- **Licence: Apache-2.0.** The model card and GitHub page carry no usage or ethics restriction on cloning beyond the licence — [HF model card](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base).
- **Vendor benchmarks:** the model card reports 1.7B-Base WER lower than ElevenLabs in English, French and 5 other languages, and higher in German, Portuguese and Spanish. It also reports speaker similarity higher than ElevenLabs in most languages. These are Qwen's own evaluations — [HF model card](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base).
- **Independent production report (09 Apr 2026):**
  - Qwen3-TTS 1.7B has "flat intonation, uniform rhythm" over long passages and no inline emotion tags.
  - It mispronounces English tech terms (in a Portuguese context), and the first syllable is clipped unless the reference has leading silence.
  - Throughput is about 1× real time on an unnamed RunPod GPU, at about $0.08 per 28-min episode vs about $2.70 with ElevenLabs.
  - The author's verdict: Qwen3 "doesn't beat even ElevenLabs v2" — [akitaonrails.com](https://akitaonrails.com/en/2026/04/09/how-elevenlabs-was-not-killed-by-qwen3-tts).
- **VRAM:** one guide gives 2-7 GB for the 1.7B model, which fits a 16 GB T4. The official pages give no figure — [ltx-2 guide](https://ltx-2-7y7.pages.dev/blog/qwen3-tts-comprehensive-guide-en).
- **Measured on T4 by Zehon:** 461.8 s of audio in 22 min (≈2.9× real time), bf16. About 1 sentence in 6 ends abruptly — [repo: historique.md / CONTEXTE.md, branch optimistic-bohr].
- **ElevenLabs Terms (last updated 09 Oct 2026):**
  - free users "may only use the Services for non-commercial purposes" (§1(c));
  - "you retain all rights in and to your Output" (§4(c)(ii));
  - "You may not provide Input or create Output for which you do not have all the rights necessary" (§4(g));
  - the Voice Library is governed by a separate Voice Library Addendum.
  The fetched page showed no clause restricting the use of Output to train other models — [ElevenLabs Terms](https://elevenlabs.io/terms-of-use).
- ElevenLabs help centre: commercial use is allowed if you hold the IP rights and comply with the ToS/Prohibited Use Policy; "some products and features may have additional terms" — [ElevenLabs help](https://elevenlabs.io/docs/help-center/legal/can-i-publish-the-content-i-generate-on-the-platform/llms.txt). Third-party guide: Voice Library voices "may carry additional terms set by the individual voice creator" — [licenseorg](https://licenseorg.com/blog/elevenlabs-licensing-guide-ai-voices).
- **Case law:** in *Lehrman & Sage v. Lovo* (S.D.N.Y., July 2025), federal trademark and most copyright claims over AI voice clones were dismissed, but **state right-of-publicity claims for commercial cloning survived**. Lovo filed for Chapter 7 and the case was stayed on 11 Jun 2026 — [Tushnet](https://tushnet.com/2025/07/21/ai-voice-cloning-opinion-narrows-claims-to-rop-rejecting-tm-and-most-copyright-theories/); [Resemble deepfake watchlist, June 2026](https://www.resemble.ai/resources/the-deepfake-watchlist-week-of-june-19-25-2026). The **NO FAKES Act** (a federal right in one's voice) was advanced by the Senate Judiciary Committee on 18 Jun 2026, with no final passage found. Tennessee's ELVIS Act (Mar 2024) extends the right of publicity to AI voice — same sources.
- **YouTube:** cloning one's own voice for voice-overs does not require disclosure. A realistic depiction of a real person giving advice they never gave does. The help page does not address narration with another real person's cloned voice — [YouTube Help 14328491](https://support.google.com/youtube/answer/14328491?hl=en).
- **Colab:** the FAQ lists "creating deepfakes" and "using multiple accounts to get around limits" among disallowed activities — [Colab FAQ](https://research.google.com/colaboratory/faq.html).
- **Zehon's current choice (30/09/2026):** "a male narrative voice created on ElevenLabs, cloned by Qwen3-TTS". The commercial licence of the ElevenLabs plan used is still flagged "to verify" — [repo: historique.md, branch optimistic-bohr].

### Inferences
- **Safe source voices, in order:**
  1. **Qwen3-TTS VoiceDesign** voice made from a text prompt. It is fully owned, costs $0, sits under Apache-2.0, and no real person is behind it.
  2. **ElevenLabs Voice Design** (synthetic, not a Library voice) generated on a **paid** plan, then cloned. The output is owned per §4(c)(ii), but a free-plan sample is non-commercial.
  3. Franco's own voice: no disclosure needed, but his accent in English is untested.
  4. A voice actor's sample bought with a written licence that explicitly covers AI cloning.
  **Avoid:** Voice Library voices (real actors, governed by the Addendum), celebrity or known-YouTuber voices, and any free-plan ElevenLabs output used commercially.
- For a US finance channel, the "very realistic" goal conflicts with Qwen's measured flat long-form prosody. Mitigations: one sentence per call (as Zehon does), seeds re-rolled on flagged lines, 200-400 ms leading silence in the reference, and an English pronunciation lexicon for terms like 401(k), APR, S&P 500 and "Roth". Benchmark: A/B the first 60 s against an ElevenLabs Starter render before committing.
- **15-min timing on a T4:** about 2,300-2,400 words at an assumed 150-160 wpm ≈ 15 min of audio → **≈45 min synthesis + ≈5 min model load + ≈3 min Whisper.** One run fits inside a free session. The Drive cache already resumes after disconnects.

### Gaps
- No independent English MOS/naturalness test of Qwen3-TTS vs ElevenLabs v3 was found. No newer Qwen3-TTS release after Jan 2026 was found in the sources read.
- I did not read the ElevenLabs Voice Library Addendum or the Prohibited Use Policy text itself. Whether ElevenLabs forbids using its Output as a cloning reference for another engine is unconfirmed: the clause was not seen in the fetched ToS.
- The ElevenLabs plan Franco used for the Zehon voice is unknown.

## 3. Gemini images: free limits, commercial terms, watermark, mascot consistency, paid cost, animated shots

### Takeaway
The free Gemini app gives roughly **20 Nano Banana 2 images per day** (secondary sources). Google's own page publishes no fixed numbers, only relative tiers (Plus 2×, Pro 4×). That is far below 150-300 images per video at more than 1 video a week. The API has **no free tier for image models**. Paid images cost **$0.039** (2.5 Flash Image; $0.0195 in batch) to **$0.067** (Nano Banana 2 at 1K) each, so about $3-14 per video. The visible sparkle watermark appears on free and AI Pro app images. **API/AI Studio output with a paid key has no visible sparkle**; the invisible SynthID always stays. That is the clean, legitimate route for thumbnails.

### Cited Findings
- **Official Gemini app limits page:** usage is compute-based, "Your limit refreshes every 5 hours until you reach your weekly limit". No AI plan = standard limits; AI Plus 2×; AI Pro 4×; AI Ultra 5× or 20× AI Pro. Image generation (Nano Banana 2) is available on the free plan. Nano Banana Pro "redo" and video generation appear to need a plan. No exact counts are published — [Google Gemini Help 16275805](https://support.google.com/gemini/answer/16275805?hl=en).
- **Secondary sources:** free ≈ 20 Nano Banana 2 images/day at up to 1K, varying with load; Nano Banana Pro free ≈ 2-3/day — [Analytics Insight](https://www.analyticsinsight.net/artificial-intelligence/nano-banana-ai-daily-image-generation-limits-for-free-pro-and-ultra-plans-with-google-gemini); [zenken](https://ai.zenken.co.jp/en/post/gemini-image-guide/). Older Feb 2026 posts cite about 100/day for the original Nano Banana, which is likely outdated.
- **API pricing (AI Studio pricing page, fetched 2026-11-05):**
  - free tier "Not available" for all image models;
  - Gemini 2.5 Flash Image $0.039/image (batch $0.0195);
  - Gemini 3.1 Flash Image (Nano Banana 2) $0.045 (0.5K), $0.067 (1K), $0.101 (2K), $0.151 (4K);
  - Gemini 3 Pro Image $0.134 (1K/2K), $0.24 (4K);
  - paid-tier data is not used to improve products.
  — [Google AI Studio pricing](https://aistudio.google.com/docs/pricing).
- **Visible watermark:** secondary sources report the sparkle on free and Google AI Pro images, and none on AI Ultra or on AI Studio/API output with a paid key. SynthID stays in all cases — [Google AI Developers Forum thread](https://discuss.ai.google.dev/t/regression-forced-visible-star-watermark-breaks-gemini-nano-banana-pro-image-to-image-and-flow-frame-to-video-workflows/114193); [PhoneArena](https://www.phonearena.com/news/google-upgrades-their-image-creation-with-nano-banana-pro-built-on-gemini-3-pro_id175929); [yingtu.ai](https://yingtu.ai/blog/nano-banana-pro-watermark). The earlier finance report observed the sparkle on some Bille and Owen thumbnails — [repo report](reports/Croissance%20cha%C3%AEnes%20YouTube%20finance.md).
- **YouTube auto-labels** content with C2PA metadata or detected as AI. The help page doesn't mention SynthID. AI help for a thumbnail counts as "production assistance" that needs no disclosure, and disclosure itself doesn't limit reach or monetisation — [YouTube Help 14328491](https://support.google.com/youtube/answer/14328491?hl=en).
- **Commercial use:** secondary sources agree Google does not claim ownership of Gemini outputs but disagree on whether there is an explicit commercial licence. The old Generative AI Additional Terms were deprecated on 22 May 2024. Free-tier prompts and images may be used to improve models. Copyrightability of AI images is unsettled — [terms.law](https://terms.law/ai-output-rights/gemini/); [licenseorg](https://licenseorg.com/guide/ai-content/google-gemini-image).
- **Animated shots:** Veo is no longer free in the Gemini app (the promo ended 24 Aug 2025). **Google Flow free accounts get 50 credits/day**, and a Veo 3.1 Lite clip costs 10 credits, so about 5 clips/day. Google AI Pro ($19.99/month) gives 1,000 Flow credits/month — [Krea, 2026](https://www.krea.ai/blog/best-free-ai-video-generators-in-2026); [zsky.ai](https://zsky.ai/blog/how-much-does-google-veo-cost); [Android Central](https://www.androidcentral.com/apps-software/googles-new-ai-video-generator-is-free-for-gemini-users-but-not-for-long). Zehon produced 8 clips (1280×720, 24 fps, 8 s) per video through the Gemini Video tool or Flow — [repo: historique.md].
- **Mascot consistency (Zehon, measured):** reference sheet (front, ¾, side, back, 4 expressions) + "image generator" preamble re-attached in each conversation + **batches of 10 per conversation**. Known defects: extra arm, text in image (~5%), sheet copied into the scene — [repo: etape4_scenes.md; historique.md].

### Inferences
- **Volume math:** 2 videos/week × about 100 Gemini images = 200 images/week. At about 20 per day per free account, one account covers about 140/week at best. Zehon's habit of using **several Google accounts** to stretch free quotas is fragile, and for Colab it explicitly breaches the FAQ. I found no Gemini-app clause either way.
- The cheapest compliant scale-up is the **paid API with batch mode on Gemini 2.5 Flash Image**: about 100 images × $0.0195 ≈ **$2 per video**, ≈ $16/month at 2 videos/week; at 1K Nano Banana 2 prices ≈ $6.70/video. The API also allows **automation** (Claude writes prompts → a Colab or GitHub script calls the API with the mascot sheet attached to every call → files land in `images/`). This removes the biggest manual block. It breaks the "$0 beyond Claude" budget but stays near-free.
- **Thumbnails:** generate them through the paid API (about $0.04-0.13 each, so less than $1 per video for 5 variants), with no visible sparkle and SynthID kept. Do not use watermark-removal tools on app images. Whether the Gemini/Google terms forbid removing the visible mark was not verified, and AI Studio offers a clean, permitted route anyway.
- Alternative at $19.99/month: **Google AI Pro** gives 4× the app image limits and 1,000 Flow credits, but the visible sparkle reportedly remains on Pro.

### Gaps
- Google publishes no exact daily image count for the free app. Its consistency limits for multi-reference images were not tested on 150-300 images.
- Imagen 4 and Veo API prices were not captured: the pricing page was truncated.
- No official Google statement was found on whether AI Pro images carry the visible sparkle.

## 4. Editing on Colab: assembly, limits, render time, music/SFX

### Takeaway
Zehon's `monter.py` (OpenCV + Pillow + FFmpeg, CPU) already does Ken Burns, crossfades, title cards, keyword text, word-highlighted subtitles, music ducking and automated QA. It is a working "Remotion-like" renderer and needs no GPU. Measured speed is about 5.3 min of render per minute of video, so 80+ min for a 15-min video. Free Colab sessions last up to 12 h but have unpublished idle timeouts and GPU quotas.

### Cited Findings
- Render measured at 42 min for 7:55 and 44 min for 8:02, on a Colab CPU runtime, output 287 MB in 1080p. A 10-scene extract (48 s) renders in 83 s on 4 cores in the Claude Code container — [repo: historique.md, branch optimistic-bohr].
- Features built: zoom/pan, 0.5-1 s fades, title cards, animated text, burned-in subtitles (34 chars, 7 words max, current word gold), `.srt` export (164 subtitles, 97% aligned on the voice), music bed looped with fades at −26 dB (−6 dB more under the voice), and `verdict.json` with preview frames. Validated by Franco on 30/09/2026 — same source.
- **Colab free tier:** runtimes last "at most 12 hours, depending on availability and your usage patterns". Idle timeouts vary and are not published. GPU limits are not published and change over time; use a CPU runtime when no GPU is needed. Disallowed: multiple accounts to get around limits, deepfakes, and bypassing the notebook UI or remote control on free sessions. Pro+ allows up to 24 h of continuous execution — [Colab FAQ](https://research.google.com/colaboratory/faq.html).
- **Music:** Zehon's criteria are the YouTube Audio Library with "attribution not required", calm ambient, no drums or vocals. Measured: a −14 LUFS bed ends 23 dB under the voice — [repo: historique.md].

### Inferences
- The renderer is CPU-bound frame-by-frame OpenCV. Expected **≈80-85 min for 15 min** and ≈55 min for 10 min. Speed-ups worth testing:
  - render scenes in parallel processes, then concatenate with FFmpeg;
  - use FFmpeg's `zoompan` filter for still scenes instead of Python frame loops;
  - render at 30 fps rather than higher (Zehon already uses 30).
  A 2-3× gain is plausible but unmeasured.
- Finance channels need additional blocks: **animated charts / counters** (matplotlib frames or Pillow, driven by `02b_factcheck.md`), a "level" banner for simulations, and SFX hits (whoosh, cash register). The YouTube Audio Library has a sound-effects section, but its terms were not checked in this session.
- Keep voice (GPU) and render (CPU) as **separate notebook runs** so the render does not eat GPU quota.

### Gaps
- No measurement exists of `monter.py` with parallelism, or on a Colab GPU runtime.
- YouTube Audio Library licence terms (attribution flags, Content ID behaviour) were not fetched in this session.

## 5. Claude Pro ($20/month) limits and fit for scripts + research

### Takeaway
Anthropic does not publish a message count. Pro has a **5-hour session limit plus a weekly limit**, shared between claude.ai and Claude Code. Third-party estimates and reported 2026 changes are inconsistent. Zehon's measured content workflow is token-heavy (about 47 k extra tokens per task, 5 sessions per video), and Franco already rotates **several Pro accounts**. One Pro account will likely support about 1-2 finance videos per week only if the expensive model is reserved for the script and research is kept lean.

### Cited Findings
- "Pro and Max plans have a five-hour session limit and a weekly limit." Claude Code and claude.ai share the same limits. Check with `/status`. Options when you hit the limit: wait, enable usage credits (extra usage), switch to API credits, or upgrade to Max. An `ANTHROPIC_API_KEY` env var switches billing to the API. The article gives no numbers or dates ("Updated this week") — [Anthropic Help: Using Claude Code with Pro/Max](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan).
- **Third-party claims (conflicting):**
  - Claude Code 5-hour limits were doubled for Pro/Max on 6 May 2026, and peak-hour throttling was removed;
  - weekly changes are disputed (+50% temporary from 13 May 2026; "25% higher since 14 September");
  - estimates of about 40-80 Sonnet hours/week and about 45 prompts per 5 h on Pro.
  — [morphllm](https://www.morphllm.com/claude-code-usage-limits); [verdent.ai](https://www.verdent.ai/guides/claude-code-limits-doubled-may-2026); [alexcloudstar](https://alexcloudstar.com/blog/claude-code-usage-limits-2026/).
- **Zehon:** content-maker costs about 47,000 extra tokens and 450 s per task (measured). There are 5 sessions per video with a model per phase (Opus only for the script) to save tokens. Franco works on "comptes Pro" (plural) — [repo: nouveau_systeme.md §10; CONTEXTE.md].

### Inferences
- Rough per-video budget for a 15-min finance video:
  - research and fact-check with web fetches is the heaviest phase (many pages read in context);
  - the script (about 2,400 words plus one revision) is small in output tokens but long in context;
  - scenes and prompts mean about 100-150 prompts printed in chat, which is output-heavy.
- **Tips:**
  - keep the one-phase-per-session rule;
  - use Sonnet for research and prompts and Opus only for the script;
  - let Claude write scenes and prompts to a file via a Python generator (as Zehon already does) instead of printing 150 prompts in chat;
  - cache research per topic family (credit, tax, retirement) in `Memoire/` so it is reused across a series;
  - batch similar videos ("Every Level" series) to reuse structure;
  - check `/status` before starting a heavy phase.
- Rotating multiple paid accounts to dodge limits may conflict with Anthropic's terms. This was not verified here. The legitimate escalation is "extra usage" credits or Max.

### Gaps
- No official numeric Pro limit and no measured token count per full Zehon video were found, so "how many 2,400-word scripts per week" cannot be stated as a fact. Measure it: run `/status` before and after each phase on the first 2 videos.

## 6. Time budget per video and weekly capacity at 20 h

### Takeaway
No human hours are measured for Zehon, so these are estimates built from Zehon's measured machine times and step list. Estimates: a 15-min simulation takes about 14-18 h for the first videos and about 8-11 h once optimised. A 10-min business explainer takes about 10-13 h first and about 6-8 h later. That means about **1 video/week in month 1 and 2/week after optimisation** within 20 h. The 7-9 videos in 14 days that the winners published is out of reach with manual Gemini-app images. Image generation is the lever.

### Cited Findings
- **Machine times:** voice ≈2.9× audio length on a T4; render ≈5.3× video length on CPU; scene alignment 0.3 s — [repo: historique.md, branch optimistic-bohr].
- 76 images + 8 clips + 5 thumbnails were produced by hand by Franco for 8 min — [repo: historique.md].
- Classic solo faceless documentary: 16-28 h per video — [OutlierKit, cited in repo report](https://outlierkit.com/resources/faceless-business-documentary-channels/).
- Winners published 7-9 long videos in their first 14 days, and the first breakout came between video 1 and video 11 — [repo report](reports/Croissance%20cha%C3%AEnes%20YouTube%20finance.md).

### Inferences
Estimated Franco hours per video. Machine time runs unattended in parallel.

| Step | 15-min simulation, first videos | optimised | 10-min explainer, optimised |
|---|---|---|---|
| Topic + angle pick (pause) | 0.5 | 0.25 | 0.25 |
| Research + fact-check review (`02b_factcheck.md`) | 2-3 | 1.5 | 1-1.5 |
| Outline + script review (2 pauses) | 2 | 1-1.5 | 1 |
| Images: about 100 in the Gemini app at ~1.5-2 min each incl. save/rename/check/redo | 3-4 | 2.5 (app) / 0.5 (API batch) | 1.5 / 0.3 |
| Animated clips (6-8, Flow) | 1 | 0.5 | 0.5 |
| Voice run + re-listen to flagged lines | 0.75 | 0.5 | 0.3 |
| Render launch + watch-through QA | 1.5 | 1 | 0.75 |
| Thumbnails (3-5) + title/description | 1.5 | 1 | 0.75 |
| Upload/schedule/end screens | 0.5 | 0.25 (API) | 0.25 |
| **Total** | **≈13-15 h** (+2-3 h of first-time setup per format) | **≈8.5-9 h (app) / ≈6.5 h (API images)** | **≈6-7 h / ≈4.5 h** |

- **Weekly capacity at 20 h:**
  - weeks 1-4: 1-1.5 videos/week, plus building the English variant of the system;
  - after optimisation: 2 simulations/week, or 2 simulations + 1 explainer if images go through the paid API.
  - Batch work: research one series of 3 at once, scripts in one sitting, all images of 2 videos in one Gemini day per account, voice and render overnight.
- **Pre-launch bank:** the report recommends 6 videos ahead. At about 12 h each that is about 72 h, i.e. 3.5 weeks at 20 h/week before publishing day 1.

### Gaps
- Every human-hour figure above is an estimate. Franco should log time per step on the first 2 finance videos.

## 7. Automation path after launch, and what must stay human

### Takeaway
Upload automation is now cheaper and less restricted than commonly assumed. As of the 2026-11-05 fetch, YouTube's `videos.insert` docs list a **separate "Video Uploads" quota bucket, 1 unit per call, 100 calls/day**, and state that **videos from unverified API projects are *not* restricted to private**. There is also a `status.containsSyntheticMedia` field for AI disclosure. The realistic $0 automation path is Colab (voice, render) + the Gemini API (images) + a YouTube upload script with `publishAt` scheduling, all triggered by Claude Code. Topic choice, fact-check sign-off and the final watch-through stay human, both to protect quality and as evidence against the "inauthentic content" policy.

### Cited Findings
- `videos.insert`: "Quota impact: 100 calls per day. A call to this method has a quota cost of 1 unit in the Video Uploads quota bucket." Max file 256 GB. `status.publishAt` supports scheduling. "Videos uploaded from unverified API projects are not restricted to private viewing mode." `status.containsSyntheticMedia` is a writable field — [YouTube Data API: videos.insert](https://developers.google.com/youtube/v3/docs/videos/insert) (redirects to /youtube/data/reference/rest/v3/videos/insert; fetched 2026-11-05). This **contradicts the older rule** (private-until-audit for projects created after 28 Jul 2020, upload = 1,600 units) that the brief assumed.
- **Disclosure** doesn't limit reach or monetisation, but repeated non-disclosure can lead to penalties including YPP suspension. Realistic synthetic scenes or real people saying things they didn't need disclosure; animation and production assistance don't — [YouTube Help 14328491](https://support.google.com/youtube/answer/14328491?hl=en).
- **"Inauthentic content":** YouTube does not monetise repetitive, templated, mass-produced content "with little variation"; AI itself isn't banned. A clarification on 16 Jul 2026 split it into categories — [TechCrunch 20 Jul 2026, cited in repo revenus doc](https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/). Reviews appear to weigh the channel's overall character. A January 2026 report says 16 channels (35 M subscribers) were terminated — [AIR Media-Tech timeline](https://air.io/en/monetization/youtube-monetization-policy-changes-2026-a-complete-dated-timeline); [The Next Web](https://thenextweb.com/news/youtube-ai-slop-crackdown-faceless-creators-collateral-damage). The earlier report flags "templated storylines" risk for the Every Level/POV cluster — [repo report].
- **Colab:** free notebooks can't be driven through remote control or by bypassing the notebook UI on zero-balance sessions. Runtimes last at most 12 h. Using multiple accounts to get around limits is disallowed — [Colab FAQ](https://research.google.com/colaboratory/faq.html). Zehon already uses fixed Drive "launcher" notebooks that clone the repo, so a run is one click — [repo: CONTEXTE.md, branch optimistic-bohr].
- The YouTube Data API key already works in the Zehon environment for stats. Transcripts are blocked from cloud IPs — [repo: CONTEXTE.md].

### Inferences
- **Automation order (highest hours saved first):**
  1. **Images via the Gemini API batch** (about $2-7 per video): a script reads `03_scenes.md` and attaches the mascot sheet to every call. Saves about 2-3 h per video.
  2. **Thumbnails via API** (clean, no sparkle).
  3. **Upload + schedule + thumbnail + captions + `containsSyntheticMedia`** from a Python script run in Claude Code or Colab with OAuth. This saves about 15-20 min per video, but more importantly allows publishing at fixed US times while Franco works from Canada.
  4. **Chained Colab run** (voice → render) in one notebook launch.
  5. **Optional schedulers:** GitHub Actions or Google Apps Script to trigger uploads at `publishAt`. Not needed: YouTube's own `publishAt` already schedules.
  Colab cannot be cron-scheduled on the free tier without breaching the "no remote control / bypass UI" rules, so voice and render stay one click each.
- **Must stay human:** topic and format rotation (formats wear out in 2-3 months per the report), the fact-check sign-off on every dollar figure and rule (tax brackets, contribution limits, rates, with source and date), script approval, image spot-check (extra limbs, text), full watch-through before publish, thumbnail choice, and replies to comments. Keep the dated files of research, fact-checks and approvals as evidence of human authorship if monetisation is challenged.
- **Policy-safe variety:** vary structure per video (simulation vs. explainer vs. POV), and include real data charts and series-specific visuals. Avoid publishing more than about 3/week of the same template.

### Gaps
- `thumbnails.set` and `captions.insert` quota costs and the default daily project quota were not fetched in this session.
- GitHub Actions free-minute limits and Google Apps Script quotas were not verified in this session.
- No primary YouTube source was read for the exact July 2026 inauthentic-content categories (only TechCrunch via the repo, plus secondary blogs).
