#!/usr/bin/env python3
"""Whose Dime assembly (build session S07): a video folder into render/video.mp4.

    python3 assemble.py FOLDER                 # the whole video
    python3 assemble.py FOLDER --scenes 1-10   # an extract: render/extract_001-010.mp4
    python3 assemble.py FOLDER --plan          # gate, charts, timing and chapters only, no render
    python3 assemble.py FOLDER --plan --no-files   # the same without images and clips (they are in Drive)

FOLDER holds `03_scenes.md`, `02_script.md`, `02_script_voice.txt`,
`02b_factcheck.md`, `images/`, `clips/` and the voice of the S06 notebook
(`voice/voice.wav`, `voice/words.json`, `voice/state.json`).

1. **Gate** (decision D4): the checker's `scenes` and `voice` targets must
   pass (no [TO VERIFY] fact used, a signed registry unchanged since its
   signature, scenes equal to the script word for word); the voice is `ready`.
2. **Charts**: `charts.py` redraws every chart from `02b_factcheck.md`
   (a refused chart stops the assembly: never a stale or unsourced chart).
3. **Timing**: each spoken scene is found in `words.json` (the voice
   version's words, numbers said in words and respellings matched back, as
   the voice notebook matches Whisper); a scene starts in the pause before
   its first word. A `title` or `chapter` card adds 2.5 s of silence.
4. **Render**: images with one of four slow motions, charts, Flow clips
   (slowed, then frozen, if short; the scene's image if the clip is missing),
   cards drawn from the on-screen text, on-screen keywords, crossfades;
   sound at -14 LUFS. 1920x1080, 30 fps.
5. **Technical check** (size, audio, no silence, no clipping, duration).

Outputs, in FOLDER/render/, **named after the output** (audit P3: an
extract never overwrites the whole video's verdict):

    <name>.mp4  report_<name>.json  verdict_<name>.json  preview_<name>/   (name: video, extract_001-010)
    chapters.txt  plan.json   (whole video and --plan only)

The verdict carries `<branch>@<commit>` of the code (audit C3): `main@...` in Colab.
Every number lives in ../settings.json; colours in whosedime/common/palette.json.
Needs numpy, opencv-python(-headless), Pillow, ffmpeg and ffprobe.
"""
from __future__ import annotations

import argparse
import bisect
import difflib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import charts  # noqa: E402  (also puts the repo's checker on the path)
from charts import PAL, REPO, SETTINGS, checker, font, mix, wrap  # noqa: E402

sys.path.insert(0, str(REPO / "whosedime" / "notebooks"))
import voice_whosedime as vw  # noqa: E402  (norm_tokens: the voice notebook's own word matching)

CARDS = set(checker.SETTINGS["scenes"]["cards"])


class AssemblyError(Exception):
    """The assembly stops: the message says why and what to do."""


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def minutes(t):
    return f"{int(t // 60)}:{int(t % 60):02d}"


# ------------------------------------------------------------------ scenes and gate
@dataclass
class Scene:
    n: int
    type: str
    text: str
    motion: str
    on_screen: str
    chart: str
    image: Path | None = None
    clip: Path | None = None
    tokens: int = 0
    coverage: float = 1.0
    voice_start: float = 0.0
    voice_end: float = 0.0
    start: float = 0.0
    end: float = 0.0
    warnings: list = field(default_factory=list)

    @property
    def card(self):
        return self.type in CARDS

    @property
    def duration(self):
        return self.end - self.start


def empty(cell):
    return checker.empty(cell)


def load_scenes(folder):
    """Scenes of 03_scenes.md, read with the checker's parser (one parser)."""
    path = Path(folder) / checker.SETTINGS["files"]["scenes"]
    rows, error = checker.scene_table(checker.norm(path.read_text(encoding="utf-8")))
    if error:
        raise AssemblyError(f"{path.name} line {error[0]}: {error[1]}")
    out = []
    for _, r in rows:
        out.append(Scene(int(r["n"]), r["type"].lower(), "" if empty(r["spoken text"]) else r["spoken text"],
                         r["motion"], "" if empty(r["on-screen text"]) else r["on-screen text"],
                         "" if empty(r["chart"]) else r["chart"]))
    return out


