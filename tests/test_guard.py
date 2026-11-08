"""Tests of tools/guard/guard.py (S10): each rule gets a faulty call (hook
JSON on stdin, as Claude Code sends it) that must be blocked or warned with
its rule id, and a clean call that must pass in silence. The guard runs in
a throwaway git repository (WHOSEDIME_GUARD_ROOT), with its own log and
state, and must answer in under 0.5 s a call."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUARD = ROOT / "tools" / "guard" / "guard.py"
BRANCH = "claude/work"
SESSION = "cse_TESTSESSION01"

spec = importlib.util.spec_from_file_location("guard", GUARD)
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)

FRENCH = ("Ce fichier explique comment la vidéo est montée. On prend les images "
          "et on les place dans le dossier, puis le script fait le reste. Il faut "
          "vérifier que la voix est prête avant de lancer le montage, sinon les "
          "scènes ne sont pas alignées. C'est une étape très simple mais elle "
          "demande de l'attention, car une erreur ici coûte une heure de rendu.\n") * 2
ENGLISH = ("This file explains how the video is assembled. We take the images and "
           "place them in the folder, then the script does the rest. Check that the "
           "voice is ready before starting the assembly, otherwise the scenes are not "
           "aligned. It is a simple step but it needs attention, since a mistake here "
           "costs an hour of rendering. The café scene stays as written.\n") * 2


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


class GuardTest(unittest.TestCase):
    seen_rules = set()

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = self.tmp / "repo"
        (self.repo / "docs" / "whosedime" / "watch").mkdir(parents=True)
        (self.repo / "whosedime").mkdir()
        subprocess.run(["git", "init", "-q", "-b", BRANCH, str(self.repo)], check=True)
        git(self.repo, "config", "user.email", "t@example.com")
        git(self.repo, "config", "user.name", "t")
        (self.repo / "README.md").write_text("x\n")
        (self.repo / "docs" / "whosedime" / "critique_log.jsonl").write_text(
            '{"session": "https://claude.ai/code/session_OTHER"}\n')
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "init")
        self.log = self.tmp / "guard_log.jsonl"
        self.env = dict(os.environ, WHOSEDIME_GUARD_ROOT=str(self.repo),
                        WHOSEDIME_GUARD_LOG=str(self.log),
                        WHOSEDIME_GUARD_STATE=str(self.tmp / "state"),
                        CLAUDE_CODE_REMOTE_SESSION_ID=SESSION)
        self.times = []

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        if self.times:
            self.assertLess(max(self.times), 0.5, "the guard took over 0.5 s on a call")

    # ------------------------------------------------------------ helpers
    def call(self, phase, tool, tool_input, response=None, failure=False):
        ev = dict(session_id="s-test", cwd=str(self.repo), tool_name=tool,
                  tool_input=tool_input,
                  hook_event_name={"pre": "PreToolUse", "post": "PostToolUse"}[phase])
        if failure:
            ev["hook_event_name"] = "PostToolUseFailure"
        if response is not None:
            ev["tool_response"] = response
        t0 = time.perf_counter()
        r = subprocess.run([sys.executable, str(GUARD), "post-failure" if failure else phase],
                           input=json.dumps(ev), capture_output=True, text=True, env=self.env)
        self.times.append(time.perf_counter() - t0)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)["hookSpecificOutput"] if r.stdout.strip() else None

    def bash(self, phase, command, **kw):
        return self.call(phase, "Bash", {"command": command}, **kw)

    def assert_blocked(self, out, rule):
        self.assertIsNotNone(out, f"expected a block by {rule}")
        self.assertEqual(out.get("permissionDecision"), "deny", out)
        self.assertIn(f"[{rule}]", out["permissionDecisionReason"])
        self.assertIn("Fix:", out["permissionDecisionReason"])
        self.last_log_is(rule, "block")

    def assert_warned(self, out, rule):
        self.assertIsNotNone(out, f"expected a warning by {rule}")
        self.assertNotIn("permissionDecision", out)
        self.assertIn(f"[{rule}]", out["additionalContext"])
        self.last_log_is(rule, "warn")

    def last_log_is(self, rule, action):
        line = json.loads(self.log.read_text().splitlines()[-1])
        self.assertEqual((line["rule"], line["action"]), (rule, action))
        self.assertEqual(line["session"], "session_TESTSESSION01")
        for k in ("date", "call", "detail"):
            self.assertTrue(line[k])
        GuardTest.seen_rules.add(rule)

    def assert_silent(self, out):
        self.assertIsNone(out)

    def file(self, rel_path):
        return str(self.repo / rel_path)

    # ------------------------------------------------------------- blocks
    def test_skills_generated(self):
        self.assert_blocked(self.call("pre", "Edit", {"file_path": self.file(
            ".claude/skills/whosedime-maker/SKILL.md"), "old_string": "a", "new_string": "b"}),
            "skills-generated")
        self.assert_blocked(self.call("pre", "Write", {"file_path": self.file(
            "whosedime/whosedime-maker.skill"), "content": "x"}), "skills-generated")
        self.assert_blocked(self.bash("pre", "sed -i 's/a/b/' .claude/skills/x/SKILL.md"),
                            "skills-generated")
        self.assert_silent(self.call("pre", "Edit", {"file_path": self.file(
            "whosedime/whosedime-maker/SKILL.md"), "old_string": "a", "new_string": "b"}))
        self.assert_silent(self.bash("pre", "python3 tools/sync_skills.py"))
        self.assert_silent(self.bash("pre", "cat .claude/skills/x/SKILL.md > /tmp/copy.md"))

    def test_push_other_branch(self):
        for cmd in ("git push origin main --dry-run", "git push -u origin claude/other",
                    "git push origin HEAD:main", "git push --all origin",
                    "git fetch origin x && git push origin +main"):
            self.assert_blocked(self.bash("pre", cmd), "push-other-branch")
        for cmd in (f"git push -u origin {BRANCH}", "git push",
                    f"git fetch origin {BRANCH} && git push -u origin {BRANCH}",
                    "git checkout -B claude/new && git push -u origin claude/new",
                    "git push origin HEAD"):
            self.assert_silent(self.bash("pre", cmd))
        git(self.repo, "checkout", "-q", "-b", "main")
        self.assert_blocked(self.bash("pre", "git push"), "push-other-branch")

    def test_secret_print(self):
        for cmd in ("echo $YOUTUBE_API_KEY", 'echo "key=${SUPADATA_API_KEY:0:6}"', "env",
                    "printenv", "printenv SUPADATA_API_KEY", "env | grep KEY",
                    "env | sort", "export -p",
                    "python3 -c \"import os; print(os.environ['YOUTUBE_API_KEY'])\"",
                    "cat <<EOF\n$YOUTUBE_API_KEY\nEOF"):
            self.assert_blocked(self.bash("pre", cmd), "secret-print")
        for cmd in ('[ -n "$YOUTUBE_API_KEY" ] && echo set', "env | cut -d= -f1",
                    "printenv PATH", "env FOO=1 python3 x.py", "echo ${#YOUTUBE_API_KEY}",
                    "env | grep -c PATH", "python3 whosedime/watch/watch.py --help",
                    "cat <<'EOF' > notes.txt\necho $YOUTUBE_API_KEY\nEOF"):
            self.assert_silent(self.bash("pre", cmd))
        self.assert_warned(self.bash("pre", "env | mystery"), "secret-print")

    def test_watch_rerun(self):
        (self.repo / "docs/whosedime/watch/2026-11-08.md").write_text("# report\n")
        self.assert_blocked(self.bash("pre", "python3 whosedime/watch/watch.py --date 2026-11-08"),
                            "watch-rerun")
        self.assert_blocked(self.bash("pre", "cd x && python3 whosedime/watch/watch.py "
                                             "--date=2026-11-08 --no-search"), "watch-rerun")
        for cmd in ("python3 whosedime/watch/watch.py --date 2026-11-08 --force",
                    "python3 whosedime/watch/watch.py --date 2026-11-15",
                    "python3 whosedime/watch/watch.py --refresh-medians"):
            self.assert_silent(self.bash("pre", cmd))

    def test_commit_untested(self):
        commit = "git commit -m 'S10: guard'"
        self.assert_silent(self.bash("pre", commit))              # nothing edited yet
        self.assert_silent(self.call("post", "Write", {"file_path": self.file(
            "docs/whosedime/notes.md"), "content": "x"}, response={"type": "create"}))
        self.assert_silent(self.bash("pre", commit))              # docs only
        self.call("post", "Edit", {"file_path": self.file("whosedime/watch/watch.py")},
                  response={})
        self.assert_blocked(self.bash("pre", commit), "commit-untested")
        self.assert_silent(self.bash(                              # chained after the suite
            "pre", "python3 -m unittest discover -s tests && " + commit))
        self.bash("post", "python3 -m unittest tests.test_watch",  # partial run: not enough
                  response={"stdout": "", "stderr": "Ran 12 tests in 1s\n\nOK\n"})
        self.assert_blocked(self.bash("pre", commit), "commit-untested")
        self.bash("post", "python3 -m unittest discover -s tests 2>&1 | tail -3",
                  response={"stdout": "Ran 180 tests in 30s\n\nOK\n", "stderr": ""})
        self.assert_silent(self.bash("pre", commit))
        self.bash("post", "python3 -m unittest discover -s tests",
                  response={"stdout": "", "stderr": "Ran 180 tests\n\nFAILED (failures=1)\n"})
        out = self.bash("pre", commit)
        self.assert_blocked(out, "commit-untested")
        self.assertIn("FAILED (failures=1)", out["permissionDecisionReason"])
        self.bash("post", "python3 -m unittest discover -s tests",
                  response={"stdout": "Ran 180 tests\n\nOK\n"})
        self.assert_silent(self.bash("pre", commit))
        self.bash("post", "python3 -m unittest discover -s tests", failure=True,
                  response={"error": "Exit code 1"})
        self.assert_blocked(self.bash("pre", commit), "commit-untested")

    # ------------------------------------------------------------ warnings
    def test_state_length(self):
        state = self.repo / "docs/whosedime/STATE.md"
        state.write_text("line\n" * 61)
        out = self.call("post", "Edit", {"file_path": str(state)}, response={})
        self.assert_warned(out, "state-length")
        self.assertIn("61 lines", out["additionalContext"])
        state.write_text("line\n" * 60)
        self.assert_silent(self.call("post", "Edit", {"file_path": str(state)}, response={}))
        state.write_text("line\n" * 62)
        self.assert_warned(self.bash("post", "printf '\\n\\n' >> docs/whosedime/STATE.md",
                                     response={}), "state-length")

    def test_watch_report_length(self):
        rep = self.repo / "docs/whosedime/watch/2026-11-15.md"
        rep.write_text("row\n" * 101)
        self.assert_warned(self.bash("post", "python3 whosedime/watch/watch.py --date 2026-11-15",
                                     response={"stdout": "Report: ..."}), "watch-report-length")
        self.assert_warned(self.call("post", "Write", {"file_path": str(rep)}, response={}),
                           "watch-report-length")
        rep.write_text("row\n" * 100)
        self.assert_silent(self.call("post", "Write", {"file_path": str(rep)}, response={}))

    def test_french_text(self):
        fr = self.repo / "whosedime/notes_montage.md"
        fr.write_text(FRENCH)
        self.assert_warned(self.call("post", "Write", {"file_path": str(fr)},
                                     response={"type": "create"}), "french-text")
        en = self.repo / "docs/whosedime/assembly_notes.md"
        en.write_text(ENGLISH)
        self.assert_silent(self.call("post", "Write", {"file_path": str(en)},
                                     response={"type": "create"}))
        git(self.repo, "add", "-A")                 # tracked: no longer new
        git(self.repo, "commit", "-q", "-m", "fr")
        self.assert_silent(self.call("post", "Edit", {"file_path": str(fr)}, response={}))
        outside = self.repo / "notes_fr.md"          # outside whosedime/: not judged
        outside.write_text(FRENCH)
        self.assert_silent(self.call("post", "Write", {"file_path": str(outside)},
                                     response={"type": "create"}))

    def test_critique_reminder(self):
        (self.repo / "whosedime/tool.py").write_text("x = 1\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "tool")
        self.assert_warned(self.bash("post", "git commit -m tool", response={}),
                           "critique-reminder")
        log = self.repo / "docs/whosedime/critique_log.jsonl"
        log.write_text(log.read_text() + json.dumps(
            {"session": "https://claude.ai/code/session_TESTSESSION01"}) + "\n")
        self.assert_silent(self.bash("post", "git commit -m tool", response={}))
        (self.repo / "README.md").write_text("y\n")  # not a deliverable
        git(self.repo, "commit", "-qam", "readme")
        log.write_text("")
        self.assert_silent(self.bash("post", "git commit -am readme", response={}))

    # ------------------------------------------------------------ general
    def test_no_false_block_from_file_names_or_messages(self):
        """Live false block of S10: `git add whosedime/watch/watch.py` read as
        a watch run; a multi-line quoted message must stay one argument."""
        (self.repo / "docs/whosedime/watch/2026-11-08.md").write_text("# report\n")
        self.assert_silent(self.bash("pre", "git add whosedime/watch/watch.py tests/x.py"))
        self.assert_silent(self.bash("pre", 'git add -A && git commit -q -m "S10: guard\n\n'
                                            '- watch.py: checks\nenv\nprintenv\n'
                                            'git push origin main\npython3 whosedime/watch/watch.py"'))
        self.assert_blocked(self.bash("pre", "ls\npython3 whosedime/watch/watch.py --date 2026-11-08"),
                            "watch-rerun")

    def test_clean_calls_leave_no_log(self):
        self.assert_silent(self.bash("pre", "ls -la"))
        self.assert_silent(self.call("pre", "Read", {"file_path": self.file("README.md")}))
        self.assert_silent(self.bash("post", "ls", response={"stdout": "x"}))
        self.assertFalse(self.log.exists())

    def test_bad_input_is_silent(self):
        for phase in ("pre", "post", "nonsense"):
            r = subprocess.run([sys.executable, str(GUARD), phase], input="not json{",
                               capture_output=True, text=True, env=self.env)
            self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_secret_value_never_logged(self):
        env = dict(self.env, YOUTUBE_API_KEY="AIzaFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKE123")
        ev = dict(session_id="s", tool_name="Bash", hook_event_name="PreToolUse",
                  tool_input={"command": "echo AIzaFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKE123 "
                                         "$YOUTUBE_API_KEY"})
        subprocess.run([sys.executable, str(GUARD), "pre"], input=json.dumps(ev),
                       capture_output=True, text=True, env=env)
        self.assertNotIn("FAKEFAKE", self.log.read_text())


class RulesTableTest(unittest.TestCase):
    def test_table(self):
        ids = [r["id"] for r in G.RULES]
        self.assertEqual(len(ids), len(set(ids)))
        for r in G.RULES:
            self.assertIn(r["when"], ("pre", "post"))
            self.assertIn(r["action"], ("block", "warn"))
            self.assertTrue(callable(getattr(G, r["check"])), r["check"])
            self.assertTrue(r["case"] and r["fix"] and r["rule"])
        # only pre rules block: a post rule cannot undo a call
        self.assertTrue(all(r["action"] == "warn" for r in G.RULES if r["when"] == "post"))

    def test_settings_wire_the_guard(self):
        hooks = json.loads((ROOT / ".claude" / "settings.json").read_text())["hooks"]
        for event, phase in (("PreToolUse", "pre"), ("PostToolUse", "post"),
                             ("PostToolUseFailure", "post-failure")):
            cmds = [h["command"] for m in hooks[event] for h in m["hooks"]]
            self.assertTrue(any("tools/guard/guard.py" in c and c.endswith(" " + phase)
                                for c in cmds), event)

    def test_french_detector_on_repo_files(self):
        """Measured on the repository: no English file of whosedime/ or
        docs/whosedime/ reads as French."""
        files = subprocess.run(["git", "-C", str(ROOT), "ls-files", "whosedime", "docs/whosedime"],
                               capture_output=True, text=True).stdout.split()
        judged = flagged = 0
        for f in files:
            if not f.endswith(G.TEXT_SUFFIXES):
                continue
            try:
                text = (ROOT / f).read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            fr, n, _, _ = G.french_score(text)
            judged += n >= G.FRENCH_MIN_WORDS
            flagged += fr
        self.assertGreater(judged, 50)
        self.assertEqual(flagged, 0)
        self.assertTrue(G.french_score(FRENCH)[0])


def tearDownModule():
    every = {r["id"] for r in G.RULES}
    missing = every - GuardTest.seen_rules
    if missing and len(GuardTest.seen_rules) > 3:   # only when the whole class ran
        raise AssertionError(f"rules never caught in tests: {sorted(missing)}")


if __name__ == "__main__":
    unittest.main()
