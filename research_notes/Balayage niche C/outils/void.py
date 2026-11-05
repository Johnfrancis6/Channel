import json
from yt import *
Q = {"costco":"costco hot dog business","cards":"credit card rewards who pays","robinhood":"robinhood free trading how it makes money",
     "amazon":"amazon free shipping cost business","bnpl":"klarna afterpay buy now pay later how they make money"}
out={}
for k,q in Q.items():
    r = api("search", part="snippet", q=q, type="video", order="viewCount", publishedAfter="2025-11-05T00:00:00Z", relevanceLanguage="en", maxResults=25)
    vs = [v for v in videos([i["id"]["videoId"] for i in r["items"]]) if v["dur"]>180]
    out[k]=vs
    print("##",k, "| vidéos longues depuis 12 mois:",len(vs))
    for v in sorted(vs,key=lambda v:-v["views"])[:6]: print("  ",v["views"],v["date"],v["channel"][:22],"|",v["title"][:70])
json.dump(out,open("void.json","w"))
