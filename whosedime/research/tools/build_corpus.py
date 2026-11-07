"""Build the hits-and-flops corpus for the S02 storytelling rules.

Standard library only. Reads YOUTUBE_API_KEY and SUPADATA_API_KEY from the
environment (never printed). API answers and transcripts are cached in
corpus/raw/ (git-ignored: we do not republish other people's scripts).

    python3 whosedime/research/tools/build_corpus.py catalog   # channel medians, candidates
    python3 whosedime/research/tools/build_corpus.py select    # writes corpus/index.csv
    python3 whosedime/research/tools/build_corpus.py fetch     # transcripts (Supadata)

Definitions (stated in research/README.md):
- channel median: median views of the channel's long videos (> 3 min)
  published in the 24 months before FETCH_DATE;
- candidate: 8 to 25 min, published in that window, at least MIN_AGE_DAYS old;
- ratio: views / channel median; hit >= 2.0, flop <= 0.5.
"""
import csv, datetime, hashlib, json, os, pathlib, re, statistics, sys, time
import urllib.error, urllib.parse, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
RESEARCH = HERE.parent
RAW = RESEARCH / "corpus" / "raw"
CACHE = RAW / "api_cache"
UNITS = RAW / "youtube_units.txt"
SUPA_CALLS = RAW / "supadata_calls.txt"
INDEX = RESEARCH / "corpus" / "index.csv"

FETCH_DATE = datetime.date(2026, 11, 7)
WINDOW_DAYS = 730
MIN_AGE_DAYS = 14
MIN_S, MAX_S = 8 * 60, 25 * 60
HANDLES = ["crayon_capital", "builtonyou", "CEOzoned", "junkbondinvest", "MagnatesMedia"]
N_HITS, N_FLOPS = 20, 10
MAX_SUPADATA = 40


def _bump(path, n):
    path.write_text(str((int(path.read_text()) if path.exists() else 0) + n))


def yt(point, **params):
    CACHE.mkdir(parents=True, exist_ok=True)
    key = hashlib.md5((point + json.dumps(params, sort_keys=True)).encode()).hexdigest()
    f = CACHE / f"{point}_{key}.json"
    if f.exists():
        return json.loads(f.read_text())
    p = dict(params, key=os.environ["YOUTUBE_API_KEY"])
    url = f"https://www.googleapis.com/youtube/v3/{point}?{urllib.parse.urlencode(p)}"
    with urllib.request.urlopen(url, timeout=30) as r:
        d = json.load(r)
    f.write_text(json.dumps(d))
    _bump(UNITS, 100 if point == "search" else 1)
    return d


def iso_dur(s):
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    d, h, mi, se = [int(x or 0) for x in m.groups()] if m else (0, 0, 0, 0)
    return d * 86400 + h * 3600 + mi * 60 + se


def catalog():
    """Every channel's videos in the window, with views and durations."""
    start = FETCH_DATE - datetime.timedelta(days=WINDOW_DAYS)
    rows = []
    for h in HANDLES:
        c = yt("channels", part="snippet,contentDetails", forHandle=h)["items"][0]
        pl = c["contentDetails"]["relatedPlaylists"]["uploads"]
        ids, tok = [], None
        while True:
            kw = dict(part="contentDetails", playlistId=pl, maxResults=50)
            if tok:
                kw["pageToken"] = tok
            r = yt("playlistItems", **kw)
            ids += [i["contentDetails"]["videoId"] for i in r.get("items", [])]
            tok = r.get("nextPageToken")
            if not tok:
                break
        for i in range(0, len(ids), 50):
            r = yt("videos", part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50]))
            for v in r["items"]:
                pub = datetime.date.fromisoformat(v["snippet"]["publishedAt"][:10])
                if pub < start or pub > FETCH_DATE:
                    continue
                rows.append(dict(video_id=v["id"], channel=c["snippet"]["title"], handle=h,
                                 title=v["snippet"]["title"], published=pub.isoformat(),
                                 duration_s=iso_dur(v["contentDetails"]["duration"]),
                                 views=int(v["statistics"].get("viewCount", 0))))
    for h in HANDLES:
        longs = [r for r in rows if r["handle"] == h and r["duration_s"] > 180]
        med = statistics.median([r["views"] for r in longs]) if longs else 0
        for r in longs:
            r["channel_median"] = med
            r["ratio"] = round(r["views"] / med, 3) if med else 0
    return [r for r in rows if r["duration_s"] > 180]


def candidates(rows):
    out = []
    for r in rows:
        age = (FETCH_DATE - datetime.date.fromisoformat(r["published"])).days
        if MIN_S <= r["duration_s"] <= MAX_S and age >= MIN_AGE_DAYS:
            r["label"] = "hit" if r["ratio"] >= 2 else "flop" if r["ratio"] <= 0.5 else ""
            if r["label"]:
                out.append(r)
    return out


def pick(cands, label, n):
    """Round-robin over channels so no channel dominates; strongest first."""
    by = {}
    for r in sorted(cands, key=lambda r: r["ratio"], reverse=(label == "hit")):
        if r["label"] == label:
            by.setdefault(r["handle"], []).append(r)
    out = []
    while len(out) < n and any(by.values()):
        for h in HANDLES:
            if by.get(h) and len(out) < n:
                out.append(by[h].pop(0))
    return out


FIELDS = ["video_id", "channel", "title", "published", "duration_s", "views",
          "channel_median", "ratio", "label", "transcript_words"]


def select():
    rows = catalog()
    sel = pick(candidates(rows), "hit", N_HITS) + pick(candidates(rows), "flop", N_FLOPS)
    with INDEX.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in sel:
            t = RAW / f"{r['video_id']}.txt"
            r["transcript_words"] = len(t.read_text().split()) if t.exists() else ""
            w.writerow(r)
    print(f"{len(sel)} rows -> {INDEX}")


def supadata(video_id):
    t = RAW / f"{video_id}.txt"
    if t.exists():
        return t.read_text()
    used = int(SUPA_CALLS.read_text()) if SUPA_CALLS.exists() else 0
    if used >= MAX_SUPADATA:
        raise SystemExit(f"Supadata budget reached ({MAX_SUPADATA} calls)")
    url = ("https://api.supadata.ai/v1/youtube/transcript?"
           + urllib.parse.urlencode({"videoId": video_id, "text": "true", "lang": "en"}))
    req = urllib.request.Request(url, headers={"x-api-key": os.environ["SUPADATA_API_KEY"],
                                               "User-Agent": "whosedime-research"})
    _bump(SUPA_CALLS, 1)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        print(f"{video_id}: HTTP {e.code}")
        return ""
    text = d.get("content") or ""
    if isinstance(text, list):
        text = " ".join(x.get("text", "") for x in text)
    if text:
        t.write_text(text)
    return text


def fetch():
    with INDEX.open() as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        text = supadata(r["video_id"])
        print(f"{r['video_id']} {r['label']:4} {len(text.split()):6} words")
        time.sleep(0.5)
    select()  # refresh transcript_words


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "catalog"
    if cmd == "catalog":
        rows = catalog()
        for h in HANDLES:
            mine = [r for r in rows if r["handle"] == h]
            c = [r for r in candidates(mine)]
            print(f"{h:16} long={len(mine):4} median={mine[0]['channel_median'] if mine else 0:>10}"
                  f" hits={sum(r['label']=='hit' for r in c):3} flops={sum(r['label']=='flop' for r in c):3}")
    elif cmd == "select":
        select()
    elif cmd == "fetch":
        fetch()
