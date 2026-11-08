#!/usr/bin/env python3
"""Live guard for Whose Dime sessions (S10, decision D15).

Claude Code runs this script on every tool call (hooks in
.claude/settings.json). It reads the hook JSON on stdin and:

- before a call (PreToolUse): blocks a call that breaks a rule of CLAUDE.md
  or ROADMAP.md, with the rule and the fix in one line;
- after a call (PostToolUse): warns, and the agent reads the warning at once.

Every block and warning is appended to docs/whosedime/guard_log.jsonl.
Standard library only; no network, no model. A crash or a timeout lets the
call through (Claude Code treats exit 1 and timeouts as non-blocking): the
guard can only fail open.

    echo '{"hook_event_name": "PreToolUse", ...}' | python3 tools/guard/guard.py

How "tests ran after the last code edit" is known (rule commit-untested),
cheaply: when a Bash call starts a unittest/pytest run, the guard writes
{"time", "ok": false} in a per-session state file; when the call ends with
"OK" (or pytest's "passed" and no "failed") in its output, PostToolUse sets
ok to true. A run that fails or is interrupted stays false. At `git commit`,
the guard asks `git status` for changed .py/.ipynb files: any of them
modified after the last run's start, or a last run not ok, blocks.
"""
import datetime as dt
import json
import os
import pathlib
import re
import shlex
import subprocess
import sys
import time

# ------------------------------------------------------------------ rules
# One table. kind: "block" (PreToolUse, the call does not run) or "warn"
# (PostToolUse, the call ran; the agent reads the line). "case" is the real
# case that justifies the rule (critique_log.jsonl or the S09 cases).

RULES = {
    "skills-generated": dict(
        kind="block",
        rule="`.claude/skills/` and `*.skill` are generated (CLAUDE.md, ROADMAP rule 4)",
        fix="edit `<channel>/<skill>/` then run `python3 tools/sync_skills.py`",
        case="ROADMAP rule 4; S10 live check"),
    "push-main": dict(
        kind="block",
        rule="`main` changes only through a pull request Franco merges (CLAUDE.md, D5)",
        fix="push the work branch named in STATE.md and let Franco merge",
        case="CLAUDE.md branch rule; S10 live check"),
    "push-other-branch": dict(
        kind="block",
        rule="push only the current branch (CLAUDE.md: work on the branch named in STATE.md)",
        fix="`git push -u origin <current branch>`, or check out the branch first",
        case="critique_log 2026-11-08 build_automation: three sessions push to one branch"),
    "secret-print": dict(
        kind="block",
        rule="never print YOUTUBE_API_KEY or SUPADATA_API_KEY (CLAUDE.md, ROADMAP rule 8)",
        fix="test presence only: `[ -n \"$YOUTUBE_API_KEY\" ] && echo set`",
        case="ROADMAP rule 8"),
    "watch-rerun": dict(
        kind="block",
        rule="one watch run per date: a second run spends the units again (S09: 520 units in a day)",
        fix="read the existing report; rerun only if Franco asks, with `--force`",
        case="critique_log 2026-11-08 build_S09_report: run twice, 520 units"),
    "commit-untested": dict(
        kind="block",
        rule="tests green before committing code (CLAUDE.md, ROADMAP rule 5)",
        fix="run `python3 -m unittest discover -s tests`, fix until OK, then commit",
        case="ROADMAP rule 5"),
    "state-length": dict(
        kind="warn",
        rule="docs/whosedime/STATE.md is 60 lines at most (ROADMAP hand-off)",
        fix="shorten STATE.md now (move detail to the session prompt or DECISIONS.md)",
        case="critique_log 2026-11-08 build_S09_tool: 62-line STATE.md"),
    "watch-report-length": dict(
        kind="warn",
        rule="a watch report is one page: 100 lines at most",
        fix="cut the report to its tables and counts; the full lists stay in last_run.json",
        case="critique_log 2026-11-08 build_S09_report: 184-line report"),
    "french-text": dict(
        kind="warn",
        rule="everything committed for Whose Dime is in English (D2)",
        fix="rewrite the file in English (French goes only to Franco, in the chat)",
        case="D2; Zehon files in French sit beside Whose Dime ones"),
    "critique-missing": dict(
        kind="warn",
        rule="every deliverable gets a line in critique_log.jsonl (CRITIQUE_PROTOCOL.md)",
        fix="self-critique, ask Franco's grade, append the line and commit it",
        case="critique_log 2026-11-08 build_S09_tool: no check while the agent works"),
}

