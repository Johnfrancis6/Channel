#!/usr/bin/env bash
# Sous-titres français d'une vidéo YouTube, sans cookies, depuis un conteneur.
# Le client « mweb » passe la vérification anti-robot ; --ignore-no-formats-error
# évite l'échec sur les formats vidéo, qu'on ne télécharge pas.
# Usage : transcription.sh <video_id> [dossier]   ->  <dossier>/<id>.txt
# Limite : YouTube renvoie 429 après quelques dizaines de requêtes ; attendre.
set -euo pipefail
id="$1"; dir="${2:-.}"; mkdir -p "$dir"
yt-dlp -q --skip-download --ignore-no-formats-error --write-auto-subs --write-subs \
  --sub-langs "fr-orig,fr" --sub-format json3 \
  --extractor-args "youtube:player_client=mweb" -o "$dir/%(id)s" \
  "https://www.youtube.com/watch?v=$id"
f=$(ls "$dir/$id".fr-orig.json3 "$dir/$id".fr.json3 2>/dev/null | head -1)
python3 - "$f" "$dir/$id.txt" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
t = "".join(s.get("utf8", "") for e in d.get("events", []) for s in (e.get("segs") or []))
open(sys.argv[2], "w").write(" ".join(t.replace("\n", " ").split()))
PY
echo "$dir/$id.txt"
