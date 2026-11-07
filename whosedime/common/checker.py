#!/usr/bin/env python3
"""Shared checker for Whose Dime deliverables (S03). Standard library only.

    python3 whosedime/common/checker.py script      SCRIPT        [--facts F] [--thresholds J]
    python3 whosedime/common/checker.py voice       SCRIPT VOICE  [--facts F]
    python3 whosedime/common/checker.py scenes      SCENES        [--facts F]
    python3 whosedime/common/checker.py publication PUBLICATION   [--facts F]
    python3 whosedime/common/checker.py all         FOLDER        [--thresholds J]
    python3 whosedime/common/checker.py fingerprint 02b_factcheck.md

--facts defaults to 02b_factcheck.md next to the checked file; `all` reads the
file names of settings.json in FOLDER (voice, scenes and publication only if
present). `scenes` reads 02_script.md next to 03_scenes.md.

Exit code: 0 no block (warnings allowed), 1 at least one BLOCK, 2 usage error.

BLOCK (decision D4 and the S03 prompt):
- a number, date or name absent from the registry, or only in a fact that is
  [TO VERIFY] or withdrawn; a [^Fnn] tag naming no verified fact;
- a quotation (two words or more in quotation marks) that is not word for
  word in the people block ("..." or an ellipsis may cut words out);
- any [TO VERIFY] tag; a malformed registry; an unsigned registry (voice), or
  one whose signature hash is missing or no longer matches its content (voice:
  "registry changed since it was signed");
- a title longer than settings.json allows; a phrase of forbidden_phrases.txt;
- a voice version that differs from the script beyond allowed rewrites
  (numbers, $ and % spelled out, respellings of lexicon.tsv);
- (S05) a title or thumbnail line holding a number without the [^Fnn] tag of a
  fact that holds that number (audit C2);
- (S05) scenes: a spoken text that is not the script word for word; a chart
  scene citing no verified fact id, or showing a number its cited facts do not
  hold; a bad table, type, visual name or motion; a card with spoken text; an
  image or clip without its prompt; a real person of the people block named in
  a prompt; on-screen numbers as for facts. The scene mix of settings.json
  (counts, words per scene, motions, on-screen share) only warns.
WARN: every rule of style_thresholds.json (metrics from measure.py, imported,
not copied), on the whole script, as the thresholds were calibrated. Metrics
counted from the first word (first person, first turn, numbers in the first
60 words) thus measure the cold open; cutting the cold open out first would
make "no person found" read as the cold open's length and pass. Also warned:
an ending without a next-video phrase; digits or symbols left in the voice;
capitalised sentence-first words that may be unregistered names (one line).

Signature: `Signed: Franco, YYYY-MM-DD, sha256:<12 hex>`. The hash is taken over
the registry text without its `## Signature` section (and without any
`Signed:` line), each line stripped on the right; `fingerprint` prints it.

Names are capitalised words inside a sentence. A sentence's first word blocks
only if it is a given name of measure.py. Any other capitalised first word that
is in no registry line, not in the not-names lists, not a number word, and
never written in lower case elsewhere in the file is collected into ONE warning
line (a capitalised common word cannot be told from a name there, so it cannot
block). Titles and thumbnail texts are in title case, so only their numbers
are checked, not their names.
"""
import argparse
import difflib
import hashlib
import importlib.util
import json
import re
import sys
import unicodedata
from decimal import Decimal, InvalidOperation
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SETTINGS = json.loads((HERE / "settings.json").read_text(encoding="utf-8"))

TAG_RE = re.compile(r"\[\^([^\]\s]+)\]")
TO_VERIFY_RE = re.compile(r"\[\s*TO\s+VERIFY", re.I)
TO_VERIFY_TAG_RE = re.compile(r"\[\s*TO\s+VERIFY[^\]]*\]", re.I)
URL_RE = re.compile(r"https?://\S+|www\.\S+")
TIME_RE = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b")
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
HEADING_RE = re.compile(r"^\s*#{1,6}\s+(.*?)\s*#*\s*$")
LIST_RE = re.compile(r"^\s*(?:\d+[.)]|[-*+])\s+")
FOOTDEF_RE = re.compile(r"^\[\^[^\]]+\]:")
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
FACT_ID_RE = re.compile(r"^F\d{2,}$")
SIGNED_RE = re.compile(r"^\s*signed:", re.I)
SIGN_HASH_RE = re.compile(r"sha256:[0-9a-f]+", re.I)
ELLIPSIS_RE = re.compile(r"\.\.\.|…")
CODE_RE = re.compile(r"(?<![\w$.])(?!\d+(?:st|nd|rd|th|s)\b)(?=[\w-]*[A-Za-z])(?=[\w-]*\d)[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*")
STATUSES = {"verified": "verified", "[to verify]": "to_verify", "to verify": "to_verify",
            "withdrawn": "withdrawn"}


