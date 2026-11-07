# Critique protocol (Whose Dime)

English version of [`docs/audit/PROTOCOLE_CRITIQUES.md`](../audit/PROTOCOLE_CRITIQUES.md)
(decided by Franco on 07/11/2026). From now on, grades are collected on
Whose Dime deliverables only (decision D11), in
[`critique_log.jsonl`](critique_log.jsonl). The old French journal
(`docs/audit/journal_critiques.jsonl`) stays as the Zehon archive.

The log will be used to design the incoherence-detection skill, once it
holds about 30 graded lines.

## After every deliverable

Deliverables: research, fact check, outline, script, voice version, scenes
and prompts, publication, and any build artefact (skill, checker, notebook,
report, session prompt).

1. **Claude critiques its own deliverable**, in 5 lines at most, before
   presenting it as finished. Each defect has a type from the list below
   and points to the exact place (line, scene, sentence).
2. **Claude asks Franco for his grade**, in a single question:
   "Accurate / Clear / Lively, from 1 to 5, and one sentence?"
   (In French: « Exact / Clair / Vivant, de 1 à 5, et une phrase ? »)
3. **Claude appends one line** to `critique_log.jsonl` and commits it,
   even if Franco does not answer: his fields then stay `null`.

## Defect types

| Type | Example |
|---|---|
| `fact` | number, date or name wrong, unsourced, or quoted from memory |
| `inconsistency` | script contradicts the outline; a scene does not match the sentence spoken; the title promises what the video does not show |
| `process` | step skipped, file missing or misnamed, duplicate in Drive, session resuming at the wrong place |
| `robotic` | report-like sentence, list of facts, no person and no scene |
| `formal` | stiff register, jargon, administrative phrasing |
| `nuance` | absolute claim where the sources hesitate; no "but" |
| `comprehension` | notion not explained, sentence too long for the ear, logical jump |
| `voice` | word or number mispronounced, cut ending, flat delivery (after Franco listens) |

## Line format

```json
{"date": "2026-11-12", "channel": "whose_dime", "video": "01_uber", "step": "3b_script",
 "deliverable": "02_script.md", "session": "<session link>",
 "self_critique": [{"type": "robotic", "where": "beat 3, l. 2", "defect": "three numbers in a row, no scene"}],
 "franco": {"accurate": 4, "clear": 3, "lively": 2, "comment": "sounds like a lecture"},
 "fixed": true}
```

A defect that Franco reports and Claude missed is written in
`self_critique` with `"seen_by": "franco"`: these are the most useful cases
for the future skill.
