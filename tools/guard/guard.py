#!/usr/bin/env python3
"""Live guard for Whose Dime sessions (S10, decision D15).

Claude Code runs this script on every tool call (hooks in
.claude/settings.json). It reads the hook JSON on stdin and:

- `pre` (PreToolUse): blocks a call that breaks a rule of CLAUDE.md or
  ROADMAP.md; the agent reads the reason (rule + fix, one line) at once.
- `post` (PostToolUse) and `post-failure` (PostToolUseFailure): warns
  after a call (the agent reads the warning before going on) and records
  test runs and code edits for the commit rule.

Every block and warning is appended to docs/whosedime/guard_log.jsonl.
Standard library only; no network, no model. A bug in the guard never
blocks work: any exception ends in silence (exit 0).

    echo '<hook json>' | python3 tools/guard/guard.py pre
    python3 tools/guard/guard.py rules        # print the table

Environment (tests): WHOSEDIME_GUARD_ROOT (repository root),
WHOSEDIME_GUARD_LOG (log path), WHOSEDIME_GUARD_STATE (state directory).
"""
import datetime as dt
import json
import os
import pathlib
import re
import shlex
import subprocess
import sys
import tempfile

# ------------------------------------------------------------------ RULES
# One row per rule. `when`: pre (before the call) or post (after it).
# `action`: block or warn. `case`: the real case that let the rule in
# (critique_log.jsonl line, or the S09 cases named in the S10 prompt).
# `check`: the function below that returns the detail, or None.
RULES = [
    dict(id="skills-generated", when="pre", action="block",
         rule="never edit .claude/skills/ or *.skill by hand (CLAUDE.md)",
         fix="edit <channel>/<skill>/, then run python3 tools/sync_skills.py",
         case="CLAUDE.md rule; ROADMAP rule 4", check="check_skills_edit"),
    dict(id="push-other-branch", when="pre", action="block",
         rule="push only the current work branch; main changes through a pull request Franco merges",
         fix="git push -u origin <current branch>; for main, open a pull request",
         case="CLAUDE.md rule; ROADMAP rule 2", check="check_push"),
    dict(id="secret-print", when="pre", action="block",
         rule="never print YOUTUBE_API_KEY or SUPADATA_API_KEY (CLAUDE.md)",
         fix='test it without printing: [ -n "$YOUTUBE_API_KEY" ] && echo set',
         case="CLAUDE.md rule; ROADMAP rule 8", check="check_secret_print"),
    dict(id="watch-rerun", when="pre", action="block",
         rule="one watch run per date (300-unit budget)",
         fix="read the existing report; add --force only if Franco asks for a second run",
         case="S09: run twice on 2026-11-08, 520 units (critique_log line 35)",
         check="check_watch_rerun"),
    dict(id="commit-untested", when="pre", action="block",
         rule="tests green before committing code (CLAUDE.md)",
         fix="run python3 -m unittest discover -s tests, fix it, then commit",
         case="CLAUDE.md rule; ROADMAP rule 5", check="check_commit"),
    dict(id="state-length", when="post", action="warn",
         rule="docs/whosedime/STATE.md is 60 lines at most",
         fix="shorten STATE.md now (merge or drop done lines)",
         case="S09: STATE.md written at 62 lines", check="check_state_length"),
    dict(id="watch-report-length", when="post", action="warn",
         rule="a watch report is one page (100 lines at most)",
         fix="cut the report to one page before going on",
         case="S09: first report 184 lines (critique_log line 35)",
         check="check_report_length"),
    dict(id="french-text", when="post", action="warn",
         rule="everything committed for Whose Dime is in English (D2)",
         fix="rewrite the new file in English (quotes of Franco may stay)",
         case="D2; the S01 merge carried French Zehon files beside whosedime/",
         check="check_french"),
    dict(id="critique-reminder", when="post", action="warn",
         rule="each deliverable gets a self-critique and a critique_log.jsonl line",
         fix="self-critique (5 lines), ask Franco's grade, append the line (CRITIQUE_PROTOCOL.md)",
         case="S09: defects found only at the end-of-task critique (critique_log line 34)",
         check="check_critique"),
]

