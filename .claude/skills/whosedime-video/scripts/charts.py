#!/usr/bin/env python3
"""Whose Dime charts (build session S07): one 1920x1080 PNG per `chart` scene.

    python3 charts.py FOLDER [--scenes 1-20] [--out DIR]

FOLDER is a video folder: `03_scenes.md` and `02b_factcheck.md`. For every
`chart` scene it writes `charts/scene_NNN.png` (or DIR/scene_NNN.png).

The `chart` cell of `03_scenes.md` says what to draw (step4_scenes.md):

    F07 · compare · invested $3.5 billion; valuation $62.5 billion

**A number is never typed by hand** (decision D4, audit C2). Before anything
is drawn, every number of the cell must be held by one of the facts it cites,
and every fact cited must be `verified` in the registry: a fact still
[TO VERIFY] (or withdrawn, or unknown) refuses the chart, and so does a number
that is not in its facts. The drawing adds no number of its own: no axis, no
tick, no "rest" of a percentage, no "one figure = 1,000". Bars and grids are
proportional, the labels are the cell's own words.

The scene table and the registry are read with whosedime/common/checker.py
(`scene_table`, `Registry`, `fact_numbers`): one parser, the checker's. The
colours come from whosedime/common/palette.json, every size from
../settings.json. Pillow and the standard library only.

Kinds (settings.json of the checker, `scenes.chart_kinds`):
number one big figure · compare two to four values · split a part of a whole ·
timeline dated steps · icons a count as a grid of figures · scale a range
(1 to 5) · shape a rise and a fall · map money moving from one place to another.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SETTINGS = json.loads((SKILL / "settings.json").read_text(encoding="utf-8"))
FONTS = SKILL / "assets" / "fonts"
BOLD = FONTS / "Nunito-ExtraBold.ttf"
MONO = FONTS / "IBMPlexMono-Medium.ttf"


def find_repo(start=HERE):
    """The repo root: the first parent holding whosedime/common/checker.py (also from the .claude/skills mirror)."""
    for p in [start, *start.parents]:
        if (p / "whosedime" / "common" / "checker.py").is_file():
            return p
    raise RuntimeError("whosedime/common/checker.py not found above " + str(start))


REPO = find_repo()
sys.path.insert(0, str(REPO / "whosedime" / "common"))
import checker  # noqa: E402  (the repo's checker: one scene parser, one registry parser)

PALETTE_PATH = REPO / "whosedime" / "common" / "palette.json"


def load_palette(path=PALETTE_PATH):
    """{role or colour name: (r, g, b)} from palette.json."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rgb = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for k, v in data["colors"].items()}
    rgb.update({role: rgb[name] for role, name in data["roles"].items()})
    return rgb


PAL = load_palette()


class ChartError(Exception):
    """A chart that may not be drawn: the message names the scene and the reason."""


# ------------------------------------------------------------------ reading the cell
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
DATE_RE = re.compile(rf"\b(?:(?:early|late|mid)\s+)?(?:(?:{MONTHS})\s+(?:\d{{1,2}},\s*)?)?(?:1[89]|20)\d{{2}}\b")
QUALIFIERS = r"about|around|nearly|almost|roughly|more than|more like|over|under|less than|below|only"
SCALE_WORDS = {"thousand": 10 ** 3, "million": 10 ** 6, "billion": 10 ** 9, "trillion": 10 ** 12}
VALUE_RE = re.compile(
    rf"(?:\b(?P<q>{QUALIFIERS})\s+)?(?P<v>(?P<cur>[$€£])\d[\d,]*(?:\.\d+)?(?:\s(?:thousand|million|billion|trillion)\b)?"
    rf"|\d[\d,]*(?:\.\d+)?(?:\s?%|\s(?:percent|thousand|million|billion|trillion)\b)?)", re.I)


def word_re(words):
    """One regex for a word list of settings.json: whole words, '*' at the end = any ending ('bankrupt*')."""
    alts = [re.escape(w[:-1]) + r"\w*" if w.endswith("*") else re.escape(w) for w in words]
    return re.compile(r"\b(?:" + "|".join(alts) + r")\b", re.I)


# The colour of a figure says what it means (Franco, 08/11): gain green only for the company's money coming
# in, loss coral only for money lost, everything else navy ink. The words are in settings.json (charts).
LOSS_RE = word_re(SETTINGS["charts"]["loss_words"])
GAIN_RE = word_re(SETTINGS["charts"]["gain_words"])
PEOPLE_RE = re.compile(r"\b(?:owners?|drivers?|people|workers?|riders?|passengers?|users?|employees?)\b", re.I)
FALL_RE = re.compile(r"\b(?:crash\w*|fell|fall\w*|drop\w*|collaps\w*|sank|plung\w*)\b", re.I)


