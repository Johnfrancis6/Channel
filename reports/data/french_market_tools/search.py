import json, sys, yt
Q = {
 "fr": ["histoire de l'entreprise", "l'histoire complète de", "comment cette marque est devenue", "la chute de l'empire",
        "faillite entreprise histoire", "arnaque milliards histoire", "crise financière expliquée simplement", "le scandale qui a ruiné"],
 "en": ["company history", "the entire history of", "how this brand became", "the fall of the empire company",
        "company bankruptcy story", "billion dollar scam story", "financial crisis explained simply", "the scandal that ruined company"],
}
REG = {"fr": "FR", "en": "US"}
hits = {}
for lang, qs in Q.items():
    for q in qs:
        for order in ("viewCount", "date"):
            p = dict(part="snippet", q=q, type="video", maxResults=50, relevanceLanguage=lang, regionCode=REG[lang],
                     order=order, videoDuration="medium" if order == "date" else "any", publishedAfter="2025-01-01T00:00:00Z")
            d = yt.get("search", **p)
            for it in d.get("items", []):
                c = it["snippet"]["channelId"]
                h = hits.setdefault(lang, {}).setdefault(c, {"title": it["snippet"]["channelTitle"], "n": 0, "via": set()})
                h["n"] += 1; h["via"].add(order)
json.dump({l: {c: dict(v, via=sorted(v["via"])) for c, v in d.items()} for l, d in hits.items()},
          open("search_channels.json", "w"), ensure_ascii=False, indent=0)
print({l: len(v) for l, v in hits.items()}, "units", yt.used[0])
