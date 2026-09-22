#!/usr/bin/env python3
r"""Flatten the folio deck into the single self-contained file Canva can import.

WHY THIS EXISTS
---------------
The deck named in `design-system/canva.config.json` is the source of truth for
the twelve A3 pages, and it is written the way a stylesheet-backed document should
be: classes, custom properties, pseudo-elements, `calc()`, real `<table>`s.
Canva's HTML import understands none of that. It reads a document as a flat
tree of boxes with literal inline styles, so everything the browser resolves
at render time has to be resolved here instead.

Hand-maintaining that second copy is what went wrong last time: the previous
`canva-import-rev.html` was written by hand and then the deck moved on without
it. By the time it was regenerated it had drifted a whole design revision -
no area colour theming, no 60 degree chapter transition, the old CSS
oval-and-circle ornament instead of the drawn rose, the 0.4 mm masthead rule,
missing page 6 grain lines and dimensions, missing the page 7 true-size tag
reverse, missing the page 8 timeline, missing the page 2 image credits, and
several paragraphs of superseded copy. This script makes the export a build
product: edit the deck, re-run this, and the two cannot drift again.

WHAT IT DOES
------------
  1.  Lifts each `<section>` out of the deck, exactly as scripts/preview.ps1
      does, and substitutes the values renderVals() would have produced.
  2.  Runs the deck.css cascade in Python - selector matching, specificity,
      source order, the element's own inline style, then `!important`
      declarations last - so every element ends up with one literal style
      attribute and no class. Selectors may use descendant and child
      combinators, `:first-child`, `:last-child` and `::before`/`::after`.
      Anything else (`+`, `~`, other pseudo-classes) stops the build with
      an error rather than silently dropping the rule.
  3.  Resolves custom properties and `calc()` to literals. `--area-border`
      on a page root becomes the chapter's actual hex; `calc(--band-h *
      0.57735)` becomes 15.0111mm. What cannot reduce (`calc(100% - 3.6mm)`)
      is left as a calc with the variables already substituted out.
  4.  Materialises `::before` / `::after` as real divs. Every pseudo-element
      in deck.css is either absolutely positioned or a flex item, so a div in
      the same position renders identically.
  5.  Rewrites the four constructs Canva cannot take (see below).
  6.  Emits the pages in reverse order behind `data-document-role="page"`
      wrappers, which is the shape Canva's importer reads.

THE FOUR REWRITES
-----------------
  clip-path      The 60 degree masthead transition is two clipped rectangles.
                 Rebuilt as an opaque rectangle plus a CSS border triangle,
                 which is the same geometry out of borders alone. The swing
                 tag's cut corner on page 7 is dropped instead: the tag's
                 ground and the page's ground are both #FEFBFC, so the clip
                 removes nothing visible, and the drawn outline SVG over it
                 is what shows the shape.
  <table>        Collapsed-border tables become CSS grid. Each cell is a grid
                 item holding an absolutely positioned fill (background plus
                 its right and bottom hairline) under a relatively positioned
                 content box - a Canva element is a shape or a text box, not
                 both, so the two jobs are split onto two divs. The table's
                 own top and left hairlines move to the grid container.
  column-count   Multi-column text becomes two explicit grid columns. The
                 break point is not guessed: Chrome renders the real deck and
                 reports the first character that lands in the second column,
                 and the copy is split there. Splitting on a line boundary
                 means both halves break identically to the multicol original.
  writing-mode   The page 6 grain labels are `vertical-rl`. Re-emitted as a
                 horizontal box rotated 90 degrees about its top-left corner,
                 positioned from the measured geometry so the ink lands in
                 the same place.

NO GLOBAL RESET. The export deliberately does not ship `* { box-sizing:
border-box }`. The deck assumes the initial content-box and states
`box-sizing` per element where it needs it (`.page`, `.masthead`, `.m2-*`,
`.plate-num`, and inline on the page 6 drawing plates). A blanket reset would
silently shrink every bordered box by its border and the export would stop
matching the print proof.

IMAGES. `./assets/x.png` is repointed to `./assets/x.jpg` wherever a
same-named JPEG exists beside it, so a compressed upload copy can sit next to
a print master. Assets with no twin, which today is every plate (they are
SVG placeholders from assets/plates.json), are left alone.

USAGE
-----
    python scripts/canva.py build                 # build the export
    python scripts/canva.py build --verify        # build, then diff every page
                                                  # against the real deck in
                                                  # headless Chrome
    python scripts/canva.py build --order fwd     # pages 1..12 file order
    python scripts/canva.py build --pdf           # also print a true-size A3 PDF

Output lands in build/canva/ (ignored by git). Settings come from
design-system/canva.config.json; see canva/config.py.

Requires: beautifulsoup4, tinycss2 (and Pillow for --verify).
    python -m pip install beautifulsoup4 tinycss2 pillow
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import tinycss2
except ImportError:  # pragma: no cover - dependency guard
    sys.exit("tinycss2 is required: python -m pip install tinycss2")
try:
    from bs4 import BeautifulSoup, Comment, NavigableString, Tag
except ImportError:  # pragma: no cover - dependency guard
    sys.exit("beautifulsoup4 is required: python -m pip install beautifulsoup4")


from .config import (  # noqa: E402
    DECK,
    DECK_CSS,
    DS,
    EXPORT_HTML,
    EXPORT_PDF,
    HEAD_FONTS,
    PAGE_H_MM,
    PAGE_W_MM,
    PROPS,
    THUMBNAIL,
    TITLE,
    ds_uri,
    ensure_build_dir,
    find_chrome,
)

DEFAULT_OUT = EXPORT_HTML


# ---------------------------------------------------------------------------
# Stylesheet
# ---------------------------------------------------------------------------
class Rule:
    """One selector out of one CSS rule, with its declarations."""

    __slots__ = ("compounds", "pseudo", "spec", "order", "decls", "important", "text")

    def __init__(self, compounds, pseudo, spec, order, decls, text, important=None):
        self.compounds = compounds  # list of dicts, ancestor-first
        self.pseudo = pseudo        # None | 'before' | 'after'
        self.spec = spec            # (a, b, c)
        self.order = order
        self.decls = decls          # list of (prop, value), normal weight
        self.important = important or []  # list of (prop, value) flagged !important
        self.text = text


def parse_compound(part: str):
    """`td:first-child` -> {'tag': 'td', 'classes': [], 'pseudo': ['first-child']}."""
    tag = None
    classes = []
    pseudo_classes = []
    i = 0
    m = re.match(r"[a-zA-Z][\w-]*", part)
    if m:
        tag = m.group(0).lower()
        i = m.end()
    while i < len(part):
        ch = part[i]
        m = re.match(r"[.:]{1,2}[\w-]+", part[i:])
        if not m:
            raise ValueError(f"unsupported selector fragment: {part!r}")
        token = m.group(0)
        i += m.end()
        if ch == ".":
            classes.append(token[1:])
        else:
            pseudo_classes.append(token.lstrip(":"))
    return {"tag": tag, "classes": classes, "pseudo": pseudo_classes}


def parse_selector(sel: str):
    """Descendant and child combinators and compounds - all deck.css needs.

    Each compound carries `child`: True when it must be the direct child of
    the compound before it (`a > b`), False for a plain descendant (`a b`).
    """
    sel = sel.strip()
    pseudo = None
    m = re.search(r"::(before|after)$", sel)
    if m:
        pseudo = m.group(1)
        sel = sel[: m.start()]
    if "+" in sel or "~" in sel:
        raise ValueError(f"unsupported combinator in {sel!r}")
    compounds = []
    child = False
    for tok in re.split(r"(\s*>\s*|\s+)", sel):
        tok = tok.strip()
        if not tok:
            continue
        if tok == ">":
            child = True
            continue
        comp = parse_compound(tok)
        comp["child"] = child
        child = False
        compounds.append(comp)
    if child or not compounds:
        raise ValueError(f"malformed selector {sel!r}")
    a = 0
    b = sum(len(c["classes"]) + len(c["pseudo"]) for c in compounds)
    c = sum(1 for x in compounds if x["tag"]) + (1 if pseudo else 0)
    return compounds, pseudo, (a, b, c)


def load_stylesheet(path: Path):
    """Return (rules, root_vars). `:root` is lifted out as the initial env."""
    rules = []
    root_vars = {}
    order = 0
    sheet = tinycss2.parse_stylesheet(
        path.read_text(encoding="utf-8"), skip_comments=True, skip_whitespace=True
    )
    for node in sheet:
        if node.type != "qualified-rule":
            continue
        prelude = tinycss2.serialize(node.prelude).strip()
        decls = []
        important = []
        for d in tinycss2.parse_declaration_list(node.content, skip_whitespace=True):
            if d.type != "declaration":
                continue
            pair = (d.lower_name, tinycss2.serialize(d.value).strip())
            (important if d.important else decls).append(pair)
        for sel in [s.strip() for s in prelude.split(",") if s.strip()]:
            order += 1
            if sel == ":root":
                root_vars.update({k: v for k, v in decls if k.startswith("--")})
                continue
            # State selectors have no meaning in a static export.
            if ":hover" in sel:
                continue
            compounds, pseudo, spec = parse_selector(sel)
            rules.append(Rule(compounds, pseudo, spec, order, decls, sel, important))
    return rules, root_vars


def el_classes(el: Tag):
    c = el.get("class")
    if not c:
        return ()
    return tuple(c) if isinstance(c, list) else tuple(str(c).split())


def element_siblings(el: Tag):
    parent = el.parent
    if parent is None:
        return [el]
    return [c for c in parent.children if isinstance(c, Tag)]


def compound_matches(el: Tag, comp) -> bool:
    if comp["tag"] and el.name.lower() != comp["tag"]:
        return False
    classes = el_classes(el)
    for cls in comp["classes"]:
        if cls not in classes:
            return False
    for pc in comp["pseudo"]:
        sibs = element_siblings(el)
        if pc == "first-child":
            if not sibs or sibs[0] is not el:
                return False
        elif pc == "last-child":
            if not sibs or sibs[-1] is not el:
                return False
        else:
            return False
    return True


def rule_matches(el: Tag, ancestors, rule: Rule) -> bool:
    """Match right to left. `pool` is the ancestor chain nearest-first, so a
    child combinator pins the next compound to pool[0]; a descendant
    combinator may skip ahead."""
    if not compound_matches(el, rule.compounds[-1]):
        return False
    pool = list(reversed(ancestors))
    need_child = rule.compounds[-1]["child"]
    for comp in reversed(rule.compounds[:-1]):
        if need_child:
            if not pool or not compound_matches(pool.pop(0), comp):
                return False
        else:
            while pool:
                cand = pool.pop(0)
                if compound_matches(cand, comp):
                    break
            else:
                return False
        need_child = comp["child"]
    return True


# ---------------------------------------------------------------------------
# Values: var() substitution and calc() reduction
# ---------------------------------------------------------------------------
LENGTH_TO_MM = {"mm": 1.0, "cm": 10.0, "in": 25.4, "pt": 25.4 / 72.0, "px": 25.4 / 96.0}


def fmt_num(x: float) -> str:
    s = f"{x:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def split_top_level(s: str, sep: str = ","):
    out, depth, cur = [], 0, []
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == sep and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    return out


class UnresolvedVar(Exception):
    pass


def substitute_vars(value: str, env: dict, depth: int = 0) -> str:
    if depth > 12:
        raise UnresolvedVar("var() recursion")
    while True:
        idx = value.find("var(")
        if idx == -1:
            return value
        depth_paren = 0
        end = None
        for j in range(idx + 3, len(value)):
            if value[j] == "(":
                depth_paren += 1
            elif value[j] == ")":
                depth_paren -= 1
                if depth_paren == 0:
                    end = j
                    break
        if end is None:
            raise UnresolvedVar(f"unbalanced var() in {value!r}")
        inner = value[idx + 4 : end]
        parts = split_top_level(inner, ",")
        name = parts[0].strip()
        fallback = ",".join(parts[1:]).strip() if len(parts) > 1 else None
        if name in env:
            repl = substitute_vars(env[name], env, depth + 1)
        elif fallback is not None:
            repl = substitute_vars(fallback, env, depth + 1)
        else:
            raise UnresolvedVar(name)
        value = value[:idx] + repl + value[end + 1 :]


CALC_TOKEN = re.compile(r"\s*([-+*/()]|[0-9]*\.?[0-9]+(?:[a-zA-Z%]+)?)")


class Dim:
    """A calc() sum: a scalar plus a coefficient per unit."""

    def __init__(self, units=None):
        self.units = dict(units or {})

    @staticmethod
    def number(x, unit=""):
        return Dim({unit: x})

    def add(self, other, sign=1):
        out = Dim(self.units)
        for u, v in other.units.items():
            out.units[u] = out.units.get(u, 0.0) + sign * v
        return out

    def scale(self, k):
        return Dim({u: v * k for u, v in self.units.items()})

    def is_scalar(self):
        return set(self.units) <= {""}

    def render(self):
        units = {u: v for u, v in self.units.items() if abs(v) > 1e-9}
        if not units:
            return "0"
        if len(units) == 1:
            u, v = next(iter(units.items()))
            return fmt_num(v) + u
        return None


def reduce_calc(expr: str):
    """Evaluate a calc() body to a single value, or None if it cannot reduce."""
    tokens = []
    pos = 0
    while pos < len(expr):
        m = CALC_TOKEN.match(expr, pos)
        if not m:
            if expr[pos].isspace():
                pos += 1
                continue
            return None
        tokens.append(m.group(1))
        pos = m.end()
    idx = 0

    def peek():
        return tokens[idx] if idx < len(tokens) else None

    def parse_primary():
        nonlocal idx
        t = peek()
        if t is None:
            raise ValueError
        if t == "(":
            idx += 1
            v = parse_sum()
            if peek() != ")":
                raise ValueError
            idx += 1
            return v
        if t == "-":
            idx += 1
            return parse_primary().scale(-1)
        if t == "+":
            idx += 1
            return parse_primary()
        idx += 1
        m = re.fullmatch(r"([0-9]*\.?[0-9]+)([a-zA-Z%]*)", t)
        if not m:
            raise ValueError
        num, unit = float(m.group(1)), m.group(2)
        if unit in LENGTH_TO_MM:
            return Dim.number(num * LENGTH_TO_MM[unit], "mm")
        return Dim.number(num, unit)

    def parse_product():
        nonlocal idx
        v = parse_primary()
        while peek() in ("*", "/"):
            op = peek()
            idx += 1
            rhs = parse_primary()
            if op == "*":
                if v.is_scalar():
                    v = rhs.scale(v.units.get("", 0.0))
                elif rhs.is_scalar():
                    v = v.scale(rhs.units.get("", 0.0))
                else:
                    raise ValueError
            else:
                if not rhs.is_scalar():
                    raise ValueError
                v = v.scale(1.0 / rhs.units.get("", 1.0))
        return v

    def parse_sum():
        nonlocal idx
        v = parse_product()
        while peek() in ("+", "-"):
            op = peek()
            idx += 1
            v = v.add(parse_product(), 1 if op == "+" else -1)
        return v

    try:
        v = parse_sum()
    except (ValueError, IndexError):
        return None
    if idx != len(tokens):
        return None
    return v.render()


def resolve_calcs(value: str) -> str:
    out = value
    while True:
        idx = out.find("calc(")
        if idx == -1:
            return out
        depth = 0
        end = None
        for j in range(idx + 4, len(out)):
            if out[j] == "(":
                depth += 1
            elif out[j] == ")":
                depth -= 1
                if depth == 0:
                    end = j
                    break
        if end is None:
            return out
        inner = out[idx + 5 : end]
        inner = resolve_calcs(inner)
        reduced = reduce_calc(inner)
        if reduced is None:
            # Cannot fold (percentages against an unknown box). Keep the calc,
            # but with the variables already substituted out of it.
            head, tail = out[:idx], out[end + 1 :]
            out = head + "calc(" + inner + ")" + tail
            nxt = out.find("calc(", idx + 5)
            if nxt == -1:
                return out
            prefix, rest = out[: idx + 5], out[idx + 5 :]
            return prefix + resolve_calcs(rest)
        out = out[:idx] + reduced + out[end + 1 :]


def parse_inline_style(text: str):
    decls = []
    for chunk in split_top_level(text or "", ";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        if ":" not in chunk:
            continue
        prop, _, val = chunk.partition(":")
        decls.append((prop.strip().lower(), val.strip()))
    return decls


# `inset` is a 2021 shorthand. Every renderer understands the four longhands.
def expand_inset(prop, value):
    parts = value.split()
    if len(parts) == 1:
        t = r = b = l = parts[0]
    elif len(parts) == 2:
        t = b = parts[0]
        r = l = parts[1]
    elif len(parts) == 3:
        t, r, b = parts
        l = r
    elif len(parts) == 4:
        t, r, b, l = parts
    else:
        return [(prop, value)]
    return [("top", t), ("right", r), ("bottom", b), ("left", l)]


DROP_PROPS = {"content"}


def finalise_decls(decls, env, warnings, where):
    """Cascade output -> the literal declarations that go in style=""."""
    ordered = []
    for prop, value in decls:
        if prop.startswith("--"):
            continue
        if prop in DROP_PROPS:
            continue
        try:
            value = substitute_vars(value, env)
        except UnresolvedVar as exc:
            warnings.append(f"{where}: dropped {prop} (unresolved var {exc})")
            continue
        value = resolve_calcs(value)
        if prop == "inset":
            ordered.extend(expand_inset(prop, value))
        else:
            ordered.append((prop, value))
    # Last declaration of a property wins, and keeps the later position so a
    # shorthand written after a longhand still overrides it the same way.
    seen = {}
    for i, (p, v) in enumerate(ordered):
        seen[p] = i
    return [(p, v) for i, (p, v) in enumerate(ordered) if seen[p] == i]


def style_string(decls):
    return ";".join(f"{p}:{v}" for p, v in decls)


# ---------------------------------------------------------------------------
# The flattening walk
# ---------------------------------------------------------------------------
class Flattener:
    def __init__(self, rules, warnings):
        self.rules = rules
        self.warnings = warnings

    def cascade(self, el, ancestors, pseudo=None):
        matched = [r for r in self.rules if r.pseudo == pseudo and rule_matches(el, ancestors, r)]
        matched.sort(key=lambda r: (r.spec, r.order))
        decls = []
        for r in matched:
            decls.extend(r.decls)
        if pseudo is None:
            decls.extend(parse_inline_style(el.get("style", "")))
        # !important declarations beat every normal one, including the
        # element's inline style, and rank among themselves by specificity.
        for r in matched:
            decls.extend(r.important)
        return decls

    def walk(self, el: Tag, ancestors, env):
        decls = self.cascade(el, ancestors)
        local_env = dict(env)
        for prop, value in decls:
            if prop.startswith("--"):
                local_env[prop] = value

        where = el.name + ("." + ".".join(el_classes(el)) if el_classes(el) else "")
        final = finalise_decls(decls, local_env, self.warnings, where)

        children = [c for c in el.children if isinstance(c, Tag)]

        # Pseudo-elements become real divs before the walk recurses, so they
        # are flattened by the same code path as everything else.
        for pseudo, position in (("before", 0), ("after", None)):
            pdecls = self.cascade(el, ancestors, pseudo)
            if not pdecls:
                continue
            pfinal = finalise_decls(pdecls, local_env, self.warnings, f"{where}::{pseudo}")
            div = Tag(name="div")
            div["style"] = style_string(pfinal)
            if position == 0:
                el.insert(0, div)
            else:
                el.append(div)

        # The class attribute stays on the tree for the whole walk. Stripping
        # it here strips it from an ancestor before its descendants are
        # reached, and every descendant selector in deck.css - `.tbl th`,
        # `.p7-tagwrap .tag` - then silently matches nothing. serialize()
        # drops class on the way out instead.
        if final:
            el["style"] = style_string(final)
        else:
            el.attrs.pop("style", None)

        for child in [c for c in el.children if isinstance(c, Tag)]:
            self.walk(child, ancestors + [el], local_env)
        return local_env


# ---------------------------------------------------------------------------
# Structural rewrites
# ---------------------------------------------------------------------------
def _find_by_marker(root: Tag, marker: str):
    return [el for el in root.find_all(True) if marker in (el.get("data-x") or "")]


def mark_structural(soup: BeautifulSoup):
    """Tag the elements the rewrites need before their classes are stripped."""
    for el in soup.find_all(True):
        classes = el_classes(el)
        if "masthead2" in classes:
            el["data-x"] = "masthead2"
        elif "m2-cream" in classes:
            el["data-x"] = "m2-cream"
        elif "m2-area" in classes:
            el["data-x"] = "m2-area"
        elif "kicker" in classes:
            el["data-x"] = "kicker"
        elif "grain-label" in classes:
            el["data-x"] = "grain-label"


def apply_masthead_rewrite(page: Tag, warnings):
    """The 60 degree chapter transition, out of borders instead of clip-path.

    `.m2-cream` and `.m2-area` are two rectangles that each clip away half of
    a shared 60 degree seam. Drop both clips and the area block's rectangle
    covers the cream's right edge - so instead the cream keeps its full
    rectangle and goes under, the area block gives up its background, and the
    field is painted back as two absolutely positioned children: a rectangle
    from the slant rightwards, and one border triangle for the wedge. The
    triangle is a zero-size box whose bottom border is the fill and whose
    left border is transparent, which is the same shape the clip cut.

    The whole field - wedge and rectangle together - is ONE border triangle,
    not a triangle butted against a rectangle. A box of width W with a
    transparent left border L and a coloured bottom border B paints the
    polygon (0,B) (L+W,B) (L+W,0) (L,0): the mitre gives the 60 degree edge
    and the rest of the bottom border gives the flat run to the trim. Drawn
    as two boxes, the join between them leaves a sub-pixel seam of cream
    showing through at the rasterised edge, which is visible on screen.

    The dateline is lifted to position:relative so it paints over the fill.
    Positioned boxes paint after in-flow content, and that shape-under-text
    split is what Canva wants of a coloured panel anyway.
    """
    for mh in _find_by_marker(page, "masthead2"):
        mh_style = dict(parse_inline_style(mh.get("style", "")))
        cream = None
        area = None
        for child in mh.children:
            if not isinstance(child, Tag):
                continue
            if child.get("data-x") == "m2-cream":
                cream = child
            elif child.get("data-x") == "m2-area":
                area = child
        if cream is None or area is None:
            warnings.append("masthead2 without both halves; left as-is")
            continue

        cream_style = dict(parse_inline_style(cream.get("style", "")))
        area_style = dict(parse_inline_style(area.get("style", "")))
        slant = cream_style.pop("clip-path", None)
        area_style.pop("clip-path", None)
        band = mh_style.get("min-height") or "26mm"
        # The slant is band-height / tan(60), already reduced by resolve_calcs
        # into the negative margin the area block carries.
        ml = area_style.get("margin-left", "0mm")
        slant_mm = abs(float(re.sub(r"[^0-9.\-]", "", ml) or 0))
        band_mm = float(re.sub(r"[^0-9.\-]", "", band) or 26)
        field = area_style.pop("background", None) or "#F5EFE2"

        cream.attrs["style"] = style_string(
            [(k, v) for k, v in cream_style.items()]
        )
        area_style["position"] = "relative"
        area.attrs["style"] = style_string([(k, v) for k, v in area_style.items()])

        area_w_mm = float(re.sub(r"[^0-9.\-]", "", area_style.get("width", "122mm")) or 122)
        wedge = Tag(name="div")
        wedge["style"] = (
            "position:absolute;top:0;left:0;height:0;"
            f"width:{fmt_num(area_w_mm - slant_mm)}mm;"
            f"border-left:{fmt_num(slant_mm)}mm solid transparent;"
            f"border-bottom:{fmt_num(band_mm)}mm solid {field}"
        )
        area.insert(0, wedge)

        for kicker in _find_by_marker(area, "kicker"):
            ks = parse_inline_style(kicker.get("style", ""))
            ks.insert(0, ("position", "relative"))
            kicker["style"] = style_string(ks)
        for el in (mh, cream, area):
            el.attrs.pop("data-x", None)
        for el in area.find_all(True):
            el.attrs.pop("data-x", None)


def drop_remaining_clip_paths(page: Tag, warnings):
    """Page 7's tag corner. Ground and page are both #FEFBFC, so the clip is
    invisible; the drawn outline SVG is what shows the cut corner."""
    for el in page.find_all(True):
        style = el.get("style")
        if not style or "clip-path" not in style:
            continue
        decls = [(p, v) for p, v in parse_inline_style(style) if p != "clip-path"]
        el["style"] = style_string(decls)


def apply_grain_rewrite(page: Tag, measures, page_key, warnings):
    """`writing-mode: vertical-rl` -> a rotated horizontal box.

    Rotating a W x H box by 90 degrees about its top-left corner puts it at
    x in [-H, 0], y in [0, W]. So placing left at (x0 + H) and top at y0 lands
    the rotated ink exactly on the vertical box Chrome measured.
    """
    labels = _find_by_marker(page, "grain-label")
    for i, el in enumerate(labels):
        key = f"{page_key}:{i}"
        m = measures.get("grain", {}).get(key)
        decls = [(p, v) for p, v in parse_inline_style(el.get("style", ""))]
        decls = [(p, v) for p, v in decls if p not in ("writing-mode", "transform", "top", "left")]
        if not m:
            warnings.append(f"grain label {key} not measured; left unrotated")
            el["style"] = style_string(decls)
            el.attrs.pop("data-x", None)
            continue
        decls.extend(
            [
                ("left", f"{fmt_num(m['x'] + m['w'])}mm"),
                ("top", f"{fmt_num(m['y'])}mm"),
                ("transform-origin", "0 0"),
                ("transform", "rotate(90deg)"),
                ("white-space", "nowrap"),
            ]
        )
        el["style"] = style_string(decls)
        el.attrs.pop("data-x", None)


def _cell_alignment(decls):
    """`vertical-align` has no meaning on a grid item; emulate it."""
    va = None
    keep = []
    for p, v in decls:
        if p == "vertical-align":
            va = v
        else:
            keep.append((p, v))
    return keep, (va or "middle")


def apply_table_rewrite(page: Tag, measures, page_key, warnings):
    for ti, table in enumerate(page.find_all("table")):
        measured = measures.get("tables", {}).get(f"{page_key}:{ti}")
        tstyle = dict(parse_inline_style(table.get("style", "")))
        rows = []
        for tr in table.find_all("tr"):
            cells = [c for c in tr.children if isinstance(c, Tag) and c.name in ("th", "td")]
            if cells:
                rows.append(cells)
        if not rows:
            continue
        def span_of(cell, attr):
            try:
                return max(1, int(cell.get(attr, 1)))
            except (TypeError, ValueError):
                return 1

        # A spanned cell covers several tracks, so the row width is the sum of
        # the colspans, not the cell count. Page 8's costing table ends on a
        # `colspan="3"` total row and would otherwise read as ragged.
        widths_per_row = [sum(span_of(c, "colspan") for c in r) for r in rows]
        ncols = max(widths_per_row)
        if any(w != ncols for w in widths_per_row):
            warnings.append(
                f"table with ragged rows ({widths_per_row}); grid columns may not line up"
            )

        # Column widths are the ones Chrome actually used, in millimetres.
        # A measured track cannot disagree with the table it replaces; the
        # authored percentages can, and did.
        widths = None
        if measured and measured.get("cols"):
            cells0 = measured["cols"]
            if sum(c["span"] for c in cells0) == ncols:
                widths = []
                for c in cells0:
                    # A spanned first-row cell covers several tracks; share
                    # its measured width between them rather than guess.
                    for _ in range(c["span"]):
                        widths.append(f"{fmt_num(c['w'] / c['span'])}mm")
        if widths is None:
            warnings.append(
                f"table {page_key}:{ti} not measured; falling back to authored widths"
            )
            widths = []
            for i in range(ncols):
                w = None
                if i < len(rows[0]):
                    w = dict(parse_inline_style(rows[0][i].get("style", ""))).get("width")
                widths.append(w or "1fr")

        border = "0.12mm solid #1A1A1A"
        for cell in rows[0]:
            b = dict(parse_inline_style(cell.get("style", ""))).get("border")
            if b:
                border = b
                break

        grid = Tag(name="div")
        gdecls = [
            ("display", "grid"),
            ("grid-template-columns", " ".join(widths)),
            ("border-top", border),
            ("border-left", border),
        ]
        for prop in (
            "font-family",
            "font-size",
            "line-height",
            "color",
            "width",
            "margin",
            "margin-top",
            "margin-bottom",
        ):
            if prop in tstyle:
                gdecls.append((prop, tstyle[prop]))
        if measured and measured.get("w"):
            gdecls.append(("width", f"{fmt_num(measured['w'])}mm"))
            gdecls.append(("box-sizing", "border-box"))
        grid["style"] = style_string(gdecls)

        for row in rows:
            for cell in row:
                cdecls = parse_inline_style(cell.get("style", ""))
                cmap = dict(cdecls)
                pad = cmap.get("padding", "1.3mm")
                bg = cmap.get("background", cmap.get("background-color", "transparent"))
                cdecls, va = _cell_alignment(cdecls)
                keep = [
                    (p, v)
                    for p, v in cdecls
                    if p
                    not in (
                        "padding",
                        "background",
                        "background-color",
                        "border",
                        "width",
                    )
                ]

                # The hairlines go on the grid item, not on the fill div.
                # A collapsed table border occupies real space between rows;
                # a border on an inset:0 overlay is painted inside the cell
                # and occupies none, which shortened every table by a pixel
                # a row and walked the rest of the page up with it.
                item = Tag(name="div")
                item_decls = [
                    ("position", "relative"),
                    ("border-right", border),
                    ("border-bottom", border),
                ]
                cspan, rspan = span_of(cell, "colspan"), span_of(cell, "rowspan")
                if cspan > 1:
                    item_decls.append(("grid-column", f"span {cspan}"))
                if rspan > 1:
                    item_decls.append(("grid-row", f"span {rspan}"))
                if va == "middle":
                    item_decls += [("display", "flex"), ("align-items", "center")]
                item["style"] = style_string(item_decls)

                fill = Tag(name="div")
                fill["style"] = (
                    f"position:absolute;top:0;left:0;right:0;bottom:0;background:{bg}"
                )
                item.append(fill)

                body = Tag(name="div")
                body_decls = [("position", "relative"), ("margin", pad)]
                if va == "middle":
                    body_decls.append(("flex", "1"))
                body_decls += keep
                body["style"] = style_string(body_decls)
                for child in list(cell.contents):
                    body.append(child.extract())
                item.append(body)
                grid.append(item)

        table.replace_with(grid)


def _plain_text_len(node) -> int:
    if isinstance(node, NavigableString):
        return len(str(node))
    return sum(_plain_text_len(c) for c in node.children)


def split_node_at_offset(node, offset):
    """Clone `node` into (head, tail) at a plain-text character offset.

    Used to break a paragraph exactly where the browser broke the column, so
    both halves re-break identically to the multicol original.
    """
    if isinstance(node, NavigableString):
        text = str(node)
        return NavigableString(text[:offset]), NavigableString(text[offset:])

    head = Tag(name=node.name, attrs=dict(node.attrs))
    tail = Tag(name=node.name, attrs=dict(node.attrs))
    remaining = offset
    for child in list(node.children):
        n = _plain_text_len(child)
        if remaining >= n:
            head.append(_clone(child))
            remaining -= n
        elif remaining <= 0:
            tail.append(_clone(child))
        else:
            h, t = split_node_at_offset(child, remaining)
            head.append(h)
            tail.append(t)
            remaining = 0
    return head, tail


def _clone(node):
    if isinstance(node, NavigableString):
        return NavigableString(str(node))
    new = Tag(name=node.name, attrs=dict(node.attrs))
    for c in node.children:
        new.append(_clone(c))
    return new


def apply_column_rewrite(page: Tag, measures, page_key, warnings):
    blocks = []
    for el in page.find_all(True):
        style = el.get("style") or ""
        if "column-count" in style:
            blocks.append(el)
    for i, el in enumerate(blocks):
        key = f"{page_key}:{i}"
        m = measures.get("cols", {}).get(key)
        decls = parse_inline_style(el.get("style", ""))
        smap = dict(decls)
        gap = smap.get("column-gap", "6mm")
        keep = [
            (p, v)
            for p, v in decls
            if p not in ("column-count", "column-gap", "columns", "column-fill")
        ]
        if not m or m.get("block") is None:
            warnings.append(f"column block {key} not measured; left as multicol")
            continue

        children = [c for c in el.children if isinstance(c, Tag)]
        col1 = Tag(name="div")
        col2 = Tag(name="div")
        bi = m["block"]
        off = m.get("offset")
        for idx, child in enumerate(children):
            if idx < bi:
                col1.append(_clone(child))
            elif idx > bi:
                col2.append(_clone(child))
            else:
                if off is None or off <= 0:
                    col2.append(_clone(child))
                else:
                    head, tail = split_node_at_offset(child, off)
                    # The break is a line boundary, so the space that ended
                    # the last line of column one belongs to neither half.
                    if tail.contents and isinstance(tail.contents[0], NavigableString):
                        tail.contents[0].replace_with(
                            NavigableString(str(tail.contents[0]).lstrip())
                        )
                    col1.append(head)
                    col2.append(tail)

        el.clear()
        el.append(col1)
        el.append(col2)
        # Height is pinned to what the multicol actually measured. Balanced
        # columns are not simply "the taller of the two": a fragmented
        # paragraph drops its bottom margin at the break, which two real
        # columns keep, and the balancer picks a height of its own. Pinning
        # is exact, and it is re-measured on every build, so editing the copy
        # cannot leave a stale number behind.
        pinned = []
        if m.get("height"):
            pinned = [("height", f"{fmt_num(m['height'])}mm"),
                      ("box-sizing", "border-box"),
                      ("overflow", "hidden")]
        # Track widths are the used multicol column width, not `1fr 1fr`.
        # The two agree to a fraction of a pixel, and a fraction of a pixel
        # is the difference between a word fitting on a line and not: page
        # 12's left column moved "did," across a line break on 1fr.
        tracks = "1fr 1fr"
        if m.get("colW"):
            tracks = f"{fmt_num(m['colW'])}mm {fmt_num(m['colW'])}mm"
        el["style"] = style_string(
            [("display", "grid"), ("grid-template-columns", tracks),
             ("column-gap", gap), ("align-items", "start")] + pinned + keep
        )


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}

ENTITIES = {
    "\u2019": "&rsquo;", "\u2018": "&lsquo;", "\u201c": "&ldquo;", "\u201d": "&rdquo;",
    "\u2014": "&mdash;", "\u2013": "&ndash;", "\u00b7": "&middot;", "\u00d7": "&times;",
    "\u2212": "&minus;", "\u00a0": "&nbsp;", "\u00bd": "&frac12;", "\u00b0": "&deg;",
    "\u2026": "&hellip;", "\u00e9": "&eacute;",
}


def escape_text(text: str) -> str:
    out = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    for ch, ent in ENTITIES.items():
        out = out.replace(ch, ent)
    return out


def escape_attr(text: str) -> str:
    out = text.replace("&", "&amp;").replace('"', "&quot;")
    for ch, ent in ENTITIES.items():
        out = out.replace(ch, ent)
    return out


def serialize(node, svgs, buf):
    if isinstance(node, Comment):
        return
    if isinstance(node, NavigableString):
        buf.append(escape_text(str(node)))
        return
    if node.name == "x-svg":
        raw = svgs[int(node["data-svg"])]
        style = node.get("style", "")
        raw = re.sub(r'\sclass="[^"]*"', "", raw, count=1)
        if style:
            raw = re.sub(r"^<svg", f'<svg style="{escape_attr(style)}"', raw, count=1)
        buf.append(raw)
        return
    attrs = []
    for k, v in node.attrs.items():
        if k == "class":
            continue
        if isinstance(v, list):
            v = " ".join(v)
        attrs.append(f' {k}="{escape_attr(str(v))}"')
    buf.append(f"<{node.name}{''.join(attrs)}>")
    if node.name in VOID:
        return
    for child in node.children:
        serialize(child, svgs, buf)
    buf.append(f"</{node.name}>")


# ---------------------------------------------------------------------------
# Source loading
# ---------------------------------------------------------------------------
SECTION_RE = re.compile(r"(?s)<section([^>]*)>(.*?)</section>")
SVG_RE = re.compile(r"(?s)<svg\b.*?</svg>")


def substitute_props(text: str, warnings) -> str:
    def repl(m):
        key = m.group(1)
        if key not in PROPS:
            warnings.append(f"unresolved deck prop {{{{ {key} }}}}")
            return ""
        return PROPS[key]

    return re.sub(r"\{\{\s*(\w+)\s*\}\}", repl, text)


def repoint_assets(text: str) -> str:
    def repl(m):
        stem = m.group(1)
        if (DS / "assets" / f"{stem}.jpg").exists():
            return f"./assets/{stem}.jpg"
        return m.group(0)

    return re.sub(r"\./assets/([\w-]+)\.png", repl, text)


def load_sections(warnings):
    """Return [(label, notes, body_html)] in reading order, pages 01..12.

    The deck's twelve sections are the whole document. There is no cover
    page: NESA's folio rules have no such concept - the physical display
    folio leads with an EMPTY first sleeve for paperwork - and the Canva
    document must match the deck page for page.
    """
    raw = DECK.read_text(encoding="utf-8")
    out = []
    for m in SECTION_RE.finditer(raw):
        attrs, body = m.group(1), m.group(2)
        label = (re.search(r'data-label="([^"]*)"', attrs) or [None, ""])[1]
        notes_m = re.search(r'data-speaker-notes="([^"]*)"', attrs)
        notes = notes_m.group(1) if notes_m else ""
        out.append((label, notes, body))
    out.sort(key=lambda t: t[0])
    return out


def prepare_body(body: str, warnings):
    """Props, asset twins, SVG protection. Returns (html, svg_sources)."""
    body = substitute_props(body, warnings)
    body = repoint_assets(body)
    svgs = []

    def stash(m):
        raw = m.group(0)
        cls = re.search(r'class="([^"]*)"', raw)
        svgs.append(raw)
        attr = f' class="{cls.group(1)}"' if cls else ""
        return f'<x-svg data-svg="{len(svgs) - 1}"{attr}></x-svg>'

    body = SVG_RE.sub(stash, body)
    return body, svgs


# ---------------------------------------------------------------------------
# Measurement pass (headless Chrome renders the real deck and reports)
# ---------------------------------------------------------------------------
# The whole point of measuring in the browser is to get the real line breaks,
# and line breaks are font metrics. Running at parse time reads a layout still
# set in the fallback face: on page 2 that moved every column break by a few
# words. Wait for the webfonts and for load before measuring anything.
MEASURE_JS = r"""
Promise.all([
  document.fonts.ready,
  new Promise(function (r) {
    if (document.readyState === 'complete') { r(); }
    else { window.addEventListener('load', r); }
  })
]).then(function () {
  var PX = 25.4 / 96;
  var out = {cols: {}, grain: {}, tables: {}};

  // Column widths. A percentage on a `<td>` is a content width that the
  // table's own layout algorithm then reconciles against padding, collapsed
  // borders and the other columns; the same percentage as a grid track is
  // the whole track. Reusing the authored percentages put every column of
  // the page 3 analysis table a few pixels out. Take the used widths.
  document.querySelectorAll('[data-measure-table]').forEach(function (t) {
    var key = t.getAttribute('data-measure-table');
    var tr = t.querySelector('tr');
    if (!tr) return;
    var cells = Array.prototype.filter.call(tr.children, function (c) {
      return c.tagName === 'TD' || c.tagName === 'TH';
    });
    out.tables[key] = {
      w: t.getBoundingClientRect().width * PX,
      cols: cells.map(function (c) {
        var r = c.getBoundingClientRect();
        var span = parseInt(c.getAttribute('colspan') || '1', 10) || 1;
        return {w: r.width * PX, span: span};
      })
    };
  });

  function textNodes(root) {
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
    var ns = [], n;
    while ((n = w.nextNode())) ns.push(n);
    return ns;
  }

  document.querySelectorAll('[data-measure-col]').forEach(function (el) {
    var key = el.getAttribute('data-measure-col');
    var cs = getComputedStyle(el);
    var box = el.getBoundingClientRect();
    var gap = parseFloat(cs.columnGap) || 0;
    var colW = (box.width - gap) / 2;
    var threshold = box.left + colW + gap / 2;
    var kids = Array.prototype.slice.call(el.children);
    var result = {block: null, offset: null,
                  height: box.height * PX, colW: colW * PX};
    for (var i = 0; i < kids.length; i++) {
      var r = document.createRange();
      r.selectNodeContents(kids[i]);
      var rects = Array.prototype.slice.call(r.getClientRects());
      if (!rects.length) continue;
      var anyRight = rects.some(function (q) { return q.left >= threshold; });
      var anyLeft = rects.some(function (q) { return q.left < threshold; });
      if (!anyRight) continue;
      if (!anyLeft) { result.block = i; result.offset = null; break; }
      // The break falls inside this block: find the first character that
      // renders in the second column.
      var ns = textNodes(kids[i]);
      var base = 0, found = null;
      for (var j = 0; j < ns.length && found === null; j++) {
        var node = ns[j], len = node.nodeValue.length;
        var rr = document.createRange();
        rr.selectNodeContents(node);
        var nrects = Array.prototype.slice.call(rr.getClientRects());
        var nodeHasRight = nrects.some(function (q) { return q.left >= threshold; });
        if (!nodeHasRight) { base += len; continue; }
        for (var k = 0; k < len; k++) {
          var cr = document.createRange();
          cr.setStart(node, k);
          cr.setEnd(node, k + 1);
          var b = cr.getBoundingClientRect();
          if (b.width === 0 && b.height === 0) continue;
          if (b.left >= threshold) { found = base + k; break; }
        }
        base += len;
      }
      result.block = i;
      result.offset = found;
      break;
    }
    out.cols[key] = result;
  });

  document.querySelectorAll('[data-measure-grain]').forEach(function (el) {
    var key = el.getAttribute('data-measure-grain');
    var host = el.offsetParent || el.parentElement;
    var p = host.getBoundingClientRect();
    var b = el.getBoundingClientRect();
    out.grain[key] = {
      x: (b.left - p.left) * PX,
      y: (b.top - p.top) * PX,
      w: b.width * PX,
      h: b.height * PX
    };
  });

  document.documentElement.innerHTML =
    '<head></head><body><pre id="measure">' +
    JSON.stringify(out).replace(/&/g, '&amp;').replace(/</g, '&lt;') +
    '</pre></body>';
});
"""


def run_measure(sections, chrome, warnings):
    """Render the untouched deck and ask the browser where things land."""
    if not chrome:
        warnings.append("no Chrome found; column splits and grain labels not measured")
        return {"cols": {}, "grain": {}}

    parts = []
    for label, _notes, body in sections:
        body = substitute_props(body, warnings)
        body = re.sub(r'(?<=["\'(])\./', ds_uri(), body)
        # Number the measurable elements in document order, per page, so the
        # keys line up with the same enumeration on the flattened side.
        ci = [0]
        gi = [0]

        def tag_cols(m):
            attr = m.group(0)
            out = attr[:-1] + f' data-measure-col="{label}:{ci[0]}">'
            ci[0] += 1
            return out

        body = re.sub(r"<div[^>]*style=\"[^\"]*column-count[^\"]*\"[^>]*>", tag_cols, body)

        def tag_grain(m):
            attr = m.group(0)
            out = attr[:-1] + f' data-measure-grain="{label}:{gi[0]}">'
            gi[0] += 1
            return out

        body = re.sub(r"<span[^>]*class=\"grain-label\"[^>]*>", tag_grain, body)

        ti = [0]

        def tag_table(m):
            out = m.group(0) + f' data-measure-table="{label}:{ti[0]}"'
            ti[0] += 1
            return out

        body = re.sub(r"<table\b", tag_table, body)
        parts.append(
            f'<div class="sheet" style="position:relative;overflow:hidden;'
            f'width:{PAGE_W_MM}mm;height:{PAGE_H_MM}mm">{body}</div>'
        )

    page = (
        '<!DOCTYPE html><html><head><meta charset="utf-8">\n'
        f"{HEAD_FONTS}\n"
        f'<link rel="stylesheet" href="{ds_uri()}deck.css">\n'
        "<style>html,body{margin:0;padding:0;background:#fff}</style>\n"
        f"</head><body>{''.join(parts)}\n<script>{MEASURE_JS}</script></body></html>"
    )

    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "measure.html"
        src.write_text(page, encoding="utf-8")
        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--hide-scrollbars",
            "--virtual-time-budget=20000",
            "--run-all-compositor-stages-before-draw",
            "--dump-dom",
            src.as_uri(),
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=180,
                                 encoding="utf-8", errors="replace")
        except subprocess.TimeoutExpired:
            warnings.append("Chrome measurement timed out")
            return {"cols": {}, "grain": {}}
    dom = res.stdout or ""
    m = re.search(r'<pre id="measure">(.*?)</pre>', dom, re.S)
    if not m:
        warnings.append("Chrome measurement produced no result block")
        return {"cols": {}, "grain": {}}
    payload = m.group(1).replace("&lt;", "<").replace("&amp;", "&")
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        warnings.append(f"measurement JSON unreadable: {exc}")
        return {"cols": {}, "grain": {}}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_page(label, notes, body, rules, root_vars, measures, warnings):
    body_html, svgs = prepare_body(body, warnings)
    soup = BeautifulSoup(f"<div id=__root>{body_html}</div>", "html.parser")
    root = soup.find(id="__root")

    page = None
    for child in root.children:
        if isinstance(child, Tag) and "page" in el_classes(child):
            page = child
            break
    if page is None:
        warnings.append(f"page {label}: no .page root found")
        return None

    mark_structural(page)

    flat = Flattener(rules, warnings)
    flat.walk(page, [], dict(root_vars))

    apply_masthead_rewrite(page, warnings)
    apply_grain_rewrite(page, measures, label, warnings)
    apply_column_rewrite(page, measures, label, warnings)
    apply_table_rewrite(page, measures, label, warnings)
    drop_remaining_clip_paths(page, warnings)
    for el in page.find_all(True):
        el.attrs.pop("data-x", None)

    buf = []
    serialize(page, svgs, buf)
    inner = "".join(buf)

    wrapper = (
        f'<div data-document-role="page" data-label="{escape_attr(label)}"'
        f' data-speaker-notes="{escape_attr(notes)}"'
        f' style="width:{fmt_num(PAGE_W_MM)}mm;height:{fmt_num(PAGE_H_MM)}mm;'
        f'overflow:hidden;background:#FEFBFC;position:relative">\n{inner}\n</div>'
    )
    return wrapper


def write_pdf(pages, chrome, out_pdf: Path, warnings):
    """Print the same pages to an A3 PDF, in reading order.

    This is the route that does not need anything published. Canva's own
    upload accepts PDF (to 300 MB and 500 pages) but does NOT accept HTML,
    zipped or otherwise - the HTML path exists only through the connector's
    `import-design-from-url`, which needs a URL that is already public, and
    this repository is private. So a PDF is what you can actually hand to
    Canva by hand.

    Forward order 01..12: `-rev` exists because the HTML importer
    reverses the file, and nothing reverses a PDF.
    """
    if not chrome:
        warnings.append("no Chrome found; PDF not written")
        return None

    body = "\n".join(
        f'<div style="break-after:page;page-break-after:always">{html}</div>'
        for _label, html in pages
    )
    body = re.sub(r'(?<=["\'(])\./', ds_uri(), body)
    doc = (
        '<!DOCTYPE html><html><head><meta charset="utf-8">\n'
        f"{HEAD_FONTS}\n<style>\n"
        f"  @page {{ size: {PAGE_W_MM}mm {PAGE_H_MM}mm; margin: 0; }}\n"
        "  html, body { margin: 0; padding: 0; background: #ffffff; }\n"
        "  a { color: #1A1A1A; text-decoration: underline; }\n"
        "  /* Backgrounds and hairlines are the artwork, not ink the browser\n"
        "     may drop to be helpful. */\n"
        "  * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }\n"
        "  div:last-child { break-after: auto; page-break-after: auto; }\n"
        f"</style></head><body>\n{body}\n</body></html>"
    )

    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "print.html"
        src.write_text(doc, encoding="utf-8")
        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            "--virtual-time-budget=30000",
            "--run-all-compositor-stages-before-draw",
            f"--print-to-pdf={out_pdf}",
            src.as_uri(),
        ]
        try:
            subprocess.run(cmd, capture_output=True, timeout=300)
        except subprocess.TimeoutExpired:
            warnings.append("Chrome timed out writing the PDF")
            return None
    if not out_pdf.exists():
        warnings.append("Chrome did not write the PDF")
        return None
    return out_pdf


def build(order="rev", chrome=None, out_path=DEFAULT_OUT):
    warnings = []
    rules, root_vars = load_stylesheet(DECK_CSS)
    sections = load_sections(warnings)
    measures = run_measure(sections, chrome, warnings)

    pages = []
    for label, notes, body in sections:
        html = build_page(label, notes, body, rules, root_vars, measures, warnings)
        if html:
            pages.append((label, html))

    ordered = list(reversed(pages)) if order == "rev" else pages
    doc = (
        '<!-- @dsCard group="Folio" name="A3 print export (flattened)" -->\n'
        "<!--\n"
        "  GENERATED FILE - DO NOT EDIT BY HAND.\n\n"
        f"  Built from design-system/{DECK.name} and {DECK_CSS.name} by:\n\n"
        "      python scripts/canva.py build --verify\n\n"
        "  An edit made here is lost on the next build, and - worse - it makes\n"
        "  this file disagree with the deck, which is what left the previous\n"
        "  hand-written version a whole design revision behind. Change the deck\n"
        "  or deck.css and rebuild. --verify screenshots every page twice, once\n"
        "  from the deck and once from this file, and diffs the two.\n"
        "-->\n"
        "<!DOCTYPE html>\n<html>\n<head>\n"
        '<meta charset="utf-8">\n'
        f"<title>{escape_text(TITLE)} - A3 folio, flattened for Canva</title>\n"
        f"{HEAD_FONTS}\n"
        "<style>\n"
        "  /* Deliberately no box-sizing reset: the deck is authored against\n"
        "     the initial content-box and states border-box per element. */\n"
        "  html, body { margin: 0; padding: 0; background: #ffffff; }\n"
        "  a { color: #1A1A1A; text-decoration: underline; }\n"
        "</style>\n"
        '<template id="__bundler_thumbnail"><svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 100 100"><rect width="100" height="100" fill="{THUMBNAIL["fill"]}"/>'
        '<text x="50" y="62" font-size="34" font-family="Georgia,serif" fill="#fff" '
        f'text-anchor="middle">{escape_text(THUMBNAIL["text"])}</text></svg></template>\n'
        "</head>\n<body>\n"
        + "\n\n".join(html for _label, html in ordered)
        + "\n</body>\n</html>\n"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(doc, encoding="utf-8")
    return out_path, [lbl for lbl, _ in ordered], warnings, pages


def main(argv=None):
    ap = argparse.ArgumentParser(prog="canva.py build", description=__doc__.splitlines()[0])
    ap.add_argument("--order", choices=("rev", "fwd"), default="rev")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--chrome")
    ap.add_argument("--verify", action="store_true",
                    help="screenshot every page twice - real deck and export - and diff")
    ap.add_argument("--pdf", nargs="?", const=str(EXPORT_PDF),
                    help="also print an A3 PDF, cover first - the file Canva's own "
                         "upload will take, since it does not accept HTML")
    args = ap.parse_args(argv)

    ensure_build_dir()
    chrome = find_chrome(args.chrome)
    out, labels, warnings, pages = build(
        order=args.order, chrome=chrome, out_path=args.out
    )
    print(f"  wrote {out}  ({len(labels)} pages: {', '.join(labels)})")

    if args.pdf:
        pdf = write_pdf(pages, chrome, Path(args.pdf), warnings)
        if pdf:
            mb = pdf.stat().st_size / 1024 / 1024
            print(f"  wrote {pdf}  ({len(pages)} A3 pages, {mb:.1f} MB, pages 01-12)")
    for w in warnings:
        print(f"  ! {w}")

    if args.verify:
        from .verify import verify

        return verify(out, chrome)
    return 0


if __name__ == "__main__":
    sys.exit(main())