SECRETS = ("YOUTUBE_API_KEY", "SUPADATA_API_KEY")
STATE_MAX = 60
REPORT_MAX = 100
STATE_PATH = "docs/whosedime/STATE.md"
WATCH_SCRIPT = "whosedime/watch/watch.py"
WATCH_REPORTS = "docs/whosedime/watch"
LOG_PATH = "docs/whosedime/guard_log.jsonl"
CRITIQUE_LOG = "docs/whosedime/critique_log.jsonl"
ENGLISH_DIRS = ("whosedime/", "docs/whosedime/")
DELIVERABLE_DIRS = ("whosedime/", "docs/whosedime/", "tools/")
NOT_DELIVERABLES = {STATE_PATH, LOG_PATH, CRITIQUE_LOG, "whosedime/watch/last_run.json",
                    "whosedime/watch/channels.csv"}
CODE_SUFFIXES = (".py", ".ipynb")
TEXT_SUFFIXES = (".md", ".txt", ".py", ".json", ".jsonl", ".csv", ".tsv", ".ipynb")
EDIT_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")

# French detector, measured 08/11 on the repo: English files of whosedime/ and
# docs/whosedime/ score at most 0.017 (stopwords) and 1.4 (accents per 1,000
# characters); Zehon's French Markdown at least 0.11 and 19.
FR_WORDS = set("le la les un une des du est sont pas avec pour dans nous vous qui "
               "que sur au aux ce cette ces mais ou donc être avoir fait très aussi "
               "comme il elle ils elles leur".split())
FR_ACCENTS = re.compile(r"[àâçéèêëîïôûùüÿœ]", re.I)
FR_MIN_WORDS = 20
FR_RATIO = 0.05
FR_ACCENTS_PER_K = 5.0     # counts only with French stopwords at 2.5 % or more:
                           # a short English text with "café crème" scored 11

TEST_CMD = re.compile(r"\b(unittest|pytest)\b")


# --------------------------------------------------------------- helpers

def repo_root(data):
    return pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".")


def rel(path, root):
    p = pathlib.Path(path)
    try:
        return p.resolve().relative_to(root.resolve()).as_posix()
    except (ValueError, OSError):
        return p.as_posix()


def git(root, *args):
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                           text=True, timeout=2)
        return r.stdout if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def state_file(data):
    base = pathlib.Path(os.environ.get("GUARD_STATE_DIR") or "/tmp/whosedime_guard")
    sid = re.sub(r"[^\w-]", "_", data.get("session_id") or "nosession")
    return base / f"{sid}.json"


def load_state(data):
    try:
        return json.loads(state_file(data).read_text())
    except (OSError, ValueError):
        return {}


def save_state(data, st):
    f = state_file(data)
    try:
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(st))
    except OSError:
        pass


def summary(data):
    ti = data.get("tool_input") or {}
    s = ti.get("command") or ti.get("file_path") or ti.get("notebook_path") or ""
    s = " ".join(str(s).split())
    return f"{data.get('tool_name', '?')}: {s[:160]}"


def log(root, data, rule, detail):
    line = dict(date=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                session=data.get("session_id", ""), rule=rule,
                action=RULES[rule]["kind"], call=summary(data), detail=detail)
    try:
        p = root / LOG_PATH
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
    except OSError:
        pass


def message(rule, detail):
    r = RULES[rule]
    head = "BLOCKED" if r["kind"] == "block" else "WARNING"
    return f"Guard {head} [{rule}]: {detail}. Rule: {r['rule']}. Fix: {r['fix']}."


HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?(?:\n\s*\2\s*(?:\n|$)|\Z)", re.S)


def strip_heredocs(command):
    """Heredoc bodies are data, not commands (S10: a Python heredoc naming
    watch.py was blocked as a watch run). Keeps the line that opens them."""
    return HEREDOC.sub(lambda m: m.group(0).split("\n", 1)[0] + "\n", command or "")


OPERATORS = {"&&", "||", ";", "&", "|", ";;", "|&"}


