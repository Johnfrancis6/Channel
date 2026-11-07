"""Turn corpus/metrics.csv into style thresholds (S02).

    python3 whosedime/research/tools/make_rules.py

Writes style_thresholds.json and the rule table of storytelling_rules.md
(between the <!-- rules:start --> and <!-- rules:end --> markers), from the
one RULES list below, so the two files cannot drift. Prints how many rules
each hit, flop and Zehon script trips.

Threshold methods (hits only, statistics.quantiles, method "inclusive"):
- "q1" / "q3": hits' first / third quartile. Used when the hit-flop
  direction holds inside all 4 channels that have both (stronger evidence,
  tighter bound).
- "p10" / "p90": hits' 10th / 90th percentile. Default: flags only what
  is rarer than 9 hits in 10.
- a number: set by another source (plan, report or audit), named in "source".
Level: "block" only if the hits' and flops' interquartile ranges do not
overlap; otherwise "warn".
"""
import csv, json, pathlib, statistics

HERE = pathlib.Path(__file__).resolve().parent
RESEARCH = HERE.parent
METRICS = RESEARCH / "corpus" / "metrics.csv"
JSON_OUT = RESEARCH / "style_thresholds.json"
MD = RESEARCH / "storytelling_rules.md"

# id, metric, min method, max method, rounding, plain rule, source, change from Zehon
RULES = [
    ("S1", "words_before_first_person", None, "q3", 0,
     "Name a real person early: the person who made the decision appears in the cold open.",
     "niche (4/4 channels: hits name a person earlier); Crayon report (hits name one in the first two sentences)",
     "Zehon named nobody before word 230 (aluminium) or 807 (glass)."),
    ("S2", "people_mentions_per_150", "p10", None, 1,
     "Keep people on screen: named people come back all along, not only in the cold open.",
     "Zehon audit S3 and C7 (people refused); niche floor (weak: direction holds in 1/4 channels)",
     "'The process, not the biography' is dropped: the decision and its people carry the story."),
    ("S3", "dialogue_per_1000", 1.0, None, 1,
     "Play two or three short scenes with spoken lines in quotation marks.",
     "Crayon report (hits play mini-scenes; recommendation: 2-3 per video, about 1 line per 1,000 words); "
     "Zehon audit (glass: 1 quotation). Niche transcripts give only a lower bound (captions rarely mark quotes)",
     "Zehon had one quotation in the glass script."),
    ("S4", "sentence_sd", "p10", None, 1,
     "Vary sentence length: short punches next to longer sentences that breathe.",
     "Zehon audit C7 (asked >= 5 words); re-measured on niche hits",
     "Zehon bounded sentences on both sides (SD 4.8 and 4.1 words)."),
    ("S5", "sentence_mean", None, "p90", 1,
     "Keep the average sentence short enough for the ear.",
     "niche (3/4 channels: hits shorter)",
     "No change in practice: Zehon averaged 10.5 words."),
    ("S6", "share_over_25", None, "p90", 2,
     "Long sentences (over 25 words) are allowed, but rare.",
     "Zehon audit S2 (the 25-word ceiling made the rhythm choppy); niche hits",
     "Zehon forbade any sentence over 25 words; now up to the share hits use."),
    ("S7", "numbers_per_100", None, "q3", 1,
     "Fewer numbers: about one every 40 words at most; tell the rest with people and scenes.",
     "niche (4/4 channels: hits use fewer numbers than flops); Zehon audit C7 (asked <= 1 per 40 words = 2.5)",
     "Zehon aluminium had 3.3 numbers per 100 words (one every 9 s)."),
    ("S8", "numbers_first_60", "p10", "p90", 0,
     "One to four numbers in the first 60 words: a figure lands in the first 30 s, not a wall of them.",
     "PLAN_ACTION section 2 (a sourced figure in the first 30 s); niche hits",
     "Same idea as Zehon's hook figure; now with a ceiling."),
    ("S9", "words_before_first_tension", None, 100, 0,
     "Turn the story early: a 'but', 'until' or 'instead' within the first 100 words.",
     "PLAN_ACTION section 2 (title question before 0:40, about 100 words at 150 wpm); "
     "Crayon report (paradox in the first two sentences); niche hits",
     "Zehon already did this (word 45); kept, without forcing one connector."),
    ("S10", "contrast_per_1000", "p10", "p90", 1,
     "Use 'but' and 'however' for real nuance: some, not none, and not as a tic.",
     "niche hits; critique protocol (nuance: no 'but'); Zehon audit S1 (the 'Sauf que' tic)",
     "Zehon forced 'Sauf que' at the end of each block (10 contrast words per 1,000)."),
    ("S11", "you_per_1000", "q1", None, 1,
     "Talk to the viewer: 'you', 'your' (what you pay, what you'd do).",
     "niche (4/4 channels: hits say 'you' more)",
     "Zehon already used 'tu' often; keep it, in English."),
    ("S12", "top_connector_per_1000", None, "p90", 1,
     "Do not lean on one sentence opener ('And', 'But', 'So') more than hits do.",
     "Zehon audit C7 (asked <= 3 'Sauf que'); re-measured: English hits repeat openers more "
     "(median 5.9 per 1,000, 4/4 channels), so only the excess is flagged",
     "Zehon's '<= 3' does not carry over to English: hits start ~13 sentences with 'And' or 'But'."),
    ("S13", "jargon_per_1000", None, "p90", 1,
     "Keep finance jargon rare.",
     "niche (3/4 channels: hits use less jargon)",
     "New: Zehon had no finance vocabulary."),
    ("S14", "jargon_explained_share", 1.0, None, 2,
     "Explain every finance term in plain words the first time it comes ('which means...', "
     "'think of it as...').",
     "Whose Dime goal (ROADMAP S02: money explained simply) and Zehon audit 'adapt' list (EBITDA, 10-K); "
     "NOT the niche: hits rarely explain with these markers (median 0.0)",
     "New for Whose Dime."),
]

