import json, sys
from yt import *
H = ["@ColdFusion","@MagnatesMedia","@companyman","@HowMoneyWorks","@BusinessCasual","@LogicallyAnswered",
     "@ModernMBA","@BusinessBlaze","@PolyMatter","@EconomicsExplained","@WallStreetMillennial","@Asianometry",
     "@CEOzoned","@TradeoffLayer","@thecorporatestoryyt","@fletcherfinance","@theinvisibleledger-h7s",
     "@thequietmonopoly-u2c","@brandsunfolded","@systemledger-media","@livingmath","@mogul-ed","@nextgianthistory",
     "@behindthesuccess-s2n","@exhibita_official","@mirkosinsights","@richanatomy09"]
res = {}
for h in H:
    c = channel(h)
    if not c: print("introuvable", h); continue
    ids = uploads(c["uploads"])
    c["videos"] = videos(ids)
    res[h] = c
    print(h, c["title"], c["subs"], len(c["videos"]))
json.dump(res, open("catalogs.json","w"))
