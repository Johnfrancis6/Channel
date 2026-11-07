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
        self.assertEqual(pub.blocks, [], pub.render())     # title 2 is exactly 40 characters
        self.assertEqual(pub.codes("WARN"), ["name-first"], pub.render())   # S04: measured 1 warning

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


class TestSignatureHash(unittest.TestCase):
    """S04 task 0: the signature is bound to the registry's content."""

    def voice_with(self, registry_text):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "02b_factcheck.md"
            path.write_text(registry_text)
            return C.check_voice(FIX / "script_clean.md", FIX / "voice_clean.txt", path)

    def test_fixture_hash_matches_its_content(self):
        reg = C.Registry(FACTS)
        self.assertRegex(reg.signed_hash, r"^sha256:[0-9a-f]{12}$")
        self.assertEqual(reg.signed_hash, reg.fingerprint)
        code, out = run(["fingerprint", str(FACTS)])
        self.assertEqual((code, out.strip()), (0, reg.fingerprint))

    def test_unchanged_copy_passes(self):
        self.assertEqual(self.voice_with(FACTS.read_text()).items, [])

    def test_edited_verified_line_blocks_voice(self):
        text = FACTS.read_text()
        edited = text.replace("Reuters, 2016-08-01", "Reuters, 2016-08-02")   # F09, verified
        self.assertNotEqual(edited, text)
        report = self.voice_with(edited)
        self.assertEqual(blocks(report), {"signature"}, report.render())
        self.assertIn("registry changed since it was signed", report.render())

    def test_signature_without_hash_blocks_voice(self):
        text = re.sub(r", sha256:[0-9a-f]+", "", FACTS.read_text())
        report = self.voice_with(text)
        self.assertEqual(blocks(report), {"signature"}, report.render())
        self.assertIn("no sha256 hash", report.render())

    def test_hash_ignores_the_signature_section_and_line_endings(self):
        text = FACTS.read_text()
        resigned = re.sub(r"Signed: .*", "Signed: Franco, 2026-12-01, " + C.fingerprint(text), text)
        self.assertEqual(C.fingerprint(resigned), C.fingerprint(text))
        self.assertEqual(C.fingerprint(text.replace("\n", "  \r\n")), C.fingerprint(text))


class TestSentenceFirstNames(unittest.TestCase):
    """S04 task 0: unknown capitalised first words go into one warning line."""

    def check(self, text):
        return TestRules.check(self, text)

    def test_name_only_as_first_word_warns_once(self):
        report = self.check("Uber needed money. Goldman found it. Riders came back. Bankers called.")
        self.assertEqual(blocks(report), set())
        warns = [m for lv, c, m in report.items if c == "name-first"]
        self.assertEqual(len(warns), 1, report.render())
        self.assertIn("Goldman", warns[0])
        self.assertIn("Bankers", warns[0])

    def test_word_in_lower_case_elsewhere_or_registered_is_not_collected(self):
        report = self.check("Riders came back. Then the riders paid. Kalanick smiled. Twenty friends waited.")
        self.assertNotIn("name-first", report.codes())

    def test_clean_script_measured_count(self):
        report = C.check_script(FIX / "script_clean.md", FACTS)
        self.assertEqual(report.codes("WARN"), ["name-first"], report.render())   # measured 07/11: 1 warning


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


UBER = ROOT / "whosedime" / "whosedime-maker" / "evals" / "files" / "01_uber"


