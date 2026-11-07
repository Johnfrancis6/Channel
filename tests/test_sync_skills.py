"""Tests of tools/sync_skills.py: reproducible VERSION and archive, drift check."""
import contextlib
import importlib.util
import io
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sync = load(ROOT / "tools" / "sync_skills.py")


def make_repo(root):
    """A tiny repo: one skill per channel, one of them with evals/."""
    a = root / "zehon" / "alpha"
    (a / "references").mkdir(parents=True)
    (a / "evals").mkdir()
    (a / "SKILL.md").write_text("---\nname: alpha\n---\nAlpha.\n", encoding="utf-8")
    (a / "references" / "one.md").write_text("one\n", encoding="utf-8")
    (a / "evals" / "evals.json").write_text("[]\n", encoding="utf-8")
    b = root / "whosedime" / "beta"
    b.mkdir(parents=True)
    (b / "SKILL.md").write_text("---\nname: beta\n---\nBeta.\n", encoding="utf-8")
    (root / "zehon" / "notes").mkdir()  # no SKILL.md: not a skill
    return a, b


def quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


class SyncSkills(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.alpha, self.beta = make_repo(self.tmp)

    def test_both_channels_found_and_synced(self):
        self.assertEqual([s.name for s in sync.skills(self.tmp)], ["alpha", "beta"])
        self.assertEqual(sync.sync(self.tmp), ["alpha", "beta"])
        self.assertTrue((self.tmp / "zehon" / "alpha.skill").is_file())
        self.assertTrue((self.tmp / "whosedime" / "beta.skill").is_file())
        self.assertFalse((self.tmp / ".claude" / "skills" / "notes").exists())
        self.assertEqual(sync.drift(self.tmp), [])

    def test_same_source_same_version_and_bytes(self):
        sync.sync(self.tmp)
        first_version = sync.version(self.alpha)
        first_bytes = (self.tmp / "zehon" / "alpha.skill").read_bytes()
        copy = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, copy)
        make_repo(copy)
        sync.sync(copy)
        self.assertRegex(first_version, r"^[0-9a-f]{12}$")
        self.assertEqual(sync.version(copy / "zehon" / "alpha"), first_version)
        self.assertEqual((copy / "zehon" / "alpha.skill").read_bytes(), first_bytes)
        mirror_version = (self.tmp / ".claude" / "skills" / "alpha" / "VERSION").read_text().strip()
        self.assertEqual(mirror_version, first_version)
        with zipfile.ZipFile(io.BytesIO(first_bytes)) as z:
            self.assertEqual(z.read("alpha/VERSION").decode().strip(), first_version)

    def test_one_changed_byte_changes_version(self):
        before = sync.version(self.alpha)
        (self.alpha / "references" / "one.md").write_text("onf\n", encoding="utf-8")
        self.assertNotEqual(sync.version(self.alpha), before)

    def test_evals_not_in_archive(self):
        with zipfile.ZipFile(io.BytesIO(sync.archive(self.alpha))) as z:
            names = z.namelist()
        self.assertIn("alpha/SKILL.md", names)
        self.assertIn("alpha/VERSION", names)
        self.assertFalse([n for n in names if "/evals/" in n])

    def test_check_fails_after_hand_edit_in_mirror(self):
        sync.sync(self.tmp)
        self.assertEqual(quiet(sync.main, ["--check"], root=self.tmp), 0)
        mirror_file = self.tmp / ".claude" / "skills" / "beta" / "SKILL.md"
        mirror_file.write_text("edited by hand\n", encoding="utf-8")
        snapshot = mirror_file.read_bytes()
        self.assertEqual(quiet(sync.main, ["--check"], root=self.tmp), 1)
        self.assertEqual(mirror_file.read_bytes(), snapshot, "--check must not write")

    def test_duplicate_name_across_channels_is_refused(self):
        dup = self.tmp / "whosedime" / "alpha"
        dup.mkdir()
        (dup / "SKILL.md").write_text("dup\n", encoding="utf-8")
        self.assertTrue(any("both" in line for line in sync.drift(self.tmp)))
        with self.assertRaises(ValueError):
            sync.sync(self.tmp)

    def test_repository_in_sync(self):
        self.assertEqual(sync.drift(), [], "run: python3 tools/sync_skills.py")


if __name__ == "__main__":
    unittest.main()
