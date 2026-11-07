"""Tests of the whosedime-maker skill (S04): its frame, and the reference
outputs of the Uber script eval, which must keep passing the checker."""
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
        for step in ("step1_topic.md", "step2_research.md", "step3_script.md"):
            self.assertIn(step, text)

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
        self.assertEqual([r.target for r in reports], ["script", "voice"])
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

    def test_listening_sample_is_the_voice_start(self):
        sample = (RUN / "02c_listen_20s.txt").read_text().strip()
        voice = (RUN / "02_script_voice.txt").read_text()
        self.assertTrue(voice.startswith(sample))
        self.assertTrue(40 <= len(sample.split()) <= 60)


if __name__ == "__main__":
    unittest.main()
