"""A short Whose Dime video folder for the assembly tests (S07): 10 scenes cut from the Uber eval run,
generated images, a generated clip and a stub voice (tone bursts timed like words).

    make_folder(tmp) -> Path of the folder

The 10 scenes are Uber scenes 1, 2, 5, 7, 8, 9, 11, 18, 20, 21 renumbered 1 to 10: a clip, images,
four charts, the title card and a chapter card. The script is their spoken text; the voice version
says the numbers in words, as the real one does; the registry is the eval's.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
UBER = ROOT / "whosedime" / "whosedime-maker" / "evals" / "files" / "01_uber"
sys.path.insert(0, str(ROOT / "whosedime" / "common"))
sys.path.insert(0, str(ROOT / "whosedime" / "notebooks"))
import checker  # noqa: E402
import voice_whosedime as vw  # noqa: E402

PICK = [1, 2, 5, 7, 8, 9, 11, 18, 20, 21]
SPELL = [("2008", "two thousand eight"), ("41 percent", "forty-one percent"),
         ("May 31, 2010", "May thirty-first, twenty ten"), ("$2 billion", "two billion dollars"),
         ("$1.4 billion", "one point four billion dollars"), ("September 2015", "September twenty fifteen"),
         ("June 1, 2016", "June first, twenty sixteen"), ("$3.5 billion", "three point five billion dollars")]
SCENE_COLS = checker.SETTINGS["scenes"]["columns"]
VISUALS = checker.SETTINGS["scenes"]["visuals"]


def uber_rows():
    rows, _ = checker.scene_table(checker.norm((UBER / "03_scenes.md").read_text(encoding="utf-8")))
    return {int(r["n"]): r for _, r in rows}


def uber_prompts():
    return checker.scene_prompts(checker.norm((UBER / "03_scenes.md").read_text(encoding="utf-8")))


def write_scenes(folder, rows):
    prompts = uber_prompts()
    lines = ["# Scenes — test \"Uber, ten scenes\"", "", "## Scenes", "",
             "| " + " | ".join(SCENE_COLS) + " |", "|" + "---|" * len(SCENE_COLS)]
    gemini, flow = ["## Gemini prompts", ""], ["## Flow clips", ""]
    for new, old in enumerate(PICK, 1):
        r = dict(rows[old], n=str(new))
        r["visual"] = VISUALS[r["type"]].format(n=new)
        lines.append("| " + " | ".join(r[c] for c in SCENE_COLS) + " |")
        if r["type"] in ("image", "video"):
            gemini += [f"**scene_{new:03d}** — *test*", f"> {prompts['scene'][old][1]}", ""]
        if r["type"] == "video":
            flow += [f"**anim_{new:03d}** — *test*", f"> {prompts['anim'][old][1]}", ""]
    (folder / "03_scenes.md").write_text("\n".join(lines + [""] + gemini + flow) + "\n", encoding="utf-8")


def spoken(rows):
    return [rows[n]["spoken text"] for n in PICK if rows[n]["type"] not in ("title", "chapter")]


def voice_line(text):
    for written, said in SPELL:
        text = text.replace(written, said)
    return text


def make_images(folder, rows):
    (folder / "images").mkdir()
    for new, old in enumerate(PICK, 1):
        if rows[old]["type"] in ("image", "video"):
            im = Image.new("RGB", (1600, 900), (60 + 17 * new, 90, 140 - 9 * new))
            d = ImageDraw.Draw(im)
            for k in range(0, 1600, 80):
                d.line((k, 0, k + 400, 900), fill=(240, 220, 190), width=6)
            d.ellipse((650, 300, 950, 600), fill=(231, 179, 62))
            im.save(folder / "images" / f"scene_{new:03d}.png")


def make_clip(folder, n, seconds=3):
    (folder / "clips").mkdir(exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc=size=1280x720:rate=24:duration={seconds}",
                    "-pix_fmt", "yuv420p", str(folder / "clips" / f"scene_{n:03d}.mp4")], check=True)


def make_voice(folder, lines, word_s=0.16, sr=24000):
    """voice/voice.wav, words.json and state.json like the S06 notebook writes them, with tone bursts for words."""
    out = folder / "voice"
    out.mkdir()
    rng = np.random.default_rng(7)
    parts, words, t = [], [], 0.0
    for b, line in enumerate(lines, 1):
        for w in vw.spoken_words(line):
            dur = word_s + 0.012 * len(w)
            n = int(dur * sr)
            tone = 0.25 * np.sin(2 * np.pi * (180 + 40 * (len(w) % 5)) * np.arange(n) / sr)
            tone += 0.03 * rng.standard_normal(n)
            tone *= np.hanning(n)
            gap = int(0.05 * sr)
            parts += [tone.astype(np.float32), np.zeros(gap, np.float32)]
            words.append({"n": len(words) + 1, "word": w, "start_s": round(t, 3), "end_s": round(t + dur, 3),
                          "block": b, "sentence": b, "timed": "heard"})
            t += dur + gap / sr
        pause = int(0.6 * sr)
        parts.append(np.zeros(pause, np.float32))
        t += pause / sr
    audio = np.concatenate(parts)
    vw.write_wav(out / "voice.wav", audio, sr)
    duration = round(len(audio) / sr, 3)
    vw.write_json(out / "words.json", {"video": folder.name, "duration_s": duration, "sample_rate": sr,
                                       "made": "2026-11-07T00:00:00Z", "voice": "stub", "blocks": [], "words": words})
    vw.write_json(out / "state.json", {"status": "ready", "outputs": ["voice.wav", "words.json"]})
    return duration


def make_folder(tmp, clip=True):
    folder = Path(tmp) / "Videos" / "99_test"
    folder.mkdir(parents=True)
    rows = uber_rows()
    shutil.copy(UBER / "02b_factcheck.md", folder / "02b_factcheck.md")
    texts = spoken(rows)
    (folder / "02_script.md").write_text("# Test script\n\n" + "\n\n".join(texts) + "\n", encoding="utf-8")
    voice_lines = [voice_line(t) for t in texts]
    (folder / "02_script_voice.txt").write_text("\n\n".join(voice_lines) + "\n", encoding="utf-8")
    write_scenes(folder, rows)
    make_images(folder, rows)
    if clip:
        make_clip(folder, 1)
    make_voice(folder, voice_lines)
    return folder
