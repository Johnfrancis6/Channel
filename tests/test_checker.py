"""Tests of whosedime/common/checker.py (S03): each faulty fixture in
tests/fixtures/whosedime/ carries one fault and must be blocked for it; the
clean Uber pair must pass with at most 3 warnings."""
import contextlib
import importlib.util
import io
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMON = ROOT / "whosedime" / "common"
FIX = ROOT / "tests" / "fixtures" / "whosedime"
THRESHOLDS = ROOT / "whosedime" / "research" / "style_thresholds.json"
FACTS = FIX / "factcheck_clean.md"


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


C = load(COMMON / "checker.py")
RULE_IDS = {r["id"] for r in json.loads(THRESHOLDS.read_text())["rules"]}


def blocks(report):
    return set(report.codes("BLOCK"))


def style_warnings(report):
    return [c for c in report.codes("WARN") if c in RULE_IDS]


def run(argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = C.main(argv)
    return code, out.getvalue()


class TestRegistryFormat(unittest.TestCase):
    def test_format_example_parses_back(self):
        doc = (COMMON / "FACTCHECK_FORMAT.md").read_text()
        example = re.search(r"<!-- example:start -->\s*```markdown\n(.*?)```\s*<!-- example:end -->",
                            doc, re.S).group(1)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "02b_factcheck.md"
            path.write_text(example)
            reg = C.Registry(path)
        self.assertEqual(reg.errors, [])
        self.assertEqual(sorted(reg.facts), ["F01", "F02", "F03", "F04", "F05", "F06"])
        self.assertEqual([f["status"] for f in reg.facts.values()],
                         ["verified"] * 3 + ["to_verify"] * 3)
        self.assertEqual(reg.people_names(), ["Garrett Camp", "Travis Kalanick"])
        self.assertIsNone(reg.signed)
        self.assertIn("1.1 billion", reg.numbers)
        self.assertIn("kalanick", reg.names)

    def test_clean_registry_is_signed_and_well_formed(self):
        reg = C.Registry(FACTS)
        self.assertEqual(reg.errors, [])
        self.assertTrue(reg.signed)
        self.assertNotIn("Uber Technologies", reg.people_names())   # role: organisation

    def test_malformed_registry_blocks(self):
        text = FACTS.read_text().replace("| F09 | In 2016, Uber sold its operations in China to Didi | Reuters, 2016-08-01 |",
                                         "| F08 | In 2016, Uber sold its operations in China to Didi | — |")
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "02b_factcheck.md").write_text(text)
            shutil.copy(FIX / "script_clean.md", Path(d) / "02_script.md")
            report = C.check_script(Path(d) / "02_script.md")
        self.assertEqual(blocks(report) - {"source-tag", "name"}, {"registry"})


class TestFaultyFiles(unittest.TestCase):
    def assertOnlyBlock(self, report, code):
        self.assertEqual(blocks(report), {code}, report.render())

    def test_unknown_number(self):
        report = C.check_script(FIX / "script_unknown_number.md", FACTS)
        self.assertOnlyBlock(report, "number")
        self.assertIn("18 billion", report.render())

    def test_to_verify(self):
        self.assertOnlyBlock(C.check_script(FIX / "script_to_verify.md", FACTS), "to-verify")

    def test_misquote(self):
        self.assertOnlyBlock(C.check_script(FIX / "script_misquote.md", FACTS), "quote")

    def test_unsigned_registry_blocks_voice(self):
        report = C.check_voice(FIX / "script_clean.md", FIX / "voice_clean.txt", FIX / "factcheck_unsigned.md")
        self.assertOnlyBlock(report, "signature")
        script = C.check_script(FIX / "script_clean.md", FIX / "factcheck_unsigned.md")
        self.assertEqual(blocks(script), set())          # the signature blocks the voice only

    def test_long_title(self):
        report = C.check_publication(FIX / "publication_long_title.md", FACTS)
        self.assertOnlyBlock(report, "title")
        self.assertIn("41 characters", report.render())

    def test_publication_unknown_number(self):
        report = C.check_publication(FIX / "publication_unknown_number.md", FACTS)
        self.assertOnlyBlock(report, "number")
        self.assertIn("31 billion", report.render())

    def test_advice(self):
        self.assertOnlyBlock(C.check_script(FIX / "script_advice.md", FACTS), "forbidden")

    def test_voice_drift(self):
        report = C.check_voice(FIX / "script_clean.md", FIX / "voice_drift.txt", FACTS)
        self.assertOnlyBlock(report, "voice-drift")

    def test_zehon_style_warns(self):
        report = C.check_script(FIX / "script_zehon_style.md", FACTS)
        self.assertGreaterEqual(len(style_warnings(report)), 2, report.render())


