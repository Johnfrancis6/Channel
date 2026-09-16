#!/usr/bin/env python3
"""
formats_video.py — ce qui change entre un Short et un format long, en un
seul endroit.

Le format d'une video (`state.json > format_video`) n'est pas un pilier de
plus : le pilier designe le **sujet** (`actu_ia`, `tuto`...), le format
designe le **pipeline**. Court ou long change le budget en mots, les
dimensions de la composition, le decoupage du storyboard et la strategie de
rendu — au meme titre que `voie`, qui est bien a la racine du state.

Pourquoi ce fichier plutot que des constantes par script : `MOTS_PAR_SECONDE`
vivait deja en double, recopie a l'identique dans `metriques.py` (A5) et
`generer_storyboard.py` (A6). Deux copies d'un debit mesure une seule fois,
qu'il faut recalibrer des qu'il y aura un corpus — c'est exactement le motif
« deux sources pour une meme regle » que la revue du 11/09 a corrige sur le
graphe des etapes. Ajouter un format aurait double la dette au lieu de
l'eteindre.

Ce module est un outil partage (§9.2) : il est deploye sous `<skill>/outils/`
chez les agents qui le declarent dans `OUTILS_PAR_SKILL`, pour qu'un skill
reste installable seul (§14).
"""

SHORT = "short"
LONG = "long"
FORMATS = (SHORT, LONG)

# Ce que lit tout code qui rencontre une video creee avant le 16/09/2026 :
# le champ est absent de leur state.json, et elles sont toutes des Shorts.
FORMAT_DEFAUT = SHORT


def format_de(state):
    """Format d'une video, lu tolerant depuis son state.json.

    Retombe sur "short" pour un state sans le champ (videos anterieures au
    16/09/2026) **et** pour une valeur inconnue : un format inattendu ne doit
    pas faire echouer un montage, il doit produire un Short et se voir au
    rapport. La validation stricte est le travail du schema, pas des lecteurs.
    """
    valeur = (state or {}).get("format_video")
    return valeur if valeur in FORMATS else FORMAT_DEFAUT


# --- Budget (§7.3) ----------------------------------------------------
#
# Debit mesure sur 2026-09-11_v01 : 231 mots reellement prononces pour 82,5 s
# de voix off, pauses inter-phrases comprises.
#
# ATTENTION, cette valeur vaut pour un Short et **n'a jamais ete mesuree sur
# un format long**. Un debit moyen sur 15 minutes integre des respirations,
# des changements de rythme et des pauses de section qu'une video de 50 s n'a
# pas : il sera plus bas, d'un montant que personne ne connait. On garde donc
# une seule constante plutot que d'en inventer une seconde, et `calibrage()`
# dit a l'agent que l'estimation longue est une borne basse. Le jour ou un
# long format aura ete enregistre, c'est ici qu'on corrige — et a un seul
# endroit.
MOTS_PAR_SECONDE = 2.8

# Cout en mots d'une idee, **tout compris** : l'idee plus sa part de hook, de
# promesse, d'exemple et de CTA. Mesure sur 2026-09-11_v01, les trois idees
# ne pesaient que 115 mots sur 231 — un budget qui ne compterait que les
# idees serait faux de moitie.
#
# Le long format n'est pas « plus d'idees » : c'est la meme enveloppe
# narrative etiree sur un segment entier, avec sa propre mise en place, son
# exemple deroule et sa transition. 300 mots par idee = ~107 s par segment.
# Valeur de depart assumee, a recalibrer sur le premier script long reel.
MOTS_PAR_IDEE = {SHORT: 45, LONG: 300}

# Nombre d'idees par defaut. Ce n'est pas une duree : c'est le nombre de
# choses que la video dit. 8 segments x 300 mots = 2400 mots, soit ~14 min a
# 2,8 mots/s — et moins si le debit long est plus lent, ce qui est probable.
IDEES_MAX_DEFAUT = {SHORT: 3, LONG: 8}

# Au-dela de quel depassement on parle. Sous +20 %, un script se resserre au
# calibrage ; au-dela, c'est une idee de trop, et ca se regle en reecrivant.
TOLERANCE_BUDGET = 0.20


def mots_par_idee(format_video, surcharge=None):
    if surcharge:
        return int(surcharge)
    return MOTS_PAR_IDEE[format_video if format_video in FORMATS else FORMAT_DEFAUT]


def idees_par_defaut(format_video):
    return IDEES_MAX_DEFAUT[format_video if format_video in FORMATS else FORMAT_DEFAUT]


def calibrage(format_video):
    """D'ou vient le modele de budget, en clair, pour l'agent qui le lit.

    Un chiffre sans sa provenance se lit comme une loi. Celui du Short a ete
    mesure une fois ; celui du long est une hypothese. La difference doit
    voyager avec la valeur, sinon A5 refusera un script long au nom d'un seuil
    que personne n'a etabli.
    """
    if format_video == LONG:
        return ("non_mesure", "Aucun format long n'a encore ete enregistre : le debit "
                              "(2,8 mots/s) et le cout par idee (300 mots) sont des "
                              "hypotheses de depart. La duree estimee est une borne "
                              "basse — un debit long est probablement plus lent.")
    return ("mesure_n1", "Debit calibre sur une seule video (2026-09-11_v01, 82,5 s). "
                         "A recalibrer quand le corpus aura plusieurs voix.")


# --- Composition (§8) -------------------------------------------------
#
# Le Short est vertical, le long est paysage. Ces valeurs alimentent
# `charte.format`, que `Root.tsx` lit dans `calculateMetadata` depuis le
# 16/09/2026 : les dimensions ne sont plus en dur dans la composition.
DIMENSIONS = {
    SHORT: {"largeur_px": 1080, "hauteur_px": 1920, "fps": 30},
    LONG: {"largeur_px": 1920, "hauteur_px": 1080, "fps": 30},
}


def dimensions(format_video):
    return dict(DIMENSIONS[format_video if format_video in FORMATS else FORMAT_DEFAUT])


# --- Storyboard (§8) --------------------------------------------------
#
# « Une scene par phrase » est la regle du Short, et elle tient : 24 phrases
# font 24 scenes a trancher, ce qui est une seance de travail pour A6.
#
# Sur un format long, la meme regle produit 150 a 300 scenes toutes marquees
# `a_completer`. Ce n'est pas une charge de travail, c'est un livrable
# indefendable : A6 le rendra en sautant des scenes, et A7 montera a
# l'aveugle. Le squelette long groupe donc les phrases en scenes de duree
# cible, et c'est le generateur qui le fait — pas A6 a qui on demanderait de
# reparer un squelette illisible.
#
# 12 s : assez long pour qu'une scene porte une idee et non un mot, assez
# court pour qu'un plan fixe ne s'installe pas. ~2400 mots a 2,8 mots/s = 857 s,
# soit ~71 scenes — une planche de storyboard qu'un humain peut relire.
DUREE_SCENE_CIBLE_S = {SHORT: None, LONG: 12.0}

# Plafond dur, quel que soit le calcul. Au-dela, le squelette est coupe en
# scenes plus longues plutot que de deborder : c'est la borne qui garantit
# que le livrable d'A6 reste relisible meme sur un script inattendu.
SCENES_MAX = {SHORT: None, LONG: 120}


def duree_scene_cible(format_video):
    return DUREE_SCENE_CIBLE_S[format_video if format_video in FORMATS else FORMAT_DEFAUT]


def scenes_max(format_video):
    return SCENES_MAX[format_video if format_video in FORMATS else FORMAT_DEFAUT]
