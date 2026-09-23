"""Build GitHub wiki pages from docs/. The wiki is a copy: docs/ is the source and every run replaces it."""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "docs"

LINK = re.compile(r'(!?)\[([^\]]*)\]\(([^)\s]+)((?:\s+"[^"]*")?)\)')
CODE_SPAN = re.compile(r"(`+[^`]*`+)")
FENCE = re.compile(r"^\s*(```|~~~)")


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()


def default_repo():
    if os.environ.get("GITHUB_REPOSITORY"):
        return os.environ["GITHUB_REPOSITORY"]
    url = git("remote", "get-url", "origin")
    match = re.search(r"github\.com[:/](.+?)(?:\.git)?$", url)
    if not match:
        sys.exit(f"cannot read owner/name from origin {url}; pass --repo")
    return match.group(1)


def title_of(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


class Rewriter:
    def __init__(self, repo, ref):
        self.web = f"https://github.com/{repo}"
        self.raw = f"https://raw.githubusercontent.com/{repo}/{ref}"
        self.ref = ref
        self.errors = []

    def target(self, source, image, href):
        if re.match(r"^[a-z][a-z0-9+.-]*:", href, re.I) or href.startswith("#"):
            return href
        path, _, fragment = href.partition("#")
        fragment = f"#{fragment}" if fragment else ""
        resolved = (source.parent / path).resolve()
        try:
            relative = resolved.relative_to(REPO).as_posix()
        except ValueError:
            self.errors.append(f"{source.name}: {href} points outside the repo")
            return href
        if not resolved.exists():
            self.errors.append(f"{source.name}: {href} does not exist")
            return href
        if resolved.parent == DOCS and resolved.suffix == ".md":
            return resolved.stem + fragment
        if image:
            return f"{self.raw}/{relative}"
        kind = "tree" if resolved.is_dir() else "blob"
        return f"{self.web}/{kind}/{self.ref}/{relative}{fragment}"

    def line(self, source, text):
        def link(match):
            image, label, href, title = match.groups()
            return f"{image}[{label}]({self.target(source, bool(image), href)}{title})"

        parts = CODE_SPAN.split(text)
        return "".join(part if i % 2 else LINK.sub(link, part) for i, part in enumerate(parts))

    def page(self, source):
        out, fenced = [], False
        for text in source.read_text(encoding="utf-8").splitlines():
            if FENCE.match(text):
                fenced = not fenced
            out.append(text if fenced else self.line(source, text))
        return "\n".join(out) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=REPO / "build" / "wiki", help="output folder, emptied first")
    parser.add_argument("--repo", default=None, help="owner/name for links back to the repo")
    parser.add_argument("--ref", default=os.environ.get("GITHUB_REF_NAME", "main"), help="branch the links use")
    args = parser.parse_args()

    repo = args.repo or default_repo()
    sha = os.environ.get("GITHUB_SHA") or git("rev-parse", "HEAD")
    rewriter = Rewriter(repo, args.ref)
    sources = sorted(DOCS.glob("*.md"))
    reserved = {"home", "_sidebar", "_footer"} & {p.stem.lower() for p in sources}
    if reserved:
        sys.exit(f"docs/ uses a name the wiki reserves: {', '.join(sorted(reserved))}")

    pages = {source.stem: rewriter.page(source) for source in sources}
    if rewriter.errors:
        sys.exit("broken links in docs/:\n  " + "\n  ".join(rewriter.errors))

    index = "".join(f"- [{title_of(source)}]({source.stem})\n" for source in sources)
    pages["Home"] = (
        "Reference documents for the folio, copied from the "
        f"[docs/]({rewriter.web}/tree/{args.ref}/docs) folder of the repository.\n\n{index}"
    )
    pages["_Sidebar"] = f"[Home](Home)\n\n{index}"
    pages["_Footer"] = (
        f"Generated from [docs/ at {sha[:7]}]({rewriter.web}/commit/{sha}). "
        "Edit the repository, not the wiki. Every sync replaces the wiki.\n"
    )

    if args.out.exists():
        shutil.rmtree(args.out)
    args.out.mkdir(parents=True)
    for name, text in pages.items():
        (args.out / f"{name}.md").write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {len(pages)} pages to {args.out}")


if __name__ == "__main__":
    main()
