# S11b — Generation test (first real images and clip, then video 1's pieces)

> Changes from ROADMAP.md: follow-up of S11 (08/11). S11 built `whosedime/generate/` and
> measured the container; no paid call was made because the Gemini key was declined in the
> session. The plan moved generation to **Colab, where Drive is mounted** (the connector's
> base64 cannot carry MB files). This session checks the first real run and prepares video 1's.

## Start: preconditions (check, else report and stop)

1. `generate_whosedime.ipynb` is in `main` (Franco merged a PR of the work branch), else
   say so to the orchestrator: the Drive launcher `WhoseDime/generate_launcher.ipynb`
   (placed by S11) clones `main` and cannot find the notebook before.
2. Video 1 has `03_scenes.md` in Drive (video 1's session 3), else nothing to generate.
3. `Videos/01_uber/generate/ledger.jsonl` exists in Drive: Franco ran the launcher with
   `MODE = "test"` (3 images, 1 clip, $0.98), with his key as the Colab secret `GEMINI_API_KEY`.

If 1 or 2 fail: send the orchestrator one line (what is missing, who acts), then stop.
If only 3 fails: tell Franco in one line what to click (launcher, `VIDEO = "01_uber"`,
`MODE = "test"`), then stop.

## Read

`docs/whosedime/generation_report.md`, `whosedime/generate/README.md`, `STATE.md`.

## Do

1. Read `generate/ledger.jsonl` and `generate/status.json` (small, via the connector): models,
   sizes (`px` should be 2752x1536), seconds, `usage`, any `warning` or `error`. Fix the
   code if the real answer differs from the assumed one (tests first, with that answer shape).
2. Look at the 3 images and the clip: ask Franco to open them in Drive, or download a
   **reduced** copy only if it is small (a few KB): never pull a 2K PNG through the context.
   Check them against the S11 assumptions: style steady across separate calls, no text,
   no logo, no likeness, continuity reference kept.
3. Give Franco the measured price of the test (ledger total) and the estimate for the
   rest of video 1 (`MODE = "estimate"`), and ask for the amount (one question). Only with
   his word: he runs `MODE = "full"` with `APPROVED_USD`.
4. Voice (S11 warning): the CPU sample spoke at 206 words a minute (target 142-154). When
   the Colab 20 s sample exists, read its rate in `voice/listen_20s.json`; flag it if above 161.

## Do not

- Spend beyond the agreed amount; never print a key; never put a real name in a prompt.
- Edit video 1's content files, the checker, or the voice and assembly notebooks.

## Hand-off

`ROADMAP.md` "The hand-off" (D17, D19: report to `session_01Cw13LhWRZyGn7FWUAAzMb1`).
Model: **Sonnet 5.5**.
