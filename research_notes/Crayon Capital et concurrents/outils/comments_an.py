import json, re, collections, sys
cat=json.load(open("cat.json")); com=json.load(open("comments.json"))
CATS={
 "éloge":r"\b(great|amazing|awesome|love (this|it|the|your)|best (video|channel)|underrated|masterpiece|incredible|well done|so good|fantastic|brilliant)\b",
 "simplicité / pédagogie":r"like (i'?m|i am|you'?re) (5|five)|finally understand|easy to understand|explained (so )?(well|simply|clearly)|my (teacher|professor)|school|learned more|simple",
 "dessin / animation":r"animat|drawing|drawn|art style|artwork|illustrat|doodle|crayon|visual",
 "narration / voix":r"\bvoice\b|narrat|storytell",
 "demande de sujet":r"(do|make) (a|one|an) (video|episode)|next (video|episode|one)|please (do|make|cover)|can you (do|make|cover)|cover (the|a)|part 2|you should do",
 "correction / désaccord":r"\b(actually|incorrect|inaccura|wrong|mistake|not true|misleading|error|correction|fact.?check)\b",
 "récit personnel":r"\b(i worked|my (dad|father|mom|mother|grand|uncle|family)|i remember|when i was|i was (a|an|there|born)|i lived|i used to)\b",
 "politique / morale":r"\b(trump|biden|democrat|republican|capitalis|communis|socialis|billionaire|greed|corrupt|government|elite|oligarch|tax the)\b",
 "IA (critique ou soupçon)":r"\bai (voice|generated|slop|art|image)|\bai\b.*\b(made|written)|chatgpt|slop|\bbot\b",
 "sponsor / pub":r"\bsponsor|\bad\b|ads\b|incogni|betterhelp|abacus|nordvpn|zocdoc",
 "humour":r"\b(lol|lmao|😂|🤣)",
}
def run(h, ids=None):
    cid=cat[h]["id"]; rows=[]
    for vid,L in com[h].items():
        if ids and vid not in ids: continue
        rows+=L
    n=len(rows)
    if not n: return None
    res={"n":n}
    for k,p in CATS.items():
        m=[r for r in rows if re.search(p,r["text"],re.I)]
        res[k]=(round(len(m)/n*100,1), round(sum(r["likes"] for r in m)/max(sum(r["likes"] for r in rows),1)*100,1))
    creator_top=sum(1 for r in rows if r["author"]==cid)
    replied=sum(1 for r in rows if any(x["author"]==cid for x in r["replies"]))
    res["créateur : commentaires"]=creator_top; res["créateur : fils avec réponse %"]=round(replied/n*100,1)
    return res
if __name__=="__main__":
    out={}
    for h in com:
        r=run(h); 
        if r: out[h]=r
    json.dump(out,open("comments_an.json","w"),ensure_ascii=False)
    ks=list(CATS)
    print("chaîne | n | "+" | ".join(ks)+" | créateur com | fils répondus %")
    for h,r in out.items(): print(h,"|",r["n"],"|"," | ".join(f'{r[k][0]}' for k in ks),"|",r["créateur : commentaires"],"|",r["créateur : fils avec réponse %"])