class TestScenes(unittest.TestCase):
    """S05: the scenes check, on faulty copies of the Uber reference run's 03_scenes.md."""

    def check(self, edit=None):
        with tempfile.TemporaryDirectory() as d:
            for name in ("02b_factcheck.md", "02_script.md", "03_scenes.md"):
                shutil.copy(UBER / name, Path(d) / name)
            path = Path(d) / "03_scenes.md"
            if edit:
                path.write_text(edit(path.read_text()))
            return C.check_scenes(path)

    def faulty(self, old, new, code, count=1):
        def edit(text):
            self.assertIn(old, text)
            return text.replace(old, new, count)
        report = self.check(edit)
        self.assertIn(code, blocks(report), report.render())
        return report

    def test_reference_run_passes(self):
        report = self.check()
        self.assertEqual(report.items, [], report.render())

    def test_chart_without_fact_id_blocks(self):
        report = self.faulty("| F04 · timeline · launch", "| timeline · launch", "chart-source")
        self.assertEqual(blocks(report), {"chart-source"})

    def test_chart_citing_an_unverified_fact_blocks(self):
        self.faulty("| F04 · timeline · launch", "| F27 · timeline · launch", "chart-source")

    def test_chart_number_not_in_its_fact_blocks(self):
        report = self.faulty("F07 · number · $3.5 billion", "F07 · number · $4.5 billion", "chart-source")
        self.faulty("F05 · split · riders paid 41%", "F06 · split · riders paid 41%", "chart-source")
        self.assertNotIn("number", blocks(report))       # a chart number is checked against its own fact

    def test_spoken_text_must_be_the_script(self):
        report = self.faulty("Two friends, one cold street, no taxi.", "Two friends, one street, no taxi.", "scene-text")
        self.assertIn("from scene 2", report.render())

    def test_real_person_named_in_a_prompt_blocks(self):
        self.faulty("Two young men in winter coats", "Travis Kalanick and a friend in winter coats", "prompt-person")
        self.faulty("one raises his hand", "Kalanick raises his hand", "prompt-person")

    def test_sentence_first_common_word_is_not_a_person(self):
        report = self.check(lambda t: t.replace("Plain cream background.", "Rich cream background."))
        self.assertNotIn("prompt-person", blocks(report), report.render())

    def test_missing_prompts_block(self):
        self.faulty("**anim_001**", "**note_001**", "prompt")
        self.faulty("**scene_002**", "**scene_x02**", "prompt")

    def test_cards_numbers_visuals_and_on_screen_numbers(self):
        self.faulty("| 7 | title | — |", "| 7 | title | Who pays? |", "scene-card")
        self.faulty("| 3 | image |", "| 4 | image |", "scene-number")
        self.faulty("| images/scene_002.png |", "| images/scene_2.png |", "scene-visual")
        self.faulty("| zoom_in | — | — |", "| dolly | — | — |", "scene-motion")
        self.faulty("| PARIS, 2008 |", "| PARIS, 2007 |", "number")

    def test_mix_only_warns(self):
        report = self.check(lambda t: t.replace("| image |", "| chart |", 1).replace(
            "| images/scene_002.png | zoom_in | — | — |", "| charts/scene_002.png | — | — | F01 · timeline · 2008 |"))
        self.assertEqual(blocks(report), set(), report.render())
        self.assertIn("prompt", report.codes("WARN"))         # its image prompt is now unused

    def test_cli_and_all(self):
        self.assertEqual(run(["scenes", str(UBER / "03_scenes.md")])[0], 0)
        self.assertEqual([r.target for r in C.check_all(UBER)], ["script", "voice", "scenes", "publication"])


class TestTitleSource(unittest.TestCase):
    """S05, audit C2: a number in a title or a thumbnail text cites the fact that holds it."""

    def check(self, titles, thumbnail="- WHO PAID?"):
        with tempfile.TemporaryDirectory() as d:
            shutil.copy(FACTS, Path(d) / "02b_factcheck.md")
            path = Path(d) / "04_publication.md"
            path.write_text(f"# Publication\n\n## Titles\n\n{titles}\n\n## Thumbnail\n\n{thumbnail}\n\n"
                            "## Description\n\nWe follow the dollar.\n")
            return C.check_publication(path)

    def test_number_without_tag_blocks(self):
        self.assertIn("title-source", blocks(self.check("1. Uber Lost $9.1 Billion. Who Paid?")))
        self.assertIn("title-source", blocks(self.check("1. Uber Was Cheap. Who Paid?", "- $9.1 BILLION")))

    def test_tag_of_another_fact_blocks(self):
        self.assertIn("title-source", blocks(self.check("1. Uber Lost $9.1 Billion. Who Paid? [^F23]")))

    def test_right_tag_and_no_number_pass(self):
        report = self.check("1. Uber Lost $9.1 Billion. Who Paid? [^F22]\n2. Uber Was Cheap. Who Paid?",
                            "- $9.1 BILLION [^F22]")
        self.assertEqual(report.blocks, [], report.render())


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
