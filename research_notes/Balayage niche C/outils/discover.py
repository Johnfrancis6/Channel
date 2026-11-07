import json
from yt import *
Q = ["company history documentary","why no one can copy","how does it make money business model",
     "rise and fall of the company","can it beat business explained","monopoly explained company",
     "brand business documentary","the genius strategy of"]
found = {}
for q in Q:
    r = api("search", part="snippet", q=q, type="video", order="viewCount", publishedAfter="2026-03-01T00:00:00Z",
            relevanceLanguage="en", maxResults=50, videoDuration="medium")
    for it in r.get("items", []):
        found.setdefault(it["id"]["videoId"], q)
for q in ["Company Man business","Business Blaze Simon Whistler"]:
    r = api("search", part="snippet", q=q, type="channel", maxResults=5)
    for it in r["items"]: print(q, "->", it["snippet"]["channelTitle"], it["snippet"]["channelId"])
vs = videos(list(found))
json.dump(vs, open("discover.json","w"))
print(len(vs))
