"""Hits against flops, metric by metric, from corpus/metrics.csv.

    python3 whosedime/research/tools/compare.py

For each metric: n, median and interquartile range (Q1-Q3, statistics.quantiles,
method "inclusive") of hits and of flops, whether the two IQRs overlap, the
Zehon values. Standard library only.
"""
import csv, pathlib, statistics

CORPUS = pathlib.Path(__file__).resolve().parent.parent / "corpus"
SKIP = {"video_id", "channel", "label", "top_opener", "top_connector"}


def iqr(v):
    q = statistics.quantiles(v, n=4, method="inclusive")
    return q[0], q[2]


def compare():
    rows = list(csv.DictReader((CORPUS / "metrics.csv").open()))
    out = {}
    for k in rows[0]:
        if k in SKIP:
            continue
        g = {lab: [float(r[k]) for r in rows if r["label"] == lab and r[k] not in ("", "None")]
             for lab in ("hit", "flop", "zehon")}
        h, f = g["hit"], g["flop"]
        if len(h) < 2 or len(f) < 2:
            continue
        hq, fq = iqr(h), iqr(f)
        out[k] = dict(n_hit=len(h), n_flop=len(f),
                      hit_median=statistics.median(h), hit_iqr=hq,
                      flop_median=statistics.median(f), flop_iqr=fq,
                      overlap=not (hq[1] < fq[0] or fq[1] < hq[0]),
                      zehon=g["zehon"])
    return out


if __name__ == "__main__":
    for k, d in compare().items():
        print(f"{k:28} hit {d['hit_median']:8.2f} [{d['hit_iqr'][0]:7.2f}-{d['hit_iqr'][1]:7.2f}] n={d['n_hit']:2}"
              f" | flop {d['flop_median']:8.2f} [{d['flop_iqr'][0]:7.2f}-{d['flop_iqr'][1]:7.2f}] n={d['n_flop']:2}"
              f" | {'OVERLAP' if d['overlap'] else 'separate'} | zehon {d['zehon']}")