# ------------------------------------------------------------------ loading
def load_module(path):
    spec = importlib.util.spec_from_file_location(Path(path).stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_list(name):
    """Non-empty, non-comment lines of a list file in this folder."""
    path = HERE / SETTINGS["lists"][name]
    return [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")]


def load_thresholds(path=None):
    path = Path(path) if path else ROOT / SETTINGS["style_thresholds"]
    data = json.loads(path.read_text(encoding="utf-8"))
    return data, load_module(ROOT / data["measure"])


# ------------------------------------------------------------------ report
class Report:
    def __init__(self, target, path):
        self.target, self.path, self.items, self.summary = target, Path(path), [], ""

    def add(self, level, code, msg, line=None):
        where = f"line {line}: " if line else ""
        self.items.append((level, code, where + msg))

    def block(self, code, msg, line=None):
        self.add("BLOCK", code, msg, line)

    def warn(self, code, msg, line=None):
        self.add("WARN", code, msg, line)

    @property
    def blocks(self):
        return [i for i in self.items if i[0] == "BLOCK"]

    @property
    def warnings(self):
        return [i for i in self.items if i[0] == "WARN"]

    def codes(self, level=None):
        return [c for lv, c, _ in self.items if level in (None, lv)]

    def render(self):
        out = [f"== {self.target}: {self.path}"]
        out += [f"{lv:<5} {code:<11} {msg}" for lv, code, msg in self.items]
        out.append(f"-- {self.summary}{len(self.blocks)} block(s), {len(self.warnings)} warning(s).")
        return "\n".join(out)


# ------------------------------------------------------------------ text helpers
def norm(text):
    return unicodedata.normalize("NFKC", text).replace("’", "'").replace("‘", "'")


def text_lines(raw, skip_sections=()):
    """[(line number, section, text)] of a Markdown file, without comments,
    headings, footnote definitions, list markers or emphasis."""
    raw = COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), norm(raw))
    out, section, in_footnote = [], "", False
    for n, line in enumerate(raw.splitlines(), 1):
        h = HEADING_RE.match(line)
        if h:
            section, in_footnote = h.group(1).strip().lower(), False
            continue
        if FOOTDEF_RE.match(line):
            in_footnote = True
            continue
        if in_footnote and (line.startswith((" ", "\t")) or not line.strip()):
            continue
        in_footnote = False
        if any(section.startswith(s) for s in skip_sections) or not line.strip():
            continue
        line = LIST_RE.sub("", line.lstrip("> ").rstrip())
        line = re.sub(r"[*`]|(?<!\w)_|_(?!\w)", "", line)
        out.append((n, section, line))
    return out


def spoken_text(lines):
    return "\n".join(TAG_RE.sub("", t) for _, _, t in lines)


def phrase_regex(phrase):
    if phrase.startswith("re:"):
        return re.compile(phrase[3:], re.I)
    return re.compile(r"(?<![\w'])" + re.escape(phrase.lower()).replace(r"\ ", r"\s+")
                      + r"(?![\w'])", re.I)


# ------------------------------------------------------------------ numbers
UNITS = dict(zip("zero one two three four five six seven eight nine ten eleven twelve thirteen "
                 "fourteen fifteen sixteen seventeen eighteen nineteen".split(), range(20)))
TENS = dict(zip("twenty thirty forty fifty sixty seventy eighty ninety".split(), range(20, 100, 10)))
ORDS = dict(zip("first second third fourth fifth sixth seventh eighth ninth tenth eleventh twelfth "
                "thirteenth fourteenth fifteenth sixteenth seventeenth eighteenth nineteenth".split(),
                range(1, 20)))
ORDS.update(zip("twentieth thirtieth fortieth fiftieth sixtieth seventieth eightieth ninetieth".split(),
                range(20, 100, 10)))
PLURAL_TENS = dict(zip("twenties thirties forties fifties sixties seventies eighties nineties".split(),
                       range(20, 100, 10)))
SCALES = {"million", "billion", "trillion"}
NUMBER_WORDS = set(UNITS) | set(TENS) | set(ORDS) | set(PLURAL_TENS) | SCALES | {"hundred", "thousand"}
CURRENCY = {"$": "dollars", "€": "euros", "£": "pounds"}
SAME_WORD = {"dollar": "dollars", "euro": "euros", "pound": "pounds", "percentage": "percent"}
TOKEN_RE = re.compile(r"\d+(?:,\d{3})*(?:\.\d+)?[a-z]*|[a-z]+(?:'[a-z]+)*")


def _dec(s):
    try:
        d = Decimal(s)
    except InvalidOperation:
        return s
    return format(d.normalize(), "f")


def _below100(w, i):
    if i >= len(w):
        return None
    t = w[i]
    if t in TENS:
        v = TENS[t]
        if i + 1 < len(w) and 1 <= UNITS.get(w[i + 1], 0) <= 9:
            return v + UNITS[w[i + 1]], i + 2, False
        if i + 1 < len(w) and 1 <= ORDS.get(w[i + 1], 0) <= 9:
            return v + ORDS[w[i + 1]], i + 2, True
        return v, i + 1, False
    if t in UNITS:
        return UNITS[t], i + 1, False
    if t in ORDS:
        return ORDS[t], i + 1, True
    if t in PLURAL_TENS:
        return PLURAL_TENS[t], i + 1, False
    return None


def _below1000(w, i):
    if w[i] == "a" and i + 1 < len(w) and w[i + 1] in ("hundred", "thousand"):
        v, j, ordinal, simple = 1, i + 1, False, False
    else:
        r = _below100(w, i)
        if not r:
            return None
        (v, j, ordinal), simple = r, True
    if j < len(w) and w[j] == "hundred" and not ordinal:
        v, j, simple = v * 100, j + 1, False
        k = j + 1 if w[j:j + 1] == ["and"] and _below100(w, j + 1) else j
        r = _below100(w, k)
        if r:
            v, j, ordinal = v + r[0], r[1], r[2]
    return v, j, ordinal, simple