def gate(folder):
    """Decision D4: the checker must let the scenes and the voice version through; the voice must be ready."""
    folder, files = Path(folder), checker.SETTINGS["files"]
    for name in ("scenes", "script", "voice", "facts"):
        if not (folder / files[name]).is_file():
            raise AssemblyError(f"{files[name]} is missing from {folder}")
    reports = [checker.check_scenes(folder / files["scenes"], folder / files["script"], folder / files["facts"]),
               checker.check_voice(folder / files["script"], folder / files["voice"], folder / files["facts"])]
    blocks = [f"{r.target}: {msg}" for r in reports for _, _, msg in r.blocks]
    if blocks:
        raise AssemblyError("The checker blocks the assembly (decision D4):\n- " + "\n- ".join(blocks[:12]))
    state_path = folder / SETTINGS["files"]["voice_state"]
    warnings = []
    if state_path.is_file():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if state.get("status") != "ready":
            raise AssemblyError(f"The voice is '{state.get('status')}', not ready ({state_path}): run the voice notebook.")
        dry = [b for b in state.get("blocks", []) if isinstance(b, dict) and b.get("flagged_dry")]
        if dry or state.get("flagged_dry"):
            warnings.append("voice: dry endings flagged in state.json, listen before publishing")
    else:
        warnings.append(f"no {state_path.name}: voice readiness not checked")
    return warnings


def find_file(folder, sub, n, exts):
    for ext in exts:
        p = Path(folder) / sub / f"scene_{n:03d}{ext}"
        if p.is_file():
            return p
    return None


def attach_files(scenes, folder, only=None, need=True):
    """Image of every image and video scene, clip of video scenes (optional: the image replaces it),
    chart of chart scenes. Returns (missing, warnings)."""
    f = SETTINGS["files"]
    missing, warnings = [], []
    for s in scenes:
        if only and not only[0] <= s.n <= only[1]:
            continue
        if s.type in ("image", "video"):
            s.image = find_file(folder, "images", s.n, f["image_exts"])
            if s.image is None:
                missing.append(f"images/scene_{s.n:03d}.png")
        if s.type == "video":
            s.clip = find_file(folder, "clips", s.n, f["clip_exts"])
            if s.clip is None and s.image is not None:
                warnings.append(f"scene {s.n}: no clip, its image is used (zoom_in)")
        if s.type == "chart":
            s.image = find_file(folder, "charts", s.n, [".png"])
            if s.image is None:
                missing.append(f"charts/scene_{s.n:03d}.png")
    return (missing if need else []), warnings


# ------------------------------------------------------------------ timing
def load_words(folder):
    path = Path(folder) / SETTINGS["files"]["words"]
    if not path.is_file():
        raise AssemblyError(f"{path} is missing: run the voice notebook (MODE = 'full') first.")
    data = json.loads(path.read_text(encoding="utf-8"))
    words = data.get("words") or []
    if not words:
        raise AssemblyError(f"{path} holds no word.")
    duration = float(data.get("duration_s") or words[-1]["end_s"])
    return words, duration


def align(scenes, words, duration, lexicon=None):
    """Voice start and end of every spoken scene, found in words.json; coverage = share of its words matched."""
    lexicon = vw.load_lexicon() if lexicon is None else lexicon
    spoken = [s for s in scenes if not s.card]
    s_tok, s_own = [], []
    for k, s in enumerate(spoken):
        toks = vw.norm_tokens(checker.TAG_RE.sub("", s.text), lexicon)
        s.tokens = len(toks)
        s_tok += toks
        s_own += [k] * len(toks)
    v_tok, v_own = [], []
    for j, w in enumerate(words):
        toks = vw.norm_tokens(w["word"], lexicon) or [w["word"].lower()]
        v_tok += toks
        v_own += [j] * len(toks)
    match = [None] * len(s_tok)
    for a, b, size in difflib.SequenceMatcher(None, s_tok, v_tok, autojunk=False).get_matching_blocks():
        for i in range(size):
            match[a + i] = v_own[b + i]
    # a time for every script token: matched ones from the voice, the others interpolated by position
    t_start = [words[m]["start_s"] if m is not None else None for m in match]
    t_end = [words[m]["end_s"] if m is not None else None for m in match]
    known = [i for i, t in enumerate(t_start) if t is not None]
    if not known:
        raise AssemblyError("No word of 03_scenes.md was found in words.json: is it the voice of this script?")
    for i in range(len(s_tok)):
        if t_start[i] is None:
            left = max((k for k in known if k < i), default=None)
            right = min((k for k in known if k > i), default=None)
            lt = t_end[left] if left is not None else 0.0
            rt = t_start[right] if right is not None else duration
            li = left if left is not None else -1
            ri = right if right is not None else len(s_tok)
            u = (i - li) / (ri - li)
            t_start[i] = lt + (rt - lt) * u
            t_end[i] = t_start[i]
    pos = 0
    for s in spoken:
        rng = range(pos, pos + s.tokens)
        pos += s.tokens
        if not rng:
            s.coverage = 0.0
            continue
        s.coverage = sum(match[i] is not None for i in rng) / len(rng)
        s.voice_start, s.voice_end = t_start[rng[0]], t_end[rng[-1]]
    return spoken


