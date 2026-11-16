"""Tests of the generation pipeline (S11), with a fake Gemini API: no network, no money."""
import base64
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "whosedime" / "generate"))
import clips  # noqa: E402
import gemini  # noqa: E402
import images  # noqa: E402
import run as runner  # noqa: E402

EVAL = ROOT / "whosedime" / "whosedime-maker" / "evals" / "files" / "01_uber"
KEY = "AIzaFAKEKEY-never-printed-0123456789"


def png_bytes(w=2752, h=1536):
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (w, h), (244, 236, 221)).save(buf, "PNG")
    return buf.getvalue()


def mp4_bytes():
    out = Path(tempfile.mkdtemp()) / "c.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "color=c=0x1e2b45:s=320x180:d=1:r=24",
                    "-pix_fmt", "yuv420p", str(out)], check=True)
    return out.read_bytes()


class FakeApi:
    """Answers like the Interactions API; records every call (method, url, headers, payload)."""

    def __init__(self, fail=None, image=None, video_inline=False):
        self.calls, self.fail = [], list(fail or [])
        self.image = image or png_bytes()
        self.video_inline = video_inline
        self.mp4 = None

    def __call__(self, method, url, headers, body, timeout):
        payload = json.loads(body) if body else None
        self.calls.append((method, url, headers, payload))
        if self.fail:
            code = self.fail.pop(0)
            if code:
                return code, json.dumps({"error": {"message": f"bad call with key {headers.get('x-goog-api-key')}"}}).encode()
        if method == "GET" and "/models" in url:
            return 200, b'{"models": []}'
        if method == "GET" and "files/" in url:
            return 200, self.mp4
        kind = payload["response_format"]["type"]
        if kind == "image":
            part = {"type": "image", "mime_type": "image/png", "data": base64.b64encode(self.image).decode()}
        else:
            self.mp4 = self.mp4 or mp4_bytes()
            part = ({"type": "video", "data": base64.b64encode(self.mp4).decode()} if self.video_inline else
                    {"type": "video", "uri": "https://generativelanguage.googleapis.com/v1beta/files/abc:download"})
        answer = {"steps": [{"type": "user_input", "content": []}, {"type": "model_output", "content": [part]}],
                  "status": "completed", "usage": {"total_output_tokens": 1680}}
        return 200, json.dumps(answer).encode()

    def posts(self):
        return [c for c in self.calls if c[0] == "POST"]


def client(api, key=KEY):
    return gemini.Client(transport=api, key=key, sleep=lambda s: None)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.folder = self.tmp / "01_uber"
        shutil.copytree(EVAL, self.folder)
        self.logs = []

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def log(self, line):
        self.logs.append(line)


class TestPrompts(Base):
    def test_reads_preamble_scenes_and_clips(self):
        p = gemini.prompts(self.folder)
        self.assertGreaterEqual(len(p["scene"]), 50)
        self.assertEqual(len(p["anim"]), 5)
        self.assertIn(1, p["scene"])
        self.assertTrue(set(p["anim"]) <= set(p["scene"]))  # a clip starts from its scene image
        self.assertIn("flat 2D editorial illustration", p["preamble"])

    def test_preamble_loses_chat_sentences_only(self):
        p = gemini.prompts(self.folder)["preamble"]
        for gone in ("reply only", "wait", "message I send", "You are an image generator"):
            self.assertNotIn(gone, p)
        for kept in ("Palette:", "No text, no letters", "exactly two arms"):
            self.assertIn(kept, p)

    def test_range(self):
        self.assertEqual(images.parse_range("1-3,9"), {1, 2, 3, 9})
        self.assertIsNone(images.parse_range(""))


