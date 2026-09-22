"""Settings for every canva-sync step: discovery, validation and the write guard.

Two files drive the pipeline. Neither lives inside this bundle, because both
describe the repository being synced, not the tool:

  canva.config.json        committed. Which deck to flatten, where its stylesheet
                           and assets are, the page size, the prop values the
                           renderer would produce, the webfonts, and the colours
                           the ops generator needs.
  canva.local.json         ignored by git. The Canva design id, the page id map
                           and the media-library asset id map for one account.
                           assets/canva.local.template.json is the template.

Discovery order, first hit wins:

  1. --config PATH
  2. the CANVA_CONFIG environment variable
  3. canva.config.json, then design-system/canva.config.json, at the working
     directory and at each parent of it

Every path in the config resolves against the directory the config was found in,
so that directory is the repository root as far as this tool is concerned.

Generated output goes under `output_dir` and nowhere else. `write_text` enforces
that; `save_local` is the single deliberate exception, because refreshing Canva
ids is the one thing the pipeline writes back outside the build folder. Nothing
here ever writes to the deck: the sync is one way, repo to Canva.
"""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_NAME = "canva.config.json"
SEARCH_RELATIVE = (CONFIG_NAME, f"design-system/{CONFIG_NAME}")

DEFAULT_REWRITE_CLASSES = {
    "structural": ["evidence-table", "spec-table", "plate-grid", "grain-labels"],
    "grain_label": "grain-labels",
}


class ConfigError(Exception):
    """Config missing, unreadable or invalid. The CLI turns this into exit 3."""


@dataclass
class Settings:
    """One loaded canva.config.json, with every path already resolved."""

    path: Path
    root: Path
    data: dict
    local: dict = field(default_factory=dict)

    # -- paths ---------------------------------------------------------------

    @property
    def deck_dir(self) -> Path:
        return self.root / self.data.get("deck_dir", "design-system")

    @property
    def deck(self) -> Path:
        return self.deck_dir / self.data["deck"]

    @property
    def deck_css(self) -> Path:
        return self.deck_dir / self.data.get("deck_css", "deck.css")

    @property
    def assets_dir(self) -> Path:
        return self.deck_dir / self.data.get("assets_dir", "assets")

    @property
    def output_dir(self) -> Path:
        return self.root / self.data.get("output_dir", "build/canva")

    @property
    def local_path(self) -> Path:
        return self.root / self.data.get("local_ids", "canva.local.json")

    @property
    def export_html(self) -> Path:
        return self.output_dir / "canva-import-rev.html"

    @property
    def export_pdf(self) -> Path:
        return self.output_dir / "canva-import-A3.pdf"

    @property
    def layout_json(self) -> Path:
        return self.output_dir / "canva-layout.json"

    @property
    def verify_dir(self) -> Path:
        return self.output_dir / "verify"

    # -- values --------------------------------------------------------------

    @property
    def title(self) -> str:
        return self.data.get("title", "Folio")

    @property
    def page_mm(self) -> tuple[float, float]:
        w, h = self.data.get("page_mm", [297.0, 420.0])
        return float(w), float(h)

    @property
    def canva_px(self) -> tuple[int, int]:
        w, h = self.data.get("canva_px", [1123, 1588])
        return int(w), int(h)

    @property
    def background(self) -> str:
        return self.data.get("background", "#FEFBFC")

    @property
    def pattern_fill(self) -> str:
        """Flat tone a hatched pattern-piece fill collapses to."""
        return self.data.get("pattern_fill", "#F5EFE2")

    @property
    def props(self) -> dict:
        return dict(self.data.get("props", {}))

    @property
    def thumbnail(self) -> dict:
        return self.data.get("thumbnail", {"text": "F", "fill": "#888888"})

    @property
    def placeholder(self) -> dict:
        return self.data.get("placeholder", {"fill": "#EEEEEE", "stroke": "#888888"})

    @property
    def known_residuals(self) -> dict:
        return {k: float(v) for k, v in self.data.get("known_residuals", {}).items()}

    @property
    def dialect(self) -> str:
        return self.data.get("dialect", "claude-canva-connector")

    @property
    def rewrite_classes(self) -> dict:
        merged = dict(DEFAULT_REWRITE_CLASSES)
        merged.update(self.data.get("rewrite_classes", {}))
        return merged

    @property
    def head_fonts(self) -> str:
        families = "&".join(f"family={f}" for f in self.data.get("google_fonts", []))
        if not families:
            return ""
        return (
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous">\n'
            f'<link href="https://fonts.googleapis.com/css2?{families}&display=swap" rel="stylesheet">'
        )

    # -- helpers -------------------------------------------------------------

    def deck_uri(self) -> str:
        """file:/// URI of the deck folder, trailing slash, for repointing ./ refs."""
        return "file:///" + str(self.deck_dir).replace("\\", "/") + "/"

    def deck_css_uri(self) -> str:
        return "file:///" + str(self.deck_css).replace("\\", "/")

    def ensure_output_dir(self) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return self.output_dir

    def page_id(self, label: str) -> str:
        return self.local.get("pages", {}).get(label, "PAGE_ID")

    def asset_ids(self) -> dict:
        return dict(self.local.get("assets", {}))

    # -- the one-way guard ---------------------------------------------------

    def writable(self, path: Path, extra: Path | None = None) -> bool:
        """Where the sync is allowed to write.

        Never inside the deck folder, whatever else is asked: that folder is
        the source of truth and the sync only ever reads it. Otherwise: under
        output_dir, the local id file, or a destination the caller named on the
        command line (--out, --keep)."""
        p = Path(path).resolve()
        deck_dir = self.deck_dir.resolve()
        if p == deck_dir or deck_dir in p.parents:
            return False
        for base in (self.output_dir.resolve(), *([Path(extra).resolve()] if extra else ())):
            if p == base or base in p.parents:
                return True
        return p == self.local_path.resolve()

    def write_text(self, path: Path, text: str, *, extra: Path | None = None) -> Path:
        """Write inside the sync's own territory, or refuse.

        Every step writes through here, so a bug that aimed an output at the
        deck is a loud error rather than a silent edit to the source of truth."""
        path = Path(path)
        if not self.writable(path, extra):
            raise ConfigError(
                f"refusing to write outside {self.output_dir}: {path}\n"
                "the Canva sync is one way; it never writes into the deck"
            )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def save_local(self, data: dict) -> Path:
        """The one write outside output_dir: refreshed Canva ids."""
        self.local = data
        self.local_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return self.local_path


