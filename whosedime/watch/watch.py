#!/usr/bin/env python3
"""Weekly competitor watch for Whose Dime (session S09).

One run reads the uploads of the niche's channels (channels.csv), compares
them with the previous run (last_run.json) and writes a one-page report in
docs/whosedime/watch/<run date>.md:

- new long videos (over 3 min) published in the 7 days before the run;
- hits: tracked videos (published in the last 28 days) at 5x their
  channel's median of long-video views or more, measured on the run date;
- title changes on videos seen at the previous run;
- new entrants: at most 2 search.list calls, last 7 days, English, 4-20 min,
  sorted by views; a channel not in the list with a video at 100 K views or
  more is proposed (never added: Franco decides);
- brands covered: titles that name a brand of docs/finance/marques.md, so its
  "gap" column can be reread (proposed only: marques.md is not edited).

Budget: under 300 YouTube Data API units a run. The tool counts every call
(playlistItems, videos, channels: 1 unit; search: 100) and refuses a call
that would cross the budget. Standard library only; the logic of the API
helpers comes from research_notes/Balayage niche C/outils/yt.py (no cache
here: a weekly watch needs fresh numbers).

    python3 whosedime/watch/watch.py                 # weekly run
    python3 whosedime/watch/watch.py --no-search     # skip new entrants (about 50 units)
    python3 whosedime/watch/watch.py --refresh-medians   # recompute medians, no report

Needs YOUTUBE_API_KEY in the environment (never printed).
"""
import argparse
import collections
import csv
import datetime as dt
import json
import os
import pathlib
import re
import statistics
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CHANNELS_CSV = HERE / "channels.csv"
STATE_JSON = HERE / "last_run.json"
REPORT_DIR = ROOT / "docs" / "whosedime" / "watch"
BRANDS_MD = ROOT / "docs" / "finance" / "marques.md"
SCAN_DIR = ROOT / "research_notes" / "Balayage niche C"

API_URL = "https://www.googleapis.com/youtube/v3/"
COST = {"search": 100, "channels": 1, "playlistItems": 1, "videos": 1}
BUDGET = 300
SHORT_MAX_S = 180           # a video of 3 min or less is a Short
WINDOW_DAYS = 7             # "new" = published in the 7 days before the run
TRACK_DAYS = 28             # videos followed for hits and title changes
HIT_RATIO = 5.0
HIT_MIN_VIEWS = 10_000      # below it, a "hit" on a tiny channel is counted, not listed
NEW_ROWS = 12               # new long videos listed (by views); the rest counted
ENTRANT_MIN_VIEWS = 100_000
SEARCH_QUERIES = ("company history documentary",
                  "how does it make money business model")
CHANNEL_FIELDS = ["handle", "title", "channel_id", "uploads_playlist_id",
                  "median_long_views", "median_source", "median_date"]


class BudgetExceeded(RuntimeError):
    pass


# --------------------------------------------------------------- API layer

def http_fetch(endpoint, params):
    """Real call to the YouTube Data API. The key never leaves this function:
    errors name the endpoint and the API's message, never the URL."""
    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        raise SystemExit("YOUTUBE_API_KEY is not set: stop and tell Franco.")
    query = dict(params, key=key)
    url = API_URL + endpoint + "?" + urllib.parse.urlencode(query)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            msg = json.load(e).get("error", {}).get("message", "")
        except Exception:
            msg = ""
        raise RuntimeError(f"{endpoint}: HTTP {e.code} {msg}".strip()) from None


class Api:
    """Counts units per call and refuses any call that would cross the budget.
    `fetch(endpoint, params) -> dict` is injectable (tests use a fake)."""

    def __init__(self, fetch=http_fetch, budget=BUDGET):
        self.fetch = fetch
        self.budget = budget
        self.units = 0
        self.calls = collections.Counter()

    def remaining(self):
        return self.budget - self.units

    def get(self, endpoint, **params):
        cost = COST.get(endpoint, 1)
        if self.units + cost > self.budget:
            raise BudgetExceeded(f"{endpoint} would bring the run to "
                                 f"{self.units + cost} units (budget {self.budget})")
        self.units += cost          # YouTube bills failed calls too
        self.calls[endpoint] += 1
        return self.fetch(endpoint, params)


