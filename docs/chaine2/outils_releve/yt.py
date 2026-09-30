#!/usr/bin/env python3
"""Script ponctuel : toutes les videos d'une chaine avec duree, vues, likes, commentaires."""
import json, os, re, sys, statistics, urllib.parse, urllib.request
from datetime import datetime, timezone
K = os.environ["YOUTUBE_API_KEY"]
def get(ep, **p):
    p["key"] = K
    with urllib.request.urlopen(f"https://www.googleapis.com/youtube/v3/{ep}?{urllib.parse.urlencode(p)}", timeout=30) as r:
        return json.load(r)
def dur(s):
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s)
    d, h, mi, se = (int(x or 0) for x in m.groups()); return d*86400 + h*3600 + mi*60 + se
def chaine(ref, maxv=500):
    sel = {"id": ref} if ref.startswith("UC") else {"forHandle": ref}
    c = get("channels", part="snippet,statistics,contentDetails,brandingSettings", **sel)["items"][0]
    up = c["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, tok = [], None
    while len(ids) < maxv:
        p = dict(part="contentDetails", playlistId=up, maxResults=50)
        if tok: p["pageToken"] = tok
        r = get("playlistItems", **p); ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        tok = r.get("nextPageToken")
        if not tok: break
    vids = []
    for i in range(0, len(ids), 50):
        for v in get("videos", part="snippet,statistics,contentDetails,localizations", id=",".join(ids[i:i+50]))["items"]:
            s, st = v["snippet"], v["statistics"]
            vids.append(dict(id=v["id"], titre=s["title"], titre_local=s.get("localized",{}).get("title"),
                date=s["publishedAt"], duree=dur(v["contentDetails"]["duration"]),
                vues=int(st.get("viewCount",0)), likes=int(st["likeCount"]) if "likeCount" in st else None,
                comms=int(st["commentCount"]) if "commentCount" in st else None,
                lang=s.get("defaultLanguage"), audio=s.get("defaultAudioLanguage"),
                locs=sorted((v.get("localizations") or {}).keys())))
    vids.sort(key=lambda v: v["date"])
    cs = c["statistics"]
    return dict(id=c["id"], titre=c["snippet"]["title"], handle=c["snippet"].get("customUrl"),
        cree=c["snippet"]["publishedAt"], pays=c["snippet"].get("country"),
        description=c["snippet"].get("description","")[:300],
        abonnes=int(cs.get("subscriberCount",0)), vues=int(cs.get("viewCount",0)), nb=int(cs.get("videoCount",0)), videos=vids)
if __name__ == "__main__":
    out = [chaine(r) for r in sys.argv[1:]]
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
