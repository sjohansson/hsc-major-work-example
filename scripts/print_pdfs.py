"""Print the folio and the production items to PDF, the way Ctrl+P prints the preview, and check each one.

preview.ps1 builds the pages. Headless Chrome prints each built page at the size its @page rule names. A PDF
passes when it has one page per sheet in the preview and every page is the sheet size to within 1 mm.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# preview.ps1 item -> the page it writes.
ITEMS = {
    "folio": "folio.html",
    "spine": "binder-spine.html",
    "tag": "swing-tag.html",
    "labels": "product-labels.html",
    "mounts": "mount-scaffold.html",
}

SHEET = re.compile(r'class="pv"')
PAGE_SIZE = re.compile(r"@page\s*\{\s*size:\s*([\d.]+)mm\s+([\d.]+)mm")
PDF_PAGE = re.compile(rb"/Type\s*/Page(?![s\w])")
MEDIA_BOX = re.compile(rb"/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\]")
PT_PER_MM = 72 / 25.4
TOLERANCE_MM = 1.0


def find_chrome(explicit=None):
    if explicit:
        return explicit
    if os.environ.get("CHROME_PATH"):
        return os.environ["CHROME_PATH"]
    for name in ("google-chrome", "chrome", "chromium", "msedge", "microsoft-edge"):
        if shutil.which(name):
            return shutil.which(name)
    for base in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)")):
        for rel in (r"Google\Chrome\Application\chrome.exe", r"Microsoft\Edge\Application\msedge.exe"):
            if base and (Path(base) / rel).exists():
                return str(Path(base) / rel)
    return None


def build_previews(items, out):
    pwsh = shutil.which("pwsh")
    if not pwsh:
        sys.exit("pwsh not found; preview.ps1 needs PowerShell 7")
    command = f"& '{REPO / 'scripts' / 'preview.ps1'}' -Item {','.join(items)} -NoOpen -OutDir '{out}'"
    subprocess.run([pwsh, "-NoProfile", "-Command", command], check=True)


def print_pdf(chrome, html, pdf):
    pdf.unlink(missing_ok=True)
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        "--virtual-time-budget=30000",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={pdf}",
        html.as_uri(),
    ]
    subprocess.run(cmd, capture_output=True, timeout=600)
    return pdf.exists()


def check(html, pdf):
    """What is wrong with the PDF, measured against the preview it was printed from. Empty when it passes."""
    text = html.read_text(encoding="utf-8-sig")
    sheets = len(SHEET.findall(text))
    size = PAGE_SIZE.search(text)
    if not size:
        return [f"{html.name} has no @page size"]
    want = (float(size.group(1)), float(size.group(2)))

    data = pdf.read_bytes()
    pages = len(PDF_PAGE.findall(data))
    problems = []
    if pages != sheets:
        problems.append(f"{pages} pages, the preview has {sheets} sheets")
    for box in {m.groups() for m in MEDIA_BOX.finditer(data)}:
        x0, y0, x1, y1 = (float(v) for v in box)
        got = ((x1 - x0) / PT_PER_MM, (y1 - y0) / PT_PER_MM)
        if any(abs(g - w) > TOLERANCE_MM for g, w in zip(got, want)):
            problems.append(f"a page is {got[0]:.1f} x {got[1]:.1f} mm, the sheet is {want[0]:g} x {want[1]:g} mm")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=REPO / "build" / "print", help="output folder")
    parser.add_argument("--item", nargs="+", choices=list(ITEMS), default=list(ITEMS), help="what to print")
    parser.add_argument("--chrome", default=None, help="path to Chrome or Edge")
    args = parser.parse_args()

    chrome = find_chrome(args.chrome)
    if not chrome:
        sys.exit("no Chrome or Edge found; set CHROME_PATH or pass --chrome")
    out = args.out.resolve()
    build_previews(args.item, out)

    failed = False
    for item in args.item:
        html = out / ITEMS[item]
        pdf = html.with_suffix(".pdf")
        problems = check(html, pdf) if print_pdf(chrome, html, pdf) else ["Chrome did not write the PDF"]
        failed |= bool(problems)
        status = "FAIL " + "; ".join(problems) if problems else f"ok, {pdf.stat().st_size / 1e6:.1f} MB"
        print(f"  {item:<8} {pdf.name:<22} {status}")
    if failed:
        sys.exit("one or more PDFs failed the check")


if __name__ == "__main__":
    main()
