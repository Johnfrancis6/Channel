#!/usr/bin/env python3
"""
new_short.py — crée une nouvelle vidéo Short dans /ChaineYouTube/videos/.

Il écrit UNIQUEMENT :
  - videos/{video_id}/            (nouveau dossier, création exclusive)
  - videos/{video_id}/state.json
  - videos/{video_id}/checkpoints/

Il ne lance aucun agent et ne modifie aucun fichier partagé. Le registre des
vidéos est une vue reconstruite à partir des state.json.

Les consignes de Franco sont structurees plutot que deversees dans une note
libre : `--format` (le format narratif, qui porte le budget en mots par
idee), `--reference` (video de reference pour la mise en scene) et `--idees`
(le budget du Short : un nombre d'idees, pas une duree). `--note` reste pour
le reste.

Sortie : un objet JSON sur stdout (toujours), avec "ok" et "code".
Codes : 0 ok | 2 racine/config/argument | 3 backlog vide | 4 doublon | 5 sujet_id invalide
"""
import argparse
import json
import os
import re
import shutil
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

PILIERS = ["actu_ia", "avis_outil", "concept", "projet_perso", "tuto", "a_determiner"]

# Le titre de travail sert d'etiquette : tableau de bord, registre, en-tete du
# storyboard. Le sujet, lui, peut faire plusieurs lignes. Les recopier l'un
# dans l'autre sans limite a produit un "titre" de 180 caracteres sur la
# premiere video, repris tel quel partout en aval.
TITRE_MAX = 80

# Nombre d'idees par defaut dans un Short. La duree n'est pas fixee en
# secondes : c'est le nombre d'idees qui est plafonne, et le cout en mots
# d'une idee depend du format (un dialogue coute plus qu'une explication).
# Un format peut donc depasser 60 s sans deroger a la regle.
IDEES_MAX_DEFAUT = 3
STATUTS_INACTIFS = {"abandonnee"}
TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "state_template.json"


def maintenant_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sortir(code, message, **extra):
    print(json.dumps({"ok": code == 0, "code": code, "message": message, **extra},
                     ensure_ascii=False, indent=2))
    sys.exit(code)


def est_racine(p):
    return p.is_dir() and ((p / "00_Profil").is_dir() or (p / "videos").is_dir())


def trouver_racine(arg):
    if arg:
        p = Path(arg).expanduser()
        return p.resolve() if est_racine(p) else None
    candidats = []
    env = os.environ.get("CHAINE_YT_ROOT")
    if env:
        candidats.append(Path(env).expanduser())
    home = Path.home()
    for sous in ["ChaineYouTube", "GoogleDrive/ChaineYouTube", "Google Drive/ChaineYouTube",
                 "gdrive/ChaineYouTube", "My Drive/ChaineYouTube", "Mon Drive/ChaineYouTube"]:
        candidats.append(home / sous)
    candidats += sorted(home.glob("Library/CloudStorage/GoogleDrive-*/*/ChaineYouTube"))
    for lettre in "GHIJ":
        for sous in ["Mon Drive", "My Drive"]:
            candidats.append(Path(f"{lettre}:/") / sous / "ChaineYouTube")
    for c in candidats:
        try:
            if est_racine(c):
                return c.resolve()
        except OSError:
            continue
    return None


