# Outils de relevé ponctuels (chaîne 2)

Scripts **d'analyse**, hors pipeline : ils ne sont appelés par aucun agent.
Ils servent à refaire les relevés de `docs/chaine2/` à une autre date.
Le jour où A3 doit les reprendre, on les intègre à
`agents/short-analyse-chaines/scripts/` (pas avant).

| Script | Rôle | Coût |
|---|---|---|
| `yt.py @handle…` | Toutes les vidéos d'une chaîne : durée, vues, likes, commentaires, localisations | API, ~1 unité par tranche de 50 vidéos |
| `profil.py @handle…` | Résumé d'une chaîne (médiane, cadence, top 3) à partir de `yt.py` | idem |
| `niches.py` | Recherche YouTube « vidéos de cette année », 2 requêtes EN et 2 FR par niche | yt-dlp, **pas de quota API**, mais YouTube renvoie 429 si on enchaîne trop |
| `transcription.sh <id>` | Sous-titres français en texte brut | yt-dlp, client `mweb` |

Prérequis : `YOUTUBE_API_KEY` (API Data v3), `pip install yt-dlp`.
Accès réseau nécessaires : `googleapis.com`, `youtube.com`, `i.ytimg.com`
(miniatures). `socialblade.com` reste refusé.

La recherche de l'API (`search.list`) coûte 100 unités sur 10 000 par jour :
préférer `niches.py` (yt-dlp) pour chercher, et l'API pour les statistiques.
