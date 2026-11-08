"""Tests of the Whose Dime charts and assembly (S07): whosedime/whosedime-video/, the palette, the notebook.

The assembly runs on a short folder (tests/whosedime_video_fixture.py): 10 scenes cut from the Uber
eval run, generated images and clip, a stub voice. Renders are made at 640x360 with the ultrafast
preset to keep the suite quick; the notebook test renders a two-scene extract at 1920x1080.
"""
import importlib.util
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
VIDEO = ROOT / "whosedime" / "whosedime-video"
NB = ROOT / "whosedime" / "notebooks"
UBER = ROOT / "whosedime" / "whosedime-maker" / "evals" / "files" / "01_uber"
PALETTE = ROOT / "whosedime" / "common" / "palette.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(VIDEO / "scripts"))
sys.path.insert(0, str(NB))

import assemble as A  # noqa: E402
import charts as C  # noqa: E402
import whosedime_video_fixture as FX  # noqa: E402

HEX_RE = re.compile(r"#[0-9A-Fa-f]{6}\b")
SMALL = (640, 360)


def foreign_colours(paths, palette):
    """[(file, colour)] of every #RRGGBB in the files that is not a colour of the palette."""
    allowed = {v.upper() for v in palette["colors"].values()}
    out = []
    for p in paths:
        for m in HEX_RE.findall(Path(p).read_text(encoding="utf-8", errors="ignore")):
            if m.upper() not in allowed:
                out.append((str(p), m))
    return out


def channel_files():
    roots = [ROOT / "whosedime", ROOT / "docs" / "whosedime"]
    skip = {"corpus", "__pycache__"}
    return [p for r in roots for p in r.rglob("*") if p.is_file() and p.suffix in (".md", ".py", ".json", ".txt", ".ipynb")
            and not skip & set(p.parts) and p != PALETTE]


class Palette(unittest.TestCase):
    def setUp(self):
        self.pal = json.loads(PALETTE.read_text(encoding="utf-8"))

    def test_one_source_no_other_colour(self):
        self.assertEqual(foreign_colours(channel_files(), self.pal), [])

    def test_a_different_colour_elsewhere_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "03_scenes.md"
            bad.write_text("Palette: cream #F4ECDD, dollar green #2F7A56.\n", encoding="utf-8")
            self.assertEqual(foreign_colours([bad], self.pal), [(str(bad), "#2F7A56")])

    def test_prompt_line_is_the_colours(self):
        line = ", ".join(f"{self.pal['names'][k]} {v}" for k, v in self.pal["colors"].items())
        self.assertEqual(self.pal["prompt_line"], line)

    def test_eval_scenes_and_preamble_copy_the_prompt_line(self):
        text = (UBER / "03_scenes.md").read_text(encoding="utf-8")
        self.assertIn(f"Palette (channel, every image and chart): {self.pal['prompt_line']}.", text)
        self.assertIn(f"Palette: {self.pal['prompt_line']}.", text)
        step4 = (ROOT / "whosedime" / "whosedime-maker" / "references" / "step4_scenes.md").read_text(encoding="utf-8")
        self.assertIn("whosedime/common/palette.json", step4)
        self.assertEqual(HEX_RE.findall(step4), [], "step4_scenes.md points to palette.json, it holds no colour")

    def test_charts_and_cards_read_it(self):
        rgb = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for k, v in self.pal["colors"].items()}
        self.assertEqual(C.PAL["background"], rgb[self.pal["roles"]["background"]])
        self.assertEqual(C.PAL["ink"], rgb[self.pal["roles"]["ink"]])
        card = A.Scene(1, "chapter", "", "—", "THE DECISION", "")
        self.assertEqual(tuple(A.card_image(card, *SMALL)[5, 5]), rgb["cream"])


