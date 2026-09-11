#!/usr/bin/env python3
"""
generer_rapport.py — assemble 02_Veille_hebdo/{AAAA-Sxx}_analyse_concurrentielle.md
a partir des stats recuperees par stats_youtube.py (§4.3, A3).

Les notes qualitatives (hooks, CTA, structure), tirees des transcriptions
quand elles sont disponibles, sont fournies a part : c'est la partie
fragile du pipeline (§4.3), un echec de transcription ne doit jamais
bloquer le rapport de stats.

Usage :
  python3 generer_rapport.py --stats stats.json --semaine 2026-S37 \
      [--notes notes.json] --sortie 2026-S37_analyse_concurrentielle.md
"""
import argparse
import json


def rendre(chaines, semaine, notes):
    notes = notes or {}
    lignes = [f"# Analyse concurrentielle — {semaine}", ""]

    for c in chaines:
        titre = c.get("titre") or c.get("channel_id")
        lignes.append(f"## {titre} (`{c.get('channel_id')}`)")
        if c.get("erreur"):
            lignes.append(f"- Erreur : {c['erreur']}")
            lignes.append("")
            continue

        lignes.append(f"- Abonnes : {c.get('abonnes', 'inconnu')}")
        lignes.append(f"- Vues totales : {c.get('vues_totales', 'inconnu')}")
        lignes.append(f"- Nombre de videos : {c.get('nb_videos', 'inconnu')}")

        videos = c.get("videos_recentes") or []
        if videos:
            lignes.append("- Videos recentes :")
            for v in videos:
                lignes.append(f"  - {v.get('titre')} — {v.get('vues', '?')} vues ({v.get('date_publication', '?')})")

        note = notes.get(c.get("channel_id"))
        lignes.append("- Notes qualitatives (hooks, CTA, structure) :")
        lignes.append(f"  {note}" if note else "  Transcriptions indisponibles pour cette chaine.")
        lignes.append("")

    return "\n".join(lignes)


def main():
    ap = argparse.ArgumentParser(description="Genere le rapport hebdomadaire d'analyse concurrentielle (§4.3, A3).")
    ap.add_argument("--stats", required=True, help="Fichier JSON produit par stats_youtube.py (cle 'chaines')")
    ap.add_argument("--semaine", required=True, help="Ex: 2026-S37")
    ap.add_argument("--notes", help="JSON optionnel {channel_id: note qualitative texte}")
    ap.add_argument("--sortie", required=True)
    a = ap.parse_args()

    with open(a.stats, encoding="utf-8-sig") as f:
        data = json.load(f)
    chaines = data.get("chaines", data if isinstance(data, list) else [])

    notes = None
    if a.notes:
        with open(a.notes, encoding="utf-8-sig") as f:
            notes = json.load(f)

    contenu = rendre(chaines, a.semaine, notes)
    with open(a.sortie, "w", encoding="utf-8") as f:
        f.write(contenu)

    print(json.dumps({"ok": True, "sortie": a.sortie, "nb_chaines": len(chaines)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