def timeline(scenes, duration, S=SETTINGS):
    """Video start and end of every scene; the card insertions [(voice time, seconds)]; the total length."""
    tm = S["timing"]
    spoken = [s for s in scenes if not s.card]
    cuts = [0.0]
    for prev, nxt in zip(spoken, spoken[1:]):
        cut = max(prev.voice_end, nxt.voice_start - tm["cut_lead_s"])
        cuts.append(min(max(cut, cuts[-1]), duration))
    cuts.append(duration)
    insertions, cursor, k = [], 0.0, 0
    for s in scenes:
        if s.card:
            s.start, s.end = cursor, cursor + tm["card_s"]
            insertions.append((cuts[k], tm["card_s"]))
        else:
            s.start, s.end = cursor, cursor + (cuts[k + 1] - cuts[k])
            k += 1
        cursor = s.end
    scenes[-1].end += tm["end_hold_s"]
    return insertions, scenes[-1].end


def scene_warnings(scenes, S=SETTINGS):
    tm = S["timing"]
    out = []
    for s in scenes:
        if not s.card and s.coverage < tm["coverage_min"]:
            out.append(f"scene {s.n}: found at {s.coverage:.0%} in the voice (03_scenes.md and the voice differ?)")
        if s.type in ("image", "chart") and s.duration > tm["image_max_s"]:
            out.append(f"scene {s.n}: a still for {s.duration:.1f} s (cut it in two?)")
        if s.duration < 1.0:
            out.append(f"scene {s.n}: only {s.duration:.1f} s on screen")
    return out


def chapter_labels(folder, scenes):
    """Labels of the chapters: 04_publication.md's '--:-- Label' lines when they match the cards, else the card text."""
    cards = [s for s in scenes if s.card]
    first = SETTINGS["chapters"]["first_label"]
    labels = [first] + [s.on_screen.capitalize() for s in cards]
    pub = Path(folder) / checker.SETTINGS["files"]["publication"]
    if pub.is_file():
        found = re.findall(r"^\s*(?:0:00|--:--)\s+(.+?)\s*$", pub.read_text(encoding="utf-8"), re.M)
        if len(found) == len(cards) + 1:
            labels = found
    return labels


def chapters(folder, scenes, total):
    """['0:00 Cold open', '0:45 Who pays?', ...] and the warnings of YouTube's rules."""
    ch = SETTINGS["chapters"]
    cards = [s for s in scenes if s.card]
    starts = [0.0] + [s.start for s in cards]
    labels = chapter_labels(folder, scenes)
    lines = [f"{minutes(t)} {label}" for t, label in zip(starts, labels)]
    warnings = []
    if len(lines) < ch["min_count"]:
        warnings.append(f"chapters: {len(lines)}, YouTube needs at least {ch['min_count']}")
    for (t, label), nxt in zip(zip(starts, labels), starts[1:] + [total]):
        if nxt - t < ch["min_s"]:
            warnings.append(f"chapter '{label}' lasts {nxt - t:.1f} s, YouTube needs {ch['min_s']} s")
    return lines, warnings


# ------------------------------------------------------------------ pictures
def read_rgb(path, w, h):
    """An image (or a video's first frame) resized to cover w x h, centred."""
    im = Image.open(path).convert("RGB")
    scale = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * scale)), max(h, round(im.height * scale))), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return np.asarray(im.crop((x, y, x + w, y + h)))


def card_image(scene, w, h):
    """A title card (navy, the series name) or a chapter card (cream, the chapter), drawn from palette.json."""
    title = scene.type == "title"
    bg, ink = (PAL["ink"], PAL["background"]) if title else (PAL["background"], PAL["ink"])
    im = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(im)
    k = w / 1920
    f = font(round((170 if title else 104) * k))
    lines = wrap(d, scene.on_screen, f, w * 0.8)
    while len(lines) > 2 and f.size > 40:
        f = font(f.size - 8)
        lines = wrap(d, scene.on_screen, f, w * 0.8)
    step = f.size * 1.12
    y = h / 2 - step * len(lines) / 2
    for line in lines:
        d.text((w / 2, y), line, font=f, fill=ink, anchor="ma")
        y += step
    bar = round(14 * k)
    d.rounded_rectangle((w / 2 - 110 * k, y + 30 * k, w / 2 + 110 * k, y + 30 * k + bar), bar / 2, fill=PAL["highlight"])
    return np.asarray(im)


