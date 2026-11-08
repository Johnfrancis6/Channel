"""Tests of the Whose Dime voice notebook (S06): whosedime/notebooks/.

The real model needs a GPU, so a stub stands in for it: each word is a
short harmonic tone, sentences end with a longer gap, and a "dry" seed cuts
the clip in the middle of its last word. A stub aligner finds the tones by
their energy and labels them with the text's words, as Whisper would.
"""
import importlib.util
import json
import random
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
NB = ROOT / "whosedime" / "notebooks"
UBER = ROOT / "whosedime" / "whosedime-maker" / "evals" / "files" / "01_uber"
VOICE_DIRECTION = ROOT / "whosedime" / "research" / "voice_direction.md"


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    spec.loader.exec_module(module)
    return module


V = load(NB / "voice_whosedime.py")
SR = 16000


def tone(seconds, sr=SR, f0=140.0, amp=0.3):
    """A voiced 'word': a few harmonics with 10 ms attack and 20 ms release."""
    t = np.arange(int(sr * seconds)) / sr
    x = sum(np.sin(2 * np.pi * f0 * k * t) / k for k in (1, 2, 3, 4))
    env = np.minimum(1.0, np.minimum(t / 0.01, (seconds - t) / 0.02))
    return (amp * x * np.clip(env, 0, 1) / 1.6).astype(np.float32)


def noise(seconds, sr=SR, rng=None, amp=0.001):
    rng = rng or np.random.default_rng(0)
    return (amp * rng.standard_normal(int(sr * seconds))).astype(np.float32)


