"""Storytelling metrics for one text (Whose Dime, S02).

Standard library only, so the S03 checker can import it:

    from measure import measure
    m = measure(text, duration_s=None, lang="en", people=None)

Command line:

    python3 measure.py FILE [--duration SECONDS] [--lang en|fr]   # JSON for one text
    python3 measure.py --corpus                                    # writes corpus/metrics.csv

Every method below is deliberately simple and stated, so a number can be
recomputed by hand. Lexical lists are English; `lang="fr"` swaps in short
French lists only to measure the two Zehon scripts for contrast (finance
jargon is not measured in French).

Methods
-------
Cleaning: caption tags in square brackets ("[music]") and ">>" speaker
markers are removed; Markdown heading lines (#...) are dropped.

Words: whitespace tokens that contain a letter or a digit.

Sentences: split after ., ! or ? (plus closing quotes) when followed by
whitespace; a list of abbreviations (Mr., Dr., Inc., U.S., ...) is protected.

Named people (list method): a person is introduced by (a) a given name
from GIVEN_NAMES followed by one or two capitalised words (a name
never runs past punctuation; pronouns and articles in NOT_NAMES never
count), (b) a title
from TITLES followed by one to three capitalised words, or (c) a name passed in
`people`. Once introduced, any capitalised token of that name (given name
or surname, possessive 's stripped) counts as one mention. Mentions are
counted per 150 words.

Tension markers (EN): but, yet, then, until, instead, "only to".
Contrast words (EN): but, yet, however, although, except.

Numbers: a run of consecutive numeric tokens counts once ("$1.5 billion",
"2 834", "twenty-two thousand"). Numeric tokens: anything with a digit,
scale words (hundred, thousand, million, billion, trillion) and English
number words from eleven upwards. "one" to "ten" are not counted (too
often pronouns or idioms: "one kid", "two for one").

Quoted dialogue: spans between quote marks (" ", “ ”, « ») of two words or
more. Auto-captions mark few of them: for transcripts this is a lower bound.

Questions to the viewer: sentences ending in "?" outside quoted spans.

Openers: the first word of each sentence, lower-cased. The most repeated
connector opener is the most frequent opener found in CONNECTORS.

Finance jargon: occurrences of the terms in JARGON (words a lay viewer may
not know; everyday words with a second meaning, such as "bond", "royalty",
"monopoly", "inflation", were removed after reading the corpus). A distinct term is
"explained" if, after at least one of its occurrences, the next 25 words
contain an explanation marker from EXPLAIN_MARKERS, or the term is
directly followed by ", a", ", an" or " (" (apposition).
"""
import csv
import json
import pathlib
import re
import statistics
import sys
from collections import Counter

# ---------------------------------------------------------------- word lists
GIVEN_NAMES = set("""
aaron adam adolf al alan albert alex alexander alfred alice allen amanda amy andrew andy angela
ann anna anne anthony antonio arnold arthur barack barbara ben benjamin bernard bernie betty bill
billy bob bobby brad brian bruce carl carlos carol catherine charles charlie chris christian
christopher chuck clara colin craig dan daniel dave david dennis diana dick don donald doug
douglas earl ed eddie edward elizabeth ellen elon emily emma eric ernest evan frank franklin fred
frederick friedrich gary george gerald gordon grace greg gregory hank hans harold harry harvey
helen henri henry herbert howard hugh humphry ian isaac jack jacob jake james jamie jan jane
janet jason jay jean jeff jeffrey jen jennifer jensen jeremy jerry jim jimmy joan joe john johnny
jon jonathan jordan jose joseph josh joshua juan judy julia julie justin karen karl kate katherine
keith ken kenneth kevin kim kurt larry laura lee leo leonard linda lisa louis lucy luke margaret
maria marie mark martha martin mary masayoshi matt matthew max michael mike milton nancy nathan
neil nick nicholas noah oliver oscar pat patricia patrick paul peter phil philip phillip pierre
ralph ray raymond reed richard rick robert robin roger ronald rose roy russell ruth ryan sam
samuel sarah scott sean sergey shawn sophie stanley stephen steve steven susan ted terry thomas
tim timothy todd tom tony travis victor vincent walt walter warren wayne william
alastair angelo garrett dara
""".split())
NOT_NAMES = set("""
i i'm i've i'll i'd you you're he he's she she's we we're they they're it it's this that these
those the a an and but so or then now here there what why how when who where yes no not
""".split())
TITLES = set("""
mr mrs ms dr sir president senator governor emperor king queen prince princess pope ceo founder
chairman judge general colonel captain professor minister chancellor mayor
empereur roi reine pharaon chimiste physicien monsieur madame
""".split())
ABBREVIATIONS = ["Mr.", "Mrs.", "Ms.", "Dr.", "St.", "Jr.", "Sr.", "Inc.", "Co.", "Corp.",
                 "Ltd.", "U.S.", "U.K.", "vs.", "e.g.", "i.e.", "No.", "Mt.", "a.m.", "p.m."]

