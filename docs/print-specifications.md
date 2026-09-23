# Print specifications

## Folio pages

- Sheet: A3, 297 x 420 mm, portrait, printed one side only.
- Format: PDF with vector type and drawings; raster plates at 300 dpi. The browser export is RGB.
  If the print shop needs CMYK, convert with its supplied press profile after approving the RGB proof.
- No bleed and no printer margins. The page box is the sheet.
- Binding margin: 25 mm on the left, held by the masthead and the page grid.
- Type: nothing below 12 pt on a folio page (NESA rule). Body runs at 12.5 pt.
- Backgrounds and hairlines are the artwork. Print with background graphics on. The preview shell and the PDF
  route both set `print-color-adjust: exact`.
- Never print the folio from an A4 proof. At A4 the 12.5 pt body scales to about 8.8 pt and breaks the type rule
  on every page.

### Printing the folio

Any printer that takes A3 will do: a school colour laser, a home A3 inkjet, or a print and copy shop.

- Paper: a heavy matte or satin stock, around 150 to 200 gsm, holds the solid fills without curling and stands
  up to handling in a binder. Plain 80 gsm copy paper shows through and cockles under heavy ink.
- Send the PDF, not the HTML, and ask for actual size. "Fit to page" or "shrink to fit" scales every page and
  breaks the type rule.
- Print one page first. Check a known measurement with a ruler, and check the colour fills and the hairlines,
  before printing all twelve.
- Expect colour to shift a little between printers, and between screen and paper. Judge the colour on the
  printed proof, not on the screen.
- Laser toner sits on the surface and can crack on a fold, so keep the pages flat. Inkjet needs a few minutes
  to dry before the pages are stacked.

## Production items

| Item | Sheet | Trim | Notes |
| --- | --- | --- | --- |
| Binder spine insert | A2, 420 x 594 mm | 59 x 436 mm | The strip is longer than A3, so it prints on A2, two up with a spare. |
| Swing tag | A4 | 70 x 120 mm | Front and back on one sheet. Chamfered corner and punch hole are cut by hand. |
| Product labels | A4 x 4 | 71 x 48 mm patch | Each cell is the finished patch with the 55 x 36 mm ruled box inset. Sheet 1 as it reads, for printable fabric sheets and a label printer. Sheet 2 mirrored, for iron-on transfer paper. Sheets 3 and 4 are the reading proof and the notes, plain paper only. |
| Mount scaffold | A4 x 3 | 38 x 22 mm reference-offcut slots | Print at 100 % with margins set to none. Check the 100 mm calibration bar with a ruler before cutting. |

## Proofing

The print proof comes from `scripts/preview.ps1`, not from Canva. Open the built page, Ctrl+P, scale 100 %,
margins none, background graphics on. The `@page` rule in each preview names the sheet size so the browser does
not paginate against Letter or A4.

`python scripts/print_pdfs.py` makes the same print without the dialog. It builds the previews, prints each one
with headless Chrome to `build/print/`, and fails if a PDF has a different page count from its preview or a page
more than 1 mm off the sheet size. The `Print` workflow (`.github/workflows/print.yml`) runs it on every push to
`main` that touches the design system and keeps the PDFs as a run artifact. The folio PDF is about 100 MB,
because the plates are embedded at full resolution.