def _cardinal(w, i):
    """Parse spelled-out number words at w[i]: (digits, next index, ordinal, spelled_small)."""
    r = _below1000(w, i)
    if not r:
        return None
    v, j, ordinal, simple = r
    if j < len(w) and w[j] == "thousand" and not ordinal:
        v, j, simple = v * 1000, j + 1, False
        k = j + 1 if w[j:j + 1] == ["and"] and _below1000(w, j + 1) else j
        r = _below1000(w, k) if k < len(w) else None
        if r:
            v, j, ordinal = v + r[0], r[1], r[2]
    dec = ""
    if j < len(w) and w[j] == "point" and not ordinal:
        k, digits = j + 1, ""
        while k < len(w) and (UNITS.get(w[k], 99) <= 9 or w[k] == "oh"):
            digits += str(UNITS.get(w[k], 0))
            k += 1
        if digits:
            dec, j, simple = "." + digits, k, False
    if simple and not ordinal and 10 <= v <= 99:      # years said in pairs: "twenty oh eight"
        if w[j:j + 1] == ["oh"] and j + 1 < len(w) and 1 <= UNITS.get(w[j + 1], 0) <= 9:
            v, j, simple = v * 100 + UNITS[w[j + 1]], j + 2, False
        else:
            r = _below100(w, j)
            if r and r[0] >= 10:
                v, j, ordinal, simple = v * 100 + r[0], r[1], r[2], False
    spelled_small = simple and v <= 10 and j - i == 1
    return _dec(f"{v}{dec}"), j, ordinal, spelled_small


def canon(text):
    """Canonical tokens of a text: [(token, kind)], kind 'word', 'num' (digits
    written), 'spelled' (number said in words), 'small' (one to ten, or an
    ordinal word: not a fact). Both sides of every comparison use this."""
    t = norm(TAG_RE.sub(" ", text))
    t = re.sub(r"([$€£])\s?(\d+(?:,\d{3})*(?:\.\d+)?)(\s?(?:hundred|thousand|million|billion|trillion)\b)?",
               lambda m: f" {m[2]}{m[3] or ''} {CURRENCY[m[1]]} ", t, flags=re.I)
    t = t.replace("%", " percent ").replace("&", " and ").lower()
    t = re.sub(r"per cent\b", "percent", t)
    t = re.sub(r"[-–—/]", " ", t)
    w = []
    for tok in TOKEN_RE.findall(t):
        if tok[0].isdigit():
            m = re.match(r"([\d,.]+)([a-z]*)$", tok)
            tok = m[1].replace(",", "") if m[2] in ("", "st", "nd", "rd", "th", "s") else tok
        w.append(SAME_WORD.get(tok, tok))
    out, i = [], 0
    while i < len(w):
        tok = w[i]
        if tok[0].isdigit():
            kind, i = "num", i + 1
            if i < len(w) and w[i] in ("hundred", "thousand") and re.fullmatch(r"[\d.]+", tok):
                tok = _dec(str(Decimal(tok) * (100 if w[i] == "hundred" else 1000)))
                i += 1
            out.append((tok, kind))
            continue
        if tok == "a" and i + 1 < len(w) and w[i + 1] in SCALES:     # "a million" = "one million"
            out.append(("1", "small"))
            i += 1
            continue
        r = _cardinal(w, i) if (tok in UNITS or tok in TENS or tok in ORDS or tok in PLURAL_TENS
                                or tok == "a") else None
        if r and r[1] > i and not (tok == "a" and r[0] == "1" and r[1] == i + 1):
            digits, i, ordinal, small = r
            out.append((digits, "small" if (small or (ordinal and int(Decimal(digits)) <= 31))
                        else "spelled"))
        else:
            out.append((tok, "word"))
            i += 1
    return out


def number_keys(tokens):
    """[(key, kind)] of the numbers in canonical tokens; a scale word joins the key."""
    keys = []
    for k, (tok, kind) in enumerate(tokens):
        if kind == "word":
            continue
        nxt = tokens[k + 1][0] if k + 1 < len(tokens) else ""
        keys.append((f"{tok} {nxt}" if nxt in SCALES else tok, kind))
    return keys