@dataclass
class Value:
    text: str           # as written in the cell: "$3.5 billion", "41%"
    qualifier: str      # "about", "more than"... or ""
    start: int          # span in the item, qualifier included
    end: int
    unit: str           # "$", "%" or "n"
    amount: Decimal
    is_date: bool

    @property
    def shown(self):
        """The value as drawn: the cell's own digits, 'percent' as '%'."""
        return re.sub(r"\s?(?:%|percent)$", "%", self.text, flags=re.I)


def values(text):
    """Every number of a text, in order, with its unit and whether it is part of a date."""
    dates = [m.span() for m in DATE_RE.finditer(text)]
    out = []
    for m in VALUE_RE.finditer(text):
        v = m.group("v")
        digits = re.search(r"\d[\d,]*(?:\.\d+)?", v).group(0).replace(",", "")
        try:
            amount = Decimal(digits)
        except InvalidOperation:
            continue
        scale = re.search(r"(thousand|million|billion|trillion)$", v, re.I)
        if scale:
            amount *= SCALE_WORDS[scale.group(1).lower()]
        unit = "$" if m.group("cur") else "%" if re.search(r"%|percent", v, re.I) else "n"
        is_date = any(a <= m.start("v") < b for a, b in dates) and unit == "n"
        out.append(Value(v, (m.group("q") or "").lower(), m.start(), m.end(), unit, amount, is_date))
    return out


def headline(vals):
    """The value a chart is about: money, a percentage, a scaled or large count; never a date."""
    real = [v for v in vals if not v.is_date]
    for v in real:
        if v.unit in "$%" or v.amount >= 10:
            return v
    return real[0] if real else None


def tidy(text):
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,;:)])", r"\1", text)
    return text.strip(" ,;:-—")


def cap(text):
    """First letter up, unless the word has a capital inside it (uberX, iPhone)."""
    if not text:
        return text
    first = text.split()[0]
    if re.search(r"[a-z][A-Z]", first):
        return text
    return text[0].upper() + text[1:]


@dataclass
class Item:
    text: str
    before: str
    value: Value | None
    after: str
    values: list

    @property
    def label(self):
        """The words around the value, as one label (bars): 'a $1.8 billion loss in 2022' -> 'loss in 2022'."""
        before = re.sub(r"^(?:a|an|the)$", "", self.before.strip(), flags=re.I)
        return cap(re.sub(r"^(?:of|for)\s+", "", tidy(f"{before} {self.after}"), flags=re.I))

    @property
    def tone(self):
        """D13 words, on an amount of money only (D14): a count of people or a percentage stays ink."""
        if self.value is None or self.value.unit != "$":
            return "ink"
        if LOSS_RE.search(self.text):
            return "loss"
        if GAIN_RE.search(self.text):
            return "gain"
        return "ink"


def make_item(text):
    text = tidy(text)
    vals = values(text)
    v = headline(vals)
    if v is None:
        return Item(text, text, None, "", vals)
    return Item(text, tidy(text[:v.start]), v, tidy(text[v.end:]), vals)


@dataclass
class Spec:
    n: int
    ids: list
    kind: str
    what: str
    title: str
    items: list
    source: str


def parse_cell(n, cell, kinds=None):
    """(ids, kind, what) of a `chart` cell 'F07 · compare · ...'."""
    kinds = kinds or checker.SETTINGS["scenes"]["chart_kinds"]
    parts = [p.strip() for p in re.split(r"\s*·\s*", cell.strip(), maxsplit=2)]
    if len(parts) < 3:
        raise ChartError(f"scene {n}: the chart cell is not 'Fnn · <kind> · <what it shows>': {cell[:80]}")
    ids = re.findall(r"\bF\d{2,}\b", parts[0])
    kind = parts[1].lower()
    if kind not in kinds:
        raise ChartError(f"scene {n}: chart kind '{parts[1]}' is not {', '.join(kinds)}")
    return ids, kind, parts[2]


def check_sources(n, ids, what, registry):
    """Decision D4: every fact cited verified, every number of the cell held by one of them."""
    if registry.errors:
        line, msg = registry.errors[0]
        raise ChartError(f"scene {n}: the registry {registry.path.name} is malformed (line {line}: {msg})")
    if not ids:
        raise ChartError(f"scene {n}: the chart cites no fact id (e.g. 'F07 · number · ...')")
    for i in ids:
        status = registry.status(i)
        if status != "verified":
            why = "not an id of the registry" if status is None else (
                "still [TO VERIFY]" if status == "to_verify" else status.replace("_", " "))
            raise ChartError(f"scene {n}: {i} is {why}: a chart draws verified facts only (D4)")
    for key in checker.fact_numbers(what):
        if not registry.numbers.get(key, set()) & set(ids):
            raise ChartError(f"scene {n}: '{key}' is not in the fact(s) it cites ({', '.join(ids)}): "
                             f"a chart never draws a number typed by hand")


