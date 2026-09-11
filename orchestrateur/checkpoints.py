import os
import re

DECISION_RE = re.compile(
    r"##\s*D[ÉE]CISION\s*\n"
    r"Statut\s*:\s*(?P<statut>\S+)\s*(?:<!--.*?-->)?\s*\n"
    r"Commentaire\s*:\s*(?P<commentaire>.*)",
    re.IGNORECASE | re.DOTALL,
)


def chemin_rapport(video_dir, checkpoint_id):
    return os.path.join(video_dir, "checkpoints", f"rapport_{checkpoint_id}.md")


def lire_decision(video_dir, checkpoint_id):
    """Retourne {"statut": "EN_ATTENTE"|"VALIDE"|"REFUSE", "commentaire": str} ou None si le rapport n'existe pas."""
    path = chemin_rapport(video_dir, checkpoint_id)
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        contenu = f.read()
    match = DECISION_RE.search(contenu)
    if not match:
        return None
    statut = match.group("statut").strip().upper()
    commentaire = match.group("commentaire").strip()
    return {"statut": statut, "commentaire": commentaire or None}


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
