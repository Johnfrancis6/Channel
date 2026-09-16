#!/usr/bin/env python3
"""
lancer_voix_off.py — execute l'etape E4 (voix off) sur un runtime Colab,
depuis la machine de Franco ou depuis cron, sans ouvrir un navigateur.

Repose sur le **Colab CLI officiel** de Google (`pip install
google-colab-cli`, Linux et macOS uniquement). L'enchainement est celui
qu'un humain faisait a la main : allouer un GPU, monter le Drive, executer
le notebook, recuperer le journal, liberer la machine.

## Ce que ce script ne peut PAS faire tourner seul

`colab drivemount` monte le Drive avec un **jeton ephemere** : l'URL
d'autorisation porte `authorize-for-drive-credentials-ephem` et
`prompt=consent`, et le consentement est redemande **a chaque session**.
Autoriser une fois dans un notebook classique ne se reporte pas. Constate le
16/09/2026, apres trois runs echoues sur `ValueError: mount failed`.

Il n'y a donc pas de run entierement sans humain tant que le montage de Drive
est sur le chemin. Deux facons de vivre avec :

- **`--reprendre`** (ce script) : Franco cree la session et monte Drive
  lui-meme, une fois, puis le script prend la suite sur cette session vivante.
  Un clic par run, et tout le reste est automatique.
- **L'echange par fichiers**, pas encore ecrit : ne pas monter Drive du tout,
  pousser le script et la reference avec `colab upload`, recuperer les quatre
  sorties avec `colab download`, et ecrire `state.json` localement. La seule
  voie vers un run reellement sans humain — au prix de sortir la synthese du
  notebook.

## Ce qui decide du succes

**Pas le code de retour de `colab exec`.** Le notebook signale ses echecs
par `SystemExit` depuis une cellule ; rien ne garantit qu'un noyau Jupyter
distant traduise ca en code de sortie non nul, et la documentation du CLI
ne dit rien des codes de retour. S'y fier, c'est reproduire le defaut de
`capturer_web.py`, qui a valide trois fois une capture fausse parce que le
controle regardait la mauvaise chose.

Ce script conclut donc en **relisant le resultat sur le Drive** : le statut
de `E4_audio` dans `state.json`, et les quatre sorties attendues, non vides.
C'est la seule preuve qui ne depende pas d'une API non documentee.

## Codes de sortie

| 0 | audio produit et verifie |
| 1 | le run a eu lieu mais n'a pas abouti (statut ou sorties manquantes) |
| 2 | racine inutilisable — Drive non monte. Rien n'a ete lance |
| 3 | aucune video n'attend l'audio, ou plusieurs (choix ambigu) |
| 4 | `colab` absent du PATH, ou commande du CLI en echec |

Usage :
  python3 outils/lancer_voix_off.py --root /chemin/ChaineYouTube
  python3 outils/lancer_voix_off.py --root ... --video 2026-09-11_v01 --gpu L4
  python3 outils/lancer_voix_off.py --root ... --sans-drive   # sans aucun humain
  python3 outils/lancer_voix_off.py --root ... --reprendre --session voixoff
  python3 outils/lancer_voix_off.py --root ... --garder   # laisse la session ouverte
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parent.parent
NOTEBOOK = RACINE_DEPOT / "notebooks" / "voix_off.ipynb"

# Memes statuts que l'auto-detection de la Cell 1 du notebook : `attente_franco`
# (pret), `echec` (a reprendre), `en_cours` (run precedent coupe net).
STATUTS_CANDIDATS = ("attente_franco", "echec", "en_cours")

# Les quatre fichiers que E4 doit produire (§7.2). `04_phrases.json` est le
# plus important des quatre pour l'aval : c'est lui qui recale les scenes sur
# la voix, et la seule etape qui connaisse les bornes exactement.
SORTIES_ATTENDUES = (
    "04_voixoff.wav",
    "04_timestamps.json",
    "04_phrases.json",
    "04_rapport_audio.md",
)

# Le chemin du Drive **vu depuis la VM Colab**, qui n'est pas celui vu depuis
# la machine de Franco (Google Drive pour ordinateur, rclone, chemin arbitraire).
RACINE_VM = "/content/drive/MyDrive/ChaineYouTube"

# Le preambule ne fait que poser des variables d'environnement : il repond en
# une fraction de seconde. 120 s ne sert qu'a absorber une VM encore tiede.
TIMEOUT_PREAMBULE = 120


def attendre_miroir_local(racine, video_id, delai_s, journal):
    """Le montage (E6) lit le disque local, pas la VM : il faut que le miroir
    Drive ait redescendu les fichiers. Ce n'est PAS un critere de succes du
    run — seulement une commodite pour l'etape suivante."""
    fin = time.monotonic() + delai_s
    while True:
        ok, message = verifier_sorties(racine, video_id)
        if ok:
            return True, "miroir local a jour"
        if time.monotonic() >= fin:
            return False, message
        journal("miroir local pas encore a jour, nouvelle verification dans 15 s")
        time.sleep(15)


