"""Refuse an edit aimed outside build/reviews/.

A pre-tool hook for any host that has one. It reads a tool call as JSON on stdin,
finds the file path the call would write, and denies the call unless that path is
under build/reviews/ in the repository that holds this script. It never fails
loudly. Malformed hook events and unrecognised patch payloads are denied, because
the guard cannot establish that their targets stay inside the review folder.

    python review_guard.py --hook          read a tool call on stdin
    python review_guard.py --path FILE     check one path and exit 0 or 1
"""

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
ALLOWED = REPO / "build" / "reviews"
EDIT_TOOLS = {
    "edit", "multiedit", "write", "notebookedit", "apply_patch",
    "create_file", "replace_string_in_file", "edit_notebook_file",
}


def writable(path: Path) -> bool:
    target = path.resolve() if path.is_absolute() else (REPO / path).resolve()
    return ALLOWED == target or ALLOWED in target.parents


def deny(reason: str) -> int:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))
    return 0


def patch_targets(command: str) -> list[str]:
    """Collect every source and destination path from a Codex patch."""
    lines = command.strip().splitlines()
    if len(lines) < 3 or lines[0] != "*** Begin Patch" or lines[-1] != "*** End Patch":
        raise ValueError("The review guard requires a complete apply_patch payload.")
    prefixes = ("*** Add File: ", "*** Update File: ", "*** Delete File: ", "*** Move to: ")
    targets = [line[len(prefix):] for line in lines for prefix in prefixes if line.startswith(prefix)]
    if not targets or any(not target.strip() for target in targets):
        raise ValueError("The review guard could not identify every patch target.")
    return targets


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="review_guard.py", description=__doc__.splitlines()[0])
    ap.add_argument("--hook", action="store_true", help="read a pre-tool event on stdin")
    ap.add_argument("--path", help="check one path instead of reading an event")
    args = ap.parse_args(argv)

    if args.path:
        if writable(Path(args.path)):
            return 0
        print(f"{args.path} is outside {ALLOWED}", file=sys.stderr)
        return 1

    if not args.hook:
        ap.error("pass --hook or --path")

    try:
        event = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return deny("The review guard could not read the hook event.")

    if not isinstance(event, dict):
        return deny("The review guard requires a hook event object.")
    tool = str(event.get("tool_name", "")).lower()
    if tool not in EDIT_TOOLS | {"apply_patch"}:
        return 0
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return deny("The review guard requires file-edit arguments.")
    try:
        if tool == "apply_patch":
            command = tool_input.get("command") or tool_input.get("input")
            if not isinstance(command, str):
                raise ValueError("The review guard requires the patch in tool_input.command.")
            targets = patch_targets(command)
        else:
            target = (
                tool_input.get("file_path")
                or tool_input.get("filePath")
                or tool_input.get("notebook_path")
                or tool_input.get("notebookPath")
            )
            if not isinstance(target, str) or not target:
                raise ValueError("The review guard requires a target file path.")
            targets = [target]
        cwd = Path(event.get("cwd") or REPO)
        if not cwd.is_absolute():
            raise ValueError("The review guard requires an absolute working directory.")
        for target in targets:
            if not writable(cwd / target):
                break
        else:
            return 0
    except (ValueError, TypeError, OSError, RuntimeError) as exc:
        return deny(f"The review guard could not check the edit: {exc}")
    return deny(
        f"The assessor marks; it never writes folio content. {target} is outside "
        f"{ALLOWED}. A fix is described in the findings table and a person applies it."
    )


if __name__ == "__main__":
    sys.exit(main())
