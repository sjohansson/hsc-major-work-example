"""Compare what Canva holds against what the repo says it should hold.

The push direction is build -> verify -> extract -> ops. This is the read
direction. The Canva connector is a conversation-side tool, so this script
cannot call it; instead it takes the JSON that `read-design` returned, saved
to a file, and diffs it against build/canva/canva-layout.json page by page:

  - text in the repo layout that Canva does not have (missing)
  - text Canva has that the repo layout does not (extra: edited in Canva, or
    left over from an earlier push)
  - image asset ids on the Canva page that canva.local.json does not map

With --refresh-ids it also rewrites the design id and the page id map in
design-system/canva.local.json from the dump, which is how a fresh Canva
design gets wired up after its pages are created.

The dump's shape is not pinned to one connector version. The walker accepts
either the raw response or a bare list of pages, finds pages as the first
list of objects that carry elements, and reads text from any of the keys
`text`, `plain_text` or `content` and asset ids from `asset_id` or
`media_id`. If a future response nests things differently, fix the walker
here rather than the comparison.

    python scripts/canva.py check --dump read-design.json
    python scripts/canva.py check --dump read-design.json --page 03
    python scripts/canva.py check --dump read-design.json --refresh-ids
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from .config import LOCAL, asset_ids, save_local
from .config import LAYOUT_JSON as LAYOUT

TEXT_KEYS = ("text", "plain_text", "content")
ASSET_KEYS = ("asset_id", "media_id")
ID_KEYS = ("id", "page_id")
ELEMENT_KEYS = ("elements", "children", "items")


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def walk(node, texts: list, assets: list):
    """Collect text strings and asset ids anywhere under node."""
    if isinstance(node, dict):
        for k, v in node.items():
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
    known = set(asset_ids().values())
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
    local = dict(LOCAL)
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
    save_local(local)
    print(f"  wrote canva.local.json: design {local.get('design_id') or '(none)'}, {len(pages)} page ids")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="canva.py check", description=__doc__.splitlines()[0])
    ap.add_argument("--dump", type=Path, required=True, help="saved read-design JSON")
    ap.add_argument("--page", help="check one folio page label, e.g. 03")
    ap.add_argument("--refresh-ids", action="store_true",
                    help="rewrite design id and page ids in canva.local.json from the dump")
    args = ap.parse_args(argv)

    dump = json.loads(args.dump.read_text(encoding="utf-8"))
    canva_pages = find_pages(dump)
    if not canva_pages:
        sys.exit("no pages found in the dump; see the walker notes in canva/check.py")
    if args.refresh_ids:
        refresh_ids(dump, canva_pages)
    if not LAYOUT.exists():
        print(f"  {LAYOUT} not found; run `python scripts/canva.py extract` to compare text")
        return 0
    layout_pages = json.loads(LAYOUT.read_text(encoding="utf-8"))
    problems = compare(layout_pages, canva_pages, args.page)
    if problems:
        print(f"  {problems} page(s) differ")
        return 1
    print("  Canva matches the repo layout")
    return 0


if __name__ == "__main__":
    sys.exit(main())