def _horodatage():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def verifier_racine(root):
    """(ok, message). Aucune ecriture — c'est tout l'interet de la fonction.

    Meme garde-fou que `lancer_orchestrateur.py` : un point de montage vide
    ressemble a s'y meprendre a une racine valide, et tout ce qu'on y ecrit
    masque le vrai Drive au remontage.
    """
    racine = Path(root)
    if not racine.is_dir():
        return False, f"racine introuvable : {racine} (Drive non monte ?)"
    if not (racine / "videos").is_dir():
        return False, f"pas de dossier videos/ sous {racine} (Drive non monte ?)"
    return True, "racine utilisable"


def _statut_audio(state):
    return (state.get("etapes", {}).get("E4_audio", {}) or {}).get("statut")


def lire_state(racine, video_id):
    chemin = Path(racine) / "videos" / video_id / "state.json"
    if not chemin.is_file():
        return None
    try:
        # utf-8-sig : les state.json edites sous Windows portent un BOM.
        return json.loads(chemin.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError):
        return None


def candidats_audio(racine):
    """Videos dont E4_audio attend un run. Meme regle que le notebook."""
    candidats = []
    dossier_videos = Path(racine) / "videos"
    if not dossier_videos.is_dir():
        return candidats
    for dossier in sorted(dossier_videos.iterdir()):
        state = lire_state(racine, dossier.name)
        if state is None:
            continue
        if _statut_audio(state) in STATUTS_CANDIDATS:
            candidats.append((state.get("video_id", dossier.name),
                              _statut_audio(state),
                              state.get("titre_travail", "")))
    return candidats


def choisir_video(racine, video_id):
    """(video_id, message). video_id vaut None quand il n'y a rien a faire."""
    if video_id:
        state = lire_state(racine, video_id)
        if state is None:
            return None, f"state.json introuvable ou illisible pour {video_id}"
        return video_id, f"video imposee : {video_id} (E4_audio={_statut_audio(state)})"

    candidats = candidats_audio(racine)
    if not candidats:
        return None, ("aucune video n'attend l'audio "
                      f"(E4_audio pas dans {STATUTS_CANDIDATS})")
    if len(candidats) > 1:
        lignes = ", ".join(f"{v} ({s})" for v, s, _ in candidats)
        return None, (f"choix ambigu, {len(candidats)} videos attendent l'audio : "
                      f"{lignes} — precise --video")
    vid, statut, _ = candidats[0]
    return vid, f"une seule video en attente : {vid} (E4_audio={statut})"


def verifier_sorties(racine, video_id):
    """(ok, message). Relit le resultat reel sur le Drive, apres le run."""
    dossier = Path(racine) / "videos" / video_id
    manquants = []
    for nom in SORTIES_ATTENDUES:
        chemin = dossier / nom
        if not chemin.is_file():
            manquants.append(f"{nom} (absent)")
        elif chemin.stat().st_size == 0:
            manquants.append(f"{nom} (vide)")
    if manquants:
        return False, "sorties manquantes : " + ", ".join(manquants)

    state = lire_state(racine, video_id)
    if state is None:
        return False, "state.json illisible apres le run"
    statut = _statut_audio(state)
    if statut != "termine":
        message = (state.get("etapes", {}).get("E4_audio", {}) or {}).get("message") or "(sans message)"
        return False, f"E4_audio = '{statut}' apres le run — {message}"
    return True, "audio produit, quatre sorties presentes, E4_audio = termine"


# Racine de travail sur le disque de la VM, quand on n'utilise pas Drive.
RACINE_VM_LOCALE = "/content/ChaineYouTube"

# Ce que le notebook LIT. Etabli en relisant ses cellules, pas en supposant :
# 03_script_tts.txt (Cell 4), state.json (Cell 0), et le profil de voix
# ref.wav + ref.txt (Cell 2, branche « voix existante »).
ENTREES_VIDEO = ("state.json", "03_script_tts.txt")
ENTREES_VOIX = ("ref.wav", "ref.txt")

