"""Tests of tools/guard/guard.py (S10): each rule gets a faulty call (hook
JSON on stdin, as Claude Code sends it) and a clean one. A faulty call is
blocked (PreToolUse deny) or warned (PostToolUse additionalContext) with its
rule and logged; a clean call passes silently; each call takes < 0.5 s.
Everything runs in a throwaway git repo (no network)."""
import datetime as dt
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
GUARD = ROOT / "tools" / "guard" / "guard.py"
BRANCH = "claude/work-branch"
TODAY = dt.datetime.now(dt.timezone.utc).date().isoformat()


def sh(cwd, *args):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True)


class GuardTest(unittest.TestCase):
    def setUp(self):
        self.repo = pathlib.Path(tempfile.mkdtemp())
        self.state = pathlib.Path(tempfile.mkdtemp())
        sh(self.repo, "git", "init", "-q", "-b", BRANCH)
        sh(self.repo, "git", "config", "user.email", "t@t")
        sh(self.repo, "git", "config", "user.name", "t")
        for d in ("docs/whosedime/watch", "whosedime/watch", "tools", "tests",
                  ".claude/skills/whosedime-maker"):
            (self.repo / d).mkdir(parents=True, exist_ok=True)
        (self.repo / "docs/whosedime/STATE.md").write_text("line\n" * 40)
        (self.repo / "docs/whosedime/critique_log.jsonl").write_text(
            '{"deliverable": "old.py"}\n')
        (self.repo / "tools/old.py").write_text("x = 1\n")
        (self.repo / "docs/whosedime/watch/2026-11-08.md").write_text("# report\n")
        sh(self.repo, "git", "add", "-A")
        sh(self.repo, "git", "commit", "-qm", "init")
        self.session = "test-session"

    def call(self, event, tool, tool_input, response=None):
        data = dict(session_id=self.session, cwd=str(self.repo), hook_event_name=event,
                    tool_name=tool, tool_input=tool_input)
        if response is not None:
            data["tool_response"] = response
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(self.repo),
                   GUARD_STATE_DIR=str(self.state))
        t0 = time.monotonic()
        r = subprocess.run([sys.executable, str(GUARD)], input=json.dumps(data),
                           capture_output=True, text=True, env=env, timeout=5)
        self.assertLess(time.monotonic() - t0, 0.5, "guard too slow")
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout) if r.stdout.strip() else None

    def bash(self, command, event="PreToolUse", response=None):
        return self.call(event, "Bash", {"command": command}, response)

    def log(self):
        p = self.repo / "docs/whosedime/guard_log.jsonl"
        return [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []

    def assertBlocked(self, out, rule):
        self.assertIsNotNone(out, f"{rule}: not blocked")
        h = out["hookSpecificOutput"]
        self.assertEqual(h["permissionDecision"], "deny")
        self.assertIn(f"[{rule}]", h["permissionDecisionReason"])
        self.assertIn("Fix:", h["permissionDecisionReason"])
        self.assertEqual((self.log()[-1]["rule"], self.log()[-1]["action"]), (rule, "block"))

    def assertWarned(self, out, rule):
        self.assertIsNotNone(out, f"{rule}: no warning")
        self.assertIn(f"[{rule}]", out["hookSpecificOutput"]["additionalContext"])
        self.assertEqual((self.log()[-1]["rule"], self.log()[-1]["action"]), (rule, "warn"))

    # ------------------------------------------------------------ blocks

    def test_skills_generated(self):
        skill = str(self.repo / ".claude/skills/whosedime-maker/SKILL.md")
        self.assertBlocked(self.call("PreToolUse", "Edit", {"file_path": skill,
                           "old_string": "a", "new_string": "b"}), "skills-generated")
        self.assertBlocked(self.call("PreToolUse", "Write", {"file_path": str(
            self.repo / "whosedime-maker.skill"), "content": "x"}), "skills-generated")
        self.assertBlocked(self.bash("echo x >> .claude/skills/whosedime-maker/SKILL.md"),
                           "skills-generated")
        self.assertBlocked(self.bash("sed -i 's/a/b/' .claude/skills/x/SKILL.md"),
                           "skills-generated")
        # clean: the source skill, reading the generated one, the sync tool
        self.assertIsNone(self.call("PreToolUse", "Edit", {"file_path": str(
            self.repo / "whosedime/whosedime-maker/SKILL.md")}))
        self.assertIsNone(self.bash("cat .claude/skills/whosedime-maker/SKILL.md | head"))
        self.assertIsNone(self.bash("python3 tools/sync_skills.py --check"))

    def test_push(self):
        self.assertBlocked(self.bash("git push origin main"), "push-main")
        self.assertBlocked(self.bash("git push --dry-run origin HEAD:main"), "push-main")
        self.assertBlocked(self.bash("git fetch && git push -u origin +work:refs/heads/main"),
                           "push-main")
        self.assertBlocked(self.bash("git push --all origin"), "push-main")
        self.assertBlocked(self.bash("git push origin claude/other-session"),
                           "push-other-branch")
        # clean
        self.assertIsNone(self.bash(f"git push -u origin {BRANCH}"))
        self.assertIsNone(self.bash("git push origin HEAD"))
        self.assertIsNone(self.bash("git push"))
        self.assertIsNone(self.bash("git log --oneline main..HEAD"))
        # false block met live in S10: a push named inside a quoted JSON string
        self.assertIsNone(self.bash("python3 tools/guard/guard.py <<<'{\"tool_input\": "
                                    "{\"command\": \"git commit -m x && git push origin "
                                    "other\"}, \"cwd\": \"/x\"}'"))
        self.assertIsNone(self.bash("git commit -m 'a; b && c' \\\n  && git push origin HEAD"))
        # false block met live in S10: a redirection read as a branch
        self.assertIsNone(self.bash(f"git push -u origin {BRANCH} 2>&1 | tail -1"))
        self.assertIsNone(self.bash(f"git push origin {BRANCH} > /tmp/out 2>/dev/null"))
        self.assertBlocked(self.bash("git push origin main 2>&1 | tail -1"), "push-main")

    def test_push_from_main(self):
        sh(self.repo, "git", "checkout", "-qb", "main")
        self.assertBlocked(self.bash("git push"), "push-main")

    def test_secret_print(self):
        for cmd in ("echo $YOUTUBE_API_KEY", 'printf "%s" "${SUPADATA_API_KEY}"',
                    "env", "printenv", "env | grep KEY", "printenv YOUTUBE_API_KEY",
                    "cat /proc/self/environ", "ls; env | sort"):
            self.assertBlocked(self.bash(cmd), "secret-print")
        for cmd in ('[ -n "$YOUTUBE_API_KEY" ] && echo set', "env | cut -d= -f1",
                    "env | grep -c YOUTUBE", "printenv HOME", "env PYTHONPATH=. python3 x.py",
                    "echo $HOME", "python3 whosedime/watch/watch.py --help",
                    "grep -n YOUTUBE_API_KEY whosedime/watch/watch.py"):
            self.assertIsNone(self.bash(cmd), cmd)

    def test_watch_rerun(self):
        self.assertBlocked(self.bash("python3 whosedime/watch/watch.py --date 2026-11-08"),
                           "watch-rerun")
        (self.repo / f"docs/whosedime/watch/{TODAY}.md").write_text("# r\n")
        self.assertBlocked(self.bash("cd x && python3 whosedime/watch/watch.py --no-search"),
                           "watch-rerun")
        # clean: --force, another date, reading the file
        self.assertIsNone(self.bash("python3 whosedime/watch/watch.py --date 2026-11-08 --force"))
        self.assertIsNone(self.bash("python3 whosedime/watch/watch.py --date 2026-11-15"))
        self.assertIsNone(self.bash("cat whosedime/watch/watch.py"))
        # the two false blocks met live in S10: a heredoc body and an assignment
        self.assertIsNone(self.bash("python3 - <<'EOF'\nrun('python3 whosedime/watch/watch.py')\n"
                                    "p='whosedime/watch/watch.py'; s=open(p).read()\nEOF\nls"))
        self.assertIsNone(self.bash("python3 -c \"p='whosedime/watch/watch.py'; print(p)\""))
        self.assertIsNone(self.bash("python3 /tmp/patch_watch.py whosedime/watch/watch.py"))

    def test_commit_untested(self):
        (self.repo / "tools/new.py").write_text("y = 2\n")
        # no test run yet
        self.assertBlocked(self.bash("git add -A && git commit -m x"), "commit-untested")
        # a failed run (no OK in the output)
        test = "python3 -m unittest discover -s tests"
        self.assertIsNone(self.bash(test))
        self.bash(test, "PostToolUse", {"stdout": "", "stderr": "Ran 3 tests\n\nFAILED (failures=1)"})
        self.assertBlocked(self.bash("git commit -am x"), "commit-untested")
        # a run that never reports back (exit != 0: no PostToolUse)
        self.bash(test)
        self.assertBlocked(self.bash("git commit -am x"), "commit-untested")
        # a green run: commit allowed
        self.bash(test)
        self.bash(test, "PostToolUse", {"stdout": "", "stderr": "Ran 3 tests in 0.1s\n\nOK\n"})
        self.assertIsNone(self.bash("git add -A && git commit -m x"))
        # code edited after the green run
        time.sleep(0.05)
        (self.repo / "tools/new.py").write_text("y = 3\n")
        self.assertBlocked(self.bash("git commit -am x"), "commit-untested")

    def test_commit_docs_only_needs_no_tests(self):
        (self.repo / "docs/whosedime/notes.md").write_text("Some notes.\n")
        self.assertIsNone(self.bash("git add -A && git commit -m docs"))

    # ---------------------------------------------------------- warnings

    def test_state_length(self):
        p = self.repo / "docs/whosedime/STATE.md"
        p.write_text("line\n" * 61)
        self.assertWarned(self.call("PostToolUse", "Edit", {"file_path": str(p)}),
                          "state-length")
        p.write_text("line\n" * 60)
        self.assertIsNone(self.call("PostToolUse", "Edit", {"file_path": str(p)}))

    def test_watch_report_length(self):
        p = self.repo / "docs/whosedime/watch/2026-11-15.md"
        p.write_text("row\n" * 184)
        self.assertWarned(self.bash("python3 whosedime/watch/watch.py --date 2026-11-15",
                                    "PostToolUse", {"stdout": "Report: ..."}),
                          "watch-report-length")
        p.write_text("row\n" * 87)
        self.assertIsNone(self.call("PostToolUse", "Write", {"file_path": str(p)}))

    def test_french_text(self):
        fr = self.repo / "docs/whosedime/notes_fr.md"
        fr.write_text("Le sel est une matière première que nous utilisons dans la cuisine "
                      "depuis des siècles, et il a fait la fortune de villes entières. "
                      "Mais qui a payé pour cette richesse ? Les ouvriers des salines.\n")
        self.assertWarned(self.call("PostToolUse", "Write", {"file_path": str(fr)}),
                          "french-text")
        # a new file made by a shell command is caught too
        fr2 = self.repo / "whosedime/notes2.md"
        fr2.write_text(fr.read_text())
        self.assertWarned(self.bash("cat > whosedime/notes2.md <<EOF", "PostToolUse", {}),
                          "french-text")
        # clean: English with a French name and a café
        en = self.repo / "docs/whosedime/notes_en.md"
        en.write_text("Uber was cheap because investors paid for every ride. Travis "
                      "Kalanick met Garrett Camp at LeWeb in Paris, over a café crème, "
                      "and the drivers carried the cost of the cars for years.\n")
        self.assertIsNone(self.call("PostToolUse", "Write", {"file_path": str(en)}))

    def test_french_detector_no_false_alert_on_repo(self):
        """Measured: every tracked English text file of whosedime/ and
        docs/whosedime/ passes; Zehon's French Markdown is flagged."""
        sys.path.insert(0, str(GUARD.parent))
        import guard
        files = subprocess.run(["git", "ls-files", "whosedime", "docs/whosedime"], cwd=ROOT,
                               capture_output=True, text=True).stdout.split()
        alerts = [f for f in files if f.endswith(guard.TEXT_SUFFIXES)
                  and guard.is_french((ROOT / f).read_text(encoding="utf-8", errors="ignore"))]
        self.assertEqual(alerts, [])
        fr = subprocess.run(["git", "ls-files", "docs/chaine2/*.md"], cwd=ROOT,
                            capture_output=True, text=True).stdout.split()
        caught = [f for f in fr if guard.is_french((ROOT / f).read_text(encoding="utf-8"))]
        self.assertEqual(len(caught), len(fr))

    def test_critique_missing(self):
        (self.repo / "tools/report.py").write_text("z = 1\n")
        sh(self.repo, "git", "add", "-A")
        sh(self.repo, "git", "commit", "-qm", "report")
        self.assertWarned(self.bash("git commit -m report", "PostToolUse", {}),
                          "critique-missing")
        # clean: a commit whose deliverable is named in the log
        (self.repo / "docs/whosedime/critique_log.jsonl").write_text(
            '{"deliverable": "report.py"}\n')
        (self.repo / "tools/report.py").write_text("z = 2\n")
        sh(self.repo, "git", "add", "tools/report.py")
        sh(self.repo, "git", "commit", "-qm", "again")
        self.assertIsNone(self.bash("git commit -m again", "PostToolUse", {}))

    def test_silent_on_ordinary_calls_and_bad_input(self):
        self.assertIsNone(self.bash("ls -la && git status"))
        self.assertIsNone(self.bash("ls", "PostToolUse", {"stdout": "a"}))
        self.assertIsNone(self.call("PreToolUse", "Read", {"file_path": "x"}))
        r = subprocess.run([sys.executable, str(GUARD)], input="not json",
                           capture_output=True, text=True, timeout=5)
        self.assertEqual((r.returncode, r.stdout), (0, ""))
        self.assertEqual(self.log(), [])

    def test_rules_table_complete(self):
        sys.path.insert(0, str(GUARD.parent))
        import guard
        for name, r in guard.RULES.items():
            self.assertIn(r["kind"], ("block", "warn"), name)
            self.assertTrue(r["rule"] and r["fix"] and r["case"], name)


if __name__ == "__main__":
    unittest.main()