LEX = {
    "en": dict(
        tension=["but", "yet", "then", "until", "instead", "only to"],
        contrast=["but", "yet", "however", "although", "except"],
        connectors={"and", "but", "so", "then", "now", "because", "yet", "still", "also", "plus",
                    "or", "meanwhile", "instead", "however", "and so", "which"},
        you={"you", "your", "you're", "yours", "yourself"},
        number_words={"eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
                      "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
                      "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "million",
                      "millions", "billion", "billions", "trillion", "trillions", "dozen"},
    ),
    "fr": dict(
        tension=["mais", "pourtant", "puis", "jusqu'à", "au lieu", "sauf que"],
        contrast=["mais", "pourtant", "cependant", "bien que", "sauf"],
        connectors={"et", "mais", "sauf", "alors", "puis", "or", "pourtant", "donc", "car"},
        you={"tu", "ton", "ta", "tes", "toi", "vous", "votre", "vos"},
        number_words={"mille", "million", "millions", "milliard", "milliards"},
    ),
}

JARGON = [
    "ebitda", "valuation", "ipo", "equity", "private equity", "venture capital",
    "venture capitalist", "leverage", "leveraged", "liquidity", "dividend", "dividends",
    "shareholder", "shareholders", "buyback", "buybacks", "market cap", "market capitalization",
    "cash flow", "balance sheet", "gross margin", "profit margin", "operating loss",
    "operating profit", "operating income",
    "net loss", "write-down", "burn rate", "unit economics", "interest rate", "interest rates",
    "junk bond", "junk bonds", "bond sale", "collateral", "derivatives", "securities",
    "mortgage-backed", "credit default swap", "credit default swaps", "hedge fund",
    "hedge funds", "short seller", "short sellers", "spac", "subsidy", "subsidies",
    "subsidize", "subsidized", "antitrust", "interchange", "chapter 11",
    "quantitative easing", "monetary policy", "fiscal", "gdp", "deflation",
    "franchisee", "franchisees", "sec", "10-k", "take rate", "gig economy", "lobbying",
]
EXPLAIN_MARKERS = [
    "means", "meaning", "which is", "which means", "that is", "in other words", "basically",
    "think of", "essentially", "put simply", "simply put", "is when", "is what", "is just",
    "fancy word", "fancy way", "a.k.a", "aka", "also known as", "stands for", "imagine",
    "in plain english", "translation",
]

# ------------------------------------------------------------------ helpers
QUOTE_RE = re.compile(r'"([^"]+)"|“([^”]+)”|«([^»]+)»')
WORD_RE = re.compile(r"[\w$%€£'’.,-]*[A-Za-zÀ-ÿ0-9][\w$%€£'’.,-]*")


def clean(text):
    lines = [ln for ln in text.splitlines() if not ln.lstrip().startswith("#")]
    t = "\n".join(lines).replace("\\", "")
    t = re.sub(r"\[[^\]]{0,40}\]", " ", t)
    t = t.replace(">>", " ").replace("**", "")
    return re.sub(r"[ \t]+", " ", t).strip()


def tokens(text):
    """Raw whitespace tokens that hold a letter or a digit (punctuation kept)."""
    return [w for w in text.split() if re.search(r"[A-Za-zÀ-ÿ0-9]", w)]