# Ce qu'il ECRIT, en plus des quatre sorties : le rapport par tentative, et
# state.json qu'il met a jour.
NOM_DOSSIER_AUDIO = "audio"


def version_voix(racine, nom_voix):
    """Derniere version vN/ du profil de voix, ou None. Meme regle que la
    Cell 2 du notebook : les dossiers `v<entier>`, le plus grand gagne."""
    dossier = Path(racine) / "00_Profil" / "voix" / nom_voix
    if not dossier.is_dir():
        return None
    versions = [int(p.name[1:]) for p in dossier.iterdir()
                if p.is_dir() and p.name.startswith("v") and p.name[1:].isdigit()]
    return max(versions) if versions else None


def plan_transfert(racine, video_id, nom_voix, racine_vm):
    """(entrees, manquants) — les fichiers a televerser, en (local, distant).

    Fonction pure : c'est elle qui decide de ce que la VM verra, donc c'est
    elle qu'on teste. Un fichier oublie ici ne se verrait qu'au milieu d'un
    run, dans un message de cellule.
    """
    racine = Path(racine)
    entrees, manquants = [], []

    for nom in ENTREES_VIDEO:
        local = racine / "videos" / video_id / nom
        if local.is_file():
            entrees.append((local, f"{racine_vm}/videos/{video_id}/{nom}"))
        else:
            manquants.append(str(local))

    v = version_voix(racine, nom_voix)
    if v is None:
        manquants.append(f"{racine}/00_Profil/voix/{nom_voix}/v*/ (aucun profil de voix)")
    else:
        for nom in ENTREES_VOIX:
            local = racine / "00_Profil" / "voix" / nom_voix / f"v{v}" / nom
            if local.is_file():
                entrees.append((local, f"{racine_vm}/00_Profil/voix/{nom_voix}/v{v}/{nom}"))
            else:
                manquants.append(str(local))

    return entrees, manquants


def fusionner_state(local_path, distant_path):
    """Recopie E4_audio et l'historique neuf, sans toucher au reste.

    Rapatrier le state.json de la VM tel quel ecraserait ce que
    l'Orchestrateur aurait ecrit pendant le run. Le §4.2 est explicite : une
    etape ne touche qu'a elle-meme. On respecte la meme regle ici, du cote
    du transfert.
    """
    distant = json.loads(Path(distant_path).read_text(encoding="utf-8-sig"))
    if not Path(local_path).is_file():
        Path(local_path).write_text(json.dumps(distant, ensure_ascii=False, indent=2),
                                    encoding="utf-8")
        return "state.json cree depuis la VM (absent en local)"

    local = json.loads(Path(local_path).read_text(encoding="utf-8-sig"))
    local.setdefault("etapes", {})["E4_audio"] = distant.get("etapes", {}).get("E4_audio", {})

    # L'historique est append-only des deux cotes : on ajoute ce que la VM a
    # ecrit en plus, dans l'ordre, sans dedoublonner sur l'horodatage seul —
    # deux evenements peuvent tomber dans la meme seconde.
    h_local = local.get("historique", [])
    h_distant = distant.get("historique", [])
    nouveaux = h_distant[len(h_local):] if len(h_distant) > len(h_local) else []
    if nouveaux:
        local.setdefault("historique", []).extend(nouveaux)

    Path(local_path).write_text(json.dumps(local, ensure_ascii=False, indent=2),
                                encoding="utf-8")
    return f"state.json fusionne : E4_audio + {len(nouveaux)} evenement(s)"


MARQUEUR_VERDICT = "RESULTAT_E4"


def code_verification(racine_vm, video_id):
    """Le code qui juge le run, execute **sur la VM**.

    C'est la ou l'ecriture a eu lieu. Juger depuis la machine de Franco
    revenait a interroger un miroir Drive asynchrone : le 16/09/2026, un run
    parfaitement reussi — WER 1,47 %, `E4_audio = termine`, quatre fichiers
    ecrits — a ete declare en echec parce que les fichiers n'etaient pas
    encore redescendus dans `/mnt/g`.

    La sortie est une ligne machine prefixee par MARQUEUR_VERDICT. Son
    **absence** vaut echec : si le snippet n'a pas pu s'executer, on ne
    conclut pas au succes.
    """
    return (
        "import json, os\n"
        f"_d = {racine_vm + '/videos/' + video_id!r}\n"
        f"_attendues = {list(SORTIES_ATTENDUES)!r}\n"
        "_f = {}\n"
        "for _n in _attendues:\n"
        "    _p = os.path.join(_d, _n)\n"
        "    _f[_n] = os.path.getsize(_p) if os.path.isfile(_p) else None\n"
        "try:\n"
        "    _s = json.load(open(os.path.join(_d, 'state.json'), encoding='utf-8-sig'))\n"
        "    _e = (_s.get('etapes', {}).get('E4_audio', {}) or {})\n"
        "    _st, _msg = _e.get('statut'), _e.get('message')\n"
        "except Exception as _ex:\n"
        "    _st, _msg = None, f'state.json illisible : {_ex}'\n"
        f"print({MARQUEUR_VERDICT!r}, json.dumps("
        "{'statut': _st, 'message': _msg, 'fichiers': _f}))\n"
    )


