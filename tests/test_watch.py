"""Tests of whosedime/watch/watch.py (S09) with a fake YouTube API (no
network): one channel carries a hit, a renamed title and a Short; the report
must list the hit and the rename, and not the Short."""
import datetime as dt
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WATCH = ROOT / "whosedime" / "watch" / "watch.py"


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


W = load(WATCH)
RUN = dt.date(2026, 11, 8)

# Channel A (median 10 000): a hit, a renamed video, a Short, an old video.
# Channel B (median 50 000): one ordinary new video.
VIDEOS = {
    "hit1": dict(ch="UCa", t="Why Klarna Lends for Free", d="2026-11-05", v=80_000, s="PT14M2S"),
    "ren1": dict(ch="UCa", t="Uber Was Cheap. Who Paid?", d="2026-11-03", v=9_000, s="PT12M"),
    "short1": dict(ch="UCa", t="Visa in 60 seconds", d="2026-11-06", v=900_000, s="PT58S"),
    "old1": dict(ch="UCa", t="An old story", d="2026-09-01", v=500_000, s="PT11M"),
    "b1": dict(ch="UCb", t="The Rolex Waitlist Explained", d="2026-11-04", v=40_000, s="PT15M"),
    # search results: one outside channel above 100 K, one below, one Short
    "e1": dict(ch="UCx", t="How Costco Makes Money", d="2026-11-06", v=250_000, s="PT13M"),
    "e2": dict(ch="UCy", t="Small video", d="2026-11-06", v=4_000, s="PT10M"),
    "e3": dict(ch="UCz", t="Huge Short", d="2026-11-06", v=2_000_000, s="PT40S"),
    "e4": dict(ch="UCa", t="Why Klarna Lends for Free", d="2026-11-05", v=80_000, s="PT14M2S"),
}
PLAYLISTS = {"UUa": ["hit1", "ren1", "short1", "old1"], "UUb": ["b1"]}


HANDLES = {"UCa": "@chanA", "UCb": "@chanB"}


class FakeApi:
    def __init__(self, renamed=None, handles=None):
        self.renamed = renamed or {}
        self.handles = dict(HANDLES, **(handles or {}))
        self.log = []

    def __call__(self, endpoint, params):
        self.log.append(endpoint)
        if endpoint == "channels":
            return {"items": [{"id": c, "snippet": {"customUrl": self.handles[c].lower()}}
                              for c in params["id"].split(",") if self.handles.get(c)]}
        if endpoint == "playlistItems":
            return {"items": [{"contentDetails": {
                "videoId": i, "videoPublishedAt": VIDEOS[i]["d"] + "T12:00:00Z"}}
                for i in PLAYLISTS[params["playlistId"]]]}
        if endpoint == "videos":
            items = []
            for i in params["id"].split(","):
                v = VIDEOS[i]
                items.append({"id": i, "snippet": {
                    "title": self.renamed.get(i, v["t"]), "publishedAt": v["d"] + "T12:00:00Z",
                    "channelId": v["ch"], "channelTitle": "Chan " + v["ch"],
                    "defaultAudioLanguage": "en"},
                    "statistics": {"viewCount": str(v["v"])},
                    "contentDetails": {"duration": v["s"]}})
            return {"items": items}
        if endpoint == "search":
            ids = ["e1", "e2", "e3", "e4"]
            return {"items": [{"id": {"videoId": i}} for i in ids]}
        raise AssertionError(endpoint)


CHANNELS = [
    dict(handle="@chanA", title="Chan A", channel_id="UCa", uploads_playlist_id="UUa",
         median_long_views="10000", median_source="test", median_date="2026-11-05"),
    dict(handle="@chanB", title="Chan B", channel_id="UCb", uploads_playlist_id="UUb",
         median_long_views="50000", median_source="test", median_date="2026-11-05"),
]


class WatchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.channels = self.tmp / "channels.csv"
        W.save_channels(CHANNELS, self.channels)
        self.state = self.tmp / "last_run.json"
        self.reports = self.tmp / "reports"

    def run_watch(self, fake, search=True, date=RUN):
        api = W.Api(fetch=fake)
        result, path = W.run(api, date, channels_path=self.channels, state_path=self.state,
                             report_dir=self.reports, brands_path=W.BRANDS_MD,
                             search=search, scan_dir=self.tmp)
        return api, result, path.read_text()

    def test_first_run_then_hit_rename_and_no_short(self):
        api, result, report = self.run_watch(FakeApi())
        self.assertIn("First run", report.split("## Title changes")[1].split("##")[0])
        self.assertTrue(self.state.exists())
        # second run, a week later: ren1 renamed in between
        api, result, report = self.run_watch(
            FakeApi(renamed={"ren1": "Uber's $7.9 Billion Secret"}),
            date=RUN + dt.timedelta(days=1))
        hits = report.split("## Hits")[1].split("##")[0]
        self.assertIn("Why Klarna Lends for Free", hits)
        self.assertIn("8.0×", hits)
        self.assertNotIn("Rolex", hits)                   # 0.8× is not a hit
        renames = report.split("## Title changes")[1].split("##")[0]
        self.assertIn("Uber Was Cheap. Who Paid?", renames)
        self.assertIn("Uber's $7.9 Billion Secret", renames)
        self.assertNotIn("Visa in 60 seconds", report)    # the Short
        self.assertNotIn("Huge Short", report)
        self.assertNotIn("An old story", report)          # outside the windows
        self.assertEqual(result["shorts_skipped"], 1)
        # the hit was already a hit at the first run: not new
        self.assertEqual([h["first_seen"] for h in result["hits"]], [False])

    def test_units_counted_and_written(self):
        fake = FakeApi()
        api, result, report = self.run_watch(fake)
        # 1 channels (handles) + 2 playlistItems + 1 videos (tracked)
        # + 2 search + 1 videos (search)
        self.assertEqual(api.units, 1 + 2 + 1 + 200 + 1)
        self.assertEqual(fake.log.count("search"), 2)
        self.assertIn(f"**Quota: {api.units} units** of 300", report)
        self.assertEqual(json.loads(self.state.read_text())["units"], api.units)

    # ------------------------------------------------- checks (S10, task 3)

    def checks(self, report):
        line = next(l for l in report.splitlines() if l.startswith("**Checks**"))
        return line

    def test_checks_clean_run(self):
        api, result, report = self.run_watch(FakeApi(), search=False)
        line = self.checks(report)
        self.assertIn("(0 flagged)", line)
        self.assertIn("run date not reported before", line)
        self.assertIn("no handle moved", line)
        self.assertIn(f"units within budget ({api.units} of 300 today)", line)
        self.assertLess(report.index("**Checks**"), report.index("## Hits"))

    def test_rerun_refused_without_force(self):
        self.run_watch(FakeApi())                         # 205 units
        fake = FakeApi()
        with self.assertRaises(W.RunRefused):
            self.run_watch(fake, search=False)
        self.assertEqual(fake.log, [])                    # no unit spent
        api, result, report = self.run_watch_forced(FakeApi())
        line = self.checks(report)
        self.assertIn("already reported: rerun forced", line)
        self.assertIn("**units over budget: ", line)      # 205 + 205 > 300
        self.assertEqual(json.loads(self.state.read_text())["day_units"], 410)

    def run_watch_forced(self, fake):
        api = W.Api(fetch=fake)
        result, path = W.run(api, RUN, channels_path=self.channels, state_path=self.state,
                             report_dir=self.reports, brands_path=W.BRANDS_MD,
                             search=True, scan_dir=self.tmp, force=True)
        return api, result, path.read_text()

    def test_thin_median_flagged(self):
        rows = [dict(CHANNELS[0], title="How They Make Billions",
                     median_source="all uploads (2 long; fragile)"),
                dict(CHANNELS[1], median_source="full catalogue (chaines_C.csv)")]
        W.save_channels(rows, self.channels)
        (self.tmp / "chaines_C.csv").write_text("handle,videos_longues\n@chanB,4\n")
        api, result, report = self.run_watch(FakeApi(), search=False)
        line = self.checks(report)
        self.assertIn("2 median(s) on fewer than 5 videos", line)
        self.assertIn("How They Make Billions: 2", line)
        self.assertIn("Chan B: 4", line)

    def test_moved_handle_flagged_and_updated(self):
        api, result, report = self.run_watch(FakeApi(handles={"UCb": "@chanB_new"}),
                                             search=False)
        self.assertIn("**handle moved**: @chanB is now @chanb_new", self.checks(report))
        self.assertIn("@chanb_new", self.channels.read_text())

    def test_quiet_channel_flagged(self):
        api, result, report = self.run_watch(FakeApi(), search=False,
                                             date=RUN + dt.timedelta(days=61))
        line = self.checks(report)
        self.assertIn("2 channel(s) with no upload for 60 days", line)
        self.assertIn("@chanA (last 2026-11-06)", line)

    def test_budget_refuses_extra_call(self):
        api = W.Api(fetch=FakeApi(), budget=150)
        api.get("search", q="x")
        with self.assertRaises(W.BudgetExceeded):
            api.get("search", q="y")
        self.assertEqual(api.units, 100)

    def test_search_skipped_when_budget_short(self):
        api = W.Api(fetch=FakeApi(), budget=100)
        result, path = W.run(api, RUN, channels_path=self.channels, state_path=self.state,
                             report_dir=self.reports, brands_path=W.BRANDS_MD, scan_dir=self.tmp)
        self.assertIsNone(result["search"])
        self.assertLess(api.units, 100)
        self.assertIn("search skipped", path.read_text())

    def test_new_entrants_proposed_only_outside_list_and_above_threshold(self):
        api, result, report = self.run_watch(FakeApi())
        self.assertEqual([v["id"] for v in result["entrants"]], ["e1"])
        part = report.split("## New entrants")[1].split("##")[0]
        self.assertIn("How Costco Makes Money", part)
        self.assertNotIn("Small video", part)
        self.assertIn("Franco decides", part)
        self.assertEqual(len(W.load_channels(self.channels)), 2)   # nothing added

    def test_brands_covered_from_marques(self):
        api, result, report = self.run_watch(FakeApi())
        names = {b["brand"] for b in result["brands"]}
        self.assertEqual(names, {"Klarna", "Rolex", "Costco", "Uber"})
        self.assertNotIn("Visa et Mastercard", names)      # only in the Short
        part = report.split("## Brands covered")[1]
        self.assertIn("Gap column today", part)

    def test_brand_terms(self):
        brands = W.load_brands(W.BRANDS_MD)
        self.assertEqual(len(brands), 40)
        find = lambda t: {b["brand"] for b in W.brands_in(t, brands)}
        self.assertEqual(find("Why Dominos Won"), {"Domino's"})
        self.assertEqual(find("McDonald’s $5 Meal"), {"McDonald's"})
        self.assertEqual(find("The Amex Trick"), {"American Express"})
        self.assertEqual(find("Pineapple Express"), set())
        self.assertEqual(find("Apple Pay vs the App Store"), {"Apple Pay", "Apple App Store"})

    def test_tiny_hit_counted_not_listed(self):
        rows = [dict(CHANNELS[0], median_long_views="10")]      # 5x = 50 views
        facts = {"x": dict(id="x", title="Tiny", published="2026-11-06", channel_id="UCa",
                           channel_title="A", lang="en", views=900, dur=700)}
        result = W.build(RUN, rows, {"@chanA": [("x", "2026-11-06")]}, facts, None)
        self.assertEqual(len(result["hits"]), 1)
        report = W.render(result, W.Api(fetch=FakeApi()))
        hits = report.split("## Hits")[1].split("## New")[0]
        self.assertNotIn("Tiny", hits)
        self.assertIn("1 videos — @chanA 1", hits)

    def test_handle_updated_when_channel_moved(self):
        (self.tmp / "videos_C.csv").write_text(
            "handle,video_id,date,titre,duree_s,vues,likes,commentaires\n"
            "@chanA,hit1,2026-11-05,t,842,1,0,0\n")
        rows = [dict(handle="@chanA", title="", channel_id="", uploads_playlist_id="")]

        def fake(endpoint, params):
            if endpoint == "videos":
                return FakeApi()(endpoint, params)
            return {"items": [{"id": "UCa", "snippet": {"title": "Chan A",
                                                         "customUrl": "@chana114"},
                               "contentDetails": {"relatedPlaylists": {"uploads": "UUa"}}}]}
        warnings = W.resolve_ids(W.Api(fetch=fake), rows, self.tmp)
        self.assertEqual(rows[0]["handle"], "@chana114")
        self.assertIn("@chanA is now @chana114", warnings[0])

    def test_parse_duration(self):
        self.assertEqual(W.parse_duration("PT3M"), 180)
        self.assertEqual(W.parse_duration("PT1H2M3S"), 3723)
        self.assertEqual(W.parse_duration(None), 0)

    def test_resolve_ids_from_scan_videos(self):
        (self.tmp / "videos_C.csv").write_text(
            "handle,video_id,date,titre,duree_s,vues,likes,commentaires\n"
            "@chanA,hit1,2026-11-05,t,842,1,0,0\n")
        rows = [dict(handle="@chanA", title="", channel_id="", uploads_playlist_id="",
                     median_long_views="1")]

        def fake(endpoint, params):
            if endpoint == "videos":
                return FakeApi()(endpoint, params)
            self.assertEqual(params["id"], "UCa")
            return {"items": [{"id": "UCa", "snippet": {"title": "Chan A", "customUrl": "@chana"},
                               "contentDetails": {"relatedPlaylists": {"uploads": "UUa"}}}]}
        api = W.Api(fetch=fake)
        warnings = W.resolve_ids(api, rows, self.tmp)
        self.assertEqual(warnings, [])
        self.assertEqual(rows[0]["uploads_playlist_id"], "UUa")
        self.assertEqual(api.units, 2)

    def test_channels_csv_seeded_from_scan(self):
        rows = W.channels_from_scan()
        self.assertEqual(len(rows), 47)
        self.assertEqual(rows[0]["handle"], "@ColdFusion")


if __name__ == "__main__":
    unittest.main()