def parse_duration(s):
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    if not m:
        return 0
    d, h, mi, se = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + se


def fetch_videos(api, ids):
    """id -> facts, 50 ids per videos.list call (1 unit each)."""
    out, ids = {}, list(dict.fromkeys(ids))
    for i in range(0, len(ids), 50):
        r = api.get("videos", part="snippet,statistics,contentDetails",
                    id=",".join(ids[i:i + 50]), maxResults=50)
        for v in r.get("items", []):
            sn, st = v["snippet"], v.get("statistics", {})
            out[v["id"]] = dict(
                id=v["id"], title=sn["title"], published=sn["publishedAt"][:10],
                channel_id=sn["channelId"], channel_title=sn.get("channelTitle", ""),
                lang=sn.get("defaultAudioLanguage") or sn.get("defaultLanguage") or "",
                views=int(st.get("viewCount", 0)),
                dur=parse_duration(v.get("contentDetails", {}).get("duration")))
    return out


def fetch_uploads(api, playlist_id):
    """Latest 50 uploads of a channel: [(video_id, published date)]."""
    r = api.get("playlistItems", part="contentDetails", playlistId=playlist_id,
                maxResults=50)
    out = []
    for it in r.get("items", []):
        cd = it.get("contentDetails", {})
        when = cd.get("videoPublishedAt")
        if cd.get("videoId") and when:      # private videos have no date
            out.append((cd["videoId"], when[:10]))
    return out


# ---------------------------------------------------------------- channels

def load_channels(path=CHANNELS_CSV):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_channels(rows, path=CHANNELS_CSV):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CHANNEL_FIELDS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in CHANNEL_FIELDS})


def channels_from_scan(scan_dir=SCAN_DIR):
    """Seed of channels.csv: the 47 channels of chaines_C.csv (scan of
    2026-11-05), median of long-video views over the full catalogue."""
    rows = []
    with open(scan_dir / "chaines_C.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(dict(handle=r["handle"], title=r["titre"], channel_id="",
                             uploads_playlist_id="",
                             median_long_views=r["mediane_vues_longues"],
                             median_source="full catalogue (chaines_C.csv)",
                             median_date="2026-11-05"))
    return rows


def resolve_ids(api, rows, scan_dir=SCAN_DIR):
    """Fill channel_id and uploads_playlist_id where missing, for 2 units:
    one known video per handle (videos_C.csv) gives the channel id, then one
    channels.list call gives the uploads playlist and the handle to check.
    A handle with no known video costs 1 unit (channels.list forHandle).
    Returns warnings."""
    warnings = []
    todo = [r for r in rows if not r.get("uploads_playlist_id")]
    if not todo:
        return warnings
    sample = {}
    videos_csv = scan_dir / "videos_C.csv"
    if videos_csv.exists():
        with open(videos_csv, newline="", encoding="utf-8") as f:
            for v in csv.DictReader(f):
                sample.setdefault(v["handle"], v["video_id"])
    by_video = {sample[r["handle"]]: r for r in todo if r["handle"] in sample}
    for vid, v in fetch_videos(api, list(by_video)).items():
        by_video[vid]["channel_id"] = v["channel_id"]
    with_id = [r for r in todo if r.get("channel_id")]
    for i in range(0, len(with_id), 50):
        chunk = {r["channel_id"]: r for r in with_id[i:i + 50]}
        res = api.get("channels", part="snippet,contentDetails",
                      id=",".join(chunk), maxResults=50)
        for c in res.get("items", []):
            r = chunk[c["id"]]
            r["uploads_playlist_id"] = c["contentDetails"]["relatedPlaylists"]["uploads"]
            r["title"] = c["snippet"]["title"]
            custom = c["snippet"].get("customUrl", "")
            if custom and custom.lower() != r["handle"].lower():
                warnings.append(f"handle updated: {r['handle']} is now {custom} "
                                f"(same channel, found by a known video)")
                r["handle"] = custom
    for r in todo:
        if r.get("uploads_playlist_id"):
            continue
        res = api.get("channels", part="snippet,contentDetails", forHandle=r["handle"])
        if res.get("items"):
            c = res["items"][0]
            r["channel_id"] = c["id"]
            r["uploads_playlist_id"] = c["contentDetails"]["relatedPlaylists"]["uploads"]
            r["title"] = c["snippet"]["title"]
        else:
            warnings.append(f"{r['handle']}: channel not found")
    return warnings


