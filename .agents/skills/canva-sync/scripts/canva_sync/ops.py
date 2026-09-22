#!/usr/bin/env python3
r"""Turn canva-layout.json into edit-design operation arrays.

The push itself happens over the Canva MCP connector (a conversation-side
tool, not an HTTP API this script could call), so this script's job is to
make every payload mechanical and reproducible from the repo: the agent runs
it, pastes the printed JSON into `edit-design`, and nothing about the pages
is improvised at push time.

Phases per page:
    elements  ops that create everything: insert_shape / insert_fill /
              add_text, in paint order. Chunked so one edit-design call
              stays a sane size. `PAGE_ID` is a placeholder for the id the
              add_page result returns.
    format    add_text carries no styling, so every text element needs a
              follow-up format_text. This phase consumes the element ids
              the elements phase returned (one per add_text, in order) and
              emits the format ops.

Usage:
    canva_sync.py ops --page 01 --phase elements
    canva_sync.py ops --page 01 --phase elements --chunk 2
    canva_sync.py ops --page 01 --phase format --ids ids.txt
    canva_sync.py ops --summary

Asset mapping: canva.local.json ("assets") maps repo image
names to Canva media-library asset ids. Images with no mapping are emitted as
a placeholder rect so the push can proceed and the image be dropped in
afterwards. Page ids come from the same file ("pages"); without it every op
carries the literal PAGE_ID for the caller to substitute.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from . import COMMAND  # noqa: E402
from .config import cfg  # noqa: E402

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
    op = {"type": "insert_shape", "page_id": "PAGE_ID",
          "top": e["y"], "left": e["x"], "width": w, "height": h,
          "path": path, "view_box_width": vw, "view_box_height": vh}
    if e.get("fill"):
        op["color"] = e["fill"]
    if e.get("stroke"):
        op["stroke_color"] = e["stroke"]
        op["stroke_weight"] = max(e.get("sw", 1), 0.5)
    return op


def ornament_ops(e):
    """The house mark drawn as two shapes: an oval in the primary colour beside
    a ringed disc in the secondary. Used wherever the ornament asset named in
    canva.config.json appears and no asset id is mapped for it."""
    ornament = cfg().data.get("ornament", {})
    h = e["h"]
    rose_d = h * 0.9
    cy = e["y"] + e["h"] / 2
    sage_w, sage_h = h * 0.75, h * 0.42
    return [
        {"type": "insert_shape", "page_id": "PAGE_ID",
         "top": cy - sage_h / 2, "left": e["x"], "width": sage_w, "height": sage_h,
         "path": circle_path(sage_w, sage_h) if sage_w == sage_h else
                 f"M 0 {sage_h/2} A {sage_w/2} {sage_h/2} 0 1 0 {sage_w} {sage_h/2} "
                 f"A {sage_w/2} {sage_h/2} 0 1 0 0 {sage_h/2} Z",
         "view_box_width": sage_w, "view_box_height": sage_h,
         "color": ornament.get("primary", "#888888"), "rotation": -28},
        {"type": "insert_shape", "page_id": "PAGE_ID",
         "top": cy - rose_d / 2, "left": e["x"] + sage_w + h * 0.2,
         "width": rose_d, "height": rose_d,
         "path": circle_path(rose_d, rose_d),
         "view_box_width": rose_d, "view_box_height": rose_d,
         "color": ornament.get("secondary", "#AAAAAA"),
         "stroke_color": ornament.get("secondary_stroke", "#666666"), "stroke_weight": 1},
    ]


def image_op(e, assets) -> dict:
    placeholder = cfg().placeholder
    aid = assets.get(e["asset"])
    if not aid:
        # placeholder rect; the asset name rides in a hairline-stroked frame
        return {"type": "insert_shape", "page_id": "PAGE_ID",
                "top": e["y"], "left": e["x"], "width": e["w"], "height": e["h"],
                "path": f"M 0 0 H {e['w']} V {e['h']} H 0 Z",
                "view_box_width": e["w"], "view_box_height": e["h"],
                "color": placeholder["fill"], "stroke_color": placeholder["stroke"],
                "stroke_weight": 1}
    return {"type": "insert_fill", "page_id": "PAGE_ID", "asset_type": "image",
            "asset_id": aid, "alt_text": e["asset"],
            "top": e["y"], "left": e["x"], "width": e["w"], "height": e["h"]}


def text_op(e) -> dict:
    op = {"type": "add_text", "page_id": "PAGE_ID", "text": e["text"],
          "top": e["y"], "left": e["x"], "width": max(e["w"], 8)}
    if e.get("rot"):
        op["rotation"] = e["rot"]
    return op


def format_op(e, element_id) -> dict:
    f = {"font_size": int(e["size"]), "color": e["color"],
         "text_align": e["align"], "line_height": e["lh"]}
    if e.get("bold"):
        f["font_weight"] = "bold"
    if e.get("italic"):
        f["font_style"] = "italic"
    return {"type": "format_text", "element_id": element_id, "formatting": f}


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


def main(argv=None, settings=None):
    settings = settings or cfg()
    ap = argparse.ArgumentParser(prog=f"{COMMAND} ops", description=__doc__.splitlines()[0])
    ap.add_argument("--page")
    ap.add_argument("--phase", choices=("elements", "format"))
    ap.add_argument("--chunk", type=int, help="print only this 1-based chunk")
    ap.add_argument("--chunk-size", type=int, default=CHUNK_DEFAULT)
    ap.add_argument("--ids", help="file of element ids, one per line, in add_text order")
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args(argv)

    assets = settings.asset_ids()

    if args.summary:
        pages = load_layout()
        for p in pages:
            els = [e for e in p["elements"] if not is_page_ground(e, p)]
            texts = sum(1 for e in els if e["kind"] == "text")
            n_chunks = (len(els) + args.chunk_size - 1) // args.chunk_size
            print(f"  page {p['label']}: {len(els)} ops in {n_chunks} chunk(s), "
                  f"{texts} texts to format")
        missing = sorted({e["asset"] for p in pages for e in p["elements"]
                          if e["kind"] == "image" and e["asset"] not in assets})
        if missing:
            print(f"  unmapped assets ({len(missing)}): {', '.join(missing)}")
        return 0

    if not args.page or not args.phase:
        ap.error("--page and --phase are required unless --summary")
    page = load_page(args.page)
    els = [e for e in page["elements"] if not is_page_ground(e, page)]

    pid = settings.page_id(args.page)

    if args.phase == "elements":
        ops = [{"type": "replace_speaker_notes", "page_id": pid,
                "notes": page.get("notes", "")[:5000]}]
        for e in els:
            if e["kind"] == "shape":
                ops.append(shape_op(e))
            elif e["kind"] == "image":
                if e["asset"] == settings.data.get("ornament", {}).get("asset") \
                        and e["asset"] not in assets:
                    ops.extend(ornament_ops(e))
                else:
                    ops.append(image_op(e, assets))
            else:
                ops.append(text_op(e))
        ops = [({**o, "page_id": pid} if o.get("page_id") == "PAGE_ID" else o) for o in ops]

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
        chunks = [ops[i:i + args.chunk_size] for i in range(0, len(ops), args.chunk_size)]
        if args.chunk:
            print(json.dumps(chunks[args.chunk - 1], separators=(",", ":")))
        else:
            print(f"{len(chunks)} chunk(s) of <= {args.chunk_size} ops; "
                  f"use --chunk N to print one", file=sys.stderr)
    elif args.phase == "format":
        ids = Path(args.ids).read_text(encoding="utf-8").split()
        texts = [e for e in els if e["kind"] == "text"]
        if len(ids) != len(texts):
            print(f"id count {len(ids)} != text count {len(texts)}", file=sys.stderr)
            return 1
        ops = [format_op(e, i) for e, i in zip(texts, ids)]
        print(json.dumps(ops, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
