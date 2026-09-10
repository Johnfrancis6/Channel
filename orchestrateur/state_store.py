import json
import os
import tempfile
from datetime import datetime, timezone


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_state(video_dir):
    path = os.path.join(video_dir, "state.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(video_dir, state):
    path = os.path.join(video_dir, "state.json")
    fd, tmp_path = tempfile.mkstemp(dir=video_dir, prefix=".state.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def list_video_dirs(root):
    videos_dir = os.path.join(root, "videos")
    if not os.path.isdir(videos_dir):
        return []
    dirs = []
    for name in sorted(os.listdir(videos_dir)):
        video_dir = os.path.join(videos_dir, name)
        if os.path.isfile(os.path.join(video_dir, "state.json")):
            dirs.append(video_dir)
    return dirs


def ajouter_historique(state, agent, evenement, message):
    state.setdefault("historique", []).append({
        "horodatage": now_iso(),
        "agent": agent,
        "evenement": evenement,
        "message": message,
    })
