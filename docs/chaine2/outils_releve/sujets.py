#!/usr/bin/env python3
"""Script ponctuel : quels sujets des chaînes anglaises les chaînes françaises reprennent.

Entrée : le relevé de yt.py ({"en": [chaînes], "fr": [chaînes]}) et, facultatif, les titres
anglais déclarés des vidéos françaises ({id: {"en": titre}}). Chaque vidéo de plus de 3 min reçoit
au plus un sujet (le premier de SUJETS qui correspond, du plus précis au plus large), à partir de
son titre (et de son titre anglais déclaré pour une vidéo française). Sortie : sujets.json.

    python3 sujets.py releve.json [fr_titres_en.json] > sujets.json
"""
import json, re, statistics, sys, unicodedata
from datetime import datetime

# (clé, motif anglais, motif français) — testés sans accents ni majuscules, du plus précis au plus large.
SUJETS = [
    ("journee", r"all day|during the day|before (jobs|work)|without jobs|no jobs", r"toute la journee|la journee|avant (le|l.invention du) travail|24 heures dans"),
    ("predateurs_endormis", r"sleeping humans|attack sleeping", r"endormis|quand tu dors"),
    ("bebes", r"(kids|babies|twins) alive|babies crying|baby .*cry|human babies", r"bebes? en vie|bebe hurlait"),
    ("nuit", r"at night|during the night|all night|scared at night", r"la nuit\b(?! d.un)|avant l.electricite"),
    ("pluie", r"\brain", r"pluie|pleuv|il a plu"),
    ("souvenir_bebe", r"remember being a baby|baby memories", r"souvient d.avoir ete bebe|souvenir de ton enfance"),
    ("s_endormir", r"remember falling asleep|pretend to sleep", r"t.endors|s.endormir"),
    ("regles", r"\bperiods?\b", r"\bregles\b"),
    ("contraception", r"prevent pregnancy|condoms", r"eviter? (une|la) grossesse|pilule"),
    ("grossesse_naissance", r"pregnan|give birth|childbirth", r"enceinte|grossesse|accouch"),
    ("seule_espece", r"only human species|other human species|neanderthals disappear|nine human", r"seule espece|neuf especes|autres especes humaines|seuls survivants|encore debout|seuls humains encore"),
    ("couleur_peau", r"black to white|dark skin|become white|light skin|look so different", r"peau claire|noir au blanc|couleurs? de peau"),
    ("yeux_bleus", r"blue eyes", r"yeux bleus"),
    ("vetements", r"clothes", r"habill|vetements"),
    ("alcool", r"alcohol", r"alcool"),
    ("drogues_tabac", r"smok|weed|cannabis|popular dru|drugs", r"\bfum|cannabis|drogue"),
    ("sel", r"\bsalt\b", r"\bsel\b"),
    ("sucre_chocolat", r"sugar|chocolate", r"sucre|chocolat"),
    ("metaux", r"\biron\b|metal|bronze|copper|\btin\b", r"\bfer\b|metaux|bronze|cuivre|etain"),
    ("verre", r"\bglass\b", r"\bverre\b"),
    ("papier", r"\bpaper\b", r"papier"),
    ("argent", r"money|banks|taxes", r"\bargent\b|impots"),
    ("armes_feu", r"\bguns?\b|firearm", r"armes? a feu"),
    ("chiens_loups", r"\bdogs?\b|wolves|wolf", r"chiens?\b|loups?\b"),
    ("animaux_aide", r"know when .*help|helping them|we.re helping|save humans|rescue us|ask humans for help|bring babies to humans", r"animaux .*aid|en detresse|vers nous|qui les ont sauves"),
    ("animaux_tristes", r"human is sad|you.re sad", r"tu es triste|on est triste|tristesse"),
    ("animaux_peur", r"(animals|animal) .*(scared|fear|terrified)|learn to fear", r"animaux .*peur"),
    ("animaux_pensent", r"animals think", r"animaux pensent|pensent .*animaux|animaux des humains"),
    ("manger_predateurs", r"eat predators|lion meat|eat lions|dog meat|hunt humans", r"predateurs\b.*mange|mange.*predateurs|viande de predateurs|requin|orques"),
    ("oeufs_lait", r"\beggs\b|\bmilk\b", r"oeufs|\blait\b"),
    ("chaleur", r"heatwave|\bheat\b|desert", r"canicule|chaleur|43 .c|desert|trop chaud"),
    ("moustiques", r"mosquito", r"moustique"),
    ("froid_hiver", r"winter|freezing|\bcold\b|frozen north|ice age|71.c", r"hiver|froid|−20|-20|−30|-30|glacial|chauffage"),
    ("predateurs", r"predator", r"predateur|meute|proie"),
    ("eau", r"dirty water|transport water|actually drink", r"eau sale|l.eau\b"),
    ("hygiene", r"\bclean\b|wash|gross was", r"propres|nettoy|fesses"),
    ("intimite", r"privacy|private life", r"intimite|vie privee"),
    ("ennui_plaisir", r"boredom|for fun|for pleasure", r"ennui|plaisir|amus|divertir"),
    ("voyager", r"travel|without maps", r"voyag|pieds nus|perdus"),
    ("communiquer", r"communicat|speak|speech", r"communiqu|sans parler"),
    ("sante", r"\bsick\b|medicine|disease|wounds|cancer|surgery|toothache|pandemic", r"maladie|medecine|infection|cancer"),
    ("obesite", r"obes", r"obese"),
    ("esperance_vie", r"die young|die at 30|age did most|lifespan", r"esperance de vie|30 ans"),
    ("consanguinite", r"family members|inbreeding", r"avec leur famille|consanguin"),
    ("peur_noir", r"fear the dark", r"peur du noir"),
    ("roue", r"\bwheel", r"\broue\b"),
    ("grands_parents", r"grandparents|elders", r"grands-parents"),
    ("dents", r"tooth|teeth", r"caries|\bdents\b"),
    ("pain", r"\bbread\b", r"\bpain\b"),
    ("odeur", r"\bsmell", r"sentaient"),
    ("civilisations", r"civilizations (collapse|disappear)|ancient wonder", r"civilisations .*dispar"),
    ("titanic", r"titanic", r"titanic"),
    ("maquillage", r"makeup", r"maquill"),
    ("pere", r"identify fathers", r"qui est le pere"),
    ("guerre", r"\bwars?\b", r"guerre"),
    ("ecriture_noms", r"writing|signatures|names", r"ecriture"),
    ("momies", r"mummif", r"momifi"),
    ("riches", r"\brich\b", r"\briches\b"),
    ("dangereux", r"terrifying animal|so dangerous|made humans so dangerous", r"si dangereux|redoutable"),
    ("beaute", r"attractive", r"\bbeaux\b|seduisant"),
    ("femmes_fortes", r"stronger than|cavewomen", r"plus fortes"),
    ("afrique", r"africa", r"afrique"),
    ("ocean", r"ocean get creepier|deep ocean", r"ocean devient"),
    ("armes", r"weapon|\baxe\b|bola|boomerang", r"\barmes\b"),
    ("feu", r"\bfire\b", r"\bfeu\b"),
    ("mort", r"after we die|death|dying|\bdie\b|buried|graves", r"\bmort\b|morts\b|enterr"),
    ("manger", r"\beat\b|food|meals", r"mang|repas|gras"),
    ("couple_sexe", r"partner|sex life|in love|find love|relationships|share wives|loyal", r"drague|amour|partenaire|infideles|mariage|qui on aimait"),
    ("enfants_12", r"parents at 12", r"enfants a 12"),
    ("criminels", r"criminals", r"meurtrier|prisons"),
    ("cheveux", r"\bbald|shave|hair", r"cheveux"),
    ("lunettes", r"glasses|eyesight", r"lunettes|myopes"),
    ("geants_chasse", r"hunt giant|weapon .*giants", r"chassaient.*geants|armes de l.age de pierre"),
    ("calhoun", r"calhoun|universe 25", r"univers 25|calhoun"),
    ("amerique", r"america", r"amerique"),
    ("domestication", r"domesticat|zebra|giraffe|camels", r"zebre|dompt|domestiqu"),
    ("pouvoir_rois", r"royals|kings|pharaoh|countries|leader", r"\brois\b|pharaons|leader|\bchef"),
]
GENRE = ("Ink Explainer", "Axen", "Zenn", "The Primal Glitch", "Paint It Simple", "Mack", "Explain In Paint", "Stickly")