# ------------------------------------------------------------------ registry
class Registry:
    def __init__(self, path):
        self.path = Path(path)
        self.facts, self.people, self.errors = {}, [], []
        self.signed = self.signed_hash = None
        raw = norm(self.path.read_text(encoding="utf-8"))
        self.fingerprint = fingerprint(raw)
        self._parse(raw)
        self.numbers, self.names = {}, {}       # key -> {fact ids}; name token -> {ids}
        for f in self.facts.values():
            for key, _ in number_keys(canon(f["text"])):
                self.numbers.setdefault(key, set()).add(f["id"])
            for tok in name_tokens(f["text"], all_words=True):
                self.names.setdefault(tok, set()).add(f["id"])
        for p in self.people:
            for tok in name_tokens(p["name"], all_words=True):
                self.names.setdefault(tok, set()).add(p["ref"])

    def status(self, ref):
        if ref in self.facts:
            return self.facts[ref]["status"]
        return next((p["status"] for p in self.people if p["ref"] == ref), None)

    def people_names(self):
        """Names of real people (rows whose role is not 'organisation'), for measure()."""
        return sorted({p["name"] for p in self.people if p["role"].strip().lower() != "organisation"})

    def _parse(self, raw):
        section, header = "", None
        tables = {"facts": [], "people": []}
        for n, line in enumerate(raw.splitlines(), 1):
            h = HEADING_RE.match(line)
            if h and line.lstrip().startswith("##"):
                section, header = h.group(1).strip().lower(), None
                continue
            s = re.match(r"^\s*signed:\s*(.*)$", line, re.I)
            if s:
                value = s.group(1).strip()
                h = SIGN_HASH_RE.search(value)
                rest = SIGN_HASH_RE.sub("", value)
                if DATE_RE.search(rest) and re.search(r"[A-Za-z]", DATE_RE.sub("", rest)):
                    self.signed, self.signed_hash = value, h.group(0).lower() if h else None
                continue
            if not line.strip().startswith("|"):
                continue
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                continue
            kind = "facts" if section.startswith("facts") else "people" if section.startswith("people") else None
            if kind is None:
                continue
            if header is None:
                header = [c.lower() for c in cells]
                continue
            tables[kind].append((n, dict(zip(header, cells))))
        need = {"facts": ["id", "text", "source", "read", "status"],
                "people": ["name", "role", "date", "decision", "quote", "source", "status"]}
        for kind, rows in tables.items():
            if rows and any(col not in rows[0][1] for col in need[kind]):
                self.errors.append((rows[0][0], f"{kind} table needs the columns {', '.join(need[kind])}"))
                tables[kind] = []
        if not tables["facts"]:
            self.errors.append((None, "no '## Facts' table found"))
        for n, row in tables["facts"]:
            fid = row["id"]
            status = STATUSES.get(row["status"].lower())
            if not FACT_ID_RE.match(fid):
                self.errors.append((n, f"fact id '{fid}' is not F01, F02..."))
            elif fid in self.facts:
                self.errors.append((n, f"fact id {fid} used twice"))
            if status is None:
                self.errors.append((n, f"{fid}: status '{row['status']}' is not verified, [TO VERIFY] or withdrawn"))
            if not row["text"] or not row["source"] or row["source"] in ("-", "—"):
                self.errors.append((n, f"{fid}: a fact needs its text and its source"))
            if status == "verified" and not DATE_RE.search(row["read"]):
                self.errors.append((n, f"{fid}: verified, but no date read (YYYY-MM-DD)"))
            self.facts.setdefault(fid, dict(row, id=fid, status=status or "to_verify", line=n))
        for k, (n, row) in enumerate(tables["people"], 1):
            status = STATUSES.get(row["status"].lower())
            quote = row["quote"].strip().strip('"“”')
            if not row["name"]:
                self.errors.append((n, "people row without a name"))
            if status is None:
                self.errors.append((n, f"{row['name']}: status '{row['status']}' is not verified, [TO VERIFY] or withdrawn"))
            if quote not in ("", "-", "—") and (not row["source"] or row["source"] in ("-", "—")):
                self.errors.append((n, f"{row['name']}: a quote needs its source"))
            self.people.append(dict(row, quote="" if quote in ("-", "—") else quote,
                                    status=status or "to_verify", line=n, ref=f"people line {n}"))


def fingerprint(raw):
    """sha256:<12 hex> of a registry's text without its '## Signature' section
    and without any 'Signed:' line; lines stripped on the right, so trailing
    spaces and line endings do not count."""
    keep, in_sig = [], False
    for line in norm(raw).splitlines():
        h = HEADING_RE.match(line)
        if h and line.lstrip().startswith("##"):
            in_sig = h.group(1).strip().lower().startswith("signature")
        if in_sig or SIGNED_RE.match(line):
            continue
        keep.append(line.rstrip())
    text = "\n".join(keep).strip("\n") + "\n"
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:SETTINGS["signature_hash_chars"]]


def name_tokens(text, all_words=False):
    """Lower-case name tokens of a text: capitalised words (or every word if
    all_words), possessive stripped, split on hyphens unless they hold digits."""
    out = []
    for raw in text.split():
        core = raw.strip(".,;:!?\"“”«»()[]{}*_#")
        core = re.sub(r"'(?:s|m|re|ve|ll|d)$", "", core)
        if not core or not re.search(r"[A-Za-z]", core):
            continue
        parts = [core] if re.search(r"\d", core) else re.split(r"[-/]", core)
        for p in parts:
            p = p.strip(".'")
            if p and (all_words or p[0].isupper() or re.search(r"\d", p)):
                out.append(p.lower())
    return out


# ------------------------------------------------------------------ fact checks
def _words(text):
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)?", norm(text).lower())


def quote_ok(quote, registry):
    """True if every part of the quote (cut at ellipses) sits word for word,
    in order, inside one verified quotation of the people block."""
    parts = [_words(p) for p in ELLIPSIS_RE.split(quote)]
    parts = [p for p in parts if p]
    for person in registry.people:
        if person["status"] != "verified" or not person["quote"]:
            continue
        hay, pos = _words(ELLIPSIS_RE.sub(" ", person["quote"])), 0
        for part in parts:
            k = next((i for i in range(pos, len(hay) - len(part) + 1) if hay[i:i + len(part)] == part), None)
            if k is None:
                break
            pos = k + len(part)
        else:
            return True
    return False


