"""Scene images of a Whose Dime video by the Gemini API (S11).

    python3 whosedime/generate/images.py FOLDER --estimate          # price only, no call
    python3 whosedime/generate/images.py FOLDER --test              # 3 images at most (test budget)
    python3 whosedime/generate/images.py FOLDER --approved-usd 3.5  # the rest, within Franco's amount
    options: --scenes 1-14 (a range or list), --redo 9,12 (make again)

Reads the preamble and the `scene_NNN` prompts of `03_scenes.md` (one per `image` and
`video` scene; step4_scenes.md), and writes `images/scene_NNN.png` at 2K 16:9
(2752x1536, larger than the assembly's 1920x1080 plus its 10 % margin). One call per
image, the preamble's style sentences in front of the prompt. A prompt that says
"Same setting ... as scene_NNN" gets that image attached, so the place stays the same
(the Gemini chat did it by memory). An image already in the folder is kept (resume after
a failure); every paid call is a line of `generate/ledger.jsonl`.
"""
from __future__ import annotations

import argparse
import base64
import io
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gemini import SETTINGS, ApiError, Budget, BudgetError, Client, Ledger, jpeg_b64, media_parts, prompts, sha12, usage  # noqa: E402

REF_RE = re.compile(r"\bas scene_(\d{3})\b", re.I)


def parse_range(text):
    """'1-14' or '3,9,12' or '1-5,9' -> set of ints; None for an empty text."""
    if not text:
        return None
    out = set()
    for part in text.split(","):
        a, _, b = part.strip().partition("-")
        out |= set(range(int(a), int(b or a) + 1))
    return out


def todo(folder, p, scenes=None, redo=None, settings=SETTINGS):
    """Scene numbers to make, in order: each prompt without its PNG, plus the redo list."""
    d = Path(folder) / settings["images"]["dir"]
    out = []
    for n in sorted(p["scene"]):
        if scenes and n not in scenes:
            continue
        if (redo and n in redo) or not (d / f"scene_{n:03d}.png").exists():
            out.append(n)
    return out


def estimate(n_images, settings=SETTINGS):
    return round(n_images * settings["images"]["usd_per_image"], 2)


def payload(preamble, prompt, ref_b64=None, ref_n=None, settings=SETTINGS):
    s = settings["images"]
    text = f"{preamble}\n\n{prompt}"
    parts = [{"type": "text", "text": text}]
    if ref_b64:
        parts[0]["text"] += f"\n\nThe attached image is scene_{ref_n:03d}: keep its setting, light and style."
        parts.append({"type": "image", "mime_type": "image/jpeg", "data": ref_b64})
    return {"model": s["model"], "input": parts, "store": False,
            "response_format": {"type": "image", "mime_type": "image/png",
                                "aspect_ratio": s["aspect_ratio"], "image_size": s["image_size"]}}


def save_png(data, path, settings=SETTINGS):
    """Decode, check the size, write a PNG. Returns (width, height, warning or None)."""
    from PIL import Image
    im = Image.open(io.BytesIO(data)).convert("RGB")
    warn = None
    mw, mh = settings["images"]["min_px"]
    if im.width < mw or im.height < mh:
        warn = f"{im.width}x{im.height} is under {mw}x{mh}: enlarged"
        scale = max(mw / im.width, mh / im.height)
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".part.png")
    im.save(tmp, "PNG", optimize=True)
    tmp.replace(path)  # never a half-written image left under the real name
    return im.width, im.height, warn


def make(folder, client, budget, scenes=None, redo=None, log=print, settings=SETTINGS):
    """Generate the images; returns {'made': [...], 'failed': {n: reason}, 'stopped': reason or None}."""
    folder = Path(folder)
    p = prompts(folder)
    ledger = budget.ledger
    s = settings["images"]
    d = folder / s["dir"]
    result = {"made": [], "failed": {}, "stopped": None}
    streak = 0
    for n in todo(folder, p, scenes, redo, settings):
        prompt = p["scene"][n]
        m = REF_RE.search(prompt)
        ref_n = int(m.group(1)) if m else None
        ref = d / f"scene_{ref_n:03d}.png" if ref_n else None
        ref_b64 = jpeg_b64(ref, s["ref_max_px"]) if ref and ref.exists() else None
        usd = s["usd_per_image"] + (s["usd_per_input_image"] if ref_b64 else 0)
        try:
            budget.allow(usd)
        except BudgetError as e:
            result["stopped"] = str(e)
            log(f"⏸ stopped before scene_{n:03d}: {e}")
            break
        t = time.time()
        line = dict(kind="image", scene=n, model=s["model"], size=s["image_size"],
                    prompt_sha=sha12(prompt), ref=ref_n if ref_b64 else None)
        try:
            answer = client.interact(payload(p["preamble"], prompt, ref_b64, ref_n, settings), settings["api"]["timeout_image_s"])
            parts = media_parts(answer, "image")
            if not parts or not parts[0].get("data"):
                raise ApiError("no image in the answer")
            w, h, warn = save_png(base64.b64decode(parts[0]["data"]), d / f"scene_{n:03d}.png", settings)
        except (ApiError, ValueError, OSError) as e:
            # an answer without an image may still be billed: counted at the image price
            billed = isinstance(e, ApiError) and "no image" in str(e)
            ledger.add(**line, ok=billed, usd=round(usd, 4) if billed else 0, error=str(e)[:300],
                       seconds=round(time.time() - t, 1))
            result["failed"][n] = str(e)[:200]
            log(f"✗ scene_{n:03d}: {str(e)[:200]}")
            streak += 1
            if streak >= settings["api"]["stop_after_failures"]:
                result["stopped"] = f"{streak} failures in a row"
                log(f"⏸ stopped: {streak} failures in a row")
                break
            continue
        streak = 0
        budget.count()
        ledger.add(**line, ok=True, usd=round(usd, 4), file=f"{s['dir']}/scene_{n:03d}.png", px=[w, h],
                   seconds=round(time.time() - t, 1), usage=usage(answer), warning=warn)
        result["made"].append(n)
        log(f"✓ scene_{n:03d} {w}x{h} ${usd:.4f} {time.time() - t:.0f} s" + (f" ({warn})" if warn else ""))
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("folder")
    ap.add_argument("--estimate", action="store_true", help="price of what is left, no call")
    ap.add_argument("--test", action="store_true", help=f"{SETTINGS['budget']['test_images']} images at most")
    ap.add_argument("--approved-usd", type=float, default=SETTINGS["budget"]["approved_usd"])
    ap.add_argument("--scenes", default="")
    ap.add_argument("--redo", default="")
    a = ap.parse_args(argv)
    p = prompts(a.folder)
    left = todo(a.folder, p, parse_range(a.scenes), parse_range(a.redo))
    ledger = Ledger(a.folder)
    print(f"{len(p['scene'])} image prompts, {len(left)} to make: about ${estimate(len(left)):.2f} "
          f"at ${SETTINGS['images']['usd_per_image']} each ({SETTINGS['images']['model']}, "
          f"{SETTINGS['images']['image_size']}); spent so far ${ledger.spent():.2f}")
    if a.estimate or not left:
        return 0
    budget = Budget(ledger, a.approved_usd, SETTINGS["budget"]["test_images"] if a.test else None)
    r = make(a.folder, Client(), budget, parse_range(a.scenes), parse_range(a.redo))
    print(f"made {len(r['made'])}, failed {len(r['failed'])}, spent in all ${ledger.spent():.2f}")
    return 1 if r["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