def refresh_medians(api, rows, today):
    """Median of long-video views over each channel's latest 50 uploads
    (about 2 units a channel: about 95 for 47). Changes the median's basis
    from the full catalogue to recent videos: run it on its own, quarterly."""
    ids = {}
    for r in rows:
        if r.get("uploads_playlist_id"):
            ids[r["handle"]] = [v for v, _ in fetch_uploads(api, r["uploads_playlist_id"])]
    facts = fetch_videos(api, [v for L in ids.values() for v in L])
    for r in rows:
        long_views = [facts[v]["views"] for v in ids.get(r["handle"], [])
                      if v in facts and facts[v]["dur"] > SHORT_MAX_S]
        if long_views:
            r["median_long_views"] = str(int(statistics.median(long_views)))
            r["median_source"] = f"latest 50 uploads ({len(long_views)} long)"
            r["median_date"] = today.isoformat()


# ------------------------------------------------------------------ brands

BRAND_TERMS = {   # brand as named in marques.md -> title terms (else: its own name)
    "American Express": ["american express", "amex"],
    "Visa et Mastercard": ["visa", "mastercard", "interchange", "swipe fee"],
    "Chase (JPMorgan)": ["chase", "jpmorgan", "jp morgan"],
    "Venmo (PayPal)": ["venmo", "paypal"],
    "Cash App (Block)": ["cash app"],
    "Chase Sapphire": ["sapphire"],
    "Berkshire Hathaway": ["berkshire", "buffett"],
    "TurboTax (Intuit)": ["turbotax", "intuit"],
    "Apple App Store": ["app store"],
    "Boeing": ["boeing", "737 max"],
    "Chick-fil-A": ["chick-fil-a", "chick fil a"],
    "In-N-Out": ["in-n-out", "in n out"],
    "Domino's": ["domino"],
    "Spirit Airlines": ["spirit airlines"],
}


def _norm(text):
    return re.sub(r"['’]", "", text.lower())


def load_brands(path=BRANDS_MD):
    """The 40 rows of marques.md: [{rank, brand, gap, regex}]."""
    lines = pathlib.Path(path).read_text(encoding="utf-8").splitlines()
    header = next(l for l in lines if l.startswith("| # | Marque"))
    cols = [c.strip() for c in header.strip("|").split("|")]
    gap_i = next(i for i, c in enumerate(cols) if c.startswith("Vide"))
    brands = []
    for l in lines:
        m = re.match(r"\|\s*(\d+)\s*\|\s*\*\*(.+?)\*\*\s*\|", l)
        if not m:
            continue
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        name = m.group(2)
        terms = BRAND_TERMS.get(name, [name])
        rx = re.compile(r"\b(?:" + "|".join(re.escape(_norm(t)) for t in terms)
                        + r")s?\b")
        brands.append(dict(rank=int(m.group(1)), brand=name, gap=cells[gap_i], regex=rx))
    return brands


def brands_in(title, brands):
    t = _norm(title)
    return [b for b in brands if b["regex"].search(t)]


# ------------------------------------------------------------------- build

