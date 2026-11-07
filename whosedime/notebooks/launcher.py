"""Run a Whose Dime notebook of the repo from the small launcher kept in Drive (decision D5).

The Drive copy (`voice_launcher.ipynb`) is only a form plus a few lines
that clone `main` and call `run()`. The real notebook lives here, in
`whosedime/notebooks/`: a fix merged into `main` serves the next run, and
nothing is ever copied into Drive again.

`run()` executes the notebook's code cells in order, in the launcher's
namespace. The cell tagged `settings` sets the defaults; the launcher's
values then override them, so a setting added later to the notebook keeps
its default even in an old launcher. The first cell that fails stops the run.
"""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent


def code_cells(notebook):
    """[(index, source, is_settings)] for the notebook's code cells."""
    nb = json.loads((HERE / notebook).read_text(encoding="utf-8"))
    return [(i, "".join(c["source"]), "settings" in c.get("metadata", {}).get("tags", []))
            for i, c in enumerate(nb["cells"]) if c["cell_type"] == "code"]


def commit():
    """Short hash, date and subject of the commit being run."""
    r = subprocess.run(["git", "-C", str(HERE), "log", "-1", "--format=%h %ad %s", "--date=short"],
                       capture_output=True, text=True)
    return r.stdout.strip() or "unknown"


def run(notebook, settings, namespace=None):
    """Execute the notebook; settings = the launcher's form, namespace = its globals()."""
    namespace = {} if namespace is None else namespace
    namespace["REPO_READY"] = True  # the launcher already cloned the repo: the notebook does not clone it again
    namespace.setdefault("COMMIT", commit())
    try:
        transform = get_ipython().transform_cell  # noqa: F821 (Colab: "!command", "%magic")
    except NameError:
        transform = None
    for i, source, is_settings in code_cells(notebook):
        if transform:
            source = transform(source)
        exec(compile(source, f"<{notebook}, cell {i}>", "exec"), namespace)
        if is_settings:
            namespace.update(settings)
    return namespace