# ------------------------------------------------------------- constants
KEYS = ("YOUTUBE_API_KEY", "SUPADATA_API_KEY")
STATE_MAX = 60
REPORT_MAX = 100
FILE_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")
PROTECTED_BRANCHES = ("main", "master")
CODE_DIRS = ("whosedime/", "tools/", "tests/", "zehon/", ".claude/")
CODE_SUFFIXES = (".py", ".ipynb", ".sh")
NOT_DELIVERABLES = ("docs/whosedime/critique_log.jsonl", "docs/whosedime/guard_log.jsonl")
TEXT_SUFFIXES = (".md", ".txt", ".py", ".json", ".csv", ".tsv", ".ipynb", ".html")
SEPARATORS = {"&&", "||", ";", "|", "&", "(", ")", "|&", ";;"}
WRAPPERS = {"sudo", "time", "command", "nohup", "exec"}
# French: accents plus function words that are not English words.
FRENCH_ACCENTS = set("éèêëàâçùûôîïœÉÈÊÀÇÔ")
FRENCH_WORDS = set("""le la les des une est et pour que qui dans avec pas sur du
au aux ce cette ces sont mais où nous vous ils elle elles leur leurs très être
fait comme sans entre chez donc alors aussi déjà été avait était sera peut
même encore ou par il on se sa ses son ne qu sont lui""".split())
FRENCH_MIN_WORDS = 40          # shorter text: never judged
FRENCH_WORD_RATIO = 0.12       # share of French function words
FRENCH_ACCENT_RATIO = 0.02     # share of words with a French accent


def root():
    env = os.environ.get("WHOSEDIME_GUARD_ROOT")
    return pathlib.Path(env) if env else pathlib.Path(__file__).resolve().parents[2]


def rel(path):
    """Repository-relative posix path, or None outside the repository."""
    if not path:
        return None
    p = pathlib.Path(path)
    r = root().resolve()
    if not p.is_absolute():
        p = r / p
    try:
        return p.resolve().relative_to(r).as_posix()
    except ValueError:
        return None


# ----------------------------------------------------------- shell parse

def strip_heredocs(cmd):
    """Remove heredoc bodies; return (command, bodies whose $ expand)."""
    expanding = []

    def cut(m):
        if not m.group(1):
            expanding.append(m.group(3))
        return m.group(0).split("\n", 1)[0]
    pat = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n(.*?)\n\s*\2[ \t]*(?=\n|$)", re.S)
    return pat.sub(cut, cmd), expanding


def split_lines(cmd):
    """Split on newlines outside quotes (a quoted multi-line commit message
    stays one token)."""
    lines, cur, quote, esc = [], [], None, False
    for ch in cmd:
        if esc:
            esc = False
        elif ch == "\\" and quote != "'":
            esc = True
        elif quote:
            quote = None if ch == quote else quote
        elif ch in "'\"":
            quote = ch
        elif ch == "\n":
            lines.append("".join(cur))
            cur = []
            continue
        cur.append(ch)
    lines.append("".join(cur))
    return lines


def segments(cmd):
    """Split a shell command into simple commands: [(tokens, separator
    before)]. Quotes are honoured; on a parse error, a plain split."""
    cmd, _ = strip_heredocs(cmd)
    cmd = cmd.replace("\\\n", " ")
    out = []
    for line in split_lines(cmd):
        try:
            lex = shlex.shlex(line, posix=True, punctuation_chars=";&|()")
            lex.whitespace_split = True
            lex.commenters = "#"
            toks = list(lex)
        except ValueError:
            toks = line.split()
        cur, sep = [], ";"
        for t in toks:
            if t in SEPARATORS:
                if cur:
                    out.append((cur, sep))
                cur, sep = [], t
            else:
                cur.append(t)
        if cur:
            out.append((cur, sep))
    return out


