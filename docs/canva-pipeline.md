# The Canva pipeline

The repo is the source of truth. The deck named in `design-system/canva.config.json` is flattened into the shape
Canva can read, checked pixel for pixel against the real deck, measured into an element list, and turned into
`edit-design` operations for the Canva connector. A read-back step compares what Canva holds against the repo.

There is no cover page. NESA has no such concept, and the Canva document matches the deck's twelve pages exactly.

## The chain

```text
Folio Deck.dc.html + deck.css                    (source of truth)
        |  python scripts/canva.py build
        v
build/canva/canva-import-rev.html                (flattened, pixel-verified against the deck)
        |  python scripts/canva.py verify         proves it renders as the deck
        |  python scripts/canva.py extract
        v
build/canva/canva-layout.json                    (measured element list, 1123 x 1588 px per page)
        |  python scripts/canva.py ops --page NN ...
        v
edit-design operation arrays                     (pushed over the Canva connector)
        ^
        |  python scripts/canva.py check --dump read-design.json
        |  compares what Canva returned against canva-layout.json
```

`python scripts/canva.py all` runs build with verify, then extract, then an ops summary.

## What the flattener understands

Build re-implements the `deck.css` cascade in Python: selector matching, specificity, source order, the element's
own inline style, then `!important` last. Selectors may use descendant and child combinators (`a b`, `a > b`),
`:first-child`, `:last-child` and `::before` / `::after`. Sibling combinators (`+`, `~`) and other pseudo-classes
are not supported, and a stylesheet rule that uses one stops the build with an error rather than dropping the rule.
Anything the cascade gets subtly wrong shows up in verify as a pixel difference, which is why `all` runs verify
before anything is pushed. Verify's default tolerance is 0.35 per cent of a page's pixels (`--tolerance`), raised
per page by `known_residuals` in the config.

## Files

| File | Holds | Committed |
| --- | --- | --- |
| `design-system/canva.config.json` | Deck filename, page size, prop values, webfonts, ornament and placeholder colours, known residuals, output folder | Yes |
| `design-system/canva.local.json` | Design id, page id map, media-library asset id map for one Canva account | No. Template: `canva.local.example.json` |
| `build/canva/canva-import-rev.html` | The flattened deck, pages in reverse order (the shape Canva's importer reads) | No |
| `build/canva/canva-layout.json` | Per page: ordered shapes, images and texts with geometry and style | No |
| `build/canva/verify/` | Reference and export renders and diffs from the last verify | No |

Setup: `pip install -r requirements.txt`, and Chrome or Edge on `PATH` or named in `CHROME_PATH`.

## The push loop (per page, in a session with the Canva connector)

1. `read-design` with `open_transaction: true` gives a transaction id.
2. `python scripts/canva.py ops --page NN --phase elements --chunk-size 250 --chunk 1`. Paste the output into
   `edit-design` with `page_index` set to the folio page number. The first op carries the page's speaker notes.
3. The response echoes the page document. The text locator ids, in document order, are the `add_text` ops in
   order. Write them to a file, one per line.
4. `python scripts/canva.py ops --page NN --phase format --ids <file>`. Paste into `edit-design`. This applies
   sizes, weights, italics, colours, alignment and line heights, because `add_text` cannot carry styling.
5. Check the returned thumbnail against the repo page, then `finalize: commit`.

Without `canva.local.json` every op carries the literal `PAGE_ID` and every image is a placeholder rectangle.
That is enough to generate and inspect ops on a fresh clone.

## The read-back

Save the JSON that `read-design` returns and run:

```pwsh
python scripts/canva.py check --dump read-design.json
python scripts/canva.py check --dump read-design.json --page 03
python scripts/canva.py check --dump read-design.json --refresh-ids
```

Per page it reports text in the repo layout that Canva lacks, text Canva has that the repo does not (edited in
Canva, or left from an earlier push), and image asset ids the local map does not know. `--refresh-ids` writes the
design id and page ids from the dump into `canva.local.json`, which is how a fresh Canva design gets wired up once
its pages exist. Edits made in Canva are reported, not written back into the deck; the deck is edited by hand.

## What crosses and what does not

- Geometry, stacking order, colours, text content, sizes, weights, italics, alignment and the images all cross.
  The 60 degree masthead transition crosses as a mitred polygon shape.
- Font families do not cross. `format_text` has no family parameter, so text lands in Canva's default face at
  the correct size and weight. Apply Fraunces (display) and PT Serif (body) from the brand kit in Canva. The
  brand kit also wants the sixteen area hexes from the top of `deck.css`.
- Hatched fills on the pattern-piece plates flatten to their base tone.
- Images map by filename to asset ids in `canva.local.json`. Upload the assets in the Canva app first, then
  record the ids. Unmapped images push as placeholder rectangles that can be filled afterwards. The one exception
  is the house mark named under `ornament` in the config: unmapped, it pushes as two flat shapes (an oval beside a
  ringed disc) in the ornament colours, a stand-in for the drawn flower rather than a copy of it. Map
  `house-mark.svg` to an uploaded asset to get the real mark.
- `ops --summary` lists every image the deck uses that the local map does not cover. Run it after any rename under
  `design-system/assets/`, because the map is keyed by filename and goes stale silently.

## Other routes

- `python scripts/canva.py build --pdf` also writes `build/canva/canva-import-A3.pdf`, a true-size A3 PDF of
  the twelve pages (about 100 MB, since the plates are embedded at print resolution). Canva's own upload takes PDF
  but rebuilds it less editably. A fallback, not the pipeline.
- The flattened HTML doubles as the payload for the connector's `import-design-from-url`, which needs a public
  URL. Publish it somewhere only if that route is wanted.

The print proof does not come from Canva. It comes from `scripts/preview.ps1 -Item folio` and Ctrl+P at 100%,
the only route that holds true millimetres.
