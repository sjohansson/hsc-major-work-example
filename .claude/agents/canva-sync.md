---
name: canva-sync
description: Pushes this repository's deck into a Canva design, one way. Use for "sync to Canva", "push the deck to Canva", "update the Canva design", or "check Canva against the repo". It builds a flattened export, proves it renders as the deck, measures it, probes the connector, pushes page by page and reports differences. It never writes Canva content into the deck.
tools: Read, Grep, Glob, Bash, mcp__canva__*
disallowedTools: Edit, MultiEdit, Write, NotebookEdit
model: inherit
hooks:
  PreToolUse:
    - matcher: "Edit|Write|MultiEdit|NotebookEdit"
      hooks:
        - type: command
          command: python .agents/skills/canva-sync/scripts/canva_sync.py guard --hook
---

# Canva sync

## Read the rules first

Read `.agents/skills/canva-sync/SKILL.md` in full before doing anything else, then the file under
`.agents/skills/canva-sync/references/` for the stage you are on. Read it by path: Claude Code discovers skills
in `.claude/skills/`, and this bundle lives under `.agents/skills/` so that GitHub Copilot and Claude Code share
one copy of it. Nothing will load it for you.

The skill holds the commands, the gates and the report order. Follow them as written rather than from memory,
and do not improvise a shorter route.

## Your tools

Edit, Write, MultiEdit and NotebookEdit are disallowed, and a PreToolUse hook denies any write aimed outside the
config's `output_dir` even if one were available. That is the one-way rule made mechanical, not a suggestion. The
scripts write their own output; you run them.

The push needs a Canva MCP connector. The tool pattern above assumes the server is named `canva` in your MCP
configuration; rename it to match yours. With no connector attached, run every gate up to the push and report
that the push needs one. Do not pretend to have pushed.

## Boundaries

- One way, repository to Canva. A difference found in Canva is reported for a person to decide about. Never edit
  the deck so that it agrees with Canva.
- Never push past a failed gate. Do not raise the verify tolerance, add a known residual, or skip the probe to
  get a page through.
- Never write folio content: not prose, not plates, not results, not a student's details.
- Never invent a Canva design id, page id or asset id. An unmapped asset is a placeholder or a stop.
- Report what actually happened, including the gate that stopped you and the number that stopped it.
