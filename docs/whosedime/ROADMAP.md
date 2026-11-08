# Whose Dime — build roadmap (sessions S01 to S09)

How the Whose Dime production pipeline gets built: one Claude Code session
per step, each one small enough to finish, test and hand over. **Each
session writes the prompt of the next one.** This file says what every
session is for; the next-session prompt says exactly how.

Read first: [`STATE.md`](STATE.md) (where we are), [`DECISIONS.md`](DECISIONS.md)
(what Franco decided), and the audit that motivates every step:
[`reports/Audit pipeline de production.md`](../../reports/Audit%20pipeline%20de%20production.md)
(French).

## Rules for every session

1. **Language.** Everything committed for Whose Dime is in English (D2).
   Talk to Franco in English (his choice since 2026-11-08, D17).
2. **Branches.** Build sessions work on the branch named in `STATE.md`
   (today: `claude/admiring-ramanujan-k2uiqe`). `git fetch` before every
   push. Production code that Colab runs lives on `main` (D5): sessions
   S01, S05 and S07 end with a pull request to `main`, which Franco merges.
3. **Scope.** Do only what the session prompt lists. Anything else goes to
   the "Open issues" section of `STATE.md`, with a one-line reason.
4. **Generated files.** Never edit `.claude/skills/` or `*.skill` by hand:
   edit the source, then run the sync tool named in `STATE.md`.
5. **Tests.** `python3 -m unittest discover -s tests` must pass before the
   final commit. A new check comes with a test that feeds it a faulty file.
6. **Critique protocol.** For every deliverable: a self-critique of 5 lines
   at most, Franco's grade question, one line in
   [`critique_log.jsonl`](critique_log.jsonl). See
   [`CRITIQUE_PROTOCOL.md`](CRITIQUE_PROTOCOL.md).
7. **Measured or assumed.** Say which. Recommendations, not lists of
   options. One question at a time when you need Franco.
8. **Secrets.** `YOUTUBE_API_KEY` and `SUPADATA_API_KEY` are in the
   environment: never print them. Reddit and Social Blade are blocked from
   the cloud: no workaround.
9. **Stop at the end of the scope**, even if Franco says "continue".

## The hand-off (last 15 minutes of every session)

1. Update [`STATE.md`](STATE.md) (60 lines at most): what is done, what is
   not, open issues, the branch, the sync tool, the next session.
2. Add to [`DECISIONS.md`](DECISIONS.md) anything Franco decided.
3. Write the next prompt in `docs/whosedime/sessions/SNN_<name>.md`, from
   the template below and the row of this roadmap. Carry over anything not
   finished; change the plan if the session learned something, and say so
   in one line at the top of the prompt.
4. Commit, `git fetch`, push. Give Franco the GitHub link of every file
   written (`https://github.com/Johnfrancis6/Channel/blob/<branch>/<path>`).
5. End the reply with:

   > ⏹️ **End of session SNN.** Before the next one: *(what Franco must
   > do, one line)*. **Next session: model <Model>**, with the Google Drive
   > connector.

   followed by the paste-ready opening message in a code block:

   ```text
   Whose Dime build, session SNN+1: <name>.
   git fetch origin <branch> && git checkout <branch> (stay on it).
   Read docs/whosedime/sessions/SNN+1_<name>.md and follow it.
   ```

### Template of a session prompt

```markdown
# SNN — <name>

> Changes from ROADMAP.md: <none | one line>

## Context (3 lines at most)
## Setup (git commands, packages)
## Read (exact files, in order; nothing else unless needed)
## Do (numbered tasks; each with its acceptance check)
## Do not
## Deliverables (paths)
## Hand-off (pointer to ROADMAP.md "The hand-off", plus the next session's name and model)
```

## The sessions

Audit corrections: C1 fact registry, C2 publication checked against
research, C3 one branch, C4 truthful state, C5 one source for targets,
C6 voice, C7 non-robotic writing, C8 names, versions, tests.

