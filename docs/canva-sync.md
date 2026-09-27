# Syncing the folio to Canva

<!-- cspell:ignore EXPERIMENTATIONAND -->

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
| `canva.local.json` | Design id, page id map, asset id map for one Canva account | No. Copy `canva.local.example.json` and fill in your ids |
| `build/canva/canva-import-rev.html` | The flattened deck, pages in reverse (the order Canva's importer reads) | No |
| `build/canva/canva-layout.json` | Per page: ordered shapes, images and texts with geometry and style | No |
| `build/canva/verify/` | Reference and export renders and diffs from the last verify | No |

To set it up, copy the example and edit the copy:

```text
cp canva.local.example.json canva.local.json
```

- `design_id` is the id in the design's Canva URL, `canva.com/design/<design_id>/edit`.
- `pages` maps a deck page label to a Canva page id. Leave it as `{}` and run
  `python .agents/skills/canva-sync/scripts/canva_sync.py check --dump design.json --refresh-ids` on the
  connector's `read-design` output to fill it in; the ids start with `PB`.
- `assets` maps an image's filename, as the deck refers to it, to a Canva asset id (starting `MA`) for an image
  already uploaded to the account. [Uploading the images](#uploading-the-images) says how to put them there
  from this repository. Leave it as `{}` and every image is pushed as a placeholder rectangle.

Replace or remove every `x` placeholder before pushing: an id that is not real is sent to Canva as it stands.

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

## Uploading the images

The connector can put local files into the account's media library, so the images do not have to be uploaded
in the Canva app by hand. All 53 folio images went up this way on 28 September 2026:

1. `create-upload-url` returns a one-time upload URL. It takes one request and expires after 30 minutes, so ask
   for one per file.
2. POST the file's bytes to it:

   ```text
   curl -sS -X POST -H "Content-Type: application/octet-stream" --data-binary @design-system/assets/i1.png "<upload url>"
   ```

   A `201` response carries `{"mediaId":"MA..."}`. `get-assets` with that id confirms Canva holds the image.
3. Record the id in `canva.local.json` under `assets`, keyed by the filename as the deck refers to it:
   `"i1.png": "MA..."`.
4. Run `ops --summary --json` and check that `unmapped_assets` is empty.

Uploading is a separate step from the push, run in the main session with the person's go-ahead. It writes into
their Canva media library and into `canva.local.json`, and the Canva Sync agent has no edit tool for either.

### SVGs with text

Twelve of the fourteen SVGs carry text: the pattern pieces (`pattern-*-measured.svg`), the production drawings
(`production-*.svg`) and the cut layouts (`cut-layout-*.svg`). Canva's SVG import has no PT Serif, so it draws
their labels in a wider fallback face and clips a caption that runs to the edge. Upload a PNG render of each
instead, recorded under the SVG's name so the deck's references still match:

- Put the SVG in an `<img>` at its own millimetre size and screenshot it with headless Chrome at
  `--force-device-scale-factor=4` on a transparent background. That is the deck's own rendering at four times
  96 dpi, which is enough for print.
- PT Serif has to be installed on the machine. An SVG loaded through `<img>` cannot fetch web fonts, so without
  it the render falls back to another face as well.
- Keep the renders under `build/canva/`. They are generated; the SVG stays the source.

The two SVGs without text, `house-mark.svg` and `draw_overskirt.svg`, upload as they are.

## What crosses and what does not

- Geometry, stacking order, colours, text content, sizes, alignment and the mapped images all cross. So do bold
  and italic when they apply to a whole text box. The 60 degree masthead transition crosses as a mitred polygon
  shape.
- Font families do not cross. The format operation has no family parameter, so text lands in Canva's default
  face, Arimo, at the correct size and weight. Apply Fraunces (display) and PT Serif (body) from the brand kit in
  Canva. The brand kit also wants the sixteen area hexes from the top of `deck.css`.
- Arimo is wider than PT Serif. A paragraph can take an extra line, and short boxes such as "Student No.
  12345678" and "Page 2 of 12" in the footer wrap. On a dense page that makes boxes overlap; see
  [Before committing a page](#before-committing-a-page).
- Bold, italic and underlined words inside a paragraph come out in the paragraph's own style: the "The ledger."
  lead-in on page 1, *Wednesday* in a caption, and the source links on page 2.
- The page background is white, not `#FEFBFC`. There is no operation to set an existing page's background;
  `add_page` sets it only for a new page.
- Hatched fills on the pattern-piece plates and the stitch rows (`.rule-fine`, drawn as a repeating background
  image) flatten to the `pattern_fill` tone. A stitch row arrives as a pale solid bar.
- Plate numbers sit at the left of their circles. `.plate-num` centres its digit with flexbox, and extract reads
  `text-align`, which is `start`.
- Images map by filename to asset ids in `canva.local.json`. Unmapped images push as placeholder rectangles that
  can be filled afterwards.
- `ops --summary` lists every image the deck uses that the local map does not cover. Run it after any rename
  under `design-system/assets/`, because the map is keyed by filename and goes stale silently.

## Before committing a page

The thumbnail is too small to show these, so check the draft itself before asking the person to approve it:

- **Overlaps.** Compare the text boxes in the last `edit-design` response: a box whose bottom runs past the top
  of the next box in the same column overlaps it. On page 12 one paragraph ran 13 px into the next and a table
  cell spilled into the row below. Move the lower box down, or widen the box.
- **The 12 pt floor.** 16 px is 12 pt on the 1123 px A3 page. Never set text smaller to clear an overlap. On
  28 September two page 12 cells were set to 15 px, which is 11.25 pt, to stop one. Canva flags nothing, but the
  NESA Assessor measures the smallest text on every page. Move or widen the box, or say that the deck needs
  fewer words.
- **Line breaks.** Extract reads `textContent`, which drops a `<br/>` without leaving a space. The pages 09 to 12
  mastheads, `Investigation, Experimentation<br/>and Evaluation`, come out as "EXPERIMENTATIONAND EVALUATION".
  Until extract is fixed, send that box's text with a `\n` where the `<br/>` is, and format the page with
  `--ids`, because `--from-dump` cannot pair the changed text.

## Verify and its tolerance

Verify renders each page twice, once from the deck and once from the flattened export, and diffs the two images.
The default tolerance is 0.35 per cent of a page's pixels. All twelve pages are well inside it. On 28 September
2026 the worst was page 02 at 0.146 per cent, and every differing pixel was a letter drawn a fraction of a pixel
apart, not a moved line.

Page 12 used to carry a `known_residuals` entry of 0.5 per cent. Its evaluation text is a two-column block with
`text-wrap: pretty`, and splitting the columns once made Chrome break one word differently. On 28 September it
measured 0.102 per cent, with the remaining pixels on the table hairlines and none in the columns, so the entry
was removed. `known_residuals` is now empty.

A residual is recorded only when it is understood, and written down here when it is. It is not a way to get a
page through the gate.

## The connector

The pipeline pushes through Canva's connector as it is exposed today (checked 28 September 2026): `read-design`
opens an editing transaction, `edit-design` applies operations to one page at a time and then commits or cancels,
elements are addressed by locator id, and `create-upload-url` takes local images. The `probe` command is the
gate: it checks the connector's tool list, operation types and field names against the dialect before anything
is pushed. The dialect was verified on 26 September 2026 by pushing page 01, reading it back and committing it,
and again on 28 September 2026 with pages 02 and 12 and their uploaded images. Nothing is committed to the design
without the person approving the preview.

What crosses and what does not is listed [above](#what-crosses-and-what-does-not).

Canva's older public tool set could replace text in an existing design but could not create a page's elements. The
route for a connector that still speaks it is to publish the flattened HTML at a public URL and import it, which a private
repository cannot do without publishing the file somewhere. `references/canva-connector.md` in the bundle has
the detail.

## Other routes

- `python .agents/skills/canva-sync/scripts/canva_sync.py build --pdf` also writes
  `build/canva/canva-import-A3.pdf`, a true-size A3 PDF of the twelve pages (about 100 MB, since the plates are
  embedded at print resolution). Canva's own upload takes PDF but rebuilds it less editably. A fallback, not the
  pipeline.

The print proof does not come from Canva. It comes from `scripts/preview.ps1 -Item folio` and Ctrl+P at 100%,
the only route that holds true millimetres.