def words(tokens):
    """Drop leading VAR=value assignments and wrappers (sudo, time...)."""
    i = 0
    while i < len(tokens) and (re.match(r"^[A-Za-z_]\w*=", tokens[i]) or tokens[i] in WRAPPERS):
        i += 1
    return tokens[i:]


def git_sub(tokens):
    """('push', args, dir) for a git command, else (None, [], None)."""
    w = words(tokens)
    if not w or os.path.basename(w[0]) != "git":
        return None, [], None
    i, gdir = 1, None
    while i < len(w) and w[i].startswith("-"):
        if w[i] in ("-C", "-c", "--git-dir", "--work-tree") and i + 1 < len(w):
            if w[i] == "-C":
                gdir = w[i + 1]
            i += 2
        else:
            i += 1
    if i >= len(w):
        return None, [], None
    return w[i], w[i + 1:], gdir


def current_branch(cwd):
    try:
        r = subprocess.run(["git", "-C", cwd or str(root()), "rev-parse", "--abbrev-ref", "HEAD"],
                           capture_output=True, text=True, timeout=3)
        b = r.stdout.strip()
        return b if r.returncode == 0 and b and b != "HEAD" else None
    except Exception:
        return None


def is_test_run(tokens):
    """None, 'full' or 'partial' for a unittest / pytest command."""
    w = words(tokens)
    text = " ".join(w)
    if "unittest" in text:
        if "discover" in text:
            return "full"
        after = text.split("unittest", 1)[1].split()
        return "full" if not [a for a in after if not a.startswith("-")] else "partial"
    if w and (os.path.basename(w[0]) == "pytest" or "-m pytest" in text):
        args = [a for a in w[1:] if not a.startswith("-") and a not in ("-m", "pytest")]
        return "partial" if any(a.endswith(".py") or "::" in a for a in args) else "full"
    return None


def redirect_targets(tokens):
    """Files written by >, >>, tee, sed -i, cp or mv in one simple command."""
    out, w = [], words(tokens)
    for i, t in enumerate(w):
        m = re.match(r"^\d*>>?(.+)$", t)
        if m and not m.group(1).startswith("&"):
            out.append(m.group(1))
        elif re.match(r"^\d*>>?$", t) and i + 1 < len(w):
            out.append(w[i + 1])
    if w:
        cmd = os.path.basename(w[0])
        args = [a for a in w[1:] if not a.startswith("-")]
        if cmd == "tee":
            out += args
        elif cmd == "sed" and any(a.startswith("-i") or a == "--in-place" for a in w[1:]):
            out += args[1:]
        elif cmd in ("cp", "mv") and len(args) >= 2:
            out.append(args[-1])
    return out


# ----------------------------------------------------------- pre checks

def is_skill_path(r):
    return bool(r) and (r.startswith(".claude/skills/") or r.endswith(".skill"))


def check_skills_edit(ev):
    tin = ev.get("tool_input") or {}
    if ev.get("tool_name") in FILE_TOOLS:
        r = rel(tin.get("file_path") or tin.get("notebook_path"))
        return f"{ev['tool_name']} of {r}" if is_skill_path(r) else None
    if ev.get("tool_name") == "Bash":
        for toks, _ in segments(tin.get("command", "")):
            for t in redirect_targets(toks):
                r = rel(t) if not t.startswith("~") else None
                if is_skill_path(r):
                    return f"shell write to {r}"
    return None