class Charts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.registry = C.checker.Registry(UBER / "02b_factcheck.md")
        cls.written, cls.refused = C.draw_folder(UBER, out=Path(cls.tmp) / "charts", log=lambda *a: None)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_the_25_uber_charts_render(self):
        self.assertEqual(self.refused, [])
        self.assertEqual(len(self.written), 25)
        for p in self.written:
            with Image.open(p) as im:
                self.assertEqual(im.size, (1920, 1080), p.name)

    def test_unverified_fact_refused(self):
        with self.assertRaisesRegex(C.ChartError, r"F27 is still \[TO VERIFY\]"):
            C.build_spec(9, "F27 · number · James Farrar", self.registry)

    def test_number_not_in_its_fact_refused(self):
        with self.assertRaisesRegex(C.ChartError, r"'4.5 billion' is not in the fact\(s\) it cites \(F07\)"):
            C.build_spec(9, "F07 · number · $4.5 billion into Uber, June 1, 2016", self.registry)
        with self.assertRaisesRegex(C.ChartError, r"'41' is not in"):           # a true number, from another fact
            C.build_spec(9, "F07 · split · riders paid 41%", self.registry)

    def test_no_id_and_unknown_id_refused(self):
        with self.assertRaisesRegex(C.ChartError, "cites no fact id"):
            C.build_spec(9, "— · number · $3.5 billion", self.registry)
        with self.assertRaisesRegex(C.ChartError, "F99 is not an id"):
            C.build_spec(9, "F99 · number · $3.5 billion", self.registry)

    def test_a_refused_chart_leaves_no_png(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            for name in ("02b_factcheck.md", "03_scenes.md"):
                shutil.copy(UBER / name, folder / name)
            scenes = folder / "03_scenes.md"
            scenes.write_text(scenes.read_text(encoding="utf-8").replace(
                "F09 · number · $20 million settlement, January 2017", "F27 · number · $20 million settlement"),
                encoding="utf-8")
            (folder / "charts").mkdir()
            Image.new("RGB", (4, 4)).save(folder / "charts" / "scene_051.png")       # a stale chart
            written, refused = C.draw_folder(folder, log=lambda *a: None)
            self.assertEqual(len(written), 24)
            self.assertEqual(len(refused), 1)
            self.assertIn("scene 51", refused[0])
            self.assertFalse((folder / "charts" / "scene_051.png").exists())

    def test_reading_the_cells(self):
        s = C.build_spec(11, "F06 · compare · year ending September 2015: losses $2 billion, revenue $1.4 billion",
                         self.registry)
        self.assertEqual(s.title, "Year ending September 2015")
        self.assertEqual([(i.label, i.value.shown) for i in s.items],
                         [("Losses", "$2 billion"), ("Revenue", "$1.4 billion")])
        s = C.build_spec(87, "F01, F04, F07, F14, F18, F24 · timeline · 2008 Paris; May 31, 2010 launch; "
                         "June 1, 2016 $3.5 billion; May 2019 IPO; February 19, 2021 ruling; 2023 first operating profit",
                         self.registry)
        self.assertEqual([C.DATE_RE.search(i.text).group(0) for i in s.items],
                         ["2008", "May 31, 2010", "June 1, 2016", "May 2019", "February 19, 2021", "2023"])
        s = C.build_spec(35, "F13 · number · accumulated deficit about $7.9 billion, end of 2018", self.registry)
        self.assertEqual((s.items[0].value.qualifier, s.items[0].value.shown, s.items[0].tone), ("about", "$7.9 billion", "loss"))

    def test_bars_only_for_comparable_values(self):
        s = C.build_spec(42, "F14 · compare · priced at $45 a share; raised $8.1 billion; first day closed below $45",
                         self.registry)
        self.assertFalse(C.comparable(s.items, 50))
        s = C.build_spec(25, "F07 · compare · invested $3.5 billion; valuation $62.5 billion", self.registry)
        self.assertTrue(C.comparable(s.items, 50))

    def spec(self, n):
        cell = dict(C.chart_rows(UBER / "03_scenes.md"))[n]
        return C.build_spec(n, cell, self.registry)

    def test_colour_by_meaning(self):
        """S07b: gain green only for profit/revenue, loss coral only for money lost (settings.json, charts); S07c (D14): on money only."""
        tones = lambda n: [i.tone for i in self.spec(n).items]
        self.assertNotIn("gain", tones(50))                       # "only 10 percent earned $90,000": not a gain
        self.assertEqual(tones(77), ["loss", "gain"])             # 2022 loss coral, 2023 profit green
        self.assertEqual(tones(11), ["loss", "gain"])             # losses coral, revenue green
        self.assertEqual(tones(25), ["ink", "ink"])               # invested, valuation: not the company's income
        self.assertEqual(tones(68), ["ink", "ink"])               # warnings, cut off: not money (draw_scale colours it)
        self.assertEqual(tones(82), ["ink", "gain", "ink", "ink"])  # D14: 950 owners bankrupt are people, not money
        self.assertEqual(tones(35), ["loss"])                     # D14: a loss in $ keeps its coral
        self.assertEqual(tones(76), ["loss", "loss"])
        self.assertEqual(C.GAIN_RE.pattern, C.word_re(C.SETTINGS["charts"]["gain_words"]).pattern)
        self.assertTrue(C.LOSS_RE.search("bankruptcy") and not C.LOSS_RE.search("fell"))

    def test_colour_drawn(self):
        """Scene 50 has no gain-green pixel; scene 25 (bars, no gain or loss) draws its last bar in mustard."""
        def has(n, role):
            with Image.open(Path(self.tmp) / "charts" / f"scene_{n:03d}.png") as im:
                return any(c == C.PAL[role] for _, c in im.convert("RGB").getcolors(1 << 20))
        self.assertFalse(has(50, "gain"))
        self.assertTrue(has(25, "highlight") and not has(25, "gain"))
        self.assertTrue(has(77, "gain") and has(77, "loss"))
        self.assertFalse(has(82, "loss"))                          # D14: no coral on a count of people

    def test_icons_layout(self):
        """S07b: one figure size per chart, at least icons_min_cell px, the block centred in the free area."""
        cfg = C.SETTINGS["charts"]
        for n, items in ((61, 2), (70, 1)):
            s = self.spec(n)
            cv = C.Canvas()
            top, bottom = cv.frame(s)
            blocks = C.icons_layout(s, top, bottom, cv)
            self.assertEqual(len(blocks), items)
            self.assertEqual(len({b.cell for b in blocks}), 1, f"scene {n}: two figure sizes")
            self.assertGreaterEqual(blocks[0].cell, cfg["icons_min_cell"], f"scene {n}")
            self.assertEqual(len({b.grid[1] for b in blocks}), 1, f"scene {n}: blocks not on one top line")
            y0, y1 = min(b.box[1] for b in blocks), max(b.box[3] for b in blocks)
            self.assertLess(abs((y0 + y1) / 2 - (top + bottom) / 2), 40, f"scene {n}: block not centred")
            self.assertGreaterEqual(y0, top)
            self.assertLessEqual(y1, bottom)
            for b in blocks:
                self.assertGreaterEqual(b.cols * b.rows, b.n_icons)
                gw = b.cell * (b.cols + cfg["icons_gap"] * (b.cols - 1))
                self.assertAlmostEqual(b.grid[2] - b.grid[0], gw, places=3)
        self.assertEqual([(b.cols, b.rows) for b in C.icons_layout(self.spec(61), *C.Canvas().frame(self.spec(61)))][1],
                         (5, 3))                                   # 15 days: 5 x 3, no ragged row

    def test_source_line_follows_same_as(self):
        self.assertEqual(C.short_source("F08", self.registry), "Fortune, 2016-06-01")
        self.assertEqual(C.short_source("F10", self.registry), "The Register, 2017-01-20")


class Assembly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.folder = FX.make_folder(cls.tmp)
        cls.quiet = staticmethod(lambda *a: None)
        cls.verdict = A.run(cls.folder, size=SMALL, preset="ultrafast", log=cls.quiet)
        cls.render = cls.folder / "render"

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def copy(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        dst = tmp / "Videos" / self.folder.name
        shutil.copytree(self.folder, dst, ignore=shutil.ignore_patterns("render"))
        return dst

    def test_short_render_passes_the_technical_check(self):
        self.assertTrue(self.verdict["ready"], self.verdict)
        self.assertEqual(self.verdict["output"], "video.mp4")
        self.assertTrue(all(c.startswith("✓") for c in self.verdict["check"]))
        self.assertRegex(self.verdict["code"], r"^[\w./-]+@[0-9a-f]{7,}$")
        for name in ("video.mp4", "report_video.json", "verdict_video.json", "chapters.txt", "plan.json"):
            self.assertTrue((self.render / name).is_file(), name)
        self.assertEqual(len(list((self.render / "preview_video").glob("*.jpg"))), 6)
        self.assertLessEqual(len((self.render / "verdict_video.json").read_bytes()), 1000)

    def test_scenes_follow_the_voice(self):
        p = A.plan(self.folder, files=False, log=self.quiet)
        scenes, total = p["scenes"], p["total"]
        for a, b in zip(scenes, scenes[1:]):
            self.assertAlmostEqual(a.end, b.start, places=6)
        words, duration = A.load_words(self.folder)
        self.assertAlmostEqual(total, duration + 2 * 2.5 + 1.5, places=3)
        for s in scenes:
            if not s.card:
                self.assertGreaterEqual(s.coverage, 0.8, f"scene {s.n}")
        # scene 5 ("Uber launched ... May 31, 2010") starts just before its first word, after the title card
        s5 = scenes[4]
        first = next(w for w in words if w["word"] == "Uber" and w["start_s"] > scenes[2].voice_start)
        self.assertAlmostEqual(s5.start, first["start_s"] + 2.5 - 0.25, delta=0.05)

    def test_chapters(self):
        lines = (self.render / "chapters.txt").read_text(encoding="utf-8").splitlines()
        self.assertEqual([l.split(" ", 1)[1] for l in lines], ["Cold open", "Who pays?", "The decision"])
        self.assertEqual(lines[0].split()[0], "0:00")
        plan = json.loads((self.render / "plan.json").read_text(encoding="utf-8"))
        title = next(s for s in plan["scenes"] if s["type"] == "title")
        self.assertEqual(lines[1].split()[0], A.minutes(title["start_s"]))

    def test_chapter_labels_from_the_publication(self):
        folder = self.copy()
        (folder / "04_publication.md").write_text("0:00 Cold open\n--:-- Who pays?\n--:-- The big bet\n", encoding="utf-8")
        p = A.plan(folder, files=False, log=self.quiet)
        self.assertEqual([l.split(" ", 1)[1] for l in p["plan"]["chapters"]], ["Cold open", "Who pays?", "The big bet"])

    def test_extract_leaves_the_full_verdict_untouched(self):
        before = {n: (self.render / n).read_bytes() for n in ("verdict_video.json", "report_video.json", "chapters.txt")}
        v = A.run(self.folder, only=(2, 4), size=SMALL, preset="ultrafast", log=self.quiet)
        self.assertEqual(v["output"], "extract_002-004.mp4")
        self.assertTrue(v["ready"], v)
        self.assertTrue((self.render / "verdict_extract_002-004.json").is_file())
        self.assertTrue((self.render / "preview_extract_002-004").is_dir())
        for n, data in before.items():
            self.assertEqual((self.render / n).read_bytes(), data, n)

    def test_gate_blocks_a_to_verify_fact(self):
        folder = self.copy()
        scenes = folder / "03_scenes.md"
        text = scenes.read_text(encoding="utf-8")
        scenes.write_text(text.replace("| F04 · timeline ·", "| F27 · timeline ·"), encoding="utf-8")
        with self.assertRaisesRegex(A.AssemblyError, r"(?s)D4.*F27 is to verify"):
            A.plan(folder, log=self.quiet)

    def test_gate_blocks_a_registry_changed_since_signed(self):
        folder = self.copy()
        reg = folder / "02b_factcheck.md"
        reg.write_text(reg.read_text(encoding="utf-8").replace("Garrett Camp's idea", "Garrett Camp's first idea"),
                       encoding="utf-8")
        with self.assertRaisesRegex(A.AssemblyError, "changed since it was signed"):
            A.plan(folder, log=self.quiet)

    def test_gate_blocks_a_voice_not_ready(self):
        folder = self.copy()
        (folder / "voice" / "state.json").write_text('{"status": "running"}', encoding="utf-8")
        with self.assertRaisesRegex(A.AssemblyError, "not ready"):
            A.plan(folder, log=self.quiet)

    def test_a_chart_the_tool_cannot_draw_stops_the_assembly(self):
        folder = self.copy()
        scenes = folder / "03_scenes.md"
        text = scenes.read_text(encoding="utf-8")
        scenes.write_text(text.replace("F04 · timeline · launch in San Francisco, May 31, 2010",
                                       "F04 · map · launch in San Francisco, May 31, 2010"), encoding="utf-8")
        with self.assertRaisesRegex(A.AssemblyError, r"(?s)Charts refused.*scene 5: map chart"):
            A.plan(folder, log=self.quiet)

    def test_missing_image_stops_missing_clip_warns(self):
        folder = self.copy()
        shutil.rmtree(folder / "clips")
        p = A.plan(folder, log=self.quiet)
        self.assertIn("scene 1: no clip, its image is used (zoom_in)", p["warnings"])
        (folder / "images" / "scene_002.png").unlink()
        with self.assertRaisesRegex(A.AssemblyError, "images/scene_002.png"):
            A.plan(folder, log=self.quiet)

    def test_find_video(self):
        root = self.folder.parent.parent
        self.assertEqual(A.find_video(root, "99_test"), self.folder)
        with self.assertRaises(A.AssemblyError):
            A.find_video(root, "")      # its whole video is ready: nothing waits
        with self.assertRaises(A.AssemblyError):
            A.find_video(root, "00_none")


class Notebooks(unittest.TestCase):
    def cells(self, name):
        return json.loads((NB / name).read_text(encoding="utf-8"))["cells"]

    def params(self, source):
        return re.findall(r"^(\w+) = .*# @param", source, re.M)

    def test_code_cells_compile(self):
        for name in ("assembly_whosedime.ipynb", "assembly_launcher.ipynb"):
            for i, c in enumerate(self.cells(name)):
                if c["cell_type"] == "code":
                    compile("".join(c["source"]), f"{name}[{i}]", "exec")

    def test_launcher_passes_every_setting_and_runs_main(self):
        main = [c for c in self.cells("assembly_whosedime.ipynb") if "settings" in c["metadata"].get("tags", [])]
        self.assertEqual(len(main), 1)
        settings = self.params("".join(main[0]["source"]))
        launch = "".join(next(c for c in self.cells("assembly_launcher.ipynb") if c["cell_type"] == "code")["source"])
        self.assertEqual(self.params(launch), settings)
        passed = re.search(r"dict\((.*?)\), globals\(\)", launch, re.S).group(1)
        self.assertEqual(re.findall(r"(\w+)=", passed), settings)
        self.assertIn('BRANCH = "main"', launch)
        self.assertIn("print(f\"▶ Running {BRANCH} @ {COMMIT}\")", launch)
        self.assertIn('launcher.run("assembly_whosedime.ipynb"', launch)

    def test_notebook_runs_through_the_launcher(self):
        spec = importlib.util.spec_from_file_location("launcher", NB / "launcher.py")
        L = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(L)
        with tempfile.TemporaryDirectory() as tmp:
            folder = FX.make_folder(tmp)
            ns = L.run("assembly_whosedime.ipynb", dict(VIDEO=folder.name, MODE="plan", SCENES="", ROOT=tmp), {})
            self.assertEqual(ns["RESULT"]["chapters"][0], "0:00 Cold open")
            ns = L.run("assembly_whosedime.ipynb", dict(VIDEO="", MODE="extract", SCENES="3-4", ROOT=tmp), {})
            self.assertEqual(ns["FOLDER"], folder)
            self.assertTrue(ns["RESULT"]["ready"], ns["RESULT"])
            self.assertIn("✓ size: 1920x1080", ns["RESULT"]["check"])
            self.assertFalse((folder / "render" / "verdict_video.json").exists())


if __name__ == "__main__":
    unittest.main()
