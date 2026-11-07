# Whose Dime — storytelling research (S02)

| File | What it is |
|---|---|
| [`storytelling_rules.md`](storytelling_rules.md) | The 14 writing rules (S1-S14), 5 by-ear rules (E1-E5), limits |
| [`style_thresholds.json`](style_thresholds.json) | Ids, metrics, thresholds, levels: the only place S03 reads them from |
| [`voice_direction.md`](voice_direction.md) | Narrator, rate, pauses, dialogue voices, blind test for video 1 |
| [`rewrite_uber_cold_open.md`](rewrite_uber_cold_open.md) | Uber cold open before/after, measured; texts in `examples/` |
| `corpus/index.csv`, `corpus/metrics.csv` | 30 videos (20 hits, 10 flops) and their metrics, + 2 Zehon scripts |
| `tools/` | `build_corpus.py` (API + transcripts), `measure.py` (metrics, stdlib), `compare.py`, `make_rules.py` (JSON + rule table) |

Transcripts and API caches live in `corpus/raw/` (git-ignored: other
people's scripts are not republished). To rerun, with both API keys set:
`python3 whosedime/research/tools/build_corpus.py select`, then `fetch`,
then `measure.py --corpus`, then `make_rules.py`. Tests: `tests/test_measure.py`.

**Quota used (2026-11-07, measured)**: YouTube Data v3 **29 units**
(channels, playlistItems, videos; no search); Supadata **30 calls** (budget 40).