def plat(t):
    t = unicodedata.normalize("NFKD", (t or "").lower())
    return "".join(c for c in t if not unicodedata.combining(c)).replace("’", "'")


def sujet(titres, langue):
    for cle, en, fr in SUJETS:
        for t, l in titres:
            if re.search(en if l == "en" else fr, plat(t)):
                return cle
    return None


def jour(v):
    return datetime.fromisoformat(v["date"].replace("Z", "+00:00")).date()


def main(releve, titres_en=None):
    d = json.load(open(releve, encoding="utf-8"))
    loc = json.load(open(titres_en, encoding="utf-8")) if titres_en else {}
    lignes = []
    for langue in ("en", "fr"):
        for c in d[langue]:
            for v in c["videos"]:
                if v["duree"] <= 180:
                    continue
                titres = [(v["titre"], langue)]
                if langue == "fr" and (loc.get(v["id"]) or {}).get("en"):
                    titres.append((loc[v["id"]]["en"], "en"))
                lignes.append(dict(langue=langue, chaine=c["titre"].strip(), genre=c["titre"] in GENRE,
                                   id=v["id"], date=str(jour(v)), vues=v["vues"], titre=v["titre"],
                                   sujet=sujet(titres, langue)))
    json.dump(lignes, sys.stdout, ensure_ascii=False, indent=0)


if __name__ == "__main__":
    main(*sys.argv[1:])