def tokens(command):
    """Quote-aware tokens of a shell line; operators are their own tokens
    (S10: splitting on '&&' before reading quotes took a quoted JSON string
    for a `git push`)."""
    text = strip_heredocs(command).replace("\\\n", " ").replace("\n", " ; ")
    lex = shlex.shlex(text, posix=True, punctuation_chars=";&|")
    lex.whitespace_split = True
    try:
        return list(lex)
    except ValueError:                       # unbalanced quote: plain split
        return text.split()


def pipelines(command):
    """Pipelines of a shell line: lists of simple commands joined by '|'."""
    out, pipe, cmd = [], [], []
    for t in tokens(command) + [";"]:
        if t in OPERATORS:
            if cmd:
                pipe.append(cmd)
            cmd = []
            if t not in ("|", "|&") and pipe:
                out.append(pipe)
                pipe = []
        else:
            cmd.append(t)
    return out


def segments(command):
    """Simple commands of a shell line, each as a token list (best effort)."""
    return [c for pipe in pipelines(command) for c in pipe]


def git_sub(toks):
    """('push', args) for a `git [-C x] push args` token list, else (None, [])."""
    if not toks or os.path.basename(toks[0]) != "git":
        return None, []
    i = 1
    while i < len(toks) and toks[i].startswith("-"):
        i += 2 if toks[i] in ("-C", "-c", "--git-dir", "--work-tree") else 1
    if i >= len(toks):
        return None, []
    return toks[i], toks[i + 1:]


# ------------------------------------------------------- PreToolUse checks

def check_skills(data, root):
    ti = data.get("tool_input") or {}
    if data.get("tool_name") in EDIT_TOOLS:
        p = rel(ti.get("file_path") or ti.get("notebook_path") or "", root)
        if "/.claude/skills/" in "/" + p or p.endswith(".skill"):
            return f"`{p}` is a generated file"
    elif data.get("tool_name") == "Bash":
        cmd = strip_heredocs(ti.get("command", ""))
        target =r"[^\s;|&]*(?:\.claude/skills/|\.skill\b)"
        if re.search(r"(?:>>?|\btee\b(?:\s+-a)?)\s*" + target, cmd) or \
           re.search(r"\bsed\s+(?:-\w*i\w*|--in-place)\b[^;|&]*" + target, cmd):
            return "the command writes into a generated skill file"
    return None


def check_push(data, root):
    if data.get("tool_name") != "Bash":
        return None
    current = None
    for toks in segments(data["tool_input"].get("command", "")):
        sub, args = git_sub(toks)
        if sub != "push":
            continue
        if current is None:
            current = git(root, "rev-parse", "--abbrev-ref", "HEAD").strip()
        flags = [a for a in args if a.startswith("-")]
        pos = [a for a in args if not a.startswith("-")]
        if "-o" in args or "--push-option" in args or "--repo" in args:
            pos = pos[1:] if pos else pos          # rough: an option took a value
        if {"--all", "--mirror"} & set(flags):
            return "push-main", "`git push --all/--mirror` would push `main`"
        for spec in pos[1:]:                       # pos[0] is the remote
            dst = spec.split(":")[-1].lstrip("+")
            dst = re.sub(r"^refs/heads/", "", dst)
            if spec.startswith(":"):
                dst = spec[1:]
            if dst in ("HEAD", "") or dst == current:
                continue
            if dst in ("main", "master"):
                return "push-main", f"`git push` to `{dst}`"
            if not dst.startswith("refs/tags/") and "--tags" not in flags:
                return "push-other-branch", f"`git push` to `{dst}` while on `{current}`"
        if not pos[1:] and current in ("main", "master"):
            return "push-main", "`git push` from `main`"
    return None


