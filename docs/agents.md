# Agents in this repo

Two agents work on this repo: `canva-sync`, which pushes the deck into Canva, and `nesa-assessor`, which marks
the exported folio PDF. Each has one shared definition and three host wrappers.

## One agent, four files

| Host | canva-sync | nesa-assessor |
| --- | --- | --- |
| Agnostic | `.agents/agents/canva-sync.md` | `.agents/agents/nesa-assessor.md` |
| GitHub Copilot | `.github/agents/canva-sync.agent.md` | `.github/agents/nesa-assessor.agent.md` |
| Claude Code | `.claude/agents/canva-sync.md` | `.claude/agents/nesa-assessor.md` |
| Codex | `.codex/agents/canva-sync.toml` | `.codex/agents/nesa-assessor.toml` |

The agnostic file is the agent. It holds the role, required reading, argument meanings, and boundaries. Its
frontmatter contains only `name` and `description`. The procedure stays in the skill or marking documents it
names, so changing a host never changes the marking or sync rules.

The vendor files are thin wrappers. Each says to read the agnostic file and explains what its host adds.
Copilot and Claude Code use Markdown with frontmatter; Codex uses a standalone TOML file with instructions
and comments. A wrapper never copies the procedure. If it disagrees with the agnostic file, the wrapper is wrong.

This split is part of the teaching example: the four files show the same role and the controls each host adds.
None of these hosts discovers the Markdown files in `.agents/agents/` as native agents. The wrappers read them.

## What each host adds

| Setting | GitHub Copilot | Claude Code | Codex |
| --- | --- | --- | --- |
| Identity | `name`, display name | `name`, slug | `name`, agent name |
| Selection | `description` | `description` | `description` |
| Instructions | Markdown body | Markdown body | `developer_instructions` |
| Argument hint | `argument-hint` | None | Put arguments in the delegation prompt |
| Tool controls | `tools` allowlist, `agents: []` | `tools` and `disallowedTools` | Permission profiles and pre-tool hooks |
| Model | Host default | `model: inherit` | Omit `model` and `model_reasoning_effort` |
| Write guard | Tool list, instructions, and optional agent-scoped hook | `PreToolUse` command hook | Inline `hooks.PreToolUse` command hook |
| Filesystem boundary | Host permissions | Host permissions | `default_permissions` and a named profile |
| Discovery | `.github/agents/*.agent.md` | `.claude/agents/*.md` | `.codex/agents/*.toml` |

Codex model and reasoning settings use the parent's values unless configured subagent defaults or explicit
spawn settings select others. The wrappers deliberately do not pin a model. There is no Codex `tools` allowlist
or `disallowedTools` field in these files; copying another host's frontmatter would not enforce its restrictions.

## The guards

The assessor writes review artefacts only under `build/reviews/`. The Canva scripts write generated files under
the configured `output_dir`, currently `build/canva/`. The existing `check --refresh-ids` command may also update
the ignored `canva.local.json`; it is account metadata, not folio content.

- **Agnostic**: the files state the boundaries and tell the host integrator which controls are needed.
- **Copilot**: the Canva wrapper omits `edit`; both wrappers set `agents: []` because neither workflow needs
  delegation. The assessor keeps `edit` to write reviews and adds an agent-scoped hook for hosts with
  `chat.useCustomAgentHooks` enabled. Those controls do not restrict writes made through shell commands, so the
  host's permissions and the agent's instructions still matter.
- **Claude Code**: the Canva wrapper removes direct editing tools. Both wrappers register the shared guard for
  editing tools. Their hooks check file paths, not arbitrary shell commands.
- **Codex**: the Canva hook denies all direct file edits, including edits inside the output folder. Its scripts
  do the writing. The assessor hook checks every `apply_patch` add, update, delete, and move path against
  `build/reviews/`. A patch with one forbidden target is denied in full. The filesystem profiles also constrain
  shell writes inside the sandbox. Both profiles allow temporary scratch directories for tools.

The guards live with their skills: `.agents/skills/canva-sync/scripts/` and
`.agents/skills/get-nesa-grading-rules/scripts/`. The assessor guard accepts both Claude file-path events and
Codex patch events. It resolves paths against the hook's working directory and follows filesystem links before
checking the boundary. Unreadable editing payloads are denied.

Try the assessor boundary directly:

```pwsh
python .agents/skills/get-nesa-grading-rules/scripts/review_guard.py --path build/reviews/x.md
python .agents/skills/get-nesa-grading-rules/scripts/review_guard.py --path docs/x.md
```

