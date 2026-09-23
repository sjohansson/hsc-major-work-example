# The Canva connector, the dialects and the probe

## What Canva publishes

Canva's public MCP server is at `https://mcp.canva.com/mcp` and authenticates with OAuth. Its documented tools,
checked against Canva's developer documentation in September 2026, include:

| Tool | Does |
| --- | --- |
| `search-designs` | Find designs in the account |
| `get-design`, `get-design-pages`, `get-design-content` | Read a design's metadata, pages and content |
| `get-presenter-notes` | Read speaker notes |
| `get-design-thumbnail` | A rendered thumbnail |
| `import-design-from-url` | Create a design from a document at a public URL |
| `upload-asset-from-url`, `get-assets` | Put images in the media library and list them |
| `export-design` | Export to PDF and other formats |
| `start-editing-transaction`, `perform-editing-operations`, `commit-editing-transaction`, `cancel-editing-transaction` | The editing transaction |

Two things follow, and both shape this skill:

- **There is no public `read-design` or `edit-design`.** Those are the names an older connector used, and the
  names the default dialect here still asks for.
- **`perform-editing-operations` documents `replace_text` and `find_and_replace_text` only.** It changes text in
  a design that already exists. It does not create shapes, images or text boxes.

`start-editing-transaction` returns the design's `richtexts` and `fills`, each carrying an `element_id`. Canva's
documentation is explicit that those element ids are the source for editing operations, and that they do not
come from `get-design-content`.

## The two dialects

`ops` builds abstract operations; a file under `assets/dialects/` spells them for one connector.

**`claude-canva-connector`** is the vocabulary this pipeline has always emitted: `insert_shape`, `insert_fill`,
`add_text`, `format_text`, `replace_speaker_notes`, applied through `read-design` and `edit-design`. It is
marked `unverified`, because it is not in Canva's public documentation and nothing in this repository has ever
pushed with it. It is the default because it is the only dialect that can build a page from nothing.

**`canva-mcp-public`** is the documented server above. `capabilities.create_elements` is false, so asking it for
the elements phase exits 1 and names the route below instead of emitting a payload the connector would reject.

Adding a third is a JSON file, not a code change. `dialect.py` explains the file's shape at the top.

## The probe

```text
canva_sync.py probe --tools tools.json
canva_sync.py probe --tools - --dialect canva-mcp-public
```

List the connector's tools, save that JSON - the whole response, or a bare list of names, either is read - and
run the probe. It checks that every tool the dialect needs is present, ignoring case and the difference between
`-` and `_`, and, where the apply tool's input schema enumerates operation types, that every type the dialect
emits is among them. It prints its finding as JSON and exits 1 when they do not match.

A pass is not a guarantee. When the schema does not enumerate operation types the probe says so in its `reason`,
and the first page still has to be pushed and read back as `push-loop.md` describes.

If the tool list cannot be dumped at all, probe by hand: open a transaction, apply one shape operation to a
scratch page, read the page back, and cancel the transaction. If the shape is not there, the vocabulary is
wrong.

## The import-from-URL route

With the public connector, a design is not built operation by operation. It is imported:

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