def check_secret(data, root):
    if data.get("tool_name") != "Bash":
        return None
    cmd = data["tool_input"].get("command", "")
    names = "|".join(SECRETS)
    for pipe in pipelines(cmd):
        first = pipe[0]
        prog = os.path.basename(first[0])
        rest = " ".join(first[1:])
        if prog in ("echo", "printf", "print") and \
                re.search(r"\$\{?(?:" + names + r")\b", rest):
            return f"`{prog}` of a secret"
        if prog == "cat" and re.search(r"/proc/[^\s]*/environ", rest):
            return "`cat /proc/.../environ` prints every secret"
        if prog in ("env", "printenv") or (prog == "export" and first[1:] == ["-p"]):
            args = [a for a in first[1:] if not a.startswith("-")]
            if prog == "env" and args:
                if not all("=" in a for a in args):  # env VAR=x cmd: runs cmd
                    continue
            if prog == "printenv" and args and not set(args) & set(SECRETS):
                continue
            filters = " ".join(" ".join(c) for c in pipe[1:])
            if re.search(r"\bwc\b|\bgrep\s+-\w*[cqlL]|\bcut\b.*-f\s*1\b|"
                         r"sed\s+['\"]?s/=\.\*//", filters):
                continue
            return f"`{prog}` prints the environment, secrets included"
    return None


def check_watch(data, root):
    if data.get("tool_name") != "Bash":
        return None
    for toks in segments(data["tool_input"].get("command", "")):
        args = [t for t in toks if not t.startswith("-")]
        runs = os.path.basename(toks[0]) == "watch.py" or (
            os.path.basename(toks[0]).startswith("python") and len(args) > 1
            and os.path.basename(args[1]) == "watch.py")
        if not runs:
            continue
        if {"--force", "--refresh-medians", "-h", "--help"} & set(toks):
            continue
        date = dt.datetime.now(dt.timezone.utc).date().isoformat()
        for i, t in enumerate(toks):
            if t == "--date" and i + 1 < len(toks):
                date = toks[i + 1]
            elif t.startswith("--date="):
                date = t.split("=", 1)[1]
        if (root / WATCH_REPORTS / f"{date}.md").exists():
            return f"a watch report for {date} already exists ({WATCH_REPORTS}/{date}.md)"
    return None


def changed_code(root):
    out = []
    for line in git(root, "status", "--porcelain", "--untracked-files=all").splitlines():
        path = line[3:].split(" -> ")[-1].strip('"')
        if path.endswith(CODE_SUFFIXES) and (root / path).exists():
            out.append(path)
    return out


def check_commit(data, root):
    if data.get("tool_name") != "Bash":
        return None
    if not any(git_sub(t)[0] == "commit" for t in segments(data["tool_input"].get("command", ""))):
        return None
    code = changed_code(root)
    if not code:
        return None
    last = load_state(data).get("last_test")
    if not last:
        return f"no test run in this session, and code changed: {', '.join(code[:3])}"
    if not last.get("ok"):
        return "the last test run of this session failed or did not finish"
    newer = [p for p in code if (root / p).stat().st_mtime > last["time"]]
    if newer:
        return f"code edited after the last test run: {', '.join(newer[:3])}"
    return None


PRE_CHECKS = [("skills-generated", check_skills), ("push", check_push),
              ("secret-print", check_secret), ("watch-rerun", check_watch),
              ("commit-untested", check_commit)]


def pre(data, root):
    if data.get("tool_name") == "Bash" and TEST_CMD.search(data["tool_input"].get("command", "")):
        st = load_state(data)
        st["last_test"] = dict(time=time.time(), ok=False,
                               command=data["tool_input"]["command"][:120])
        save_state(data, st)
    for name, fn in PRE_CHECKS:
        hit = fn(data, root)
        if not hit:
            continue
        rule, detail = hit if isinstance(hit, tuple) else (name, hit)
        log(root, data, rule, detail)
        return dict(hookSpecificOutput=dict(
            hookEventName="PreToolUse", permissionDecision="deny",
            permissionDecisionReason=message(rule, detail)))
    return None


# ------------------------------------------------------ PostToolUse checks

def french_score(text):
    words = re.findall(r"[a-zàâçéèêëîïôûùüÿœ']+", text.lower())
    if len(words) < FR_MIN_WORDS:
        return 0.0, 0.0
    ratio = sum(w in FR_WORDS for w in words) / len(words)
    accents = len(FR_ACCENTS.findall(text)) * 1000 / max(1, len(text))
    return ratio, accents


def is_french(text):
    ratio, accents = french_score(text)
    return ratio >= FR_RATIO or (accents >= FR_ACCENTS_PER_K and ratio >= FR_RATIO / 2)