class StubSynth:
    """synth(text, seed) -> (audio, sr). Seeds in `dry` give a clip cut mid-word."""

    def __init__(self, dry=()):
        self.dry = set(dry)
        self.calls = []

    def __call__(self, text, seed):
        self.calls.append((text, seed))
        rng = np.random.default_rng(seed)
        parts = [noise(0.08, rng=rng)]
        words = text.split()
        for i, w in enumerate(words):
            letters = sum(c.isalnum() for c in w)
            parts.append(tone(min(0.5, max(0.12, 0.05 * letters))))
            if i < len(words) - 1:
                end_of_sentence = w.rstrip("\"”").endswith((".", "?", "!"))
                parts.append(noise(0.12 if end_of_sentence else 0.05, rng=rng))
        parts.append(noise(0.25, rng=rng))
        audio = np.concatenate(parts)
        if seed in self.dry:  # cut inside the last word: no end silence, sound still loud
            last = len(tone(min(0.5, max(0.12, 0.05 * sum(c.isalnum() for c in words[-1])))))
            audio = audio[: len(audio) - len(parts[-1]) - last // 2]
        return audio, SR


def stub_aligner(audio, sr, text):
    """Word times from the energy of the clip, labelled with the text's words in order."""
    frame = int(sr * 0.005)
    n = len(audio) // frame
    db = 20 * np.log10(np.sqrt(np.mean(audio[: n * frame].reshape(n, frame) ** 2, axis=1)) + 1e-12)
    loud = db > np.percentile(db, 95) - 30
    segments, start, quiet = [], None, 0
    for i, on in enumerate(loud):
        if on:
            if start is None:
                start = i
            quiet, end = 0, i + 1
        elif start is not None:
            quiet += 1
            if quiet * 5 >= 25:
                segments.append((start, end))
                start = None
    if start is not None:
        segments.append((start, n if loud[-1] else end))
    words = V.spoken_words(text)
    return [{"word": w, "start": round(s * 0.005, 3), "end": round(e * 0.005, 3)}
            for w, (s, e) in zip(words, segments)]


def stub_designer(text, description, seed):
    audio, sr = StubSynth()(text, seed)
    return audio, sr


def fake_drive(tmp):
    """WhoseDime/Videos/01_uber with the Uber eval files, and a kept narrator."""
    root = Path(tmp) / "WhoseDime"
    video = root / "Videos" / "01_uber"
    video.mkdir(parents=True)
    for name in ("02_script.md", "02b_factcheck.md", "02_script_voice.txt", "02c_listen_20s.txt"):
        shutil.copy(UBER / name, video / name)
    return root, video


class Settings(unittest.TestCase):
    def setUp(self):
        self.S = V.load_settings()

    def test_one_source_for_the_description(self):
        """The narrator description A is the one of voice_direction.md (C5: one source)."""
        text = VOICE_DIRECTION.read_text(encoding="utf-8")
        quote = re.search(r"### VoiceDesign description to try first\n\n((?:> .*\n)+)", text).group(1)
        expected = " ".join(line[2:].strip() for line in quote.splitlines())
        self.assertEqual(self.S["design"]["descriptions"]["A"], expected)

    def test_pauses_match_voice_direction(self):
        text = VOICE_DIRECTION.read_text(encoding="utf-8")
        for label, key in (("A full stop inside a block", "full_stop"), ("A question", "question"),
                           (r"The end of a block \(2-4 sentences\)", "block")):
            ms = int(re.search(r"\| " + label + r" \| \*\*(\d+) ms\*\*", text).group(1))
            self.assertEqual(self.S["pauses_ms"][key], ms, key)

    def test_reference_text_length(self):
        """20-30 s at the speech rate assumed in voice_direction.md (165-180 words a minute)."""
        words = len(V.spoken_words(self.S["design"]["reference_text"]))
        self.assertTrue(20 * 165 / 60 <= words <= 30 * 165 / 60, words)


class Text(unittest.TestCase):
    def setUp(self):
        self.S = V.load_settings()

    def test_blocks_and_pauses(self):
        text = ('"Why not?" she said.\nIt was cheap.\nWho paid?\n\nNobody knew.\n'
                'He wrote: "It was a subsidy."\n\nThe end.\n')
        blocks = V.parse_blocks(text, self.S)
        self.assertEqual([len(b.sentences) for b in blocks], [3, 2, 1])
        p = self.S["pauses_ms"]
        self.assertEqual([s.pause_ms for s in blocks[0].sentences], [p["quote"], p["full_stop"], p["block"]])
        self.assertEqual([s.kind for s in blocks[1].sentences], ["full_stop", "quote"])
        self.assertEqual(blocks[1].sentences[-1].pause_ms, p["block"])
        self.assertEqual([s.n for b in blocks for s in b.sentences], [1, 2, 3, 4, 5, 6])

    def test_uber_voice_text(self):
        blocks = V.parse_blocks((UBER / "02_script_voice.txt").read_text(encoding="utf-8"), self.S)
        self.assertGreater(len(blocks), 50)
        self.assertTrue(all(1 <= len(b.sentences) <= 4 for b in blocks))

    def test_numbers_and_respellings_match_whisper_digits(self):
        lex = V.load_lexicon()
        self.assertEqual(V.number_words(2008), ["two", "thousand", "eight"])
        self.assertGreater(V.similarity("forty-one percent of Kuh-LAN-ick's", "41% of Kalanick's", lex), 0.95)
        self.assertGreater(V.similarity("one point four billion dollars", "1.4 billion dollars", lex), 0.75)

    def test_time_words_interpolates_unmatched(self):
        heard = [{"word": "Uber", "start": 0.1, "end": 0.4}, {"word": "2016", "start": 0.5, "end": 1.1},
                 {"word": "deal", "start": 1.2, "end": 1.5}]
        timed = V.time_words(["Uber", "twenty", "sixteen", "deal"], heard, 2.0)
        self.assertEqual(timed[0], (0.1, 0.4, "heard"))
        self.assertEqual(timed[3], (1.2, 1.5, "heard"))
        self.assertEqual(timed[1][2], "interpolated")
        self.assertTrue(0.4 <= timed[1][0] < timed[2][0] < timed[2][1] <= 1.2)


class Detector(unittest.TestCase):
    """Task 4: a clip cut mid-word is flagged, a clean one is not."""

    def setUp(self):
        self.S = V.load_settings()
        rng = np.random.default_rng(1)
        word = tone(0.4)
        self.clean = np.concatenate([noise(0.1, rng=rng), word, noise(0.3, rng=rng)])
        self.clean_end = 0.5
        self.cut = np.concatenate([noise(0.1, rng=rng), word[: len(word) // 2]])
        self.cut_end = len(self.cut) / SR

    def test_cut_clip_is_flagged(self):
        r = V.check_ending(self.cut, SR, self.cut_end, self.S)
        self.assertTrue(r.dry)
        self.assertEqual(len(r.reasons), 2)  # word at the very end, and still loud

    def test_clean_clip_passes(self):
        r = V.check_ending(self.clean, SR, self.clean_end, self.S)
        self.assertFalse(r.dry, r.reasons)
        self.assertGreater(r.gap_ms, 250)

    def test_loudness_alone_without_transcription(self):
        self.assertTrue(V.check_ending(self.cut, SR, None, self.S).dry)
        self.assertFalse(V.check_ending(self.clean, SR, None, self.S).dry)

    def test_word_too_close_to_the_end(self):
        """Quiet tail, but the transcribed word ends 40 ms before the end: dry."""
        r = V.check_ending(self.clean, SR, len(self.clean) / SR - 0.04, self.S)
        self.assertTrue(r.dry)
        self.assertIn("ms before the clip end", r.reasons[0])

    def test_retries_then_flag(self):
        s = V.Sentence(1, "It was cheap for a reason.", "full_stop", 700)
        retried = V.synth_clip([s], StubSynth(dry={10}), stub_aligner, self.S, 10)
        self.assertEqual([a["dry"] for a in retried.attempts], [True, False])
        self.assertFalse(retried.flagged)
        self.assertEqual(retried.seed, 10 + self.S["dry_ending"]["retry_seed_step"])
        step = self.S["dry_ending"]["retry_seed_step"]
        always = V.synth_clip([s], StubSynth(dry={10, 10 + step, 10 + 2 * step}), stub_aligner, self.S, 10)
        self.assertEqual(len(always.attempts), self.S["dry_ending"]["retries"] + 1)
        self.assertTrue(always.flagged)


class EndToEnd(unittest.TestCase):
    """Task 1-3 on a fake Drive folder with the stub model: design, sample, gates, full, blind test."""

    @classmethod
    def setUpClass(cls):
        cls.S = V.load_settings()
        cls.tmp = tempfile.mkdtemp()
        cls.root, cls.video = fake_drive(cls.tmp)
        cls.voice_dir = cls.root / cls.S["drive"]["voice"]
        cls.log = []
        made = V.design_candidates(stub_designer, cls.voice_dir, cls.S, log=cls.log.append)
        cls.made = made
        cls.vid = V.keep_candidate(cls.voice_dir, "A", cls.S, log=cls.log.append)
        cls.synth = StubSynth(dry={cls.S["seed"] + 3})  # block 3 ends dry on its first try
        step = cls.S["dry_ending"]["retry_seed_step"]
        cls.synth.dry |= {cls.S["seed"] + 5 + k * step for k in range(3)}  # block 5 always dry
        cls.sample = V.run_sample(cls.video, cls.synth, stub_aligner, cls.S, vid=cls.vid, log=cls.log.append)
        cls.calls_after_sample = len(cls.synth.calls)
        cls.out = cls.video / "voice"
        (cls.out / "state.json").write_text('{"junk": 1}', encoding="utf-8")
        cls.state = V.run_full(cls.video, cls.synth, stub_aligner, cls.S, vid=cls.vid, listened=True,
                               commit="abc1234", log=cls.log.append)
        cls.words = json.loads((cls.out / "words.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def test_design_then_keep(self):
        self.assertEqual([m["label"] for m in self.made], ["A", "B", "C"])
        ref = json.loads((self.voice_dir / "ref.json").read_text(encoding="utf-8"))
        self.assertEqual(ref["description"], self.S["design"]["descriptions"]["A"])
        self.assertEqual((self.voice_dir / "ref.txt").read_text(encoding="utf-8"), self.S["design"]["reference_text"])
        V.keep_candidate(self.voice_dir, "A", self.S, log=lambda m: None)  # again: the old one is archived
        self.assertEqual(len(list((self.voice_dir / "old").glob("*_ref.wav"))), 1)

    def test_sample_first(self):
        self.assertTrue((self.out / "listen_20s.wav").is_file())
        self.assertEqual(self.sample["voice"], self.vid)
        sample_words = len(V.spoken_words((self.video / "02c_listen_20s.txt").read_text(encoding="utf-8")))
        self.assertEqual(self.sample["words"], sample_words)
        # the full run re-used the sample's block 1 from the cache
        self.assertNotIn((V.parse_blocks((self.video / "02c_listen_20s.txt").read_text(encoding="utf-8"),
                                         self.S)[0].text, self.S["seed"] + 1),
                         self.synth.calls[self.calls_after_sample:])

    def test_gates(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, video = fake_drive(tmp)
            with self.assertRaisesRegex(V.GateError, "No 20 s sample"):
                V.run_full(video, StubSynth(), stub_aligner, self.S, vid=self.vid, listened=True, log=lambda m: None)
            shutil.copytree(self.out, video / "voice", ignore=shutil.ignore_patterns("cache"))
            with self.assertRaisesRegex(V.GateError, "I_LISTENED"):
                V.run_full(video, StubSynth(), stub_aligner, self.S, vid=self.vid, listened=False, log=lambda m: None)
            with self.assertRaisesRegex(V.GateError, "another reference voice"):
                V.run_full(video, StubSynth(), stub_aligner, self.S, vid="0" * 12, listened=True, log=lambda m: None)
            voice = video / "02_script_voice.txt"
            voice.write_text(voice.read_text(encoding="utf-8").replace("no taxi.", "no taxi at all."), encoding="utf-8")
            with self.assertRaisesRegex(V.GateError, "checker blocks"):
                V.run_sample(video, StubSynth(), stub_aligner, self.S, vid=self.vid, log=lambda m: None)

    def test_outputs_and_state(self):
        self.assertTrue((self.out / "voice.wav").is_file())
        audio, sr = V.read_wav(self.out / "voice.wav")
        self.assertAlmostEqual(len(audio) / sr, self.words["duration_s"], places=2)
        state = json.loads((self.out / "state.json").read_text(encoding="utf-8"))
        self.assertNotIn("junk", state)  # rewritten whole
        self.assertEqual(state["status"], "ready")
        self.assertEqual(state["commit"], "abc1234")
        self.assertIsInstance(state["rate_total_wpm"], float)
        self.assertIsInstance(state["rate_speech_wpm"], float)
        self.assertGreater(state["rate_speech_wpm"], state["rate_total_wpm"])
        self.assertIn(state["rate_verdict"].split(":")[0], ("in target", "near target", "outside the range"))
        self.assertEqual(state["settings"]["pauses_ms"], self.S["pauses_ms"])

    def test_every_word_timed_in_order(self):
        text = (self.video / "02_script_voice.txt").read_text(encoding="utf-8")
        self.assertEqual([w["word"] for w in self.words["words"]], V.spoken_words(text))
        starts = [w["start_s"] for w in self.words["words"]]
        self.assertEqual(starts, sorted(starts))
        self.assertTrue(all(w["end_s"] >= w["start_s"] for w in self.words["words"]))
        heard = sum(w["timed"] == "heard" for w in self.words["words"])
        self.assertGreater(heard / len(self.words["words"]), 0.95)

    def test_pauses_follow_punctuation(self):
        blocks = self.words["blocks"]
        for a, b in zip(blocks, blocks[1:]):
            self.assertAlmostEqual(b["start_s"] - a["end_s"], self.S["pauses_ms"]["block"] / 1000, places=2)
        inner = [p for b in blocks for p in b["inner_pauses"]]
        self.assertTrue(inner)
        for b in blocks:
            for s, nxt in zip(b["sentences"], b["sentences"][1:]):
                gap_ms = (nxt["start_s"] - s["end_s"]) * 1000
                self.assertGreaterEqual(gap_ms, s["pause_after_ms"] - 15, (b["n"], s["text"]))

    def test_dry_endings_redone_then_flagged(self):
        dry = self.state["dry_endings"]
        self.assertIn({"block": 3, "attempts": 2}, dry["redone"])
        self.assertEqual([f["block"] for f in dry["flagged"]], [5])
        self.assertEqual(self.words["blocks"][4]["flagged_dry"], True)
        self.assertEqual(dry["checked"], len(self.words["blocks"]))

    def test_resume_from_cache(self):
        synth = StubSynth(dry=self.synth.dry)
        V.run_full(self.video, synth, stub_aligner, self.S, vid=self.vid, listened=True, log=lambda m: None)
        self.assertEqual(synth.calls, [])
        V.run_full(self.video, synth, stub_aligner, self.S, vid=self.vid, listened=True, redo="2", log=lambda m: None)
        self.assertEqual([seed for _, seed in synth.calls], [self.S["seed"] + 2 + self.S["redo_seed_offset"]])

    def test_blind_test(self):
        key = V.run_blind_test(self.video, StubSynth(), stub_aligner, self.S, vid=self.vid,
                               log=lambda m: None, rng=random.Random(7))
        out = self.out / "blind_test"
        n = len(key["pairs"])
        self.assertTrue(5 <= n <= 9, n)
        self.assertTrue(18 <= sum(p["sentences"] for p in key["pairs"]) <= 24)
        self.assertEqual(len(list(out.glob("pair_*_X.wav"))), n)
        self.assertEqual(len(list(out.glob("pair_*_Y.wav"))), n)
        vote = (out / "vote.md").read_text(encoding="utf-8")
        self.assertNotIn("old way", vote)
        self.assertEqual(vote.count("\n| "), n + 1)
        self.assertEqual({p["X"] for p in key["pairs"]} | {p["Y"] for p in key["pairs"]}, {"A", "B"})
        self.assertEqual(key["pairs"][0]["block"], 1)  # the cold open is in


class Notebooks(unittest.TestCase):
    def cells(self, name):
        return json.loads((NB / name).read_text(encoding="utf-8"))["cells"]

    def params(self, source):
        return re.findall(r"^(\w+) = .*# @param", source, re.M)

    def test_code_cells_compile(self):
        for name in ("voice_whosedime.ipynb", "voice_launcher.ipynb"):
            for i, c in enumerate(self.cells(name)):
                if c["cell_type"] == "code":
                    compile("".join(c["source"]), f"{name}[{i}]", "exec")

    def test_launcher_passes_every_setting_and_runs_main(self):
        main = [c for c in self.cells("voice_whosedime.ipynb") if "settings" in c["metadata"].get("tags", [])]
        self.assertEqual(len(main), 1)
        settings = self.params("".join(main[0]["source"]))
        launch = "".join(next(c for c in self.cells("voice_launcher.ipynb") if c["cell_type"] == "code")["source"])
        self.assertEqual(self.params(launch), settings)
        passed = re.search(r"dict\((.*?)\), globals\(\)", launch, re.S).group(1)
        self.assertEqual(re.findall(r"(\w+)=", passed), settings)
        self.assertIn('BRANCH = "main"', launch)
        self.assertIn("print(f\"▶ Running {BRANCH} @ {COMMIT}\")", launch)

    def test_cell_order_design_before_clone(self):
        sources = ["".join(c["source"]) for c in self.cells("voice_whosedime.ipynb") if c["cell_type"] == "code"]
        order = [next(i for i, s in enumerate(sources) if key in s)
                 for key in ("qwen_designer", "qwen_clone_synth", "run_sample", "run_full", "run_blind_test")]
        self.assertEqual(order, sorted(order))

    def test_launcher_runs_settings_then_overrides(self):
        L = load(NB / "launcher.py")
        cells = L.code_cells("voice_whosedime.ipynb")
        self.assertEqual(sum(1 for _, _, s in cells if s), 1)
        self.assertTrue(cells[0][2], "the settings cell is the first code cell")


if __name__ == "__main__":
    unittest.main()
