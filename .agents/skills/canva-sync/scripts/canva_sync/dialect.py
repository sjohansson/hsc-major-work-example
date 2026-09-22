"""Connector dialects: the same page, spelled the way one connector spells it.

`ops` builds abstract operations - notes, shape, image, text, format - that say
what has to happen to a page without naming any connector's vocabulary. A
dialect file under `assets/dialects/` turns those into the payload one
connector actually accepts, and states which tools that connector must expose.

Two ship with the bundle:

  claude-canva-connector   the vocabulary this pipeline has always emitted
                           (insert_shape / insert_fill / add_text /
                           format_text / replace_speaker_notes). Marked
                           `unverified`: it is not in Canva's public
                           documentation, so a connector that takes it has to
                           prove it by probe before anything is pushed.
  canva-mcp-public         Canva's documented public MCP server. Its editing
                           transaction applies `replace_text` and
                           `find_and_replace_text` only, so it can change text
                           in a design that already exists but cannot create a
                           page's elements. Asking it for the elements phase is
                           an error that names the import-from-URL route.

The probe is the gate. `canva_sync.py probe --tools tools.json` takes a dump of
the connector's tool list - the agent gets that by listing the MCP server's
tools - and reports whether the dialect's required tools are there and, when
the dump carries input schemas that enumerate operation types, whether every op
type the dialect emits is among them. Exit 1 means do not push.

A dialect file:

    {
      "name": "...",
      "status": "verified" | "unverified",
      "required_tools": ["..."],
      "apply_tool": "...",
      "op_types_path": ["properties", "operations", "items", ...],
      "capabilities": {"create_elements": true, ...},
      "ops": {
        "<abstract op>": {
          "type": "<connector op type>",
          "emit": [["from", "<out key>", "<abstract key>"],
                   ["const", "<out key>", <value>],
                   ["nest", "<out key>", [ ...more entries... ]]]
        }
      }
    }

`emit` is an ordered list so the payload's key order is the dialect's business,
not Python's. A `from` entry whose abstract key is absent is skipped, which is
how optional fields (rotation, stroke, italics) stay optional.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from . import COMMAND

DIALECT_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "dialects"


class DialectError(Exception):
    """An unknown dialect, a malformed dialect file, or an op it cannot spell."""


class Dialect:
    def __init__(self, data: dict, path: Path):
        self.path = path
        self.data = data
        self.name = data.get("name") or path.stem
        self.status = data.get("status", "unverified")
        self.required_tools = list(data.get("required_tools", []))
        self.apply_tool = data.get("apply_tool", "")
        self.capabilities = dict(data.get("capabilities", {}))
        self.ops = dict(data.get("ops", {}))

    # -- rendering -----------------------------------------------------------

    def _emit(self, entries, source: dict) -> dict:
        out: dict = {}
        for entry in entries:
            kind, key = entry[0], entry[1]
            if kind == "const":
                out[key] = entry[2]
            elif kind == "from":
                src = entry[2]
                if src in source and source[src] is not None:
                    out[key] = source[src]
            elif kind == "nest":
                nested = self._emit(entry[2], source)
                if nested:
                    out[key] = nested
            else:
                raise DialectError(f"{self.path.name}: unknown emit entry {kind!r}")
        return out

    def render(self, op: dict) -> dict:
        """One abstract op as this connector spells it."""
        kind = op["op"]
        spec = self.ops.get(kind)
        if spec is None:
            raise DialectError(
                f"dialect {self.name!r} has no way to spell a {kind!r} operation"
            )
        return {"type": spec["type"], **self._emit(spec.get("emit", []), op)}

    def render_all(self, ops) -> list:
        return [self.render(o) for o in ops]

    def op_types(self) -> set:
        return {spec["type"] for spec in self.ops.values()}

    def can(self, capability: str) -> bool:
        return bool(self.capabilities.get(capability))


def available() -> list:
    return sorted(p.stem for p in DIALECT_DIR.glob("*.json"))


def load(name: str) -> Dialect:
    path = DIALECT_DIR / f"{name}.json"
    if not path.exists():
        raise DialectError(
            f"no dialect {name!r}; the bundle ships {', '.join(available()) or 'none'}"
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DialectError(f"{path} is not valid JSON: {exc}") from exc
    return Dialect(data, path)


# -- the probe ---------------------------------------------------------------


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def _tool_names(dump) -> dict:
    """Map normalised tool name -> the tool object (or an empty dict)."""
    tools = dump
    if isinstance(dump, dict):
        for key in ("tools", "result", "data"):
            if isinstance(dump.get(key), list):
                tools = dump[key]
                break
            if isinstance(dump.get(key), dict) and isinstance(dump[key].get("tools"), list):
                tools = dump[key]["tools"]
                break
    found = {}
    if isinstance(tools, list):
        for t in tools:
            if isinstance(t, str):
                found[_norm(t)] = {}
            elif isinstance(t, dict):
                name = t.get("name") or t.get("tool") or t.get("id")
                if name:
                    found[_norm(name)] = t
    return found


def _enumerated_op_types(tool: dict) -> set:
    """Every enum value under the tool's schema that looks like an op type.

    Connectors describe their apply tool differently, so rather than pin one
    JSON pointer this collects the enums of any property named `type` or
    `operation`. No enums found means the schema does not say, which the probe
    reports as unknown rather than as a failure."""
    found = set()

    def walk(node, key=None):
        if isinstance(node, dict):
            if key in ("type", "operation", "op") and isinstance(node.get("enum"), list):
                found.update(str(v) for v in node["enum"])
            for k, v in node.items():
                walk(v, k)
        elif isinstance(node, list):
            for v in node:
                walk(v, key)

    walk(tool)
    return found


def probe(dialect: Dialect, dump) -> dict:
    tools = _tool_names(dump)
    missing = [t for t in dialect.required_tools if _norm(t) not in tools]
    apply_tool = tools.get(_norm(dialect.apply_tool), {}) if dialect.apply_tool else {}
    declared = _enumerated_op_types(apply_tool)
    wanted = sorted(dialect.op_types())
    unsupported = sorted(t for t in wanted if declared and t not in declared)

    result = {
        "dialect": dialect.name,
        "status": dialect.status,
        "tools_seen": len(tools),
        "required_tools": dialect.required_tools,
        "missing_tools": missing,
        "op_types": wanted,
        "op_types_declared": sorted(declared) if declared else None,
        "unsupported_op_types": unsupported,
    }
    if missing:
        result["ok"] = False
        result["reason"] = "the connector does not expose every tool this dialect needs"
    elif unsupported:
        result["ok"] = False
        result["reason"] = "the apply tool's schema does not list every operation type"
    else:
        result["ok"] = True
        result["reason"] = (
            "tools match; the operation vocabulary is still unconfirmed because the "
            "schema does not enumerate it - push one page and read it back first"
            if declared == set() else "tools and operation types both match"
        )
    return result


def main(argv=None, settings=None):
    ap = argparse.ArgumentParser(
        prog=f"{COMMAND} probe",
        description="Check a connector's tool list against the configured dialect.",
    )
    ap.add_argument("--tools", required=True,
                    help="the connector's tool list as JSON, a file path or - for stdin")
    ap.add_argument("--dialect", help="override the dialect named in the config")
    ap.add_argument("--list", action="store_true", help="list the dialects the bundle ships")
    args = ap.parse_args(argv)

    if args.list:
        print(json.dumps(available()))
        return 0

    d = load(args.dialect or (settings.dialect if settings else "claude-canva-connector"))
    raw = sys.stdin.read() if args.tools == "-" else Path(args.tools).read_text(encoding="utf-8")
    try:
        dump = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"the tool list is not JSON: {exc}", file=sys.stderr)
        return 2

    result = probe(d, dump)
    print(json.dumps(result, indent=2))
    if not result["ok"]:
        print(f"  probe failed: {result['reason']}", file=sys.stderr)
        return 1
    if d.status != "verified":
        print(f"  dialect {d.name!r} is marked {d.status}: push one page and read it "
              f"back before pushing the rest", file=sys.stderr)
    return 0
