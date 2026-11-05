import json, collections
from yt import *
cat = json.load(open("catalogs.json"))
r = api("channels", part="snippet,statistics,contentDetails", id="UCQMyhrt92_8XM0KgZH6VnRg")
c = r["items"][0]
cm = dict(id=c["id"], title=c["snippet"]["title"], created=c["snippet"]["publishedAt"][:10], country=c["snippet"].get("country"),
  subs=int(c["statistics"]["subscriberCount"]), views=int(c["statistics"]["viewCount"]), nvid=int(c["statistics"]["videoCount"]),
  uploads=c["contentDetails"]["relatedPlaylists"]["uploads"])
cm["videos"] = videos(uploads(cm["uploads"]))
cat["@companyman"] = cm
for k in ["@BusinessBlaze"]: cat.pop(k, None)
json.dump(cat, open("catalogs.json","w"))
print("Company Man", cm["subs"], len(cm["videos"]))
# channels in discovery
d = json.load(open("discover.json"))
ids = sorted({v["channel_id"] for v in d})
known = {c["id"] for c in cat.values()}
chs = {}
for i in range(0, len(ids), 50):
    rr = api("channels", part="snippet,statistics", id=",".join(ids[i:i+50]))
    for c in rr["items"]:
        chs[c["id"]] = dict(title=c["snippet"]["title"], created=c["snippet"]["publishedAt"][:10],
            subs=int(c["statistics"].get("subscriberCount",0)), nvid=int(c["statistics"].get("videoCount",0)),
            views=int(c["statistics"].get("viewCount",0)), handle=c["snippet"].get("customUrl"))
json.dump(chs, open("discover_channels.json","w"))
by = collections.defaultdict(list)
for v in d: by[v["channel_id"]].append(v)
rows = []
for cid, vs in by.items():
    c = chs.get(cid, {})
    rows.append((c.get("created",""), c.get("title"), c.get("handle"), c.get("subs"), c.get("nvid"), max(v["views"] for v in vs), [ (v["views"], v["title"][:60], v["date"]) for v in sorted(vs, key=lambda v:-v["views"])[:2]]))
for r_ in sorted(rows, reverse=True):
    if r_[0] >= "2024-06-01": print(r_)
