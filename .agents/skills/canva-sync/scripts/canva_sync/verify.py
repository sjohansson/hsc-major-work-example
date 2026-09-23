#!/usr/bin/env python3
r"""Prove the flattened Canva export still renders as the deck does.

The export in `<output_dir>/canva-import-rev.html` is built by
`canva_sync.py build`, which re-implements the deck's cascade in
Python and then rewrites four constructs Canva cannot read. Both halves of
that are places a mistake would be silent: a selector that fails to match
drops a rule, a mis-reduced `calc()` moves a box by a millimetre, a table
converted to grid loses a hairline. None of it shows up as an error.

So this checks the only thing that matters: render each page twice in the
same browser - once as the real deck against the real stylesheet, once as
the flattened export - and diff the two images pixel for pixel. Anything the
flattening changed shows up as ink where the reference has none.

    canva_sync.py verify
    canva_sync.py verify --scale 2 --keep build/canva/verify-2x

Pages are compared at 96 dpi by default, which puts an A3 sheet at
1123 x 1588 px and makes a hairline about half a pixel; `--scale 2` doubles
that when a diff needs looking at rather than counting. Antialiasing along
type edges is real and unavoidable, so a channel difference of 16/255 or
less is not counted - what is being looked for is displaced or missing
geometry, not resampling noise.

Exit status is 1 if any page differs by more than --tolerance per cent of
its pixels, so this can gate a commit.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from . import COMMAND  # noqa: E402
from .build import SECTION_RE, substitute_props  # noqa: E402
from .config import cfg, find_chrome  # noqa: E402

PAGE_RE = re.compile(r'(?s)(<div data-document-role="page".*?)(?=<div data-document-role="page"|</body>)')
LABEL_RE = re.compile(r'data-label="([^"]*)"')

# Known residuals live in canva.config.json ("known_residuals": per page
# label, in per cent). They record a difference that is real, understood and
# not a regression. The one the example folio ships with:
#
#   12  The evaluation text is a two-column multicol whose third paragraph
#       runs across the break, and the block carries `text-wrap: pretty`.
#       Pretty adjusts a paragraph's last few lines by looking ahead to its
#       end. In the deck that end is down in column two, so the column-one
#       fragment is broken without any adjustment; once the fragment is a
#       paragraph of its own it has an end of its own, and Chrome pulls
#       "did," up onto the previous line. Same words, same column, same
#       height - two lines break one word differently. Setting `text-wrap:
#       wrap` on the fragment does not restore it (greedy and pretty agree
#       on the half), and pinning the track width to the measured multicol
#       column does not either: the look-ahead is genuinely gone with the
#       text that left. Canva re-flows text on import in any case.
#
# Every other page is held to --tolerance, so a real regression still fails.


def reference_pages(warnings):
    """Every deck page (plus the cover partial) as the browser really draws it."""
    settings = cfg()
    out = []
    raw = settings.deck.read_text(encoding="utf-8")
    for m in SECTION_RE.finditer(raw):
        label = (LABEL_RE.search(m.group(1)) or [None, "?"])[1]
        body = substitute_props(m.group(2), warnings)
        body = re.sub(r'(?<=["\'(])\./', settings.deck_uri(), body)
        out.append((label, body))
    return out


def export_pages(path: Path):
    raw = path.read_text(encoding="utf-8")
    body = raw.split("<body>", 1)[1]
    out = []
    for m in PAGE_RE.finditer(body):
        chunk = m.group(1)
        label = (LABEL_RE.search(chunk) or [None, "?"])[1]
        # The export's ./assets/ refs are relative to the deck folder;
        # make them absolute so the temp file resolves them.
        chunk = re.sub(r'(?<=["\'(])\./', cfg().deck_uri(), chunk)
        out.append((label, chunk))
    return out


def wrap(body: str) -> str:
    settings = cfg()
    page_w, page_h = settings.page_mm
    return (
        '<!DOCTYPE html><html><head><meta charset="utf-8">\n'
        f"{settings.head_fonts}\n"
        f'<link rel="stylesheet" href="{settings.deck_css_uri()}">\n'
        "<style>html,body{margin:0;padding:0;background:#fff}\n"
        f".sheet{{position:relative;overflow:hidden;width:{page_w}mm;height:{page_h}mm}}</style>\n"
        f'</head><body><div class="sheet">{body}</div></body></html>'
    )


def wrap_export(body: str) -> str:
    """No deck.css: the whole point is that the export needs no stylesheet."""
    return (
        '<!DOCTYPE html><html><head><meta charset="utf-8">\n'
        f"{cfg().head_fonts}\n"
        "<style>html,body{margin:0;padding:0;background:#fff}\n"
        "a{color:#1A1A1A;text-decoration:underline}</style>\n"
        f"</head><body>{body}</body></html>"
    )


def shoot(chrome, html_path: Path, png_path: Path, scale: float):
    page_w, page_h = cfg().page_mm
    w = int(round(page_w / 25.4 * 96 * scale))
    h = int(round(page_h / 25.4 * 96 * scale))
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        "--default-background-color=FFFFFFFF",
        f"--force-device-scale-factor={scale}",
        f"--window-size={int(round(page_w / 25.4 * 96))},{int(round(page_h / 25.4 * 96))}",
        "--virtual-time-budget=15000",
        "--run-all-compositor-stages-before-draw",
        f"--screenshot={png_path}",
        html_path.as_uri(),
    ]
    subprocess.run(cmd, capture_output=True, timeout=180)
    return w, h


def verify(export_path: Path | None = None, chrome=None, scale: float = 1.0,
           tolerance: float = 0.35, keep: Path | None = None):
    from PIL import Image, ImageChops

    settings = cfg()
    export_path = Path(export_path) if export_path else settings.export_html
    residuals = settings.known_residuals
    chrome = chrome or find_chrome()
    if not chrome:
        print("  ! no Chrome found; cannot verify")
        return 1

    warnings: list[str] = []
    refs = dict(reference_pages(warnings))
    outs = export_pages(export_path)
    if not outs:
        print("  ! export has no pages")
        return 1

    workdir = Path(keep) if keep else settings.verify_dir
    if not settings.writable(workdir, extra=workdir):
        print(f"  ! refusing to write renders to {workdir}", file=sys.stderr)
        return 2
    workdir.mkdir(parents=True, exist_ok=True)

    worst = 0.0
    failed = []
    print(f"  comparing {len(outs)} pages at {scale}x -> {workdir}")
    for label, chunk in outs:
        if label not in refs:
            print(f"  ! page {label}: no reference section")
            failed.append(label)
            continue
        ref_html = workdir / f"ref-{label}.html"
        out_html = workdir / f"out-{label}.html"
        ref_png = workdir / f"ref-{label}.png"
        out_png = workdir / f"out-{label}.png"
        settings.write_text(ref_html, wrap(refs[label]), extra=workdir)
        settings.write_text(out_html, wrap_export(chunk), extra=workdir)
        shoot(chrome, ref_html, ref_png, scale)
        shoot(chrome, out_html, out_png, scale)
        if not ref_png.exists() or not out_png.exists():
            print(f"  ! page {label}: screenshot failed")
            failed.append(label)
            continue

        a = Image.open(ref_png).convert("RGB")
        b = Image.open(out_png).convert("RGB")
        if a.size != b.size:
            b = b.resize(a.size)
        diff = ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v > 16 else 0)
        n = sum(diff.histogram()[255:])
        pct = 100.0 * n / (a.size[0] * a.size[1])
        worst = max(worst, pct)
        limit = max(tolerance, residuals.get(label, 0.0))
        bbox = diff.getbbox()
        over = pct > limit
        if over:
            flag = "DIFF"
        elif pct > tolerance:
            flag = "known"
        else:
            flag = "ok "
        extra = f"  bbox={bbox}" if bbox and over else ""
        print(f"  {flag:<5} page {label:<5} {pct:6.3f}% differing{extra}")
        if over:
            failed.append(label)
            diff.save(workdir / f"diff-{label}.png")

    for w in warnings:
        print(f"  ! {w}")
    if failed:
        print(f"  ! pages over tolerance: {', '.join(failed)} (worst {worst:.3f}%)")
        return 1
    known = ", ".join(sorted(residuals)) or "none"
    print(f"  every page within {tolerance}%, except the known residual on {known}")
    return 0


def main(argv=None, settings=None):
    settings = settings or cfg()
    ap = argparse.ArgumentParser(prog=f"{COMMAND} verify", description=__doc__.splitlines()[0])
    ap.add_argument("--export", type=Path, default=None)
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--tolerance", type=float, default=0.35)
    ap.add_argument("--chrome")
    ap.add_argument("--keep", type=Path, help="write the renders here instead of <output_dir>/verify")
    args = ap.parse_args(argv)
    return verify(args.export, find_chrome(args.chrome), args.scale, args.tolerance, args.keep)


if __name__ == "__main__":
    sys.exit(main())
