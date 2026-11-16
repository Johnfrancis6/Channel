#!/usr/bin/env python3
"""Live guard for Whose Dime sessions (S10, decision D15).

Claude Code runs this on every tool call (hooks in .claude/settings.json):

    python3 tools/guard/guard.py pre    # PreToolUse: may block the call
    python3 tools/guard/guard.py post   # PostToolUse: may warn after the call

The hook JSON arrives on stdin (session_id, cwd, tool_name, tool_input, and
tool_response after the call). A block or a warning is one line on stderr
with exit code 2: Claude Code then refuses the call (pre) or shows the line
to the agent (post), which reads it at once. Silence and exit 0 otherwise.
Every block and warning is appended to docs/whosedime/guard_log.jsonl.

Rules live in RULES below; each entered because it would have caught a real
case (critique_log.jsonl or the S09 cases named in sessions/S10). When
unsure, a rule warns: a guard that blocks good work is worse than none.
Standard library only; no network, no model. Any internal error lets the
call through (exit 0): the guard must never stop work by crashing.
"""
import datetime as dt
import json
import os
import pathlib
import re
import shlex
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
LOG = "docs/whosedime/guard_log.jsonl"
STATE_MD = "docs/whosedime/STATE.md"
WATCH_DIR = "docs/whosedime/watch"
CRITIQUE_LOG = "docs/whosedime/critique_log.jsonl"
STATE_LINES, REPORT_LINES = 60, 100

# ----------------------------------------------------------------- rules
# name: (when, action, where it comes from, the one-line message)
RULES = {
    "skills-edit": ("pre", "block", "CLAUDE.md; S01-S05 edits",
                    "never edit .claude/skills/ or *.skill: edit <channel>/<skill>/, "
                    "then run python3 tools/sync_skills.py"),
    "push-branch": ("pre", "block", "CLAUDE.md, ROADMAP rule 2",
                    "push only the current work branch (never main: main changes "
                    "through a pull request Franco merges)"),
    "secret-print": ("pre", "block", "CLAUDE.md",
                     "never print YOUTUBE_API_KEY or SUPADATA_API_KEY: test it with "
                     "[ -n \"$YOUTUBE_API_KEY\" ] && echo set"),
    "watch-rerun": ("pre", "block", "S09: two runs in a day, 520 units",
                    "a watch report already exists for today: read it, or add "
                    "--force if Franco asked for a rerun"),
    "commit-untested": ("pre", "block", "CLAUDE.md: tests green before the commit",
                        "run python3 -m unittest discover -s tests (green) before "
                        "git commit"),
    "state-length": ("post", "warn", "S09: a 62-line STATE.md",
                     "STATE.md is over 60 lines: shorten it now"),
    "report-length": ("post", "warn", "S09: a 184-line report for 'one page'",
                      "the watch report is over 100 lines (one page asked): shorten it"),
    "french-text": ("post", "warn", "CLAUDE.md: everything for Whose Dime in English",
                    "new Whose Dime file looks French: write it in English"),
    "critique-missing": ("post", "warn", "CRITIQUE_PROTOCOL.md",
                         "a deliverable was committed with no critique_log.jsonl line "
                         "today: add self-critique and Franco's grade"),
}

SECRETS = r"(YOUTUBE_API_KEY|SUPADATA_API_KEY)"
FRENCH_WORDS = {"le", "la", "les", "des", "du", "une", "est", "pour", "avec",
                "dans", "qui", "que", "pas", "sur", "mais", "nous", "sont", "cette",
                "aux", "ou", "et", "ce", "il", "elle", "au"}
CODE_EXT = {".py", ".ipynb", ".sh"}


# ----------------------------------------------------------------- state

def _git(cwd, *args):
    try:
        r = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True,
                           text=True, timeout=3)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def _state_path(cwd):
    """Per-clone, never committed: inside .git/."""
    g = _git(cwd, "rev-parse", "--git-dir")
    if not g:
        return None
    p = pathlib.Path(g)
    return (p if p.is_absolute() else pathlib.Path(cwd) / p) / "whosedime_guard.json"


def _load_state(cwd):
    p = _state_path(cwd)
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}


def _save_state(cwd, state):
    p = _state_path(cwd)
    if p:
        try:
            p.write_text(json.dumps(state))
        except Exception:
            pass


# --------------------------------------------------------------- helpers

def _rel(cwd, path):
    if not path:
        return ""
    p = pathlib.Path(path)
    if not p.is_absolute():
        p = pathlib.Path(cwd) / p
    try:
        return p.resolve().relative_to(pathlib.Path(cwd).resolve()).as_posix()
    except ValueError:
        return p.as_posix()


