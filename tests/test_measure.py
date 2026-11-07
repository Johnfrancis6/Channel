"""Tests of whosedime/research/tools/measure.py on short hand-counted texts,
and of the agreement between storytelling_rules.md and style_thresholds.json."""
import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESEARCH = ROOT / "whosedime" / "research"


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


M = load(RESEARCH / "tools" / "measure.py")

# Hand count (0-based word index in brackets):
# Travis[0] Kalanick[1] had a problem. | But[5] nobody saw it yet[9]. |
# In 2009, a black car cost $100 an hour in San Francisco. |
# He said, "Everyone should have a private driver." | Would you pay for that? |
# Investors did, until[37] the money ran out.
# 42 words; sentence lengths 5, 5, 12, 8, 5, 7.
TEXT = ('Travis Kalanick had a problem. But nobody saw it yet. In 2009, a black car '
        'cost $100 an hour in San Francisco. He said, "Everyone should have a private '
        'driver." Would you pay for that? Investors did, until the money ran out.')


class MeasureHandCounted(unittest.TestCase):
    def setUp(self):
        self.m = M.measure(TEXT, duration_s=21)

    def test_counts(self):
        self.assertEqual(self.m["words"], 42)
        self.assertEqual(self.m["sentences"], 6)
        self.assertEqual(self.m["wpm"], 120.0)            # 42 / (21/60)

    def test_sentence_lengths(self):
        self.assertEqual(self.m["sentence_mean"], 7.0)    # 42 / 6
        self.assertEqual(self.m["sentence_sd"], 2.76)     # sqrt(38 / 5)
        self.assertEqual(self.m["share_over_25"], 0.0)

    def test_people_and_tension(self):
        self.assertEqual(self.m["words_before_first_person"], 0)
        self.assertEqual(self.m["distinct_people"], 1)
        self.assertEqual(self.m["people_mentions_per_150"], 3.57)   # 1 * 150 / 42
        self.assertEqual(self.m["words_before_first_tension"], 5)   # "But"

    def test_per_thousand(self):
        self.assertEqual(self.m["contrast_per_1000"], 47.62)  # but, yet
        self.assertEqual(self.m["dialogue_per_1000"], 23.81)  # one quoted line
        self.assertEqual(self.m["questions_per_1000"], 23.81)  # "Would you pay for that?"
        self.assertEqual(self.m["you_per_1000"], 23.81)

    def test_numbers(self):
        self.assertEqual(self.m["numbers_per_100"], 4.76)  # 2009, $100
        self.assertEqual(self.m["numbers_first_60"], 2)

    def test_openers(self):
        self.assertEqual(self.m["top_opener_count"], 1)
        self.assertEqual(self.m["top_connector"], "but")
        self.assertEqual(self.m["top_connector_count"], 1)


class MeasureEdgeCases(unittest.TestCase):
    def test_jargon_explained(self):
        m = M.measure("The company used leverage, which means borrowed money. Then came the IPO.")
        self.assertEqual(m["words"], 12)
        self.assertEqual(m["jargon_distinct"], 2)
        self.assertEqual(m["jargon_explained_share"], 0.5)  # leverage yes, IPO no
        self.assertEqual(m["jargon_per_1000"], 166.67)

    def test_name_stops_at_punctuation(self):
        m = M.measure("They called him Jordan. They left early. Nobody cared.")
        self.assertEqual(m["distinct_people"], 0)

    def test_title_and_registry(self):
        m = M.measure("Then CEO Dara Khosrowshahi arrived. Khosrowshahi cut costs.")
        self.assertEqual(m["distinct_people"], 1)
        self.assertEqual(m["people_mentions_per_150"], round(2 * 150 / 8, 2))  # 8 words, 2 mentions
        m = M.measure("Garrett Camp had an idea.", people=["Garrett Camp"])
        self.assertEqual(m["words_before_first_person"], 0)

    def test_number_runs_count_once(self):
        m = M.measure("It lost $1.5 billion, then twenty-two thousand drivers left.")
        self.assertEqual(m["numbers_per_100"], round(2 * 100 / 9, 2))

    def test_caption_cleaning(self):
        m = M.measure("[music] >> Hello there. [Music] Bye now.")
        self.assertEqual(m["words"], 4)

    def test_french_connector(self):
        m = M.measure("Il part. Sauf que non. Sauf que oui. Et voilà.", lang="fr")
        self.assertEqual(m["top_connector"], "sauf")
        self.assertEqual(m["top_connector_count"], 2)
        self.assertIsNone(m["jargon_per_1000"])


class RulesAgree(unittest.TestCase):
    def test_md_and_json_hold_the_same_rules(self):
        data = json.loads((RESEARCH / "style_thresholds.json").read_text())
        md = (RESEARCH / "storytelling_rules.md").read_text()
        table = md[md.index("<!-- rules:start -->"):md.index("<!-- rules:end -->")]
        md_ids = re.findall(r"^\| (S\d+) \| [^|]+\| `", table, re.M)
        json_ids = [r["id"] for r in data["rules"]]
        self.assertEqual(md_ids, json_ids)
        metrics = set(M.measure("Word.").keys())
        for r in data["rules"]:
            self.assertIn(r["metric"], metrics)
            self.assertIn(r["level"], ("block", "warn"))
            self.assertTrue(r["min"] is not None or r["max"] is not None)
            self.assertIn(f"`{r['metric']}`", table)


if __name__ == "__main__":
    unittest.main()
