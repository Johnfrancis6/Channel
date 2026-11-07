# Crayon Capital et concurrents : données (relevé du 2026-11-07)

Données du rapport [Crayon Capital et concurrents](../../reports/Crayon%20Capital%20et%20concurrents.md).

| Fichier | Contenu |
|---|---|
| `chaines.csv` | 23 chaînes : abonnés, médianes, rythme, durée, conversion, likes, commentaires, sponsors et autres revenus détectés dans les 20 dernières descriptions |
| `crayon_videos.csv` | Les 33 vidéos de Crayon Capital : vues, likes, durée, sponsor, document de sources |
| `commentaires_categories.csv` | 18 600 commentaires classés par expressions : part des commentaires et part des likes par catégorie, commentaires et réponses du créateur |
| `outils/` | Scripts de collecte (`s1.py` catalogues, `s2.py` recherche de concurrents, `s3.py` commentaires, `comp.py` tableau, `comments_an.py` catégories). Cache local dans `outils/cache/`, non versionné |

Coût : 895 unités de l'API YouTube Data v3, 12 transcriptions Supadata
(vidéos de Crayon : 6 hits, 6 flops). Les textes des commentaires et des
transcriptions ne sont pas versionnés ; seules les mesures le sont.
Changements de titres : comparaison avec le relevé du 2026-11-05
(`research_notes/Balayage niche C/`).