# Ported from the 08/11 S10 (session S13): heredoc bodies are data, quotes
# are read before operators, redirections are not arguments.
HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?(?:\n\s*\2\s*(?:\n|$)|\Z)", re.S)
OPERATORS = {"&&", "||", ";", "&", "|", ";;", "|&"}


def _strip_heredocs(cmd):
    """Keep the line that opens a heredoc, drop its body (a Python heredoc
    naming watch.py was blocked as a watch run)."""
    return HEREDOC.sub(lambda m: m.group(0).split("\n", 1)[0] + "\n", cmd or "")


def _pipelines(cmd):
    """Pipelines of a shell line, each a list of simple commands (strings),
    split on operators outside quotes; redirections such as `2>&1` and
    `> file` are dropped (15/11: `git push -u origin BRANCH 2>&1` read `2>&1`
    as a branch; splitting on '&&' before quotes read a quoted JSON string as
    a `git push`)."""
    text = _strip_heredocs(cmd).replace("\\\n", " ").replace("\n", " ; ")
    text = re.sub(r"\d*>&\d+|&>>?", " ", text)
    text = re.sub(r"(?<![\w$])\d+(?=[<>])", " ", text)   # `2> f`: the 2 is no argument
    lex = shlex.shlex(text, posix=True, punctuation_chars=";&|<>")
    lex.whitespace_split = True
    try:
        toks = list(lex)
    except ValueError:                       # unbalanced quote: plain split
        toks = text.split()
    out, pipe, words, skip = [], [], [], False
    for t in toks + [";"]:
        if skip and t not in OPERATORS:
            skip = False
            continue
        skip = False
        if re.fullmatch(r"\d*(<<<|<<|>>|>|<)", t) or re.fullmatch(r"[<>]+", t):
            skip = True                      # a redirection and its target
            continue
        if t in OPERATORS or re.fullmatch(r"[;&|]+", t):
            if words:
                pipe.append(shlex.join(words))
            words = []
            if t not in ("|", "|&") and pipe:
                out.append(pipe)
                pipe = []
        else:
            words.append(t)
    return out


def _segments(cmd):
    """Simple commands of a shell line, operators outside quotes."""
    return [c for pipe in _pipelines(cmd) for c in pipe]


def _words(seg):
    try:
        return shlex.split(seg)
    except ValueError:
        return seg.split()


def _is_skills_path(p):
    return "/.claude/skills/" in "/" + p or p.startswith(".claude/skills/") \
        or p.endswith(".skill")


# ------------------------------------------------------------- pre rules

def pre_skills(call):
    tool, inp = call["tool_name"], call["tool_input"]
    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        p = inp.get("file_path") or inp.get("notebook_path") or ""
        return _is_skills_path(_rel(call["cwd"], p))
    if tool == "Bash":
        cmd = inp.get("command", "")
        # a write by the shell: redirection, sed -i, cp/mv/rm/tee with the path as target
        for line in _strip_heredocs(cmd).splitlines():
            if "sync_skills.py" not in line and \
                    re.search(r">>?\s*\S*(\.claude/skills/|\.skill\b)", line):
                return True
        for seg in _segments(cmd):
            if "sync_skills.py" in seg:
                continue
            if re.search(r">>?\s*\S*(\.claude/skills/|\.skill\b)", seg):
                return True
            w = _words(seg)
            if not w:
                continue
            if w[0] in ("cp", "mv", "tee", "rm", "touch") and \
                    any(_is_skills_path(x) for x in w[-1:] if not x.startswith("-")):
                return True
            if w[0] in ("rm", "tee") and any(_is_skills_path(x) for x in w[1:]):
                return True
            if w[0] == "sed" and any(x.startswith("-i") for x in w) and \
                    any(_is_skills_path(x) for x in w[1:]):
                return True
    return False


def pre_push(call):
    if call["tool_name"] != "Bash":
        return False
    for seg in _segments(call["tool_input"].get("command", "")):
        w = _words(seg)
        if len(w) < 2 or w[0] != "git":
            continue
        i = 1
        while i < len(w) and w[i] in ("-C", "-c"):
            i += 2
        if i >= len(w) or w[i] != "push":
            continue
        args = [x for x in w[i + 1:] if not x.startswith("-")]
        if any(x in ("--all", "--mirror") for x in w):
            return True
        refs = args[1:]
        if not refs:
            current = _git(call["cwd"], "rev-parse", "--abbrev-ref", "HEAD")
            if current == "main":
                return True
            continue
        current = _git(call["cwd"], "rev-parse", "--abbrev-ref", "HEAD")
        if "--tags" in w:                    # tags are not branches (08/11 S10)
            continue
        for ref in refs:
            dest = ref.lstrip("+").split(":")[-1].removeprefix("refs/heads/")
            if dest.startswith("refs/tags/"):
                continue
            if dest in ("main", "master") or (current and dest not in (current, "HEAD")):
                return True
    return False


