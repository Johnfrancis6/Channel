"""Scene clips of a Whose Dime video by the Gemini API, image to video (S11).

    python3 whosedime/generate/clips.py FOLDER --estimate
    python3 whosedime/generate/clips.py FOLDER --test               # 1 clip at most (test budget)
    python3 whosedime/generate/clips.py FOLDER --approved-usd 4.2   # the rest, within Franco's amount
    options: --scenes 1,47 --redo 47

For each `anim_NNN` prompt of `03_scenes.md` whose image `images/scene_NNN.png` exists,
asks Gemini Omni Flash (`gemini-omni-1.2-flash`; Veo 3.1 Preview was shut down in the
Gemini API on 2026-10-22) for an 8 s 1080p 16:9 clip that starts from the image, and
writes `clips/scene_NNN.mp4`. The image stays: if a clip fails, the assembly uses it.
The clip's sound is not used by the assembly. Resume, ledger and budget as images.py.
"""
from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gemini import SETTINGS, ApiError, Budget, BudgetError, Client, Ledger, jpeg_b64, media_parts, prompts, sha12, usage  # noqa: E402
from images import parse_range  # noqa: E402


def cost(settings=SETTINGS):
    c = settings["clips"]
    return round(c["duration_s"] * c["usd_per_second"], 4)


def todo(folder, p, scenes=None, redo=None, settings=SETTINGS):
    """(ready, missing_image): anim numbers to make whose image exists, and those still without one."""
    folder = Path(folder)
    ready, missing = [], []
    for n in sorted(p["anim"]):
        if scenes and n not in scenes:
            continue
        clip = folder / settings["clips"]["dir"] / f"scene_{n:03d}.mp4"
        if clip.exists() and not (redo and n in redo):
            continue
        img = folder / settings["images"]["dir"] / f"scene_{n:03d}.png"
        (ready if img.exists() else missing).append(n)
    return ready, missing


def payload(prompt, image_b64, settings=SETTINGS):
    c = settings["clips"]
    return {"model": c["model"], "store": False,
            "input": [{"type": "image", "mime_type": "image/jpeg", "data": image_b64},
                      {"type": "text", "text": prompt}],
            "response_format": {"type": "video", "resolution": c["resolution"],
                                "duration": f"{c['duration_s']}s", "aspect_ratio": c["aspect_ratio"],
                                "delivery": "uri"}}


def probe(path):
    """(duration_s, width, height) by ffprobe, or None if the file is not a video."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height:format=duration", "-of", "json", str(path)],
                       capture_output=True, text=True)
    try:
        j = json.loads(r.stdout)
        st = j["streams"][0]
        return round(float(j["format"]["duration"]), 2), st["width"], st["height"]
    except (ValueError, KeyError, IndexError):
        return None


def fetch(client, part, timeout):
    """The clip's bytes: inline base64, or its URI (delivery 'uri', for clips over 4 MB)."""
    if part.get("data"):
        return base64.b64decode(part["data"])
    uri = part.get("uri")
    if not uri:
        raise ApiError("no video data or uri in the answer")
    if "alt=media" not in uri:
        uri += ("&" if "?" in uri else "?") + "alt=media"
    return client.request("GET", uri, timeout=timeout)


def make(folder, client, budget, scenes=None, redo=None, log=print, settings=SETTINGS):
    folder = Path(folder)
    p = prompts(folder)
    c = settings["clips"]
    ready, missing = todo(folder, p, scenes, redo, settings)
    result = {"made": [], "failed": {}, "stopped": None, "no_image": missing}
    for n in missing:
        log(f"… anim_{n:03d}: images/scene_{n:03d}.png not made yet")
    streak = 0
    for n in ready:
        usd = cost(settings)
        try:
            budget.allow(usd)
        except BudgetError as e:
            result["stopped"] = str(e)
            log(f"⏸ stopped before anim_{n:03d}: {e}")
            break
        t = time.time()
        line = dict(kind="clip", scene=n, model=c["model"], size=c["resolution"], seconds_video=c["duration_s"],
                    prompt_sha=sha12(p["anim"][n]))
        out = folder / c["dir"] / f"scene_{n:03d}.mp4"
        try:
            img = jpeg_b64(folder / settings["images"]["dir"] / f"scene_{n:03d}.png", 1920)
            answer = client.interact(payload(p["anim"][n], img, settings), settings["api"]["timeout_clip_s"])
            parts = media_parts(answer, "video")
            if not parts:
                raise ApiError("no video in the answer")
            data = fetch(client, parts[0], settings["api"]["timeout_clip_s"])
            out.parent.mkdir(parents=True, exist_ok=True)
            tmp = out.with_suffix(".part.mp4")
            tmp.write_bytes(data)
            info = probe(tmp)
            if not info:
                tmp.unlink()
                raise ApiError("the answer is not a readable video")
            tmp.replace(out)
        except (ApiError, ValueError, OSError) as e:
            budget.ledger.add(**line, ok=False, usd=0, error=str(e)[:300], seconds=round(time.time() - t, 1))
            result["failed"][n] = str(e)[:200]
            log(f"✗ anim_{n:03d}: {str(e)[:200]}")
            streak += 1
            if streak >= settings["api"]["stop_after_failures"]:
                result["stopped"] = f"{streak} failures in a row"
                log(f"⏸ stopped: {streak} failures in a row")
                break
            continue
        streak = 0
        budget.count()
        budget.ledger.add(**line, ok=True, usd=usd, file=f"{c['dir']}/scene_{n:03d}.mp4", bytes=out.stat().st_size,
                          probe=list(info), seconds=round(time.time() - t, 1), usage=usage(answer))
        result["made"].append(n)
        log(f"✓ clip scene_{n:03d} {info[1]}x{info[2]} {info[0]} s ${usd:.2f} {time.time() - t:.0f} s")
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("folder")
    ap.add_argument("--estimate", action="store_true")
    ap.add_argument("--test", action="store_true", help=f"{SETTINGS['budget']['test_clips']} clip at most")
    ap.add_argument("--approved-usd", type=float, default=SETTINGS["budget"]["approved_usd"])
    ap.add_argument("--scenes", default="")
    ap.add_argument("--redo", default="")
    a = ap.parse_args(argv)
    p = prompts(a.folder)
    ready, missing = todo(a.folder, p, parse_range(a.scenes), parse_range(a.redo))
    ledger = Ledger(a.folder)
    n = len(ready) + len(missing)
    print(f"{len(p['anim'])} clip prompts, {n} to make ({len(missing)} still without their image): "
          f"about ${n * cost():.2f} at ${cost():.2f} each ({SETTINGS['clips']['model']}, "
          f"{SETTINGS['clips']['resolution']}, {SETTINGS['clips']['duration_s']} s); spent so far ${ledger.spent():.2f}")
    if a.estimate or not ready:
        return 0
    budget = Budget(ledger, a.approved_usd, SETTINGS["budget"]["test_clips"] if a.test else None)
    r = make(a.folder, Client(), budget, parse_range(a.scenes), parse_range(a.redo))
    print(f"made {len(r['made'])}, failed {len(r['failed'])}, spent in all ${ledger.spent():.2f}")
    return 1 if r["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
