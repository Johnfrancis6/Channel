#!/usr/bin/env python3
"""Sync the channel skills to .claude/skills/ and rebuild their .skill archives.

Every folder that holds a SKILL.md directly under a channel folder
(zehon/, whosedime/) is a skill. For each one this tool:

- mirrors the source to .claude/skills/<skill>/;
- rebuilds the archive to install on claude.ai, <channel>/<skill>.skill
  (without evals/, fixed dates, so the same source gives the same bytes);
- writes a generated VERSION file into the mirror and the archive: the
  first 12 hex characters of a SHA-256 over the sorted source paths and
  their bytes. Two copies with the same VERSION come from the same source.

.claude/skills/ and the .skill files are generated: never edit them by
hand. Edit the source in <channel>/<skill>/, then run:

  python3 tools/sync_skills.py           # sync
  python3 tools/sync_skills.py --check   # report drift, write nothing (exit 1 on drift)
"""
import argparse
import hashlib
import io
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHANNELS = ("zehon", "whosedime")
MIRROR = Path(".claude") / "skills"
IGNORED = {"__pycache__", ".pytest_cache", ".DS_Store"}
NOT_ARCHIVED = {"evals"}
VERSION_FILE = "VERSION"
FIXED_DATE = (2026, 1, 1, 0, 0, 0)  # reproducible archive: same source, same bytes


def skills(root=ROOT):
    """Skill source folders of every channel, sorted by channel then name."""
    found = []
    for channel in CHANNELS:
        base = Path(root) / channel
        if base.is_dir():
            found += sorted(d for d in base.iterdir() if d.is_dir() and (d / "SKILL.md").is_file())
    return found


def files(folder, excluded=()):
    """Relative paths of the files under folder, sorted, without caches or excluded parts."""
    skip = IGNORED | set(excluded)
    return sorted(p.relative_to(folder) for p in Path(folder).rglob("*")
                  if p.is_file() and not skip & set(p.relative_to(folder).parts)
                  and p.suffix not in (".pyc", ".pyo"))


def version(source):
    """First 12 hex characters of a SHA-256 over the sorted source paths and bytes."""
    digest = hashlib.sha256()
    for relative in files(source):
        data = (Path(source) / relative).read_bytes()
        digest.update(relative.as_posix().encode("utf-8") + b"\0")
        digest.update(len(data).to_bytes(8, "big") + data)
    return digest.hexdigest()[:12]


def _entry(name, data):
    info = zipfile.ZipInfo(name, FIXED_DATE)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    return info, data


def archive(source):
    """Bytes of the .skill: a zip of <skill>/..., without evals/, fixed dates, plus VERSION."""
    source = Path(source)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
        for relative in files(source, NOT_ARCHIVED):
            z.writestr(*_entry(f"{source.name}/{relative.as_posix()}", (source / relative).read_bytes()))
        z.writestr(*_entry(f"{source.name}/{VERSION_FILE}", f"{version(source)}\n".encode()))
    return buffer.getvalue()


def _source_errors(sources):
    errors = []
    seen = {}
    for source in sources:
        if source.name in seen:
            errors.append(f"{source.name}: skill name used in both {seen[source.name]}/ and {source.parent.name}/")
        seen[source.name] = source.parent.name
        if (source / VERSION_FILE).exists():
            errors.append(f"{source.parent.name}/{source.name}/{VERSION_FILE}: generated file found in the source")
    return errors


def drift(root=ROOT):
    """List of differences between the sources and the generated copies (empty when in sync)."""
    root = Path(root)
    sources = skills(root)
    found = _source_errors(sources)
    mirror_root = root / MIRROR
    for source in sources:
        mirror = mirror_root / source.name
        expected = set(files(source)) | {Path(VERSION_FILE)}
        present = set(files(mirror)) if mirror.is_dir() else set()
        found += [f"{source.name}/{f}: missing from .claude/skills/" for f in sorted(expected - present)]
        found += [f"{source.name}/{f}: extra in .claude/skills/" for f in sorted(present - expected)]
        for f in sorted(expected & present):
            wanted = (f"{version(source)}\n".encode() if f == Path(VERSION_FILE)
                      else (source / f).read_bytes())
            if (mirror / f).read_bytes() != wanted:
                found.append(f"{source.name}/{f}: content differs")
        package = source.parent / f"{source.name}.skill"
        if not package.is_file() or package.read_bytes() != archive(source):
            found.append(f"{source.parent.name}/{package.name}: out of date")
    names = {s.name for s in sources}
    if mirror_root.is_dir():
        found += [f"{d.name}: orphan folder in .claude/skills/"
                  for d in sorted(mirror_root.iterdir()) if d.is_dir() and d.name not in names]
    return found


def sync(root=ROOT):
    """Rebuild every mirror, VERSION and archive. Returns the synced skill names."""
    root = Path(root)
    sources = skills(root)
    errors = _source_errors(sources)
    if errors:
        raise ValueError("; ".join(errors))
    mirror_root = root / MIRROR
    mirror_root.mkdir(parents=True, exist_ok=True)
    names = {s.name for s in sources}
    for d in mirror_root.iterdir():
        if d.is_dir() and d.name not in names:
            shutil.rmtree(d)
    for source in sources:
        mirror = mirror_root / source.name
        if mirror.exists():
            shutil.rmtree(mirror)
        for relative in files(source):
            (mirror / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / relative, mirror / relative)
        (mirror / VERSION_FILE).write_text(f"{version(source)}\n", encoding="utf-8")
        (source.parent / f"{source.name}.skill").write_bytes(archive(source))
    return [s.name for s in sources]


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="report drift without writing anything")
    if parser.parse_args(argv).check:
        found = drift(root)
        for line in found:
            print(line)
        print("No drift." if not found else "\nRun: python3 tools/sync_skills.py")
        return 1 if found else 0
    names = sync(root)
    print("Synced:", ", ".join(f"{n} ({version(s)})" for n, s in zip(names, skills(root))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
