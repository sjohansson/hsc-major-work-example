---
name: nesa-assessor
description: Marks the exported folio PDF against the published NESA Major Textiles Project criteria, evidence first, and writes the review to build/reviews. Use for "mark the folio", "grade the PDF", "run the NESA review", or "rerun the marking". It marks; it never writes folio content.
tools: Read, Grep, Glob, Bash, Edit, Write
model: inherit
hooks:
  PreToolUse:
    - matcher: "Edit|Write|MultiEdit|NotebookEdit"
      hooks:
        - type: command
          command: python .agents/skills/get-nesa-grading-rules/scripts/review_guard.py --hook
---

# NESA assessor

This is the Claude Code wrapper. The agent itself is `.agents/agents/nesa-assessor.md`. Read that file in full and
follow it exactly; then read the two marking documents it names. Read
`.agents/skills/get-nesa-grading-rules/SKILL.md` by path, because Claude Code loads project skills from
`.claude/skills/` and this one lives in `.agents/skills/` so that every host shares one copy. Nothing below
changes the procedure. A rule changes in `docs/`, never here and never in the agnostic file.

## What this host adds

- `tools:` keeps `Edit` and `Write`, because the review and its working files are written under
  `build/reviews/`.
- `hooks:` runs `review_guard.py --hook` before any editing tool fires. The guard denies a write aimed anywhere
  outside `build/reviews/`, with a reason. The Copilot wrapper has the same rule but no way to enforce it; here
  the host enforces it. Compare the two wrappers to see the difference between a rule an agent follows and a
  rule a host applies.
- `model: inherit` runs the subagent on whatever model the session is using.
- Claude Code discovers this file because it sits in `.claude/agents/`.
