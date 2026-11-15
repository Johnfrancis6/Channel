import json, os, sys, urllib.request, urllib.parse, re, hashlib
from pathlib import Path
CACHE = Path(__file__).parent / "cache"; CACHE.mkdir(exist_ok=True)
KEY = os.environ["YOUTUBE_API_KEY"]
UNITS = {"search": 100}
used = [0]
def get(ep, **p):
    h = hashlib.md5((ep + json.dumps(p, sort_keys=True)).encode()).hexdigest()
    f = CACHE / f"{ep}_{h}.json"
    if f.exists():
        return json.loads(f.read_text())
    q = urllib.parse.urlencode(dict(p, key=KEY))
    try:
        with urllib.request.urlopen(f"https://www.googleapis.com/youtube/v3/{ep}?{q}", timeout=30) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300].replace(KEY, "***")
        raise SystemExit(f"HTTP {e.code} on {ep}: {body}")
    used[0] += UNITS.get(ep, 1)
    f.write_text(json.dumps(d))
    return d
