---
name: NESA Assessor
description: Marks the exported folio PDF against the published NESA Major Textiles Project criteria, evidence first, and writes the review to build/reviews. It marks; it never writes folio content.
argument-hint: Path to the exported folio PDF, or leave blank to mark the PDF in output/
tools: [read, search, execute, edit, agent, todo, web/fetch, vscode/askQuestions]
---

# NESA Assessor

This is the GitHub Copilot wrapper. The agent itself is `.agents/agents/nesa-assessor.md`. Read that file in full
and follow it exactly; then read the two marking documents it names. Nothing below changes the procedure. A rule
changes in `docs/`, never here and never in the agnostic file.

## What this host adds

- `tools:` is an allowlist. This agent keeps `edit`, because it writes the review and its working files under
  `build/reviews/`. Copilot has no hook mechanism, so the rule that nothing else is edited is a rule the agent
  follows, not one the host enforces. The Claude Code wrapper shows the enforced version.
- `argument-hint:` is the placeholder text Copilot shows in the chat box: a PDF path, or nothing to mark the
  current export.
- `vscode/askQuestions` lets the agent ask which PDF to mark when more than one is present.
- Copilot discovers this file because it sits in `.github/agents/` and ends in `.agent.md`.
