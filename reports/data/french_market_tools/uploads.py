import json, re, yt
ch = json.load(open("channels.json"))
def dur(s):
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    d, h, mi, se = (int(x or 0) for x in m.groups()) if m else (0, 0, 0, 0)
    return d * 86400 + h * 3600 + mi * 60 + se
vids = {}
for cid, c in ch.items():
    if c["videos"] > 300 or c["videos"] == 0:
        continue
    ids, tok = [], None
    while True:
        p = dict(part="contentDetails", playlistId=c["uploads"], maxResults=50)
        if tok: p["pageToken"] = tok
        try:
            d = yt.get("playlistItems", **p)
        except SystemExit as e:
            print(cid, e); break
        ids += [i["contentDetails"]["videoId"] for i in d.get("items", [])]
        tok = d.get("nextPageToken")
        if not tok: break
    rows = []
    for k in range(0, len(ids), 50):
        d = yt.get("videos", part="snippet,contentDetails,statistics", id=",".join(ids[k:k+50]), maxResults=50)
        for v in d.get("items", []):
            s, st = v["snippet"], v.get("statistics", {})
            rows.append({"id": v["id"], "t": s["title"], "pub": s["publishedAt"][:10], "dur": dur(v["contentDetails"].get("duration")),
                         "views": int(st.get("viewCount", 0)), "audio": s.get("defaultAudioLanguage") or s.get("defaultLanguage"),
                         "live": s.get("liveBroadcastContent")})
    vids[cid] = rows
json.dump(vids, open("videos.json", "w"), ensure_ascii=False)
print(len(vids), "channels", sum(map(len, vids.values())), "videos", "units", yt.used[0])
