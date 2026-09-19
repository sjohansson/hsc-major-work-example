"""Paths and settings shared by every Canva pipeline step.

Two files under design-system/ drive the pipeline:

  canva.config.json        committed. Which deck to flatten, its page size,
                           the prop values renderVals() would produce, the
                           webfonts, and the colours the ops generator needs.
  canva.local.json         ignored by git. The Canva design id, the page id
                           map and the media-library asset id map for one
                           account. canva.local.example.json is the template.

Generated output goes under build/ (also ignored), never into design-system/.
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
DS = REPO / "design-system"
CONFIG_PATH = DS / "canva.config.json"
LOCAL_PATH = DS / "canva.local.json"


def _load(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


CFG = _load(CONFIG_PATH, None)
if CFG is None:
    raise SystemExit(f"missing {CONFIG_PATH}")

LOCAL = _load(LOCAL_PATH, {"design_id": "", "pages": {}, "assets": {}})

DECK = DS / CFG["deck"]
DECK_CSS = DS / CFG.get("deck_css", "deck.css")
TITLE = CFG.get("title", "Folio")

PAGE_W_MM, PAGE_H_MM = (float(v) for v in CFG.get("page_mm", [297.0, 420.0]))
CANVA_W, CANVA_H = (int(v) for v in CFG.get("canva_px", [1123, 1588]))
BACKGROUND = CFG.get("background", "#FEFBFC")

PROPS = dict(CFG.get("props", {}))
THUMBNAIL = CFG.get("thumbnail", {"text": "F", "fill": "#888888"})
ORNAMENT = CFG.get("ornament", {})
PLACEHOLDER = CFG.get("placeholder", {"fill": "#EEEEEE", "stroke": "#888888"})
KNOWN_RESIDUALS = {k: float(v) for k, v in CFG.get("known_residuals", {}).items()}

BUILD = REPO / CFG.get("output_dir", "build/canva")
EXPORT_HTML = BUILD / "canva-import-rev.html"
EXPORT_PDF = BUILD / "canva-import-A3.pdf"
LAYOUT_JSON = BUILD / "canva-layout.json"
VERIFY_DIR = BUILD / "verify"

_families = "&".join(f"family={f}" for f in CFG.get("google_fonts", []))
HEAD_FONTS = (
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous">\n'
    f'<link href="https://fonts.googleapis.com/css2?{_families}&display=swap" rel="stylesheet">'
) if _families else ""


def ensure_build_dir() -> Path:
    BUILD.mkdir(parents=True, exist_ok=True)
    return BUILD


def ds_uri() -> str:
    """file:/// URI of design-system/, with a trailing slash, for repointing ./ refs."""
    return "file:///" + str(DS).replace("\\", "/") + "/"


def find_chrome(explicit: str | None = None) -> str | None:
    """A headless-capable Chromium: explicit path, CHROME_PATH, PATH, then the usual Windows installs."""
    if explicit:
        return explicit
    env = os.environ.get("CHROME_PATH")
    if env and Path(env).exists():
        return env
    for name in ("chrome", "chromium", "google-chrome", "msedge", "microsoft-edge"):
        p = shutil.which(name)
        if p:
            return p
    for base in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)")):
        if not base:
            continue
        for rel in (r"Google\Chrome\Application\chrome.exe", r"Microsoft\Edge\Application\msedge.exe"):
            c = Path(base) / rel
            if c.exists():
                return str(c)
    return None


def page_id(label: str) -> str:
    return LOCAL.get("pages", {}).get(label, "PAGE_ID")


def asset_ids() -> dict:
    return dict(LOCAL.get("assets", {}))


def save_local(data: dict) -> None:
    LOCAL_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
