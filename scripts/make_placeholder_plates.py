#!/usr/bin/env python3
"""Write one placeholder SVG per image slot listed in design-system/assets/plates.json.

Each placeholder is drawn at the slot's printed size in millimetres: a paper
ground, a hairline frame, the caption, the size, and a tone label. The deck
and the production items reference these files by name, so the layout, the
print proof and the Canva export all work before any real artwork exists.
Drop a real image in under the same filename (SVG, or change the extension
in the deck) and the placeholder is gone.

    python scripts/make_placeholder_plates.py            # write all
    python scripts/make_placeholder_plates.py --force    # overwrite real files too

By default a file is only written if it is missing or already a placeholder
(it carries the data-placeholder attribute), so real artwork is never
clobbered.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

REPO = Path(__file__).resolve().parent.parent
ASSETS = REPO / "design-system" / "assets"
MANIFEST = ASSETS / "plates.json"

TONES = {
    # ground, frame, type
    "mono": ("#E9E7E4", "#6A6A6A", "#3A3A3A"),
    "sketch": ("#F7F5F1", "#8A8A8A", "#3A3A3A"),
    "photo": ("#DCDCDC", "#4A4A4A", "#2A2A2A"),
    "flat": ("#FFFFFF", "#1A1A1A", "#1A1A1A"),
}


def svg_for(p: dict) -> str:
    w, h = float(p["w"]), float(p["h"])
    ground, frame, ink = TONES.get(p.get("tone", "mono"), TONES["mono"])
    cap = escape(p.get("caption", p["file"]))
    size = f"{w:g} x {h:g} mm"
    # Type sizes scale with the slot so a 35 mm sketch and a 173 mm flat both read.
    fs = max(2.6, min(w, h) * 0.075)
    small = fs * 0.75
    cx, cy = w / 2, h / 2
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {h:g}" width="{w:g}mm" height="{h:g}mm" data-placeholder="true">',
        f'  <rect x="0" y="0" width="{w:g}" height="{h:g}" fill="{ground}" />',
        f'  <rect x="0.4" y="0.4" width="{w - 0.8:g}" height="{h - 0.8:g}" fill="none" stroke="{frame}" stroke-width="0.25" />',
        f'  <path d="M0 0 L{w:g} {h:g} M{w:g} 0 L0 {h:g}" stroke="{frame}" stroke-width="0.12" opacity="0.5" />',
        f'  <rect x="{cx - w * 0.42:g}" y="{cy - fs * 2.2:g}" width="{w * 0.84:g}" height="{fs * 4.4:g}" fill="{ground}" opacity="0.92" />',
        f'  <text x="{cx:g}" y="{cy - fs * 0.35:g}" text-anchor="middle" font-family="PT Serif, Georgia, serif" '
        f'font-size="{fs:g}" fill="{ink}">{cap}</text>',
        f'  <text x="{cx:g}" y="{cy + fs * 1.05:g}" text-anchor="middle" font-family="PT Serif, Georgia, serif" '
        f'font-size="{small:g}" fill="{ink}" opacity="0.8">placeholder, {size}</text>',
        "</svg>",
    ]
    return "\n".join(lines) + "\n"


def is_placeholder(path: Path) -> bool:
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:600]
    except OSError:
        return False
    return 'data-placeholder="true"' in head


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--force", action="store_true", help="overwrite files that are not placeholders")
    args = ap.parse_args(argv)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    ASSETS.mkdir(parents=True, exist_ok=True)
    written = skipped = 0
    for p in manifest["plates"]:
        out = ASSETS / p["file"]
        if out.exists() and not args.force and not is_placeholder(out):
            print(f"  keep   {out.name} (real artwork)")
            skipped += 1
            continue
        out.write_text(svg_for(p), encoding="utf-8")
        written += 1
        print(f"  wrote  {out.name}  {p['w']:g} x {p['h']:g} mm  page {p.get('page', '?')}")
    print(f"  {written} written, {skipped} kept")
    return 0


if __name__ == "__main__":
    sys.exit(main())
