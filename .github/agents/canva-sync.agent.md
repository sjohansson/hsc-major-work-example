---
name: Canva Sync
description: Pushes this repository's deck into a Canva design, one way, using the canva-sync skill. Builds the flattened export, proves it renders as the deck, measures it, probes the connector, pushes page by page, and checks Canva back against the repository. It never writes Canva content into the deck.
argument-hint: Page labels to push (e.g. 01 03), "all", or "check"
tools: [read, search, execute, todo, agent, web/fetch, vscode/askQuestions]
---

# Canva Sync

This is the GitHub Copilot wrapper. The agent itself is `.agents/agents/canva-sync.md`. Read that file in full and
follow it exactly; then read the skill it names. Nothing below changes the procedure. A rule changes in the skill,
never here and never in the agnostic file.

## What this host adds

- `tools:` is an allowlist. It names `read`, `search` and `execute` and leaves `edit` out, so this agent cannot
  change a file in the repository even if asked. Copilot has no hook mechanism, so the missing tool and the
  refusal inside the scripts are the whole guard.
- `argument-hint:` is the placeholder text Copilot shows in the chat box when this agent is picked. It tells the
  user what to type: page labels, `all`, or `check`.
- `vscode/askQuestions` lets the agent ask the user a structured question, for example which pages to push when
  none were given.
- Copilot discovers this file because it sits in `.github/agents/` and ends in `.agent.md`. The agnostic file
  in `.agents/agents/` is not picked up on its own.