def short_source(fid, registry, seen=()):
    """The source of a fact without its URL: 'Fortune, 2016-06-01'; follows 'same as F05'."""
    src = registry.facts[fid]["source"]
    m = re.match(r"^\s*same(?:\s+\w+)?\s+as\s+(F\d{2,})", src, re.I)
    if m and m.group(1) in registry.facts and m.group(1) not in seen:
        return short_source(m.group(1), registry, (*seen, fid))
    src = re.split(r"https?://|\(the original|; read in full", src)[0]
    return tidy(re.sub(r"\((?:as|same as)\s+F\d{2,}\)", "", src))


def build_spec(n, cell, registry):
    ids, kind, what = parse_cell(n, cell)
    check_sources(n, ids, what, registry)
    title = ""
    body = what
    head, sep, rest = what.partition(": ")
    if kind != "timeline" and sep and ";" not in head and headline(values(head)) is None:
        title, body = cap(tidy(head)), rest
    if ";" in body:
        raw_items = body.split(";")
    elif kind == "compare" and ", " in body:
        raw_items = re.split(r",\s+(?!\d{4}\b)", body)
    else:
        raw_items = [body]
    items = [make_item(t) for t in raw_items if tidy(t)]
    sources = []
    for i in ids:
        s = short_source(i, registry)
        if s not in sources:
            sources.append(s)
    return Spec(n, ids, kind, what, title, items, ("Sources: " if len(sources) > 1 else "Source: ") + " · ".join(sources))


# ------------------------------------------------------------------ drawing helpers
def font(size, mono=False):
    return ImageFont.truetype(str(MONO if mono else BOLD), int(size))


def width(draw, text, f):
    return draw.textlength(text, font=f)


def wrap(draw, text, f, max_w):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if line and width(draw, trial, f) > max_w:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


def balanced(draw, text, f, max_w):
    """wrap() with the same number of lines, but as even as they can be: 'Medallion owners / bankrupt by 2019',
    not 'Medallion owners bankrupt by / 2019' (no lone word on the last line)."""
    lines = wrap(draw, text, f, max_w)
    lo, hi = max(width(draw, w, f) for w in text.split()), max_w
    while len(lines) > 1 and hi - lo > 1:
        mid = (lo + hi) / 2
        if len(wrap(draw, text, f, mid)) == len(lines):
            hi = mid
        else:
            lo = mid
    return wrap(draw, text, f, hi) if len(lines) > 1 else lines


def fit(draw, text, size, max_w, min_size=24, mono=False):
    """The largest font (down to min_size) that fits text on one line in max_w."""
    while size > min_size and width(draw, text, font(size, mono)) > max_w:
        size -= 4
    return font(size, mono)


def mix(c1, c2, a):
    """c1 blended toward c2 by a (0 = c1)."""
    return tuple(int(round(x + (y - x) * a)) for x, y in zip(c1, c2))


class Canvas:
    def __init__(self):
        cfg = SETTINGS["video"]
        self.w, self.h = cfg["width"], cfg["height"]
        self.c = SETTINGS["charts"]
        self.m = self.c["margin"]
        self.img = Image.new("RGB", (self.w, self.h), PAL["background"])
        self.d = ImageDraw.Draw(self.img)

    def lines(self, lines, f, cx, y, fill, spacing=1.18, align="center", x=None):
        """Draw lines centred on cx (or left at x); returns the y below them."""
        step = f.size * spacing
        for line in lines:
            if align == "center":
                self.d.text((cx, y), line, font=f, fill=fill, anchor="ma")
            else:
                self.d.text((x, y), line, font=f, fill=fill, anchor="la")
            y += step
        return y

    def block_height(self, parts):
        return sum(len(lines) * f.size * 1.18 + gap for lines, f, _, gap in parts)

    def stack(self, parts, cx, top, bottom):
        """Vertically centre [(lines, font, fill, gap_after)] between top and bottom."""
        y = top + max(0, (bottom - top - self.block_height(parts)) / 2)
        for lines, f, fill, gap in parts:
            y = self.lines(lines, f, cx, y, fill) + gap
        return y

    def frame(self, spec):
        """Title on top, source at the foot. Returns (top, bottom) of the free area."""
        top = self.m * 0.75
        if spec.title:
            f = fit(self.d, spec.title.upper(), self.c["title_size"], self.w - 2 * self.m)
            self.d.text((self.w / 2, top), spec.title.upper(), font=f, fill=PAL["ink"], anchor="ma")
            ry = top + f.size * 1.35
            self.d.rounded_rectangle((self.w / 2 - 60, ry, self.w / 2 + 60, ry + 8), 4, fill=PAL["highlight"])
            top = ry + 50
        else:
            top = self.m
        fs = font(self.c["source_size"], mono=True)
        lines = wrap(self.d, spec.source, fs, self.w - 2 * self.m)
        if len(lines) > 2:
            lines = lines[:2]
            while width(self.d, lines[1] + " …", fs) > self.w - 2 * self.m:
                lines[1] = lines[1].rsplit(" ", 1)[0]
            lines[1] += " …"
        y = self.h - self.m * 0.5 - fs.size * 1.25 * (len(lines) - 1)
        for line in lines:
            self.d.text((self.m, y), line, font=fs, fill=mix(PAL["ink"], PAL["background"], 0.45), anchor="ls")
            y += fs.size * 1.25
        return top, self.h - self.m * 0.5 - fs.size * (1.25 * len(lines) + 1)

    def value_parts(self, item, size, max_w, fill=None):
        """[(lines, font, fill, gap)] for 'before / qualifier / VALUE / after', top to bottom."""
        c = self.c
        parts = []
        lab, small = font(c["label_size"]), font(c["small_size"])
        if item.before:
            parts.append((wrap(self.d, cap(item.before), lab, max_w), lab, PAL["ink"], 10))
        if item.value is not None:
            if item.value.qualifier:
                parts.append(([item.value.qualifier.upper()], small, mix(PAL["ink"], PAL["background"], 0.3), 0))
            fv = fit(self.d, item.value.shown, size, max_w, 40)
            parts.append(([item.value.shown], fv, fill or PAL[item.tone], 12))
        if item.after:
            text = item.after if item.before else cap(item.after)
            parts.append((wrap(self.d, text, lab, max_w), lab, PAL["ink"], 0))
        return parts

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.img.save(path, optimize=True)
        return path


