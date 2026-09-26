# Preview site

`scripts/preview.ps1` builds a static copy of the folio and the production items, opens it in a browser, and
rebuilds it every time a file under `design-system/` is saved. The open tab reloads itself. Change a stylesheet,
a page, or an image, and the result is on screen about a second later, at true millimetre size.

It needs PowerShell 7 (`pwsh`) and a browser. Chrome is tried first, then Edge, then whatever the system opens
`.html` files with.

## Running it

```pwsh
pwsh scripts/preview.ps1                     # everything, then watch
pwsh scripts/preview.ps1 -Item folio         # just the deck, then watch
pwsh scripts/preview.ps1 -Item tag, labels   # two items side by side
pwsh scripts/preview.ps1 -Item folio -NoWatch   # build and open once, then return to the prompt
pwsh scripts/preview.ps1 -NoOpen             # build once, no browser, no watching (for tools and CI)
```

Ctrl+C stops the watching. The pages stay in the output folder and still open, they just stop reloading.

`Get-Help .\scripts\preview.ps1 -Full` lists every parameter. The ones that change the artwork:

| Parameter | What it does |
| --- | --- |
| `-Item` | `folio`, `spine`, `tag`, `labels`, `mounts`, `meta`, or `all` (the default). Several at once are fine. |
| `-Guides` | Folio: the six-column grid and the margin box. Spine: the trim outline inside the bleed. |
| `-Bleed` | Folio: corner crop marks and the 3 mm bleed box. |
| `-DashedSlots` | Mount scaffold: dashed cut guides instead of the hairline. |
| `-Slate`, `-Wine` | The two garment colours, as hex. |
| `-StudentNo`, `-GownSize` | The values printed on the pages, tag, and labels. |
| `-SpineBandH` | Height of the spine's cream band in mm. |
| `-OutDir` | Where the pages go. Defaults to `folio-preview` in the system temp folder. |
| `-Browser` | Path to a browser, if the default is not the one you want. |

## Working on a design

1. Start the script with the item you are working on, and any overlays you want: for example
   `pwsh scripts/preview.ps1 -Item folio -Guides`.
2. Put the browser beside the editor.
3. Edit and save. The terminal prints the changed file and the rebuild, and the tab reloads at the same scroll
   position.
4. Zoom with Ctrl + scroll to check hairlines and small type. Ctrl+0 resets. A millimetre on screen is not a
   millimetre on paper, so judge size on a printed proof.

Everything under `design-system/` is watched: the `.dc.html` pages, `deck.css` and the item stylesheets, the
plates in `assets/`, and the design notes in `meta/`. A few things need a restart instead (Ctrl+C, then run the
script again):

- A different parameter, such as turning `-Guides` on or trying another `-Slate`. Parameters are fixed for the
  life of the run.
- An edit to `scripts/preview.ps1` itself.
- An item not named in `-Item`. The watch rebuilds only the items it started with. Run without `-Item` to
  rebuild everything on each save.

Two warnings in the terminal are worth reading:

- `unresolved tokens` means a page uses a `{{ name }}` the script has no value for. The token renders empty,
  the same as in the design host. Add the value to the item's `Vals` in the script, or fix the spelling.
- `skipped` means a source file or its `<section>` could not be found.

Each sheet is drawn in a box of its real size with `overflow: hidden`. Anything that runs past the page edge is
cut off in the preview. That is on purpose. It is the same page edge the printer will use.

## How it works

The `.dc.html` sources are design components. They need the design host's runtime (`deck-stage.js`,
`support.js`, and React) to render, so they only preview inside the VS Code design host. The script does the small
part of that job the artwork depends on, without the runtime:

1. It reads each source and takes out every `<section>`. One section is one page.
2. It replaces each `{{ token }}` with the value the component's `renderVals()` would give it: the colours, the
   student number, the gown size, and the overlay markup for `-Guides` and `-Bleed`.
3. It rewrites the relative `./assets/` paths so they point back into `design-system/`.
4. It wraps the pages in a plain HTML shell: a toolbar, a label above each sheet, and one box per sheet at the
   sheet's size in millimetres.
5. It writes one HTML file per item and an `index.html` that links them all.

The stylesheets are not copied. Each page links `deck.css` and its item stylesheet by `file://` path, straight
from `design-system/`, so the page always shows the current styles. The design notes page (`meta`) has no
tokens and is copied whole, with only its paths rewritten.

### How the reload works

The pages are local files opened as `file://` URLs. There is no web server to tell the browser about a change,
and a `file://` page cannot `fetch()` another local file. It can load a local script, though, so that is what
the reload uses:

- After each build, the script writes `live-reload.js` to the output folder. It holds one line, a stamp:
  the time of the build.
- Every 600 ms each open page loads that file again and reads the stamp.
- When the stamp changes, the page saves its scroll position and reloads.

A `FileSystemWatcher` on `design-system/` starts each rebuild. Editors often save a file in several writes, so
the script waits until nothing has changed for 300 ms, then re-runs itself with the same parameters. The output
folder is outside `design-system/`, so the rebuild's own writes do not start another one.

A build with `-NoOpen` leaves the reload out entirely. `scripts/print_pdfs.py` and the CI workflows build that
way, so their pages and PDFs carry no script and nothing waits for changes.

## What the preview does not show

The design host's prop panel, slide navigation, and speaker notes. Use the parameters in place of the props.
Everything that matters for print behaves as it does in the host: millimetre sizing, hairline weights, the
webfonts, zoom, and printing at 100 %.

## Print proof

Open a built page, press Ctrl+P, and set scale 100 %, margins none, background graphics on. Each page asks for
its own paper size, so the browser does not fit it to Letter or A4. The toolbar and the page labels are hidden
in print. See [print-specifications.md](print-specifications.md) for paper, printers, and the PDF route through
`scripts/print_pdfs.py`.
