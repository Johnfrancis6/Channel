#!/usr/bin/env python3
"""
lancer_voix_off.py — execute l'etape E4 (voix off) sur un runtime Colab,
depuis la machine de Franco ou depuis cron, sans ouvrir un navigateur.

Repose sur le **Colab CLI officiel** de Google (`pip install
google-colab-cli`, Linux et macOS uniquement). L'enchainement est celui
qu'un humain faisait a la main : allouer un GPU, monter le Drive, executer
le notebook, recuperer le journal, liberer la machine.

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
  python3 outils/lancer_voix_off.py --root ... --garder   # laisse la session ouverte
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
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
            "   → pip install google-colab-cli  (Linux et macOS uniquement)\n"
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


def executer_run(video_id, session, gpu, mode, racine_vm, forcer, garder,
                 chemin_journal, timeout_exec, journal):
    """Enchaine les commandes du CLI. Leve ErreurColab si l'outil echoue."""
    journal(f"session={session} gpu={gpu} mode={mode} video={video_id}")

    r = _colab(["new", "-s", session, "--gpu", gpu], timeout=600, journal=journal)
    if r.returncode != 0:
        raise ErreurColab(f"`colab new` a echoue : {(r.stderr or r.stdout).strip()[-400:]}")

    try:
        r = _colab(["drivemount", "-s", session], timeout=600, journal=journal)
        if r.returncode != 0:
            raise ErreurColab(
                "`colab drivemount` a echoue : "
                f"{(r.stderr or r.stdout).strip()[-400:]}\n"
                "   → si Drive demande un consentement navigateur, monte-le une\n"
                "     premiere fois a la main depuis Colab avec ce meme compte."
            )

        r = _colab(["exec", "-s", session],
                   entree=_preambule(video_id, mode, racine_vm, forcer),
                   timeout=300, journal=journal)
        if r.returncode != 0:
            raise ErreurColab(f"pose des parametres impossible : {(r.stderr or r.stdout).strip()[-400:]}")

        # Le long : synthese, transcription, controle WER. Son code de retour
        # n'est PAS ce qui decide du succes (voir l'en-tete du module).
        r = _colab(["exec", "-s", session, "-f", str(NOTEBOOK)],
                   timeout=timeout_exec, journal=journal)
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
    finally:
        if garder:
            journal(f"session {session} laissee ouverte (--garder)")
        else:
            rs = _colab(["stop", "-s", session], timeout=300, journal=journal)
            if rs.returncode != 0:
                # Une session qui survit coute du quota, mais le run, lui, a
                # peut-etre reussi : on le signale sans faire echouer.
                journal(f"⚠️ `colab stop` a echoue, session {session} peut-etre encore active")


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
    ap.add_argument("--garder", action="store_true",
                    help="Ne pas arreter la session Colab a la fin (diagnostic).")
    ap.add_argument("--timeout", type=int, default=5400,
                    help="Delai maximal du run du notebook, en secondes. Defaut : 5400 (1 h 30).")
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

    session = a.session or f"voixoff-{video_id}"
    dossier_video = Path(a.root) / "videos" / video_id
    chemin_journal = dossier_video / "audio" / f"journal_colab_{_horodatage().replace(':', '')}.md"

    if a.verifier:
        print(f"   session      : {session}")
        print(f"   gpu          : {a.gpu}")
        print(f"   mode         : {a.mode}")
        print(f"   notebook     : {NOTEBOOK}")
        print(f"   racine VM    : {a.racine_vm}")
        print(f"   journal      : {chemin_journal}")
        print(f"   colab present: {'oui' if shutil.which('colab') else 'NON — pip install google-colab-cli'}")
        return 0

    try:
        executer_run(video_id, session, a.gpu, a.mode, a.racine_vm, a.forcer,
                     a.garder, chemin_journal, a.timeout, journal)
    except ErreurColab as e:
        print(f"❌ {e}", file=sys.stderr)
        return 4

    ok, message = verifier_sorties(a.root, video_id)
    if not ok:
        print(f"❌ {message}", file=sys.stderr)
        if chemin_journal.is_file():
            print(f"   → journal du run : {chemin_journal}", file=sys.stderr)
        print(f"   → rapport audio  : {dossier_video / '04_rapport_audio.md'}", file=sys.stderr)
        return 1

    print(f"✅ {message}")
    print(f"   journal du run : {chemin_journal}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
