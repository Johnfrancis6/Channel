#!/usr/bin/env python3
"""Mesures YouTube pour les étapes 1 et 2 (Claude Code, avec YOUTUBE_API_KEY).

Deux usages :
  python3 youtube.py chaine @zelanstudio [--n 30]
      Les N dernières vidéos d'une chaîne : date, vues, titre (coût : ~2 unités).
  python3 youtube.py chercher "histoire du verre" [--langue fr] [--n 10]
      Les vidéos les plus vues sur une requête, avec leurs vues réelles
      (coût : ~101 unités, sur 10 000 par jour).

Sortie en Markdown, prête à coller dans Memoire/sujets.md. Chaque relevé
porte sa date : un nombre de vues sans date ne vaut rien.
Sans YOUTUBE_API_KEY, le script le dit et s'arrête : la skill se rabat
alors sur la recherche web, et marque la demande « non vérifiée ».
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import date


def api(point, **params):
    params["key"] = os.environ["YOUTUBE_API_KEY"]
    url = f"https://www.googleapis.com/youtube/v3/{point}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def details(ids):
    videos = []
    for i in range(0, len(ids), 50):
        rep = api("videos", part="snippet,statistics", id=",".join(ids[i:i + 50]))
        for v in rep["items"]:
            videos.append({
                "id": v["id"],
                "date": v["snippet"]["publishedAt"][:10],
                "chaine": v["snippet"]["channelTitle"],
                "titre": v["snippet"]["title"],
                "vues": int(v["statistics"].get("viewCount", 0)),
            })
    return videos


def chaine(handle, n):
    ref = {"id": handle} if handle.startswith("UC") else {"forHandle": handle}
    items = api("channels", part="contentDetails", **ref).get("items")
    if not items:
        sys.exit(f"Chaîne introuvable : {handle}")
    uploads = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    rep = api("playlistItems", part="contentDetails", playlistId=uploads,
              maxResults=min(n, 50))
    ids = [i["contentDetails"]["videoId"] for i in rep["items"]]
    return sorted(details(ids), key=lambda v: v["date"], reverse=True)


def chercher(requete, langue, n):
    rep = api("search", part="id", q=requete, type="video", order="viewCount",
              relevanceLanguage=langue, maxResults=min(n, 50))
    ids = [i["id"]["videoId"] for i in rep["items"]]
    return sorted(details(ids), key=lambda v: v["vues"], reverse=True)


def tableau(videos, titre):
    lignes = [f"### {titre} (relevé API du {date.today():%d/%m/%Y})", "",
              "| Date | Chaîne | Titre | Vues | Lien |", "|---|---|---|---|---|"]
    for v in videos:
        t = v["titre"].replace("|", "/")
        vues = f"{v['vues']:,}".replace(",", " ")
        lignes.append(f"| {v['date']} | {v['chaine']} | {t} | {vues} | https://youtu.be/{v['id']} |")
    return "\n".join(lignes)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sous = p.add_subparsers(dest="cmd", required=True)
    c = sous.add_parser("chaine")
    c.add_argument("handle")
    c.add_argument("--n", type=int, default=30)
    r = sous.add_parser("chercher")
    r.add_argument("requete")
    r.add_argument("--langue", default="fr")
    r.add_argument("--n", type=int, default=10)
    a = p.parse_args()

    if not os.environ.get("YOUTUBE_API_KEY"):
        sys.exit("YOUTUBE_API_KEY absente : demande non mesurable, marque-la « non vérifiée ».")
    if a.cmd == "chaine":
        print(tableau(chaine(a.handle, a.n), f"Dernières vidéos de {a.handle}"))
    else:
        print(tableau(chercher(a.requete, a.langue, a.n),
                      f"Les plus vues pour « {a.requete} » ({a.langue})"))


if __name__ == "__main__":
    main()