def check_push(ev):
    if ev.get("tool_name") != "Bash":
        return None
    cmd = (ev.get("tool_input") or {}).get("command", "")
    cur = None
    for toks, _ in segments(cmd):
        sub, args, gdir = git_sub(toks)
        if sub in ("checkout", "switch") and "--" not in args:
            pos = [a for a in args if not a.startswith("-")]
            if pos:
                cur = pos[0]
            continue
        if sub != "push":
            continue
        if cur is None:
            cur = current_branch(gdir or ev.get("cwd"))
        if "--all" in args or "--mirror" in args or "--branches" in args:
            return "git push --all/--mirror pushes every branch"
        pos, skip, delete = [], False, False
        for a in args:
            if skip:
                skip = False
            elif a in ("-o", "--push-option", "--repo", "--receive-pack", "--exec"):
                skip = True
            elif a in ("-d", "--delete"):
                delete = True
            elif not a.startswith("-"):
                pos.append(a)
        refspecs = pos[1:]
        if not refspecs:
            if cur in PROTECTED_BRANCHES:
                return f"git push from {cur}"
            continue
        for spec in refspecs:
            spec = spec.lstrip("+")
            if spec.startswith("refs/tags/"):
                continue
            src, _, dst = spec.partition(":")
            dst = dst or src
            if dst == "HEAD":
                dst = cur
            dst = (dst or "").replace("refs/heads/", "")
            if dst in PROTECTED_BRANCHES:
                return f"git push to {dst}"
            if cur and dst != cur:
                return f"git push {'--delete ' if delete else ''}to {dst} (current branch: {cur})"
    return None


def _mentions_key(token):
    for k in KEYS:
        if re.search(r"\$\{?" + k + r"\b", token) and "${#" + k not in token:
            return k
    return None


def _dump_consumer(segs, i):
    """A full env dump at segment i: 'safe', 'leak' or 'unsure' from its pipe."""
    if i + 1 >= len(segs) or segs[i + 1][1] not in ("|", "|&"):
        return "leak"
    w = words(segs[i + 1][0])
    cmd = os.path.basename(w[0]) if w else ""
    opts = [a for a in w[1:] if a.startswith("-")]
    args = [a for a in w[1:] if not a.startswith("-")]
    if cmd in ("wc",):
        return "safe"
    if cmd == "cut" and any(re.match(r"^-f1$|^-f$", o) for o in opts) or (
            cmd == "cut" and "-f" in opts and args[-1:] == ["1"]):
        return "safe"
    if cmd in ("grep", "egrep", "rg"):
        if any(o in ("-q", "-c", "-l", "--count", "--quiet") or re.match(r"^-[a-zA-Z]*[qcl]", o)
               for o in opts):
            return "safe"
        pattern = " ".join(args).upper()
        if any(o.startswith("-v") for o in opts) or any(
                s in pattern for s in ("KEY", "YOUTUBE", "SUPADATA", "API", ".", "*")):
            return "leak"
        return "safe"
    if cmd in ("sort", "head", "tail", "cat", "less", "more", "tee", "awk", "sed", "uniq"):
        return "leak"
    return "unsure"


def check_secret_print(ev):
    if ev.get("tool_name") != "Bash":
        return None
    cmd = (ev.get("tool_input") or {}).get("command", "")
    _, bodies = strip_heredocs(cmd)
    for b in bodies:
        k = _mentions_key(b)
        if k:
            return f"heredoc expands ${k}"
    segs = segments(cmd)
    for i, (toks, _) in enumerate(segs):
        w = words(toks)
        if not w:
            continue
        name = os.path.basename(w[0])
        args = w[1:]
        if name in ("echo", "printf", "print"):
            for t in args:
                k = _mentions_key(t)
                if k:
                    return f"{name} ${k}"
        if name in ("python", "python3", "node", "perl", "ruby") and any(
                k in " ".join(args) for k in KEYS):
            text = " ".join(args)
            if re.search(r"\bprint\b|console\.log|puts|\bsay\b", text):
                k = next(k for k in KEYS if k in text)
                return f"{name} prints {k}"
        dump = False
        if name == "env":
            rest = [a for a in args if not a.startswith("-") and "=" not in a]
            dump = not rest
        elif name == "printenv":
            named = [a for a in args if not a.startswith("-")]
            hit = [a for a in named if a in KEYS]
            if hit:
                return f"printenv {hit[0]}"
            dump = not named
        elif name in ("export", "declare", "typeset") and (not args or set(args) <= {"-p", "-x", "-px"}):
            dump = True
        elif name == "set" and not args:
            dump = True
        if any("/environ" in a for a in args) and name in ("cat", "strings", "xargs", "tr", "less"):
            return f"{name} of a process environ file"
        if dump:
            verdict = _dump_consumer(segs, i)
            if verdict == "leak":
                return f"{' '.join(w[:2])} prints every variable, the keys included"
            if verdict == "unsure":
                return "WARN:" + f"{' '.join(w[:2])} piped to a filter the guard cannot read"
    return None


