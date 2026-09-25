# The Canva connector, the dialects and the probe

## What Canva's connector exposes

Checked on 26 September 2026 through the claude.ai Canva connector. The tools that matter here:

| Tool | Does |
| --- | --- |
| `search-designs` | Find designs in the account |
| `read-design` | Read a design's metadata, pages, content, thumbnails and speaker notes; with `open_transaction: true`, open an editing transaction |
| `edit-design` | Apply operations to one page of an open transaction, then commit or cancel it |
| `import-design-from-url` | Create a design from a document at a public URL |
| `upload-asset-from-url`, `get-assets` | Put images in the media library and list them |
| `export-design` | Export to PDF and other formats |

The editing transaction works like this:

1. `read-design` with `open_transaction: true` (and `"thumbnails"` in `filter.fields` for a before picture) returns a
   `transaction_id`.
2. `edit-design` with that `transaction_id`, a 1-based `page_index`, `finalize: "keep_open"` and an `operations`
   array applies the operations to that page and returns the draft page: its `id` and its `elements`, each with an
   element `id`, and text as `textRegions[].characters`.
3. `edit-design` with `finalize: "commit"` and no operations saves everything. The connector requires the person
   to see a preview and approve before this call. `finalize: "cancel"` with no operations discards everything.
   Neither can carry operations.

Elements are addressed by **locator id**: the page id, a hyphen, and the element id, for example
`PBPLrWbbTNTyFGHq-LBMKbVQbB97s87LB`. `format_text`, `delete_element`, `position_element` and the other edit
operations take `locator_id`; the create operations (`add_text`, `insert_shape`, `insert_fill`,
`replace_speaker_notes`) take `page_id`. `add_page` takes `width`, `height`, `background_color` and `title`.

What the schema will and will not take, and where the pipeline meets it:

- `insert_shape` paths accept only `M L H V C S A Z`. `ops` refuses to emit a path with any other command.
- `format_text` has no font family. Size (a whole number of pixels), `bold` or `normal`, `italic` or `normal`,
  colour as six-digit hex, `start`/`center`/`end` alignment and a line height between 0.5 and 2.5 all cross.
- There is no operation to set an existing page's background colour. `add_page` sets it for a new page.
- Formatting applies to a whole text box. Bold or italic words inside a paragraph (a lead-in, an emphasised term)
  come out in the paragraph's own style.
- Canva's default face is wider than Fraunces and PT Serif, so a paragraph can run a line longer than in the deck
  and short single-line boxes (a footer label, a page number) can wrap. Apply the brand fonts in Canva, or widen
  the box there; the deck is not changed to suit.

The tool set Canva's public server documented before this (`start-editing-transaction`,
`perform-editing-operations`, `commit-editing-transaction`, `cancel-editing-transaction`, `get-design-content`)
could only replace text in an existing design. It no longer appears on the connector.

## The two dialects

`ops` builds abstract operations; a file under `assets/dialects/` spells them for one connector.

**`claude-canva-connector`** is the default, verified on 26 September 2026 by pushing page 01: `add_page`, `insert_shape`, `insert_fill`, `add_text`,
`format_text` and `replace_speaker_notes` through `read-design` and `edit-design`, as described above. Its file
also records the transaction calls and the path commands the connector draws. Its `status` becomes `verified`
once a page pushed with it has been read back and matched.

**`canva-mcp-public`** is the legacy tool set above. `capabilities.create_elements` is false, so asking it for
the elements phase exits 1 and names the import-from-URL route instead of emitting a payload the connector would
reject.

Adding a third is a JSON file, not a code change. `dialect.py` explains the file's shape at the top.

## The probe

```text
canva_sync.py probe --tools tools.json
canva_sync.py probe --tools - --dialect canva-mcp-public
```

List the connector's tools, save that JSON - the whole response, or a bare list of names, either is read - and
run the probe. It checks that every tool the dialect needs is present, ignoring case and the difference between
`-` and `_`. Where the dump carries the apply tool's input schema it also checks that every operation type the
dialect emits is among the schema's types, and, where the schema describes each type's fields, that every field
the dialect emits is accepted and every required field is emitted. It prints its finding as JSON, with
`field_problems` per operation type, and exits 1 when anything does not match.

Save the tool list **with input schemas**. A list of names alone proves only that the tools exist; the field
check is what catches a renamed field such as `element_id` becoming `locator_id` before it reaches Canva.

A pass is not a guarantee. The probe reads field names, not values or behaviour, so the first page pushed with
an unverified dialect still has to be read back as `push-loop.md` describes. When the schema does not describe
the operations the probe says so in its `reason`.

If the tool list cannot be dumped at all, probe by hand: open a transaction, apply one shape operation to a
scratch page, read the page back, and cancel the transaction. If the shape is not there, the vocabulary is
wrong.

## The import-from-URL route

Only a connector that matches the legacy `canva-mcp-public` dialect needs this. There a design is not built
operation by operation. It is imported:

1. `build` the flattened export.
2. Publish `<output_dir>/canva-import-rev.html` at a **public HTTPS URL**. `import-design-from-url` fetches it
   itself, so a private repository, a local file or an authenticated host will not do. This is the step that
   makes the route awkward, and it is worth saying out loud before anyone starts.
3. Import it, which creates the design with its pages.
4. Use `check --dump - --refresh-ids` to record the design id and page ids.
5. Use the `canva-mcp-public` dialect to correct text from then on.

The pages arrive in the file's order, which is why the export is written in reverse: the importer reverses it
back.

## Assets

Images cross only if the account already holds them. Upload them - in the Canva app, or with
`upload-asset-from-url`, which also needs a public HTTPS URL - and record the ids in the local id file under
`assets`, keyed by the image's filename as the deck refers to it.

The map is keyed by filename and goes stale silently, so run `ops --summary` after any rename under the assets
folder. An image with no id becomes a placeholder rectangle; it is never guessed at.

## A note on dates

The tool list above was correct in September 2026. Connectors change. If the probe fails on a tool name that
looks like it was renamed rather than removed, check Canva's current documentation before editing a dialect
file, and update this page when you do.
