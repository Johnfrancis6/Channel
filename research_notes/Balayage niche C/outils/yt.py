import json, os, urllib.parse, urllib.request, re, pathlib, hashlib
CACHE = pathlib.Path(__file__).parent / "cache"; CACHE.mkdir(exist_ok=True)  # cache local, non versionné
UNITS = pathlib.Path(__file__).parent / "units.txt"
COST = {"search": 100, "channels": 1, "playlistItems": 1, "videos": 1}
def api(point, **params):
    key = hashlib.md5((point + json.dumps(params, sort_keys=True)).encode()).hexdigest()
    f = CACHE / f"{point}_{key}.json"
    if f.exists(): return json.loads(f.read_text())
    p = dict(params); p["key"] = os.environ["YOUTUBE_API_KEY"]
    url = f"https://www.googleapis.com/youtube/v3/{point}?{urllib.parse.urlencode(p)}"
    with urllib.request.urlopen(url, timeout=30) as r: d = json.load(r)
    f.write_text(json.dumps(d))
    u = int(UNITS.read_text()) if UNITS.exists() else 0
    UNITS.write_text(str(u + COST.get(point, 1)))
    return d
def dur(s):
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    if not m: return 0
    d,h,mi,se = [int(x or 0) for x in m.groups()]
    return d*86400+h*3600+mi*60+se
def videos(ids):
    out = []
    for i in range(0, len(ids), 50):
        r = api("videos", part="snippet,statistics,contentDetails", id=",".join(ids[i:i+50]))
        for v in r.get("items", []):
            s = v["statistics"]
            out.append(dict(id=v["id"], title=v["snippet"]["title"], date=v["snippet"]["publishedAt"][:10],
                channel=v["snippet"]["channelTitle"], channel_id=v["snippet"]["channelId"],
                views=int(s.get("viewCount", 0)), likes=int(s.get("likeCount", 0)), comments=int(s.get("commentCount", 0)),
                dur=dur(v["contentDetails"].get("duration"))))
    return out
def channel(handle):
    r = api("channels", part="snippet,statistics,contentDetails", forHandle=handle)
    if not r.get("items"): return None
    c = r["items"][0]
    return dict(id=c["id"], title=c["snippet"]["title"], created=c["snippet"]["publishedAt"][:10],
        country=c["snippet"].get("country"), subs=int(c["statistics"].get("subscriberCount", 0)),
        views=int(c["statistics"].get("viewCount", 0)), nvid=int(c["statistics"].get("videoCount", 0)),
        uploads=c["contentDetails"]["relatedPlaylists"]["uploads"])
def uploads(pl, maxn=2000):
    ids, tok = [], None
    while len(ids) < maxn:
        kw = dict(part="contentDetails", playlistId=pl, maxResults=50)
        if tok: kw["pageToken"] = tok
        r = api("playlistItems", **kw)
        ids += [i["contentDetails"]["videoId"] for i in r.get("items", [])]
        tok = r.get("nextPageToken")
        if not tok: break
    return ids