def check_facts(lines, registry, report, measure, names=True, title_case=(), first_words_warn=True):
    """Numbers, dates, names, quotations and [^F..] tags of text lines against the registry."""
    not_names = set(read_list("not_names")) | measure.NOT_NAMES | measure.TITLES
    lower_words = {w for _, _, t in lines for w in re.findall(r"(?<![\w'])[a-z][a-z'-]*", norm(t))}
    first_words = {}                           # sentence-first words that may be names -> first line
    for n, section, text in lines:
        for ref in TAG_RE.findall(text):
            st = registry.status(ref)
            if st is None:
                report.block("source-tag", f"[^{ref}] is not an id of the registry", n)
            elif st != "verified":
                report.block("source-tag", f"[^{ref}] points to a fact that is {st.replace('_', ' ')}", n)
        text = TIME_RE.sub(" ", URL_RE.sub(" ", TAG_RE.sub("", TO_VERIFY_TAG_RE.sub(" ", text))))

        def unquote(m):
            inner = next(g for g in m.groups() if g is not None)
            if len(measure.words(inner)) < SETTINGS["quote_min_words"]:
                return m.group(0)
            if not quote_ok(inner, registry):
                report.block("quote", f"not word for word in the people block: \"{inner.strip()[:90]}\"", n)
            return " QUOTE. " if re.search(r"[.!?]\W*$", inner) else " QUOTE "
        text = measure.QUOTE_RE.sub(unquote, text)

        no_codes = CODE_RE.sub(" ", text)          # "10-K", "S-1", "Q3" are names, not numbers
        for key, kind in number_keys(canon(no_codes)):
            if kind == "small":
                continue
            ids = registry.numbers.get(key)
            if not ids:
                report.block("number", f"'{key}' is in no fact of the registry", n)
            elif not any(registry.status(i) == "verified" for i in ids):
                report.block("number", f"'{key}' is only in {', '.join(sorted(ids))}, not verified", n)

        if not names or any(section.startswith(s) for s in title_case):
            continue
        toks = text.split()
        for i, raw in enumerate(toks):
            start = i == 0 or re.search(r"[.!?][\"”')\]]*$", toks[i - 1])
            for tok in name_tokens(raw):
                if tok == "quote" or tok in not_names or re.fullmatch(r"[\d.,]+[a-z]{0,2}", tok):
                    continue
                if start and tok not in measure.GIVEN_NAMES:
                    if (tok not in registry.names and tok not in lower_words and tok not in NUMBER_WORDS
                            and tok[0].isalpha()):
                        first_words.setdefault(raw.strip(".,;:!?\"“”()[]*_'"), n)
                    continue
                ids = registry.names.get(tok)
                if not ids:
                    report.block("name", f"'{raw.strip('.,;:!?()')}' is a name in no line of the registry", n)
                elif not any(registry.status(i) == "verified" for i in ids):
                    report.block("name", f"'{tok}' is only in {', '.join(sorted(ids))}, not verified", n)
    if first_words and first_words_warn:
        report.warn("name-first", "sentence-first word(s) in no registry line and never in lower case; "
                    "register any that is a name: " + ", ".join(f"{w} (line {n})" for w, n in first_words.items()))


def check_common(raw, lines, report, registry, measure, title_case=(), first_words_warn=True):
    """Blocks shared by every target: registry errors, [TO VERIFY], forbidden phrases, facts."""
    for line, msg in registry.errors:
        report.block("registry", f"{registry.path.name}{f' line {line}' if line else ''}: {msg}")
    for n, line in enumerate(norm(raw).splitlines(), 1):
        if TO_VERIFY_RE.search(line):
            report.block("to-verify", f"[TO VERIFY] tag: {line.strip()[:90]}", n)
    patterns = [(p, phrase_regex(p)) for p in read_list("forbidden")]
    for n, _, text in lines:
        for phrase, rx in patterns:
            if rx.search(text):
                report.block("forbidden", f"forbidden phrase '{phrase}': {text.strip()[:90]}", n)
    check_facts(lines, registry, report, measure, title_case=title_case, first_words_warn=first_words_warn)


# ------------------------------------------------------------------ targets
def check_script(path, facts=None, thresholds=None, style=True):
    path = Path(path)
    registry = Registry(facts or path.parent / SETTINGS["files"]["facts"])
    rules, measure = load_thresholds(thresholds)
    raw = path.read_text(encoding="utf-8")
    lines = text_lines(raw, SETTINGS["unspoken_sections"])
    report = Report("script", path)
    check_common(raw, lines, report, registry, measure)
    text = spoken_text(lines)
    if not style:
        return report
    m = measure.measure(text, people=registry.people_names())
    for rule in rules["rules"]:
        value = m.get(rule["metric"])
        if value is None:
            continue
        low, high = rule.get("min"), rule.get("max")
        if (low is not None and value < low) or (high is not None and value > high):
            bound = " and ".join(b for b in (low is not None and f">= {low}", high is not None and f"<= {high}") if b)
            (report.block if rule["level"] == "block" else report.warn)(
                rule["id"], f"{rule['metric']} = {value}, rule {bound}")
    tail = " ".join(text.split()[-SETTINGS["ending_words"]:])
    if not any(phrase_regex(p).search(norm(tail)) for p in read_list("next_video")):
        report.warn("ending", f"the last {SETTINGS['ending_words']} words announce no next video "
                    f"(phrases in {SETTINGS['lists']['next_video']})")
    report.summary = f"{m['words']:,} words. "
    return report


def lexicon():
    pairs = []
    for line in (HERE / SETTINGS["lists"]["lexicon"]).read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#") and "\t" in line:
            written, spoken = line.split("\t", 1)
            pairs.append(([t for t, _ in canon(written)], [t for t, _ in canon(spoken)]))
    return sorted(pairs, key=lambda p: -len(p[0]))


def respell(tokens, lex):
    out, i = [], 0
    while i < len(tokens):
        for written, spoken in lex:
            if written and tokens[i:i + len(written)] == written:
                out += spoken
                i += len(written)
                break
        else:
            out.append(tokens[i])
            i += 1
    return out