def words(text):
    return [w.strip(".,;:!?\"“”«»()") for w in tokens(text)]


def sentences(text):
    t = text
    for a in ABBREVIATIONS:
        t = t.replace(a, a.replace(".", "․"))
    parts = re.split(r'(?<=[.!?])["”»]?\s+', t)
    out = []
    for p in parts:
        p = p.replace("․", ".").strip()
        if words(p):
            out.append(p)
    return out


def _phrase_positions(wl, phrase):
    """Word indexes where a (possibly multi-word) lower-case phrase starts."""
    ph = phrase.split()
    n = len(ph)
    return [i for i in range(len(wl) - n + 1) if wl[i:i + n] == ph]


def _norm(w):
    return re.sub(r"['’]s$", "", w).lower()


def _is_cap(w):
    return bool(w) and w[0].isupper() and any(c.isalpha() for c in w)


def _is_numeric(w, number_words):
    lw = w.lower().strip("$%€£")
    if re.search(r"\d", w):
        return True
    return any(part in number_words for part in lw.split("-"))


def count_numbers(wl_raw, number_words):
    """Runs of consecutive numeric tokens, each run counted once."""
    n, prev = 0, False
    for w in wl_raw:
        cur = _is_numeric(w, number_words)
        if cur and not prev:
            n += 1
        prev = cur
    return n


def find_people(toks, people=None):
    """Return (index of first mention, number of mentions, distinct names).

    `toks` are the raw word tokens (punctuation kept), aligned with words().
    A name never runs past a token that ends in punctuation.
    """
    known = {}  # token (lower) -> canonical name
    for name in people or []:
        for tok in name.split():
            known[_norm(tok)] = name
    bare = [t.strip(".,;:!?\"“”«»()") for t in toks]

    def cap(i):
        return i < len(bare) and _is_cap(bare[i]) and _norm(bare[i]) not in NOT_NAMES \
            and _norm(bare[i]) not in TITLES

    def stops(i):
        return bool(re.search(r"[.,;:!?)\"”»]$", toks[i]))

    first, mentions, distinct = None, 0, set()
    i = 0
    while i < len(bare):
        lw = _norm(bare[i])
        intro, start = None, i
        if lw.split("'")[-1].rstrip(".") in TITLES and not stops(i) and cap(i + 1):
            start = i + 1
        if (start > i or (lw in GIVEN_NAMES and not stops(i) and cap(i + 1))) and cap(start):
            j = start
            while j < start + 3 and cap(j):
                j += 1
                if stops(j - 1):
                    break
            intro = bare[start:j]
        if intro:
            name = " ".join(_norm(t) for t in intro)
            for tok in intro:
                known.setdefault(_norm(tok), name)
            mentions += 1
            distinct.add(name)
            first = start if first is None else first
            i = start + len(intro)
            continue
        if cap(i) and lw in known:
            mentions += 1
            distinct.add(known[lw])
            first = i if first is None else first
        i += 1
    return first, mentions, sorted(distinct)


def jargon(wl, low_text):
    """(occurrences, distinct terms, distinct terms explained at least once)."""
    hits, explained = Counter(), set()
    for term in JARGON:
        k = len(term.split())
        for p in _phrase_positions(wl, term):
            hits[term] += 1
            after = " ".join(wl[p + k:p + k + 25])
            if any(re.search(r"\b" + re.escape(m) + r"\b", after) for m in EXPLAIN_MARKERS):
                explained.add(term)
        if hits[term] and re.search(r"\b" + re.escape(term) + r"\b(, an? | \()", low_text):
            explained.add(term)
    return sum(hits.values()), len(hits), len(explained)


def _per(x, n, base):
    return round(x * base / n, 2) if n else 0.0