def build(run_date, channels, uploads, facts, prev, search=None, brands=(),
          errors=()):
    """Pure part of a run. `uploads`: handle -> [(id, date)]; `facts`:
    id -> video facts; `prev`: last_run.json content or None; `search`:
    {"queries", "results": [video facts]} or None. Returns the result dict."""
    window = (run_date - dt.timedelta(days=WINDOW_DAYS)).isoformat()
    track = (run_date - dt.timedelta(days=TRACK_DAYS)).isoformat()
    medians = {c["handle"]: float(c["median_long_views"] or 0) for c in channels}
    known_ids = {c["channel_id"] for c in channels if c.get("channel_id")}
    prev_videos = (prev or {}).get("videos", {})
    prev_hits = set((prev or {}).get("hits", []))

    tracked, new, hits, shorts = {}, [], [], 0
    for c in channels:
        h = c["handle"]
        for vid, date in uploads.get(h, []):
            v = facts.get(vid)
            if not v or date < track:
                continue
            if v["dur"] <= SHORT_MAX_S:
                shorts += 1
                continue
            med = medians.get(h) or 0
            row = dict(v, handle=h, ratio=(v["views"] / med) if med else None)
            tracked[vid] = row
            if date >= window:
                new.append(row)
            if row["ratio"] is not None and row["ratio"] >= HIT_RATIO:
                hits.append(dict(row, first_seen=vid not in prev_hits))

    renames = []
    for vid, old in prev_videos.items():
        cur = facts.get(vid)
        if cur and cur["title"] != old["title"]:
            renames.append(dict(handle=old.get("handle", ""), id=vid,
                                old=old["title"], new=cur["title"],
                                views=cur["views"]))

    entrants, search_stats = [], None
    if search is not None:
        res = search["results"]
        long_ = [v for v in res if v["dur"] > SHORT_MAX_S and v["published"] >= window
                 and (not v["lang"] or v["lang"].lower().startswith("en"))]
        outside = [v for v in long_ if v["channel_id"] not in known_ids]
        best = {}
        for v in outside:
            if v["views"] >= ENTRANT_MIN_VIEWS:
                if v["channel_id"] not in best or v["views"] > best[v["channel_id"]]["views"]:
                    best[v["channel_id"]] = v
        entrants = sorted(best.values(), key=lambda v: -v["views"])
        search_stats = dict(queries=list(search["queries"]), results=len(res),
                            long=len(long_), outside=len(outside))

    covered = collections.defaultdict(list)
    seen = set()
    for v in sorted(new, key=lambda v: -v["views"]) + entrants:
        if v["id"] in seen:
            continue
        seen.add(v["id"])
        for b in brands_in(v["title"], brands):
            covered[b["brand"]].append(v)
    brand_rows = [dict(rank=b["rank"], brand=b["brand"], gap=b["gap"],
                       videos=covered[b["brand"]]) for b in brands if b["brand"] in covered]

    return dict(run_date=run_date.isoformat(), window_start=window, track_start=track,
                channels=len(channels), first_run=prev is None,
                prev_date=(prev or {}).get("run_date"),
                new=sorted(new, key=lambda v: (v["published"], v["views"]), reverse=True),
                hits=sorted(hits, key=lambda v: -v["views"]), renames=renames,
                shorts_skipped=shorts, entrants=entrants, search=search_stats,
                brands=brand_rows, tracked=tracked, errors=list(errors))


def new_state(result, units):
    return dict(run_date=result["run_date"], units=units,
                hits=[v["id"] for v in result["hits"]],
                videos={vid: dict(handle=v["handle"], title=v["title"], views=v["views"],
                                  published=v["published"], dur=v["dur"])
                        for vid, v in sorted(result["tracked"].items())})


# ------------------------------------------------------------------ report

def _k(n):
    return f"{n / 1e6:.2f} M" if n >= 1e6 else (f"{n / 1e3:.1f} K" if n >= 1e3 else str(n))


def _ratio(r):
    if r is None:
        return "—"
    return f"{r:.2f}×" if r < 1 else f"{r:.1f}×"


def _cell(s):
    return s.replace("|", "\\|")


def _link(v):
    return f"[{_cell(v['title'])}](https://youtu.be/{v['id']})"