def check_voice(script, voice, facts=None):
    script, voice = Path(script), Path(voice)
    registry = Registry(facts or script.parent / SETTINGS["files"]["facts"])
    _, measure = load_thresholds()
    report = Report("voice", voice)
    if not registry.signed:
        report.block("signature", f"{registry.path.name} is not signed: Franco signs the fact check before the voice")
    elif registry.signed_hash != registry.fingerprint:
        why = (f"signed {registry.signed_hash}, content is now {registry.fingerprint}" if registry.signed_hash
               else "the signature has no sha256 hash")
        report.block("signature", f"{registry.path.name}: registry changed since it was signed ({why}); "
                     f"Franco re-reads it and signs again with `checker.py fingerprint`")
    s_raw, v_raw = script.read_text(encoding="utf-8"), voice.read_text(encoding="utf-8")
    s_lines = text_lines(s_raw, SETTINGS["unspoken_sections"])
    check_common(s_raw, s_lines, report, registry, measure, first_words_warn=False)   # the script report has it
    for n, line in enumerate(norm(v_raw).splitlines(), 1):
        if TO_VERIFY_RE.search(line):
            report.block("to-verify", f"[TO VERIFY] tag in the voice version: {line.strip()[:90]}", n)
        elif re.search(r"\d|[%$€£&/#*_<>=+\[\]()]", line):
            report.warn("voice-text", f"digit or symbol left (spell it out): {line.strip()[:90]}", n)
    s_tok = [(t, n) for n, _, text in s_lines for t, _ in canon(text)]
    v_tok = [(t, n) for n, line in enumerate(norm(v_raw).splitlines(), 1) for t, _ in canon(line)]
    s, v, lex = [t for t, _ in s_tok], [t for t, _ in v_tok], lexicon()
    drift = 0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, s, v, autojunk=False).get_opcodes():
        if op == "equal" or respell(s[i1:i2], lex) == v[j1:j2]:
            continue
        drift += 1
        s_line = s_tok[min(i1, len(s_tok) - 1)][1] if s_tok else 0
        v_line = v_tok[min(j1, len(v_tok) - 1)][1] if v_tok else 0
        report.block("voice-drift", f"script line {s_line} \"{' '.join(s[max(0, i1 - 4):i2 + 4])}\" "
                     f"became voice line {v_line} \"{' '.join(v[max(0, j1 - 4):j2 + 4])}\"")
    report.summary = f"{len(v):,} words, {drift} drift(s) from the script. "
    return report


def check_publication(path, facts=None):
    path = Path(path)
    registry = Registry(facts or path.parent / SETTINGS["files"]["facts"])
    _, measure = load_thresholds()
    raw = path.read_text(encoding="utf-8")
    lines = text_lines(raw, SETTINGS["unspoken_sections"])
    report = Report("publication", path)
    check_common(raw, lines, report, registry, measure, title_case=SETTINGS["title_case_sections"])
    check_titles_sourced(lines, registry, report)
    titles =[(n, TAG_RE.sub("", t).strip().strip('"“”')) for n, sec, t in lines
              if any(sec.startswith(s) for s in SETTINGS["title_sections"])]
    if not titles:
        report.block("title", "no title found (list items under '## Titles')")
    for n, title in titles:
        if len(title) > SETTINGS["title_max_chars"]:
            report.block("title", f"{len(title)} characters (max {SETTINGS['title_max_chars']}): {title}", n)
    report.summary = f"{len(titles)} title(s). "
    return report


def fact_numbers(text):
    """Number keys of a text (words one to ten left out), cleaned as check_facts cleans it."""
    text = TIME_RE.sub(" ", URL_RE.sub(" ", TAG_RE.sub("", TO_VERIFY_TAG_RE.sub(" ", text))))
    return [key for key, kind in number_keys(canon(CODE_RE.sub(" ", text))) if kind != "small"]


def check_sourced(text, ids, registry, report, code, n, what):
    """Every number of `text` must be in one of the facts `ids` (S05, audit C2)."""
    keys = fact_numbers(text)
    if keys and not ids:
        report.block(code, f"{what} holds a number but cites no fact id: {text.strip()[:90]}", n)
        return
    for key in keys:
        if ids and not registry.numbers.get(key, set()) & set(ids):
            report.block(code, f"'{key}' is not in the fact(s) it cites ({', '.join(ids)}): {text.strip()[:90]}", n)


def check_titles_sourced(lines, registry, report):
    """A title or thumbnail text holding a number cites, as [^Fnn], the fact that holds it."""
    for n, sec, text in lines:
        if any(sec.startswith(s) for s in SETTINGS["sourced_sections"]):
            check_sourced(text, TAG_RE.findall(text), registry, report, "title-source", n, "this line")


def _cells(line):
    return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]


def scene_table(raw):
    """(rows, error): rows are (line number, {column: cell}) of the first table whose
    header holds the columns of settings.json (scenes.columns)."""
    cols = SETTINGS["scenes"]["columns"]
    rows, header = [], None
    for n, line in enumerate(raw.splitlines(), 1):
        if not line.strip().startswith("|"):
            if header and rows:
                break
            continue
        cells = _cells(line)
        if header is None:
            if [c.lower() for c in cells] == cols:
                header = cols
            continue
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        if len(cells) != len(cols):
            return rows, (n, f"{len(cells)} columns, the table has {len(cols)}: {' | '.join(cols)}")
        rows.append((n, dict(zip(cols, cells))))
    if header is None:
        return [], (None, f"no scene table (header | {' | '.join(cols)} |)")
    return rows, None