def watch_date(args):
    for j, a in enumerate(args):
        if a == "--date" and j + 1 < len(args):
            return args[j + 1]
        if a.startswith("--date="):
            return a.split("=", 1)[1]
    return dt.datetime.now(dt.timezone.utc).date().isoformat()


def watch_calls(cmd):
    """[(args, date)] for each watch.py run in a command (not --refresh-medians / --help)."""
    out = []
    for toks, _ in segments(cmd):
        w = words(toks)
        if not w or not (os.path.basename(w[0]).startswith("python") or w[0].endswith("watch.py")):
            continue                     # `git add watch.py` is not a run
        for j, t in enumerate(w):
            if t.endswith("watch/watch.py") or t == "watch.py":
                args = w[j + 1:]
                if not {"--refresh-medians", "-h", "--help"} & set(args):
                    out.append((args, watch_date(args)))
                break
    return out


def check_watch_rerun(ev):
    if ev.get("tool_name") != "Bash":
        return None
    for args, date in watch_calls((ev.get("tool_input") or {}).get("command", "")):
        if "--force" in args:
            continue
        if (root() / "docs" / "whosedime" / "watch" / f"{date}.md").exists():
            return f"docs/whosedime/watch/{date}.md already exists"
    return None


def check_commit(ev):
    if ev.get("tool_name") != "Bash":
        return None
    segs = segments((ev.get("tool_input") or {}).get("command", ""))
    state = load_state(ev)
    chained_ok = False
    for toks, sep in segs:
        kind = is_test_run(toks)
        if kind:
            chained_ok = kind == "full"
            continue
        sub, args, _ = git_sub(toks)
        if sub != "commit":
            if sep != "&&":
                chained_ok = False
            continue
        if "--dry-run" in args or (chained_ok and sep == "&&"):
            return None
        last = state.get("last_test")
        if last and not last.get("ok"):
            return f"the last test run failed ({last.get('summary', 'see its output')})"
        edit = state.get("last_code_edit", -1)
        if edit >= 0 and state.get("last_full_pass", -1) < edit:
            what = state.get("last_code_file", "a code file")
            return f"{what} was edited after the last full test run"
    return None


# ---------------------------------------------------------- post checks

def touched_files(ev):
    """Repository-relative files a call wrote (file tools, or shell writes)."""
    tin = ev.get("tool_input") or {}
    if ev.get("tool_name") in FILE_TOOLS:
        r = rel(tin.get("file_path") or tin.get("notebook_path"))
        return [r] if r else []
    if ev.get("tool_name") == "Bash":
        out = []
        for toks, _ in segments(tin.get("command", "")):
            out += [r for r in (rel(t) for t in redirect_targets(toks)) if r]
        return out
    return []


def line_count(path):
    try:
        return len(path.read_text(encoding="utf-8").splitlines())
    except (OSError, UnicodeDecodeError):
        return 0


def check_state_length(ev):
    target = "docs/whosedime/STATE.md"
    cmd = (ev.get("tool_input") or {}).get("command", "")
    if target in touched_files(ev) or (ev.get("tool_name") == "Bash" and "STATE.md" in cmd):
        n = line_count(root() / target)
        if n > STATE_MAX:
            return f"STATE.md is {n} lines (limit {STATE_MAX})"
    return None


def check_report_length(ev):
    paths = [r for r in touched_files(ev)
             if r.startswith("docs/whosedime/watch/") and r.endswith(".md")]
    if ev.get("tool_name") == "Bash":
        paths += [f"docs/whosedime/watch/{d}.md"
                  for _, d in watch_calls((ev.get("tool_input") or {}).get("command", ""))]
    for r in dict.fromkeys(paths):
        n = line_count(root() / r)
        if n > REPORT_MAX:
            return f"{r} is {n} lines (limit {REPORT_MAX})"
    return None


