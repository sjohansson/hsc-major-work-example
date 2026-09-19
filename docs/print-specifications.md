# Print specifications

## Folio pages

- Sheet: A3, 297 x 420 mm, portrait, printed one side only.
- Format: PDF, CMYK, 300 dpi (test 600 dpi for the plates).
- No bleed and no printer margins. The page box is the sheet.
- Binding margin: 25 mm on the left, held by the masthead and the page grid.
- Type: nothing below 12 pt on a folio page (NESA rule). Body runs at 12.5 pt.
- Backgrounds and hairlines are the artwork. Print with background graphics on. The preview shell and the PDF
  route both set `print-color-adjust: exact`.
- Never print the folio from an A4 proof. At A4 the 12.5 pt body scales to about 8.8 pt and breaks the type rule
  on every page.

Print shop reference used for the A3 poster stock:
<https://www.officeworks.com.au/print-copy/p/premium-posters-pcppprpcp#jump-navigation--design-guidelines>

## Production items

| Item | Sheet | Trim | Notes |
| --- | --- | --- | --- |
| Binder spine insert | A2, 420 x 594 mm | 59 x 436 mm | The strip is longer than A3, so it prints on A2, two up with a spare. |
| Swing tag | A4 | 70 x 120 mm | Front and back on one sheet. Chamfered corner and punch hole are cut by hand. |
| Product labels | A4 x 3 | 58 x 39 mm | Mirrored for iron-on transfer paper. Unmirrored (`-NoMirror`) for printable fabric sheets. |
| Mount scaffold | A4 x 3 | 34.9 x 28.5 mm slots | Print at 100 % with margins set to none. Check the 100 mm calibration bar with a ruler before cutting. |

## Proofing

The print proof comes from `scripts/preview.ps1`, not from Canva. Open the built page, Ctrl+P, scale 100 %,
margins none, background graphics on. The `@page` rule in each preview names the sheet size so the browser does
not paginate against Letter or A4.