def render(result, api):
    r = result
    calls = ", ".join(f"{k} {n}" for k, n in sorted(api.calls.items()))
    out = [f"# Competitor watch — {r['run_date']}", "",
           f"Run of **{r['run_date']}** by `whosedime/watch/watch.py`. "
           f"**Measured** (YouTube Data API, on the run date): every number below; views "
           f"are totals on the run date, so a video's age weighs on them. "
           f"**Inferred**: only the lines marked *Inferred*.", "",
           f"- Channels watched: {r['channels']} (`whosedime/watch/channels.csv`); "
           f"window: published from {r['window_start']} to the run "
           f"(hits: from {r['track_start']}).",
           f"- **Quota: {api.units} units** of {api.budget} (calls: {calls}).",
           f"- Shorts (3 min or less) left out: {r['shorts_skipped']}.", ""]
    if r["errors"]:
        out += ["**Warnings**: " + "; ".join(r["errors"]) + ".", ""]

    big = [v for v in r["hits"] if v["views"] >= HIT_MIN_VIEWS]
    small = [v for v in r["hits"] if v["views"] < HIT_MIN_VIEWS]
    out += [f"## Hits (≥ {HIT_RATIO:g}× the channel's median, ≥ {_k(HIT_MIN_VIEWS)} views)", ""]
    if big:
        per = collections.OrderedDict()
        for v in big:                       # sorted by views: first = best
            per.setdefault(v["handle"], []).append(v)
        out += ["| Channel | Best hit | Published | Views | × median | New | Other hits |",
                "|---|---|---|---|---|---|---|"]
        for h, L in per.items():
            v = L[0]
            others = ", ".join(f"{_k(x['views'])} ({_ratio(x['ratio'])})" for x in L[1:]) or "—"
            out.append(f"| {h} | {_link(v)} | {v['published']} | {_k(v['views'])} | "
                       f"{_ratio(v['ratio'])} | {'yes' if v['first_seen'] else 'no'} | {others} |")
    else:
        out.append(f"None at {_k(HIT_MIN_VIEWS)} views or more among the long videos "
                   f"published since {r['track_start']}.")
    if small:
        chans = collections.Counter(v["handle"] for v in small)
        out += ["", f"Also at ≥ {HIT_RATIO:g}× but under {_k(HIT_MIN_VIEWS)} views (tiny "
                f"medians): {len(small)} videos — " +
                ", ".join(f"{h} {n}" for h, n in chans.most_common()) + "."]
    out.append("")

    out += [f"## New long videos ({len(r['new'])})", ""]
    if r["new"]:
        top = sorted(r["new"], key=lambda v: -v["views"])[:NEW_ROWS]
        out += [f"The {len(top)} most viewed:", "",
                "| Channel | Video | Published | Views | × median |", "|---|---|---|---|---|"]
        out += [f"| {v['handle']} | {_link(v)} | {v['published']} | {_k(v['views'])} | "
                f"{_ratio(v['ratio'])} |" for v in top]
        per = collections.Counter(v["handle"] for v in r["new"])
        quiet = r["channels"] - len(per)
        out += ["", f"All {len(r['new'])} by channel: " +
                ", ".join(f"{h} {n}" for h, n in per.most_common()) +
                f". {quiet} channels published no long video. Full list: `last_run.json`."]
    else:
        out.append("No long video in the window.")
    out.append("")

    out += ["## Title changes", ""]
    if r["first_run"]:
        out.append("First run: no previous titles to compare. The titles seen today "
                   f"({len(r['tracked'])} videos) are kept in `last_run.json` for next week.")
    elif r["renames"]:
        out += [f"Since the run of {r['prev_date']}:", "",
                "| Channel | Old title | New title | Views |", "|---|---|---|---|"]
        out += [f"| {x['handle']} | {_cell(x['old'])} | "
                f"[{_cell(x['new'])}](https://youtu.be/{x['id']}) | {_k(x['views'])} |"
                for x in r["renames"]]
    else:
        out.append(f"None since the run of {r['prev_date']}.")
    out.append("")

    out += ["## New entrants (proposed, not added)", ""]
    s = r["search"]
    if s is None:
        out.append("Search skipped on this run.")
    else:
        qs = ", ".join(f"“{q}”" for q in s["queries"])
        out.append(f"{len(s['queries'])} searches ({qs}), English, 4-20 min, "
                   f"sorted by views: {s['results']} results, {s['long']} long and in the "
                   f"window, {s['outside']} from channels not in the list.")
        out.append("")
        if r["entrants"]:
            out += [f"Channels not in the list with a video at {_k(ENTRANT_MIN_VIEWS)} "
                    "views or more: **Franco decides** whether they join the list.", "",
                    "| Channel | Video | Published | Views |", "|---|---|---|---|"]
            out += [f"| {_cell(v['channel_title'])} | {_link(v)} | {v['published']} | "
                    f"{_k(v['views'])} |" for v in r["entrants"]]
        else:
            out.append(f"No channel outside the list reached {_k(ENTRANT_MIN_VIEWS)} views.")
    out.append("")

    out += ["## Brands covered (from `docs/finance/marques.md`)", ""]
    if r["brands"]:
        out += ["Titles of this week's new videos and entrants that name a brand of the "
                "table. `marques.md` is not edited: reread its gap column with these.", "",
                "| # | Brand | This week | Gap column today |", "|---|---|---|---|"]
        for b in r["brands"]:
            vids = "; ".join(f"[{v.get('handle') or _cell(v['channel_title'])}, "
                             f"{_k(v['views'])}](https://youtu.be/{v['id']}) {v['published']}"
                             for v in b["videos"])
            out.append(f"| {b['rank']} | {b['brand']} | {vids} | {_cell(b['gap'])} |")
    else:
        out.append("No title of the week names a brand of the table.")
    out.append("")
    return "\n".join(out)