def need(cond, spec, why):
    if not cond:
        raise ChartError(f"scene {spec.n}: {spec.kind} chart: {why}: {spec.what[:80]}")


# ------------------------------------------------------------------ the eight kinds
def draw_number(cv, spec, top, bottom):
    need(len(spec.items) == 1 and spec.items[0].value is not None, spec, "one item with one figure expected")
    item = spec.items[0]
    cv.stack(cv.value_parts(item, cv.c["value_size"] * 1.4, cv.w - 2 * cv.m - 200, fill=PAL["ink"]
                            if item.tone == "ink" else None), cv.w / 2, top, bottom)
    v = item.value
    # a mustard underline under the figure: the eye lands on it
    return v


def comparable(items, ratio_max):
    vals = [i.value for i in items]
    if any(v is None for v in vals) or len({v.unit for v in vals}) != 1 or min(v.amount for v in vals) <= 0:
        return False
    return max(v.amount for v in vals) / min(v.amount for v in vals) <= ratio_max


def draw_compare(cv, spec, top, bottom):
    items = spec.items
    need(2 <= len(items) <= 4 and all(i.value is not None for i in items), spec, "two to four items, each with a figure")
    n = len(items)
    col = (cv.w - 2 * cv.m) / n
    lab = font(cv.c["label_size"] if n <= 3 else cv.c["label_size"] - 8)
    if comparable(items, cv.c["bar_ratio_max"]):
        base = bottom - 170
        bar_top = top + 150
        biggest = max(i.value.amount for i in items)
        bw = min(260, col * 0.5)
        toned = any(i.tone != "ink" for i in items)   # gain or loss somewhere: no mustard (it would read as a third meaning)
        for k, it in enumerate(items):
            cx = cv.m + col * (k + 0.5)
            h = float(it.value.amount / biggest) * (base - bar_top)
            color = PAL[it.tone] if toned else (PAL["highlight"] if k == n - 1 else PAL["ink"])
            cv.d.rounded_rectangle((cx - bw / 2, base - max(h, 12), cx + bw / 2, base), 14, fill=color)
            cv.d.rectangle((cx - bw / 2, base - min(max(h, 12), 14), cx + bw / 2, base), fill=color)
            fv = fit(cv.d, it.value.shown, 96, col - 30, 40)
            y = base - max(h, 12) - 18
            cv.d.text((cx, y), it.value.shown, font=fv, fill=PAL["ink"], anchor="md")
            if it.value.qualifier:
                cv.d.text((cx, y - fv.size - 4), it.value.qualifier.upper(), font=font(cv.c["small_size"]),
                          fill=mix(PAL["ink"], PAL["background"], 0.3), anchor="md")
            cv.lines(wrap(cv.d, it.label or cap(it.text), lab, col - 40), lab, cx, base + 24, PAL["ink"])
        cv.d.line((cv.m, base, cv.w - cv.m, base), fill=mix(PAL["ink"], PAL["background"], 0.6), width=4)
    else:
        size = 120 if n <= 2 else 100 if n == 3 else 84
        for k, it in enumerate(items):
            cx = cv.m + col * (k + 0.5)
            if k:
                x = cv.m + col * k
                cv.d.line((x, top + 40, x, bottom - 40), fill=mix(PAL["ink"], PAL["background"], 0.75), width=3)
            parts = cv.value_parts(it, size, col - 60)
            parts = [(lines, lab if f.size == cv.c["label_size"] else f, fill, gap) for lines, f, fill, gap in parts]
            cv.stack(parts, cx, top, bottom)