def scene_prompts(raw):
    """{'scene': {n: (line, text)}, 'anim': {...}}: the quoted ('> ') lines after each
    **scene_NNN** or **anim_NNN** label."""
    out, cur = {"scene": {}, "anim": {}}, None
    for n, line in enumerate(raw.splitlines(), 1):
        m = re.match(r"^\s*\*\*(scene|anim)_(\d{3})\*\*", line)
        if m:
            cur = (m.group(1), int(m.group(2)))
            out[cur[0]][cur[1]] = (n, "")
        elif cur and line.lstrip().startswith(">"):
            ln, text = out[cur[0]][cur[1]]
            out[cur[0]][cur[1]] = (ln, (text + " " + line.lstrip()[1:].strip()).strip())
        elif cur and line.strip() and out[cur[0]][cur[1]][1]:
            cur = None
    return out


def empty(cell):
    return cell.strip() in ("", "-", "—")


def check_scenes(path, script=None, facts=None):
    """03_scenes.md (S05): table, spoken text = script word for word, a verified fact id on
    every chart (its numbers in that fact), card and file names, one prompt per image or
    clip, no real person named in a prompt (block); the scene mix (warn)."""
    path = Path(path)
    cfg = SETTINGS["scenes"]
    registry = Registry(facts or path.parent / SETTINGS["files"]["facts"])
    _, measure = load_thresholds()
    raw = norm(path.read_text(encoding="utf-8"))
    report = Report("scenes", path)
    rows, error = scene_table(raw)
    if error:
        report.block("scene-table", error[1], error[0])
    if not rows:
        report.summary = "0 scenes. "
        return report
    prompts = scene_prompts(raw)
    counts, spoken, on_screen_lines, n_on_screen = {}, [], [], 0
    long_short, motions_run, last_motion, run, last_video = [], [], None, 0, None
    for k, (ln, row) in enumerate(rows, 1):
        typ, num = row["type"].lower(), row["n"]
        counts[typ] = counts.get(typ, 0) + 1
        if not num.isdigit() or int(num) != k:
            report.block("scene-number", f"scene '{num}' where {k} was expected", ln)
        n = k
        if typ not in cfg["visuals"]:
            report.block("scene-type", f"scene {n}: type '{typ}' is not {', '.join(cfg['visuals'])}", ln)
            continue
        want = cfg["visuals"][typ].format(n=n)
        if (row["visual"] != want) and not (empty(want) and empty(row["visual"])):
            report.block("scene-visual", f"scene {n}: visual '{row['visual']}', expected {want}", ln)
        if typ in cfg["cards"]:
            if not empty(row["spoken text"]):
                report.block("scene-card", f"scene {n}: a {typ} card is not spoken (spoken text '—')", ln)
            if empty(row["on-screen text"]):
                report.block("scene-card", f"scene {n}: a {typ} card needs its on-screen text", ln)
        else:
            words = _words(TAG_RE.sub("", row["spoken text"]))
            spoken += [(w, n) for w in words]
            low, high = cfg["words_per_scene"]
            if not low <= len(words) <= high:
                long_short.append(f"{n} ({len(words)})")
            if not empty(row["on-screen text"]):
                n_on_screen += 1
        if not empty(row["on-screen text"]):
            on_screen_lines.append((ln, "on-screen", row["on-screen text"]))
        if typ == "image":
            if row["motion"] not in cfg["motions"]:
                report.block("scene-motion", f"scene {n}: motion '{row['motion']}' is not {', '.join(cfg['motions'])}", ln)
            run = run + 1 if row["motion"] == last_motion else 1
            last_motion = row["motion"]
            if run == cfg["same_motion_max"] + 1:
                motions_run.append(str(n))
        elif not empty(row["motion"]):
            report.block("scene-motion", f"scene {n}: a {typ} scene has no camera motion ('—')", ln)
        if typ == "chart":
            ids = re.findall(r"\bF\d{2,}\b", row["chart"])
            if not ids:
                report.block("chart-source", f"scene {n}: a chart cites no fact id of the registry (e.g. 'F07 · compare · ...')", ln)
            for i in ids:
                st = registry.status(i)
                if st != "verified":
                    report.block("chart-source", f"scene {n}: {i} is {'not an id of the registry' if st is None else st.replace('_', ' ')}", ln)
            check_sourced(re.sub(r"\bF\d{2,}\b", " ", row["chart"]), ids, registry, report, "chart-source", ln, f"scene {n}'s chart")
            parts = [p.strip().lower() for p in re.split(r"[·|]", row["chart"])]
            if len(parts) < 3 or parts[1] not in cfg["chart_kinds"]:
                report.warn("chart-kind", f"scene {n}: chart is not 'Fnn · <kind> · <what it shows>' with a kind of "
                            f"{', '.join(cfg['chart_kinds'])}: {row['chart'][:60]}", ln)
        elif not empty(row["chart"]):
            report.warn("chart-kind", f"scene {n}: a {typ} scene with a chart cell", ln)
        if typ in ("image", "video") and n not in prompts["scene"]:
            report.block("prompt", f"scene {n}: no image prompt **scene_{n:03d}**", ln)
        if typ == "video":
            if n not in prompts["anim"]:
                report.block("prompt", f"scene {n}: no clip prompt **anim_{n:03d}**", ln)
            if last_video == k - 1:
                report.warn("scene-mix", f"scenes {k - 1} and {n}: two clips in a row", ln)
            last_video = k
        elif typ in ("chart",) + tuple(cfg["cards"]) and n in prompts["scene"]:
            report.warn("prompt", f"scene {n}: a {typ} scene has an image prompt (not used)", ln)
    types = {int(r["n"]): r["type"].lower() for _, r in rows if r["n"].isdigit()}
    for n, (ln, _) in prompts["anim"].items():
        if types.get(n) != "video":
            report.block("prompt", f"**anim_{n:03d}** is for scene {n}, which is not a video scene", ln)
    persons = [p["name"] for p in registry.people if p["role"].strip().lower() != "organisation" and p["name"]]
    for kind in ("scene", "anim"):
        for n, (ln, text) in sorted(prompts[kind].items()):
            for name in persons:
                last = name.split()[-1]
                inside = [m for m in re.finditer(rf"\b{re.escape(last)}\b", text)      # capitalised, not sentence-first
                          if not re.search(r"(?:^|[.!?]\s+)$", text[:m.start()])]
                if re.search(re.escape(name), text, re.I) or inside:
                    report.block("prompt-person", f"**{kind}_{n:03d}** names {name}: a real person is never named in an image prompt", ln)
            if re.search(r"\b(?:text|letters|words|caption|sign|label)s? (?:reading|saying|that says|with the words)", text, re.I):
                report.warn("prompt-text", f"**{kind}_{n:03d}** seems to ask for text in the image", ln)

    script = Path(script) if script else path.parent / SETTINGS["files"]["script"]
    s_words = _words(spoken_text(text_lines(norm(script.read_text(encoding="utf-8")), SETTINGS["unspoken_sections"])))
    c_words = [w for w, _ in spoken]
    if s_words != c_words:
        i = next((k for k, (a, b) in enumerate(zip(s_words, c_words)) if a != b), min(len(s_words), len(c_words)))
        where = spoken[i][1] if i < len(spoken) else (spoken[-1][1] if spoken else 0)
        report.block("scene-text", f"the spoken text is not {script.name} word for word: from scene {where}, "
                     f"script \"{' '.join(s_words[max(0, i - 3):i + 6])}\", scenes \"{' '.join(c_words[max(0, i - 3):i + 6])}\"")
    check_common(raw, on_screen_lines, report, registry, measure, title_case=("on-screen",), first_words_warn=False)

    total, n_spoken = len(rows), sum(v for t, v in counts.items() if t not in cfg["cards"])
    for key, (low, high) in cfg["counts"].items():
        value = total if key == "total" else counts.get(key, 0)
        if not low <= value <= high:
            report.warn("scene-mix", f"{value} {'scenes' if key == 'total' else key + ' scene(s)'}, target {low}-{high}")
    if long_short:
        report.warn("scene-mix", f"spoken words outside {cfg['words_per_scene'][0]}-{cfg['words_per_scene'][1]} "
                    f"in scene(s) {', '.join(long_short)}")
    if motions_run:
        report.warn("scene-mix", f"same motion more than {cfg['same_motion_max']} times in a row at scene(s) {', '.join(motions_run)}")
    if n_spoken and n_on_screen / n_spoken > cfg["on_screen_share_max"]:
        report.warn("scene-mix", f"on-screen text on {n_on_screen} of {n_spoken} spoken scenes "
                    f"(at most {cfg['on_screen_share_max']:.0%})")
    mix = ", ".join(f"{counts.get(t, 0)} {t}" for t in cfg["visuals"])
    report.summary = (f"{total} scenes ({mix}), {len(c_words):,} words spoken, {len(prompts['scene'])} image "
                      f"prompt(s), {len(prompts['anim'])} clip prompt(s). ")
    return report