def lire_json(chemin, defaut=None):
    try:
        return json.loads(chemin.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return defaut
    except (json.JSONDecodeError, OSError):
        return defaut


def ecrire_json_atomique(chemin, data):
    tmp = chemin.with_name(chemin.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, chemin)


def normaliser(texte):
    if not texte:
        return ""
    t = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def raccourcir_titre(texte, maxi=TITRE_MAX):
    """Etiquette courte derivee du sujet, coupee sur un mot entier."""
    if not texte:
        return texte
    titre = " ".join(texte.split())
    if len(titre) <= maxi:
        return titre
    coupe = titre[:maxi].rsplit(" ", 1)[0].rstrip(" ,;:-—")
    return (coupe or titre[:maxi].rstrip()) + "…"


def videos_existantes(racine):
    res = []
    d = racine / "videos"
    if not d.is_dir():
        return res
    for p in sorted(d.iterdir()):
        if not p.is_dir():
            continue
        st = lire_json(p / "state.json")
        if isinstance(st, dict):
            res.append(st)
    return res


def charger_backlog(racine):
    data = lire_json(racine / "02_Veille_hebdo" / "backlog_sujets.json", {})
    sujets = data.get("sujets", []) if isinstance(data, dict) else data
    return [s for s in sujets if isinstance(s, dict) and s.get("sujet_id")]


def est_valide_en_lot(sujet):
    """Un sujet du backlog n'est "validé en lot" que s'il porte `valide_le`.

    C'est ce marqueur (§9.1) qui autorise new_short à pré-valider le CP1. Sans
    ce garde-fou, n'importe quelle entrée déposée dans backlog_sujets.json —
    une proposition du Chercheur pas encore soumise, une ligne ajoutée à la
    main — ferait démarrer une vidéo avec CP1 déjà `valide`, donc un sujet
    choisi sans l'accord de Franco. C'est précisément ce qu'interdit le §2.
    """
    return bool(sujet.get("valide_le"))


def chercher_doublon(sujet, videos):
    cible = normaliser(sujet)
    if len(cible) < 8:
        return None
    for v in videos:
        if v.get("statut_global") in STATUTS_INACTIFS:
            continue
        autre = normaliser(v.get("sujet") or v.get("titre_travail"))
        if not autre:
            continue
        if autre == cible or (min(len(autre), len(cible)) >= 15 and (autre in cible or cible in autre)):
            return v.get("video_id")
    return None


def creer_dossier_exclusif(racine, date_str, dry_run):
    d = racine / "videos"
    motif = re.compile(re.escape(date_str) + r"_v(\d{2,})$")
    nums = [int(m.group(1)) for p in d.iterdir() if (m := motif.match(p.name))] if d.is_dir() else []
    n = max(nums, default=0) + 1
    if dry_run:
        return f"{date_str}_v{n:02d}", d / f"{date_str}_v{n:02d}"
    d.mkdir(exist_ok=True)
    while True:
        vid = f"{date_str}_v{n:02d}"
        try:
            (d / vid).mkdir()
            return vid, d / vid
        except FileExistsError:
            n += 1


def main():
    ap = argparse.ArgumentParser(description="Crée une nouvelle vidéo Short (dossier + state.json).")
    ap.add_argument("--root", help="Chemin de /ChaineYouTube (sinon CHAINE_YT_ROOT ou détection auto)")
    ap.add_argument("--voie", choices=["auto", "rapide", "tampon"], default="auto")
    ap.add_argument("--sujet", help="Sujet fourni par Franco (texte libre)")
    ap.add_argument("--angle", help="Angle souhaité par Franco (optionnel)")
    ap.add_argument("--pilier", choices=PILIERS)
    ap.add_argument("--sujet-id", help="Identifiant d'un sujet validé du backlog")
    ap.add_argument("--note", help="Consigne libre de Franco pour le Chercheur")
    ap.add_argument("--titre", help=f"Titre de travail court (defaut : derive du sujet, {TITRE_MAX} car. max)")
    ap.add_argument("--format", dest="format_video",
                    help="Nom du format narratif (ex. interview_fictive, explication_progressive). "
                         "Champ libre : les formats se decouvrent au fil des premieres videos.")
    ap.add_argument("--reference", help="URL ou chemin d'une video de reference pour le format / la mise en scene")
    ap.add_argument("--idees", type=int, default=IDEES_MAX_DEFAUT,
                    help=f"Nombre d'idees cible (defaut {IDEES_MAX_DEFAUT}). C'est le budget du Short, "
                         "pas sa duree : le cout en mots d'une idee depend du format.")
    ap.add_argument("--date", help="Date de création AAAA-MM-JJ (défaut : aujourd'hui, heure locale)")
    ap.add_argument("--force", action="store_true", help="Créer même si un doublon est détecté")
    ap.add_argument("--dry-run", action="store_true", help="Tout calculer sans rien écrire")
    a = ap.parse_args()

    racine = trouver_racine(a.root)
    if racine is None:
        sortir(2, "Dossier ChaineYouTube introuvable. Passe --root ou définis CHAINE_YT_ROOT.",
               root_teste=a.root or os.environ.get("CHAINE_YT_ROOT"))

    if a.idees < 1:
        sortir(2, f"--idees doit valoir au moins 1 (recu : {a.idees})")

    date_str = a.date or datetime.now().strftime("%Y-%m-%d")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str):
        sortir(2, f"Date invalide : {date_str} (attendu AAAA-MM-JJ)")

    videos = videos_existantes(racine)
    backlog = charger_backlog(racine)
    utilises = {v.get("sujet_id") for v in videos
                if v.get("sujet_id") and v.get("statut_global") not in STATUTS_INACTIFS}
    disponibles = [s for s in backlog
                   if s["sujet_id"] not in utilises and est_valide_en_lot(s)]
    disponibles.sort(key=lambda s: (s.get("valide_le") or "", s["sujet_id"]))
    non_valides = [s["sujet_id"] for s in backlog if not est_valide_en_lot(s)]

    sujet, angle, pilier = a.sujet, a.angle, a.pilier
    sujet_id, cp1_lot, semaine = None, False, None

    if a.sujet_id:
        trouve = next((s for s in backlog if s["sujet_id"] == a.sujet_id), None)
        if trouve is None:
            sortir(5, f"sujet_id inconnu dans le backlog : {a.sujet_id}",
                   disponibles=[{"sujet_id": s["sujet_id"], "sujet": s.get("sujet")} for s in disponibles])
        if not est_valide_en_lot(trouve):
            # Pas de --force ici : §2, le système ne choisit jamais le sujet
            # final sans l'accord de Franco. Il doit valider le lot d'abord.
            sortir(5, f"Le sujet {a.sujet_id} est dans le backlog mais n'est pas validé "
                      f"(champ `valide_le` absent) : il ne peut pas pré-valider le CP1. "
                      f"Fais-le valider au CP1 groupé, ou lance-le avec --sujet pour un CP1 individuel.",
                   disponibles=[{"sujet_id": s["sujet_id"], "sujet": s.get("sujet")} for s in disponibles])
        if trouve["sujet_id"] in utilises and not a.force:
            sortir(4, f"Le sujet {a.sujet_id} est déjà utilisé par une vidéo active.")
        sujet_id, voie, cp1_lot = trouve["sujet_id"], "tampon", True
        sujet = trouve.get("sujet")
        angle = angle or trouve.get("angle")
        pilier = pilier or trouve.get("pilier")
        semaine = trouve.get("semaine")
        mode = "sujet_backlog"
    elif sujet:
        voie = a.voie if a.voie != "auto" else ("rapide" if pilier == "actu_ia" else "tampon")
        mode = "sujet_impose"
    elif a.voie == "rapide":
        voie, mode = "rapide", "veille_actu"
        pilier = pilier or "actu_ia"
    else:
        if not disponibles:
            sortir(3, "Aucun sujet validé disponible dans le backlog."
                      + (f" {len(non_valides)} sujet(s) y figurent sans `valide_le` : "
                         f"ils attendent le CP1 groupé." if non_valides else ""),
                   backlog_total=len(backlog),
                   sujets_non_valides=non_valides)
        s = disponibles[0]
        sujet_id, voie, cp1_lot = s["sujet_id"], "tampon", True
        sujet, angle = s.get("sujet"), angle or s.get("angle")
        pilier = pilier or s.get("pilier")
        semaine = s.get("semaine")
        mode = "sujet_backlog"

    pilier = pilier or "a_determiner"

    if sujet and not a.force:
        doublon = chercher_doublon(sujet, videos)
        if doublon:
            sortir(4, "Un sujet très proche existe déjà dans une vidéo active.",
                   doublon_de=doublon, sujet=sujet)

    try:
        template = json.loads(TEMPLATE.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as e:
        sortir(2, f"Template state.json illisible : {e}")

    video_id, dossier = creer_dossier_exclusif(racine, date_str, a.dry_run)
    now = maintenant_iso()

    st = template
    st.update({
        "video_id": video_id,
        "cree_le": now,
        "titre_travail": a.titre or raccourcir_titre(sujet) or "Veille actu IA — sujet à proposer",
        "sujet": sujet,
        "angle": angle,
        "sujet_id": sujet_id,
        "pilier": pilier,
        "voie": voie,
        "statut_global": "sujet_valide" if cp1_lot else "idee",
        "etape_actuelle": "E1_recherche",
    })
    st["consignes"] = {
        "mode_recherche": mode,
        "note_franco": a.note,
        # Le format porte le budget en mots par idee (§8) et sert de cle au
        # corpus : c'est lui qu'on compare d'une video a l'autre, pas la duree.
        "format": a.format_video,
        # Reference de mise en scene fournie par Franco. Lue par le Chercheur
        # (A2) et le Designer (A6) : avant, une consigne de mise en scene
        # n'avait que `note_franco` comme porte d'entree, et n'atteignait le
        # Designer que par ricochet, recopiee dans la recherche puis le script.
        "reference": a.reference,
        "idees_max": a.idees,
    }
    if cp1_lot:
        st["etapes"]["CP1"].update({
            "statut": "valide",
            "commentaire": f"Validé en lot{(' — ' + semaine) if semaine else ''}",
            "date": now,
        })
    st["historique"] = [{
        "horodatage": now, "agent": "new_short", "evenement": "cree",
        "message": f"Vidéo créée (voie {voie}, mode {mode})",
    }]

    config = lire_json(racine / "01_Orchestrateur" / "config.json", {}) or {}
    prochaine = ("Recherche détaillée (Chercheur), puis passage direct au script — CP1 déjà validé en lot"
                 if cp1_lot else
                 "Recherche (Chercheur), puis CP1 : validation du sujet et de l'angle par Franco")

    if not a.dry_run:
        try:
            (dossier / "checkpoints").mkdir(exist_ok=True)
            ecrire_json_atomique(dossier / "state.json", st)
        except OSError as e:
            shutil.rmtree(dossier, ignore_errors=True)
            sortir(2, f"Écriture impossible, dossier nettoyé : {e}")

    sortir(0, "Simulation : rien n'a été écrit." if a.dry_run else "Vidéo créée.",
           video_id=video_id,
           chemin=str(dossier),
           fichiers_crees=[] if a.dry_run else [f"videos/{video_id}/state.json", f"videos/{video_id}/checkpoints/"],
           voie=voie, mode_recherche=mode, pilier=pilier,
           titre_travail=st["titre_travail"],
           format=a.format_video, reference=a.reference, idees_max=a.idees,
           sujet=sujet, angle=angle, sujet_id=sujet_id,
           cp1=st["etapes"]["CP1"]["statut"],
           prochaine_etape=prochaine,
           backlog_restant=max(len(disponibles) - (1 if cp1_lot and sujet_id in {s["sujet_id"] for s in disponibles} else 0), 0),
           orchestrateur_cmd=config.get("orchestrateur_cmd"))


if __name__ == "__main__":
    main()