| # | Session | Goal | Main outputs | Done when | Corrections | Model |
|---|---|---|---|---|---|---|
| S01 | **Foundations** | One clean base: merge the latest Zehon pipeline, freeze Zehon, English project instructions, a sync tool that covers both channels and stamps a version, tests that run in a fresh container | merged branch, `CLAUDE.md` (English), `tools/sync_skills.py`, `whosedime/` skeleton, PR to `main` | tests green in a fresh container; sync check clean; PR open | C3, C8 | Opus 5.5 |
| S02 | **Storytelling rules for "Who Pays?"** | Measurable writing rules from the transcripts of the niche's hits and flops (named people, the decision, dialogue, rhythm, nuance, money explained simply), and the voice direction | `whosedime/research/storytelling_rules.md`, `voice_direction.md`, transcript corpus, one before/after rewrite (Uber cold open) | each rule has its source (niche transcripts, Zehon audit, or both) and a number that a checker can test | C7 | Opus 5.5 |
| S03 | **Shared checks** | The fact registry format and the checker: script and publication against `02b_factcheck.md`, `[TO VERIFY]` blocking, script against voice version, forbidden phrases (financial advice), title length, style warnings from S02 | `whosedime/common/` (checker + tests with faulty files) | a fake faulty script and publication are rejected; real-looking clean ones pass with ≤ 3 false alerts | C1, C2, C5, C7 | Opus 5.5 |
| S04 | **`whosedime-maker`, part 1: topic to script** | Steps 1 to 3 in English: topic, research + signed fact check + people registry, six-beat outline, script and voice version, validation by ear (20 s sample) | `whosedime/whosedime-maker/` (SKILL.md, references 1-3, evals) | evals pass; checker clean on an eval script about Uber | C1, C7 | Opus 5.5 |
| S05 | **`whosedime-maker`, part 2: scenes to publication, and state** | Scenes (85-95, with a `chart` type tied to fact ids), image prompts, publication (titles ≤ 40 characters, thumbnail rules), per-video state file in Drive, session table | references 4-5, `memory.md`, state convention; PR to `main` | checker passes on eval outputs; a fresh Haiku session answers "where are the videos?" correctly from the files | C2, C4 | Sonnet 5.5 |
| S06 | **Voice notebook (English)** | Paragraph synthesis, pauses that follow punctuation, dry-ending detector, 20 s listening sample, VoiceDesign then clone, both speaking rates written | `whosedime/notebooks/voice_whosedime.ipynb` + launcher | runs end to end on a fake Drive with a stub model; detector flags a cut test clip | C5, C6 | Opus 5.5 |
| S07 | **Charts and assembly** | Charts generated from `02b_factcheck.md`; assembly adapted (chart scenes, chapter cards, `chapters.txt`, verdict named after its output) | `whosedime/video-maker/`, chart tool, tests; PR to `main` | a short test render passes the technical check; an extract no longer overwrites the full verdict | C4 | Opus 5.5 |
| S08 | **Drive and pilot launch** | Create the `WhoseDime/` Drive tree, place the launchers, then start video 1 ("Uber Was Cheap. Who Paid?") with the skill's own session 1. The blind voice test (D7) happens during this first video | Drive tree, first video folder | Franco has validated topic and angle; production then follows the skill's session table | — | Sonnet 5.5 |
| S09 | **Weekly competitor watch** | The weekly tool from the old session-2 brief: new videos, hits (≥ 5× channel median), new entrants, title changes, for about 300 quota units | `whosedime/watch/`, first weekly report | one run under 300 units, report written | — | Sonnet 5.5 |

**After S09**: the incoherence-detection skill is designed once
`critique_log.jsonl` holds about 30 graded lines (plan in § 5 of the audit).

**Order.** S01 first. S02 before S04 (the script step needs its rules).
S03 before S04. S09 depends only on S01 and can run any time after it.

**Calendar (inference).** `PLAN_ACTION.md` puts the skill, the voice and the
tools in the week of 9-15 November and the pilot in 16-22 November. S01 to
S07 in one week means about one session a day: tight. If a session
overruns, the next prompt says so and shifts the pilot, rather than
skipping a check.

## What is not copied from Zehon

From the audit (§ 3, "Ce qu'il faut adapter"): the hook + 4 questions
structure and the forced "Sauf que" connector; the rule "the process, not
the biography"; the French voice version rules (numbers, acronyms,
lexicon); the ban on any end-of-video call to action (Whose Dime ends with
a bridge to the next episode and a comment question); scenes made only of
Gemini images; the round-headed character and its thumbnails. These are
rewritten in S02 to S05, not translated.
