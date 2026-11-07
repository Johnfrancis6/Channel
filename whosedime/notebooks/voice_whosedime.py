"""Whose Dime voice: the logic of voice_whosedime.ipynb (build session S06).

The notebook is a thin shell around this module, so the tests can run the
whole chain on a fake Drive folder with a stub model (no GPU). It turns a
video's `02_script_voice.txt` into `voice/`:

- `voice.wav`: the voice track, one synthesis per block of 2-4 sentences
  (audit V1, C6.1), with pauses that follow the punctuation (C6.2);
- `words.json`: the time of every word of the voice text, per block and
  sentence (the assembly aligns `03_scenes.md` on it);
- `state.json`: the run, rewritten whole, with both speaking rates (C5).

Each clip goes through the dry-ending detector (C6.3): redone with another
seed, twice at most, then flagged. Other modes: the 20 s listening sample
(D6), the blind test of block against sentence synthesis (D7), and the
VoiceDesign narrator saved as the reference that the Base model clones (D8).

Every number lives in `voice_settings.json` (C5). Only numpy and the
standard library are needed here; the model, Whisper, librosa and
pyloudnorm are imported inside the functions that use them (Colab).
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import wave
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SETTINGS_PATH = HERE / "voice_settings.json"
LEXICON_PATH = REPO / "whosedime" / "common" / "lexicon.tsv"
CHECKER_PATH = REPO / "whosedime" / "common" / "checker.py"


class GateError(RuntimeError):
    """A rule stops the run before any synthesis (unsigned registry, no sample)."""


def load_settings(path=SETTINGS_PATH):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha12(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()[:12]


# ------------------------------------------------------------------ text
CLOSING_QUOTES = ('"', "”")
OPENING_QUOTES = ('"', "“")
PUNCT = "\"'“”‘’.,;:!?()[]—–"


@dataclass
class Sentence:
    n: int            # 1-based over the whole text
    text: str
    kind: str         # full_stop, question, quote
    pause_ms: int     # silence after it


@dataclass
class Block:
    n: int            # 1-based
    sentences: list

    @property
    def text(self):
        return " ".join(s.text for s in self.sentences)


def sentence_kind(line):
    """'quote' if the line ends or starts with a quotation, 'question', else 'full_stop'."""
    s = line.strip()
    if s.endswith(CLOSING_QUOTES) or s.startswith(OPENING_QUOTES):
        return "quote"
    if s.endswith("?"):
        return "question"
    return "full_stop"


def parse_blocks(text, settings):
    """Blocks of the voice version: one sentence per line, a blank line between blocks."""
    pauses = settings["pauses_ms"]
    blocks, n_sentence = [], 0
    for raw in re.split(r"\n\s*\n", text.strip()):
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        if not lines:
            continue
        sentences = []
        for i, line in enumerate(lines):
            n_sentence += 1
            kind = sentence_kind(line)
            last = i == len(lines) - 1
            sentences.append(Sentence(n_sentence, line, kind, pauses["block"] if last else pauses[kind]))
        blocks.append(Block(len(blocks) + 1, sentences))
    return blocks


def spoken_words(text):
    """The words of a line as written in the voice version, punctuation stripped."""
    words = (w.strip(PUNCT) for w in text.split())
    return [w for w in words if any(c.isalnum() for c in w)]


# ------------------------------------------------------------------ word matching
ONES = ("zero one two three four five six seven eight nine ten eleven twelve thirteen "
        "fourteen fifteen sixteen seventeen eighteen nineteen").split()
TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]


def number_words(n):
    """An integer in English words, as a list ('2008' -> two thousand eight)."""
    if n < 20:
        return [ONES[n]]
    if n < 100:
        t, u = divmod(n, 10)
        return [TENS[t]] + ([ONES[u]] if u else [])
    if n < 1000:
        h, r = divmod(n, 100)
        return [ONES[h], "hundred"] + (number_words(r) if r else [])
    for size, name in ((10 ** 9, "billion"), (10 ** 6, "million"), (1000, "thousand")):
        if n >= size:
            q, r = divmod(n, size)
            return number_words(q) + [name] + (number_words(r) if r else [])
    return [str(n)]


def load_lexicon(path=LEXICON_PATH):
    """{spoken respelling (lower case): written form} from lexicon.tsv."""
    out = {}
    try:
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#") and "\t" in line:
                written, spoken = line.split("\t", 1)
                out[spoken.strip().lower()] = written.strip()
    except OSError:
        pass
    return out


def norm_tokens(text, lexicon=None):
    """Lower-case comparison tokens; digits said in words, respellings back to their written form."""
    t = text.lower().replace("’", "'")
    if lexicon:
        for spoken, written in lexicon.items():
            t = re.sub(r"(?<![\w-])" + re.escape(spoken) + r"(?![\w-])", written.lower(), t)
    t = re.sub(r"(?<=\d),(?=\d{3})", "", t)
    t = t.replace("%", " percent ").replace("&", " and ").replace("$", " ")
    out = []
    for tok in re.findall(r"\d+(?:\.\d+)?|[a-z]+(?:'[a-z]+)?", t):
        if tok[0].isdigit():
            whole, _, dec = tok.partition(".")
            out += number_words(int(whole)) + (["point"] + [ONES[int(d)] for d in dec] if dec else [])
        else:
            out.append(tok)
    return out


def similarity(text, heard_text, lexicon=None):
    """How close the transcription is to the text, 0 to 1 (letters only)."""
    a = "".join(norm_tokens(text, lexicon))
    b = "".join(norm_tokens(heard_text, lexicon))
    if not a and not b:
        return 1.0
    return round(difflib.SequenceMatcher(None, a, b, autojunk=False).ratio(), 3)


def time_words(words, heard, duration, lexicon=None):
    """Times for the voice text's own words from the transcribed ones.

    words: the written words of the block; heard: [{"word", "start", "end"}]
    from the aligner. A word matched to heard words takes their times
    ("heard"); the others share the gap between their matched neighbours, in
    proportion to their length ("interpolated"). Returns [(start, end, how)].
    """
    s_tok, s_own = [], []
    for i, w in enumerate(words):
        for tok in norm_tokens(w, lexicon) or [w.lower()]:
            s_tok.append(tok)
            s_own.append(i)
    h_tok, h_own = [], []
    for j, h in enumerate(heard):
        for tok in norm_tokens(h["word"], lexicon):
            h_tok.append(tok)
            h_own.append(j)
    spans = [None] * len(words)
    matcher = difflib.SequenceMatcher(None, s_tok, h_tok, autojunk=False)
    for a, b, size in matcher.get_matching_blocks():
        for k in range(size):
            i, j = s_own[a + k], h_own[b + k]
            st, en = heard[j]["start"], heard[j]["end"]
            spans[i] = (st, en) if spans[i] is None else (min(spans[i][0], st), max(spans[i][1], en))
    out = [None] * len(words)
    i = 0
    while i < len(words):
        if spans[i] is not None:
            out[i] = (spans[i][0], spans[i][1], "heard")
            i += 1
            continue
        j = i
        while j < len(words) and spans[j] is None:
            j += 1
        left = out[i - 1][1] if i > 0 else (heard[0]["start"] if heard else 0.0)
        right = spans[j][0] if j < len(words) else (heard[-1]["end"] if heard else duration)
        right = max(right, left)
        weights = [max(len(w), 1) for w in words[i:j]]
        total, t = float(sum(weights)), left
        for k, wgt in enumerate(weights):
            step = (right - left) * wgt / total
            out[i + k] = (t, t + step, "interpolated")
            t += step
        i = j
    return out


# ------------------------------------------------------------------ audio
def frame_db(audio, sr, frame_ms=10):
    n = max(1, int(sr * frame_ms / 1000))
    usable = len(audio) // n * n
    if usable == 0:
        return np.array([rms_db(audio)])
    frames = audio[:usable].reshape(-1, n).astype(np.float64)
    return 20 * np.log10(np.sqrt(np.mean(frames ** 2, axis=1)) + 1e-12)


def rms_db(x):
    x = np.asarray(x, dtype=np.float64)
    return float(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)) if len(x) else -240.0


def speech_level_db(audio, sr):
    """The level of the speech: 95th percentile of 10 ms frames."""
    return float(np.percentile(frame_db(audio, sr), 95))


@dataclass
class EndCheck:
    dry: bool
    gap_ms: float | None
    tail_db: float          # last 30 ms, in dB relative to the speech level
    reasons: list = field(default_factory=list)


def check_ending(audio, sr, last_word_end, settings):
    """Dry-ending detector (audit C6.3).

    Dry if the last transcribed word ends less than `word_end_gap_ms` before
    the clip end, or if the last `tail_ms` are still within `tail_loud_db`
    of the speech level. `last_word_end` may be None (no transcription):
    then only the loudness test runs.
    """
    d = settings["dry_ending"]
    duration = len(audio) / sr
    reasons, gap = [], None
    if last_word_end is not None:
        gap = round((duration - last_word_end) * 1000, 1)
        if gap < d["word_end_gap_ms"]:
            reasons.append(f"last word ends {gap:.0f} ms before the clip end (< {d['word_end_gap_ms']})")
    tail = audio[-max(1, int(sr * d["tail_ms"] / 1000)):]
    tail_rel = round(rms_db(tail) - speech_level_db(audio, sr), 1)
    if tail_rel > d["tail_loud_db"]:
        reasons.append(f"still loud in the last {d['tail_ms']} ms ({tail_rel:.0f} dB from the speech level)")
    return EndCheck(bool(reasons), gap, tail_rel, reasons)


def trim(audio, sr, settings):
    """Cut the clip's own silence at both edges, keeping a margin; short fades. Returns (audio, offset_s)."""
    t = settings["trim"]
    db = frame_db(audio, sr)
    frame = max(1, int(sr * 0.01))
    loud = np.nonzero(db > speech_level_db(audio, sr) - t["silence_below_speech_db"])[0]
    if len(loud) == 0:
        return audio.astype(np.float32), 0.0
    keep = int(sr * t["keep_ms"] / 1000)
    start = max(0, loud[0] * frame - keep)
    end = min(len(audio), (loud[-1] + 1) * frame + keep)
    out = audio[start:end].astype(np.float32).copy()
    fade = min(int(sr * t["fade_ms"] / 1000), len(out) // 2)
    if fade:
        ramp = np.linspace(0.0, 1.0, fade, dtype=np.float32)
        out[:fade] *= ramp
        out[-fade:] *= ramp[::-1]
    return out, start / sr


def resample(audio, sr_from, sr_to):
    if sr_from == sr_to:
        return audio
    try:
        import librosa
        return librosa.resample(audio, orig_sr=sr_from, target_sr=sr_to).astype(np.float32)
    except ImportError:
        n = int(round(len(audio) * sr_to / sr_from))
        return np.interp(np.linspace(0, len(audio) - 1, n), np.arange(len(audio)), audio).astype(np.float32)


def normalise(audio, sr, settings):
    """Loudness to the YouTube level (pyloudnorm on Colab, an RMS estimate elsewhere), peaks under peak_max."""
    target = settings["loudness_lufs"]
    method = "rms"
    try:
        import warnings
        import pyloudnorm as pyln
        level = pyln.Meter(sr).integrated_loudness(audio)
        if np.isfinite(level):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                audio = pyln.normalize.loudness(audio, level, target)
            method = "pyloudnorm"
    except ImportError:
        db = frame_db(audio, sr)
        active = db[db > speech_level_db(audio, sr) - 30]
        if len(active):
            level = 10 * np.log10(np.mean(10 ** (active / 10)))
            audio = audio * (10 ** ((target - level) / 20))
    peak = float(np.max(np.abs(audio))) if len(audio) else 0.0
    if peak > settings["peak_max"]:
        audio = audio * (settings["peak_max"] / peak)
    return audio.astype(np.float32), method


def write_wav(path, audio, sr):
    """16-bit PCM WAV, written to a temporary file then renamed (safe on Drive)."""
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    pcm = (np.clip(audio, -1.0, 1.0) * 32767).astype("<i2")
    with wave.open(str(tmp), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(int(sr))
        w.writeframes(pcm.tobytes())
    os.replace(tmp, path)


def read_wav(path):
    with wave.open(str(path), "rb") as w:
        sr, n, width, ch = w.getframerate(), w.getnframes(), w.getsampwidth(), w.getnchannels()
        data = w.readframes(n)
    if width != 2:
        raise ValueError(f"{path}: only 16-bit WAV is read here")
    audio = np.frombuffer(data, dtype="<i2").astype(np.float32) / 32767
    if ch > 1:
        audio = audio.reshape(-1, ch).mean(axis=1)
    return audio, sr


def write_json(path, data):
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def silence(ms, sr):
    return np.zeros(int(round(sr * ms / 1000)), dtype=np.float32)


# ------------------------------------------------------------------ one block
@dataclass
class Clip:
    """A synthesised block (or sentence), checked, timed, trimmed."""
    text: str
    audio: np.ndarray
    sr: int
    seed: int
    attempts: list          # [{"seed", "dry", "reasons"}]
    flagged: bool
    heard: str
    similarity: float
    words: list             # [{"word", "start", "end", "how", "sentence"}], times inside the clip
    pauses: list            # per inner sentence end: {"sentence", "target_ms", "model_ms", "added_ms"}


def _attempt(text, seed, synth, aligner, cache_dir, voice_id):
    """Synthesise (or read from the cache) and transcribe one clip."""
    key = sha12("\x00".join([text, str(seed), voice_id]))
    wav_path = Path(cache_dir) / f"{key}.wav" if cache_dir else None
    heard_path = Path(cache_dir) / f"{key}.json" if cache_dir else None
    if wav_path and wav_path.is_file():
        audio, sr = read_wav(wav_path)
    else:
        audio, sr = synth(text, seed)
        audio = np.asarray(audio, dtype=np.float32)
        if wav_path:
            write_wav(wav_path, audio, sr)
    if heard_path and heard_path.is_file():
        heard = json.loads(heard_path.read_text(encoding="utf-8"))
    else:
        heard = aligner(audio, sr, text)
        if heard_path:
            write_json(heard_path, heard)
    return audio, sr, heard, key


def _insert_pauses(audio, sr, sentences, timed, owners, stretch):
    """Lengthen each sentence-end gap inside a block up to its target. Returns audio, timed, report."""
    report, inserts = [], []
    for k, s in enumerate(sentences[:-1]):
        mine = [i for i, o in enumerate(owners) if o == k]
        nxt = [i for i, o in enumerate(owners) if o == k + 1]
        if not mine or not nxt:
            continue
        last, first_next = mine[-1], nxt[0]
        a, b = timed[last], timed[first_next]
        model_ms = max(0.0, (b[0] - a[1]) * 1000)
        entry = {"sentence": s.n, "target_ms": s.pause_ms, "model_ms": round(model_ms), "added_ms": 0}
        if stretch and a[2] == "heard" and b[2] == "heard" and model_ms < s.pause_ms:
            lo, hi = int(a[1] * sr), max(int(a[1] * sr) + 1, int(b[0] * sr))
            seg = frame_db(audio[lo:hi], sr, 5) if hi - lo > sr * 0.01 else None
            at = lo + (int(np.argmin(seg)) * int(sr * 0.005) if seg is not None else (hi - lo) // 2)
            add = s.pause_ms - model_ms
            inserts.append((at, add))
            entry["added_ms"] = round(add)
        report.append(entry)
    for at, add in sorted(inserts, reverse=True):
        audio = np.concatenate([audio[:at], silence(add, sr), audio[at:]])
        shift, t_at = add / 1000, at / sr
        timed = [(st + shift, en + shift, how) if st >= t_at else (st, en, how) for st, en, how in timed]
    return audio, timed, report


def synth_clip(sentences, synth, aligner, settings, seed, *, cache_dir=None, voice_id="",
               retry=True, lexicon=None):
    """One synthesis of 1-4 sentences, with the dry-ending retries, timed and trimmed."""
    text = " ".join(s.text for s in sentences)
    d = settings["dry_ending"]
    tries = d["retries"] + 1 if retry else 1
    attempts, best = [], None
    for k in range(tries):
        s = seed + k * d["retry_seed_step"]
        audio, sr, heard, _ = _attempt(text, s, synth, aligner, cache_dir, voice_id)
        end = check_ending(audio, sr, heard[-1]["end"] if heard else None, settings)
        attempts.append({"seed": s, "dry": end.dry, "reasons": end.reasons,
                         "gap_ms": end.gap_ms, "tail_db": end.tail_db})
        score = (not end.dry, end.gap_ms if end.gap_ms is not None else 0.0, -end.tail_db)
        if best is None or score > best[0]:
            best = (score, s, audio, sr, heard)
        if not end.dry:
            break
    _, seed_used, audio, sr, heard = best
    words, owners = [], []
    for k, sentence in enumerate(sentences):
        for w in spoken_words(sentence.text):
            words.append(w)
            owners.append(k)
    timed = time_words(words, heard, len(audio) / sr, lexicon)
    audio, timed, pauses = _insert_pauses(audio, sr, sentences, timed, owners,
                                          settings.get("stretch_inner_pauses", True))
    audio, offset = trim(audio, sr, settings)
    dur = len(audio) / sr
    out_words = []
    for w, (st, en, how), k in zip(words, timed, owners):
        st, en = min(max(st - offset, 0.0), dur), min(max(en - offset, 0.0), dur)
        out_words.append({"word": w, "start": round(st, 3), "end": round(max(en, st), 3),
                          "how": how, "sentence": sentences[k].n})
    heard_text = " ".join(h["word"] for h in heard)
    return Clip(text, audio, sr, seed_used, attempts, all(a["dry"] for a in attempts),
                heard_text, similarity(text, heard_text, lexicon), out_words, pauses)


# ------------------------------------------------------------------ a whole text
@dataclass
class Track:
    audio: np.ndarray
    sr: int
    blocks: list            # words.json "blocks"
    words: list             # words.json "words"
    clips: list
    speech_s: float


def assemble(blocks, clips, settings, *, last_pause=False):
    """Join the block clips with the block pause; global word and sentence times."""
    sr = clips[0].sr
    parts, cursor = [], 0
    out_blocks, out_words, speech = [], [], 0.0
    for i, (block, clip) in enumerate(zip(blocks, clips)):
        audio = resample(clip.audio, clip.sr, sr)
        start = cursor / sr
        parts.append(audio)
        cursor += len(audio)
        sentences = []
        for s in block.sentences:
            ws = [w for w in clip.words if w["sentence"] == s.n]
            s_start = start + (ws[0]["start"] if ws else 0.0)
            s_end = start + (ws[-1]["end"] if ws else len(audio) / sr)
            speech += max(0.0, s_end - s_start)
            sentences.append({"n": s.n, "text": s.text, "kind": s.kind, "start_s": round(s_start, 3),
                              "end_s": round(s_end, 3), "pause_after_ms": s.pause_ms})
        for w in clip.words:
            out_words.append({"n": len(out_words) + 1, "word": w["word"],
                              "start_s": round(start + w["start"], 3), "end_s": round(start + w["end"], 3),
                              "block": block.n, "sentence": w["sentence"], "timed": w["how"]})
        out_blocks.append({"n": block.n, "start_s": round(start, 3), "end_s": round(cursor / sr, 3),
                           "seed": clip.seed, "flagged_dry": clip.flagged, "similarity": clip.similarity,
                           "heard": clip.heard, "inner_pauses": clip.pauses, "sentences": sentences})
        if i < len(blocks) - 1 or last_pause:
            gap = silence(block.sentences[-1].pause_ms, sr)
            parts.append(gap)
            cursor += len(gap)
    audio = np.concatenate(parts) if parts else np.zeros(0, dtype=np.float32)
    return Track(audio, sr, out_blocks, out_words, clips, round(speech, 3))


def rates(n_words, speech_s, total_s, settings):
    r = settings["rate_wpm"]
    speech = round(n_words / speech_s * 60, 1) if speech_s else None
    total = round(n_words / total_s * 60, 1) if total_s else None
    if total is None:
        verdict = "unknown"
    elif r["target"][0] <= total <= r["target"][1]:
        verdict = "in target"
    elif r["never_outside"][0] <= total <= r["never_outside"][1]:
        verdict = "near target"
    else:
        verdict = "outside the range: " + ("too slow" if total < r["never_outside"][0] else "too fast")
    return speech, total, verdict


# ------------------------------------------------------------------ folders and gates
def video_paths(folder, settings):
    f = settings["files"]
    folder = Path(folder)
    out = folder / f["out_dir"]
    return {"folder": folder, "voice_text": folder / f["voice_text"], "sample_text": folder / f["sample_text"],
            "script": folder / f["script"], "out": out, "wav": out / f["wav"], "words": out / f["words"],
            "state": out / f["state"], "sample_wav": out / f["sample_wav"],
            "sample_record": out / f["sample_record"], "cache": out / f["cache"], "blind": out / f["blind_dir"]}


def find_video(root, name, settings):
    """The video folder: by name, else the newest one with a voice text and no ready voice."""
    videos = Path(root) / settings["drive"]["videos"]
    if name:
        folder = videos / name
        if not folder.is_dir():
            raise GateError(f"No folder {folder}. Check VIDEO (for example 01_uber).")
        return folder
    waiting = []
    for d in sorted(p for p in videos.iterdir() if p.is_dir()) if videos.is_dir() else []:
        p = video_paths(d, settings)
        if not p["voice_text"].is_file():
            continue
        try:
            ready = json.loads(p["state"].read_text(encoding="utf-8")).get("status") == "ready"
        except (OSError, ValueError):
            ready = False
        if not ready:
            waiting.append(d)
    if not waiting:
        raise GateError(f"No video in {videos} waiting for its voice. Write its folder name in VIDEO.")
    return waiting[-1]


def check_registry(folder, settings, python=sys.executable):
    """Decision D4: the checker's voice target must pass (signed registry, no drift from the script)."""
    p = video_paths(folder, settings)
    if not p["script"].is_file():
        raise GateError(f"{p['script'].name} is missing: the checker compares the voice version with it.")
    r = subprocess.run([python, str(CHECKER_PATH), "voice", str(p["script"]), str(p["voice_text"])],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise GateError("The checker blocks the voice (decision D4):\n" + (r.stdout + r.stderr)[-1500:])
    last = r.stdout.strip().splitlines()[-1].lstrip("- ") if r.stdout.strip() else "ok"
    return f"Checker (voice version): {last}"


def voice_id(voice_dir):
    """Fingerprint of the reference voice: ref.wav and ref.txt."""
    voice_dir = Path(voice_dir)
    wav, txt = voice_dir / "ref.wav", voice_dir / "ref.txt"
    if not (wav.is_file() and txt.is_file()):
        raise GateError(f"No reference voice in {voice_dir}: run MODE = 'design' first, then keep one candidate.")
    return sha12(wav.read_bytes() + txt.read_text(encoding="utf-8").strip().encode("utf-8"))


def settings_used(settings):
    return {k: settings[k] for k in ("pauses_ms", "stretch_inner_pauses", "dry_ending", "rate_wpm",
                                     "loudness_lufs", "seed", "language")}


def _redo_set(redo):
    if isinstance(redo, str):
        return {int(x) for x in re.findall(r"\d+", redo)}
    return set(redo or ())


def _synth_blocks(blocks, synth, aligner, settings, cache, vid, redo, log, lexicon, progress=None):
    clips = []
    for block in blocks:
        seed = settings["seed"] + block.n + (settings["redo_seed_offset"] if block.n in redo else 0)
        clip = synth_clip(block.sentences, synth, aligner, settings, seed, cache_dir=cache, voice_id=vid,
                          lexicon=lexicon)
        clips.append(clip)
        mark = " ⚠ dry ending, flagged" if clip.flagged else (
            f" (redone {len(clip.attempts) - 1}x)" if len(clip.attempts) > 1 else "")
        log(f"   [{block.n}/{len(blocks)}] {len(clip.audio) / clip.sr:4.1f} s  {block.text[:70]}{mark}")
        if progress:
            progress(block.n, len(blocks))
    return clips


def _dry_summary(blocks, clips):
    return {
        "checked": len(clips),
        "redone": [{"block": b.n, "attempts": len(c.attempts)} for b, c in zip(blocks, clips) if len(c.attempts) > 1],
        "flagged": [{"block": b.n, "text": b.text[:80], "reasons": c.attempts[-1]["reasons"]}
                    for b, c in zip(blocks, clips) if c.flagged],
    }


# ------------------------------------------------------------------ modes
def run_sample(folder, synth, aligner, settings, *, vid, commit=None, log=print, check=True):
    """D6: synthesise 02c_listen_20s.txt only, write listen_20s.wav and listen_20s.json, stop."""
    p = video_paths(folder, settings)
    if not p["sample_text"].is_file():
        raise GateError(f"{p['sample_text'].name} is missing: the skill writes it with the voice version (step 3c).")
    if check:
        log("✓ " + check_registry(folder, settings))
    p["out"].mkdir(exist_ok=True)
    p["cache"].mkdir(exist_ok=True)
    text = p["sample_text"].read_text(encoding="utf-8")
    blocks = parse_blocks(text, settings)
    lexicon = load_lexicon()
    clips = _synth_blocks(blocks, synth, aligner, settings, p["cache"], vid, set(), log, lexicon)
    track = assemble(blocks, clips, settings)
    audio, _ = normalise(track.audio, track.sr, settings)
    write_wav(p["sample_wav"], audio, track.sr)
    n_words = len(track.words)
    speech, total, verdict = rates(n_words, track.speech_s, len(audio) / track.sr, settings)
    record = {"status": "waiting for Franco's ear", "video": Path(folder).name, "made": now(),
              "commit": commit, "voice": vid, "text_sha256": sha12(text), "duration_s": round(len(audio) / track.sr, 2),
              "words": n_words, "rate_speech_wpm": speech, "rate_total_wpm": total, "rate_verdict": verdict,
              "dry_endings": _dry_summary(blocks, clips), "settings": settings_used(settings)}
    write_json(p["sample_record"], record)
    log(f"✓ {p['sample_wav'].name}: {record['duration_s']} s, {total} words a minute ({verdict})")
    return record


def run_full(folder, synth, aligner, settings, *, vid, listened=False, redo="", commit=None,
             log=print, check=True):
    """The whole voice: voice.wav, words.json, state.json (rewritten whole)."""
    p = video_paths(folder, settings)
    if not p["voice_text"].is_file():
        raise GateError(f"{p['voice_text'].name} is missing: the voice version is step 3c of whosedime-maker.")
    try:
        sample = json.loads(p["sample_record"].read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise GateError("No 20 s sample yet (decision D6): run MODE = 'sample', listen, then come back.") from None
    if sample.get("voice") != vid:
        raise GateError("The 20 s sample was made with another reference voice: run MODE = 'sample' again.")
    if not listened:
        raise GateError("Listen to voice/listen_20s.wav first, then tick I_LISTENED (decision D6).")
    if check:
        log("✓ " + check_registry(folder, settings))
    p["out"].mkdir(exist_ok=True)
    p["cache"].mkdir(exist_ok=True)
    text = p["voice_text"].read_text(encoding="utf-8")
    blocks = parse_blocks(text, settings)
    redo_set = _redo_set(redo)
    state = {"status": "running", "mode": "full", "video": Path(folder).name, "commit": commit,
             "started": now(), "updated": now(), "finished": None, "voice": vid,
             "text": {"file": p["voice_text"].name, "sha256": sha12(text), "blocks": len(blocks),
                      "sentences": sum(len(b.sentences) for b in blocks)},
             "sample": {"made": sample.get("made"), "listened": True},
             "redo_blocks": sorted(redo_set), "progress": {"done": 0, "of": len(blocks)},
             "settings": settings_used(settings), "error": None}
    write_json(p["state"], state)

    def progress(done, of):
        if done % 10 == 0 or done == of:
            state.update(progress={"done": done, "of": of}, updated=now())
            write_json(p["state"], state)

    try:
        lexicon = load_lexicon()
        clips = _synth_blocks(blocks, synth, aligner, settings, p["cache"], vid, redo_set, log, lexicon, progress)
        track = assemble(blocks, clips, settings)
        audio, loudness = normalise(track.audio, track.sr, settings)
        write_wav(p["wav"], audio, track.sr)
        duration = round(len(audio) / track.sr, 3)
        write_json(p["words"], {"video": Path(folder).name, "duration_s": duration, "sample_rate": track.sr,
                                "made": now(), "voice": vid, "blocks": track.blocks, "words": track.words})
        n_words = len(track.words)
        speech, total, verdict = rates(n_words, track.speech_s, duration, settings)
        low = [{"block": b["n"], "similarity": b["similarity"], "heard": b["heard"][:100]}
               for b in track.blocks if b["similarity"] < settings["similarity_min"]]
        used = {f"{k}.{e}" for c in clips for a in c.attempts
                for k in [sha12("\x00".join([c.text, str(a["seed"]), vid]))] for e in ("wav", "json")}
        for f in p["cache"].iterdir():
            if f.name not in used:
                f.unlink()
        state = {"status": "ready", "mode": "full", "video": Path(folder).name, "commit": commit,
                 "started": state["started"], "updated": now(), "finished": now(), "voice": vid,
                 "text": state["text"], "sample": state["sample"], "redo_blocks": sorted(redo_set),
                 "duration_s": round(duration, 1), "words": n_words, "speech_s": round(track.speech_s, 1),
                 "rate_speech_wpm": speech, "rate_total_wpm": total, "rate_verdict": verdict,
                 "rate_target_wpm": settings["rate_wpm"]["target"],
                 "rate_definitions": {
                     "rate_speech_wpm": "words / sum of sentence spans (first word start to last word end), "
                                        "pauses between sentences and blocks left out",
                     "rate_total_wpm": "words / duration of voice.wav, pauses included: the rate lessons.md keeps"},
                 "dry_endings": _dry_summary(blocks, clips), "low_similarity": low,
                 "loudness": loudness, "settings": settings_used(settings),
                 "outputs": [p["wav"].name, p["words"].name], "error": None}
        write_json(p["state"], state)
    except Exception as e:
        state.update(status="failed", updated=now(), error=f"{type(e).__name__}: {e}")
        write_json(p["state"], state)
        raise
    m, s = divmod(int(round(state["duration_s"])), 60)
    log(f"✓ voice.wav: {m} min {s:02d} s; {n_words} words")
    log(f"✓ Rate: {total} words a minute on the whole track ({verdict}; target "
        f"{settings['rate_wpm']['target'][0]}-{settings['rate_wpm']['target'][1]}), {speech} in speech only")
    if state["dry_endings"]["flagged"]:
        log(f"⚠ Dry endings flagged (after {settings['dry_ending']['retries']} retries): "
            f"blocks {[f['block'] for f in state['dry_endings']['flagged']]} -> listen; "
            "to redo, put their numbers in REDO_BLOCKS")
    if low:
        log(f"⚠ Heard far from the text: blocks {[x['block'] for x in low]} -> listen")
    return state


def pick_blind_blocks(blocks, settings):
    """About 20 sentences in whole blocks, from three places of the text (D7)."""
    b = settings["blind_test"]
    total_words = sum(len(spoken_words(x.text)) for x in blocks)
    chosen, cum, starts = [], 0, []
    for x in blocks:
        starts.append(cum)
        cum += len(spoken_words(x.text))
    anchors = b["anchors"]
    for g, anchor in enumerate(anchors):
        left = b["sentences"] - sum(len(x.sentences) for x in chosen)
        quota = round(left / (len(anchors) - g))
        i = next((k for k, s in enumerate(starts) if s >= anchor * total_words), len(blocks) - 1)
        count = 0
        while i < len(blocks) and count < quota:
            n = len(blocks[i].sentences)
            if count and count + n - quota > quota - count:
                break  # this block would overshoot more than stopping falls short
            if blocks[i] not in chosen:
                chosen.append(blocks[i])
                count += n
            i += 1
    return chosen


def run_blind_test(folder, synth, aligner, settings, *, vid, commit=None, log=print, rng=None):
    """D7: the same blocks said two ways, shuffled as X / Y; vote.md for Franco, key.json for after the vote.

    A (the old way): one clip per sentence, 300 ms between. B (the new way):
    one clip per block, pauses by punctuation. No retries in either, so the
    dry endings counted are those of the method itself.
    """
    p = video_paths(folder, settings)
    blocks = pick_blind_blocks(parse_blocks(p["voice_text"].read_text(encoding="utf-8"), settings), settings)
    out = p["blind"]
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    rng = rng or random.Random(int.from_bytes(os.urandom(4), "big"))
    lexicon = load_lexicon()
    old_pause = settings["blind_test"]["old_pause_ms"]
    pairs, dry_a, dry_b, ends_a, ends_b = [], 0, 0, 0, 0
    for k, block in enumerate(blocks, 1):
        a_parts, a_sim = [], []
        for s in block.sentences:
            c = synth_clip([s], synth, aligner, settings, settings["seed"] + 5000 + s.n,
                           voice_id=vid, retry=False, lexicon=lexicon)
            dry_a += c.flagged
            ends_a += 1
            a_parts += [c.audio, silence(old_pause, c.sr)]
            a_sim.append(c.similarity)
        audio_a = np.concatenate(a_parts[:-1])
        cb = synth_clip(block.sentences, synth, aligner, settings, settings["seed"] + block.n,
                        voice_id=vid, retry=False, lexicon=lexicon)
        dry_b += cb.flagged
        ends_b += 1
        a_is_x = rng.random() < 0.5
        x, y = (audio_a, cb.audio) if a_is_x else (cb.audio, audio_a)
        write_wav(out / f"pair_{k:02d}_X.wav", normalise(x, cb.sr, settings)[0], cb.sr)
        write_wav(out / f"pair_{k:02d}_Y.wav", normalise(y, cb.sr, settings)[0], cb.sr)
        pairs.append({"pair": k, "block": block.n, "sentences": len(block.sentences), "text": block.text,
                      "X": "A" if a_is_x else "B", "Y": "B" if a_is_x else "A",
                      "similarity_A": round(float(np.mean(a_sim)), 3), "similarity_B": cb.similarity})
        log(f"   pair {k}: block {block.n}, {len(block.sentences)} sentences")
    n_sent = sum(x["sentences"] for x in pairs)
    lines = [f"# Blind test (D7): {Path(folder).name}", "",
             f"{len(pairs)} pairs, {n_sent} sentences. Each pair is the same text said two ways, X and Y "
             "(the order changes at random). Listen to X then Y; write X or Y under **Better**, and "
             "`cut` under **Cut ending** if an ending sounds cut. Open `key.json` only after voting.", "",
             "| Pair | Text (start) | Better (X/Y) | Cut ending |", "|---|---|---|---|"]
    lines += [f"| {x['pair']} | {x['text'][:60]}... |  |  |" for x in pairs]
    (out / "vote.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    key = {"made": now(), "commit": commit, "voice": vid,
           "A": f"old way: one clip per sentence, {old_pause} ms between",
           "B": "new way: one clip per block, pauses by punctuation",
           "pairs": pairs,
           "dry_endings": {"A": f"{dry_a} of {ends_a} sentence ends", "B": f"{dry_b} of {ends_b} block ends"},
           "similarity_mean": {"A": round(float(np.mean([x["similarity_A"] for x in pairs])), 3),
                               "B": round(float(np.mean([x["similarity_B"] for x in pairs])), 3)},
           "pass_if": ["B: fewer than 1 dry ending in 30", "A preferred in fewer than 1 pair in 4",
                       "similarity of B not lower than A's"]}
    write_json(out / "key.json", key)
    log(f"✓ {len(pairs)} pairs in voice/{out.name}/: vote in vote.md, then open key.json")
    return key


# ------------------------------------------------------------------ the narrator (D8)
def design_candidates(designer, voice_dir, settings, *, log=print):
    """VoiceDesign: one reference per description (A, B, C) in Voice/candidates/."""
    d = settings["design"]
    cand = Path(voice_dir) / "candidates"
    cand.mkdir(parents=True, exist_ok=True)
    made = []
    for label, description in sorted(d["descriptions"].items()):
        seed = settings["seed"]
        audio, sr = designer(d["reference_text"], description, seed)
        audio, _ = normalise(trim(np.asarray(audio, dtype=np.float32), sr, settings)[0], sr, settings)
        write_wav(cand / f"{label}.wav", audio, sr)
        write_json(cand / f"{label}.json", {"label": label, "description": description, "seed": seed,
                                            "model": settings["models"]["design"], "made": now()})
        seconds = len(audio) / sr
        lo, hi = d["reference_seconds"]
        note = "" if lo <= seconds <= hi else f"  ⚠ outside {lo}-{hi} s"
        log(f"   candidate {label}: {seconds:.1f} s{note}")
        made.append({"label": label, "seconds": round(seconds, 1)})
    return made


def keep_candidate(voice_dir, label, settings, *, log=print):
    """Make candidate <label> the reference voice; the old one is archived with its date."""
    voice_dir = Path(voice_dir)
    src = voice_dir / "candidates" / f"{label}.wav"
    if not src.is_file():
        raise GateError(f"No candidate {label} in {voice_dir / 'candidates'}: run MODE = 'design' first.")
    if (voice_dir / "ref.wav").exists():
        old = voice_dir / "old"
        old.mkdir(exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        for name in ("ref.wav", "ref.txt", "ref.json"):
            if (voice_dir / name).exists():
                shutil.move(str(voice_dir / name), old / f"{stamp}_{name}")
    shutil.copyfile(src, voice_dir / "ref.wav")
    (voice_dir / "ref.txt").write_text(settings["design"]["reference_text"], encoding="utf-8")
    meta = json.loads((voice_dir / "candidates" / f"{label}.json").read_text(encoding="utf-8"))
    write_json(voice_dir / "ref.json", dict(meta, kept=now()))
    vid = voice_id(voice_dir)
    log(f"✓ Reference voice: candidate {label} ({vid})")
    return vid


# ------------------------------------------------------------------ the real models (Colab only)
def qwen_designer(settings, device="cuda:0"):
    """designer(text, description, seed) -> (audio, sr) on the VoiceDesign model."""
    import torch
    from qwen_tts import Qwen3TTSModel
    cuda = torch.cuda.is_available()
    model = Qwen3TTSModel.from_pretrained(settings["models"]["design"], device_map=device if cuda else "cpu",
                                          dtype=torch.bfloat16 if cuda else torch.float32)

    def designer(text, description, seed):
        torch.manual_seed(seed)
        wavs, sr = model.generate_voice_design(text=text, instruct=description, language=settings["language"])
        return wavs[0].astype(np.float32), int(sr)
    return designer


def qwen_clone_synth(voice_dir, settings, device="cuda:0"):
    """synth(text, seed) -> (audio, sr): the Base model cloning Voice/ref.wav."""
    import torch
    from qwen_tts import Qwen3TTSModel
    cuda = torch.cuda.is_available()
    model = Qwen3TTSModel.from_pretrained(settings["models"]["base"], device_map=device if cuda else "cpu",
                                          dtype=torch.bfloat16 if cuda else torch.float32)
    voice_dir = Path(voice_dir)
    prompt = model.create_voice_clone_prompt(ref_audio=str(voice_dir / "ref.wav"),
                                             ref_text=(voice_dir / "ref.txt").read_text(encoding="utf-8").strip())

    def synth(text, seed):
        torch.manual_seed(seed)
        wavs, sr = model.generate_voice_clone(text=text, language=settings["language"], voice_clone_prompt=prompt)
        return wavs[0].astype(np.float32), int(sr)
    return synth


def whisper_aligner(settings):
    """aligner(audio, sr, text) -> [{"word", "start", "end"}]. The text is not given to Whisper,
    so the similarity measures what is heard, not what is expected."""
    import torch
    from faster_whisper import WhisperModel
    cuda = torch.cuda.is_available()
    model = WhisperModel(settings["models"]["whisper"], device="cuda" if cuda else "cpu",
                         compute_type="float16" if cuda else "int8")

    def aligner(audio, sr, text):
        a16 = resample(np.asarray(audio, dtype=np.float32), sr, 16000)
        segments, _ = model.transcribe(a16, language="en", word_timestamps=True, vad_filter=False)
        return [{"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)}
                for s in segments for w in (s.words or []) if w.word.strip()]
    return aligner
