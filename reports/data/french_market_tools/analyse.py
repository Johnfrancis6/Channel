import json, re, statistics as st, sys, datetime as dt, collections
TODAY = dt.date(2026, 11, 8)
ch = json.load(open("channels.json")); vids = json.load(open("videos.json"))
BRANDS = r"amazon|apple|tesla|nike|adidas|coca|pepsi|mcdonald|starbucks|nvidia|google|microsoft|meta|facebook|netflix|disney|uber|airbnb|wework|nintendo|sony|samsung|toyota|ferrari|lvmh|louis vuitton|hermès|hermes|chanel|l'oréal|loreal|danone|carrefour|leclerc|total|renault|peugeot|michelin|ikea|lego|zara|shein|temu|tiktok|spacex|openai|chatgpt|kodak|nokia|blackberry|enron|ftx|theranos|boeing|airbus|red bull|rolex|ikea|walmart|costco|ryanair|easyjet|bic|orangina|kinder|ferrero|nutella|lacoste|decathlon|free|orange|bernard arnault|elon musk|bezos|rockefeller|madoff|ponzi|evergrande|lehman"
MONEY = {"fr": r"entreprise|marque|empire|milliard|faillite|arnaque|scandale|pdg|fondateur|business|start-?up|soci[ée]t[ée]|krach|crise financi|bourse|monopole|ruin|fortune|milliardaire|banque|march[ée]|argent|\$|€|multinationale|industrie",
         "en": r"company|brand|empire|billion|bankrupt|scam|scandal|ceo|founder|business|start-?up|corporation|crash|financial crisis|stock|monopoly|ruin|fortune|billionaire|bank|market|money|\$|industry"}
def lang_ok(c, rows):
    a = [r["audio"] for r in rows if r["audio"]]
    if len(a) >= 3:
        return sum(x.lower().startswith(c["lang"]) for x in a) / len(a) >= 0.6
    fr = sum(bool(re.search(r"\b(le|la|les|des|du|une|est|qui|comment|pourquoi)\b", r["t"].lower())) for r in rows)
    return (fr / max(1, len(rows)) >= 0.3) == (c["lang"] == "fr")
res = []
for cid, rows in vids.items():
    c = ch[cid]; lang = c["lang"]
    long = sorted([r for r in rows if r["dur"] > 180 and r["live"] == "none"], key=lambda r: r["pub"])
    if len(long) < 3 or not lang_ok(c, rows):
        continue
    rx = re.compile(f"{MONEY[lang]}|{BRANDS}", re.I)
    share = sum(bool(rx.search(r["t"])) for r in long) / len(long)
    if share < 0.5:
        continue
    views = [r["views"] for r in long]; med = st.median(views)
    first = dt.date.fromisoformat(long[0]["pub"]); age = (TODAY - first).days
    br = next(((k + 1, (dt.date.fromisoformat(r["pub"]) - first).days) for k, r in enumerate(long) if r["views"] >= 100_000), None)
    old = [r for r in long if (TODAY - dt.date.fromisoformat(r["pub"])).days > 14]
    res.append(dict(id=cid, lang=lang, title=c["title"], country=c["country"], subs=c["subs"], first=long[0]["pub"], age=age,
                    n_long=len(long), long_views=sum(views), med=med, best=max(views), share=round(share, 2),
                    r3=round(sum(r["views"] >= 3 * med for r in old) / max(1, len(old)), 3),
                    subs_per_k=round(1000 * c["subs"] / max(1, c["views"]), 1), breakthrough=br,
                    last=long[-1]["pub"], sample=[r["t"] for r in sorted(long, key=lambda r: -r["views"])[:3]]))
json.dump(res, open("qualified.json", "w"), ensure_ascii=False, indent=0)
print({l: sum(r["lang"] == l for r in res) for l in ("fr", "en")})
