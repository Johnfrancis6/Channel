#!/usr/bin/env python3
"""
stats_youtube.py — recupere les statistiques de chaines concurrentes via
l'API YouTube Data v3 (§4.3, A3 : "la voie stable"). Necessite une cle API
dans la variable d'environnement YOUTUBE_API_KEY (projet Google Cloud a
demander en audit tot, §11).

Les fonctions resumer_* sont pures (pas d'appel reseau) et testables avec
une reponse d'API en fixture.

Accepte trois formes pour designer une chaine, parce que c'est ce qu'on a
sous la main quand on la trouve : l'identifiant `UCxxxx`, le handle
`@nomdechaine`, ou l'URL complete. Les URLs modernes n'exposent plus
l'identifiant UC, et le convertir a la main pour chaque concurrent est
exactement le genre de friction qui fait qu'on ne remplit jamais la liste.

Usage :
  python3 stats_youtube.py --chaines UCxxxx @nomdechaine https://youtube.com/@autre
  python3 stats_youtube.py --chaines @nomdechaine --resoudre
Sortie : JSON sur stdout, une entree par chaine.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

API_BASE = "https://www.googleapis.com/youtube/v3"


RE_UC = re.compile(r"^UC[\w-]{20,}$")


def normaliser_reference(valeur):
    """(genre, valeur) ou genre vaut 'id', 'handle' ou 'pseudo'.

    Une URL `/channel/UCxxxx` porte l'identifiant ; `/@nom` porte un handle ;
    `/c/nom` ou `/user/nom` portent un ancien pseudo.
    """
    v = (valeur or "").strip()
    if not v:
        return None, v
    if v.startswith("http://") or v.startswith("https://"):
        chemin = urllib.parse.urlparse(v).path.strip("/")
        morceaux = [m for m in chemin.split("/") if m]
        if not morceaux:
            return None, v
        if morceaux[0] == "channel" and len(morceaux) > 1:
            v = morceaux[1]
        elif morceaux[0] in ("c", "user") and len(morceaux) > 1:
            return "pseudo", morceaux[1]
        else:
            v = morceaux[0]
    if RE_UC.match(v):
        return "id", v
    if v.startswith("@"):
        return "handle", v
    return "handle", "@" + v


def parametres_chaine(reference):
    """Parametre de channels.list correspondant a la reference donnee."""
    genre, valeur = normaliser_reference(reference)
    if genre == "id":
        return {"id": valeur}
    if genre == "pseudo":
        return {"forUsername": valeur}
    if genre == "handle":
        return {"forHandle": valeur}
    return None


def _get(endpoint, params, api_key):
    params = {**params, "key": api_key}
    url = f"{API_BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def resumer_reponse_chaine(data):
    """Extrait les stats utiles d'une reponse channels.list (part=snippet,statistics,contentDetails)."""
    items = data.get("items") or []
    if not items:
        return None
    item = items[0]
    stats = item.get("statistics", {})
    return {
        "channel_id": item.get("id"),
        "titre": (item.get("snippet") or {}).get("title"),
        "abonnes": int(stats["subscriberCount"]) if "subscriberCount" in stats else None,
        "vues_totales": int(stats["viewCount"]) if "viewCount" in stats else None,
        "nb_videos": int(stats["videoCount"]) if "videoCount" in stats else None,
        "uploads_playlist": (item.get("contentDetails") or {}).get("relatedPlaylists", {}).get("uploads"),
    }


def resumer_reponse_videos(data):
    """Extrait titre/vues/date d'une reponse videos.list (part=snippet,statistics)."""
    resultat = []
    for item in data.get("items") or []:
        stats = item.get("statistics", {})
        snippet = item.get("snippet", {})
        resultat.append({
            "video_id": item.get("id"),
            "titre": snippet.get("title"),
            "date_publication": snippet.get("publishedAt"),
            "vues": int(stats["viewCount"]) if "viewCount" in stats else None,
        })
    return resultat


def recuperer_chaine(reference, api_key, nb_videos=5):
    selecteur = parametres_chaine(reference)
    if selecteur is None:
        return {"reference": reference, "erreur": "reference de chaine illisible"}

    try:
        data = _get("channels", {"part": "snippet,statistics,contentDetails", **selecteur}, api_key)
    except urllib.error.HTTPError as e:
        # Une chaine en erreur ne doit jamais interrompre les autres (§4.3).
        return {"reference": reference, "erreur": f"HTTP {e.code} sur channels.list"}
    except OSError as e:
        return {"reference": reference, "erreur": f"reseau : {e}"}

    resume = resumer_reponse_chaine(data)
    if resume is None:
        return {"reference": reference, "erreur": "chaine introuvable"}
    resume["reference"] = reference

    videos = []
    playlist_id = resume.get("uploads_playlist")
    if playlist_id:
        pl = _get("playlistItems", {"part": "contentDetails", "playlistId": playlist_id,
                                     "maxResults": nb_videos}, api_key)
        ids = [it["contentDetails"]["videoId"] for it in pl.get("items", [])]
        if ids:
            vdata = _get("videos", {"part": "snippet,statistics", "id": ",".join(ids)}, api_key)
            videos = resumer_reponse_videos(vdata)

    resume["videos_recentes"] = videos
    return resume


def main():
    ap = argparse.ArgumentParser(description="Statistiques de chaines concurrentes (§4.3, A3).")
    ap.add_argument("--chaines", nargs="+", required=True,
                    help="Chaines : UCxxxx, @handle, ou URL complete")
    ap.add_argument("--videos-par-chaine", type=int, default=5)
    ap.add_argument("--resoudre", action="store_true",
                    help="Resout les references en channel_id et sort, sans recuperer les videos "
                         "— pour remplir 00_Profil/chaines_concurrentes.json")
    a = ap.parse_args()

    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print(json.dumps({"ok": False, "message": "YOUTUBE_API_KEY non definie."}))
        sys.exit(2)

    nb_videos = 0 if a.resoudre else a.videos_par_chaine
    resultats = [recuperer_chaine(c, api_key, nb_videos) for c in a.chaines]

    if a.resoudre:
        # Forme directement collable dans chaines_concurrentes.json.
        print(json.dumps(
            [{"channel_id": r["channel_id"], "nom": r.get("titre")}
             for r in resultats if not r.get("erreur")]
            + [{"reference": r.get("reference"), "erreur": r["erreur"]}
               for r in resultats if r.get("erreur")],
            ensure_ascii=False, indent=2))
        return

    print(json.dumps({"ok": True, "chaines": resultats}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
