#!/usr/bin/env python3
"""
generer_rapport.py — assemble 02_Veille_hebdo/{AAAA-Sxx}_analyse_concurrentielle.md
a partir des stats recuperees par stats_youtube.py (§4.3, A3).

Les analyses de structure, tirees des transcriptions quand elles sont
disponibles, sont fournies a part : c'est la partie fragile du pipeline
(§4.3), un echec de transcription ne doit jamais bloquer le rapport de
stats.

Elles arrivent desormais **mesurees et par video** (`--analyses`, lignes
produites par outils/analyser_transcription.py), plus en prose libre
indexee par chaine. La prose n'etait ni comparable ni cumulable : ecraser
cinq videos dans une phrase detruisait l'information avant de l'ecrire.
`--notes` reste accepte pour ce qui ne se mesure pas.

Usage :
  python3 generer_rapport.py --stats stats.json --semaine 2026-S37 \
      [--analyses corpus_structures.jsonl] [--notes notes.json] \
      --sortie 2026-S37_analyse_concurrentielle.md
"""
import argparse
import json


def _mediane(valeurs):
    if not valeurs:
        return None
    ordonnees = sorted(valeurs)
    m = len(ordonnees) // 2
    return ordonnees[m] if len(ordonnees) % 2 else round((ordonnees[m - 1] + ordonnees[m]) / 2, 1)


def synthese_structures(analyses):
    """Ce que les videos analysees ont en commun — la seule chose qui se
    transpose. Une moyenne sur une video ne veut rien dire ; c'est le
    cumul, semaine apres semaine, qui finit par dire quelque chose."""
    if not analyses:
        return []
    m = [a.get("metriques", {}) for a in analyses]
    debits = [x["mots_par_seconde"] for x in m if x.get("mots_par_seconde")]
    hooks = [x["hook_duree_s"] for x in m if x.get("hook_duree_s")]
    idees = [x["nb_idees"] for x in m if x.get("nb_idees") is not None]
    par_idee = [x["mots_par_idee_moyen"] for x in m if x.get("mots_par_idee_moyen")]
    durees = [x["duree_s"] for x in m if x.get("duree_s")]
    avec_cta = sum(1 for x in m if x.get("cta_present"))
    avec_sponso = sum(1 for x in m if x.get("sponsoring_present"))

    lignes = [
        "## Structure — ce que disent les videos analysees",
        "",
        f"Sur **{len(analyses)} video(s)** analysee(s) cette semaine.",
        "",
        "| Mesure | Mediane |",
        "|---|---|",
        f"| Duree | {_mediane(durees)} s |",
        f"| Debit | {_mediane(debits)} mots/s |",
        f"| Duree du hook | {_mediane(hooks)} s |",
        f"| Nombre d'idees | {_mediane(idees)} |",
        f"| Mots par idee | {_mediane(par_idee)} |",
        f"| CTA present | {avec_cta}/{len(analyses)} |",
        f"| Sponsoring | {avec_sponso}/{len(analyses)} |",
        "",
        "Ces valeurs alimentent les budgets de format (§8). Elles ne valent",
        "rien sur une semaine : c'est leur accumulation dans",
        "`corpus_structures.jsonl` qui finit par les rendre fiables.",
        "",
    ]
    return lignes


def rendre(chaines, semaine, notes, analyses=None):
    notes = notes or {}
    lignes = [f"# Analyse concurrentielle — {semaine}", ""]
    lignes += synthese_structures(analyses or [])

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

        analysees = [a for a in (analyses or []) if a.get("chaine") == c.get("channel_id")]
        if analysees:
            lignes.append("- Videos analysees :")
            for a in analysees:
                m = a.get("metriques", {})
                lignes.append(
                    f"  - {a.get('titre') or a.get('video_id')} — {m.get('duree_s')} s, "
                    f"{m.get('nb_idees')} idee(s), hook {m.get('hook_duree_s')} s, "
                    f"{m.get('mots_par_seconde')} mots/s"
                    + (", CTA" if m.get("cta_present") else "")
                    + (", sponsorisee" if m.get("sponsoring_present") else "")
                )
        else:
            lignes.append("- Aucune video analysee (transcription indisponible).")

        note = notes.get(c.get("channel_id"))
        if note:
            lignes.append(f"- Note qualitative : {note}")
        lignes.append("")

    return "\n".join(lignes)


def main():
    ap = argparse.ArgumentParser(description="Genere le rapport hebdomadaire d'analyse concurrentielle (§4.3, A3).")
    ap.add_argument("--stats", required=True, help="Fichier JSON produit par stats_youtube.py (cle 'chaines')")
    ap.add_argument("--semaine", required=True, help="Ex: 2026-S37")
    ap.add_argument("--notes", help="JSON optionnel {channel_id: note qualitative texte}")
    ap.add_argument("--analyses", help="corpus_structures.jsonl : une ligne par video mesuree")
    ap.add_argument("--sortie", required=True)
    a = ap.parse_args()

    with open(a.stats, encoding="utf-8-sig") as f:
        data = json.load(f)
    chaines = data.get("chaines", data if isinstance(data, list) else [])

    notes = None
    if a.notes:
        with open(a.notes, encoding="utf-8-sig") as f:
            notes = json.load(f)

    analyses = []
    if a.analyses:
        with open(a.analyses, encoding="utf-8-sig") as f:
            analyses = [json.loads(l) for l in f if l.strip()]

    contenu = rendre(chaines, a.semaine, notes, analyses)
    with open(a.sortie, "w", encoding="utf-8") as f:
        f.write(contenu)

    print(json.dumps({"ok": True, "sortie": a.sortie, "nb_chaines": len(chaines),
                      "nb_videos_analysees": len(analyses)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