# -- discovery and loading ---------------------------------------------------


def discover(explicit: str | None = None) -> Path:
    """Locate canva.config.json. Raises ConfigError when there is none."""
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if not p.exists():
            raise ConfigError(f"no config at {p}")
        return p
    env = os.environ.get("CANVA_CONFIG")
    if env:
        p = Path(env).expanduser().resolve()
        if not p.exists():
            raise ConfigError(f"CANVA_CONFIG points at a missing file: {p}")
        return p
    here = Path.cwd().resolve()
    for base in (here, *here.parents):
        for rel in SEARCH_RELATIVE:
            c = base / rel
            if c.exists():
                return c.resolve()
    raise ConfigError(
        f"no {CONFIG_NAME} found in {here} or any parent.\n"
        "copy assets/canva.config.template.json to the repository root, "
        "or name one with --config or CANVA_CONFIG"
    )


REQUIRED = ("deck",)
TYPES = {
    "deck": str,
    "deck_dir": str,
    "deck_css": str,
    "assets_dir": str,
    "output_dir": str,
    "local_ids": str,
    "title": str,
    "background": str,
    "pattern_fill": str,
    "dialect": str,
    "props": dict,
    "thumbnail": dict,
    "placeholder": dict,
    "known_residuals": dict,
    "rewrite_classes": dict,
    "ornament": dict,
    "google_fonts": list,
    "page_mm": list,
    "canva_px": list,
}


def validate_schema(data: dict) -> list[str]:
    """Check the config by hand against assets/canva.config.schema.json.

    Hand-written so the bundle needs no JSON-schema dependency. Returns the
    problems; an empty list means the config is usable."""
    problems = []
    if not isinstance(data, dict):
        return ["config must be a JSON object"]
    for key in REQUIRED:
        if not data.get(key):
            problems.append(f"missing required key {key!r}")
    for key, value in data.items():
        want = TYPES.get(key)
        if want is None:
            problems.append(f"unknown key {key!r}")
        elif not isinstance(value, want):
            problems.append(f"{key!r} must be {want.__name__}, got {type(value).__name__}")
    for key in ("page_mm", "canva_px"):
        v = data.get(key)
        if isinstance(v, list) and len(v) != 2:
            problems.append(f"{key!r} must hold exactly two numbers")
    for label, pct in (data.get("known_residuals") or {}).items():
        if not isinstance(pct, (int, float)):
            problems.append(f"known_residuals[{label!r}] must be a number")
    return problems


def load(explicit: str | None = None) -> Settings:
    """Discover, read, validate and resolve. Raises ConfigError on any failure."""
    path = discover(explicit)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"cannot read {path}: {exc}") from exc
    problems = validate_schema(data)
    if problems:
        joined = "\n  ".join(problems)
        raise ConfigError(f"{path} is not a valid canva-sync config:\n  {joined}")
    cfg = Settings(path=path, root=path.parent, data=data)
    if cfg.local_path.exists():
        try:
            cfg.local = json.loads(cfg.local_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ConfigError(f"cannot read {cfg.local_path}: {exc}") from exc
    else:
        cfg.local = {"design_id": "", "pages": {}, "assets": {}}
    return cfg


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


# -- the active settings -----------------------------------------------------
#
# The CLI loads the config once and activates it; every step module reads it
# back through cfg(). One object, one load, no import-time file access.

CURRENT: Settings | None = None


def activate(settings: Settings) -> Settings:
    global CURRENT
    CURRENT = settings
    return settings


def cfg() -> Settings:
    if CURRENT is None:  # pragma: no cover - programming error, not user error
        raise ConfigError("no canva-sync configuration has been loaded")
    return CURRENT
