#!/usr/bin/env python3
"""
stats_youtube.py — recupere les statistiques de chaines concurrentes via
l'API YouTube Data v3 (§4.3, A3 : "la voie stable"). Necessite une cle API
dans la variable d'environnement YOUTUBE_API_KEY (projet Google Cloud a
demander en audit tot, §11).

Les fonctions resumer_* sont pures (pas d'appel reseau) et testables avec
une reponse d'API en fixture.

Usage :
  python3 stats_youtube.py --chaines UCxxxx UCyyyy [--videos-par-chaine 5]
Sortie : JSON sur stdout, une entree par chaine.
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

API_BASE = "https://www.googleapis.com/youtube/v3"


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


def recuperer_chaine(channel_id, api_key, nb_videos=5):
    data = _get("channels", {"part": "snippet,statistics,contentDetails", "id": channel_id}, api_key)
    resume = resumer_reponse_chaine(data)
    if resume is None:
        return {"channel_id": channel_id, "erreur": "chaine introuvable"}

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
    ap.add_argument("--chaines", nargs="+", required=True, help="Identifiants de chaine YouTube (UC...)")
    ap.add_argument("--videos-par-chaine", type=int, default=5)
    a = ap.parse_args()

    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print(json.dumps({"ok": False, "message": "YOUTUBE_API_KEY non definie."}))
        sys.exit(2)

    resultats = [recuperer_chaine(c, api_key, a.videos_par_chaine) for c in a.chaines]
    print(json.dumps({"ok": True, "chaines": resultats}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
