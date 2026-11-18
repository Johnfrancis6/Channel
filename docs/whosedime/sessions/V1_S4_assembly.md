# Video 1, session 4 — assembly of "Uber Was Cheap. Who Paid?" (skill `whosedime-video`)

> Written 2026-11-18 by the orchestrator `session_01Cw13LeFBwzXQBL4SqwTyRi`. Model: Opus 5.5.
> Franco steps in only to grant permissions, run Colab and answer (D33). Answer him in his language (D31).

## Where we are (measured 18/11 in Drive `WhoseDime/Videos/01_uber/`, by the orchestrator)

- **Voice done** 17/11, validated by Franco 18/11: `voice/voice.wav`, `words.json`, `state.json` (`ready`, 13 min 47 s,
  157.0 wpm, narrator `d5211b92cf2b`).
- `03_scenes.md`: 94 scenes (55 image, 27 chart, 5 video, 1 title, 6 chapter).
- `images/`: **59 `.jpg`** (`scene_NNN.jpg`; `.jpg` is accepted by `image_exts`): the 55 image scenes **except 093**, plus
  the 5 start images of the video scenes (008, 027, 060, 073, 090). **Missing: `scene_093`** (Franco to make it, prompt in
  `03_scenes.md`, batch 6).
- `clips/`: **5 clips named `anim_008.mp4`, `anim_027.mp4`, `anim_060.mp4`, `anim_073.mp4`, `anim_090.mp4`**.
  `assemble.py` (`find_file`) looks only for `clips/scene_NNN.*`, so today they would be ignored (the image replaces each
  clip, with a warning). Cause: our own `03_scenes.md` headings say `anim_NNN` while its text says `clips/scene_NNN.mp4`.

## Do

1. **Accept `anim_NNN` clips** (D18, technical): `find_file` / `attach_files` in `whosedime/whosedime-video/scripts/assemble.py`
   also accept `clips/anim_NNN.<clip ext>` (prefix list in `settings.json`, `scene` first). Test it. Fix the
   `whosedime-maker` step-4 template so future `03_scenes.md` name the clip `scene_NNN.mp4` in the heading too.
   `python3 tools/sync_skills.py`, `--check`. Tests green. Commit, push, **pull request to `main`**; give the link.
2. **Read before Franco renders**: the assembly launcher and notebook (`whosedime/notebooks/assembly_*.ipynb`), the skill
   `whosedime-video` (SKILL.md, settings.json), `assemble.py`'s gate and verdict, and the S07c follow-ups still open in
   STATE.md (scene 82 people colour, 61 block high, phone sizes). Say in one line each whether video 1 is affected.
3. **Guide Franco through Colab**, one step at a time, once the PR is merged and `scene_093` is in `images/`:
   `MODE = "plan"` (gate, charts, timing; no render) → `MODE = "extract"`, `SCENES = "1-10"` (he watches) → `MODE = "full"`.
   Read every output he pastes; a refused chart is fixed in `03_scenes.md` only by Franco's validation (content), never
   by hand in a drawing (D4). Do not edit Drive files yourself (the Drive editor re-escapes `.md`).
4. After the full render: the verdict and `chapters.txt`; Franco watches the video and grades it (Accurate / Clear /
   Lively). Critique line (`"step": "V1_S4_assembly"`), STATE.md (60 lines at most), commit, push.
5. Hand-off (D17, D19): write the next prompt (video 1 publication: upload checklist from `04_publication.md`, thumbnail A,
   description with `chapters.txt`), open it with `create_session`, report to `session_01Cw13LeFBwzXQBL4SqwTyRi`
   with `send_message` (links, verdict, grades, self-critique). Then stop.

## Watch out

Branch `claude/v1-s4-assembly` (made from `main`, holds this prompt). Push without `2>&1` after the branch name; one
command per push (the guard reads the branch before a chained checkout). Everything committed in English.
