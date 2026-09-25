"""Connector dialects: the same page, spelled the way one connector spells it.

`ops` builds abstract operations - notes, shape, image, text, format - that say
what has to happen to a page without naming any connector's vocabulary. A
dialect file under `assets/dialects/` turns those into the payload one
connector actually accepts, and states which tools that connector must expose.

Two ship with the bundle:

  claude-canva-connector   Canva's connector as it is exposed today:
                           read-design and edit-design, with add_page /
                           insert_shape / insert_fill / add_text /
                           format_text / replace_speaker_notes, elements
                           addressed by locator id. The default.
  canva-mcp-public         Legacy: the start/perform/commit transaction tools
                           Canva's public server documented before September
                           2026. Its editing transaction applies
                           `replace_text` only, so it cannot create a page's
                           elements. Asking it for the elements phase is an
                           error that names the import-from-URL route.

The probe is the gate. `canva_sync.py probe --tools tools.json` takes a dump of
the connector's tool list - the agent gets that by listing the MCP server's
tools - and reports whether the dialect's required tools are there and, when
the dump carries the apply tool's input schema, whether every op type the
dialect emits is among them and whether every field it emits is one that op
type accepts, with every required field present. Exit 1 means do not push.

A dialect file:

    {
      "name": "...",
      "status": "verified" | "unverified",
      "required_tools": ["..."],
      "apply_tool": "...",
      "path_commands": "MmLl...",   optional: the SVG commands insert_shape accepts
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
        self.path_commands = data.get("path_commands", "")

    def unsupported_path_commands(self, d: str) -> str:
        """The SVG path commands in d this connector will not draw, if it says."""
        if not self.path_commands:
            return ""
        return "".join(sorted({c for c in d if c.isalpha() and c not in "eE"
                               and c not in self.path_commands}))

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


def _op_variants(tool: dict) -> dict:
    """Map op type -> the schema object that describes that op.

    Connectors describe their apply tool differently: one variant per op in an
    anyOf/oneOf with `type` as a const, or a single object whose `type` is an
    enum. This walks the whole schema rather than pinning one JSON pointer.
    A const variant carries its properties, so its fields can be checked; an
    enum only names the types."""
    found: dict = {}

    def walk(node, key=None):
        if isinstance(node, dict):
            props = node.get("properties")
            if isinstance(props, dict) and isinstance(props.get("type"), dict):
                t = props["type"]
                if "const" in t:
                    found[str(t["const"])] = node
                elif isinstance(t.get("enum"), list) and key not in ("formatting",):
                    for v in t["enum"]:
                        found.setdefault(str(v), {})
            if key in ("type", "operation", "op") and isinstance(node.get("enum"), list):
                for v in node["enum"]:
                    found.setdefault(str(v), {})
            for k, v in node.items():
                walk(v, k)
        elif isinstance(node, list):
            for v in node:
                walk(v, key)

    walk(tool)
    return found


def _field_problems(dialect: "Dialect", variants: dict) -> dict:
    """Per op type: emitted fields the schema does not accept, required ones it never emits."""

    def keys(entries):
        out = {}
        for entry in entries:
            out[entry[1]] = entry[2] if entry[0] == "nest" else None
        return out

    def compare(emitted: dict, schema: dict, where: str, problems: list):
        props = schema.get("properties")
        if not isinstance(props, dict):
            return
        for k, sub in emitted.items():
            if k not in props and k != "type":
                problems.append(f"{where}{k}: not accepted")
            elif sub is not None:
                compare(keys(sub), props[k], f"{where}{k}.", problems)
        for k in schema.get("required", []):
            if k != "type" and k not in emitted:
                problems.append(f"{where}{k}: required, never emitted")

    result = {}
    for spec in dialect.ops.values():
        schema = variants.get(spec["type"])
        if not schema:
            continue
        problems: list = []
        compare(keys(spec.get("emit", [])), schema, "", problems)
        if problems:
            result[spec["type"]] = problems
    return result


def probe(dialect: Dialect, dump) -> dict:
    tools = _tool_names(dump)
    missing = [t for t in dialect.required_tools if _norm(t) not in tools]
    apply_tool = tools.get(_norm(dialect.apply_tool), {}) if dialect.apply_tool else {}
    variants = _op_variants(apply_tool)
    declared = set(variants)
    wanted = sorted(dialect.op_types())
    unsupported = sorted(t for t in wanted if declared and t not in declared)
    fields = _field_problems(dialect, variants)
    fields_checked = sorted(t for t in wanted if variants.get(t))

    result = {
        "dialect": dialect.name,
        "status": dialect.status,
        "tools_seen": len(tools),
        "required_tools": dialect.required_tools,
        "missing_tools": missing,
        "op_types": wanted,
        "op_types_declared": sorted(declared) if declared else None,
        "unsupported_op_types": unsupported,
        "fields_checked": fields_checked,
        "field_problems": fields,
    }
    if missing:
        result["ok"] = False
        result["reason"] = "the connector does not expose every tool this dialect needs"
    elif unsupported:
        result["ok"] = False
        result["reason"] = "the apply tool's schema does not list every operation type"
    elif fields:
        result["ok"] = False
        result["reason"] = "the dialect emits fields the apply tool's schema does not accept"
    else:
        result["ok"] = True
        result["reason"] = (
            "tools match; the operation vocabulary is still unconfirmed because the "
            "schema does not enumerate it - push one page and read it back first"
            if declared == set() else
            "tools and operation types match; fields were not checked because the schema "
            "does not describe each operation" if not fields_checked else
            "tools, operation types and fields all match")
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