def touched_files(data, root):
    ti = data.get("tool_input") or {}
    if data.get("tool_name") in EDIT_TOOLS:
        p = ti.get("file_path") or ti.get("notebook_path")
        return [rel(p, root)] if p else []
    return []


def untracked(root, prefixes):
    out = []
    for line in git(root, "status", "--porcelain", "--untracked-files=all").splitlines():
        if line.startswith("?? "):
            p = line[3:].strip('"')
            if p.startswith(prefixes):
                out.append(p)
    return out


def post(data, root):
    warnings = []
    tool = data.get("tool_name")
    ti = data.get("tool_input") or {}
    cmd = ti.get("command", "") if tool == "Bash" else ""

    if tool == "Bash" and TEST_CMD.search(cmd):
        st = load_state(data)
        out = json.dumps(data.get("tool_response", ""))
        ok = bool(re.search(r"(^|\\n)OK\b", out)) and "FAILED" not in out
        ok = ok or (bool(re.search(r"\d+ passed", out)) and not re.search(r"\d+ (failed|error)", out))
        if st.get("last_test"):
            st["last_test"]["ok"] = ok
            save_state(data, st)

    files = touched_files(data, root)
    # STATE.md length
    if STATE_PATH in files or (cmd and "STATE.md" in cmd):
        p = root / STATE_PATH
        if p.exists():
            n = len(p.read_text(encoding="utf-8").splitlines())
            if n > STATE_MAX:
                warnings.append(("state-length", f"{STATE_PATH} has {n} lines"))
    # watch report length
    reports = [f for f in files if f.startswith(WATCH_REPORTS + "/") and f.endswith(".md")]
    if cmd and "watch.py" in cmd:
        d = root / WATCH_REPORTS
        if d.exists():
            newest = sorted(d.glob("*.md"), key=lambda p: p.stat().st_mtime)[-1:]
            reports += [rel(p, root) for p in newest]
    for f in dict.fromkeys(reports):
        p = root / f
        if p.exists():
            n = len(p.read_text(encoding="utf-8").splitlines())
            if n > REPORT_MAX:
                warnings.append(("watch-report-length", f"{f} has {n} lines"))
    # French text in a new file
    st = load_state(data)
    seen = set(st.get("fr_checked", []))
    new = []
    if tool == "Write":
        new = [f for f in files if f.startswith(ENGLISH_DIRS)
               and not git(root, "ls-files", f).strip()]
    elif tool == "Bash" and cmd:
        new = untracked(root, ENGLISH_DIRS)
    for f in new:
        if f in seen or not f.endswith(TEXT_SUFFIXES):
            continue
        seen.add(f)
        try:
            text = (root / f).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if is_french(text):
            ratio, acc = french_score(text)
            warnings.append(("french-text", f"new file {f} reads as French "
                             f"(French stopwords {ratio:.0%}, {acc:.0f} accents per 1,000 characters)"))
    if new:
        st = load_state(data)
        st["fr_checked"] = sorted(seen)
        save_state(data, st)
    # critique-log reminder after a commit
    if tool == "Bash" and any(git_sub(t)[0] == "commit" for t in segments(cmd)):
        names = git(root, "show", "--name-only", "--format=", "HEAD").split()
        if CRITIQUE_LOG not in names:
            dels = [n for n in names if n.startswith(DELIVERABLE_DIRS)
                    and n not in NOT_DELIVERABLES and not n.startswith("docs/whosedime/watch/")]
            if dels:
                try:
                    clog = (root / CRITIQUE_LOG).read_text(encoding="utf-8")
                except OSError:
                    clog = ""
                if not any(os.path.basename(n) in clog for n in dels):
                    warnings.append(("critique-missing", "the commit holds deliverables with "
                                     f"no critique-log line: {', '.join(dels[:3])}"))

    if not warnings:
        return None
    for rule, detail in warnings:
        log(root, data, rule, detail)
    return dict(hookSpecificOutput=dict(
        hookEventName="PostToolUse",
        additionalContext=" ".join(message(r, d) for r, d in warnings)))


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    root = repo_root(data)
    event = data.get("hook_event_name")
    out = pre(data, root) if event == "PreToolUse" else \
        post(data, root) if event == "PostToolUse" else None
    if out:
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