def on_screen_layer(text, w, h, S=SETTINGS):
    """RGBA keyword band, lower left: (array, x, y)."""
    c = S["on_screen"]
    k = w / 1920
    f = font(round(c["size"] * k))
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    tw = probe.textlength(text, font=f)
    pad = round(28 * k)
    bw, bh = int(tw + 2 * pad), int(f.size * 1.25 + 2 * pad * 0.7)
    im = Image.new("RGBA", (bw, bh), (*PAL["ink"], round(255 * c["band_alpha"])))
    d = ImageDraw.Draw(im)
    d.text((pad, bh / 2), text, font=f, fill=(*PAL["background"], 255), anchor="lm")
    d.rectangle((0, 0, round(8 * k), bh), fill=(*PAL["highlight"], 255))
    m = round(c["margin"] * k)
    return np.asarray(im), m, h - m - bh


def smooth(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


class ClipReader:
    """Frames of a Flow clip, read in order by ffmpeg, cropped to the video size; slowed then frozen if short."""

    def __init__(self, path, wanted_s, w, h, fps, slow_max):
        self.size, self.shape = w * h * 3, (h, w, 3)
        dur = probe_duration(path)
        self.slow = min(max(wanted_s / dur, 1.0), slow_max) if dur else 1.0
        self.frozen_s = max(0.0, wanted_s - dur * self.slow) if dur else wanted_s
        vf = (f"setpts={self.slow:.4f}*PTS,fps={fps},scale={w}:{h}:force_original_aspect_ratio=increase,"
              f"crop={w}:{h},format=rgb24")
        self.proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(path), "-an", "-vf", vf,
                                      "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.last, self.index = None, -1

    def frame(self, k):
        while self.index < k:
            raw = self.proc.stdout.read(self.size)
            if len(raw) < self.size:
                break
            self.last = np.frombuffer(raw, np.uint8).reshape(self.shape)
            self.index += 1
        return self.last

    def close(self):
        self.proc.stdout.close()
        self.proc.kill()
        self.proc.wait()


class Layer:
    """One scene on screen: its frame at any time of its presence (crossfades included)."""

    def __init__(self, scene, w, h, S=SETTINGS):
        self.s, self.w, self.h, self.S = scene, w, h, S
        self.ready = False
        self.clip = self.overlay = self.source = None
        self.warning = None

    def prepare(self):
        s, w, h, mo = self.s, self.w, self.h, self.S["motion"]
        fps, fade = self.S["video"]["fps"], self.S["timing"]["crossfade_s"]
        if s.card:
            self.source, self.margin = card_image(s, w, h), 1.0
        elif s.type == "chart":
            self.source, self.margin = read_rgb(s.image, w, h), 1.0
        else:
            m = mo["source_margin"]
            self.source, self.margin = read_rgb(s.image, round(w * m), round(h * m)), m
            if s.type == "video" and s.clip is not None:
                self.clip = ClipReader(s.clip, s.duration + fade, w, h, fps, mo["clip_slow_max"])
                if self.clip.frozen_s > 1.0:
                    self.warning = (f"scene {s.n}: clip too short, slowed x{self.clip.slow:.2f} "
                                    f"then frozen {self.clip.frozen_s:.1f} s")
        if s.on_screen and not s.card:
            self.overlay = on_screen_layer(s.on_screen, w, h, self.S)
        self.ready = True

    def view(self, u):
        """(zoom, centre x, centre y) of the scene's motion at progress u (0 to 1)."""
        mo, s = self.S["motion"], self.s
        u = smooth(u)
        if s.card or s.type == "chart":
            return 1 + mo["chart_zoom"] * u, 0.5, 0.5
        motion = s.motion if s.type == "image" else "zoom_in"
        if motion == "zoom_in":
            return 1 + mo["zoom"] * u, 0.5, 0.5
        if motion == "zoom_out":
            return 1 + mo["zoom"] * (1 - u), 0.5, 0.5
        a = min(mo["pan"] / 2 / self.margin, (1 - 1 / self.margin) / 2 * 0.95)
        x = 0.5 - a + 2 * a * u if motion == "pan_right" else 0.5 + a - 2 * a * u
        return 1.0, x, 0.5

    def frame(self, t):
        if not self.ready:
            self.prepare()
        s, w, h = self.s, self.w, self.h
        fade = self.S["timing"]["crossfade_s"]
        t0 = s.start - fade / 2
        u = (t - t0) / max(s.duration + fade, 1e-6)
        img = None
        if self.clip is not None:
            f = self.clip.frame(max(0, int((t - t0) * self.S["video"]["fps"])))
            img = f.copy() if f is not None else None
        if img is None:
            z, cx, cy = self.view(u)
            src = self.source
            sh, sw = src.shape[:2]
            vw_, vh_ = sw / self.margin / z, sh / self.margin / z
            x0 = min(max(cx * sw - vw_ / 2, 0), sw - vw_)
            y0 = min(max(cy * sh - vh_ / 2, 0), sh - vh_)
            sx = w / vw_
            M = np.float32([[sx, 0, -x0 * sx], [0, sx, -y0 * sx]])
            img = cv2.warpAffine(src, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        if self.overlay is not None:
            c = self.S["on_screen"]
            a = smooth((t - s.start - c["appear_s"]) / c["fade_s"]) * smooth((s.end - t) / c["fade_s"])
            if a > 0:
                img = img.copy() if not img.flags.writeable else img
                layer, x, y = self.overlay
                lh, lw = layer.shape[:2]
                region = img[y:y + lh, x:x + lw].astype(np.float32)
                alpha = layer[:, :, 3:4].astype(np.float32) / 255 * a
                img[y:y + lh, x:x + lw] = (region * (1 - alpha) + layer[:, :, :3] * alpha).astype(np.uint8)
        return img

    def release(self):
        if self.clip is not None:
            self.clip.close()
        self.clip = self.source = self.overlay = None
        self.ready = False


# ------------------------------------------------------------------ sound, render, check
def read_audio(path, rate):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(rate), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def soundtrack(voice_path, insertions, total, S=SETTINGS):
    """The voice with the cards' silences, to the video's length, at the YouTube loudness."""
    rate = S["video"]["audio_rate"]
    voice = read_audio(voice_path, rate)
    parts, last = [], 0
    for point, dur in sorted(insertions):
        i = min(int(round(point * rate)), len(voice))
        parts += [voice[last:i], np.zeros(int(round(dur * rate)), np.float32)]
        last = i
    parts.append(voice[last:])
    sound = np.concatenate(parts)
    n = int(round(total * rate))
    sound = np.concatenate([sound, np.zeros(max(0, n - len(sound)), np.float32)])[:n]
    a = S["audio"]
    r = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(rate), "-ac", "1", "-i", "-",
                        "-af", f"loudnorm=I={a['loudness_lufs']}:TP={a['true_peak_db']}:LRA=11",
                        "-f", "f32le", "-ar", str(rate), "-ac", "1", "-"],
                       input=sound.astype(np.float32).tobytes(), capture_output=True, check=True)
    out = np.frombuffer(r.stdout, np.float32)
    return np.concatenate([out, np.zeros(max(0, n - len(out)), np.float32)])[:n]


