"""Render reference images of the production items for the wiki, from the same previews the PDFs print from.

The images are build output. docs_to_wiki.py --render writes them into the wiki, never into the repo.
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from print_pdfs import REPO, find_chrome, build_previews

SCALE = 3
PX_PER_MM = 96 / 25.4 * SCALE

# Wiki image name -> (preview item, preview page, css selector, which match, mm cropped off each edge, turn, paper).
# The spine prints with 3 mm of bleed round the 59 x 436 mm trim; the crop takes it back to the trim, and the
# turn lays the strip down so it reads left to right. The brand kit images are the live specimens on the design
# notes page, drawn by deck.css. Paper is a margin in mm set on paper colour round a specimen that has no sheet
# of its own, so it does not sit on the wiki's own background. docs_to_wiki.py reads the names, so nothing here
# may need Pillow at import time: the CI wiki check runs before the requirements are installed.
IMAGES = {
    "binder-spine.png": ("spine", "binder-spine.html", ".spine-piece", 0, 3, True, 0),
    "swing-tag-front.png": ("tag", "swing-tag.html", ".tag-wrap", 0, 0, False, 0),
    "swing-tag-back.png": ("tag", "swing-tag.html", ".tag-wrap", 1, 0, False, 0),
    "label-dress.png": ("labels", "product-labels.html", ".proof-row .cell", 0, 0, False, 4),
    "label-overskirt.png": ("labels", "product-labels.html", ".proof-row .cell", 1, 0, False, 4),
    "label-collar.png": ("labels", "product-labels.html", ".proof-row .cell", 2, 0, False, 4),
    "mount-scaffold.png": ("mounts", "mount-scaffold.html", ".ms-sheet", 0, 0, False, 0),
    "type-display.png": ("meta", "design-notes.html", ".mp-spec", 0, 0, False, 0),
    "type-text.png": ("meta", "design-notes.html", ".mp-spec", 1, 0, False, 0),
    "house-mark-uses.png": ("meta", "design-notes.html", ".mp-spec", 3, 0, False, 0),
    "masthead-detail.png": ("meta", "design-notes.html", ".mp-spec", 5, 0, False, 0),
    "rule-stub.png": ("meta", "design-notes.html", ".mp-spec", 6, 0, False, 0),
    "plates.png": ("meta", "design-notes.html", ".mp-spec", 7, 0, False, 0),
    "masthead-areas.png": ("meta", "design-notes.html", ".mp-spec", 8, 0, False, 0),
    "brand-colours.png": ("meta", "design-notes.html", ".mp-cards", 0, 0, False, 4),
    "colourway-slate.png": ("meta", "design-notes.html", ".mp-wrap > .area-sources", 0, 0, False, 6),
    "colourway-bone.png": ("meta", "design-notes.html", ".mp-wrap > .area-designs", 0, 0, False, 6),
    "colourway-ash.png": ("meta", "design-notes.html", ".mp-wrap > .area-making", 0, 0, False, 6),
    "colourway-wine.png": ("meta", "design-notes.html", ".mp-wrap > .area-trials", 0, 0, False, 6),
    "emph-line.png": ("meta", "design-notes.html", ".mp-emph-line", 0, 0, False, 6),
}

# Hides everything but the target, moves the target to the top left corner, and reports its size.
# The preview centres each sheet in the window, so where the target sits depends on the window width, and on
# Linux headless Chrome can run this script before --window-size has taken effect. The sheets are pinned to the
# top left instead, so the target's place no longer depends on the window, and it is placed again on resize.
ISOLATE = """
<style>
  html, body { background: transparent !important; margin: 0 !important; padding: 0 !important; }
  .pv-bar, .pv-tag { display: none !important; }
  .stack { display: block !important; padding: 0 !important; }
  body * { visibility: hidden !important; }
  .wiki-target, .wiki-target * { visibility: visible !important; }
  /* The design notes column is 180 mm but gives way to a narrow window. The screenshot window is the target's
     own width, so the column is held at 180 mm or it would rewrap and outgrow the measured height. */
  .mp-wrap { max-width: none !important; }
  %(paper)s
</style>
<script>
  const place = () => {
    const el = document.querySelectorAll(%(selector)s)[%(index)d];
    el.classList.add("wiki-target");
    document.body.style.transform = "";
    const r = el.getBoundingClientRect();
    document.body.style.transformOrigin = "0 0";
    document.body.style.transform = `translate(${-r.left - scrollX}px, ${-r.top - scrollY}px)`;
    let pre = document.getElementById("wiki-size");
    if (!pre) {
      pre = document.createElement("pre");
      pre.id = "wiki-size";
      pre.hidden = true;
      document.documentElement.appendChild(pre);
    }
    pre.textContent = JSON.stringify([r.width, r.height]);
  };
  Promise.all([
    document.fonts.load("900 20px Fraunces"),
    document.fonts.load("20px 'PT Serif'"),
    new Promise((done) => addEventListener("load", done)),
  ]).then(() => document.fonts.ready).then(() => {
    place();
    addEventListener("resize", place);
  });
</script>
"""


def chrome_run(chrome, *args):
    return subprocess.run(
        [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
         "--virtual-time-budget=30000", "--run-all-compositor-stages-before-draw", *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300,
    )


def render(chrome, html, selector, index, crop_mm, turn, paper_mm, dest, work):
    from PIL import Image

    page = work / f"{dest.stem}.html"
    paper = (
        f".wiki-target {{ background: #FEFBFC; padding: {paper_mm}mm; margin: 0; }}"
        " .wiki-target > :first-child { margin-top: 0; }"
    ) if paper_mm else ""
    inject = ISOLATE % {"selector": json.dumps(selector), "index": index, "paper": paper}
    page.write_text(html.read_text(encoding="utf-8-sig").replace("</body>", inject + "</body>"), encoding="utf-8")

    dom = chrome_run(chrome, "--dump-dom", page.as_uri()).stdout
    size = re.search(r'<pre id="wiki-size"[^>]*>(\[.*?\])</pre>', dom)
    if not size:
        sys.exit(f"{dest.name}: {selector} [{index}] not found in {html.name}")
    width, height = (round(v) for v in json.loads(size.group(1)))

    chrome_run(
        chrome, f"--force-device-scale-factor={SCALE}", f"--window-size={width},{height}",
        "--default-background-color=00000000", f"--screenshot={dest}", page.as_uri(),
    )
    if not dest.exists():
        sys.exit(f"{dest.name}: Chrome did not write the screenshot")
    image = Image.open(dest)
    if crop_mm:
        edge = round(crop_mm * PX_PER_MM)
        image = image.crop((edge, edge, image.width - edge, image.height - edge))
    if turn:
        image = image.transpose(Image.Transpose.ROTATE_90)
    image.save(dest, optimize=True)
    return image.size


def render_all(out, chrome=None):
    chrome = find_chrome(chrome)
    if not chrome:
        sys.exit("no Chrome or Edge found; set CHROME_PATH or pass --chrome")
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        previews = Path(td) / "previews"
        build_previews(sorted({spec[0] for spec in IMAGES.values()}), previews)
        for name, (_item, html, selector, index, crop_mm, turn, paper_mm) in IMAGES.items():
            args = (selector, index, crop_mm, turn, paper_mm, out / name, previews)
            width, height = render(chrome, previews / html, *args)
            print(f"  {name:<22} {width} x {height} px")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=REPO / "build" / "wiki-images", help="output folder")
    parser.add_argument("--chrome", default=None, help="path to Chrome or Edge")
    args = parser.parse_args()
    render_all(args.out, args.chrome)


if __name__ == "__main__":
    main()
