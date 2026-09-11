import os
import re
from datetime import datetime, timezone

DECISION_RE = re.compile(
    r"##\s*D[ÉE]CISION\s*\n"
    r"Statut\s*:\s*(?P<statut>\S+)\s*(?:<!--.*?-->)?\s*\n"
    r"Commentaire\s*:\s*(?P<commentaire>[^\n]*)",
    re.IGNORECASE | re.DOTALL,
)
# [^\n]* et non .* pour "commentaire" : avec re.DOTALL, ".*" capturait tout
# le reste du fichier (footer, instructions...) au lieu de la seule ligne.


def chemin_rapport(video_dir, checkpoint_id):
    return os.path.join(video_dir, "checkpoints", f"rapport_{checkpoint_id}.md")


def lire_decision(video_dir, checkpoint_id):
    """Retourne {"statut": "EN_ATTENTE"|"VALIDE"|"REFUSE", "commentaire": str} ou None si le rapport n'existe pas."""
    path = chemin_rapport(video_dir, checkpoint_id)
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8-sig") as f:
        contenu = f.read()
    match = DECISION_RE.search(contenu)
    if not match:
        return None
    statut = match.group("statut").strip().upper()
    commentaire = match.group("commentaire").strip()
    return {"statut": statut, "commentaire": commentaire or None}


def archiver_rapport_refuse(video_dir, checkpoint_id):
    """
    Deplace un rapport refuse vers checkpoints/refuses/ et retourne le chemin
    d'archive (ou None s'il n'y avait rien a archiver).

    Indispensable apres un refus : sans ca, generer_rapport_si_absent() voit
    l'ancien fichier, ne le regenere pas, et l'Orchestrateur relit
    indefiniment le meme "REFUSE" au lieu d'attendre une nouvelle decision.
    """
    path = chemin_rapport(video_dir, checkpoint_id)
    if not os.path.isfile(path):
        return None
    dossier_archive = os.path.join(video_dir, "checkpoints", "refuses")
    os.makedirs(dossier_archive, exist_ok=True)
    horodatage = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive = os.path.join(dossier_archive, f"rapport_{checkpoint_id}_{horodatage}.md")
    suffixe = 1
    while os.path.exists(archive):
        archive = os.path.join(dossier_archive, f"rapport_{checkpoint_id}_{horodatage}_{suffixe}.md")
        suffixe += 1
    os.replace(path, archive)
    return archive


def generer_rapport_si_absent(video_dir, checkpoint_id, resume):
    path = chemin_rapport(video_dir, checkpoint_id)
    if os.path.isfile(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    contenu = (
        f"# {checkpoint_id}\n\n"
        f"{resume}\n\n"
        "## DÉCISION\n"
        "Statut : EN_ATTENTE        <!-- remplacer par VALIDE ou REFUSE -->\n"
        "Commentaire :\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(contenu)