def pre_secret(call):
    if call["tool_name"] != "Bash":
        return False
    for pipe in _pipelines(call["tool_input"].get("command", "")):
        for k, seg in enumerate(pipe):
            w = _words(seg)
            if not w:
                continue
            if w[0] == "cat" and any(re.search(r"/proc/\S*/environ", x) for x in w[1:]):
                return True                      # every variable (08/11 S10)
            if w[0] in ("env", "printenv", "export", "set", "declare") and \
                    all(x.startswith("-") for x in w[1:]):
                # piped into a counter or a name-only filter, no value is shown (08/11 S10)
                rest = " ".join(pipe[k + 1:])
                if re.search(r"^wc\b|\bgrep\s+-\w*[cqlL]|\bcut\b.*-f\s*1\b|"
                             r"sed\s+'?s/=\.\*//", rest):
                    continue
                return True                      # dumps every variable, keys included
            if w[0] == "printenv" and any(re.fullmatch(SECRETS, x) for x in w[1:]):
                return True
            if w[0] in ("echo", "printf", "print") and re.search(r"\$\{?" + SECRETS, seg):
                return True
            if re.search(r"(os\.environ|getenv)\W+" + SECRETS, seg) and "print" in seg:
                return True
    return False


def pre_watch(call):
    if call["tool_name"] != "Bash":
        return False
    cmd = call["tool_input"].get("command", "")
    for seg in _segments(cmd):
        w = _words(seg)
        # only a segment that runs watch.py (08/11 S10: an assignment or a
        # patch script naming the file was blocked)
        args = [x for x in w if not x.startswith("-")]
        runs = bool(w) and (os.path.basename(w[0]) == "watch.py" or (
            os.path.basename(w[0]).startswith("python") and len(args) > 1
            and args[1].endswith("watch/watch.py")))
        if not runs or "--force" in w or "--refresh-medians" in w \
                or "--help" in w or "-h" in w:
            continue
        m = re.search(r"--date[ =](\d{4}-\d{2}-\d{2})", seg)
        day = m.group(1) if m else dt.datetime.now(dt.timezone.utc).date().isoformat()
        if (pathlib.Path(call["cwd"]) / WATCH_DIR / f"{day}.md").exists():
            return True
    return False


def pre_commit(call):
    """Cheap test memory: the post hook records, per session, the result of
    the last `unittest` run (from its output) and any code edit after it."""
    if call["tool_name"] != "Bash":
        return False
    cmd = call["tool_input"].get("command", "")
    if not any(_words(s)[:2] == ["git", "commit"] for s in _segments(cmd) if _words(s)):
        return False
    st = _load_state(call["cwd"]).get(call.get("session_id", ""), {})
    if not st.get("code_edited"):
        return False                         # no code touched in this session
    return st.get("tests") != "ok" or st.get("edited_after_tests", False)


# ------------------------------------------------------------ post rules

def _touched(call):
    tool, inp = call["tool_name"], call["tool_input"]
    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        return [_rel(call["cwd"], inp.get("file_path") or inp.get("notebook_path"))]
    return []


def _lines(cwd, rel):
    try:
        return len((pathlib.Path(cwd) / rel).read_text(encoding="utf-8").splitlines())
    except Exception:
        return 0


def post_state(call):
    cmd = call["tool_input"].get("command", "") if call["tool_name"] == "Bash" else ""
    writes = re.search(r"(>|\bsed\s+-i|\btee\b|\bcp\b|\bmv\b|\bcheckout\b|\brestore\b)[^;&|]*STATE\.md", cmd)
    if STATE_MD in _touched(call) or writes:
        return _lines(call["cwd"], STATE_MD) > STATE_LINES
    return False


def post_report(call):
    cmd = call["tool_input"].get("command", "") if call["tool_name"] == "Bash" else ""
    files = [p for p in _touched(call) if p.startswith(WATCH_DIR + "/") and p.endswith(".md")]
    if "watch/watch.py" in cmd:
        d = pathlib.Path(call["cwd"]) / WATCH_DIR
        files = [max(d.glob("*.md"), default=None, key=lambda p: p.stat().st_mtime)]
        files = [_rel(call["cwd"], f) for f in files if f]
    return any(_lines(call["cwd"], f) > REPORT_LINES for f in files)


