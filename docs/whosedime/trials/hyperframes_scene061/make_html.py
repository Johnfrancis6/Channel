"""Trial: write a HyperFrames composition from figures.json.

    python3 make_html.py PROJ appear|vanish [duration_s] [rate_per_s]

appear: the figures arrive one by one in reading order (hiring, sign-ups).
vanish: the grid is full, then the figures go pale one by one in a fixed shuffled order
        (layoffs, bankruptcies); they stay visible, pale, so what was lost is still seen.
The HTML holds no number of the chart: background.png carries every figure of text.
"""
import json
import random
import sys
from pathlib import Path

proj, mode = Path(sys.argv[1]), sys.argv[2]
duration = float(sys.argv[3]) if len(sys.argv) > 3 else 6.0
rate = float(sys.argv[4]) if len(sys.argv) > 4 else 30.0
data = json.loads((proj / "figures.json").read_text(encoding="utf-8"))
figs = data["figures"]
pal = data["palette"]
start = 0.5 if mode == "appear" else 1.0
order = list(range(len(figs)))
if mode == "vanish":
    random.Random(61).shuffle(order)               # fixed seed: same video every render
when = {i: start + k / rate for k, i in enumerate(order)}

divs = []
for i, f in enumerate(figs):
    s = f["s"]
    if f["people"]:
        hr = s * 0.17
        inner = (f'<i style="left:{s/2-hr:.2f}px;top:{s*0.1:.2f}px;width:{2*hr:.2f}px;height:{2*hr:.2f}px;border-radius:50%"></i>'
                 f'<i style="left:{s*0.24:.2f}px;top:{s*0.48:.2f}px;width:{s*0.52:.2f}px;height:{s*0.44:.2f}px;border-radius:{s*0.18:.2f}px"></i>')
    else:
        inner = (f'<i style="left:{s*0.12:.2f}px;top:{s*0.12:.2f}px;width:{s*0.76:.2f}px;height:{s*0.76:.2f}px;'
                 f'border-radius:{s*0.14:.2f}px"></i>')
    divs.append(f'<div class="fig" id="f{i}" style="left:{f["x"]}px;top:{f["y"]}px;width:{s}px;height:{s}px;'
                f'--c:{f["fill"]}">{inner}</div>')

if mode == "appear":
    tweens = "\n".join(
        f'tl.fromTo("#f{i}", {{opacity: 0, scale: 0.4}}, {{opacity: 1, scale: 1, duration: 0.25, ease: "back.out(2)"}}, {when[i]:.4f});'
        for i in range(len(figs)))
else:
    tweens = "\n".join(
        f'tl.to("#f{i}", {{opacity: 0.18, scale: 0.86, duration: 0.3, ease: "power2.out"}}, {when[i]:.4f});'
        for i in range(len(figs)))

html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: {pal["background"]}; }}
      #root {{ position: relative; width: 1920px; height: 1080px; }}
      #bg {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; }}
      .fig {{ position: absolute; transform-origin: 50% 60%; }}
      .fig i {{ position: absolute; display: block; background: var(--c); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{duration}" data-width="1920" data-height="1080">
      <img id="bg" class="clip" src="background.png" data-start="0" data-duration="{duration}" data-track-index="0" />
      {"".join(divs)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
{tweens}
      tl.to({{}}, {{duration: 0.01}}, {duration - 0.01});
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
(proj / "index.html").write_text(html, encoding="utf-8")
last = max(when.values())
print(f"{mode}: {len(figs)} figures, {rate:g}/s, from {start} s to {last:.2f} s, video {duration} s")
