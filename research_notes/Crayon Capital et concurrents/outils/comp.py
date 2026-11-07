import json, statistics as st, re, datetime as dt
cat=json.load(open("cat.json"))
SPON=re.compile(r"#ad\b|sponsor|use code|% off|free trial|brought to you|thanks to (?!you)|incogni|nordvpn|betterhelp|abacus|ground news|brilliant\.org|surfshark|aura\.com|netsuite|monarch|squarespace|cape\.co|zocdoc|saily|raycon|kalshi|remitly",re.I)
STREAM={"newsletter":r"newsletter|substack|compoundeddaily","patreon/dons":r"patreon|buymeacoffee|ko-fi","affiliation livres":r"amzn\.to|amazon\.com/|link\.amazon","site/produit propre":r"magnatesmedia\.com|modern-mba\.com|junkbondinvestor\.com|howmoneyworkslibrary|differentiatedanalytics|companymanideas","membres YouTube":r"join this channel|/join\b|membership","ebook/cours":r"ebook|e-book|course"}
rows=[]
for h,c in cat.items():
    L=sorted([v for v in c["videos"] if v["dur"]>180],key=lambda v:v["date"])
    if len(L)<5: continue
    rec=L[-20:]
    six=[v for v in L if v["date"]>="2026-05-07"]
    sp=sum(1 for v in rec if SPON.search(v["desc"]))
    streams=[k for k,p in STREAM.items() if sum(1 for v in rec if re.search(p,v["desc"],re.I))>=3]
    rows.append(dict(h=h,subs=c["subs"],views=c["views"],n=len(L),first=L[0]["date"][:10],med=int(st.median(v["views"] for v in L)),
        med_rec=int(st.median(v["views"] for v in rec)),dur=round(st.median(v["dur"] for v in rec)/60,1),per_month=round(len(six)/6,1),
        conv=round(c["subs"]/c["views"]*1000,1),like=round(st.median(v["likes"]/max(v["views"],1)*100 for v in rec),2),
        com=round(st.median(v["comments"]/max(v["views"],1)*1000 for v in rec),2),spon=f"{sp}/{len(rec)}",streams=", ".join(streams) or "—"))
rows.sort(key=lambda r:r["first"])
print("handle | 1re longue | abonnés | vidéos | médiane | méd. 20 dern. | durée | /mois | ab/1k | likes% | comm‰ | sponsor | autres revenus")
for r in rows: print(" | ".join(str(r[k]) for k in ["h","first","subs","n","med","med_rec","dur","per_month","conv","like","com","spon","streams"]))
json.dump(rows,open("comp.json","w"))