# --------------------------------------------------------------------- run

def run(api, run_date, channels_path=CHANNELS_CSV, state_path=STATE_JSON,
        report_dir=REPORT_DIR, brands_path=BRANDS_MD, search=True,
        queries=SEARCH_QUERIES, scan_dir=SCAN_DIR):
    channels_path, state_path = pathlib.Path(channels_path), pathlib.Path(state_path)
    channels = load_channels(channels_path) if channels_path.exists() else channels_from_scan(scan_dir)
    errors = resolve_ids(api, channels, scan_dir)
    save_channels(channels, channels_path)
    prev = json.loads(state_path.read_text()) if state_path.exists() else None

    track = (run_date - dt.timedelta(days=TRACK_DAYS)).isoformat()
    uploads = {}
    for c in channels:
        if not c.get("uploads_playlist_id"):
            continue
        try:
            uploads[c["handle"]] = fetch_uploads(api, c["uploads_playlist_id"])
        except RuntimeError as e:
            errors.append(f"{c['handle']}: {e}")
    ids = [v for L in uploads.values() for v, d in L if d >= track]
    ids += list((prev or {}).get("videos", {}))      # for title changes
    facts = fetch_videos(api, ids)

    found = None
    if search:
        window = run_date - dt.timedelta(days=WINDOW_DAYS)
        queries = list(queries)[:2]                   # at most 2 search calls
        need = len(queries) * COST["search"] + 2      # + 2 videos.list calls
        if api.remaining() < need:
            errors.append(f"search skipped: {api.remaining()} units left, {need} needed")
        else:
            hits = []
            for q in queries:
                res = api.get("search", part="snippet", q=q, type="video",
                              order="viewCount", relevanceLanguage="en",
                              videoDuration="medium", maxResults=50,
                              publishedAfter=window.isoformat() + "T00:00:00Z")
                hits += [it["id"]["videoId"] for it in res.get("items", [])
                         if it.get("id", {}).get("videoId")]
            found = dict(queries=queries,
                         results=list(fetch_videos(api, hits).values()))

    brands = load_brands(brands_path) if pathlib.Path(brands_path).exists() else []
    result = build(run_date, channels, uploads, facts, prev, found, brands, errors)
    report = render(result, api)
    report_dir = pathlib.Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / f"{run_date.isoformat()}.md"
    path.write_text(report, encoding="utf-8")
    state_path.write_text(json.dumps(new_state(result, api.units), indent=1,
                                     ensure_ascii=False) + "\n", encoding="utf-8")
    return result, path


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--date", help="run date YYYY-MM-DD (default: today, UTC)")
    p.add_argument("--no-search", action="store_true", help="skip new entrants")
    p.add_argument("--refresh-medians", action="store_true",
                   help="recompute medians from the latest 50 uploads; no report")
    a = p.parse_args(argv)
    run_date = (dt.date.fromisoformat(a.date) if a.date
                else dt.datetime.now(dt.timezone.utc).date())
    api = Api()
    if a.refresh_medians:
        rows = load_channels() if CHANNELS_CSV.exists() else channels_from_scan()
        resolve_ids(api, rows)
        refresh_medians(api, rows, run_date)
        save_channels(rows)
        print(f"Medians refreshed. Units spent: {api.units}")
        return 0
    result, path = run(api, run_date, search=not a.no_search)
    print(f"Report: {path.relative_to(ROOT)}")
    print(f"Units spent: {api.units} of {api.budget} ({dict(api.calls)})")
    print(f"New long videos: {len(result['new'])}; hits: {len(result['hits'])}; "
          f"title changes: {'first run' if result['first_run'] else len(result['renames'])}; "
          f"entrants proposed: {len(result['entrants'])}; brands: {len(result['brands'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
