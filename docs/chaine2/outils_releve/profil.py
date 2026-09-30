import json,sys,statistics as S
from datetime import datetime,timezone
from yt import chaine
now=datetime(2026,9,29,16,tzinfo=timezone.utc)
def f(n): return f"{n/1e6:.2f}M" if n>=1e6 else (f"{n/1e3:.1f}k" if n>=1e3 else str(n))
out=[]
for h in sys.argv[1:]:
    try: c=chaine(h,maxv=300)
    except Exception as e: print("ERR",h,e); continue
    V=c["videos"]; 
    if not V: print(h,"vide"); continue
    lon=[v for v in V if v["duree"]>180]; sh=[v for v in V if v["duree"]<=180]
    p=lon or V
    d0=datetime.fromisoformat(V[0]["date"].replace("Z","+00:00")); age=(now-d0).days
    top=sorted(V,key=lambda v:-v["vues"])[:3]
    c["resume"]=dict(premier=V[0]["date"][:10],age_j=age,n_long=len(lon),n_short=len(sh),
        med_vues_long=S.median([v["vues"] for v in lon]) if lon else None,
        med_duree_long=S.median([v["duree"] for v in lon])/60 if lon else None,
        cadence_j=round(age/len(V),1),langs=sorted({(v["audio"] or "?")[:2] for v in V}))
    out.append(c)
    r=c["resume"]
    print(f'\n## {c["titre"]} {c["handle"]} | {f(c["abonnes"])} abo | {c["nb"]} vid ({r["n_long"]} longues, {r["n_short"]} shorts) | 1re vidéo {r["premier"]} ({age} j) | 1 vid/{r["cadence_j"]} j | méd. vues longues {f(r["med_vues_long"] or 0)} | durée méd. {r["med_duree_long"] and round(r["med_duree_long"],1)} min | audio {r["langs"]} | abo/vues {c["abonnes"]/max(c["vues"],1)*100:.2f}%')
    for v in top: print(f'   {f(v["vues"]):>7} {v["date"][:10]} {v["duree"]//60}:{v["duree"]%60:02d} {v["titre"][:90]}')
json.dump(out,open("profil_resultats.json","w"),ensure_ascii=False)