def draw_split(cv, spec, top, bottom):
    part = next((i for i in spec.items if i.value is not None and i.value.unit == "%"), None)
    need(part is not None, spec, "no percentage to split")
    rest = next((i for i in spec.items if i is not part), None)
    p = float(part.value.amount) / 100
    need(0 < p <= 1, spec, "a percentage between 0 and 100 expected")
    cx, cy, r, th = cv.m + 420, (top + bottom) / 2, min(330, (bottom - top) / 2 - 20), 120
    box = (cx - r, cy - r, cx + r, cy + r)
    cv.d.ellipse(box, fill=mix(PAL["ink"], PAL["background"], 0.8))
    cv.d.pieslice(box, -90, -90 + 360 * p, fill=PAL["highlight"])
    cv.d.ellipse((cx - r + th, cy - r + th, cx + r - th, cy + r - th), fill=PAL["background"])
    fv = fit(cv.d, part.value.shown, 130, 2 * (r - th) - 30, 40)
    cv.d.text((cx, cy), part.value.shown, font=fv, fill=PAL["ink"], anchor="mm")
    x0 = cx + r + 110
    max_w = cv.w - cv.m - x0 - 70
    lab = font(cv.c["label_size"])
    rows = [(PAL["highlight"], cap(part.text))]
    if rest is not None:
        rows.append((mix(PAL["ink"], PAL["background"], 0.8), cap(rest.text)))
    blocks = [(color, wrap(cv.d, text, lab, max_w)) for color, text in rows]
    total = sum(len(lines) * lab.size * 1.18 for _, lines in blocks) + 70 * (len(blocks) - 1)
    y = cy - total / 2
    for color, lines in blocks:
        cv.d.rounded_rectangle((x0, y + 8, x0 + 44, y + 52), 10, fill=color)
        y = cv.lines(lines, lab, None, y, PAL["ink"], align="left", x=x0 + 70) + 70


def draw_timeline(cv, spec, top, bottom):
    steps = []
    for it in spec.items:
        m = DATE_RE.search(it.text)
        need(m is not None, spec, f"no date in step '{it.text[:40]}'")
        event = tidy(it.text[:m.start()] + " " + it.text[m.end():])
        steps.append((m.group(0), cap(event)))
    n = len(steps)
    y = (top + bottom) / 2
    span = cv.w - 2 * cv.m
    col = span / n
    xs = [cv.m + col * (k + 0.5) for k in range(n)]
    cv.d.line((cv.m * 0.6, y, cv.w - cv.m * 0.6, y), fill=PAL["ink"], width=8)
    fd = font(110 if n == 1 else cv.c["label_size"] if n <= 3 else 42 if n <= 5 else 38)
    fe = font(cv.c["label_size"] if n <= 2 else 38 if n <= 4 else 34)
    for k, (x, (date, event)) in enumerate(zip(xs, steps)):
        last = k == n - 1
        cv.d.ellipse((x - 26, y - 26, x + 26, y + 26), fill=PAL["highlight"] if last else PAL["background"],
                     outline=PAL["ink"], width=8)
        dlines = wrap(cv.d, date, fd, col - 24)
        dy = y - 60 - len(dlines) * fd.size * 1.18
        cv.lines(dlines, fd, x, dy, PAL["ink"])
        cv.lines(wrap(cv.d, event, fe, col - 24), fe, x, y + 60, mix(PAL["ink"], PAL["background"], 0.15))


def person(d, x, y, s, fill):
    """A simple figure in a square cell of side s, top-left at (x, y)."""
    hr = s * 0.17
    d.ellipse((x + s / 2 - hr, y + s * 0.1, x + s / 2 + hr, y + s * 0.1 + 2 * hr), fill=fill)
    d.rounded_rectangle((x + s * 0.24, y + s * 0.48, x + s * 0.76, y + s * 0.92), s * 0.18, fill=fill)


def tile(d, x, y, s, fill):
    d.rounded_rectangle((x + s * 0.12, y + s * 0.12, x + s * 0.88, y + s * 0.88), s * 0.14, fill=fill)


@dataclass
class IconBlock:
    """The layout of one item of an `icons` chart, measured before anything is drawn."""
    cell: float          # side of one figure's cell, px (the same for every item of the chart)
    cols: int
    rows: int
    grid: tuple          # (x0, y0, x1, y1) of the figures
    caption: tuple       # (x0, y0, x1, y1) of qualifier + value + caption
    value_y: float       # top of the value's line: the same for every item of the chart (D15)
    n_icons: int
    n_sub: int           # the first n_sub figures in mustard (a part of the count: "30,000 of them")
    people: bool
    parts: list          # [(lines, font, fill, gap after)] of the caption, top to bottom

    @property
    def box(self):
        return (min(self.grid[0], self.caption[0]), self.grid[1], max(self.grid[2], self.caption[2]), self.caption[3])


def best_grid(n, w, h, gap, max_cell):
    """(cell, cols, rows): the largest square cell for n figures in w x h, figures `gap` x cell apart."""
    best = (0.0, 1, n)
    for cols in range(1, n + 1):
        rows = math.ceil(n / cols)
        cell = min(w / (cols + gap * (cols - 1)), h / (rows + gap * (rows - 1)), max_cell)
        if cell > best[0] + 1e-9:
            best = (cell, cols, rows)
    return best