class TestCleanPair(unittest.TestCase):
    def test_clean_script_passes_with_few_warnings(self):
        report = C.check_script(FIX / "script_clean.md", FACTS)
        self.assertEqual(report.blocks, [], report.render())
        self.assertLessEqual(len(report.warnings), 3, report.render())
        words = int(report.summary.split()[0].replace(",", ""))
        self.assertGreaterEqual(words, 1900)

    def test_clean_voice_and_publication_pass(self):
        voice = C.check_voice(FIX / "script_clean.md", FIX / "voice_clean.txt", FACTS)
        self.assertEqual(voice.items, [], voice.render())
        pub = C.check_publication(FIX / "publication_clean.md", FACTS)
        self.assertEqual(pub.items, [], pub.render())      # title 2 is exactly 40 characters

    def test_all_command_and_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            names = C.SETTINGS["files"]
            for src, key in [("factcheck_clean.md", "facts"), ("script_clean.md", "script"),
                             ("voice_clean.txt", "voice"), ("publication_clean.md", "publication")]:
                shutil.copy(FIX / src, Path(d) / names[key])
            code, out = run(["all", d])
            self.assertEqual(code, 0, out)
            self.assertEqual(out.count("== "), 3)
            shutil.copy(FIX / "voice_drift.txt", Path(d) / names["voice"])
            self.assertEqual(run(["all", d])[0], 1)
            self.assertEqual(run(["script", str(Path(d) / "missing.md")])[0], 2)


class TestRules(unittest.TestCase):
    """Facts rules on small texts, written to a temporary script next to the clean registry."""

    def check(self, text):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "02_script.md"
            path.write_text(text)
            shutil.copy(FACTS, Path(d) / "02b_factcheck.md")
            return C.check_script(path, style=False)

    def test_spelled_and_written_numbers_match(self):
        self.assertEqual(blocks(self.check("In twenty twenty-three, Uber made one point one billion dollars.")), set())
        self.assertEqual(blocks(self.check("Riders paid forty-one percent, back in 2015.")), set())
        self.assertEqual(blocks(self.check("Uber made 1.2 billion dollars.")), set())       # F07 holds $1.2 billion
        self.assertEqual(blocks(self.check("Uber made $1.3 billion.")), {"number"})

    def test_small_spelled_numbers_are_not_facts(self):
        self.assertEqual(blocks(self.check("Two friends, one cold street, no taxi.")), set())

    def test_unverified_fact_and_tag_block(self):
        report = self.check("By 2030, the cut fell to about 10 percent.[^F25]")
        self.assertEqual(blocks(report), {"number", "source-tag"})
        self.assertIn("not verified", report.render())
        self.assertEqual(blocks(self.check("This is sourced.[^F99]")), {"source-tag"})

    def test_unknown_name_blocks(self):
        self.assertEqual(blocks(self.check("Then the money came from Goldman Sachs.")), {"name"})
        self.assertEqual(blocks(self.check("Then the money came from the Public Investment Fund.")), set())

    def test_quote_with_ellipsis(self):
        ok = self.check('He wrote, "In 2008, on a snowy night in Paris ... I had trouble getting a cab."')
        self.assertEqual(blocks(ok), set())
        bad = self.check('He wrote, "In 2008, on a snowy night in London ... I had trouble getting a cab."')
        self.assertEqual(blocks(bad), {"quote"})

    def test_to_verify_in_a_comment_still_blocks(self):
        self.assertEqual(blocks(self.check("Uber grew.\n<!-- [TO VERIFY: growth] -->\n")), {"to-verify"})


class TestNothingHardCoded(unittest.TestCase):
    def test_no_rule_id_or_metric_in_checker_code(self):
        source = (COMMON / "checker.py").read_text()
        for rule in json.loads(THRESHOLDS.read_text())["rules"]:
            self.assertNotRegex(source, rf"\b{rule['id']}\b")
            self.assertNotIn(rule["metric"], source)

    def test_threshold_change_in_a_copy_changes_the_warnings(self):
        data = json.loads(THRESHOLDS.read_text())
        before = C.check_script(FIX / "script_clean.md", FACTS)
        quiet = [r for r in data["rules"] if r["id"] not in before.codes("WARN")]
        rule = next(r for r in quiet if r["max"] is not None)
        rule["max"] = -1          # nothing can be below -1: the rule must now fire
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "thresholds.json"
            path.write_text(json.dumps(data))
            after = C.check_script(FIX / "script_clean.md", FACTS, thresholds=path)
        self.assertNotIn(rule["id"], before.codes("WARN"))
        self.assertIn(rule["id"], after.codes("WARN"))


class TestCanon(unittest.TestCase):
    def same(self, a, b):
        self.assertEqual([t for t, _ in C.canon(a)], [t for t, _ in C.canon(b)])

    def test_numbers_said_and_written(self):
        self.same("$1.1 billion", "one point one billion dollars")
        self.same("41%", "forty-one percent")
        self.same("in 2008", "in two thousand eight")
        self.same("in 2008", "in twenty oh eight")
        self.same("in 2023", "in twenty twenty-three")
        self.same("311 cities", "three hundred and eleven cities")
        self.same("22,000 drivers", "twenty-two thousand drivers")
        self.same("June 1st", "June first")
        self.same("the 1990s", "the nineteen nineties")
        self.same("$1 million", "a million dollars")


if __name__ == "__main__":
    unittest.main()
