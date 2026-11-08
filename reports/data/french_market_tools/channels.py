import json, yt
sc = json.load(open("search_channels.json"))
out = {}
for lang, chans in sc.items():
    ids = list(chans)
    for k in range(0, len(ids), 50):
        d = yt.get("channels", part="snippet,statistics,contentDetails", id=",".join(ids[k:k+50]), maxResults=50)
        for it in d.get("items", []):
            s, st = it["snippet"], it["statistics"]
            out[it["id"]] = {"lang": lang, "title": s["title"], "country": s.get("country"), "dlang": s.get("defaultLanguage"),
                             "created": s["publishedAt"][:10], "subs": int(st.get("subscriberCount", 0)),
                             "views": int(st.get("viewCount", 0)), "videos": int(st.get("videoCount", 0)),
                             "uploads": it["contentDetails"]["relatedPlaylists"]["uploads"], "hits": chans[it["id"]]["n"]}
json.dump(out, open("channels.json", "w"), ensure_ascii=False)
import collections
for lang in ("fr", "en"):
    v = [c for c in out.values() if c["lang"] == lang]
    print(lang, len(v), collections.Counter(c["country"] for c in v).most_common(8))
    print("  videos<=300:", sum(c["videos"] <= 300 for c in v))
print("units", yt.used[0])