def even_grid(n, cell, w, gap):
    """(cols, rows) for n figures of a given cell in width w: from a square grid wider, the first without a
    ragged last row ('15 days' as 5 x 3, not 4 + 4 + 4 + 3), else the square one."""
    fit_cols = max(1, int((w / cell + gap) / (1 + gap)))
    square = min(fit_cols, math.ceil(math.sqrt(n)))
    for cols in range(square, min(fit_cols, n) + 1):
        if n % cols == 0 and n // cols <= cols:
            return cols, n // cols
    return square, math.ceil(n / square)


def grid_size(cell, cols, rows, gap):
    return cell * (cols + gap * (cols - 1)), cell * (rows + gap * (rows - 1))


def icons_layout(spec, top, bottom, cv=None):
    """[IconBlock] of an `icons` chart between top and bottom, without drawing: one cell size for the whole
    chart (the smaller of the items' best); the values of two items on one line (D15), each grid standing on
    its own value (above its qualifier) like bars on one ground line; the whole centred between top and bottom."""
    need(1 <= len(spec.items) <= 2, spec, "one or two items expected")
    cv = cv or Canvas()
    c = cv.c
    n = len(spec.items)
    region = (cv.w - 2 * cv.m) / n
    lab, small = font(c["label_size"] - (6 if n > 1 else 0)), font(c["small_size"])
    gap, pad, between = c["icons_gap"], 40, 30
    rw = region - 2 * pad
    found, qual = [], []        # qual: height of each item's qualifier ("MORE THAN"), drawn above its value
    for k, it in enumerate(spec.items):
        counts = [v for v in it.values if not v.is_date and v.unit == "n"]
        need(counts, spec, f"no count in '{it.text[:40]}'")
        main = counts[0]
        sub = next((v for v in counts[1:] if v.amount < main.amount), None)
        unit = 1
        while main.amount / unit > c["icons_max"]:
            unit *= 10
        n_icons = max(1, int(round(main.amount / unit)))
        n_sub = int(round(sub.amount / unit)) if sub else 0
        parts = []
        if main.qualifier:
            parts.append(([main.qualifier.upper()], small, mix(PAL["ink"], PAL["background"], 0.3), 0))
        fv = fit(cv.d, main.shown, 96, rw, 40)
        parts.append(([main.shown], fv, PAL["ink"], 0))
        if sub:
            cut = sub.start
            head = it.text[:cut] if it.text[:main.start].strip() else it.text[main.end:cut]
            parts.append((balanced(cv.d, cap(tidy(head)), lab, rw), lab, PAL["ink"], 0))
            parts.append((balanced(cv.d, tidy(it.text[cut:]), lab, rw), lab, mix(PAL["highlight"], PAL["ink"], 0.35), 0))
        else:
            caption = it.text if it.text[:main.start].strip() else it.text[main.end:]
            parts.append((balanced(cv.d, cap(tidy(caption)), lab, rw), lab, PAL["ink"], 0))
        ch = cv.block_height(parts)
        qual.append(cv.block_height(parts[:1]) if main.qualifier else 0)
        gh_max = min(bottom - top - between - ch, (bottom - top) * c["icons_grid_share"])
        cell, cols, rows = best_grid(n_icons, rw, gh_max, gap, c["icons_max_cell"])
        found.append((cv.m + region * k + pad, n_icons, n_sub, bool(PEOPLE_RE.search(it.text)), parts, ch, cell, cols, rows))
    cell = min(f[6] for f in found)        # one figure size for the whole chart: 95 owners and 15 days, same scale
    found = [f if f[6] == cell else (*f[:7], *even_grid(f[1], cell, rw, gap)) for f in found]
    below = max(f[5] - q for q, f in zip(qual, found))
    for q, f in zip(qual, found):          # values on one line (D15): shrink the figures until the whole fits
        rows = f[8] + gap * (f[8] - 1)
        cell = min(cell, (bottom - top - below - between - q) / rows)
    need(cell >= c["icons_min_cell"], spec, f"figures of {cell:.0f} px, under {c['icons_min_cell']} px: lower icons_max")
    above = max(q + between + grid_size(cell, f[7], f[8], gap)[1] for q, f in zip(qual, found))
    value_y = top + max(0, (bottom - top - above - below) / 2) + above
    blocks = []
    for q, (x0, n_icons, n_sub, people, parts, ch, _, cols, rows) in zip(qual, found):
        gw, gh = grid_size(cell, cols, rows, gap)
        gx = x0 + (rw - gw) / 2
        cy = value_y - q
        gy = cy - between - gh
        blocks.append(IconBlock(cell, cols, rows, (gx, gy, gx + gw, gy + gh), (x0, cy, x0 + rw, cy + ch),
                                value_y, n_icons, n_sub, people, parts))
    return blocks


