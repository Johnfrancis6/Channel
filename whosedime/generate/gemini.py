"""The Gemini API calls of the Whose Dime generation pipeline (S11), and what they share.

- `Client`: one POST to the Interactions API (images and clips), retries, never prints
  the key. The key comes from `GEMINI_API_KEY` (a Colab secret) or, with no variable,
  from the network proxy of a cloud session. Tests pass a fake `transport`.
- `prompts(folder)`: the preamble, the `scene_NNN` and `anim_NNN` prompts of
  `03_scenes.md`, read with the checker's own parser (one parser).
- `Ledger`: one JSON line per paid call in `generate/ledger.jsonl` (model, price, file,
  seconds, prompt hash), the money spent so far, and the budget gate (D18).
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "whosedime" / "common"))
import checker  # noqa: E402

SETTINGS = json.loads((HERE / "settings.json").read_text(encoding="utf-8"))


class ApiError(RuntimeError):
    pass


class BudgetError(RuntimeError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha12(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


# ------------------------------------------------------------------ prompts of 03_scenes.md
def style_preamble(preamble, settings=SETTINGS):
    """The chat preamble without its chat sentences (reply OK, wait...): the style only."""
    sentences = re.split(r"(?<=[.!?])\s+", preamble.strip())
    drop = re.compile(settings["preamble_drop"])
    return " ".join(s for s in sentences if not drop.search(s)).strip()


def read_preamble(raw):
    """The quoted lines after the **Preamble** label of `## Gemini prompts`."""
    lines, on = [], False
    for line in raw.splitlines():
        if re.match(r"^\s*\*\*Preamble\*\*", line):
            on = True
            continue
        if on:
            if line.lstrip().startswith(">"):
                lines.append(line.lstrip()[1:].strip())
            elif lines and line.strip():
                break
    return " ".join(lines).strip()


def prompts(folder):
    """{'preamble': style text, 'scene': {n: prompt}, 'anim': {n: prompt}, 'types': {n: type}}."""
    path = Path(folder) / checker.SETTINGS["files"]["scenes"]
    raw = checker.norm(path.read_text(encoding="utf-8"))
    rows, error = checker.scene_table(raw)
    if error:
        raise ValueError(f"03_scenes.md: {error[1]}")
    found = checker.scene_prompts(raw)
    pre = read_preamble(raw)
    if not pre:
        raise ValueError("03_scenes.md: no **Preamble** under ## Gemini prompts")
    return {"preamble": style_preamble(pre),
            "scene": {n: t for n, (_, t) in found["scene"].items() if t},
            "anim": {n: t for n, (_, t) in found["anim"].items() if t},
            "types": {int(r["n"]): r["type"].strip() for _, r in rows if r["n"].strip().isdigit()}}


# ------------------------------------------------------------------ the HTTP client
def urllib_transport(method, url, headers, body, timeout):
    """(status, bytes) of one HTTPS request; the system proxy and CA settings apply."""
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


class Client:
    def __init__(self, settings=SETTINGS, transport=None, key=None, sleep=time.sleep):
        self.s = settings["api"]
        self.transport = transport or urllib_transport
        self.key = key if key is not None else os.environ.get(self.s["key_env"], "")
        self.sleep = sleep

    def _headers(self):
        h = {"Content-Type": "application/json", "Api-Revision": self.s["revision"]}
        if self.key:
            h["x-goog-api-key"] = self.key
        return h

    def _scrub(self, text):
        return text.replace(self.key, "<key>") if self.key else text

    def request(self, method, path, payload=None, timeout=60):
        """JSON of a 2xx answer; retries 429 and 5xx; an ApiError names the status, never the key."""
        url = path if path.startswith("http") else f"{self.s['base']}/{path.lstrip('/')}"
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        waits = list(self.s["retry_wait_s"])[: self.s["retries"]]
        for attempt in range(len(waits) + 1):
            try:
                status, data = self.transport(method, url, self._headers(), body, timeout)
            except OSError as e:  # network error: retried like a 503
                status, data = 0, str(e).encode()
            if 200 <= status < 300:
                return data
            if status in (0, 429, 500, 502, 503, 504) and attempt < len(waits):
                self.sleep(waits[attempt])
                continue
            raise ApiError(f"HTTP {status}: {self._scrub(data[:400].decode('utf-8', 'replace'))}")
        raise ApiError("unreachable")

    def interact(self, payload, timeout):
        return json.loads(self.request("POST", "interactions", payload, timeout))

    def check_key(self):
        """True if the API answers the free model list (no money spent)."""
        try:
            self.request("GET", "models?pageSize=1", timeout=20)
            return True
        except ApiError:
            return False


def media_parts(answer, kind):
    """The model's output parts of a kind ('image', 'video') in an Interactions answer:
    the REST `steps` list, or the SDK-style `outputs` / `output_<kind>` fields."""
    parts = []
    for step in answer.get("steps", []) or []:
        if step.get("type") in ("model_output", "output", None):
            parts += [c for c in step.get("content", []) or [] if c.get("type") == kind]
    parts += [c for c in answer.get("outputs", []) or [] if c.get("type") == kind]
    single = answer.get(f"output_{kind}")
    if single:
        parts.append(single)
    return parts


def usage(answer):
    u = answer.get("usage") or answer.get("usage_metadata") or answer.get("usageMetadata") or {}
    return {k: v for k, v in u.items() if isinstance(v, (int, float))}


def jpeg_b64(path, max_px):
    """An image file as base64 JPEG, its long side at most max_px (a reference costs less)."""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im.thumbnail((max_px, max_px), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=92)
    return base64.b64encode(buf.getvalue()).decode("ascii")


# ------------------------------------------------------------------ ledger and budget (D18)
class Ledger:
    def __init__(self, folder, settings=SETTINGS):
        f = settings["files"]
        self.path = Path(folder) / f["dir"] / f["ledger"]

    def lines(self):
        if not self.path.exists():
            return []
        return [json.loads(l) for l in self.path.read_text(encoding="utf-8").splitlines() if l.strip()]

    def spent(self):
        return round(sum(l.get("usd", 0) for l in self.lines() if l.get("ok")), 4)

    def add(self, **line):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(dict({"at": now()}, **line), ensure_ascii=False) + "\n")


class Budget:
    """Test mode: at most N new pieces of a kind, whatever the money. Full mode: the ledger's
    total plus the next call must stay within the amount Franco approved."""

    def __init__(self, ledger, approved_usd=None, test_limit=None):
        self.ledger, self.approved, self.test_limit, self.made = ledger, approved_usd, test_limit, 0

    def allow(self, usd):
        if self.test_limit is not None:
            if self.made >= self.test_limit:
                raise BudgetError(f"test budget reached ({self.test_limit})")
            return
        if not self.approved:
            raise BudgetError("no approved budget: run --test, or pass --approved-usd once Franco agreed")
        if self.ledger.spent() + usd > self.approved + 1e-9:
            raise BudgetError(f"approved ${self.approved:.2f} would be passed "
                              f"(spent ${self.ledger.spent():.2f}, next ${usd:.2f})")

    def count(self):
        self.made += 1