def looks_french(text):
    words = re.findall(r"[a-zàâçéèêëîïôûùüœ']+", text.lower())
    if len(words) < 20:
        return False
    fr = sum(w in FRENCH_WORDS for w in words)
    accents = len(re.findall(r"[àâçéèêëîïôûùœ]", text.lower()))
    return fr / len(words) > 0.08 and accents / len(words) > 0.03


def post_french(call):
    if call["tool_name"] != "Write":
        return False
    rel = _rel(call["cwd"], call["tool_input"].get("file_path", ""))
    if not (rel.startswith("whosedime/") or rel.startswith("docs/whosedime/")):
        return False
    if _git(call["cwd"], "ls-files", "--", rel):
        return False                         # already tracked: not a new file
    return looks_french(call["tool_input"].get("content", ""))


def post_critique(call):
    if call["tool_name"] != "Bash":
        return False
    cmd = call["tool_input"].get("command", "")
    if not any(_words(s)[:2] == ["git", "commit"] for s in _segments(cmd) if _words(s)):
        return False
    added = _git(call["cwd"], "show", "--name-only", "--diff-filter=A",
                 "--format=", "HEAD").splitlines()
    deliverables = [p for p in added if (p.startswith("whosedime/") or
                    p.startswith("docs/whosedime/")) and not p.endswith(".jsonl")]
    if not deliverables:
        return False
    today = dt.date.today().isoformat()
    try:
        log = (pathlib.Path(call["cwd"]) / CRITIQUE_LOG).read_text(encoding="utf-8")
    except Exception:
        return True
    return f'"date": "{today}"' not in log


def record(call):
    """Post hook bookkeeping for the commit rule (no output)."""
    sid = call.get("session_id", "")
    state = _load_state(call["cwd"])
    st = state.setdefault(sid, {})
    changed = False
    for p in _touched(call):
        if pathlib.Path(p).suffix in CODE_EXT:
            st["code_edited"] = True
            st["edited_after_tests"] = True
            changed = True
    if call["tool_name"] == "Bash" and "unittest" in call["tool_input"].get("command", ""):
        resp = call.get("tool_response") or {}
        out = resp if isinstance(resp, str) else \
            (str(resp.get("stdout", "")) + "\n" + str(resp.get("stderr", "")))
        if re.search(r"^Ran \d+ tests?", out, re.M):
            ok = re.search(r"^OK\b", out, re.M) and not re.search(r"^FAILED\b", out, re.M)
            st["tests"] = "ok" if ok else "failed"
            st["edited_after_tests"] = False
            changed = True
    if changed:
        state = {k: v for k, v in list(state.items())[-20:]}   # keep it small
        _save_state(call["cwd"], state)


CHECKS = {"skills-edit": pre_skills, "push-branch": pre_push, "secret-print": pre_secret,
          "watch-rerun": pre_watch, "commit-untested": pre_commit,
          "state-length": post_state, "report-length": post_report,
          "french-text": post_french, "critique-missing": post_critique}


# ------------------------------------------------------------------ main

def summary(call):
    inp = call["tool_input"]
    s = inp.get("command") or inp.get("file_path") or inp.get("notebook_path") or ""
    s = re.sub(SECRETS + r"=\S+", r"\1=***", s)
    return f"{call['tool_name']}: {s}"[:200]


def log(call, rule, action):
    line = dict(date=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                session=call.get("session_id", ""), rule=rule, call=summary(call),
                action=action)
    try:
        with open(pathlib.Path(call["cwd"]) / LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
    except Exception:
        pass


def evaluate(when, call):
    """[(rule, action, message)] for this call."""
    out = []
    for name, (w, action, _src, msg) in RULES.items():
        if w == when:
            try:
                if CHECKS[name](call):
                    out.append((name, action, msg))
            except Exception:
                pass
    return out


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    when = argv[0] if argv else "pre"
    try:
        call = json.load(sys.stdin)
        call.setdefault("cwd", os.getcwd())
        call.setdefault("tool_input", {})
        call["tool_input"] = call["tool_input"] or {}
    except Exception:
        return 0
    if os.environ.get("WHOSEDIME_GUARD") == "off":
        return 0
    if when == "post":
        try:
            record(call)
        except Exception:
            pass
    found = evaluate(when, call)
    if not found:
        return 0
    lines = []
    for rule, action, msg in found:
        log(call, rule, action)
        verb = "BLOCKED" if action == "block" else "WARNING"
        lines.append(f"guard {verb} [{rule}]: {msg}.")
    print("\n".join(lines), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