def draw_icons(cv, spec, top, bottom):
    gap = cv.c["icons_gap"]
    for b in icons_layout(spec, top, bottom, cv):
        draw = person if b.people else tile
        step = b.cell * (1 + gap)
        for i in range(b.n_icons):
            r_, c_ = divmod(i, b.cols)
            draw(cv.d, b.grid[0] + c_ * step, b.grid[1] + r_ * step, b.cell, PAL["highlight"] if i < b.n_sub else PAL["ink"])
        y = b.caption[1]
        cx = (b.caption[0] + b.caption[2]) / 2
        for lines, f, fill, g in b.parts:
            y = cv.lines(lines, f, cx, y, fill) + g


def star(d, cx, cy, r, fill):
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def draw_scale(cv, spec, top, bottom):
    first = spec.items[0]
    nums = [v for v in first.values if not v.is_date and v.unit == "n"]
    need(len(nums) >= 2 and nums[0].amount < nums[1].amount and nums[1].amount == int(nums[1].amount),
         spec, "a range 'from A to B' expected")
    lo, hi = nums[0], nums[1]
    count = int(hi.amount - lo.amount) + 1
    need(2 <= count <= 10, spec, "a range of 2 to 10 steps expected")
    lab = font(cv.c["label_size"])
    y = cv.lines(wrap(cv.d, cap(first.text), lab, cv.w - 2 * cv.m - 200), lab, cv.w / 2, top + 20, PAL["ink"])
    r = min(95, (cv.w - 2 * cv.m) / count / 2 - 10)
    cy = y + 60 + r
    xs = [cv.w / 2 + (k - (count - 1) / 2) * (2 * r + 40) for k in range(count)]
    for x in xs:
        star(cv.d, x, cy, r, PAL["highlight"])
    fn = font(cv.c["label_size"])
    cv.d.text((xs[0], cy + r + 20), lo.text, font=fn, fill=PAL["ink"], anchor="ma")
    cv.d.text((xs[-1], cy + r + 20), hi.text, font=fn, fill=PAL["ink"], anchor="ma")
    if len(spec.items) > 1:
        note = cap(spec.items[1].text)
        y2 = cy + r + 20 + fn.size * 1.6
        ax = xs[0]
        cv.d.polygon([(ax, y2), (ax - 22, y2 + 30), (ax + 22, y2 + 30)], fill=PAL["loss"])
        lines = wrap(cv.d, note, lab, cv.w - ax - cv.m)
        cv.lines(lines, lab, None, y2 + 46, PAL["loss"], align="left", x=max(cv.m, ax - 60))


def draw_shape(cv, spec, top, bottom):
    phases = [p for p in re.split(r",\s*then\s+|;\s*|\s+then\s+", spec.what if not spec.title else
                                  "; ".join(i.text for i in spec.items)) if tidy(p)]
    need(phases, spec, "nothing to draw")
    falls = len(phases) > 1 and any(FALL_RE.search(p) for p in phases[1:])
    x0, x1 = cv.m + 40, cv.w - cv.m - 40
    y_low, y_high = bottom - 40, top + 250
    peak_x = x0 + (x1 - x0) * (0.58 if falls else 1.0)
    pts = []
    steps = 160
    for k in range(steps + 1):
        x = x0 + (x1 - x0) * k / steps
        if x <= peak_x:
            u = (x - x0) / max(1, peak_x - x0)
            yv = y_low - (y_low - y_high) * (u ** 2.2)
        else:
            u = (x - peak_x) / max(1, x1 - peak_x)
            yv = y_high + (y_low - 40 - y_high) * (1 - (1 - u) ** 2.5)
        pts.append((x, yv))
    rise = [p for p in pts if p[0] <= peak_x]
    fall = [p for p in pts if p[0] >= peak_x]
    cv.d.polygon(rise + [(peak_x, y_low), (x0, y_low)], fill=mix(PAL["background"], PAL["ink"], 0.08))
    cv.d.line(rise, fill=PAL["ink"], width=14, joint="curve")
    if falls:
        cv.d.polygon(fall + [(x1, y_low), (peak_x, y_low)], fill=mix(PAL["background"], PAL["loss"], 0.12))
        cv.d.line(fall, fill=PAL["loss"], width=14, joint="curve")
    cv.d.ellipse((peak_x - 24, y_high - 24, peak_x + 24, y_high + 24), fill=PAL["highlight"], outline=PAL["ink"], width=6)
    lab = font(cv.c["label_size"])
    first = make_item(phases[0])
    head = first.value
    tx = peak_x - 40 if falls else peak_x - 20
    anchor_x = min(max(tx, cv.m + 420), cv.w - cv.m - 420)
    if head is not None:
        fv = fit(cv.d, head.shown, 110, 760, 40)
        cv.d.text((anchor_x, y_high - 50), head.shown, font=fv, fill=PAL["ink"], anchor="md")
        if head.qualifier:
            cv.d.text((anchor_x, y_high - 60 - fv.size), head.qualifier.upper(), font=font(cv.c["small_size"]),
                      fill=mix(PAL["ink"], PAL["background"], 0.3), anchor="md")
    cv.lines(wrap(cv.d, cap(first.text), font(36), 560), font(36), None, (y_high + y_low) / 2,
             PAL["ink"], align="left", x=x0 + 20)
    if falls:
        fx = peak_x + (x1 - peak_x) * 0.32
        cv.lines(wrap(cv.d, cap(tidy(" ".join(phases[1:]))), font(42), x1 - fx), font(42), None,
                 y_high - 10, PAL["loss"], align="left", x=fx)


