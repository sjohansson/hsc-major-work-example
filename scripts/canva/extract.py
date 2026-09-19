#!/usr/bin/env python3
r"""Measure the flattened export into a Canva-native element list.

`build/canva/canva-import-rev.html` is the pixel-faithful representation of
the deck; this script turns it into `build/canva/canva-layout.json` - per
page, an ordered list of elements in the vocabulary the Canva connector's
`edit-design` tool actually speaks:

    shape  -> insert_shape   (SVG path + fill / stroke, page px)
    image  -> insert_fill    (asset name; the pusher maps names to asset ids)
    text   -> add_text + format_text (content, box, size, weight, colour...)

Nothing is guessed: headless Chrome renders each page at exactly the Canva
page size (1123 x 1588 px, which is A3 at 96 dpi) and every element's box,
computed style and paint order are read off the live layout. Document order
is paint order, so pushing the list in order reproduces the stacking.

What cannot cross:
  - Font families. `format_text` has no family parameter, so text lands in
    Canva's default face and Fraunces/PT Serif must be applied from the
    brand kit in Canva. Sizes, weights, italics, colours and alignment DO
    cross, so the layout holds.
  - Hatched fills (the pattern-piece plates): flattened to their cream base
    tone. Recorded in the element as `"pattern": true`.
  - object-fit: cover crops: the image box crosses, the crop can be refined
    with crop_media afterwards.

Usage:
    python scripts/canva.py extract            # writes build/canva/canva-layout.json
    python scripts/canva.py extract --page 07  # one page, to stdout
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from .config import (  # noqa: E402
    BACKGROUND,
    CANVA_H,
    CANVA_W,
    HEAD_FONTS,
    PAGE_H_MM,
    PAGE_W_MM,
    ds_uri,
    ensure_build_dir,
    find_chrome,
)
from .config import EXPORT_HTML as DEFAULT_OUT  # noqa: E402
from .config import LAYOUT_JSON as OUT_JSON  # noqa: E402

PAGE_RE = re.compile(
    r'(?s)(<div data-document-role="page".*?)(?=<div data-document-role="page"|</body>)'
)
LABEL_RE = re.compile(r'data-label="([^"]*)"')
NOTES_RE = re.compile(r'data-speaker-notes="([^"]*)"')

# The walker runs inside the rendered page. Everything positional is scaled
# into the 1123 x 1588 Canva frame before it leaves the browser.
WALKER_JS = r"""
Promise.all([
  document.fonts.ready,
  new Promise(function (r) {
    if (document.readyState === 'complete') { r(); } else { window.addEventListener('load', r); }
  })
]).then(function () {
  var sheet = document.querySelector('.sheet');
  var srect = sheet.getBoundingClientRect();
  var SX = %CANVA_W% / srect.width, SY = %CANVA_H% / srect.height;
  var els = [];

  function rel(r) {
    return { x: (r.left - srect.left) * SX, y: (r.top - srect.top) * SY,
             w: r.width * SX, h: r.height * SY };
  }
  function isInline(el) {
    var d = getComputedStyle(el).display;
    return d === 'inline' || d === 'inline-block';
  }
  function blockChildWithText(el) {
    return Array.prototype.some.call(el.children, function (c) {
      return !isInline(c) && c.textContent.trim() !== '';
    });
  }
  function rotationOf(cs) {
    var t = cs.transform;
    if (!t || t === 'none') return 0;
    var m = t.match(/matrix\(([-0-9.e]+),\s*([-0-9.e]+)/);
    if (!m) return 0;
    return Math.round(Math.atan2(parseFloat(m[2]), parseFloat(m[1])) * 180 / Math.PI);
  }

  function walk(el) {
    var cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return;
    var tag = el.tagName;
    var r = el.getBoundingClientRect();
    var box = rel(r);

    if (tag === 'IMG') {
      // object-fit: contain draws a smaller rect than the box; compute it so
      // the pushed image lands where the ink lands, undistorted.
      var fit = cs.objectFit || 'fill';
      var draw = box;
      if (fit === 'contain' && el.naturalWidth > 0) {
        var s = Math.min(box.w / el.naturalWidth, box.h / el.naturalHeight);
        var dw = el.naturalWidth * s, dh = el.naturalHeight * s;
        draw = { x: box.x + (box.w - dw) / 2, y: box.y + (box.h - dh) / 2, w: dw, h: dh };
      }
      els.push({ kind: 'image', src: el.getAttribute('src') || '', fit: fit,
                 x: draw.x, y: draw.y, w: draw.w, h: draw.h });
      return;
    }
    if (tag === 'svg') {
      els.push({ kind: 'svg', x: box.x, y: box.y, w: box.w, h: box.h,
                 html: el.outerHTML });
      return;
    }

    var bg = cs.backgroundColor;
    var hasBg = bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent';
    var hasPattern = cs.backgroundImage && cs.backgroundImage !== 'none';
    var bw = [cs.borderTopWidth, cs.borderRightWidth, cs.borderBottomWidth,
              cs.borderLeftWidth].map(parseFloat);
    var solidBorder = cs.borderTopStyle === 'solid' && bw[0] > 0;

    // Border-triangle device (the masthead wedge): zero content height, fat
    // borders. The painted shape is the bottom border's mitred polygon.
    if (el.clientHeight === 0 && bw[2] > 0.5 && bw[3] > 0.5 && !el.textContent.trim()) {
      var L = bw[3] * SX, B = bw[2] * SY, W = box.w;
      els.push({ kind: 'shape', x: box.x, y: box.y, w: W, h: B,
                 path: 'M 0 ' + B + ' L ' + L + ' 0 L ' + W + ' 0 L ' + W + ' ' + B + ' Z',
                 vw: W, vh: B, fill: cs.borderBottomColor, stroke: null, sw: 0 });
      return;
    }

    var sides = [cs.borderTopStyle, cs.borderRightStyle, cs.borderBottomStyle,
                 cs.borderLeftStyle].map(function (st, i) {
      return st === 'solid' && bw[i] > 0;
    });
    var fullBorder = sides[0] && sides[1] && sides[2] && sides[3];
    if ((hasBg || hasPattern || fullBorder) && box.w > 0.4 && box.h > 0.4) {
      var isRoot = el.parentElement === sheet;
      if (!isRoot) {  // page ground becomes the Canva page background instead
        els.push({ kind: 'shape', x: box.x, y: box.y, w: box.w, h: box.h,
                   rect: true,
                   fill: hasBg ? bg : (hasPattern ? 'PATTERN' : null),
                   pattern: hasPattern,
                   radiusPct: (cs.borderTopLeftRadius || '').indexOf('%') >= 0
                     ? parseFloat(cs.borderTopLeftRadius) : 0,
                   stroke: fullBorder ? cs.borderTopColor : null,
                   sw: fullBorder ? bw[0] * SX : 0 });
      }
    }
    // Partial borders (the footer's top rule, the credits' top rule) are
    // painted as their own hairline rects, one per drawn side.
    if (!fullBorder) {
      var edges = [
        [sides[0], box.x, box.y, box.w, bw[0] * SY, cs.borderTopColor],
        [sides[2], box.x, box.y + box.h - bw[2] * SY, box.w, bw[2] * SY, cs.borderBottomColor],
        [sides[3], box.x, box.y, bw[3] * SX, box.h, cs.borderLeftColor],
        [sides[1], box.x + box.w - bw[1] * SX, box.y, bw[1] * SX, box.h, cs.borderRightColor]
      ];
      edges.forEach(function (ed) {
        if (ed[0]) {
          els.push({ kind: 'shape', x: ed[1], y: ed[2], w: ed[3], h: ed[4],
                     rect: true, fill: ed[5], stroke: null, sw: 0 });
        }
      });
    }

    var text = el.textContent.replace(/\s+/g, ' ').trim();
    if (text && !blockChildWithText(el)) {
      var rot = rotationOf(cs);
      var b = box;
      if (rot !== 0) {
        // report the unrotated box: width is the layout width
        b = { x: box.x, y: box.y, w: r.height * SX, h: r.width * SY };
      }
      els.push({ kind: 'text', x: b.x, y: b.y, w: b.w, h: b.h, text: text,
                 tag: tag,
                 size: parseFloat(cs.fontSize) * SX,
                 weight: cs.fontWeight, italic: cs.fontStyle === 'italic',
                 color: cs.color, align: cs.textAlign,
                 lh: Math.round(parseFloat(cs.lineHeight) / parseFloat(cs.fontSize) * 100) / 100,
                 caps: cs.textTransform === 'uppercase',
                 family: (cs.fontFamily.split(',')[0] || '').replace(/"/g, ''),
                 rot: rot });
      return;
    }
    Array.prototype.forEach.call(el.children, walk);
  }

  Array.prototype.forEach.call(sheet.children, walk);
  document.documentElement.innerHTML =
    '<body><pre id="layout">' +
    JSON.stringify(els).replace(/[^ -~]/g, function (c) {
      return String.fromCharCode(92) + 'u' + ('000' + c.charCodeAt(0).toString(16)).slice(-4);
    }).replace(/&/g, '&amp;').replace(/</g, '&lt;') +
    '</pre></body>';
});
"""


def rgb_to_hex(c: str) -> str | None:
    if not c:
        return None
    if c.startswith("#"):
        return c.upper()
    m = re.match(r"rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)", c)
    if not m:
        return None
    if m.group(4) is not None and float(m.group(4)) == 0:
        return None
    return "#{:02X}{:02X}{:02X}".format(*(int(round(float(m.group(i)))) for i in (1, 2, 3)))


def svg_to_path(html: str, box_w: float, box_h: float):
    """One concatenated path in the svg's own viewBox units, plus stroke info.

    Circles become two arcs (insert_shape takes M/L/H/V/C/S/A/Z only).
    Sub-paths merge under one M...Z each, which keeps the care symbols and
    the tag outline one element apiece.
    """
    vb = re.search(r'viewBox="([\d.\s-]+)"', html)
    vw, vh = (24.0, 24.0)
    if vb:
        parts = vb.group(1).split()
        vw, vh = float(parts[2]), float(parts[3])
    paths = re.findall(r'<path[^>]*\sd="([^"]+)"', html)
    for cx, cy, rr in re.findall(r'<circle[^>]*cx="([\d.]+)"[^>]*cy="([\d.]+)"[^>]*r="([\d.]+)"', html):
        cx, cy, rr = float(cx), float(cy), float(rr)
        paths.append(
            f"M {cx - rr} {cy} A {rr} {rr} 0 1 0 {cx + rr} {cy} "
            f"A {rr} {rr} 0 1 0 {cx - rr} {cy} Z"
        )
    for x, y, w, h in re.findall(r'<rect[^>]*x="([\d.]+)"[^>]*y="([\d.]+)"[^>]*width="([\d.]+)"[^>]*height="([\d.]+)"', html):
        x, y, w, h = float(x), float(y), float(w), float(h)
        paths.append(f"M {x} {y} H {x + w} V {y + h} H {x} Z")
    stroke = re.search(r'stroke="(#[0-9A-Fa-f]{6})"', html)
    sw = re.search(r'stroke-width="([\d.]+)"', html)
    return {
        "path": " ".join(paths),
        "vw": vw,
        "vh": vh,
        "stroke": stroke.group(1).upper() if stroke else None,
        "sw": float(sw.group(1)) * (box_w / vw) if sw else 0,
    }


def post_process(raw_els):
    """Browser output -> the element list the pusher consumes."""
    out = []
    for e in raw_els:
        k = e["kind"]
        base = {q: round(e[q], 1) for q in ("x", "y", "w", "h")}
        if k == "image":
            name = e["src"].rsplit("/", 1)[-1]
            out.append({"kind": "image", **base, "asset": name, "fit": e["fit"]})
        elif k == "svg":
            info = svg_to_path(e["html"], e["w"], e["h"])
            if not info["path"]:
                continue
            out.append({"kind": "shape", **base, "path": info["path"],
                        "vw": info["vw"], "vh": info["vh"], "fill": None,
                        "stroke": info["stroke"], "sw": round(info["sw"], 2)})
        elif k == "shape":
            fill = rgb_to_hex(e.get("fill")) if e.get("fill") not in (None, "PATTERN") else None
            if e.get("pattern"):
                fill = "#F5EFE2"  # hatched plates flatten to their base tone
            stroke = rgb_to_hex(e.get("stroke"))
            if fill is None and stroke is None and "path" not in e:
                continue
            el = {"kind": "shape", **base, "fill": fill, "stroke": stroke,
                  "sw": round(e.get("sw", 0), 2)}
            if e.get("pattern"):
                el["pattern"] = True
            if "path" in e:  # pre-built polygon (masthead wedge)
                el.update(path=e["path"], vw=round(e["vw"], 1), vh=round(e["vh"], 1))
            elif e.get("radiusPct", 0) >= 40:  # the corner dots are circles
                el["circle"] = True
            out.append(el)
        elif k == "text":
            t = e["text"]
            if e.get("caps"):
                t = t.upper()
            if e.get("tag") == "LI":
                t = "• " + t
            w = e["weight"]
            bold = (w in ("bold", "bolder")) or (str(w).isdigit() and int(w) >= 600)
            out.append({"kind": "text", **base, "text": t,
                        "size": max(1, round(e["size"])),
                        "bold": bold, "italic": e["italic"],
                        "color": rgb_to_hex(e["color"]) or "#1A1A1A",
                        "align": {"left": "start", "start": "start", "center": "center",
                                  "right": "end", "end": "end", "justify": "start"
                                  }.get(e["align"], "start"),
                        "lh": min(2.5, max(0.5, e.get("lh") or 1.3)),
                        "family": e.get("family", ""), "rot": e.get("rot", 0)})
    return out


def extract(chrome, only_page=None):
    raw = DEFAULT_OUT.read_text(encoding="utf-8")
    body = raw.split("<body>", 1)[1]
    pages = []
    for m in PAGE_RE.finditer(body):
        chunk = m.group(1)
        label = (LABEL_RE.search(chunk) or [None, "?"])[1]
        notes = (NOTES_RE.search(chunk) or [None, ""])[1]
        # data-speaker-notes is raw attribute text: entities never met a parser.
        import html as _html
        notes = _html.unescape(notes)
        pages.append((label, notes, chunk))
    pages.sort(key=lambda t: t[0])  # file is reversed; JSON is reading order
    if only_page:
        pages = [p for p in pages if p[0] == only_page]

    result = []
    js = WALKER_JS.replace("%CANVA_W%", str(CANVA_W)).replace("%CANVA_H%", str(CANVA_H))
    with tempfile.TemporaryDirectory() as td:
        for label, notes, chunk in pages:
            chunk = re.sub(r'(?<=["\'(])\./', ds_uri(), chunk)
            doc = (
                '<!DOCTYPE html><html><head><meta charset="utf-8">\n'
                f"{HEAD_FONTS}\n"
                "<style>html,body{margin:0;padding:0;background:#fff}"
                f".sheet{{position:relative;overflow:hidden;width:{PAGE_W_MM}mm;height:{PAGE_H_MM}mm}}</style>"
                f'</head><body><div class="sheet">{chunk}</div>'
                f"<script>{js}</script></body></html>"
            )
            src = Path(td) / f"measure-{label}.html"
            src.write_text(doc, encoding="utf-8")
            res = subprocess.run(
                [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
                 "--hide-scrollbars", "--virtual-time-budget=20000",
                 "--run-all-compositor-stages-before-draw", "--dump-dom",
                 src.as_uri()],
                capture_output=True, text=True, timeout=180,
                encoding="utf-8", errors="replace",
            )
            mm = re.search(r'<pre id="layout">(.*?)</pre>', res.stdout or "", re.S)
            if not mm:
                print(f"  ! page {label}: no layout result")
                continue
            payload = mm.group(1).replace("&lt;", "<").replace("&amp;", "&")
            els = post_process(json.loads(payload))
            counts = {}
            for e in els:
                counts[e["kind"]] = counts.get(e["kind"], 0) + 1
            print(f"  page {label}: {len(els)} elements  {counts}")
            result.append({"label": label, "notes": notes,
                           "width": CANVA_W, "height": CANVA_H,
                           "background": BACKGROUND, "elements": els})
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(prog="canva.py extract", description=__doc__.splitlines()[0])
    ap.add_argument("--page", help="extract one page and print to stdout")
    ap.add_argument("--chrome")
    args = ap.parse_args(argv)
    if not DEFAULT_OUT.exists():
        sys.exit(f"{DEFAULT_OUT} not found; run `python scripts/canva.py build` first")
    chrome = find_chrome(args.chrome)
    if not chrome:
        sys.exit("no Chrome found")
    pages = extract(chrome, args.page)
    if args.page:
        print(json.dumps(pages, indent=1))
    else:
        ensure_build_dir()
        OUT_JSON.write_text(json.dumps(pages, indent=1), encoding="utf-8")
        print(f"  wrote {OUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