def probe_duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def render(scenes, sound, t0, t1, total, out, w, h, S=SETTINGS, log=print):
    """Encode the video between t0 and t1 (video time). Returns the render's warnings."""
    v, tm = S["video"], S["timing"]
    fps, fade, rate = v["fps"], tm["crossfade_s"], v["audio_rate"]
    shown = [s for s in scenes if s.end > t0 and s.start < t1]
    layers = [Layer(s, w, h, S) for s in shown]
    starts = [s.start for s in shown]
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    piece = sound[int(round(t0 * rate)):int(round(t1 * rate))]
    warnings = []
    with tempfile.NamedTemporaryFile(suffix=".f32") as audio:
        audio.write(piece.astype(np.float32).tobytes())
        audio.flush()
        cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
               "-r", str(fps), "-i", "-", "-f", "f32le", "-ar", str(rate), "-ac", "1", "-i", audio.name,
               "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", v["preset"], "-crf", str(v["crf"]),
               "-pix_fmt", "yuv420p", "-g", str(2 * fps), "-c:a", "aac", "-b:a", v["audio_bitrate"], "-ac", "2",
               "-movflags", "+faststart", "-shortest", str(out)]
        enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        n_frames = int(round((t1 - t0) * fps))
        try:
            for f in range(n_frames):
                t = t0 + f / fps
                k = max(0, bisect.bisect_right(starts, t) - 1)
                cur = layers[k]
                img = cur.frame(t)
                if k + 1 < len(layers) and t > cur.s.end - fade / 2:
                    a = smooth((t - (cur.s.end - fade / 2)) / fade)
                    img = cv2.addWeighted(img, 1 - a, layers[k + 1].frame(t), a, 0)
                elif k > 0 and t < cur.s.start + fade / 2:
                    a = smooth(0.5 + (t - cur.s.start) / fade)
                    img = cv2.addWeighted(layers[k - 1].frame(t), 1 - a, img, a, 0)
                black = min(smooth(t / tm["fade_in_s"]) if t0 == 0 else 1.0,
                            smooth((total - t) / tm["fade_out_s"]) if t1 >= total - 1e-6 else 1.0)
                if black < 1:
                    img = (img.astype(np.float32) * black).astype(np.uint8)
                enc.stdin.write(np.ascontiguousarray(img).tobytes())
                for j in range(k - 1):
                    if layers[j].ready:
                        warnings += [layers[j].warning] if layers[j].warning else []
                        layers[j].warning = None
                        layers[j].release()
                if f % (fps * 30) == 0:
                    log(f"   {f / fps:6.1f} s / {n_frames / fps:.1f} s")
        finally:
            enc.stdin.close()
            code = enc.wait()
            for layer in layers:
                if layer.warning:
                    warnings.append(layer.warning)
                if layer.ready:
                    layer.release()
    if code != 0:
        raise AssemblyError(f"ffmpeg failed (code {code}) while encoding {out}")
    return warnings


