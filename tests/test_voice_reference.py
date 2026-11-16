"""Tests of MODE = "reference" (S12, D22): the narrator's reference clip made in ElevenLabs, cloned by Qwen3-TTS.

No network and no model: the "downloaded" clip is fixture audio from the stub synthesiser of
test_voice_whosedime (a tone per word), saved as MP3 by ffmpeg. A fixture aligner plays Whisper:
it hears what the clip really says, whatever text it is told.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_voice_whosedime as T  # noqa: E402

V = T.V
HAS_FFMPEG = shutil.which("ffmpeg") is not None
OTHER = ("Here is a story about money, and about the people who pay for it without knowing. "
         "Who pays when the ride is cheap? Not the company, not the investors, and not you either. "
         "Somebody else covers the gap, every single day, and nobody sends them a thank-you card.")


class SaidAligner:
    """aligner(audio, sr, text) -> the stub transcription of what the clip really says."""

    def __init__(self, said):
        self.said = said

    def __call__(self, audio, sr, text):
        return T.stub_aligner(audio, sr, self.said)


def make_clip(path, text, *, lead_s=1.0, fmt="mp3"):
    """A clip saying `text`, with silence before it (trimmed by the import), saved like a download."""
    audio, _ = T.StubSynth()(text, 3)
    audio = np.concatenate([np.zeros(int(T.SR * lead_s), dtype=np.float32), audio])
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    wav = path.with_name(path.stem + "_tmp.wav")
    V.write_wav(wav, audio, T.SR)
    out = path.with_suffix("." + fmt)
    if fmt == "wav":
        wav.rename(out)
    else:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-ar", "44100", "-b:a", "192k", str(out)],
                       check=True)
        wav.unlink()
    return out


@unittest.skipUnless(HAS_FFMPEG, "ffmpeg is needed (apt-get install -y ffmpeg)")
class Reference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.S = V.load_settings()
        cls.text = cls.S["design"]["reference_text"]
        cls.tmp = tempfile.mkdtemp()
        cls.root, cls.video = T.fake_drive(cls.tmp)
        cls.voice_dir = cls.root / cls.S["drive"]["voice"]
        cls.voice_dir.mkdir()
        (cls.voice_dir / "ref.wav").write_bytes(b"old")  # a previous narrator: archived, not lost
        (cls.voice_dir / "ref.txt").write_text("old", encoding="utf-8")
        cls.clip = make_clip(cls.voice_dir / "elevenlabs" / "Brian reference", cls.text)
        cls.log = []
        cls.meta = V.import_reference(cls.voice_dir, SaidAligner(cls.text), cls.S, log=cls.log.append)
        cls.vid = V.voice_id(cls.voice_dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def fresh_voice_dir(self, tmp):
        d = Path(tmp) / "Voice"
        d.mkdir()
        return d

    def test_writes_what_the_clone_reads(self):
        audio, sr = V.read_wav(self.voice_dir / "ref.wav")
        self.assertEqual(sr, 24000)
        self.assertEqual((self.voice_dir / "ref.txt").read_text(encoding="utf-8"), self.text)
        ref = json.loads((self.voice_dir / "ref.json").read_text(encoding="utf-8"))
        self.assertEqual(ref["source"], "elevenlabs")
        self.assertEqual(ref["file"], "Brian reference.mp3")
        self.assertEqual(ref["text_from"], "the guide's reference text")
        self.assertGreaterEqual(ref["similarity"], 0.95)
        self.assertEqual(ref["words"], len(V.spoken_words(self.text)))
        self.assertAlmostEqual(len(audio) / sr, ref["seconds"], places=0)
        self.assertLess(ref["seconds"], 30)  # the second of silence before the voice is trimmed
        self.assertEqual(len(self.vid), 12)

    def test_old_reference_archived(self):
        old = sorted(p.name for p in (self.voice_dir / "old").iterdir())
        self.assertEqual([n.split("_", 2)[-1] for n in old], ["ref.txt", "ref.wav"])

    def test_rate_reported(self):
        ref = json.loads((self.voice_dir / "ref.json").read_text(encoding="utf-8"))
        self.assertAlmostEqual(ref["rate_wpm"], ref["words"] / ref["seconds"] * 60, delta=1.5)
        self.assertIn(ref["rate_verdict"], ("in range", "too fast", "too slow"))
        self.assertTrue(any("words a minute" in line for line in self.log))

    def test_sample_then_full_unchanged(self):
        """The rest of the chain runs as before on this reference (stub clone)."""
        rec = V.run_sample(self.video, T.StubSynth(), T.stub_aligner, self.S, vid=self.vid, log=lambda m: None)
        self.assertEqual(rec["voice"], self.vid)
        self.assertIn("rate_advice", rec)
        state = V.run_full(self.video, T.StubSynth(), T.stub_aligner, self.S, vid=self.vid, listened=True,
                           log=lambda m: None)
        self.assertEqual(state["status"], "ready")

    def test_franco_text_used_when_heard(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = self.fresh_voice_dir(tmp)
            mine = OTHER
            make_clip(d / "elevenlabs" / "take2", mine, fmt="wav")
            (d / "elevenlabs" / "take2.txt").write_text(mine + "\n", encoding="utf-8")
            meta = V.import_reference(d, SaidAligner(mine), self.S, log=lambda m: None)
            self.assertEqual(meta["text_from"], "take2.txt")
            self.assertEqual((d / "ref.txt").read_text(encoding="utf-8"), mine)

    def test_franco_text_not_said_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = self.fresh_voice_dir(tmp)
            said = OTHER
            make_clip(d / "elevenlabs" / "take3", said)
            (d / "elevenlabs" / "take3.txt").write_text(self.text, encoding="utf-8")
            with self.assertRaisesRegex(V.GateError, "does not say the text of take3.txt"):
                V.import_reference(d, SaidAligner(said), self.S, log=lambda m: None)
            self.assertFalse((d / "ref.wav").exists())

    def test_other_text_without_txt_uses_whisper(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = self.fresh_voice_dir(tmp)
            said = OTHER
            make_clip(d / "elevenlabs" / "take4", said)
            log = []
            meta = V.import_reference(d, SaidAligner(said), self.S, log=log.append)
            self.assertTrue(meta["text_from"].startswith("Whisper"))
            self.assertEqual(V.spoken_words((d / "ref.txt").read_text(encoding="utf-8")), V.spoken_words(said))
            self.assertTrue(any(line.startswith("⚠ The clip is not") for line in log))

    def test_refusals(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = self.fresh_voice_dir(tmp)
            with self.assertRaisesRegex(V.GateError, "No audio file"):
                V.import_reference(d, SaidAligner(""), self.S, log=lambda m: None)
            make_clip(d / "elevenlabs" / "a", "Too short.", lead_s=0.1)
            with self.assertRaisesRegex(V.GateError, r"a reference must last 5-60 s"):
                V.import_reference(d, SaidAligner("Too short."), self.S, log=lambda m: None)
            make_clip(d / "elevenlabs" / "b", "Also short.", fmt="wav")
            with self.assertRaisesRegex(V.GateError, r"2 audio files .*a\.mp3, b\.wav"):
                V.import_reference(d, SaidAligner(""), self.S, log=lambda m: None)


class RateAdvice(unittest.TestCase):
    def setUp(self):
        self.S = V.load_settings()

    def test_reference_rate(self):
        lo, hi = self.S["reference_import"]["rate_wpm"]
        self.assertEqual(V.reference_rate(70, 70 / ((lo + hi) / 2) * 60, self.S)[1], "in range")
        wpm, verdict, advice = V.reference_rate(70, 20, self.S)  # 210 wpm, the S11 clone's pace
        self.assertEqual((wpm, verdict), (210.0, "too fast"))
        self.assertIn("lower Speed", advice)
        self.assertIn("raise Speed", V.reference_rate(70, 40, self.S)[2])

    def test_sample_advice_points_to_the_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            V.write_json(Path(tmp) / "ref.json", {"source": "elevenlabs", "rate_wpm": 171})
            fast = V.sample_rate_advice(206.0, "outside the range: too fast", tmp, self.S)
            self.assertIn("lower Speed", fast)
            self.assertIn("171", fast)
            self.assertIn("raise Speed", V.sample_rate_advice(139.0, "near target", tmp, self.S))
            self.assertEqual(V.sample_rate_advice(149.0, "in target", tmp, self.S), "")


class NotebookReference(unittest.TestCase):
    def test_guide_text_is_the_settings_text(self):
        """The text Franco pastes is the one the import expects (one source, C5)."""
        guide = (T.ROOT / "docs" / "whosedime" / "voice_elevenlabs_guide.md").read_text(encoding="utf-8")
        quote = next(line.strip()[2:] for line in guide.splitlines() if line.strip().startswith("> So here's"))
        self.assertEqual(quote, V.load_settings()["design"]["reference_text"])

    def test_reference_mode_before_the_clone(self):
        cells = json.loads((T.NB / "voice_whosedime.ipynb").read_text(encoding="utf-8"))["cells"]
        sources = ["".join(c["source"]) for c in cells if c["cell_type"] == "code"]
        self.assertIn('"reference"', sources[0])
        at = next(i for i, s in enumerate(sources) if "import_reference" in s)
        self.assertLess(at, next(i for i, s in enumerate(sources) if "qwen_clone_synth" in s))


if __name__ == "__main__":
    unittest.main()
