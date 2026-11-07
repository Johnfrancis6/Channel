import json, os, urllib.parse, urllib.request, re, pathlib, hashlib
D = pathlib.Path(__file__).parent
CACHE = D/"cache"; CACHE.mkdir(exist_ok=True)  # cache local, non versionné
UNITS = D/"units.txt"
COST = {"search": 100}
def api(point, **params):
    key = hashlib.md5((point + json.dumps(params, sort_keys=True)).encode()).hexdigest()
    f = CACHE/f"{point}_{key}.json"
    if f.exists(): return json.loads(f.read_text())
    p = dict(params); p["key"] = os.environ["YOUTUBE_API_KEY"]
    url = f"https://www.googleapis.com/youtube/v3/{point}?{urllib.parse.urlencode(p)}"
    try:
        with urllib.request.urlopen(url, timeout=30) as r: d = json.load(r)
    except urllib.error.HTTPError as e:
        d = {"error": e.code, "items": []}
    f.write_text(json.dumps(d))
    UNITS.write_text(str((int(UNITS.read_text()) if UNITS.exists() else 0) + COST.get(point, 1)))
    return d
def dur(s):
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    d,h,mi,se = [int(x or 0) for x in m.groups()] if m else (0,0,0,0)
    return d*86400+h*3600+mi*60+se
def videos(ids):
    out = []
    for i in range(0, len(ids), 50):
        r = api("videos", part="snippet,statistics,contentDetails,status", id=",".join(ids[i:i+50]))
        for v in r.get("items", []):
            s, sn = v["statistics"], v["snippet"]
            out.append(dict(id=v["id"], title=sn["title"], date=sn["publishedAt"], desc=sn.get("description",""),
                tags=sn.get("tags",[]), lang=sn.get("defaultAudioLanguage"), channel=sn["channelTitle"],
                views=int(s.get("viewCount",0)), likes=int(s.get("likeCount",0)), comments=int(s.get("commentCount",0)),
                dur=dur(v["contentDetails"].get("duration")), caption=v["contentDetails"].get("caption"),
                madeForKids=v["status"].get("madeForKids")))
    return out
def channel(handle=None, cid=None):
    kw = {"forHandle": handle} if handle else {"id": cid}
    r = api("channels", part="snippet,statistics,contentDetails,brandingSettings,topicDetails", **kw)
    if not r.get("items"): return None
    c = r["items"][0]
    return dict(id=c["id"], title=c["snippet"]["title"], handle=c["snippet"].get("customUrl"), created=c["snippet"]["publishedAt"][:10],
        country=c["snippet"].get("country"), desc=c["snippet"].get("description",""),
        keywords=c.get("brandingSettings",{}).get("channel",{}).get("keywords",""),
        subs=int(c["statistics"].get("subscriberCount",0)), views=int(c["statistics"].get("viewCount",0)),
        nvid=int(c["statistics"].get("videoCount",0)), uploads=c["contentDetails"]["relatedPlaylists"]["uploads"],
        topics=c.get("topicDetails",{}).get("topicCategories",[]))
def uploads(pl):
    ids, tok = [], None
    while True:
        kw = dict(part="contentDetails", playlistId=pl, maxResults=50)
        if tok: kw["pageToken"] = tok
        r = api("playlistItems", **kw)
        ids += [i["contentDetails"]["videoId"] for i in r.get("items", [])]
        tok = r.get("nextPageToken")
        if not tok or len(ids) > 3000: break
    return ids
def comments(vid, n=200, order="relevance"):
    out, tok = [], None
    while len(out) < n:
        kw = dict(part="snippet,replies", videoId=vid, maxResults=100, order=order, textFormat="plainText")
        if tok: kw["pageToken"] = tok
        r = api("commentThreads", **kw)
        for t in r.get("items", []):
            top = t["snippet"]["topLevelComment"]["snippet"]
            reps = [x["snippet"] for x in t.get("replies",{}).get("comments",[])]
            out.append(dict(text=top.get("textDisplay",""), likes=top.get("likeCount",0), date=top.get("publishedAt"),
                author=top.get("authorChannelId",{}).get("value"), nrep=t["snippet"].get("totalReplyCount",0),
                replies=[dict(text=x.get("textDisplay",""), author=x.get("authorChannelId",{}).get("value"), likes=x.get("likeCount",0)) for x in reps]))
        tok = r.get("nextPageToken")
        if not tok: break
    return out
