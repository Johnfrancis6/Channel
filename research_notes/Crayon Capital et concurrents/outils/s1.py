import json
from yt2 import *
H = ["@crayon_capital","@moneychuck","@capital_case","@explainedlikeyourefive","@builtonyou","@CEOzoned","@junkbondinvest",
     "@mondostartups","@invisiblegameco","@fatalboard","@TradeoffLayer","@fortunefall-c4u","@businessdecodedmedia","@thebusinessvault-p9h",
     "@MagnatesMedia","@companyman","@ModernMBA","@BusinessCasual","@LogicallyAnswered","@HowMoneyWorks","@ColdFusion","@WallStreetMillennial"]
res = {}
for h in H:
    c = channel(handle=h)
    if not c: print("?", h); continue
    c["videos"] = videos(uploads(c["uploads"]))
    res[h] = c
    print(h, c["subs"], len(c["videos"]))
json.dump(res, open("cat.json","w"))
