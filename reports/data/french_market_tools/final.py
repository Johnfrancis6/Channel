import json, statistics as st, datetime as dt
Q = json.load(open("qualified.json")); sc = json.load(open("search_channels.json"))
FR_KEEP = {"Dolus","Fatimmond","Échos d’Acier","La Chute des Usines Français","Dossier Noir","Le Dossier Capital","Ascensions & Chutes",
 "Grandes Arnaques","SecretWealth","Les Coulisses du Business","Empires Racontés","Fleuron","Histoires de Milliards","Lore et Histoires",
 "Le Monde de la Finance","Côté Caché","Des Idées aux Empires","Dernier Bilan","Bâti Sur Toi","","Fondé sur vous","Rich And Famous Insider"}
en = sorted([r for r in Q if r["lang"] == "en"], key=lambda r: -r["subs"])
EN_DROP = {0,1,4,5,7,13,16,18,23,25,33,36,40,42,45,50,52,72,81,82,85,89,95,97,98,100,105,108,111,112,113,118,128,152}
keep = [r for r in Q if r["lang"] == "fr" and any(r["title"].startswith(k) for k in FR_KEEP if k) or (r["lang"]=="fr" and r["title"]=="")] \
     + [r for i, r in enumerate(en) if i not in EN_DROP]
keep = [r for r in keep if not (r["lang"] == "fr" and r["title"].startswith("Fronts"))]
CUT = dt.date(2026, 11, 8) - dt.timedelta(days=90)
def rate(rows, f): return f"{sum(map(f, rows))}/{len(rows)} ({100*sum(map(f, rows))/max(1,len(rows)):.0f} %)"
out = {}
for lang in ("fr", "en"):
    rows = [r for r in keep if r["lang"] == lang]
    new = [r for r in rows if r["first"] >= "2025-01-01"]
    cohort = [r for r in new if dt.date.fromisoformat(r["first"]) <= CUT]
    young = [r for r in new if dt.date.fromisoformat(r["first"]) > CUT]
    via_date_only = sum(sc[lang][r["id"]]["via"] == ["date"] for r in rows)
    print(f"\n== {lang}: {len(rows)} channels (found only by date sort: {via_date_only}); started 2025+: {len(new)}; >=90 days: {len(cohort)}; younger: {len(young)}")
    for name, rs in (("cohort >=90d", cohort), ("young <90d", young)):
        print(f" {name}: video>=100K {rate(rs, lambda r: r['best']>=1e5)} | subs>=1000 {rate(rs, lambda r: r['subs']>=1000)} | "
              f"median>=10K {rate(rs, lambda r: r['med']>=1e4)} | YPP proxy (1000 subs & 100K long views) {rate(rs, lambda r: r['subs']>=1000 and r['long_views']>=1e5)}")
        if rs:
            print(f"   median of medians {st.median(r['med'] for r in rs):.0f}; median subs {st.median(r['subs'] for r in rs):.0f}; "
                  f"median subs/1000 views {st.median(r['subs_per_k'] for r in rs if r['long_views']>1000) if any(r['long_views']>1000 for r in rs) else '-'}")
    bt = [r["breakthrough"] for r in cohort if r["breakthrough"]]
    if bt: print(f"   breakthrough (1st video >=100K): video n° median {st.median(b[0] for b in bt)}, day median {st.median(b[1] for b in bt)}")
    out[lang] = sorted(cohort + young, key=lambda r: -r["subs"])
json.dump(out, open("final.json", "w"), ensure_ascii=False, indent=0)
for r in out["fr"][:8]: print("FR", r["title"], r["subs"], r["first"], r["n_long"], int(r["med"]), r["best"], r["breakthrough"], r["subs_per_k"])
