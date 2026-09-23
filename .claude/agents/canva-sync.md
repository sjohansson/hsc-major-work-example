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

This is the Claude Code wrapper. The agent itself is `.agents/agents/canva-sync.md`. Read that file in full and
follow it exactly; then read `.agents/skills/canva-sync/SKILL.md` by path, because Claude Code loads project skills
from `.claude/skills/` and this one lives in `.agents/skills/` so that every host shares one copy. Nothing below
changes the procedure. A rule changes in the skill, never here and never in the agnostic file.

## What this host adds

- `tools:` names the tools this subagent may use. `mcp__canva__*` is every tool from an MCP server called
  `canva`; rename it if your connector is registered under another name. With no connector, every gate up to the
  push still runs.
- `disallowedTools:` removes the four editing tools outright, so the agent cannot change a file in the
  repository.
- `hooks:` runs `canva_sync.py guard --hook` before any of those tools would fire. The guard reads the tool call,
  checks the target path against the config's `output_dir`, and denies the call with a reason if it is aimed
  anywhere else. That is the one-way rule made mechanical: even if the tool list were widened, the hook still
  stands. Whether a subagent's own hooks are honoured depends on the installed version; the disallowed tools and
  the refusal inside the scripts hold either way.
- `model: inherit` runs the subagent on whatever model the session is using.
- Claude Code discovers this file because it sits in `.claude/agents/`. The agnostic file in `.agents/agents/`
  is not picked up on its own.
