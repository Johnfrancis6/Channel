"""Tests of tools/guard/guard.py (S10): each rule gets a faulty call (hook
JSON on stdin) and a clean one. Faulty calls exit 2 naming their rule; clean
calls exit 0 in silence; each call answers in under 0.5 s. Runs in a
throw-away git repository, so the real logs and state are never touched."""
import json
import pathlib
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
GUARD = ROOT / "tools" / "guard" / "guard.py"
sys.path.insert(0, str(GUARD.parent))
import guard  # noqa: E402


def sh(cwd, *cmd):
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True)


class GuardTest(unittest.TestCase):
    def setUp(self):
        self.repo = pathlib.Path(tempfile.mkdtemp())
        sh(self.repo, "git", "init", "-q", "-b", "claude/work")
        sh(self.repo, "git", "config", "user.email", "t@t")
        sh(self.repo, "git", "config", "user.name", "t")
        (self.repo / "docs/whosedime/watch").mkdir(parents=True)
        (self.repo / "docs/whosedime/watch/2026-11-08.md").write_text("# report\n")
        (self.repo / "docs/whosedime/STATE.md").write_text("x\n" * 10)
        (self.repo / "docs/whosedime/critique_log.jsonl").write_text("")
        (self.repo / "docs/whosedime/guard_log.jsonl").write_text("")
        sh(self.repo, "git", "add", "-A")
        sh(self.repo, "git", "commit", "-qm", "init")

    def call(self, when, tool, sid="s1", response=None, **inp):
        payload = dict(session_id=sid, cwd=str(self.repo), tool_name=tool,
                       tool_input=inp, hook_event_name="PreToolUse" if when == "pre"
                       else "PostToolUse")
        if response is not None:
            payload["tool_response"] = response
        t = time.perf_counter()
        r = subprocess.run([sys.executable, str(GUARD), when], input=json.dumps(payload),
                           capture_output=True, text=True, cwd=self.repo)
        self.assertLess(time.perf_counter() - t, 0.5, f"slow guard on {tool} {inp}")
        return r

    def assertFlags(self, r, rule, action="BLOCKED"):
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn(f"guard {action} [{rule}]", r.stderr)
        last = (self.repo / "docs/whosedime/guard_log.jsonl").read_text().splitlines()[-1]
        self.assertEqual(json.loads(last)["rule"], rule)

    def assertSilent(self, r):
        self.assertEqual((r.returncode, r.stderr), (0, ""))

    # ------------------------------------------------------------ blocks

    def test_skills_edit(self):
        self.assertFlags(self.call("pre", "Edit", file_path=str(self.repo / ".claude/skills/whosedime-maker/SKILL.md")), "skills-edit")
        self.assertFlags(self.call("pre", "Write", file_path="whosedime/whosedime-maker.skill"), "skills-edit")
        self.assertFlags(self.call("pre", "Bash", command="echo hi >> .claude/skills/x/SKILL.md"), "skills-edit")
        self.assertFlags(self.call("pre", "Bash", command="sed -i s/a/b/ .claude/skills/x/SKILL.md"), "skills-edit")
        self.assertSilent(self.call("pre", "Edit", file_path=str(self.repo / "whosedime/whosedime-maker/SKILL.md")))
        self.assertSilent(self.call("pre", "Bash", command="python3 tools/sync_skills.py && cat .claude/skills/x/SKILL.md"))

    def test_push(self):
        self.assertFlags(self.call("pre", "Bash", command="git push origin main --dry-run"), "push-branch")
        self.assertFlags(self.call("pre", "Bash", command="git push -u origin claude/other"), "push-branch")
        self.assertFlags(self.call("pre", "Bash", command="git fetch && git push origin HEAD:main"), "push-branch")
        self.assertSilent(self.call("pre", "Bash", command="git push -u origin claude/work"))
        self.assertSilent(self.call("pre", "Bash", command="git push"))
        self.assertSilent(self.call("pre", "Bash", command="git log main --oneline"))

    def test_secret(self):
        for c in ("echo $YOUTUBE_API_KEY", "printenv SUPADATA_API_KEY", "env", "env | sort",
                  'printf "%s" "${SUPADATA_API_KEY}"',
                  "python3 -c 'import os; print(os.environ[\"YOUTUBE_API_KEY\"])'"):
            self.assertFlags(self.call("pre", "Bash", command=c), "secret-print")
        for c in ('[ -n "$YOUTUBE_API_KEY" ] && echo set', "env FOO=1 python3 x.py",
                  "printenv HOME", "python3 whosedime/watch/watch.py --date 2026-11-15"):
            self.assertSilent(self.call("pre", "Bash", command=c))

    def test_watch_rerun(self):
        self.assertFlags(self.call("pre", "Bash", command="python3 whosedime/watch/watch.py --date 2026-11-08"), "watch-rerun")
        self.assertSilent(self.call("pre", "Bash", command="python3 whosedime/watch/watch.py --date 2026-11-08 --force"))
        self.assertSilent(self.call("pre", "Bash", command="python3 whosedime/watch/watch.py --date 2026-11-15"))
        self.assertSilent(self.call("pre", "Bash", command="python3 whosedime/watch/watch.py --refresh-medians"))

    def test_commit_untested(self):
        commit = "git add -A && git commit -m x"
        self.assertSilent(self.call("pre", "Bash", command=commit))        # no code edited
        self.call("post", "Edit", file_path=str(self.repo / "tools/a.py"))
        self.assertFlags(self.call("pre", "Bash", command=commit), "commit-untested")
        failed = {"stdout": "", "stderr": "Ran 3 tests in 0.1s\n\nFAILED (failures=1)\n"}
        self.call("post", "Bash", command="python3 -m unittest discover -s tests", response=failed)
        self.assertFlags(self.call("pre", "Bash", command=commit), "commit-untested")
        ok = {"stdout": "", "stderr": "Ran 3 tests in 0.1s\n\nOK\n"}
        self.call("post", "Bash", command="python3 -m unittest discover -s tests", response=ok)
        self.assertSilent(self.call("pre", "Bash", command=commit))
        self.assertSilent(self.call("pre", "Bash", command=commit, sid="other"))
        self.call("post", "Write", file_path="tools/b.py")                 # edit after the run
        self.assertFlags(self.call("pre", "Bash", command=commit), "commit-untested")

    # ---------------------------------------------------------- warnings

    def test_state_length(self):
        st = self.repo / "docs/whosedime/STATE.md"
        self.assertSilent(self.call("post", "Edit", file_path=str(st)))
        st.write_text("x\n" * 61)
        self.assertFlags(self.call("post", "Edit", file_path=str(st)), "state-length", "WARNING")
        self.assertSilent(self.call("post", "Bash", command="wc -l docs/whosedime/STATE.md"))
        self.assertFlags(self.call("post", "Bash", command="cat >> docs/whosedime/STATE.md"), "state-length", "WARNING")

    def test_report_length(self):
        rep = self.repo / "docs/whosedime/watch/2026-11-08.md"
        self.assertSilent(self.call("post", "Bash", command="python3 whosedime/watch/watch.py"))
        rep.write_text("x\n" * 184)
        self.assertFlags(self.call("post", "Bash", command="python3 whosedime/watch/watch.py"), "report-length", "WARNING")
        self.assertFlags(self.call("post", "Write", file_path=str(rep)), "report-length", "WARNING")

    def test_french_text(self):
        fr = ("Le contrôleur passe après chaque étape, et il compare les fichiers entre eux "
              "pour renvoyer une liste de défauts typés comme le journal, avec la phrase.")
        en = ("The controller runs after each step and compares the files with each other, "
              "then returns a list of typed defects like the log, with the sentence. Café.")
        self.assertFlags(self.call("post", "Write", file_path="docs/whosedime/new.md", content=fr), "french-text", "WARNING")
        self.assertSilent(self.call("post", "Write", file_path="docs/whosedime/new.md", content=en))
        self.assertSilent(self.call("post", "Write", file_path="docs/chaine2/new.md", content=fr))
        self.assertSilent(self.call("post", "Write", file_path="docs/whosedime/STATE.md", content=fr))  # tracked

    def test_critique_missing(self):
        (self.repo / "docs/whosedime/new.md").write_text("x\n")
        sh(self.repo, "git", "add", "-A")
        sh(self.repo, "git", "commit", "-qm", "deliverable")
        self.assertFlags(self.call("post", "Bash", command="git commit -m deliverable"), "critique-missing", "WARNING")
        import datetime as dt
        (self.repo / "docs/whosedime/critique_log.jsonl").write_text(
            json.dumps({"date": dt.date.today().isoformat()}) + "\n")
        self.assertSilent(self.call("post", "Bash", command="git commit -m deliverable"))

    def test_bad_input_passes(self):
        r = subprocess.run([sys.executable, str(GUARD), "pre"], input="not json",
                           capture_output=True, text=True)
        self.assertSilent(r)

    def test_every_rule_has_a_check(self):
        self.assertEqual(set(guard.RULES), set(guard.CHECKS))

    def test_no_false_french_on_repo_files(self):
        """Measured false alerts: English files under whosedime/ and docs/whosedime/."""
        alerts = []
        for base in ("whosedime", "docs/whosedime"):
            for p in (ROOT / base).rglob("*"):
                if p.suffix in (".md", ".py", ".json") and p.is_file():
                    if guard.looks_french(p.read_text(encoding="utf-8", errors="ignore")):
                        alerts.append(p.relative_to(ROOT).as_posix())
        self.assertLessEqual(len(alerts), 1, alerts)


if __name__ == "__main__":
    unittest.main()