def french_score(text):
    """(is_french, words, french-word share, accented-word share)."""
    ws = re.findall(r"[A-Za-zÀ-ÿœŒ]+(?:['’][A-Za-zÀ-ÿ]+)?", text)
    if len(ws) < FRENCH_MIN_WORDS:
        return False, len(ws), 0.0, 0.0
    low = [w.lower() for w in ws]
    fw = sum(1 for w in low if w in FRENCH_WORDS or re.match(r"^(?:l|d|qu|n|j|c|s)['’]", w))
    acc = sum(1 for w in ws if FRENCH_ACCENTS & set(w))
    fr, ar = fw / len(ws), acc / len(ws)
    return (fr >= FRENCH_WORD_RATIO and ar >= FRENCH_ACCENT_RATIO), len(ws), fr, ar


def is_new(r):
    try:
        res = subprocess.run(["git", "-C", str(root()), "ls-files", "--error-unmatch", r],
                             capture_output=True, timeout=3)
        return res.returncode != 0
    except Exception:
        return False


def check_french(ev):
    for r in touched_files(ev):
        if not r.startswith(("whosedime/", "docs/whosedime/")) or not r.endswith(TEXT_SUFFIXES):
            continue
        if r in NOT_DELIVERABLES or not is_new(r):
            continue
        try:
            text = (root() / r).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        fr, n, wr, ar = french_score(text)
        if fr:
            return f"new file {r} reads as French ({wr:.0%} French function words, {ar:.0%} accented words)"
    return None


def session_tag(ev):
    rid = os.environ.get("CLAUDE_CODE_REMOTE_SESSION_ID", "")
    if rid:
        return "session_" + rid.split("_", 1)[-1]
    return ev.get("session_id") or "unknown"


def check_critique(ev):
    if ev.get("tool_name") != "Bash" or ev.get("hook_event_name") == "PostToolUseFailure":
        return None
    cmd = (ev.get("tool_input") or {}).get("command", "")
    if not any(git_sub(t)[0] == "commit" for t, _ in segments(cmd)):
        return None
    try:
        r = subprocess.run(["git", "-C", str(root()), "show", "--name-only", "--format=", "HEAD"],
                           capture_output=True, text=True, timeout=3)
        files = [f for f in r.stdout.splitlines() if f]
    except Exception:
        return None
    deliv = [f for f in files if f.startswith(("whosedime/", "docs/whosedime/", "tools/"))
             and f not in NOT_DELIVERABLES]
    if not deliv:
        return None
    tag = session_tag(ev).split("_", 1)[-1]
    log = root() / "docs" / "whosedime" / "critique_log.jsonl"
    try:
        if tag and tag in log.read_text(encoding="utf-8"):
            return None
    except OSError:
        pass
    return f"commit of {deliv[0]}{' and others' if len(deliv) > 1 else ''}; no critique_log line from this session yet"


# ---------------------------------------------------------------- state

def state_path(ev):
    d = pathlib.Path(os.environ.get("WHOSEDIME_GUARD_STATE")
                     or pathlib.Path(tempfile.gettempdir()) / "whosedime-guard")
    sid = re.sub(r"[^\w-]", "_", ev.get("session_id") or "unknown")
    return d / f"{sid}.json"


def load_state(ev):
    try:
        return json.loads(state_path(ev).read_text())
    except (OSError, ValueError):
        return {}


def record(ev):
    """After a call: count it, note code edits and test results."""
    state = load_state(ev)
    seq = state.get("seq", 0) + 1
    state["seq"] = seq
    changed = False
    for r in touched_files(ev):
        if r.startswith(CODE_DIRS) or r.endswith(CODE_SUFFIXES):
            state["last_code_edit"], state["last_code_file"] = seq, r
            changed = True
    if ev.get("tool_name") == "Bash":
        kinds = [k for k in (is_test_run(t) for t, _ in segments(
            (ev.get("tool_input") or {}).get("command", ""))) if k]
        if kinds:
            ok, summary = test_outcome(ev)
            state["last_test"] = dict(seq=seq, ok=ok, summary=summary)
            if ok and "full" in kinds:
                state["last_full_pass"] = seq
            changed = True
    p = state_path(ev)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state))
    return changed