def juger_verdict(sortie):
    """(ok, message) depuis la sortie brute du snippet. Fonction pure."""
    ligne = next((l for l in (sortie or "").splitlines()
                  if l.startswith(MARQUEUR_VERDICT)), None)
    if ligne is None:
        return False, ("verdict introuvable dans la sortie de la VM — le controle "
                       "n'a pas pu s'executer, on ne conclut pas au succes")
    try:
        d = json.loads(ligne[len(MARQUEUR_VERDICT):].strip())
    except json.JSONDecodeError as e:
        return False, f"verdict illisible : {e}"

    manquants = [f"{n} ({'vide' if t == 0 else 'absent'})"
                 for n, t in d.get("fichiers", {}).items() if not t]
    if manquants:
        return False, "sorties manquantes sur le Drive : " + ", ".join(manquants)
    statut = d.get("statut")
    if statut != "termine":
        return False, f"E4_audio = '{statut}' apres le run — {d.get('message') or '(sans message)'}"
    return True, "audio produit, quatre sorties presentes, E4_audio = termine"


# ── Le CLI Colab ─────────────────────────────────────────────────────────────

class ErreurColab(RuntimeError):
    """Une commande du CLI Colab a echoue. Distincte d'un run qui n'aboutit
    pas : ici c'est l'outil qui n'a pas repondu, pas la synthese qui a rate."""