class TestImages(Base):
    def test_three_test_images_then_stop(self):
        api = FakeApi()
        ledger = gemini.Ledger(self.folder)
        r = images.make(self.folder, client(api), gemini.Budget(ledger, None, 3), log=self.log)
        self.assertEqual(len(r["made"]), 3)
        self.assertIn("test budget", r["stopped"])
        self.assertEqual(len(api.posts()), 3)
        from PIL import Image
        for n in r["made"]:
            with Image.open(self.folder / "images" / f"scene_{n:03d}.png") as im:
                self.assertEqual(im.size, (2752, 1536))
        lines = ledger.lines()
        self.assertEqual(len(lines), 3)
        self.assertTrue(all(l["model"] == "gemini-nano-banana-2.1" and l["usd"] >= 0.0504 for l in lines))
        self.assertAlmostEqual(ledger.spent(), sum(l["usd"] for l in lines))

    def test_payload_shape_and_preamble(self):
        api = FakeApi()
        images.make(self.folder, client(api), gemini.Budget(gemini.Ledger(self.folder), None, 1), log=self.log)
        _, url, headers, payload = api.posts()[0]
        self.assertTrue(url.endswith("/v1beta/interactions"))
        self.assertEqual(payload["response_format"], {"type": "image", "mime_type": "image/png",
                                                      "aspect_ratio": "16:9", "image_size": "2K"})
        self.assertFalse(payload["store"])
        self.assertTrue(payload["input"][0]["text"].startswith("Style for every image") or
                        "flat 2D" in payload["input"][0]["text"].split("\n\n")[0])
        self.assertEqual(headers["x-goog-api-key"], KEY)

    def test_no_key_header_without_a_key(self):
        api = FakeApi()
        images.make(self.folder, client(api, key=""), gemini.Budget(gemini.Ledger(self.folder), None, 1), log=self.log)
        self.assertNotIn("x-goog-api-key", api.posts()[0][2])

    def test_resume_skips_existing_and_redo(self):
        api = FakeApi()
        b = lambda n: gemini.Budget(gemini.Ledger(self.folder), None, n)  # noqa: E731
        first = images.make(self.folder, client(api), b(2), log=self.log)["made"]
        second = images.make(self.folder, client(api), b(1), log=self.log)["made"]
        self.assertNotIn(second[0], first)
        again = images.make(self.folder, client(api), b(1), redo={first[0]}, log=self.log)["made"]
        self.assertEqual(again, [first[0]])

    def test_continuity_reference_attached(self):
        p = gemini.prompts(self.folder)
        n = next(n for n, t in sorted(p["scene"].items()) if images.REF_RE.search(t))
        ref = int(images.REF_RE.search(p["scene"][n]).group(1))
        (self.folder / "images").mkdir(exist_ok=True)
        (self.folder / "images" / f"scene_{ref:03d}.png").write_bytes(png_bytes(800, 450))
        api = FakeApi()
        images.make(self.folder, client(api), gemini.Budget(gemini.Ledger(self.folder), None, 1),
                    scenes={n}, log=self.log)
        parts = api.posts()[0][3]["input"]
        self.assertEqual(parts[1]["type"], "image")
        self.assertIn(f"scene_{ref:03d}", parts[0]["text"])

    def test_small_image_enlarged_with_warning(self):
        api = FakeApi(image=png_bytes(1376, 768))
        images.make(self.folder, client(api), gemini.Budget(gemini.Ledger(self.folder), None, 1), log=self.log)
        line = gemini.Ledger(self.folder).lines()[0]
        self.assertIn("enlarged", line["warning"])
        self.assertGreaterEqual(line["px"][0], 2112)

    def test_retry_then_failure_never_prints_key(self):
        api = FakeApi(fail=[429, 0])  # one 429, then success
        r = images.make(self.folder, client(api), gemini.Budget(gemini.Ledger(self.folder), None, 1), log=self.log)
        self.assertEqual(len(r["made"]), 1)
        api = FakeApi(fail=[400])
        r = images.make(self.folder, client(api), gemini.Budget(gemini.Ledger(self.folder), None, 1), log=self.log)
        self.assertEqual(len(r["failed"]), 1)
        text = "\n".join(self.logs) + gemini.Ledger(self.folder).path.read_text()
        self.assertNotIn(KEY, text)
        self.assertIn("<key>", text)
        failed = [l for l in gemini.Ledger(self.folder).lines() if l.get("error")]
        self.assertEqual([l["usd"] for l in failed], [0])

    def test_stops_after_three_failures_in_a_row(self):
        api = FakeApi(fail=[400] * 10)
        r = images.make(self.folder, client(api), gemini.Budget(gemini.Ledger(self.folder), None, 3), log=self.log)
        self.assertEqual(len(api.posts()), 3)
        self.assertIn("3 failures", r["stopped"])

    def test_budget_gate(self):
        ledger = gemini.Ledger(self.folder)
        api = FakeApi()
        r = images.make(self.folder, client(api), gemini.Budget(ledger, 0), log=self.log)
        self.assertEqual(r["made"], [])
        self.assertIn("no approved budget", r["stopped"])
        r = images.make(self.folder, client(api), gemini.Budget(ledger, 0.11), log=self.log)
        self.assertEqual(len(r["made"]), 2)  # 2 x 0.0504 fits, a third would pass $0.11
        self.assertLessEqual(ledger.spent(), 0.11)

    def test_estimate_cli_makes_no_call(self):
        out = subprocess.run([sys.executable, str(ROOT / "whosedime/generate/images.py"), str(self.folder), "--estimate"],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("to make: about $", out.stdout)
        self.assertFalse((self.folder / "generate" / "ledger.jsonl").exists())


class TestClips(Base):
    def make_images(self, numbers):
        (self.folder / "images").mkdir(exist_ok=True)
        for n in numbers:
            (self.folder / "images" / f"scene_{n:03d}.png").write_bytes(png_bytes(960, 540))

    def test_one_test_clip_by_uri(self):
        p = gemini.prompts(self.folder)
        self.make_images(p["anim"])
        api = FakeApi()
        ledger = gemini.Ledger(self.folder)
        r = clips.make(self.folder, client(api), gemini.Budget(ledger, None, 1), log=self.log)
        self.assertEqual(len(r["made"]), 1)
        n = r["made"][0]
        clip = self.folder / "clips" / f"scene_{n:03d}.mp4"
        self.assertEqual(clip.stat().st_size, len(api.mp4))
        posts = api.posts()
        self.assertEqual(len(posts), 1)
        rf = posts[0][3]["response_format"]
        self.assertEqual((rf["resolution"], rf["duration"], rf["delivery"]), ("1080p", "8s", "uri"))
        self.assertEqual(posts[0][3]["input"][0]["type"], "image")
        get = [c for c in api.calls if c[0] == "GET"][0]
        self.assertIn("alt=media", get[1])
        line = ledger.lines()[0]
        self.assertEqual((line["model"], line["usd"]), ("gemini-omni-1.2-flash", 0.832))

    def test_inline_video_and_missing_image(self):
        p = gemini.prompts(self.folder)
        first = sorted(p["anim"])[0]
        self.make_images([first])
        api = FakeApi(video_inline=True)
        r = clips.make(self.folder, client(api), gemini.Budget(gemini.Ledger(self.folder), None, 5), log=self.log)
        self.assertEqual(r["made"], [first])
        self.assertEqual(len(r["no_image"]), len(p["anim"]) - 1)

    def test_not_a_video_is_refused(self):
        p = gemini.prompts(self.folder)
        self.make_images(p["anim"])
        api = FakeApi(video_inline=True)
        api.mp4 = b"not a video"
        r = clips.make(self.folder, client(api), gemini.Budget(gemini.Ledger(self.folder), None, 1), log=self.log)
        self.assertEqual(r["made"], [])
        self.assertFalse(list((self.folder / "clips").glob("*.mp4")))


class TestRun(Base):
    def args(self, **kw):
        ns = dict(test=False, approved_usd=0.0, no_render=True, work=None)
        ns.update(kw)
        return type("A", (), ns)

    def test_status_without_money(self):
        api = FakeApi()
        st = runner.run(self.folder, self.args(), client=client(api), log=self.log)
        self.assertEqual(api.posts(), [])  # never pays without being told
        self.assertEqual(st["steps"]["images"]["status"], "not started")
        self.assertIn("no paid call", st["steps"]["images"]["detail"])
        self.assertEqual(st["steps"]["voice"]["status"], "not started")
        self.assertEqual(st["steps"]["charts"]["status"], "done")
        self.assertTrue(st["next"].startswith("Images"))
        saved = json.loads((self.folder / "generate" / "status.json").read_text())
        self.assertEqual(saved["spent_usd"], 0)

    def test_test_mode_makes_three_images_and_no_clip(self):
        api = FakeApi()
        st = runner.run(self.folder, self.args(test=True), client=client(api), log=self.log)
        self.assertEqual(st["steps"]["images"]["have"], 3)
        self.assertEqual(st["steps"]["images"]["status"], "in progress")
        self.assertEqual(st["paid_calls"], len(api.posts()))
        self.assertLessEqual(len(api.posts()), 4)  # 3 images + at most 1 clip (if its image was among them)

    def test_bad_key_pays_nothing(self):
        api = FakeApi(fail=[403])
        st = runner.run(self.folder, self.args(test=True), client=client(api), log=self.log)
        self.assertEqual(api.posts(), [])
        self.assertIn("no working Gemini key", st["steps"]["images"]["detail"])

    def test_no_scenes_yet(self):
        (self.folder / "03_scenes.md").unlink()
        st = runner.run(self.folder, self.args(), client=client(FakeApi()), log=self.log)
        self.assertEqual(st["steps"]["scenes"]["status"], "not started")

    def test_voice_states(self):
        v = self.folder / "voice"
        v.mkdir(exist_ok=True)
        (v / "listen_20s.json").write_text("{}")
        self.assertEqual(runner.voice_state(self.folder)[0], "waiting for Franco")
        (v / "state.json").write_text(json.dumps({"status": "ready", "rate_total_wpm": 149}))
        self.assertEqual(runner.voice_state(self.folder)[0], "done")


if __name__ == "__main__":
    unittest.main()


class TestNotebook(Base):
    def test_estimate_mode_runs_without_colab_and_pays_nothing(self):
        sys.path.insert(0, str(ROOT / "whosedime" / "notebooks"))
        import launcher
        root = self.tmp / "WhoseDime"
        (root / "Videos").mkdir(parents=True)
        shutil.move(str(self.folder), root / "Videos" / "01_uber")
        ns = launcher.run("generate_whosedime.ipynb", dict(VIDEO="01_uber", MODE="estimate", APPROVED_USD=0.0,
                                                          ROOT=str(root)), {})
        self.assertEqual(ns["FOLDER"].name, "01_uber")
        self.assertFalse((root / "Videos" / "01_uber" / "generate").exists())

    def test_launcher_runs_main_and_the_notebook(self):
        nb = json.loads((ROOT / "whosedime/notebooks/generate_launcher.ipynb").read_text())
        src = "".join(next(c for c in nb["cells"] if c["cell_type"] == "code")["source"])
        self.assertIn('BRANCH = "main"', src)
        self.assertIn('launcher.run("generate_whosedime.ipynb"', src)
        self.assertNotIn("AIza", src)