def technical_check(path, expected_s, w, h, S=SETTINGS):
    """[(check, passed, detail)]: size, audio track, no silence, no clipping, duration."""
    c = S["check"]
    probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                       "stream=codec_type,width,height:format=duration", "-of", "json", str(path)],
                                      capture_output=True, text=True).stdout or "{}")
    streams = probe.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio = [s for s in streams if s.get("codec_type") == "audio"]
    dur = float(probe.get("format", {}).get("duration", 0))
    levels = subprocess.run(["ffmpeg", "-v", "info", "-i", str(path), "-vn", "-af", "volumedetect", "-f", "null", "-"],
                            capture_output=True, text=True).stderr
    mean = re.search(r"mean_volume: (-?[\d.]+) dB", levels)
    peak = re.search(r"max_volume: (-?[\d.]+) dB", levels)
    mean = float(mean.group(1)) if mean else -99.0
    peak = float(peak.group(1)) if peak else 0.0
    return [
        ("size", video.get("width") == w and video.get("height") == h, f"{video.get('width')}x{video.get('height')}"),
        ("audio track", bool(audio), f"{len(audio)} track(s)"),
        ("no silence", mean > c["mean_volume_min_db"], f"mean volume {mean:.1f} dB (floor {c['mean_volume_min_db']} dB)"),
        ("no clipping", peak <= c["peak_max_db"], f"peak {peak:.1f} dB (ceiling {c['peak_max_db']} dB)"),
        ("duration", abs(dur - expected_s) <= c["duration_tolerance_s"], f"{dur:.1f} s for {expected_s:.1f} s expected"),
    ]


def code_version():
    """'<branch>@<commit>' of the code that renders (audit C3): 'main@1a2b3c4' in Colab."""
    def git(*args):
        r = subprocess.run(["git", "-C", str(HERE), *args], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else "unknown"
    return f"{git('rev-parse', '--abbrev-ref', 'HEAD')}@{git('rev-parse', '--short', 'HEAD')}"


def preview_moments(scenes, t0, t1):
    """[(name, t in the rendered file)]: start, title card, a chart, a clip, an on-screen keyword, end."""
    inside = [s for s in scenes if s.start >= t0 - 1e-6 and s.end <= t1 + 1e-6]
    mid = lambda s: (s.start + s.end) / 2 - t0  # noqa: E731
    pick = {
        "title": next((mid(s) for s in inside if s.card), None),
        "chart": next((mid(s) for s in inside if s.type == "chart"), None),
        "clip": next((mid(s) for s in inside if s.type == "video"), None),
        "on_screen": next((min(s.end - 0.4, s.start + 2.0) - t0 for s in inside if s.on_screen and not s.card), None),
    }
    dur = t1 - t0
    moments = [("1_start", min(1.0, dur / 2))]
    for i, (name, t) in enumerate(pick.items(), 2):
        moments.append((f"{i}_{name}" if t is not None else f"{i}_middle", t if t is not None else dur * i / 7))
    moments.append(("6_end", max(0.0, dur - 0.6)))
    return moments


def write_preview(video, moments, folder, width):
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    for name, t in moments:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0.0, t):.2f}", "-i", str(video), "-frames:v", "1",
                        "-vf", f"scale='min({width},iw)':-2", "-q:v", "5", str(folder / f"{name}.jpg")], check=False)
    return sorted(p.name for p in folder.glob("*.jpg"))


