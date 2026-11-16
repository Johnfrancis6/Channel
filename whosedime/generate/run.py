"""One command per Whose Dime video: the pieces, then the render, then a status file (S11).

    python3 whosedime/generate/run.py FOLDER                      # status only, no paid call
    python3 whosedime/generate/run.py FOLDER --test               # + 3 test images and 1 test clip
    python3 whosedime/generate/run.py FOLDER --approved-usd 8     # + every missing image and clip
    options: --no-render (stop after the charts), --work DIR (render on a local disk first)

Chains what works, in order, and never pays without being told to (D18):

| Step | Runs when | Otherwise |
|---|---|---|
| images | `--test` or `--approved-usd`, and the Gemini key answers (free model list) | waiting: Franco makes them in Gemini, or gives a key |
| clips | same, for each clip whose image exists | waiting: Flow by Franco |
| voice | never here: read from `voice/state.json` (the voice notebook in Colab, D6: Franco listens to the 20 s sample first) | — |
| charts | `03_scenes.md` and `02b_factcheck.md` exist | — |
| render | every image, the voice `ready`: `assemble.py FOLDER` | `assemble.py --plan --no-files` when the voice timings exist |

Writes `generate/status.json`: one entry per step (`status` in the words of `00_state.md`:
not started, in progress, waiting for Franco, done, failed), counts, money spent, and the
next action. The skill `whosedime-maker` copies its Pieces, Voice and Render rows from it.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import clips as clips_mod  # noqa: E402
import images as images_mod  # noqa: E402
from gemini import REPO, SETTINGS, Budget, Client, Ledger, checker, now, prompts  # noqa: E402

VIDEO = REPO / "whosedime" / "whosedime-video" / "scripts"


def count(folder, sub, ext, numbers):
    d = Path(folder) / sub
    return sum((d / f"scene_{n:03d}{ext}").exists() for n in numbers)


def commit():
    r = subprocess.run(["git", "-C", str(REPO), "log", "-1", "--format=%h"], capture_output=True, text=True)
    return r.stdout.strip() or None


def voice_state(folder):
    """(status for 00_state.md, detail) from the voice notebook's own files."""
    v = Path(folder) / "voice"
    try:
        st = json.loads((v / "state.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        st = None
    if st:
        s = st.get("status")
        if s == "ready":
            return "done", f"voice/state.json ready, {st.get('rate_total_wpm', '?')} wpm"
        if s == "running":
            return "in progress", f"voice/state.json running {st.get('progress', {})}"
        return "failed", f"voice/state.json {s}: {st.get('error')}"
    if (v / "listen_20s.json").exists():
        return "waiting for Franco", "20 s sample made: Franco listens, ticks I_LISTENED, runs MODE = 'full' in Colab"
    return "not started", "voice notebook in Colab: MODE = 'sample' first (D6)"


def run_script(args, log):
    r = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)
    tail = (r.stdout + r.stderr).strip().splitlines()[-3:]
    for line in tail:
        log("   " + line)
    return r.returncode, " / ".join(tail)[-300:]


def generate(folder, kind, mod, args, client, ledger, log):
    """Run images or clips when money is allowed and the key answers; returns its result or a reason."""
    if not (args.test or args.approved_usd):
        return None, "no paid call asked (--test or --approved-usd)"
    if not client.check_key():
        return None, "no working Gemini key (GEMINI_API_KEY or the session proxy)"
    limit = SETTINGS["budget"][f"test_{kind}"] if args.test else None
    return mod.make(folder, client, Budget(ledger, args.approved_usd, limit), log=log), None


def run(folder, args, client=None, log=print):
    folder = Path(folder)
    client = client or Client()
    ledger = Ledger(folder)
    st = {"updated": now(), "commit": commit(), "video": folder.name, "steps": {}}
    steps = st["steps"]
    if not (folder / checker.SETTINGS["files"]["scenes"]).exists():
        steps["scenes"] = {"status": "not started", "detail": "03_scenes.md missing (whosedime-maker step 4)"}
        return finish(folder, st, ledger, "Step 4 of whosedime-maker: 03_scenes.md", log)
    p = prompts(folder)

    # images, then clips (a clip starts from its image)
    for kind, mod, sub, ext, need in (("images", images_mod, "images", ".png", sorted(p["scene"])),
                                      ("clips", clips_mod, "clips", ".mp4", sorted(p["anim"]))):
        res, why = generate(folder, kind, mod, args, client, ledger, log)
        have = count(folder, sub, ext, need)
        e = {"have": have, "of": len(need)}
        if have == len(need):
            e["status"] = "done"
        elif res and res["failed"]:
            e.update(status="failed", failed=res["failed"])
        else:
            e["status"] = "in progress" if have else "not started"
        e["detail"] = why or (res and res.get("stopped")) or ""
        steps[kind] = e
        log(f"{kind}: {have} of {len(need)} — {e['status']}" + (f" ({e['detail']})" if e["detail"] else ""))

    vs, vd = voice_state(folder)
    steps["voice"] = {"status": vs, "detail": vd}
    log(f"voice: {vs} ({vd})")

    types = p["types"]
    chart_n = [n for n, t in types.items() if t == "chart"]
    code, detail = run_script([VIDEO / "charts.py", folder], log)
    have = count(folder, "charts", ".png", chart_n)
    steps["charts"] = {"status": "done" if code == 0 and have == len(chart_n) else "failed",
                       "have": have, "of": len(chart_n), "detail": "" if code == 0 else detail}
    log(f"charts: {have} of {len(chart_n)}")

    img_ok = steps["images"]["status"] == "done"
    if args.no_render:
        steps["render"] = {"status": "not started", "detail": "--no-render"}
    elif img_ok and vs == "done" and steps["charts"]["status"] == "done":
        extra = ["--work", args.work] if args.work else []
        code, detail = run_script([VIDEO / "assemble.py", folder, *extra], log)
        verdict = folder / "render" / "verdict_video.json"
        ready = verdict.exists() and json.loads(verdict.read_text(encoding="utf-8")).get("ready")
        steps["render"] = {"status": "done" if ready else "failed", "detail": "render/verdict_video.json " +
                           ("ready" if ready else f"not ready: {detail}")}
    elif (folder / "voice" / "words.json").exists():
        code, detail = run_script([VIDEO / "assemble.py", folder, "--plan", "--no-files"], log)
        steps["render"] = {"status": "not started", "detail": f"plan only (exit {code}): pieces or voice missing"}
    else:
        steps["render"] = {"status": "not started", "detail": "needs every image and the voice"}
    log(f"render: {steps['render']['status']} ({steps['render']['detail']})")

    if not img_ok:
        nxt = "Images: Franco makes them in Gemini (batches of 03_scenes.md), or agrees a budget for the API"
    elif steps["clips"]["status"] != "done":
        nxt = "Clips: Flow by Franco, or the API with an agreed budget (a missing clip uses its image)"
    elif vs != "done":
        nxt = "Voice: " + vd
    elif steps["render"]["status"] != "done":
        nxt = "Render: assembly launcher in Colab, MODE = 'full'"
    else:
        nxt = "Publication: Franco checks the render and publishes"
    return finish(folder, st, ledger, nxt, log)


def finish(folder, st, ledger, nxt, log):
    st["next"] = nxt
    st["spent_usd"] = ledger.spent()
    st["paid_calls"] = sum(1 for l in ledger.lines() if l.get("ok"))
    out = Path(folder) / SETTINGS["files"]["dir"] / SETTINGS["files"]["status"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(st, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"next: {nxt}")
    log(f"status: {out}")
    return st


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("folder")
    ap.add_argument("--test", action="store_true", help="test budget: 3 images, 1 clip")
    ap.add_argument("--approved-usd", type=float, default=0.0, help="the amount Franco agreed for this video")
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--work", help="assemble.py --work (render on a local disk, then copy)")
    st = run(ap.parse_args(argv).folder, ap.parse_args(argv))
    return 1 if any(s.get("status") == "failed" for s in st["steps"].values()) else 0


if __name__ == "__main__":
    sys.exit(main())
