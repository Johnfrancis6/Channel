import json
from yt import *
H = ["@fortunefall-c4u","@builtonyou","@fatalboard","@groundbreak0","@capital_case","@businessdecodedmedia",
     "@thebusinessvault-p9h","@crayon_capital","@junkbondinvest","@mondostartups","@moneychuck","@invisiblegameco",
     "@siliconpostman","@tensetime","@breakingevenyt","@papienstv","@theecontales","@explainedlikeyourefive","@grey_finances",
     "@themoneyproff","@follow_the_money101"]
cat = json.load(open("catalogs.json"))
for h in H:
    if h in cat: continue
    c = channel(h)
    if not c: print("introuvable", h); continue
    c["videos"] = videos(uploads(c["uploads"]))
    cat[h] = c
    print(h, c["title"], c["created"], c.get("country"), c["subs"], c["views"], len(c["videos"]))
json.dump(cat, open("catalogs.json","w"))
