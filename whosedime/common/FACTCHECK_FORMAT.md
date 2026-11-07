# `02b_factcheck.md`: the fact registry (decision D4)

One registry per video, in the video folder, next to `02_script.md`. Every
number, date, name and quotation said in the script or written in the
publication must match a line of it; [`checker.py`](checker.py) blocks
anything else. Franco signs it; until he does, the voice is blocked.

## Sections

The file has three `##` sections, in this order. Tables are Markdown
tables; the first row names the columns (any order, these exact names).

**`## Facts`**: one line per fact.

| Column | What goes in it |
|---|---|
| `id` | `F01`, `F02`... never reused, never renumbered |
| `text` | the fact **as it may appear** in the script: its numbers, dates and names written the way the script writes them (`$1.1 billion`, `June 2015`, `San Francisco`). A short claim is best: everything in it counts as registered |
| `source` | URL, or document and page (`Uber 2023 Form 10-K, p. 54`). Never empty |
| `read` | date the source was read in full, `YYYY-MM-DD` (required when `verified`) |
| `status` | `verified` (read in full at the source), `[TO VERIFY]` (a lead: the script may not use it), or `withdrawn` (proved wrong or unsourced: the script and the publication may not use it) |

**`## People`**: one line per person, or per quotation when a person has
several. Names here are registered; so are the quotations.

| Column | What goes in it |
|---|---|
| `name` | full name (`Travis Kalanick`); a company or court for a quotation from a filing or a ruling |
| `role` | role at the time of the decision; `organisation` for a company or court (then it is not counted as a person by the style rules) |
| `date` | date of the decision (a date said aloud still needs a fact line) |
| `decision` | the decision, in a few words |
| `quote` | the **exact** quotation, in quotation marks, or `—` |
| `source` | where the quotation was read (required with a quote) |
| `status` | `verified`, `[TO VERIFY]` or `withdrawn`, as for facts |

**`## Signature`**: one line, `Signed: Franco, YYYY-MM-DD`. Any other
value (`Signed:` alone, `Signed: (not signed yet)`) counts as unsigned.
Re-sign after any change to a `verified` line.

## How the checker reads it

- **Numbers**: `$1.1 billion`, `1.1 billion dollars` and `one point one
  billion` are the same number; `41%` and `41 percent` too. A scale word
  (million, billion, trillion) is part of the number. Words `one` to `ten`
  are not checked (same rule as `measure.py`); digits always are.
- **Names**: capitalised words inside a sentence (see the checker's
  docstring for the limits). `10-K`, `S-1`, `Q3` are names, not numbers.
- **Quotations**: two words or more between quotation marks must sit word
  for word inside one `verified` quote of the people block (case and
  punctuation aside). `...` or `…` in the script may cut words out.
- **Tags**: the script and the publication may cite a line as `[^F04]`
  (Markdown footnote). A tag to an unknown id or to a line that is not
  `verified` blocks. Footnote definitions (`[^F04]: ...`) and `## Sources`
  sections are not checked for facts, but a `[TO VERIFY]` anywhere blocks.
- **Format errors block**: a fact without a source, a duplicate id, an
  unknown status, a verified fact without a read date.

## Example (Uber, from the S02 cold-open footnotes)

The S02 cold open used six sources; four are still `[TO VERIFY]`, so a
script using the 41 percent, the 2023 profit or the 2022 loss would be
blocked today. The test suite parses this example back.

<!-- example:start -->
```markdown
# Fact check — 01_uber "Uber Was Cheap. Who Paid?"

## Facts

| id | text | source | read | status |
|---|---|---|---|---|
| F01 | In 2008, in Paris, Travis Kalanick and Garrett Camp had trouble getting a cab; what they built next became Uber | Travis Kalanick, "Five years and 311 cities later", Uber Newsroom, 2015-06-01, https://www.uber.com/ma/en/newsroom/five-years-and-311-cities-later/ | 2026-11-07 | verified |
| F02 | Kalanick and Camp were in Paris for a week at LeWeb, in 2008 | Travis Kalanick, "Uber's Founding", Uber Newsroom, 2010-12-22, https://www.uber.com/newsroom/ubers-founding | 2026-11-07 | verified |
| F03 | the first idea was a limo timeshare service: a driver, a luxury car, a parking spot shared | same post as F02 | 2026-11-07 | verified |
| F04 | riders paid about 41 percent of what each trip really cost (year to September 2015, Hubert Horan's estimate) | Hubert Horan, Naked Capitalism, late 2016, reported by SFist, 2016-12-02, https://sfist.com/2016/12/02/day_around_the_bay_uber_loses_2_bil/ | — | [TO VERIFY] |
| F05 | Uber's first full-year operating profit: $1.1 billion, in 2023 | City A.M., https://www.cityam.com/uber-reports-first-ever-full-year-operating-profit-as-chief-hails-an-inflection-point/ (to check against the 2023 Form 10-K) | — | [TO VERIFY] |
| F06 | in 2022 Uber lost $9.1 billion, inflated by revaluing its equity stakes | Yahoo News, https://ca.news.yahoo.com/ubers-smooth-operator-dara-khosrowshahi-144348071.html (to check against the 10-K) | — | [TO VERIFY] |

## People

| name | role | date | decision | quote | source | status |
|---|---|---|---|---|---|---|
| Travis Kalanick | co-founder of Uber | 2008 | builds a car-on-demand service after a night without a cab in Paris | "In 2008, on a snowy night in Paris, Garrett Camp and I had trouble getting a cab." | Uber Newsroom, 2015-06-01, https://www.uber.com/ma/en/newsroom/five-years-and-311-cities-later/ | verified |
| Garrett Camp | co-founder of Uber | 2008 | calls the Paris evening a turning point, not the beginning: the app was already designed | "a pivotal moment" | Bloomberg, reprinted by Yahoo Finance, https://uk.finance.yahoo.com/news/much-idea-worth-uber-case-234917668.html | [TO VERIFY] |

## Signature

Signed: (not signed yet)
```
<!-- example:end -->
