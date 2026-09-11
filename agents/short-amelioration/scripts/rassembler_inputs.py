#!/usr/bin/env python3
"""
rassembler_inputs.py — liste les fichiers pertinents pour le rapport
hebdomadaire d'amelioration continue (§4.3, H1) : rapports de checkpoint,
metriques du Filtre TTS, rapports audio, exports YouTube Analytics.

Ne fait aucune analyse : c'est a l'agent (Claude) de lire ces fichiers et
d'identifier lui-meme les points faibles (§4.3 : "analyse ouverte").

Usage : python3 rassembler_inputs.py --root R [--jours 7]
"""
import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


def _modifie_recemment(chemin, seuil):
    return datetime.fromtimestamp(chemin.stat().st_mtime, timezone.utc) >= seuil


def rassembler(root, jours=7):
    seuil = datetime.now(timezone.utc) - timedelta(days=jours)
    root = Path(root)
    resultat = {"checkpoints": [], "metriques_filtre": [], "rapports_audio": [], "analytics_csv": []}

    videos_dir = root / "videos"
    if videos_dir.is_dir():
        for video_dir in sorted(p for p in videos_dir.iterdir() if p.is_dir()):
            checkpoints_dir = video_dir / "checkpoints"
            if checkpoints_dir.is_dir():
                for rapport in sorted(checkpoints_dir.glob("rapport_CP*.md")):
                    if _modifie_recemment(rapport, seuil):
                        resultat["checkpoints"].append(str(rapport))

            metriques = video_dir / "03_rapport_metriques.md"
            if metriques.is_file() and _modifie_recemment(metriques, seuil):
                resultat["metriques_filtre"].append(str(metriques))

            audio = video_dir / "04_rapport_audio.md"
            if audio.is_file() and _modifie_recemment(audio, seuil):
                resultat["rapports_audio"].append(str(audio))

    analytics_dir = root / "03_Amelioration" / "analytics"
    if analytics_dir.is_dir():
        resultat["analytics_csv"] = [str(p) for p in sorted(analytics_dir.glob("*.csv"))]

    return resultat


def main():
    ap = argparse.ArgumentParser(description="Liste les inputs du rapport hebdomadaire H1 (§4.3).")
    ap.add_argument("--root", required=True)
    ap.add_argument("--jours", type=int, default=7)
    a = ap.parse_args()

    print(json.dumps(rassembler(a.root, a.jours), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
