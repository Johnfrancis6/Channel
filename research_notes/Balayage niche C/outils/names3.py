import json, re
from yt import *
for h in ["@whosedime","@onwhosedime","@whosedimetv","@whosediming","@whosedimeyt","@thedimetrail","@followthedime","@dimetrail"]:
    r = api("channels", part="snippet,statistics", forHandle=h)
    it = r.get("items") or []
    print(h, ("PRIS: "+it[0]["snippet"]["title"]+" | abonnés "+it[0]["statistics"].get("subscriberCount","?")+" | vidéos "+it[0]["statistics"].get("videoCount","?")) if it else "libre")
r = api("search", part="snippet", q='"whose dime"', type="channel", maxResults=10)
for it in r["items"]: print("chaine:", it["snippet"]["channelTitle"])
r = api("search", part="snippet", q='"who pays?" free', type="video", maxResults=50, relevanceLanguage="en")
vs = videos([i["id"]["videoId"] for i in r["items"]])
m=[v for v in vs if re.search(r":\s*who pays\?|\.\s*who pays\?", v["title"], re.I)]
print("titres en 'X: Who Pays?' :", len(m))
for v in m: print("  ", v["views"], v["date"], v["channel"][:25], "|", v["title"][:80])