def draw_map(cv, spec, top, bottom):
    need(len(spec.items) == 1, spec, "one movement expected")
    it = spec.items[0]
    rest = tidy(it.text[:it.value.start] + " " + it.text[it.value.end:]) if it.value else it.text
    m = re.search(r"\bfrom\s+(?P<a>.+?)\s+to\s+(?P<b>.+?)$", rest)
    need(m is not None and it.value is not None, spec, "'<amount> from <place> to <place>' expected")
    cy = (top + bottom) / 2 - 40
    r = 150
    ax, bx = cv.m + 330, cv.w - cv.m - 330
    lab = font(cv.c["label_size"])
    for x, name, fill in ((ax, m.group("a"), PAL["highlight"]), (bx, m.group("b"), PAL["ink"])):
        cv.d.ellipse((x - r, cy - r, x + r, cy + r), fill=fill)
        cv.d.ellipse((x - r * 0.42, cy - r * 0.42, x + r * 0.42, cy + r * 0.42), fill=PAL["background"])
        cv.lines(wrap(cv.d, cap(name), lab, 600), lab, x, cy + r + 30, PAL["ink"])
    y = cy
    x0, x1 = ax + r + 40, bx - r - 60
    for k in range(int((x1 - x0) // 60)):
        xa = x0 + k * 60
        cv.d.rounded_rectangle((xa, y - 7, xa + 34, y + 7), 7, fill=PAL["gain"])
    cv.d.polygon([(x1, y - 40), (x1 + 60, y), (x1, y + 40)], fill=PAL["gain"])
    fv = fit(cv.d, it.value.shown, 120, x1 - x0, 40)
    cv.d.text(((x0 + x1) / 2, y - 50), it.value.shown, font=fv, fill=PAL["ink"], anchor="md")
    if it.value.qualifier:
        cv.d.text(((x0 + x1) / 2, y - 60 - fv.size), it.value.qualifier.upper(), font=font(cv.c["small_size"]),
                  fill=mix(PAL["ink"], PAL["background"], 0.3), anchor="md")


DRAW = {"number": draw_number, "compare": draw_compare, "split": draw_split, "timeline": draw_timeline,
        "icons": draw_icons, "scale": draw_scale, "shape": draw_shape, "map": draw_map}


def render(spec):
    cv = Canvas()
    top, bottom = cv.frame(spec)
    DRAW[spec.kind](cv, spec, top, bottom)
    return cv


# ------------------------------------------------------------------ a folder
def chart_rows(scenes_path):
    """[(n, chart cell)] of the chart scenes of 03_scenes.md, read with the checker's parser."""
    raw = checker.norm(Path(scenes_path).read_text(encoding="utf-8"))
    rows, error = checker.scene_table(raw)
    if error:
        raise ChartError(f"{Path(scenes_path).name} line {error[0]}: {error[1]}")
    return [(int(r["n"]), r["chart"]) for _, r in rows if r["type"].lower() == "chart" and r["n"].isdigit()]


def draw_folder(folder, out=None, only=None, log=print):
    """Draw every chart of a video folder. Returns (written paths, refusals); a refused chart is not drawn
    and an older PNG of it is removed, so the assembly never shows a stale chart."""
    folder = Path(folder)
    files = checker.SETTINGS["files"]
    registry = checker.Registry(folder / files["facts"])
    out = Path(out) if out else folder / "charts"
    written, refused = [], []
    for n, cell in chart_rows(folder / files["scenes"]):
        if only and not only[0] <= n <= only[1]:
            continue
        path = out / f"scene_{n:03d}.png"
        try:
            spec = build_spec(n, cell, registry)
            render(spec).save(path)
            written.append(path)
        except ChartError as e:
            refused.append(str(e))
            if path.exists():
                path.unlink()
            log(f"✗ {e}")
    log(f"✓ {len(written)} chart(s) in {out}" + (f", {len(refused)} refused" if refused else ""))
    return written, refused


def main(argv=None):
    p = argparse.ArgumentParser(description="Draw the charts of a Whose Dime video folder.")
    p.add_argument("folder")
    p.add_argument("--scenes", help="only these scenes, e.g. 1-20")
    p.add_argument("--out", help="output folder (default FOLDER/charts)")
    a = p.parse_args(argv)
    only = None
    if a.scenes:
        lo, _, hi = a.scenes.partition("-")
        only = (int(lo), int(hi or lo))
    try:
        _, refused = draw_folder(a.folder, a.out, only)
    except ChartError as e:
        print(f"✗ {e}")
        return 1
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