def _colab(args, entree=None, timeout=None, journal=None):
    """Lance `colab ...`. Retourne le CompletedProcess, leve ErreurColab."""
    cmd = ["colab"] + args
    if journal is not None:
        journal(f"$ {' '.join(cmd)}")
    try:
        r = subprocess.run(cmd, input=entree, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        raise ErreurColab(
            "`colab` introuvable dans le PATH.\n"
            "   → uv tool install google-colab-cli\n"
            "     (le paquet exige Python >= 3.12 ; `pip install` sous un Python\n"
            "      plus ancien repond « No matching distribution found », ce qui\n"
            "      ressemble a tort a un paquet inexistant. `uv` recupere lui-meme\n"
            "      un interprete compatible.)\n"
            "   → Linux et macOS uniquement — sous Windows, passer par WSL.\n"
            "   → puis une premiere authentification interactive : colab new"
        )
    except subprocess.TimeoutExpired:
        raise ErreurColab(f"delai depasse ({timeout} s) sur : {' '.join(cmd)}")
    if journal is not None and (r.stdout or r.stderr):
        journal((r.stdout or "") + (r.stderr or ""))
    return r


def _preambule(video_id, mode, racine_vm, forcer):
    """Le code qui pose les parametres dans le noyau distant.

    La session Colab est un noyau Jupyter persistant : ce qu'une execution y
    pose, la suivante le retrouve. C'est ce qui permet de parametrer le
    notebook sans le reecrire — les variables d'environnement locales, elles,
    ne traversent pas jusqu'a la VM.
    """
    parametres = {
        "VOIX_VIDEO_ID": video_id,
        "VOIX_MODE": mode,
        "VOIX_RACINE": racine_vm,
        "VOIX_NON_INTERACTIF": "1",
        "VOIX_FORCER_RELANCE": "1" if forcer else "",
    }
    return (
        "import os\n"
        f"os.environ.update({parametres!r})\n"
        "print('parametres poses :', "
        "{k: v for k, v in os.environ.items() if k.startswith('VOIX_')})\n"
    )


def _monter_drive(session, journal):
    """`colab drivemount`, avec reprise sur la course DNS.

    C'est la premiere commande qui parle a la VM elle-meme, sur un nom d'hote
    cree a l'instant par `colab new`. Ce nom met quelques secondes a se
    propager : la resolution echoue alors avec « Temporary failure in name
    resolution » et le run est perdu pour une raison qui n'a rien a voir avec
    Drive. On lui laisse le temps.

    La reprise ne porte QUE sur des motifs reseau connus. Un `retry` aveugle
    masquerait le refus de consentement derriere quatre minutes d'attente.
    """
    for tentative in range(1, 5):
        r = _colab(["drivemount", "-s", session], timeout=600, journal=journal)
        if r.returncode == 0:
            return
        sortie = (r.stderr or r.stdout)
        transitoire = any(motif in sortie for motif in (
            "NameResolutionError", "Temporary failure in name resolution",
            "Max retries exceeded", "ConnectionError",
        ))
        if not transitoire or tentative == 4:
            raise ErreurColab(
                "`colab drivemount` a echoue : "
                f"{sortie.strip()[-400:]}\n"
                "   → Le montage utilise un jeton ephemere : le consentement est\n"
                "     redemande a CHAQUE session, et autoriser une fois ailleurs ne\n"
                "     se reporte pas. Monte Drive a la main, puis --reprendre :\n"
                f"       colab new -s {session} --gpu T4\n"
                f"       colab drivemount -s {session}   # ouvre l'URL, autorise, Entree"
            )
        journal(f"drivemount : erreur reseau transitoire, nouvelle tentative dans 15 s ({tentative}/4)")
        time.sleep(15)


def televerser_entrees(session, entrees, journal):
    """Cree l'arborescence sur la VM, puis y pousse les fichiers."""
    dossiers = sorted({d.rsplit("/", 1)[0] for _, d in entrees})
    code = "import os\n" + "".join(f"os.makedirs({d!r}, exist_ok=True)\n" for d in dossiers)
    r = _colab(["exec", "-s", session, "--timeout", str(TIMEOUT_PREAMBULE)],
               entree=code, timeout=300, journal=journal)
    if r.returncode != 0:
        raise ErreurColab(f"creation de l'arborescence impossible : {(r.stderr or r.stdout).strip()[-300:]}")

    for local, distant in entrees:
        r = _colab(["upload", "-s", session, str(local), distant],
                   timeout=900, journal=journal)
        if r.returncode != 0:
            raise ErreurColab(f"televersement de {local.name} impossible : "
                              f"{(r.stderr or r.stdout).strip()[-300:]}")
    journal(f"{len(entrees)} fichier(s) televerse(s) vers {dossiers[0].rsplit('/videos', 1)[0]}")


def rapatrier_sorties(session, racine, video_id, racine_vm, journal):
    """Ramene les sorties sur le disque de Franco. (ramenes, avertissements).

    `state.json` passe par un fichier temporaire puis une fusion : le
    recopier tel quel ecraserait ce que l'Orchestrateur aurait ecrit pendant
    le run.
    """
    dossier = Path(racine) / "videos" / video_id
    dossier.mkdir(parents=True, exist_ok=True)
    ramenes, avertissements = [], []

    for nom in SORTIES_ATTENDUES:
        r = _colab(["download", "-s", session,
                    f"{racine_vm}/videos/{video_id}/{nom}", str(dossier / nom)],
                   timeout=900, journal=journal)
        if r.returncode == 0:
            ramenes.append(nom)
        else:
            avertissements.append(f"{nom} : {(r.stderr or r.stdout).strip()[-200:]}")

    # Le rapport de tentative : son numero n'est pas connu d'avance, on
    # demande a la VM lequel elle vient d'ecrire.
    r = _colab(["exec", "-s", session, "--timeout", str(TIMEOUT_PREAMBULE)],
               entree=("import os\n"
                       f"_d = {racine_vm + '/videos/' + video_id + '/' + NOM_DOSSIER_AUDIO!r}\n"
                       "print('RAPPORTS', sorted(os.listdir(_d)) if os.path.isdir(_d) else [])\n"),
               timeout=300, journal=journal)
    ligne = next((l for l in (r.stdout or "").splitlines() if l.startswith("RAPPORTS")), "")
    for nom in re.findall(r"'([^']+\.md)'", ligne):
        cible = dossier / NOM_DOSSIER_AUDIO / nom
        cible.parent.mkdir(parents=True, exist_ok=True)
        rr = _colab(["download", "-s", session,
                     f"{racine_vm}/videos/{video_id}/{NOM_DOSSIER_AUDIO}/{nom}", str(cible)],
                    timeout=300, journal=journal)
        if rr.returncode == 0:
            ramenes.append(f"{NOM_DOSSIER_AUDIO}/{nom}")

    # state.json en dernier : c'est lui qui fait foi pour l'aval, et on ne le
    # touche qu'une fois les sorties bien arrivees.
    with tempfile.TemporaryDirectory() as tmp:
        provisoire = Path(tmp) / "state.json"
        r = _colab(["download", "-s", session,
                    f"{racine_vm}/videos/{video_id}/state.json", str(provisoire)],
                   timeout=300, journal=journal)
        if r.returncode != 0:
            avertissements.append(f"state.json non rapatrie : {(r.stderr or r.stdout).strip()[-200:]}")
        else:
            journal(fusionner_state(dossier / "state.json", provisoire))
            ramenes.append("state.json")

    return ramenes, avertissements


def executer_run(video_id, session, gpu, mode, racine_vm, forcer, garder,
                 chemin_journal, timeout_exec, journal, reprendre=False,
                 entrees=None, racine_locale=None):
    """Enchaine les commandes du CLI. Leve ErreurColab si l'outil echoue."""
    journal(f"session={session} gpu={gpu} mode={mode} video={video_id} reprendre={reprendre}")
    verdict = (False, "le run ne s'est pas rendu jusqu'au controle")

    if reprendre:
        # La session existe deja et son Drive est monte a la main. On ne la
        # recree pas et on ne remonte pas Drive : ce serait redemander le
        # consentement qu'on vient justement de donner.
        r = _colab(["status", "-s", session], timeout=120, journal=journal)
        if r.returncode != 0:
            raise ErreurColab(
                f"session '{session}' introuvable ou eteinte : "
                f"{(r.stderr or r.stdout).strip()[-300:]}\n"
                "   → cree-la et monte Drive a la main, puis relance :\n"
                f"       colab new -s {session} --gpu {gpu}\n"
                f"       colab drivemount -s {session}   # ouvre l'URL, autorise, Entree"
            )
        journal(f"session '{session}' reprise, Drive suppose deja monte")
    else:
        r = _colab(["new", "-s", session, "--gpu", gpu], timeout=600, journal=journal)
        if r.returncode != 0:
            sortie = (r.stderr or r.stdout)
            indice = ""
            # 412 : le compte a deja trop de runtimes. Sur Colab gratuit c'est
            # un seul GPU a la fois, et un run echoue avant `colab new` ne
            # nettoie rien — le suivant se heurte a l'orphelin sans que le
            # message dise ou regarder.
            if "TooManyAssignments" in sortie or "Precondition Failed" in sortie:
                indice = (
                    "\n   → Trop de runtimes actifs sur ce compte. Liste et libere :\n"
                    "       colab sessions\n"
                    "       colab stop -s <nom>\n"
                    "     Si la liste est vide et que l'erreur persiste, un runtime tourne\n"
                    "     cote Google sans etre connu du CLI : colab.research.google.com\n"
                    "     → Execution → Gerer les sessions → tout arreter."
                )
            raise ErreurColab(f"`colab new` a echoue : {sortie.strip()[-400:]}{indice}")

    try:
        if entrees is not None:
            # Sans Drive : les entrees montent par `colab upload`, les sorties
            # redescendent par `colab download`. Aucun consentement, donc
            # aucun humain — et le notebook tourne inchange, parce que sa
            # racine est deja un parametre.
            televerser_entrees(session, entrees, journal)
        elif not reprendre:
            _monter_drive(session, journal)

        r = _colab(["exec", "-s", session, "--timeout", str(TIMEOUT_PREAMBULE)],
                   entree=_preambule(video_id, mode, racine_vm, forcer),
                   timeout=300, journal=journal)
        if r.returncode != 0:
            raise ErreurColab(f"pose des parametres impossible : {(r.stderr or r.stdout).strip()[-400:]}")

        # Le long : synthese, transcription, controle WER. Son code de retour
        # n'est PAS ce qui decide du succes (voir l'en-tete du module).
        # `colab exec --timeout` vaut 30 s par defaut : c'est le delai
        # d'attente d'une sortie de cellule, pas celui du processus. Sans lui,
        # la premiere cellule un peu longue — installation des dependances,
        # chargement du modele — leve `TimeoutError: Timeout waiting for
        # output` au bout d'une demi-minute, et le run est perdu alors que la
        # machine, elle, continue de travailler. Le budget de la cellule est
        # donc celui du run.
        r = _colab(["exec", "-s", session, "-f", str(NOTEBOOK),
                    "--timeout", str(timeout_exec)],
                   timeout=timeout_exec + 120, journal=journal)
        journal(f"`colab exec` du notebook : code {r.returncode}")

        # Le journal de session est la seule trace de ce qui s'est dit dans
        # les cellules. On l'exporte avant de liberer la machine, sinon il
        # part avec elle.
        if chemin_journal is not None:
            chemin_journal.parent.mkdir(parents=True, exist_ok=True)
            rl = _colab(["log", "-s", session, "-o", str(chemin_journal)],
                        timeout=300, journal=journal)
            if rl.returncode != 0:
                journal(f"⚠️ export du journal Colab impossible : {(rl.stderr or rl.stdout).strip()[-200:]}")

        # Le verdict, pris sur la VM et AVANT l'arret de la session : une fois
        # la machine liberee, plus rien ne peut lire ce qu'elle a ecrit.
        rv = _colab(["exec", "-s", session, "--timeout", str(TIMEOUT_PREAMBULE)],
                    entree=code_verification(racine_vm, video_id),
                    timeout=300, journal=journal)
        verdict = juger_verdict((rv.stdout or "") + (rv.stderr or ""))

        if entrees is not None:
            # On rapatrie meme quand le verdict est negatif : le rapport audio
            # est precisement ce qui dit pourquoi, et il partirait avec la VM.
            ramenes, avertissements = rapatrier_sorties(
                session, racine_locale, video_id, racine_vm, journal)
            journal(f"rapatriement : {len(ramenes)} fichier(s) — {', '.join(ramenes) or 'aucun'}")
            for a in avertissements:
                journal(f"⚠️ {a}")
    finally:
        if garder:
            journal(f"session {session} laissee ouverte")
        else:
            rs = _colab(["stop", "-s", session], timeout=300, journal=journal)
            if rs.returncode != 0:
                # Une session qui survit coute du quota, mais le run, lui, a
                # peut-etre reussi : on le signale sans faire echouer.
                journal(f"⚠️ `colab stop` a echoue, session {session} peut-etre encore active")

    return verdict


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Execute E4 (voix off) sur un runtime Colab via le Colab CLI.")
    ap.add_argument("--root", required=True, help="Racine du dossier ChaineYouTube, vue localement.")
    ap.add_argument("--video", help="video_id. Par defaut : la seule qui attend l'audio.")
    ap.add_argument("--mode", default="full",
                    choices=("full", "resume_after_fail", "quality_check"),
                    help="MODE du notebook. 'voice_only' est exclu : il demande un upload interactif.")
    ap.add_argument("--gpu", default="T4", help="Accelerateur (T4, L4, A100, H100...). Defaut : T4.")
    ap.add_argument("--session", help="Nom de session Colab. Defaut : voixoff-<video_id>.")
    ap.add_argument("--racine-vm", default=RACINE_VM, dest="racine_vm",
                    help=f"Racine vue depuis la VM Colab. Defaut : {RACINE_VM}")
    ap.add_argument("--forcer", action="store_true",
                    help="Passe outre le plafond de tentatives et un statut deja 'termine'.")
    ap.add_argument("--sans-drive", action="store_true", dest="sans_drive",
                    help="Ne monte pas Drive : televerse les entrees sur la VM et rapatrie les "
                         "sorties. C'est le SEUL mode qui tourne sans humain, le montage de "
                         "Drive redemandant un consentement a chaque session.")
    ap.add_argument("--nom-voix", default="voix_principale", dest="nom_voix",
                    help="Profil de voix dans 00_Profil/voix/. Defaut : voix_principale.")
    ap.add_argument("--reprendre", action="store_true",
                    help="Reprendre une session deja creee et dont Drive est deja monte a la "
                         "main, au lieu d'en creer une. Seul mode qui fonctionne tant que le "
                         "montage de Drive redemande un consentement a chaque session.")
    ap.add_argument("--garder", action="store_true",
                    help="Ne pas arreter la session Colab a la fin. Implicite avec --reprendre : "
                         "l'arreter jetterait le consentement Drive donne a la main, et une "
                         "seconde tentative en redemanderait un.")
    ap.add_argument("--arreter", action="store_true",
                    help="Arreter la session meme en mode --reprendre.")
    ap.add_argument("--timeout", type=int, default=5400,
                    help="Budget du run du notebook, en secondes (defaut : 5400, soit 1 h 30). "
                         "Sert deux fois, avec deux sens : passe a `colab exec --timeout`, c'est "
                         "le silence maximal tolere entre deux sorties de cellule ; en local, "
                         "c'est la duree totale du processus, bornee 120 s plus haut pour que le "
                         "cote distant echoue le premier et laisse un message exploitable.")
    ap.add_argument("--attente-miroir", type=int, default=180, dest="attente_miroir",
                    help="Secondes d'attente pour que le miroir Drive local redescende les "
                         "sorties (defaut : 180). N'influe pas sur le code de sortie.")
    ap.add_argument("--verifier", action="store_true",
                    help="Dit ce qui serait lance, sans rien lancer.")
    a = ap.parse_args(argv)

    lignes_journal = []

    def journal(ligne):
        lignes_journal.append(ligne)
        print(ligne, flush=True)

    ok, message = verifier_racine(a.root)
    if not ok:
        print(f"❌ {message}", file=sys.stderr)
        return 2

    video_id, message = choisir_video(a.root, a.video)
    print(f"🔎 {message}")
    if video_id is None:
        return 3

    if a.sans_drive and a.reprendre:
        print("❌ --sans-drive et --reprendre s'excluent : le premier n'a pas besoin de la "
              "session preparee a la main que le second reprend.", file=sys.stderr)
        return 2

    # Sans Drive, la racine vue par la VM est un dossier de son disque, pas le
    # point de montage. L'option --racine-vm reste utilisable pour l'imposer.
    racine_vm = a.racine_vm
    if a.sans_drive and racine_vm == RACINE_VM:
        racine_vm = RACINE_VM_LOCALE

    entrees = None
    if a.sans_drive:
        entrees, manquants = plan_transfert(a.root, video_id, a.nom_voix, racine_vm)
        if manquants:
            print("❌ entrees introuvables, rien n'a ete lance :", file=sys.stderr)
            for m in manquants:
                print(f"   - {m}", file=sys.stderr)
            print("   → un profil de voix manquant s'enregistre une fois depuis Colab,\n"
                  "     avec MODE='voice_only'.", file=sys.stderr)
            return 2

    session = a.session or f"voixoff-{video_id}"
    dossier_video = Path(a.root) / "videos" / video_id
    chemin_journal = dossier_video / "audio" / f"journal_colab_{_horodatage().replace(':', '')}.md"

    if a.verifier:
        print(f"   session      : {session}")
        print(f"   gpu          : {a.gpu}")
        print(f"   mode         : {a.mode}")
        print(f"   notebook     : {NOTEBOOK}")
        print(f"   racine VM    : {racine_vm}")
        print(f"   sans Drive   : {'oui — ' + str(len(entrees)) + ' entrees a televerser' if a.sans_drive else 'non — Drive monte sur la VM'}")
        print(f"   journal      : {chemin_journal}")
        if a.sans_drive:
            demarrage = "session creee, entrees televersees, aucun montage"
        elif a.reprendre:
            demarrage = "session existante reprise, Drive deja monte"
        else:
            demarrage = "session creee, drivemount tente (consentement attendu)"
        print(f"   demarrage    : {demarrage}")
        print(f"   colab present: {'oui' if shutil.which('colab') else 'NON — uv tool install google-colab-cli'}")
        return 0

    try:
        # Une session reprise garde par defaut le consentement Drive qu'elle
        # porte : c'est la seule chose du run qui ait coute un geste humain.
        garder = (a.garder or a.reprendre) and not a.arreter
        ok, message = executer_run(video_id, session, a.gpu, a.mode, racine_vm,
                                   a.forcer, garder, chemin_journal, a.timeout,
                                   journal, a.reprendre, entrees, a.root)
    except ErreurColab as e:
        print(f"❌ {e}", file=sys.stderr)
        return 4

    if not ok:
        print(f"❌ {message}", file=sys.stderr)
        if chemin_journal.is_file():
            print(f"   → journal du run : {chemin_journal}", file=sys.stderr)
        print(f"   → rapport audio  : {dossier_video / '04_rapport_audio.md'}", file=sys.stderr)
        return 1

    print(f"✅ {message}")
    print(f"   journal du run : {chemin_journal}")

    # Le run est reussi ; reste a ce que le miroir Drive local redescende les
    # fichiers, parce que c'est lui que lira le montage. Un retard de
    # synchronisation n'est pas un echec du run et ne change pas le code de
    # sortie — le dire autrement ferait chercher un bug qui n'existe pas.
    if a.sans_drive:
        # Rien a attendre : les sorties ont ete ecrites directement sur le
        # disque local par `colab download`.
        return 0

    a_jour, detail = attendre_miroir_local(a.root, video_id, a.attente_miroir, journal)
    if not a_jour:
        print(f"⚠️  Produit sur Drive, pas encore redescendu en local apres "
              f"{a.attente_miroir} s : {detail}")
        print("   → le montage (E6) lit le disque local : attends la synchronisation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
