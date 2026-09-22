# Configuration, and adopting this skill in another repository

## Where the config comes from

`canva.config.json` describes the repository, not the tool, so it lives in the repository and not in this
bundle. It is found in this order, first hit winning:

1. `--config PATH` on any command.
2. The `CANVA_CONFIG` environment variable.
3. `canva.config.json`, then `design-system/canva.config.json`, at the working directory and at each parent
   of it in turn.

Every path in the config resolves against the folder the config was found in, and that folder is the
repository root as far as this skill is concerned. So moving the config moves the root.

`doctor` prints which file it found. If that is not the one you meant, say `--config`.

## The keys

`assets/canva.config.schema.json` is the full schema with defaults and descriptions; point an editor at it.
The short version:

| Key | Default | What |
| --- | --- | --- |
| `deck_dir` | `design-system` | Folder holding the deck, its stylesheet and its assets |
| `deck` | required | The deck file. Its `<section>` elements are the pages, in `data-label` order |
| `deck_css` | `deck.css` | The stylesheet whose cascade the flattener re-implements |
| `assets_dir` | `assets` | Images, relative to `deck_dir`, and it has to be inside it |
| `output_dir` | `build/canva` | Everything generated. Ignore it in git |
| `local_ids` | `canva.local.json` | Canva account identifiers. Ignore it in git |
| `dialect` | `claude-canva-connector` | Which file under `assets/dialects/` spells the operations |
| `title` | `Folio` | Title of the flattened export |
| `page_mm` | `[297, 420]` | The deck's real page size in millimetres |
| `canva_px` | `[1123, 1588]` | The Canva page size in pixels, the element list's coordinate space |
| `background` | `#FEFBFC` | Page ground colour |
| `pattern_fill` | `#F5EFE2` | The flat tone a hatched fill collapses to |
| `props` | `{}` | Values for the deck's `{{ name }}` placeholders |
| `google_fonts` | `[]` | Families loaded into the verify render |
| `thumbnail` | | Two letters and a fill for the export's thumbnail |
| `placeholder` | | Fill and stroke of an unmapped image's rectangle |
| `known_residuals` | `{}` | Per page label, an understood difference in per cent |
| `rewrite_classes` | | Which deck classes carry the structural rewrites |

`ornament` was removed in 1.0. A config that still has it fails validation with a message saying so.

## The local id file

```json
{
  "design_id": "DAF...",
  "pages": { "01": "DAF...:page-id", "02": "..." },
  "assets": { "cover.png": "MAF...", "plate.svg": "MAF..." }
}
```

It names one person's Canva account, so it is git-ignored and `assets/canva.local.template.json` is what gets
committed. `check --refresh-ids` writes it; nothing else does. Without it, operations carry the literal
`PAGE_ID` and every image is a placeholder, which is enough to generate and inspect a push on a fresh clone.

## Adopting the skill in another repository

1. Copy the whole `canva-sync` folder into that repository's `.agents/skills/`. Nothing in it refers to this
   repository.
2. Copy `.github/agents/canva-sync.agent.md` and `.claude/agents/canva-sync.md` across, for whichever hosts
   are used. Both name the bundle path; change it if the bundle sits somewhere else.
3. Copy `assets/canva.config.template.json` to the repository root as `canva.config.json` and fill in the
   paths, the page size and the props.
4. Add the output folder and `canva.local.json` to `.gitignore`.
5. `pip install -r .agents/skills/canva-sync/requirements.txt`, and make sure Chrome or Edge is on `PATH` or
   named in `CHROME_PATH`.
6. `canva_sync.py doctor --full`. It runs every check and then the fixture selftest, so a clean result means
   the bundle works and the repository is wired up.

## Host differences worth knowing

- GitHub Copilot and VS Code discover skills in `.github/skills/`, `.claude/skills/` and `.agents/skills/`.
  Claude Code discovers project skills in `.claude/skills/` only. The bundle lives in `.agents/skills/` so both
  hosts share one copy, which means the Claude Code agent reads `SKILL.md` by path and cannot use the `skills:`
  preload field. Its agent file says so. If Claude Code adds the directory later, nothing here needs changing.
- The Claude Code agent carries its PreToolUse guard hook in its own frontmatter, so the deny applies to that
  agent and not to ordinary work in the repository. Whether subagent frontmatter hooks are honoured depends on
  the installed version; `disallowedTools` and the refusal inside `Settings.write_text` hold either way. A
  repository that wants the guard everywhere can put the same hook in `.claude/settings.json`, but it will then
  deny every write outside the output folder, for every session.
- Copilot has no hook mechanism here. Its agent simply has no `edit` tool.

## Checking a change to the bundle

```text
canva_sync.py selftest
canva_sync.py doctor --config .agents/skills/canva-sync/assets/fixtures/mini-deck/canva.config.json
canva_sync.py all
```

`selftest` runs the whole pipeline over the one-page fixture in a temporary copy, proves the fixture's own files
are untouched, and reads the package syntax tree to prove no module writes a file outside the two guarded
places. CI runs it on every push.

Adding a module means adding it to `ALLOWED_WRITERS` in `doctor.py`, which is the point: a new way to write a
file has to be argued for rather than slipped in.
