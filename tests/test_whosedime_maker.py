"""Tests of the whosedime-maker skill (S04, S05): its frame, and the reference
outputs of the Uber evals (script, scenes, publication), which must keep
passing the checker."""
import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "whosedime" / "whosedime-maker"
RUN = SKILL / "evals" / "files" / "01_uber"


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


C = load(ROOT / "whosedime" / "common" / "checker.py")


class TestSkillFrame(unittest.TestCase):
    def test_skill_md(self):
        text = (SKILL / "SKILL.md").read_text()
        self.assertLess(len(text.splitlines()), 250)
        self.assertRegex(text, r"^---\nname: whosedime-maker\ndescription: ")
        for ref in re.findall(r"\(references/([\w.]+)\)", text):
            self.assertTrue((SKILL / "references" / ref).is_file(), ref)
        for step in ("step1_topic.md", "step2_research.md", "step3_script.md",
                     "step4_scenes.md", "step5_publication.md", "memory.md"):
            self.assertIn(step, text)
        self.assertIn("## The sessions of a video", text)
        self.assertIn("00_state.md", text)

    def test_script_headings_match_the_reference(self):
        ref = (SKILL / "references" / "step3_script.md").read_text()
        heads = re.findall(r"^## (.+)$", (RUN / "02_script.md").read_text(), re.M)
        for h in heads[:-1]:                      # the last one is '## Sources'
            self.assertIn(f"`## {h}`", ref)
        self.assertEqual(heads[-1], "Sources")

    def test_evals(self):
        data = json.loads((SKILL / "evals" / "evals.json").read_text())
        self.assertEqual(data["skill_name"], "whosedime-maker")
        self.assertGreaterEqual(len(data["evals"]), 3)


class TestUberReferenceRun(unittest.TestCase):
    def test_checker_all_passes(self):
        reports = C.check_all(RUN)
        self.assertEqual([r.target for r in reports], ["script", "voice", "scenes", "publication"])
        for r in reports:
            self.assertEqual(r.blocks, [], r.render())
        self.assertLessEqual(sum(len(r.warnings) for r in reports), 3)
        words = int(reports[0].summary.split()[0].replace(",", ""))
        self.assertTrue(2000 <= words <= 2250, words)

    def test_not_the_memory_fixture(self):
        fixture = ROOT / "tests" / "fixtures" / "whosedime" / "factcheck_clean.md"
        self.assertNotEqual((RUN / "02b_factcheck.md").read_text(), fixture.read_text())
        reg = C.Registry(RUN / "02b_factcheck.md")
        self.assertEqual(reg.errors, [])
        self.assertEqual(reg.signed_hash, reg.fingerprint)
        self.assertIn("not Franco", reg.signed)

    def test_scenes_mix_and_charts(self):
        rows, error = C.scene_table((RUN / "03_scenes.md").read_text())
        self.assertIsNone(error)
        types = [r["type"] for _, r in rows]
        counts = C.SETTINGS["scenes"]["counts"]
        self.assertTrue(counts["total"][0] <= len(rows) <= counts["total"][1], len(rows))
        for t in ("image", "chart", "video", "title", "chapter"):
            self.assertTrue(counts[t][0] <= types.count(t) <= counts[t][1], (t, types.count(t)))
        reg = C.Registry(RUN / "02b_factcheck.md")
        for _, r in rows:
            if r["type"] == "chart":
                ids = re.findall(r"\bF\d{2}\b", r["chart"])
                self.assertTrue(ids and all(reg.status(i) == "verified" for i in ids), r["chart"])

    def test_publication_chapters_follow_the_cards(self):
        rows, _ = C.scene_table((RUN / "03_scenes.md").read_text())
        cards = [r["on-screen text"] for _, r in rows if r["type"] in ("title", "chapter")]
        chapters = re.findall(r"^(?:0:00|--:--) (.+)$", (RUN / "04_publication.md").read_text(), re.M)
        self.assertEqual(chapters[0], "Cold open")
        self.assertEqual(len(chapters), len(cards) + 1)
        for label, card in zip(chapters[1:], cards):
            self.assertIn(label.lower(), card.lower())

    def test_listening_sample_is_the_voice_start(self):
        sample = (RUN / "02c_listen_20s.txt").read_text().strip()
        voice = (RUN / "02_script_voice.txt").read_text()
        self.assertTrue(voice.startswith(sample))
        self.assertTrue(40 <= len(sample.split()) <= 60)


if __name__ == "__main__":
    unittest.main()