The first exits `0`; the second exits `1`. Run `python -m unittest discover -s scripts -p "test_agent_guards.py"`
to exercise the registered Codex hook commands, mixed patches, moves, traversal, and malformed inputs.

## Using the Codex agents

Use a current local Codex client with standalone custom agents, permission profiles, and inline hooks.
Open this repository as the workspace root. The `.codex/agents/` files are discovered directly; no central
agent registry, custom prompt file, or experimental multi-agent toggle is needed.

Review and trust the project through Codex. Non-managed hooks need separate trust: use `/hooks` in the CLI to
inspect and trust the exact hook definitions. Changed hooks need review again. Check the hooks for the selected
agent before its first run; a skipped or failed hook is not protection. The wrappers enable `features.hooks`
but cannot override administrator policy or supply user trust.

Delegate explicitly, with the same arguments the other hosts accept:

```text
Delegate to canva-sync with page labels 01 03. Wait for its report.
Delegate to canva-sync with all. Wait for its report.
Delegate to canva-sync with check. Wait for its report.
Delegate to canva-sync with no arguments and return its preparation report.
Delegate to nesa-assessor with output/folio.pdf. Wait for its review.
Delegate to nesa-assessor with no PDF argument to mark the current export.
```

These are delegated specialists. The CLI's `/agent` command inspects their threads; it does not register an
agent or replace the main conversation's instructions. Skills remain available in the main conversation too.

The Codex wrappers set `default_permissions` to a role-specific profile extending `:read-only`. They grant
repository writes only to their output paths, plus the Canva identifier file where applicable. They grant
temporary-directory writes for browser profiles and scratch files. Command networking stays disabled by
default; network approvals, web tools, and connectors use the host's controls. Install Python, the project
dependencies, and lint tools before delegation, since the agents cannot install into repository source folders.

Profile paths are relative to each effective workspace root. Start the delegated work at the repository root,
without unrelated writable roots. If `canva.config.json` changes `output_dir` or `local_ids`, update the Canva
profile to match before the next run. The hook launcher itself finds the Git root, so its script path also
works when the parent starts in a repository subdirectory.

The parent session's live permission overrides and managed policy can take precedence over an agent profile.
Existing `sandbox_mode` settings also prevent permission profiles from taking effect; use the current profile
configuration consistently in the host. The wrappers instruct the agent to report an inactive profile or hook
before doing protected work. They do not change the user's global configuration or trust settings.

Hooks cover supported local tool calls, not every hosted or connector action. Filesystem profiles constrain
commands inside the sandbox, not a remote filesystem connector. The agents must use local tools for local files and
must not bypass their boundaries through an alternative tool or elevated command. This distinction matters:
an instruction, a hook, and an operating-system sandbox are different controls.

Canva connectors are inherited from the parent session. The skill probes the connector actually available;
the wrapper does not assume an MCP server name, invent credentials, or install a connector. Without one, the
agent completes the preparation gates and reports that the push is unavailable.

Copilot configuration was checked against the official GitHub and VS Code documentation on 23 September 2026:
[custom agents](https://docs.github.com/en/copilot/reference/custom-agents-configuration),
[creating custom agents](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents),
[VS Code custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents), and
[agent hooks](https://code.visualstudio.com/docs/agent-customization/hooks).

Codex configuration was checked against the official documentation on 23 September 2026:
[custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents),
[hooks](https://learn.chatgpt.com/docs/hooks),
[permission profiles](https://learn.chatgpt.com/docs/permissions), and
[configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).

## Skills

Skills live once, in `.agents/skills/`. Codex and Copilot discover that folder. Claude Code's wrappers read
`SKILL.md` by path. Every wrapper also names the required reading explicitly, so it never depends on a skill
being selected automatically. There is no duplicate procedure in a vendor folder.

| Skill | Holds |
| --- | --- |
| `canva-sync` | The Canva pipeline, scripts, references, dialects, fixture deck, and write guard |
| `get-nesa-grading-rules` | The pointer to both marking documents and the review guard |

## Adding another host

Read the agnostic file. Give the agent read, search, and run tools. Block direct file editing for Canva;
permit only review artefacts for the assessor. Register the shared guard in the host's actual tool protocol
and test its denial cases. Document which boundaries the host enforces and which remain instructions.
Keep the procedure in its existing source, then add the host to the tables above.
