"""One entry point for every canva-sync step.

    canva_sync.py build   [--verify] [--pdf] [--order fwd]
    canva_sync.py verify  [--scale 2] [--keep DIR]
    canva_sync.py extract [--page 07]
    canva_sync.py ops     --page 01 --phase elements|format [...]
    canva_sync.py ops     --summary [--json]
    canva_sync.py check   --dump design.json [--refresh-ids]
    canva_sync.py probe   --tools tools.json
    canva_sync.py doctor  [--full] [--json]
    canva_sync.py selftest
    canva_sync.py guard   --hook
    canva_sync.py all

Every command takes `--config PATH`; without it the config is discovered by
walking up from the working directory (see config.py). `all` runs
build --verify, extract and ops --summary in that order and stops at the
first failure, so nothing reaches Canva that has not been pixel-verified.

Exit codes are the same everywhere:

    0  the step did what it was asked
    1  the step ran and the answer is no (a page over tolerance, a mismatch)
    2  the command line was wrong
    3  something the step needs is missing (config, deck, Chrome, layout)

Machine-readable output - op chunks, JSON summaries - goes to stdout and
nothing else does; progress and diagnostics go to stderr, so a caller can
pipe a chunk straight into a connector call.
"""

from __future__ import annotations

import sys

from . import COMMAND
from .config import ConfigError, activate, load

# Commands that need a loaded config (all but the inert guard).
STEPS = ("build", "verify", "extract", "ops", "check", "probe", "doctor", "selftest")
ALL_SEQUENCE = (("build", ["--verify"]), ("extract", []), ("ops", ["--summary"]))


def _dispatch(name, argv, settings):
    if name == "build":
        from . import build
        return build.main(argv, settings)
    if name == "verify":
        from . import verify
        return verify.main(argv, settings)
    if name == "extract":
        from . import extract
        return extract.main(argv, settings)
    if name == "ops":
        from . import ops
        return ops.main(argv, settings)
    if name == "check":
        from . import check
        return check.main(argv, settings)
    if name == "probe":
        from . import dialect
        return dialect.main(argv, settings)
    if name in ("doctor", "selftest"):
        from . import doctor
        return doctor.main(argv, settings, mode=name)
    raise AssertionError(name)


def _split_config(argv):
    """Pull --config PATH (or --config=PATH) out of the argument list."""
    rest, explicit = [], None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--config":
            if i + 1 >= len(argv):
                raise ConfigError("--config needs a path")
            explicit = argv[i + 1]
            i += 2
            continue
        if a.startswith("--config="):
            explicit = a.split("=", 1)[1]
            i += 1
            continue
        rest.append(a)
        i += 1
    return rest, explicit


def run_all(settings) -> int:
    for name, argv in ALL_SEQUENCE:
        print(f"== {name} {' '.join(argv)}".rstrip(), file=sys.stderr)
        rc = _dispatch(name, argv, settings)
        if rc:
            return rc
    return 0


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__.strip().replace("canva_sync.py", COMMAND))
        return 0 if argv else 2

    cmd, rest = argv[0], argv[1:]
    rest, explicit = _split_config(rest)

    # The guard runs inside an agent host's hook and must never fail loudly:
    # with no config it simply allows everything.
    if cmd == "guard":
        from . import doctor
        return doctor.guard_main(rest, explicit)

    if cmd not in (*STEPS, "all"):
        print(f"unknown command {cmd!r}\n\nrun `{COMMAND} --help`", file=sys.stderr)
        return 2

    try:
        settings = activate(load(explicit))
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 3

    try:
        if cmd == "all":
            return run_all(settings)
        return _dispatch(cmd, rest, settings) or 0
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    except Exception as exc:  # noqa: BLE001 - one place turns errors into exit codes
        from .ops import OpsError
        if isinstance(exc, OpsError):
            print(str(exc), file=sys.stderr)
            return 3
        raise


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
