import json, re
from yt import *
for h in ["@someonepays","@someonepaysyt","@somebodypays","@whopays","@whoreallypays","@whopaysfor","@thehiddenbill","@someone_pays","@someonealwayspays"]:
    r = api("channels", part="snippet,statistics", forHandle=h)
    it = r.get("items") or []
    print(h, "PRIS:"+it[0]["snippet"]["title"]+" "+it[0]["statistics"].get("subscriberCount","?") if it else "libre")
for q in ['"who pays for"', '"someone pays"']:
    r = api("search", part="snippet", q=q, type="video", maxResults=50, relevanceLanguage="en")
    ids=[i["id"]["videoId"] for i in r["items"]]
    vs=videos(ids)
    m=[v for v in vs if re.search(r"who (really )?pays for|someone pays", v["title"], re.I)]
    print("##", q, len(vs), "titres qui contiennent le gabarit:", len(m))
    for v in sorted(m,key=lambda v:-v["views"]): print("  ", v["views"], v["date"], v["channel"][:25], "|", v["title"][:80])
r = api("search", part="snippet", q="Someone Pays", type="channel", maxResults=10)
for it in r["items"]: print("chaine:", it["snippet"]["channelTitle"], it["snippet"]["channelId"])