def check_all(folder, thresholds=None):
    folder, files = Path(folder), SETTINGS["files"]
    facts = folder / files["facts"]
    reports = [check_script(folder / files["script"], facts, thresholds)]
    if (folder / files["voice"]).exists():
        reports.append(check_voice(folder / files["script"], folder / files["voice"], facts))
    if (folder / files["scenes"]).exists():
        reports.append(check_scenes(folder / files["scenes"], folder / files["script"], facts))
    if (folder / files["publication"]).exists():
        reports.append(check_publication(folder / files["publication"], facts))
    return reports


# ------------------------------------------------------------------ command line
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("target", choices=["script", "voice", "scenes", "publication", "all", "fingerprint"])
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--facts")
    ap.add_argument("--thresholds")
    a = ap.parse_args(argv)
    need = {"script": 1, "voice": 2, "scenes": 1, "publication": 1, "all": 1, "fingerprint": 1}[a.target]
    if len(a.paths) != need:
        ap.print_usage(sys.stderr)
        return 2
    if a.target == "fingerprint":
        path = Path(a.paths[0])
        if not path.exists():
            print(f"file not found: {path}", file=sys.stderr)
            return 2
        print(fingerprint(path.read_text(encoding="utf-8")))
        return 0
    folder = Path(a.paths[0]) if a.target == "all" else None
    required = [Path(p) for p in a.paths] if folder is None else \
        [folder / SETTINGS["files"]["facts"], folder / SETTINGS["files"]["script"]]
    if a.target == "scenes":
        required.append(Path(a.paths[0]).parent / SETTINGS["files"]["script"])
    if a.facts:
        required.append(Path(a.facts))
    elif folder is None:
        required.append(Path(a.paths[0]).parent / SETTINGS["files"]["facts"])
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        print("file not found: " + ", ".join(missing), file=sys.stderr)
        return 2
    if a.target == "script":
        reports = [check_script(a.paths[0], a.facts, a.thresholds)]
    elif a.target == "voice":
        reports = [check_voice(a.paths[0], a.paths[1], a.facts)]
    elif a.target == "scenes":
        reports = [check_scenes(a.paths[0], facts=a.facts)]
    elif a.target == "publication":
        reports = [check_publication(a.paths[0], a.facts)]
    else:
        reports = check_all(folder, a.thresholds)
    print("\n\n".join(r.render() for r in reports))
    return 1 if any(r.blocks for r in reports) else 0


if __name__ == "__main__":
    sys.exit(main())
