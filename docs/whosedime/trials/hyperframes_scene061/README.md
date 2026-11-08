# Trial: animated `icons` chart with HyperFrames (2026-11-08)

Decision D16 (an `icons` block of people may animate). **Not for video 1** (Franco,
08/11): Claude reminds Franco when video 2 starts. Not wired into the assembly.

## What was measured (this container, 4 cores)

- HyperFrames 0.9.22 (npm, Apache-2.0), Node 22, GSAP 3.15.1 copied next to `index.html`
  (no download at render time); telemetry turned off (`npx hyperframes telemetry disable`).
- Scene 61 of the Uber eval, 95 figures at 30 per second: 6 s of 1920x1080, 30 fps, H.264
  rendered in 7.4 s (`appear` and `vanish`, the same).
- The last frame of `appear` matches `charts.py`'s still PNG: 0.6 % of pixels differ (shape edges).
- Not tried: Colab (2 cores; Node 22 and Chrome to install), the assembly reading the clip.

## How it works (D4 kept)

`export_icons.py` checks the cell with `charts.py` and draws every text and number into
`background.png`; only the boxes of the animated figures go to `figures.json`.
`make_html.py` writes `index.html`: the HTML holds no number, it only moves shapes.

```bash
python3 export_icons.py <repo> 61 proj        # background.png + figures.json
cp node_modules/gsap/dist/gsap.min.js proj/
python3 make_html.py proj appear              # or: vanish
cd proj && npx hyperframes render . -o ../scene061_appear.mp4 --fps 30
```

`appear`: figures arrive one by one in reading order. `vanish`: the grid is full, then the
figures go pale (18 % opacity) one by one in a fixed shuffled order.
