"""Exploration de niches : recherche YouTube (vidéos de cette année) via yt-dlp, EN et FR."""
import json, subprocess, urllib.parse, sys, concurrent.futures as cf
NICHES = {
 "prehistoire": (["how did ancient humans", "what did prehistoric humans"], ["comment nos ancêtres préhistoriques", "hommes préhistoriques comment"]),
 "moyen_age_quotidien": (["what was life like in medieval times", "how did medieval people"], ["vie quotidienne au moyen âge", "comment vivait-on au moyen âge"]),
 "antiquite_quotidien": (["how did ancient romans", "daily life in ancient egypt"], ["comment vivaient les romains", "vie quotidienne égypte antique"]),
 "objets_pourquoi": (["why do everyday objects have", "the surprising history of everyday things"], ["pourquoi les objets du quotidien", "histoire des objets du quotidien"]),
 "inventions": (["who invented", "how was it invented history"], ["qui a inventé", "l'invention de histoire"]),
 "psychologie_effets": (["the psychology effect explained", "why your brain"], ["effet psychologique expliqué", "pourquoi ton cerveau"]),
 "animaux_comportement": (["why do animals", "why do cats dogs behave"], ["pourquoi les animaux", "pourquoi les chats font"]),
 "corps_humain": (["what happens to your body if", "why does your body"], ["que se passe-t-il dans ton corps si", "pourquoi notre corps"]),
 "medecine_histoire": (["history of medicine before", "what did doctors do before"], ["médecine d'autrefois", "comment se soignait-on avant"]),
 "what_if": (["what if the earth", "what would happen if"], ["et si la terre", "que se passerait-il si"]),
 "pov_metiers_histoire": (["your life as a medieval", "what it was like to be a"], ["ta vie de paysan au moyen âge", "dans la peau d'un"]),
 "alimentation_histoire": (["history of food why do we eat", "what did people eat in"], ["histoire de l'alimentation", "que mangeait-on au"]),
 "mythologie": (["greek mythology explained", "mythical creatures explained"], ["mythologie expliquée", "créatures légendaires"]),
 "peuples_survie": (["how do inuit survive", "how tribes survive"], ["comment survivent les inuits", "peuple qui vit comme il y a"]),
 "histoire_pour_dormir": (["history for sleep", "boring history to fall asleep"], ["histoire pour s'endormir", "documentaire pour dormir histoire"]),
 "espace": (["what if you fell into", "how big is the universe"], ["et si tu tombais dans un trou noir", "l'univers expliqué"]),
}
SP = "EgQIBRAB"  # cette année + vidéos
import os, hashlib, time
os.makedirs("cache_niches", exist_ok=True)
def cherche(q, lang):
    f = "cache_niches/" + hashlib.md5((lang+q).encode()).hexdigest() + ".json"
    if os.path.exists(f): return json.load(open(f))
    time.sleep(2)
    url = "https://www.youtube.com/results?" + urllib.parse.urlencode({"search_query": q, "sp": SP, "hl": lang, "gl": "FR" if lang == "fr" else "US"})
    r = subprocess.run(["yt-dlp", "--flat-playlist", "-J", "--playlist-end", "120", url], capture_output=True, text=True, timeout=300)
    try: d = json.loads(r.stdout)
    except Exception: return []
    res = [{k: e.get(k) for k in ("id", "title", "channel", "channel_id", "view_count", "duration")} for e in (d.get("entries") or []) if e]
    if res: json.dump(res, open(f, "w"), ensure_ascii=False)
    return res
if __name__ == "__main__":
    jobs = [(n, l, q) for n, (en, fr) in NICHES.items() for l, qs in (("en", en), ("fr", fr)) for q in qs]
    out = {}
    with cf.ThreadPoolExecutor(2) as ex:
        fut = {ex.submit(cherche, q, l): (n, l, q) for n, l, q in jobs}
        for f in cf.as_completed(fut):
            n, l, q = fut[f]; res = f.result()
            out.setdefault(n, {}).setdefault(l, {})[q] = res
            print(n, l, q, len(res), flush=True)
    json.dump(out, open("niches_brut.json", "w"), ensure_ascii=False)