def write_verdict(path, verdict, max_bytes):
    """verdict_<name>.json, compact, under max_bytes: extra warnings stay in the report."""
    every = [w if len(w) <= 110 else w[:109] + "…" for w in verdict["warnings"]]
    for k in range(len(every), -1, -1):
        verdict["warnings"] = every[:k] + ([f"+ {len(every) - k} more in the report"] if k < len(every) else [])
        text = json.dumps(verdict, ensure_ascii=False, separators=(",", ":"))
        if len(text.encode("utf-8")) <= max_bytes:
            break
    path.write_text(text, encoding="utf-8")
    return verdict


# ------------------------------------------------------------------ the run
def find_video(root, name=""):
    """The video folder: by name, else the newest one whose voice is made and whose whole video is not ready."""
    videos = Path(root) / SETTINGS["drive"]["videos"]
    if name:
        folder = videos / name
        if not folder.is_dir():
            raise AssemblyError(f"No folder {folder}. Check VIDEO (for example 01_uber).")
        return folder
    waiting = []
    for d in sorted(p for p in videos.iterdir() if p.is_dir()) if videos.is_dir() else []:
        if not (d / SETTINGS["files"]["words"]).is_file():
            continue
        verdict = d / SETTINGS["files"]["render_dir"] / f"verdict_{SETTINGS['files']['full_name']}.json"
        try:
            ready = json.loads(verdict.read_text(encoding="utf-8")).get("ready") is True
        except (OSError, ValueError):
            ready = False
        if not ready:
            waiting.append(d)
    if not waiting:
        raise AssemblyError(f"No video in {videos} with a voice and no finished render. Write its folder name in VIDEO.")
    return waiting[-1]


def output_name(only):
    f = SETTINGS["files"]
    return f["full_name"] if not only else f["extract_name"].format(a=only[0], b=only[1])


