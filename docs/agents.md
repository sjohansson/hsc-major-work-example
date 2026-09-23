# Agents in this repo

Two agents work on this repo: `canva-sync`, which pushes the deck into Canva, and `nesa-assessor`, which marks
the exported folio PDF. Each exists in three files. This page says why, and what each file teaches.

## One agent, three files

| Tier | canva-sync | nesa-assessor | Who reads it |
| --- | --- | --- | --- |
| Agnostic | `.agents/agents/canva-sync.md` | `.agents/agents/nesa-assessor.md` | Any host, and any person |
| GitHub Copilot | `.github/agents/canva-sync.agent.md` | `.github/agents/nesa-assessor.agent.md` | Copilot in VS Code |
| Claude Code | `.claude/agents/canva-sync.md` | `.claude/agents/nesa-assessor.md` | Claude Code |

The agnostic file is the agent. It holds the role, the files the agent must read first, what the arguments mean,
the tools it may not have, and the boundaries. Its frontmatter is a `name` and a `description` and nothing else,
because that is all every host agrees on.

The two vendor files are wrappers. Each opens with that host's frontmatter, then one paragraph that says "read
the agnostic file and follow it", then a section headed "What this host adds" that explains every frontmatter
field in plain words. They are twenty to thirty lines each and carry no procedure. If a wrapper and the agnostic
file ever disagree, the agnostic file wins and the wrapper is wrong.

This split exists because the repo is a teaching repo. A student who opens the three files for one agent sees the
same job expressed three ways, and the diff between them is the lesson: what an agent is, and what a host layers
on top of it.

## What each host adds

| Field | GitHub Copilot | Claude Code | What it does |
| --- | --- | --- | --- |
| `name` | Display name, `Canva Sync` | Slug, `canva-sync` | How the agent is picked |
| `description` | Free text | Free text with trigger phrases | When the host offers the agent |
| `argument-hint` | Yes | No | Placeholder text in the chat box |
| `tools` | Allowlist of host tool names | Allowlist of host tool names, MCP patterns allowed | What the agent may call |
| `disallowedTools` | No | Yes | Tools removed even if the list above would allow them |
| `model` | No | Yes, `inherit` here | Which model runs the subagent |
| `hooks` | No | Yes, `PreToolUse` here | A command the host runs before a tool fires |
| Discovery | `.github/agents/*.agent.md` | `.claude/agents/*.md` | Where the host looks |

Neither host scans `.agents/agents/` on its own, so the agnostic file is never run directly. It is read by the
wrappers, and by anyone wiring the agent into a third host.

## The guard, three ways

Both agents have a rule about what they may write. The canva-sync agent may write only under the sync's output
folder. The nesa-assessor agent may write only under `build/reviews/`. The three tiers enforce that rule
differently, and the difference is worth studying.

- **Agnostic**: the rule is stated. The file says which tools the agent must not have and where it may write.
  Whoever wires it into a host is told to withhold the edit tool, or to add the guard where the host has hooks.
- **Copilot**: the rule is partly mechanical. The canva-sync wrapper leaves `edit` out of `tools:`, so the agent
  cannot write at all. The nesa-assessor wrapper has to keep `edit` for the review, so its rule about writing
  nowhere else is one the agent follows rather than one the host enforces.
- **Claude Code**: the rule is mechanical for both. A `PreToolUse` hook runs a guard script before any editing
  tool fires. `canva_sync.py guard --hook` denies a write outside the sync's output folder; `review_guard.py
  --hook` denies a write outside `build/reviews/`. The guard reads the tool call as JSON on stdin, checks the
  path, and answers with a deny and a reason. The agent never gets to make the write.

The two guards live with their skills, not with the wrappers: `.agents/skills/canva-sync/scripts/` and
`.agents/skills/get-nesa-grading-rules/scripts/`. Any host with a pre-tool hook can run them. Try one by hand:

```pwsh
python .agents/skills/get-nesa-grading-rules/scripts/review_guard.py --path build/reviews/x.md   # exit 0
python .agents/skills/get-nesa-grading-rules/scripts/review_guard.py --path docs/x.md            # exit 1
```

## Skills

The skills live once, in `.agents/skills/`. Copilot scans that folder. Claude Code loads project skills from
`.claude/skills/`, so its wrappers tell the agent to read `SKILL.md` by path. There is no copy of a skill in a
vendor folder, and there should not be one: a skill is a procedure, and a procedure lives in one place.

| Skill | Holds |
| --- | --- |
| `canva-sync` | The Canva pipeline: scripts, references, dialects, a fixture deck, and the guard |
| `get-nesa-grading-rules` | The pointer to the two marking documents, and the review guard |

## Adding a third host

Read the agnostic file. Give the agent read, search and run tools. For canva-sync withhold every editing tool;
for nesa-assessor allow editing and, if the host has a pre-tool hook, run the guard. Put the host's own
frontmatter in a wrapper in that host's folder and write a "What this host adds" section for it. Do not copy the
body. Then add a column to the tables above.