# ---------------------------------------------------------------- measure
def measure(text, duration_s=None, lang="en", people=None):
    lex = LEX[lang]
    t = clean(text)
    wl_raw = words(t)
    wl = [w.lower() for w in wl_raw]
    n = len(wl)
    sents = sentences(t)
    lens = [len(words(s)) for s in sents]

    tot_j, distinct_j, expl_j = jargon(wl, t.lower()) if lang == "en" else (0, 0, 0)

    first_person, n_mentions, people_found = find_people(tokens(t), people)
    tension_pos = [p for m in lex["tension"] for p in _phrase_positions(wl, m)]
    contrast = sum(len(_phrase_positions(wl, m)) for m in lex["contrast"])

    quotes = [q for q in QUOTE_RE.findall(t) if len(words("".join(q))) >= 2]
    unquoted = QUOTE_RE.sub(" ", t)
    questions = sum(1 for s in sentences(unquoted) if s.rstrip().rstrip('"”»').endswith("?"))

    openers = Counter(words(s)[0].lower().strip("'’") for s in sents if words(s))
    top_op, top_n = openers.most_common(1)[0] if openers else ("", 0)
    conn = Counter({k: v for k, v in openers.items() if k in lex["connectors"]})
    top_c, top_cn = conn.most_common(1)[0] if conn else ("", 0)

    return dict(
        words=n,
        sentences=len(sents),
        wpm=round(n / (duration_s / 60), 1) if duration_s else None,
        words_before_first_person=first_person if first_person is not None else n,
        words_before_first_tension=min(tension_pos) if tension_pos else n,
        people_mentions_per_150=_per(n_mentions, n, 150),
        distinct_people=len(people_found),
        dialogue_per_1000=_per(len(quotes), n, 1000),
        sentence_mean=round(statistics.mean(lens), 2) if lens else 0.0,
        sentence_sd=round(statistics.stdev(lens), 2) if len(lens) > 1 else 0.0,
        share_over_25=round(sum(x > 25 for x in lens) / len(lens), 3) if lens else 0.0,
        numbers_per_100=_per(count_numbers(wl_raw, lex["number_words"]), n, 100),
        numbers_first_60=count_numbers(wl_raw[:60], lex["number_words"]),
        contrast_per_1000=_per(contrast, n, 1000),
        questions_per_1000=_per(questions, n, 1000),
        you_per_1000=_per(sum(w.strip("'’") in lex["you"] for w in wl), n, 1000),
        top_opener=top_op,
        top_opener_count=top_n,
        top_opener_share=round(top_n / len(sents), 3) if sents else 0.0,
        top_connector=top_c,
        top_connector_count=top_cn,
        top_connector_per_1000=_per(top_cn, n, 1000),
        jargon_per_1000=_per(tot_j, n, 1000) if lang == "en" else None,
        jargon_distinct=distinct_j if lang == "en" else None,
        jargon_explained_share=(round(expl_j / distinct_j, 3) if distinct_j else None)
        if lang == "en" else None,
    )


# ------------------------------------------------------------------ corpus
HERE = pathlib.Path(__file__).resolve().parent
CORPUS = HERE.parent / "corpus"
ZEHON = [("zehon_verre", "Zehon", "Le verre (script v2, 01/10/2026)"),
         ("zehon_aluminium", "Zehon", "L'aluminium (script, 01/10/2026)")]
METRICS = list(measure("Word.").keys())


def run_corpus():
    rows = []
    with (CORPUS / "index.csv").open() as f:
        for r in csv.DictReader(f):
            text = (CORPUS / "raw" / f"{r['video_id']}.txt").read_text()
            m = measure(text, duration_s=float(r["duration_s"]))
            rows.append(dict(video_id=r["video_id"], channel=r["channel"], label=r["label"], **m))
    for vid, ch, _title in ZEHON:
        p = CORPUS / "raw" / f"{vid}.txt"
        if p.exists():
            rows.append(dict(video_id=vid, channel=ch, label="zehon", **measure(p.read_text(), lang="fr")))
    with (CORPUS / "metrics.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["video_id", "channel", "label"] + METRICS)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} rows -> {CORPUS / 'metrics.csv'}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--corpus"]:
        run_corpus()
    elif args:
        dur = float(args[args.index("--duration") + 1]) if "--duration" in args else None
        lang = args[args.index("--lang") + 1] if "--lang" in args else "en"
        print(json.dumps(measure(pathlib.Path(args[0]).read_text(), dur, lang), indent=2))
    else:
        print(__doc__)
