"""Trial (not in the repo): export an icons chart for HyperFrames.

charts.py checks the cell (D4) and draws everything but the animated figures into a PNG
(title, value, caption, source, the static grid); the figures of the animated grid go to a
JSON list of boxes. The HTML adds no number: it only moves shapes.

    python3 export_icons.py REPO SCENE OUT_DIR
"""
import json
import sys
from pathlib import Path

repo, n, out = Path(sys.argv[1]), int(sys.argv[2]), Path(sys.argv[3])
sys.path.insert(0, str(repo / "whosedime" / "whosedime-video" / "scripts"))
import charts as C  # noqa: E402

uber = repo / "whosedime" / "whosedime-maker" / "evals" / "files" / "01_uber"
reg = C.checker.Registry(uber / "02b_factcheck.md")
cell = dict(C.chart_rows(uber / "03_scenes.md"))[n]
spec = C.build_spec(n, cell, reg)                     # refuses an unverified fact or a typed number
cv = C.Canvas()
top, bottom = cv.frame(spec)
blocks = C.icons_layout(spec, top, bottom, cv)
gap = cv.c["icons_gap"]
figures = []
for k, b in enumerate(blocks):
    step = b.cell * (1 + gap)
    animated = k == 0                                  # trial: the first grid (people) animates
    for i in range(b.n_icons):
        r, c = divmod(i, b.cols)
        x, y = b.grid[0] + c * step, b.grid[1] + r * step
        fill = C.PAL["highlight"] if i < b.n_sub else C.PAL["ink"]
        if animated:
            figures.append({"x": round(x, 2), "y": round(y, 2), "s": round(b.cell, 2),
                            "people": b.people, "fill": "#%02X%02X%02X" % fill})
        else:
            (C.person if b.people else C.tile)(cv.d, x, y, b.cell, fill)
    y = b.caption[1]
    cx = (b.caption[0] + b.caption[2]) / 2
    for lines, f, fill, g in b.parts:
        y = cv.lines(lines, f, cx, y, fill) + g
out.mkdir(parents=True, exist_ok=True)
cv.save(out / "background.png")
pal = {k: "#%02X%02X%02X" % C.PAL[k] for k in ("background", "ink", "highlight")}
(out / "figures.json").write_text(json.dumps({"scene": n, "palette": pal, "figures": figures}), encoding="utf-8")
print(f"scene {n}: {len(figures)} animated figures, cell {blocks[0].cell:.1f} px")
