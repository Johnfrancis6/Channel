import json, collections
from yt2 import *
cat = json.load(open("cat.json"))
c = channel(cid="UCQMyhrt92_8XM0KgZH6VnRg"); c["videos"] = videos(uploads(c["uploads"])); cat["@companyman"] = c
found = collections.Counter(); ex = {}
for q in ["explained like you're 5", "how he actually built the company", "the rise and fall explained", "biggest business mistakes in history explained"]:
    r = api("search", part="snippet", q=q, type="video", order="viewCount", publishedAfter="2025-01-01T00:00:00Z", relevanceLanguage="en", maxResults=50)
    for it in r["items"]:
        found[it["snippet"]["channelId"]] += 1; ex.setdefault(it["snippet"]["channelId"], it["snippet"]["title"])
known = {v["id"] for v in cat.values()}
ids = [k for k in found if k not in known]
chs = []
for i in range(0, len(ids), 50):
    r = api("channels", part="snippet,statistics", id=",".join(ids[i:i+50]))
    for x in r["items"]:
        chs.append((int(x["statistics"].get("subscriberCount",0)), x["snippet"]["publishedAt"][:10], x["snippet"]["title"], x["snippet"].get("customUrl"), found[x["id"]], ex[x["id"]][:60], x["id"]))
for c_ in sorted(chs, reverse=True)[:45]: print(c_[:6])
json.dump(cat, open("cat.json","w")); json.dump(chs, open("found.json","w"))
