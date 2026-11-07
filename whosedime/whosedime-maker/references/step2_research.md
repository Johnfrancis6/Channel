# Step 2: Research and the signed fact check

**Goal**: two files. `01_research.md` gives the script a story (people,
scenes, the dollar's path) with every fact read at its source;
`02b_factcheck.md` is the registry the checker reads, which Franco
**signs**. Rule of the channel (decision D4): **nothing is said aloud
without a `verified` line of the registry.**

## Read sources in full

- **Read** means you opened the page or document and read the passage
  yourself in this session (web fetch, PDF), not a search-engine summary,
  not your memory. A search result snippet is a lead, never a source.
- **Prefer the primary document**: the company's filing (Form 10-K, S-1,
  annual report, results press release), the court's judgment or press
  summary, the regulator's release, the founder's own post. Then a dated
  article of a major outlet that quotes it.
- **A source that blocks you** (paywall, 403): use the same text where it
  is reposted in full (say where), or another source that you can read.
  If you read none, the fact is `[TO VERIFY]`.
- **Numbers as the source writes them**: `$1,110 million` in a table may
  be said `$1.1 billion`; write both in the fact's text if the script
  rounds. Note the period (fiscal year, "year to September 2015").
- **Estimates stay estimates**: one analyst's figure is said as his
  estimate, with his name ("Hubert Horan's estimate"), never as the
  company's accounts.
- Pick the facts the story needs: about 20 to 35 lines for a 13-15 min
  video. A number nobody will say does not belong in the registry.

## What to find

1. **The payer chain**: who pays, in 3 steps (the "follow the dollar"
   beat): at each step, **a payer, an amount and a source**. Start from the
   step 1 lead; change it if the sources say otherwise, and say so.
2. **The decision**: the dated moment when someone chose to make the thing
   free or cheap: who, when, where, what they decided, what they said
   (exact words, if any).
3. **Three scenes** (audit C7): three moments we can tell, each with **a
   person, a place, a gesture, and a line** (what they said or wrote,
   sourced, word for word). One of them opens the video (by-ear rule E1).
   A scene without a sourced line can still be told, but its words are the
   narrator's, never in quotation marks.
4. **The nuance**: where the sources disagree or the story is less simple
   (the "but"): one line each, with both sources.
5. **The consequences**: who won, who lost, what changed (rulings, laws,
   prices), as facts, without a political verdict.
6. **Names to pronounce**: any name or acronym a narrator could misread;
   its respelling goes in `whosedime/common/lexicon.tsv` (repo) only with
   Franco's agreement, since it changes the checker's allowed rewrites.

## `01_research.md`

```markdown
# Research: <nn>_<topic>, "<working title>" (<date>)

**The story in one sentence**: <who decided what, and who paid>
**Payer chain**: <payer 1> → <payer 2> → <payer 3> (changed from the step 1 lead? say why)

## Sources read in full
| # | Source (author, title, outlet, date, URL) | What it holds | Read on |
|---|---|---|---|

## The decision
<date, place, people, what they chose, their words: fact ids>

## Follow the dollar (3 steps)
1. <payer>: <amount> <who receives it> (F..)
2. ...

## Three scenes (person, place, gesture, line)
1. <person>, <place>, <date>: <gesture>. Line: "<exact words>" (people block, F..)
2. ...

## Nuance (the "but")
## Consequences
## Leads not used ([TO VERIFY] or withdrawn, and why)
## Names to pronounce
```

Every fact in it carries its registry id `(F07)`: the research file
explains, the registry proves.

## `02b_factcheck.md`

Follow `whosedime/common/FACTCHECK_FORMAT.md` (repo) exactly: sections
`## Facts`, `## People`, `## Signature`, Markdown tables with the exact
column names. The rules that matter most:

- **`text` is written the way the script will say it**: its numbers,
  dates and names as they will appear (`$3.5 billion`, `June 2016`,
  `Public Investment Fund`). Everything in a fact's text counts as
  registered, so keep each line to one short claim.
- **`status`**: `verified` only if you read it in full at the source, with
  the date in `read`; else `[TO VERIFY]` (the script may not use it) or
  `withdrawn` (proved wrong).
- **People block**: one row per person (or per quotation): name, role at
  the time, date, decision, **exact quote** in quotation marks or `—`, its
  source. A company or a court quoted from a filing or a ruling has the
  role `organisation`.
- Ids `F01`, `F02`... are never reused or renumbered; a dropped fact
  becomes `withdrawn`.

Check it parses before you show it, from the repo root:
`python3 whosedime/common/checker.py fingerprint F/02b_factcheck.md` must
print a hash (a malformed table shows up at the first `script` check).

## Pause 2: Franco reads and signs

Summarize in 5 lines at most: the story, the payer chain, the decision,
the three scenes, and what stayed `[TO VERIFY]`. Give the Drive link of
both files. Then **one question**: "Have you read the fact check? If yes,
sign it." (in French: « Tu as relu le fact check ? Si oui, signe-le. »).

**How Franco signs** (Claude Code): you run
`python3 whosedime/common/checker.py fingerprint F/02b_factcheck.md` and
give him the line to paste under `## Signature`:

```
Signed: Franco, <YYYY-MM-DD>, sha256:<the printed 12 hex>
```

He pastes it himself (or tells you "signed" and you write exactly that
line with today's date: say so in the log). Any later change above the
signature, even one character, changes the hash and blocks the voice until
he signs again. On claude.ai there is no checker: deliver the registry
unsigned and say that the signature is done in Claude Code.

Then the critique line for step 2 (`"step": "2_research"`, deliverable
`01_research.md, 02b_factcheck.md`), after his grade question.
