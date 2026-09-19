# Production items

Four physical pieces sit beside the twelve folio pages. Each is a `.dc.html` design component in `design-system/`
with its own stylesheet, previewed and printed through `scripts/preview.ps1`. All four share the folio's
masthead, wordmark, house mark and area colours from `deck.css`, so the objects and the pages read as one piece
of work.

| Item | File | Sheet | Trim | Preview |
| --- | --- | --- | --- | --- |
| Binder spine insert | `Binder Spine Insert.dc.html` | A2, 420 x 594 mm, two copies | 59 x 436 mm | `-Item spine` |
| Swing tag | `Swing Tag.dc.html` | A4 | 70 x 120 mm, chamfered head, 5 mm punch | `-Item tag` |
| Product labels | `Product Labels.dc.html` | A4 x 3 | 58 x 39 mm, 55 x 36 mm ruled box | `-Item labels` |
| Mount scaffold | `Mount Scaffold A4.dc.html` | A4 x 3 | 34.9 x 28.5 mm slots | `-Item mounts` |

## Binder spine insert

The page masthead turned through 90 degrees: cream band, 38 pt wordmark, slate rule, and the 60 degree
transition into all four area fields in order, so the spine stands for the whole folio. The strip is 436 mm, 16 mm
longer than A3, which is why it prints on A2 with a spare. Measure the binder's spine pocket before printing.
Check that the cream band reads 44 mm on the proof. Trim from the foot end if the pocket is short; the wordmark
is set from the head.

## Swing tag

Two faces printed at true size, glued either side of a 1 to 1.5 mm board core, cut to the outline and punched for
a 7 mm black grosgrain ribbon. The front carries the wordmark, the house mark and the claim. The back is the
completion marker: the product specification, the five care symbols and the care sentence. The back repeats
page 7's product-label wording word for word. Change one, change all three.

## Product labels

Iron-on transfer labels for the dress and the collar, printed mirrored for light-fabric transfer paper (the
default) or unmirrored for printable fabric sheets (`-NoMirror`). Sheet 1 is the transfer sheet with crop marks,
sheet 2 the unmirrored reading proof at true size and 150 per cent, sheet 3 the production notes. Each transfer
goes on a 71 x 48 mm white polyester patch that is caught in the seam. The dress label sits in the left side seam
below the waist; the collar label sits inside the collar stand at centre back. The two care lines differ because
the fibres differ.

## Mount scaffold

The A4 cutting guide for the 36 experiment samples and 5 fabric swatches mounted on folio pages 8 to 11. The
slots are the same size as the slots on the A3 pages, on paper an A4 printer can take. Print at 100 per cent with
margins set to none and check the 100 mm calibration bar with a ruler before cutting any sample. Samples must sit
flat inside the sleeve thickness: 28 mm slot height, trimmed, nothing that has to be unfolded.

## Props shared with the deck

`slate`, `wine`, `gownSize` and `studentNo` are props on the deck and on each item that uses them. The preview
script passes one set of values to every document so the size on the labels, the size on the tag and the size on
page 7 cannot disagree.