def plan(folder, only=None, files=True, log=print):
    """Gate, charts, files, timing, chapters. Returns a dict (also written to render/plan.json for the whole video)."""
    folder = Path(folder)
    warnings = gate(folder)
    scenes = load_scenes(folder)
    if files:
        _, refused = charts.draw_folder(folder, log=log)
        if refused:
            raise AssemblyError("Charts refused (decision D4):\n- " + "\n- ".join(refused))
    missing, w2 = attach_files(scenes, folder, only, need=files)
    warnings += w2
    if missing:
        raise AssemblyError(f"Missing in {folder.name}: " + ", ".join(missing))
    words, duration = load_words(folder)
    align(scenes, words, duration)
    insertions, total = timeline(scenes, duration)
    warnings += scene_warnings(scenes)
    lines, w3 = chapters(folder, scenes, total)
    warnings += w3
    out_dir = folder / SETTINGS["files"]["render_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    result = {"video": folder.name, "made": now(), "code": code_version(), "voice_s": round(duration, 2),
              "total_s": round(total, 2), "cards": len(insertions), "chapters": lines, "warnings": warnings,
              "scenes": [{"n": s.n, "type": s.type, "start_s": round(s.start, 2), "duration_s": round(s.duration, 2),
                          "coverage": round(s.coverage, 2)} for s in scenes]}
    if not only:
        (out_dir / SETTINGS["files"]["chapters"]).write_text("\n".join(lines) + "\n", encoding="utf-8")
        (out_dir / "plan.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    log(f"🎬 {folder.name}: {len(scenes)} scenes, {minutes(total)} ({len(insertions)} card(s)), voice {minutes(duration)}")
    for s in scenes:
        if only and not only[0] <= s.n <= only[1]:
            continue
        what = s.on_screen if s.card else s.text
        log(f"   {s.n:3d} {s.type:7s} {minutes(s.start):>5s} {s.duration:5.1f} s {s.coverage:4.0%}  {what[:56]}")
    for line in lines:
        log(f"   ⏱ {line}")
    for w in warnings:
        log(f"⚠️  {w}")
    return {"scenes": scenes, "insertions": insertions, "total": total, "warnings": warnings, "plan": result}


def run(folder, only=None, plan_only=False, files=True, size=None, preset=None, work_dir=None, log=print):
    """The whole assembly; returns the verdict (or the plan with plan_only)."""
    folder = Path(folder)
    S = json.loads(json.dumps(SETTINGS))
    if preset:
        S["video"]["preset"] = preset
    w, h = size or (S["video"]["width"], S["video"]["height"])
    p = plan(folder, only, files=files if plan_only else True, log=log)
    if plan_only:
        return p["plan"]
    scenes, total = p["scenes"], p["total"]
    name = output_name(only)
    t0, t1 = 0.0, total
    if only:
        chosen = [s for s in scenes if only[0] <= s.n <= only[1]]
        if not chosen:
            raise AssemblyError(f"No scene in {only[0]}-{only[1]}")
        t0, t1 = chosen[0].start, chosen[-1].end
    out_dir = folder / S["files"]["render_dir"]
    work = Path(work_dir) if work_dir else out_dir
    work.mkdir(parents=True, exist_ok=True)
    video = work / f"{name}.mp4"
    began = time.monotonic()
    sound = soundtrack(folder / S["files"]["voice_wav"], p["insertions"], total, S)
    log(f"🎞️  Rendering {minutes(t0)} to {minutes(t1)} → {name}.mp4")
    warnings = p["warnings"] + render(scenes, sound, t0, t1, total, video, w, h, S, log)
    check = technical_check(video, t1 - t0, w, h, S)
    render_s = round(time.monotonic() - began)
    if work != out_dir:
        shutil.copy2(video, out_dir / video.name)
        video = out_dir / video.name
    code = code_version()
    ready = all(ok for _, ok, _ in check)
    report = {"video": folder.name, "output": video.name, "made": now(), "code": code,
              "from_s": round(t0, 2), "to_s": round(t1, 2), "total_s": round(total, 2), "size": f"{w}x{h}",
              "chapters": p["plan"]["chapters"] if not only else None,
              "scenes": p["plan"]["scenes"], "warnings": warnings,
              "check": [{"check": c, "passed": ok, "detail": d} for c, ok, d in check],
              "ready": ready, "render_s": render_s,
              "settings": {k: S[k] for k in ("video", "timing", "motion", "audio", "check")}}
    (out_dir / f"report_{name}.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    preview = write_preview(video, preview_moments(scenes, t0, t1), out_dir / f"preview_{name}", S["preview_width"])
    verdict = write_verdict(out_dir / f"verdict_{name}.json", {
        "video": folder.name, "output": video.name, "report": f"report_{name}.json", "ready": ready,
        "check": [f"{'✓' if ok else '✗'} {c}: {d}" for c, ok, d in check], "warnings": warnings,
        "duration_s": round(probe_duration(video), 1), "render_s": render_s, "code": code, "made": report["made"],
        "preview": f"preview_{name}/"}, S["verdict_max_bytes"])
    log("🔎 Technical check:")
    for c, ok, d in check:
        log(f"   {'✓' if ok else '✗'} {c}: {d}")
    log(f"{'✅ Ready' if ready else '❌ Not ready: do not publish'} — {out_dir / video.name} ({code})")
    return verdict


def parse_range(text):
    if not text:
        return None
    a, _, b = str(text).partition("-")
    return int(a), int(b or a)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Assemble a Whose Dime video folder.")
    ap.add_argument("folder")
    ap.add_argument("--scenes", help="an extract, e.g. 1-10 (render/extract_001-010.mp4)")
    ap.add_argument("--plan", action="store_true", help="gate, charts, timing and chapters only")
    ap.add_argument("--no-files", action="store_true", help="with --plan: do not look for images, clips, charts")
    ap.add_argument("--size", help="e.g. 960x540 for a quick look (the check then expects that size)")
    ap.add_argument("--preset", help="x264 preset (ultrafast for a test)")
    ap.add_argument("--work", help="render here first, then copy to render/ (Colab: the local disk)")
    a = ap.parse_args(argv)
    size = tuple(int(x) for x in a.size.lower().split("x")) if a.size else None
    try:
        result = run(a.folder, parse_range(a.scenes), a.plan, not a.no_files, size, a.preset, a.work)
    except AssemblyError as e:
        print(f"❌ {e}")
        return 1
    return 0 if a.plan or result.get("ready") else 1


if __name__ == "__main__":
    sys.exit(main())
