#!/usr/bin/env python3
"""One entry point for the Canva pipeline.

    python scripts/canva.py build [--verify] [--pdf] [--order fwd]
    python scripts/canva.py verify [--scale 2] [--keep DIR]
    python scripts/canva.py extract [--page 07]
    python scripts/canva.py ops --page 01 --phase elements|format [...]
    python scripts/canva.py ops --summary
    python scripts/canva.py check --dump read-design.json [--refresh-ids]
    python scripts/canva.py all

`all` runs build --verify, extract and ops --summary in that order and stops
at the first failure. Every step reads design-system/canva.config.json and
writes only under build/canva/. See docs/canva-pipeline.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from canva import build, check, extract, ops, verify  # noqa: E402

COMMANDS = {
    "build": build.main,
    "verify": verify.main,
    "extract": extract.main,
    "ops": ops.main,
    "check": check.main,
}


def run_all() -> int:
    for name, argv in (("build", ["--verify"]), ("extract", []), ("ops", ["--summary"])):
        print(f"== {name} {' '.join(argv)}".rstrip())
        rc = COMMANDS[name](argv)
        if rc:
            return rc
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0 if argv else 2
    cmd, rest = argv[0], argv[1:]
    if cmd == "all":
        return run_all()
    if cmd not in COMMANDS:
        print(f"unknown command {cmd!r}\n\n{__doc__.strip()}", file=sys.stderr)
        return 2
    return COMMANDS[cmd](rest) or 0


if __name__ == "__main__":
    sys.exit(main())
