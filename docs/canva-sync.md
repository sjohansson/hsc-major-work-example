# Syncing the folio to Canva

The repo is the source of truth. The deck is flattened into the shape Canva can read, checked pixel for pixel
against the real deck, measured into an element list, and turned into operations for a Canva connector. A
read-back step compares what Canva holds against the repo.

The sync is one way. An edit made in Canva is reported as a difference for a person to decide about; it is never
written back into the deck. The deck is edited by hand, and Canva is caught up by rebuilding.

There is no cover page. NESA has no such concept, and the Canva document matches the deck's twelve pages exactly.

## Where it lives

The whole thing is a self-contained agent skill at
[.agents/skills/canva-sync/](../.agents/skills/canva-sync/): its scripts, its references, its dialect files and
a one-page fixture deck it tests itself against. It knows nothing about this repository except what
[canva.config.json](../canva.config.json) at the root tells it, so the same folder can be copied into another
repository as it stands. `references/config.md` inside the bundle says how.

| File | Holds | Committed |
| --- | --- | --- |
| `canva.config.json` | Deck paths, page size, prop values, webfonts, placeholder colours, known residuals, output folder, dialect | Yes |
| `canva.local.json` | Design id, page id map, asset id map for one Canva account | No. Template: `.agents/skills/canva-sync/assets/canva.local.template.json` |
| `build/canva/canva-import-rev.html` | The flattened deck, pages in reverse (the order Canva's importer reads) | No |
| `build/canva/canva-layout.json` | Per page: ordered shapes, images and texts with geometry and style | No |
| `build/canva/verify/` | Reference and export renders and diffs from the last verify | No |

Setup: `pip install -r requirements.txt`, and Chrome or Edge on `PATH` or named in `CHROME_PATH`.

## Running it yourself

```pwsh
python .agents/skills/canva-sync/scripts/canva_sync.py doctor
python .agents/skills/canva-sync/scripts/canva_sync.py all
python .agents/skills/canva-sync/scripts/canva_sync.py ops --page 01 --phase elements --chunk 1
python .agents/skills/canva-sync/scripts/canva_sync.py check --dump design.json
```

`doctor` checks everything the pipeline needs and names whatever is missing. `all` runs build with verify, then
extract, then an ops summary, and stops at the first failure. `--help` on any command prints the rest, and every
command takes `--config PATH`.

## Running it as an agent

The push itself needs a Canva connector, which is a conversation-side tool rather than something a script can
call. That is what the agent is for.

The agent is [.agents/agents/canva-sync.md](../.agents/agents/canva-sync.md). It is written for any host and
holds the whole procedure: what the agent reads, what it may not have, and what the arguments mean. Three thin
wrappers wire it into the hosts this repo uses, and [agents.md](agents.md) compares the host controls:

- **GitHub Copilot / VS Code**: pick the **Canva Sync** agent
  ([.github/agents/canva-sync.agent.md](../.github/agents/canva-sync.agent.md)) and give it page labels, `all`,
  or `check`. It has no edit tool.
- **Claude Code**: ask for the **canva-sync** subagent
  ([.claude/agents/canva-sync.md](../.claude/agents/canva-sync.md)), for example "sync the deck to Canva" or
  "check Canva against the repo". It disallows the edit tools and runs a hook that denies a write outside the
  output folder.
- **Codex**: explicitly delegate to **canva-sync**
  ([.codex/agents/canva-sync.toml](../.codex/agents/canva-sync.toml)) with page labels, `all`, `check`, or no
  arguments. Its permission profile scopes script writes, and its hook denies direct file edits. Follow the
  project and hook trust setup in [agents.md](agents.md#using-the-codex-agents) before the first run.

The agent reads [.agents/skills/canva-sync/SKILL.md](../.agents/skills/canva-sync/SKILL.md) and follows the
gates in it: doctor, then build with verify, then extract, then an answered assets summary, then a connector
probe, then the push page by page, then the read-back. It cannot edit a file in this repository, and the scripts
refuse to write into the deck folder at all.

## What crosses and what does not

- Geometry, stacking order, colours, text content, sizes, weights, italics, alignment and the mapped images all
  cross. The 60 degree masthead transition crosses as a mitred polygon shape.
- Font families do not cross. The format operation has no family parameter, so text lands in Canva's default
  face at the correct size and weight. Apply Fraunces (display) and PT Serif (body) from the brand kit in Canva.
  The brand kit also wants the sixteen area hexes from the top of `deck.css`.
- Hatched fills on the pattern-piece plates flatten to their base tone.
- Images map by filename to asset ids in `canva.local.json`. Upload the assets in the Canva app first, then
  record the ids. Unmapped images push as placeholder rectangles that can be filled afterwards.
- `ops --summary` lists every image the deck uses that the local map does not cover. Run it after any rename
  under `design-system/assets/`, because the map is keyed by filename and goes stale silently.

## Verify and its tolerance

Verify renders each page twice, once from the deck and once from the flattened export, and diffs the two images.
The default tolerance is 0.35 per cent of a page's pixels. All twelve pages are well inside it; the worst is
about 0.15 per cent.

Page 12 carries a `known_residuals` entry. Its evaluation text is a two-column block with `text-wrap: pretty`,
and pretty adjusts a paragraph's last lines by looking ahead to its end. In the deck that end is down in column
two; once the column-one fragment is a paragraph of its own it has an end of its own, and Chrome breaks one word
differently. Same words, same column, same height. Canva re-flows text on import in any case.

A residual is recorded only when it is understood, and written down here when it is. It is not a way to get a
page through the gate.

## The connector, and a caveat

The operation vocabulary the pipeline emits by default is not in Canva's public MCP documentation, and nothing
here has ever pushed with it. It is marked `unverified`, and the `probe` command is the gate: it checks the
connector's tool list against the dialect before anything is pushed, and the first page of an unverified dialect
is pushed one chunk at a time and read back.

Canva's documented public server can replace text in an existing design but cannot create a page's elements. The
route for that connector is to publish the flattened HTML at a public URL and import it, which a private
repository cannot do without publishing the file somewhere. `references/canva-connector.md` in the bundle has
the detail.

## Other routes

- `python .agents/skills/canva-sync/scripts/canva_sync.py build --pdf` also writes
  `build/canva/canva-import-A3.pdf`, a true-size A3 PDF of the twelve pages (about 100 MB, since the plates are
  embedded at print resolution). Canva's own upload takes PDF but rebuilds it less editably. A fallback, not the
  pipeline.

The print proof does not come from Canva. It comes from `scripts/preview.ps1 -Item folio` and Ctrl+P at 100%,
the only route that holds true millimetres.