LABELS = {"q1": "hits Q1", "q3": "hits Q3", "p10": "hits P10", "p90": "hits P90"}


def load():
    rows = list(csv.DictReader(METRICS.open()))
    def vals(label, k):
        return [float(r[k]) for r in rows if r["label"] == label and r[k] not in ("", "None")]
    return rows, vals


def threshold(method, hits, nd):
    if method is None:
        return None
    if isinstance(method, (int, float)):
        return method
    q4 = statistics.quantiles(hits, n=4, method="inclusive")
    q10 = statistics.quantiles(hits, n=10, method="inclusive")
    x = {"q1": q4[0], "q3": q4[2], "p10": q10[0], "p90": q10[8]}[method]
    return int(round(x)) if nd == 0 else round(x, nd)


def build():
    rows, vals = load()
    out = []
    for rid, metric, lo_m, hi_m, nd, rule, source, change in RULES:
        h, f = vals("hit", metric), vals("flop", metric)
        hq = statistics.quantiles(h, n=4, method="inclusive")
        fq = statistics.quantiles(f, n=4, method="inclusive")
        overlap = not (hq[2] < fq[0] or fq[2] < hq[0])
        out.append(dict(
            id=rid, metric=metric, rule=rule, source=source, change=change,
            min=threshold(lo_m, h, nd), max=threshold(hi_m, h, nd),
            method=" / ".join(LABELS.get(m, "set by source") for m in (lo_m, hi_m) if m is not None),
            n_hit=len(h), n_flop=len(f),
            hit_median=round(statistics.median(h), 2), flop_median=round(statistics.median(f), 2),
            hit_iqr=[round(hq[0], 2), round(hq[2], 2)], flop_iqr=[round(fq[0], 2), round(fq[2], 2)],
            zehon=vals("zehon", metric),
            level="warn" if overlap else "block"))
    return rows, out


def trips(row, rules):
    bad = []
    for r in rules:
        v = row.get(r["metric"])
        if v in ("", "None", None):
            continue
        v = float(v)
        if (r["min"] is not None and v < r["min"]) or (r["max"] is not None and v > r["max"]):
            bad.append(r["id"])
    return bad


def fmt(x):
    return "—" if x is None else (f"{x:g}" if isinstance(x, (int, float)) else str(x))


def md_table(rules):
    lines = ["| Id | Rule | Metric | Threshold | Hits median [IQR] | Flops median [IQR] | n hits / flops | Level |",
             "|---|---|---|---|---|---|---|---|"]
    for r in rules:
        th = " and ".join(p for p in (
            f"≥ {fmt(r['min'])}" if r["min"] is not None else "",
            f"≤ {fmt(r['max'])}" if r["max"] is not None else "") if p)
        lines.append(f"| {r['id']} | {r['rule']} | `{r['metric']}` | **{th}** ({r['method']}) | "
                     f"{fmt(r['hit_median'])} [{fmt(r['hit_iqr'][0])}–{fmt(r['hit_iqr'][1])}] | "
                     f"{fmt(r['flop_median'])} [{fmt(r['flop_iqr'][0])}–{fmt(r['flop_iqr'][1])}] | "
                     f"{r['n_hit']} / {r['n_flop']} | `{r['level']}` |")
    lines += ["", "| Id | Source | What changes from Zehon | Zehon (glass, aluminium) |", "|---|---|---|---|"]
    for r in rules:
        z = ", ".join(fmt(x) for x in r["zehon"]) or "not measured (French)"
        lines.append(f"| {r['id']} | {r['source']} | {r['change']} | {z} |")
    return "\n".join(lines)


def main():
    rows, rules = build()
    JSON_OUT.write_text(json.dumps(dict(
        version="S02 2026-11-07",
        measure="whosedime/research/tools/measure.py",
        rules=[dict(id=r["id"], metric=r["metric"], min=r["min"], max=r["max"], level=r["level"])
               for r in rules]), indent=2) + "\n")
    if MD.exists():
        s = MD.read_text()
        a, b = s.index("<!-- rules:start -->"), s.index("<!-- rules:end -->")
        MD.write_text(s[:a] + "<!-- rules:start -->\n" + md_table(rules) + "\n" + s[b:])
    summary = {}
    for lab in ("hit", "flop", "zehon"):
        t = [len(trips(r, rules)) for r in rows if r["label"] == lab]
        summary[lab] = (statistics.median(t), max(t), len(t))
        print(f"{lab:5}: rules tripped per text: median {statistics.median(t)}, max {max(t)} (n={len(t)})")
    for r in rows:
        if r["label"] == "zehon":
            print(f"  {r['video_id']}: {trips(r, rules)}")
    return rules, summary


if __name__ == "__main__":
    main()
