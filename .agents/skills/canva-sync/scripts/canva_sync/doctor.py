"""The three checks that run before, during and around a push.

doctor    Everything the pipeline needs, checked in one go and reported as a
          list of named checks: the config, the dependencies, a browser, the
          deck and its stylesheet and assets, the selector subset the cascade
          understands, unresolved props, duplicate page labels, and the
          dialect. Run it first; it is the gate the skill opens with.

selftest  Build, verify, extract and generate ops for the one-page fixture in
          assets/fixtures/mini-deck, copied to a temporary directory. It
          proves the bundle works on a deck that is not this repository's, and
          it proves the one-way rule two ways: the fixture's own files are
          byte-identical afterwards, and the package source contains no write
          call outside Settings.write_text and Settings.save_local.

guard     A PreToolUse hook for agent hosts. It reads the tool call on stdin
          and denies an edit or write aimed anywhere but the output folder and
          the local id file. With no config discoverable it allows everything,
          so dropping the bundle into another repository cannot lock it up.
          With --no-edits, it denies direct editing tools, including Codex
          apply_patch, without loading a config.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from . import COMMAND, VERSION
from .config import ConfigError, Settings, activate, cfg, find_chrome, load

BUNDLE = Path(__file__).resolve().parent.parent.parent
EDIT_TOOLS = {
    "edit", "multiedit", "write", "notebookedit", "apply_patch",
    "create_file", "replace_string_in_file", "edit_notebook_file",
}


# -- doctor ------------------------------------------------------------------


def _check(name, ok, detail, *, warn=False):
    return {"check": name, "ok": bool(ok), "warn": bool(warn and not ok), "detail": detail}


def _stylesheet_checks(settings: Settings) -> list:
    """Parse the stylesheet with the real loader, so an unsupported selector is
    reported here rather than as a traceback halfway through a build."""
    from .build import load_stylesheet

    try:
        rules, _root = load_stylesheet(settings.deck_css)
    except Exception as exc:  # noqa: BLE001 - the message is the point
        return [_check("stylesheet", False, f"{settings.deck_css.name}: {exc}")]
    return [_check("stylesheet", True,
                   f"{settings.deck_css.name}: {len(rules)} rules, all selectors supported")]


def _deck_checks(settings: Settings) -> list:
    from .build import SECTION_RE

    out = []
    raw = settings.deck.read_text(encoding="utf-8")
    import re

    labels = [(re.search(r'data-label="([^"]*)"', m.group(1)) or [None, ""])[1]
              for m in SECTION_RE.finditer(raw)]
    dupes = sorted({lbl for lbl in labels if labels.count(lbl) > 1})
    out.append(_check("page labels", not dupes and bool(labels),
                      f"{len(labels)} sections"
                      + (f"; duplicated labels: {', '.join(dupes)}" if dupes else "")
                      + ("" if labels else "; no <section> found")))

    props = set(re.findall(r"\{\{\s*(\w+)\s*\}\}", raw))
    unresolved = sorted(props - set(settings.props))
    out.append(_check("deck props", not unresolved,
                      f"{len(props)} used"
                      + (f"; not in config: {', '.join(unresolved)}" if unresolved else "")))

    missing = []
    for ref in sorted(set(re.findall(r'\./assets/([\w.\-]+)', raw))):
        if not (settings.assets_dir / ref).exists():
            missing.append(ref)
    out.append(_check("deck assets", not missing,
                      f"{settings.assets_dir}"
                      + (f"; missing: {', '.join(missing[:8])}" if missing else ""),
                      warn=False))
    return out


def run_doctor(settings: Settings, full: bool = False) -> dict:
    checks = [_check("config", True, f"{settings.path}")]

    for mod, why in (("bs4", "beautifulsoup4"), ("tinycss2", "tinycss2"), ("PIL", "pillow")):
        try:
            __import__(mod)
            checks.append(_check(f"dependency {why}", True, "importable"))
        except ImportError:
            checks.append(_check(f"dependency {why}", False,
                                 f"not installed; pip install -r {BUNDLE / 'requirements.txt'}"))

    chrome = find_chrome()
    checks.append(_check("browser", bool(chrome),
                         chrome or "no Chrome or Edge on PATH; set CHROME_PATH. "
                                   "verify and extract need one",
                         warn=True))

    checks.append(_check("deck", settings.deck.exists(), str(settings.deck)))
    checks.append(_check("stylesheet file", settings.deck_css.exists(), str(settings.deck_css)))

    inside = settings.assets_dir == settings.deck_dir or \
        settings.deck_dir.resolve() in settings.assets_dir.resolve().parents
    checks.append(_check("assets folder", settings.assets_dir.exists() and inside,
                         f"{settings.assets_dir}"
                         + ("" if inside else " is outside deck_dir, so ./assets refs will not resolve")))

    out_ok = not settings.output_dir.resolve() == settings.deck_dir.resolve()
    checks.append(_check("output folder", out_ok,
                         f"{settings.output_dir}"
                         + ("" if out_ok else " is the deck folder; the sync refuses to write there")))

    checks.append(_check("local ids", True,
                         f"{settings.local_path}"
                         + ("" if settings.local_path.exists() else " (absent; ops carry PAGE_ID "
                            "and every image is a placeholder)")))
    legacy = settings.deck_dir / "canva.local.json"
    if legacy.exists() and legacy != settings.local_path:
        checks.append(_check("local ids location", False,
                             f"{legacy} is where this file used to live; move it to "
                             f"{settings.local_path}"))

    try:
        from .dialect import load as load_dialect
        d = load_dialect(settings.dialect)
        checks.append(_check("dialect", True,
                             f"{d.name} ({d.status}); needs {', '.join(d.required_tools)}"))
        if d.status != "verified":
            checks.append(_check("dialect verified", False,
                                 f"{d.name} is unverified: run `{COMMAND} probe --tools ...` "
                                 f"and push one page before the rest", warn=True))
    except Exception as exc:  # noqa: BLE001
        checks.append(_check("dialect", False, str(exc)))

    if settings.deck.exists():
        checks.extend(_deck_checks(settings))
    if settings.deck_css.exists():
        checks.extend(_stylesheet_checks(settings))

    failed = [c for c in checks if not c["ok"] and not c["warn"]]
    warned = [c for c in checks if c["warn"]]
    report = {
        "version": VERSION,
        "config": str(settings.path),
        "checks": checks,
        "failed": len(failed),
        "warned": len(warned),
        "ok": not failed,
    }
    if full:
        report["selftest"] = run_selftest()
        report["ok"] = report["ok"] and report["selftest"]["ok"]
    return report


def print_report(report: dict) -> None:
    for c in report["checks"]:
        mark = "ok  " if c["ok"] else ("warn" if c["warn"] else "FAIL")
        print(f"  {mark} {c['check']}: {c['detail']}", file=sys.stderr)
    if "selftest" in report:
        st = report["selftest"]
        print(f"  {'ok  ' if st['ok'] else 'FAIL'} selftest: "
              f"{'; '.join(f'{k}={v}' for k, v in st['steps'].items())}", file=sys.stderr)
    print(f"  {report['failed']} failed, {report['warned']} warning(s)", file=sys.stderr)


# -- selftest ----------------------------------------------------------------


# Receivers allowed to write a file, per module. Anything else is a new way
# for the sync to put bytes on disk, and has to be argued for rather than
# slipped in: the whole contract is that it writes to the output folder and
# nowhere else.
#
#   settings  the guarded Settings.write_text
#   self      inside config.py, which is that guard and save_local
#   path      config.py's guarded write, after the check
#   src       a render input inside a TemporaryDirectory
#   dump      selftest's synthetic connector response, in its temp copy
ALLOWED_WRITERS = {
    "build.py": {"settings", "src"},
    "verify.py": {"settings"},
    "extract.py": {"settings", "src"},
    "ops.py": set(),
    "check.py": set(),
    "cli.py": set(),
    "dialect.py": set(),
    "config.py": {"self", "path"},
    "doctor.py": {"settings", "dump"},
    "__init__.py": set(),
    "__main__.py": set(),
}


def _source_write_audit() -> list:
    """Every file write in the package, read off the syntax tree.

    Reading the tree rather than the text means a docstring that mentions
    write_text is not a finding, and a real call cannot hide behind
    formatting."""
    import ast

    offenders = []
    for py in sorted(Path(__file__).resolve().parent.glob("*.py")):
        allowed = ALLOWED_WRITERS.get(py.name)
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Name) and func.id == "open":
                offenders.append(f"{py.name}:{node.lineno}: bare open()")
                continue
            if not isinstance(func, ast.Attribute):
                continue
            if func.attr not in ("write_text", "write_bytes"):
                continue
            receiver = ast.unparse(func.value).split(".")[0].split("(")[0]
            if allowed is None:
                offenders.append(f"{py.name}:{node.lineno}: module not in the audit list")
            elif receiver not in allowed:
                offenders.append(f"{py.name}:{node.lineno}: {receiver}.{func.attr}()")
    return offenders


def run_selftest() -> dict:
    """Run the whole pipeline over the fixture deck in a temporary copy."""
    fixture = BUNDLE / "assets" / "fixtures" / "mini-deck"
    steps: dict = {}
    notes: list = []
    if not fixture.exists():
        return {"ok": False, "steps": {}, "notes": [f"no fixture at {fixture}"]}

    offenders = _source_write_audit()
    steps["write audit"] = "ok" if not offenders else "FAIL"
    notes.extend(offenders)

    before = {p.relative_to(fixture): p.read_bytes()
              for p in fixture.rglob("*") if p.is_file()}

    with tempfile.TemporaryDirectory() as td:
        work = Path(td) / "mini-deck"
        shutil.copytree(fixture, work)
        config = work / "canva.config.json"
        env = dict(os.environ)
        env.pop("CANVA_CONFIG", None)
        entry = str(BUNDLE / "scripts" / "canva_sync.py")

        def run(args, expect=0):
            res = subprocess.run([sys.executable, entry, *args, "--config", str(config)],
                                 capture_output=True, text=True, env=env, timeout=600)
            return res, res.returncode == expect

        def tail(res):
            # verify reports its diffs on stdout; build its warnings on stderr.
            return "\n".join(s for s in (res.stdout.strip(), res.stderr.strip()) if s)[-500:]

        res, ok = run(["build"])
        steps["build"] = "ok" if ok else f"FAIL rc={res.returncode}"
        if not ok:
            notes.append(tail(res))

        if find_chrome():
            res, ok = run(["verify"])
            steps["verify"] = "ok" if ok else f"FAIL rc={res.returncode}"
            if not ok:
                notes.append(tail(res))
            res, ok = run(["extract"])
            steps["extract"] = "ok" if ok else f"FAIL rc={res.returncode}"
            if ok:
                res, ok = run(["ops", "--summary", "--json"])
                steps["ops"] = "ok" if ok else f"FAIL rc={res.returncode}"
                if ok:
                    res, ok = run(["ops", "--page", "01", "--phase", "elements", "--chunk", "1"])
                    try:
                        json.loads(res.stdout)
                    except json.JSONDecodeError:
                        ok = False
                    steps["ops elements"] = "ok" if ok else "FAIL"
                res, refused = run(["ops", "--page", "01", "--phase", "elements",
                                    "--chunk", "1", "--dialect", "canva-mcp-public"], expect=1)
                steps["public dialect refuses"] = "ok" if refused else "FAIL"
                dump = work / "dump.json"
                dump.write_text(json.dumps(
                    {"design_id": "D1", "document": {"pages": [{"id": "P1", "elements": [
                        {"id": "LB1", "type": "text", "textRegions": [{"characters": "Mini deck"}]},
                        {"id": "LB2", "type": "text",
                         "textRegions": [{"characters": "not in the "}, {"characters": "repo"}]},
                    ]}]}}), encoding="utf-8")
                res, differs = run(["check", "--dump", str(dump)], expect=1)
                steps["check reports a difference"] = "ok" if differs else "FAIL"
                if differs and "not in the repo" not in res.stdout:
                    steps["check reports a difference"] = "FAIL: textRegions not read"

        else:
            steps["verify"] = "skipped: no chrome"
            notes.append("no browser found, so verify, extract, ops and check were skipped")

        # The probe must catch a field the connector does not accept, not
        # only a missing tool or op type.
        def op(t, props, req):
            return {"properties": {"type": {"const": t}, **{k: {} for k in props}},
                    "required": ["type", *req]}
        schema = {"tools": [{"name": "read-design"}, {"name": "edit-design", "inputSchema": {
            "properties": {"operations": {"items": {"anyOf": [
                op("add_page", ["width", "height", "background_color", "title"], []),
                op("replace_speaker_notes", ["page_id", "notes"], ["page_id", "notes"]),
                op("insert_shape", ["page_id", "top", "left", "width", "height", "path",
                                    "view_box_width", "view_box_height", "color",
                                    "stroke_color", "stroke_weight", "rotation"], ["page_id"]),
                op("insert_fill", ["page_id", "asset_type", "asset_id", "alt_text", "top",
                                   "left", "width", "height"], ["page_id"]),
                op("add_text", ["page_id", "text", "top", "left", "width", "rotation"],
                   ["page_id", "text"]),
                {"properties": {"type": {"const": "format_text"}, "locator_id": {},
                                "formatting": {"properties": {k: {} for k in (
                                    "font_size", "color", "text_align", "line_height",
                                    "font_weight", "font_style")}}},
                 "required": ["type", "locator_id", "formatting"]},
            ]}}}}}]}
        dump = work / "tools.json"
        dump.write_text(json.dumps(schema), encoding="utf-8")
        res, ok = run(["probe", "--tools", str(dump)])
        steps["probe accepts matching fields"] = "ok" if ok else "FAIL"
        schema["tools"][1]["inputSchema"]["properties"]["operations"]["items"]["anyOf"][-1][
            "properties"]["element_ref"] = schema["tools"][1]["inputSchema"]["properties"][
            "operations"]["items"]["anyOf"][-1]["properties"].pop("locator_id")
        dump.write_text(json.dumps(schema), encoding="utf-8")
        res, refused = run(["probe", "--tools", str(dump)], expect=1)
        steps["probe refuses a renamed field"] = "ok" if refused else "FAIL"

        # Writing outside the output folder must be refused, whatever is asked.
        try:
            settings = load(str(config))
            settings.write_text(work / "deck.css", "clobbered")
            steps["write guard"] = "FAIL: wrote into the deck folder"
        except ConfigError:
            steps["write guard"] = "ok"

    after = {p.relative_to(fixture): p.read_bytes()
             for p in fixture.rglob("*") if p.is_file()}
    unchanged = before == after
    steps["fixture untouched"] = "ok" if unchanged else "FAIL"
    if not unchanged:
        notes.append("the fixture's own files changed during the run")

    ok = all(v == "ok" or v.startswith("skipped") for v in steps.values())
    return {"ok": ok, "steps": steps, "notes": notes}


# -- guard -------------------------------------------------------------------


def _deny(reason: str) -> int:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))
    return 0


def guard_main(argv, explicit=None) -> int:
    ap = argparse.ArgumentParser(
        prog=f"{COMMAND} guard",
        description="Refuse an edit aimed outside the Canva sync's output folder.")
    ap.add_argument("--hook", action="store_true",
                    help="read a PreToolUse event on stdin")
    ap.add_argument("--no-edits", action="store_true",
                    help="deny direct file edits, including Codex apply_patch calls")
    ap.add_argument("--path", help="check one path instead of reading a hook event")
    args = ap.parse_args(argv)

    if args.no_edits:
        if not args.hook or args.path:
            ap.error("--no-edits requires --hook and cannot be combined with --path")
        try:
            event = json.loads(sys.stdin.read())
            if not isinstance(event, dict):
                raise ValueError("expected a hook event object")
        except (ValueError, TypeError):
            return _deny("The Canva sync guard could not read the hook event.")
        if str(event.get("tool_name", "")).lower() in EDIT_TOOLS | {"apply_patch"}:
            return _deny("The Canva sync has no direct file-editing tools. Use the guarded sync scripts.")
        return 0

    try:
        settings = load(explicit)
    except ConfigError:
        # No config here: this is not a repository the sync owns, so it has no
        # opinion about the edit.
        return 0

    if args.path:
        return 0 if settings.writable(Path(args.path)) else _deny(
            f"{args.path} is outside {settings.output_dir}")

    if not args.hook:
        ap.error("pass --hook or --path")

    try:
        event = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0

    tool = str(event.get("tool_name", "")).lower()
    if tool not in EDIT_TOOLS:
        return 0
    tool_input = event.get("tool_input") or {}
    target = (tool_input.get("file_path") or tool_input.get("filePath")
              or tool_input.get("notebook_path") or tool_input.get("notebookPath"))
    if not target:
        return 0
    if settings.writable(Path(target)):
        return 0
    return _deny(
        f"The Canva sync is one way: the repository is the source of truth and Canva "
        f"is written to, never read back into it. {target} is outside "
        f"{settings.output_dir}. If this edit is a real deck change, make it outside "
        f"the canva-sync agent and rebuild."
    )


# -- entry point -------------------------------------------------------------


def main(argv=None, settings=None, mode="doctor"):
    settings = settings or cfg()
    ap = argparse.ArgumentParser(prog=f"{COMMAND} {mode}",
                                 description=__doc__.splitlines()[0])
    ap.add_argument("--full", action="store_true", help="doctor: also run selftest")
    ap.add_argument("--json", action="store_true", help="print the report as JSON")
    args = ap.parse_args(argv)

    if mode == "selftest":
        report = run_selftest()
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            for k, v in report["steps"].items():
                print(f"  {'ok  ' if v == 'ok' else v.split(':')[0]:<4} {k}", file=sys.stderr)
            for n in report["notes"]:
                print(f"  ! {n}", file=sys.stderr)
        return 0 if report["ok"] else 1

    report = run_doctor(settings, full=args.full)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)
    return 0 if report["ok"] else 1


def _activate_for_tests(path):  # pragma: no cover - used by selftest subprocesses
    return activate(load(path))