def test_outcome(ev):
    if ev.get("hook_event_name") == "PostToolUseFailure":
        return False, "the command failed"
    resp = ev.get("tool_response")
    text = json.dumps(resp) if not isinstance(resp, str) else resp
    text = text.replace("\\n", "\n")
    fail = re.search(r"FAILED \([^)]*\)|\d+ failed|Error:|Traceback", text)
    ran = re.search(r"Ran (\d+) tests?", text)
    passed = re.search(r"(?m)^OK\b|OK \(|\d+ passed", text)
    if fail:
        return False, fail.group(0)
    if passed:
        return True, (ran.group(0) if ran else passed.group(0)) + " OK"
    return False, "no test result found in the output"


# ------------------------------------------------------------------ log

def summary(ev):
    tin = ev.get("tool_input") or {}
    s = tin.get("command") or tin.get("file_path") or tin.get("notebook_path") or ""
    r = rel(s) if ev.get("tool_name") in FILE_TOOLS else None
    s = r or s
    s = re.sub(r"AIza[0-9A-Za-z_\-]{30,}", "<redacted>", s)
    for k in KEYS:
        v = os.environ.get(k)
        if v and len(v) > 6:
            s = s.replace(v, "<redacted>")
    s = " ".join(s.split())
    return f"{ev.get('tool_name')}: {s[:200]}"


def log(ev, rule, action, detail):
    path = pathlib.Path(os.environ.get("WHOSEDIME_GUARD_LOG")
                        or root() / "docs" / "whosedime" / "guard_log.jsonl")
    now = dt.datetime.now(dt.timezone.utc)
    line = dict(date=now.date().isoformat(), time=now.strftime("%H:%M:%SZ"),
                session=session_tag(ev), rule=rule, action=action,
                call=summary(ev), detail=detail)
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
    except OSError:
        pass


# ------------------------------------------------------------------ main

def evaluate(ev, phase):
    """[(rule row, action, message, detail)] for one hook event."""
    found = []
    for row in RULES:
        if row["when"] != phase:
            continue
        detail = globals()[row["check"]](ev)
        if not detail:
            continue
        action = row["action"]
        if detail.startswith("WARN:"):
            action, detail = "warn", detail[5:]
        msg = (f"GUARD {action.upper()} [{row['id']}] {detail}: {row['rule']}. "
               f"Fix: {row['fix']}.")
        found.append((row, action, msg, detail))
    return found


def respond(ev, phase):
    """The hook's stdout (a JSON string) or '' for silence."""
    event = ev.get("hook_event_name") or {"pre": "PreToolUse", "post": "PostToolUse"}[phase]
    if phase == "post":
        record(ev)
        if event == "PostToolUseFailure":
            return ""
    found = evaluate(ev, phase)
    if not found:
        return ""
    for row, action, _, detail in found:
        log(ev, row["id"], action, detail)
    blocks = [m for _, a, m, _ in found if a == "block"]
    warns = [m for _, a, m, _ in found if a == "warn"]
    out = {"hookEventName": event}
    if blocks:
        out["permissionDecision"] = "deny"
        out["permissionDecisionReason"] = " ".join(blocks + warns)
    else:
        out["additionalContext"] = " ".join(warns)
    return json.dumps({"hookSpecificOutput": out})


def main(argv):
    phase = argv[1] if len(argv) > 1 else ""
    if phase == "rules":
        for r in RULES:
            print(f"{r['when']:4} {r['action']:5} {r['id']:20} {r['rule']}  [case: {r['case']}]")
        return 0
    try:
        ev = json.loads(sys.stdin.read() or "{}")
        if phase == "post-failure":
            ev.setdefault("hook_event_name", "PostToolUseFailure")
            phase = "post"
        if phase not in ("pre", "post"):
            return 0
        out = respond(ev, phase)
        if out:
            print(out)
    except Exception:
        return 0          # a guard bug never blocks work
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
