import json, statistics as st
from yt2 import *
cat=json.load(open("cat.json"))
pick={}
for h,c in cat.items():
    L=[v for v in c["videos"] if v["dur"]>180 and v["comments"]>0]
    if not L: continue
    if h=="@crayon_capital": sel=L
    else:
        L2=sorted(L,key=lambda v:-v["views"]); rec=sorted(L,key=lambda v:v["date"])[-2:]
        med=sorted(L,key=lambda v:v["views"])[len(L)//2]
        sel=list({v["id"]:v for v in L2[:2]+[med]+rec}.values())
    pick[h]=[v["id"] for v in sel]
out={}
for h,ids in pick.items():
    out[h]={}
    for vid in ids:
        out[h][vid]=comments(vid, n=300 if h=="@crayon_capital" else 200)
    print(h,len(ids),sum(len(x) for x in out[h].values()))
json.dump(out,open("comments.json","w"))
