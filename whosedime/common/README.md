# Whose Dime — shared checks (S03)

`checker.py` (standard library only) checks a video folder against its fact registry, [`02b_factcheck.md`](FACTCHECK_FORMAT.md).

| Command | Checks |
|---|---|
| `python3 whosedime/common/checker.py script 02_script.md` | facts, quotes, `[TO VERIFY]`, forbidden phrases (block); style rules and next-video ending (warn) |
| `... voice 02_script.md 02_script_voice.txt` | the script's blocks, signed registry whose `sha256:` hash matches its content, voice = script up to spelled numbers and respellings (block) |
| `... scenes 03_scenes.md` | (S05) spoken text = `02_script.md` word for word; every chart cites `verified` fact ids and only their numbers; table, types, file names, motions, cards; a prompt per image and clip; no person of the people block named in a prompt; on-screen numbers (block). Scene mix (warn) |
| `... publication 04_publication.md` | facts, quotes, `[TO VERIFY]`, forbidden phrases, title length; (S05) a number in a title or thumbnail line needs the `[^Fnn]` of a fact holding it (block). Sections: `## Titles` (list), `## Thumbnail`, `## Description`; `## Sources` and `## Notes` are skipped |
| `... all FOLDER` | the four, with the file names of `settings.json` (voice, scenes and publication if present) |
| `... fingerprint 02b_factcheck.md` | prints the `sha256:<12 hex>` hash Franco pastes on the `Signed:` line (S04) |

`--facts FILE` overrides the registry (default: `02b_factcheck.md` next to the file); `--thresholds FILE` the style JSON.
**Exit codes**: 0 no block (warnings allowed), 1 at least one `BLOCK`, 2 usage error or missing file.

Where each list lives (edit the file, never the code): style rules and thresholds in
[`../research/style_thresholds.json`](../research/style_thresholds.json); forbidden phrases in
[`forbidden_phrases.txt`](forbidden_phrases.txt); next-video phrases in [`next_video_markers.txt`](next_video_markers.txt);
capitalised non-names in [`not_names.txt`](not_names.txt); voice respellings in [`lexicon.tsv`](lexicon.tsv);
title length, ending length, file names, scene targets in [`settings.json`](settings.json). Tests: `tests/test_checker.py`.
Limits: a name used only as a sentence's first word cannot block (it cannot be told from a common word); unknown sentence-first words are listed in one `name-first` warning, which also lists common words (measured on the clean Uber script: 1 warning line, 8 words, none a name). Titles and thumbnails are checked for numbers, not names.
