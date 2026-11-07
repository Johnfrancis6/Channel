# Whose Dime — shared checks (S03)

`checker.py` (standard library only) checks a video folder against its fact registry, [`02b_factcheck.md`](FACTCHECK_FORMAT.md).

| Command | Checks |
|---|---|
| `python3 whosedime/common/checker.py script 02_script.md` | facts, quotes, `[TO VERIFY]`, forbidden phrases (block); style rules and next-video ending (warn) |
| `... voice 02_script.md 02_script_voice.txt` | the script's blocks, signed registry, voice = script up to spelled numbers and respellings (block) |
| `... publication 04_publication.md` | facts, quotes, `[TO VERIFY]`, forbidden phrases, title length (block). Sections: `## Titles` (list), `## Thumbnail`, `## Description`; `## Sources` is skipped |
| `... all FOLDER` | the three, with the file names of `settings.json` (voice and publication if present) |

`--facts FILE` overrides the registry (default: `02b_factcheck.md` next to the file); `--thresholds FILE` the style JSON.
**Exit codes**: 0 no block (warnings allowed), 1 at least one `BLOCK`, 2 usage error or missing file.

Where each list lives (edit the file, never the code): style rules and thresholds in
[`../research/style_thresholds.json`](../research/style_thresholds.json); forbidden phrases in
[`forbidden_phrases.txt`](forbidden_phrases.txt); next-video phrases in [`next_video_markers.txt`](next_video_markers.txt);
capitalised non-names in [`not_names.txt`](not_names.txt); voice respellings in [`lexicon.tsv`](lexicon.tsv);
title length, ending length, file names in [`settings.json`](settings.json). Tests: `tests/test_checker.py`.
Limits: a name used only as a sentence's first word is not checked; titles and thumbnails are checked for numbers, not names.
