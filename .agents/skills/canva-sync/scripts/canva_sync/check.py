"""Compare what Canva holds against what the repo says it should hold.

The push direction is build -> verify -> extract -> ops. This is the read
direction. The Canva connector is a conversation-side tool, so this script
cannot call it; instead it takes the JSON the connector returned for the
design, from a file or stdin, and diffs it against canva-layout.json page by
page:

  - text in the repo layout that Canva does not have (missing)
  - text Canva has that the repo layout does not (extra: edited in Canva, or
    left over from an earlier push)
  - image asset ids on the Canva page that canva.local.json does not map

With --refresh-ids it also rewrites the design id and the page id map in
canva.local.json from the dump, which is how a fresh Canva design gets wired
up after its pages are created. That file is the one thing outside the output
folder this tool ever writes; the deck is never touched.

The dump's shape is not pinned to one connector version. The walker accepts
either the raw response or a bare list of pages, finds pages as the first
list of objects that carry elements, and reads an element's text from its
`textRegions[].characters` (how read-design and edit-design return it today,
one region per run of styling, joined back together) or else from any of the
keys `text`, `plain_text`, `content` or `characters`, and asset ids from
`asset_id` or `media_id`. If a future response nests things differently, fix the walker
here rather than the comparison.

    canva_sync.py check --dump design.json
    canva_sync.py check --dump - --page 03          # read the dump from stdin
    canva_sync.py check --dump design.json --refresh-ids
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from . import COMMAND
from .config import cfg

TEXT_KEYS = ("text", "plain_text", "content", "characters")
ASSET_KEYS = ("asset_id", "media_id")
ID_KEYS = ("id", "page_id")
ELEMENT_KEYS = ("elements", "children", "items")


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def region_text(node: dict):
    """The text of an element that carries textRegions, or None."""
    regions = node.get("textRegions")
    if not isinstance(regions, list):
        return None
    return norm("".join(r.get("characters", "") for r in regions if isinstance(r, dict)))


def element_texts(page) -> list:
    """(locator id or element id, text) for every text element under a page, in order."""
    found: list = []

    def visit(node):
        if isinstance(node, dict):
            text = region_text(node)
            if text is None:
                text = next((norm(node[k]) for k in TEXT_KEYS
                             if isinstance(node.get(k), str) and node[k].strip()), None)
            ident = node.get("locator_id") or node.get("id")
            if text and isinstance(ident, str):
                found.append((ident, text))
                return
            for v in node.values():
                visit(v)
        elif isinstance(node, list):
            for v in node:
                visit(v)

    visit(page.get("elements", page))
    return found


def walk(node, texts: list, assets: list):
    """Collect text strings and asset ids anywhere under node."""
    if isinstance(node, dict):
        text = region_text(node)
        if text:
            texts.append(text)
        for k, v in node.items():
            if k == "textRegions":
                continue
            if k in TEXT_KEYS and isinstance(v, str) and v.strip():
                texts.append(norm(v))
            elif k in ASSET_KEYS and isinstance(v, str):
                assets.append(v)
            else:
                walk(v, texts, assets)
    elif isinstance(node, list):
        for v in node:
            walk(v, texts, assets)


def find_pages(dump):
    """The first list of dicts that look like pages (each carrying elements)."""
    if isinstance(dump, list) and dump and all(isinstance(p, dict) for p in dump):
        if any(any(k in p for k in ELEMENT_KEYS) for p in dump):
            return dump
    if isinstance(dump, dict):
        if "pages" in dump and isinstance(dump["pages"], list):
            return dump["pages"]
        # edit-design returns the one page it edited as document.page
        page = dump.get("page")
        if isinstance(page, dict) and any(k in page for k in ELEMENT_KEYS):
            return [page]
        for v in dump.values():
            found = find_pages(v)
            if found:
                return found
    if isinstance(dump, list):
        for v in dump:
            found = find_pages(v)
            if found:
                return found
    return []


def find_design_id(dump) -> str:
    if isinstance(dump, dict):
        for k in ("design_id", "designId"):
            if isinstance(dump.get(k), str):
                return dump[k]
        d = dump.get("design")
        if isinstance(d, dict) and isinstance(d.get("id"), str):
            return d["id"]
        for v in dump.values():
            found = find_design_id(v)
            if found:
                return found
    return ""


def page_label(index: int) -> str:
    return f"{index + 1:02d}"


def compare(layout_pages, canva_pages, only=None):
    known = set(cfg().asset_ids().values())
    problems = 0
    by_label = {p["label"]: p for p in layout_pages}
    for i, cp in enumerate(canva_pages):
        label = page_label(i)
        if only and label != only:
            continue
        lp = by_label.get(label)
        texts: list[str] = []
        assets: list[str] = []
        walk(cp, texts, assets)
        if lp is None:
            print(f"  page {label}: in Canva but not in the repo layout ({len(texts)} texts)")
            problems += 1
            continue
        want = {norm(e["text"]) for e in lp["elements"] if e["kind"] == "text" and norm(e["text"])}
        have = set(texts)
        missing = sorted(want - have)
        extra = sorted(have - want)
        unknown = sorted(set(assets) - known)
        state = "ok " if not (missing or extra or unknown) else "DIFF"
        print(f"  {state} page {label}: {len(want)} repo texts, {len(have)} canva texts, "
              f"{len(missing)} missing, {len(extra)} extra, {len(unknown)} unmapped assets")
        for t in missing:
            print(f"        - {t[:100]}")
        for t in extra:
            print(f"        + {t[:100]}")
        for a in unknown:
            print(f"        ? asset {a}")
        if missing or extra or unknown:
            problems += 1
    for label in sorted(by_label):
        if int(label) > len(canva_pages) and (not only or only == label):
            print(f"  page {label}: in the repo layout but not in Canva")
            problems += 1
    return problems


def refresh_ids(dump, canva_pages) -> None:
    settings = cfg()
    local = dict(settings.local)
    design_id = find_design_id(dump)
    if design_id:
        local["design_id"] = design_id
    pages = {}
    for i, cp in enumerate(canva_pages):
        pid = next((cp[k] for k in ID_KEYS if isinstance(cp.get(k), str)), None)
        if pid:
            pages[page_label(i)] = pid
    if pages:
        local["pages"] = pages
    local.setdefault("assets", {})
    written = settings.save_local(local)
    print(f"  wrote {written}: design {local.get('design_id') or '(none)'}, "
          f"{len(pages)} page ids", file=sys.stderr)


def main(argv=None, settings=None):
    settings = settings or cfg()
    ap = argparse.ArgumentParser(prog=f"{COMMAND} check", description=__doc__.splitlines()[0])
    ap.add_argument("--dump", required=True,
                    help="the connector's design JSON, a file path or - for stdin")
    ap.add_argument("--page", help="check one page label, e.g. 03")
    ap.add_argument("--refresh-ids", action="store_true",
                    help="rewrite design id and page ids in canva.local.json from the dump")
    args = ap.parse_args(argv)

    raw = sys.stdin.read() if args.dump == "-" else Path(args.dump).read_text(encoding="utf-8")
    try:
        dump = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"the dump is not JSON: {exc}", file=sys.stderr)
        return 2
    canva_pages = find_pages(dump)
    if not canva_pages:
        print("no pages found in the dump; see the walker notes at the top of check.py",
              file=sys.stderr)
        return 1
    if args.refresh_ids:
        refresh_ids(dump, canva_pages)
    layout = settings.layout_json
    if not layout.exists():
        print(f"  {layout} not found; run `{COMMAND} extract` to compare text",
              file=sys.stderr)
        return 0
    layout_pages = json.loads(layout.read_text(encoding="utf-8"))
    problems = compare(layout_pages, canva_pages, args.page)
    if problems:
        print(f"  {problems} page(s) differ")
        return 1
    print("  Canva matches the repo layout")
    return 0


if __name__ == "__main__":
    sys.exit(main())
