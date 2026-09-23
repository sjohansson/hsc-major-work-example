#!/usr/bin/env python3
r"""Turn canva-layout.json into connector operation arrays.

The push itself happens over a Canva connector (a conversation-side tool, not
an HTTP API this script could call), so this script's job is to make every
payload mechanical and reproducible from the repo: the agent runs it, passes
the printed JSON to the connector, and nothing about the pages is improvised
at push time.

What this module builds is an abstract operation per element - notes, shape,
image, text, format - which says what has to happen without naming any one
connector's vocabulary. `dialect.py` spells them. That is the seam: a
connector with different op names is a new file under assets/dialects/, not a
change here.

Phases per page:
    elements  everything that creates an element, in paint order. Chunked so
              one connector call stays a sane size. `PAGE_ID` stands in for
              the page id when canva.local.json does not have one yet.
    format    created text carries no styling, so every text element needs a
              follow-up format operation. This phase consumes the element ids
              the elements phase returned (one per text, in order).

Usage:
    canva_sync.py ops --page 01 --phase elements
    canva_sync.py ops --page 01 --phase elements --chunk 2
    canva_sync.py ops --page 01 --phase format --ids ids.txt
    canva_sync.py ops --page 01 --phase format --id-list a,b,c
    canva_sync.py ops --summary [--json]

Asset mapping: canva.local.json ("assets") maps repo image names to Canva
media-library asset ids. Images with no mapping are emitted as a placeholder
rectangle so the push can proceed and the image be dropped in afterwards.
Page ids come from the same file ("pages").
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from . import COMMAND  # noqa: E402
from .config import cfg  # noqa: E402
from .dialect import DialectError  # noqa: E402
from .dialect import load as load_dialect  # noqa: E402

CHUNK_DEFAULT = 40


def circle_path(w: float, h: float) -> str:
    r = min(w, h) / 2
    cx, cy = w / 2, h / 2
    return (f"M {cx - r} {cy} A {r} {r} 0 1 0 {cx + r} {cy} "
            f"A {r} {r} 0 1 0 {cx - r} {cy} Z")


def shape_op(e) -> dict:
    w, h = max(e["w"], 0.5), max(e["h"], 0.5)
    if "path" in e:
        path, vw, vh = e["path"], e["vw"], e["vh"]
    elif e.get("circle"):
        path, vw, vh = circle_path(w, h), w, h
    else:
        path, vw, vh = f"M 0 0 H {w} V {h} H 0 Z", w, h
    op = {"op": "shape", "page": "PAGE_ID",
          "top": e["y"], "left": e["x"], "width": w, "height": h,
          "path": path, "view_box_width": vw, "view_box_height": vh}
    if e.get("fill"):
        op["fill"] = e["fill"]
    if e.get("stroke"):
        op["stroke"] = e["stroke"]
        op["stroke_weight"] = max(e.get("sw", 1), 0.5)
    return op


def placeholder_op(e) -> dict:
    """An unmapped image: a hairline-stroked rectangle where the image goes."""
    placeholder = cfg().placeholder
    return {"op": "shape", "page": "PAGE_ID",
            "top": e["y"], "left": e["x"], "width": e["w"], "height": e["h"],
            "path": f"M 0 0 H {e['w']} V {e['h']} H 0 Z",
            "view_box_width": e["w"], "view_box_height": e["h"],
            "fill": placeholder["fill"], "stroke": placeholder["stroke"],
            "stroke_weight": 1}


def image_op(e, assets) -> dict:
    aid = assets.get(e["asset"])
    if not aid:
        return placeholder_op(e)
    return {"op": "image", "page": "PAGE_ID",
            "asset_id": aid, "alt_text": e["asset"],
            "top": e["y"], "left": e["x"], "width": e["w"], "height": e["h"]}


def text_op(e) -> dict:
    op = {"op": "text", "page": "PAGE_ID", "text": e["text"],
          "top": e["y"], "left": e["x"], "width": max(e["w"], 8)}
    if e.get("rot"):
        op["rotation"] = e["rot"]
    return op


def format_op(e, element_id) -> dict:
    op = {"op": "format", "element_id": element_id,
          "font_size": int(e["size"]), "color": e["color"],
          "text_align": e["align"], "line_height": e["lh"]}
    if e.get("bold"):
        op["font_weight"] = "bold"
    if e.get("italic"):
        op["font_style"] = "italic"
    return op


class OpsError(Exception):
    """A missing layout or an unknown page. The CLI turns this into exit 3."""


def load_layout():
    layout = cfg().layout_json
    if not layout.exists():
        raise OpsError(f"{layout} not found; run `{COMMAND} extract` first")
    return json.loads(layout.read_text(encoding="utf-8"))


def load_page(label):
    for p in load_layout():
        if p["label"] == label:
            return p
    raise OpsError(f"no page {label!r} in {cfg().layout_json}")


def is_page_ground(e, page):
    return (e["kind"] == "shape" and not e.get("stroke")
            and e.get("fill") == page.get("background")
            and e["x"] <= 1 and e["y"] <= 1
            and e["w"] >= page["width"] - 2 and e["h"] >= page["height"] - 2)


def summary(pages, assets, chunk_size):
    per_page = []
    for p in pages:
        els = [e for e in p["elements"] if not is_page_ground(e, p)]
        per_page.append({
            "label": p["label"],
            "ops": len(els),
            "chunks": (len(els) + chunk_size - 1) // chunk_size,
            "texts": sum(1 for e in els if e["kind"] == "text"),
        })
    missing = sorted({e["asset"] for p in pages for e in p["elements"]
                      if e["kind"] == "image" and e["asset"] not in assets})
    return {"chunk_size": chunk_size, "pages": per_page, "unmapped_assets": missing}


def main(argv=None, settings=None):
    settings = settings or cfg()
    ap = argparse.ArgumentParser(prog=f"{COMMAND} ops", description=__doc__.splitlines()[0])
    ap.add_argument("--page")
    ap.add_argument("--phase", choices=("elements", "format"))
    ap.add_argument("--chunk", type=int, help="print only this 1-based chunk")
    ap.add_argument("--chunk-size", type=int, default=CHUNK_DEFAULT)
    ap.add_argument("--ids", help="file of element ids, one per line, in text order, or - for stdin")
    ap.add_argument("--id-list", help="element ids as one comma-separated list")
    ap.add_argument("--dialect", help="override the dialect named in the config")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--json", action="store_true", help="print the summary as JSON")
    args = ap.parse_args(argv)

    assets = settings.asset_ids()
    try:
        spelling = load_dialect(args.dialect or settings.dialect)
    except DialectError as exc:
        print(str(exc), file=sys.stderr)
        return 3

    if args.summary:
        data = summary(load_layout(), assets, args.chunk_size)
        if args.json:
            print(json.dumps(data, indent=2))
            return 0
        for row in data["pages"]:
            print(f"  page {row['label']}: {row['ops']} ops in {row['chunks']} chunk(s), "
                  f"{row['texts']} texts to format", file=sys.stderr)
        if data["unmapped_assets"]:
            names = ", ".join(data["unmapped_assets"])
            print(f"  unmapped assets ({len(data['unmapped_assets'])}): {names}",
                  file=sys.stderr)
        return 0

    if not args.page or not args.phase:
        ap.error("--page and --phase are required unless --summary")
    page = load_page(args.page)
    els = [e for e in page["elements"] if not is_page_ground(e, page)]

    pid = settings.page_id(args.page)

    if args.phase == "elements":
        if not spelling.can("create_elements"):
            print(f"dialect {spelling.name!r} cannot create elements: {spelling.data.get('description', '')}\n"
                  f"publish {settings.export_html} at a public HTTPS URL and import it with "
                  f"the connector's import-from-URL tool instead, then use this dialect to "
                  f"correct text.", file=sys.stderr)
            return 1
        ops = [{"op": "notes", "page": pid, "notes": page.get("notes", "")[:5000]}]
        for e in els:
            if e["kind"] == "shape":
                ops.append(shape_op(e))
            elif e["kind"] == "image":
                ops.append(image_op(e, assets))
            else:
                ops.append(text_op(e))
        ops = [({**o, "page": pid} if o.get("page") == "PAGE_ID" else o) for o in ops]

        # Round everything: sub-pixel precision is noise to Canva and pure
        # payload weight here (a path float can carry 13 decimals).
        def _round_path(d):
            return re.sub(r"-?\d+\.\d{2,}", lambda m: f"{float(m.group(0)):.1f}", d)

        for o in ops:
            for k, v in list(o.items()):
                if isinstance(v, float):
                    o[k] = round(v, 1)
                elif k == "path":
                    o[k] = _round_path(v)
        try:
            rendered = spelling.render_all(ops)
        except DialectError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        chunks = [rendered[i:i + args.chunk_size]
                  for i in range(0, len(rendered), args.chunk_size)]
        if args.chunk:
            print(json.dumps(chunks[args.chunk - 1], separators=(",", ":")))
        else:
            print(f"{len(chunks)} chunk(s) of <= {args.chunk_size} ops; "
                  f"use --chunk N to print one", file=sys.stderr)
    elif args.phase == "format":
        if not spelling.can("format_text"):
            print(f"dialect {spelling.name!r} cannot format text", file=sys.stderr)
            return 1
        if args.id_list:
            ids = [i.strip() for i in args.id_list.split(",") if i.strip()]
        elif args.ids == "-":
            ids = sys.stdin.read().split()
        elif args.ids:
            ids = Path(args.ids).read_text(encoding="utf-8").split()
        else:
            ap.error("--phase format needs --ids or --id-list")
        texts = [e for e in els if e["kind"] == "text"]
        if len(ids) != len(texts):
            print(f"id count {len(ids)} != text count {len(texts)}", file=sys.stderr)
            return 1
        ops = [format_op(e, i) for e, i in zip(texts, ids)]
        try:
            print(json.dumps(spelling.render_all(ops), separators=(",", ":")))
        except DialectError as exc:
            print(str(exc), file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
