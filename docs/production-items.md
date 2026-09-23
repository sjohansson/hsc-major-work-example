# Production items

Four physical pieces sit beside the twelve folio pages. Each is a `.dc.html` design component in `design-system/`
with its own stylesheet, previewed and printed through `scripts/preview.ps1`. All four share the folio's
masthead, wordmark, house mark and area colours from `deck.css`, so the objects and the pages read as one piece
of work.

| Item | File | Sheet | Trim | Preview |
| --- | --- | --- | --- | --- |
| Binder spine insert | `Binder Spine Insert.dc.html` | A2, 420 x 594 mm, two copies | 59 x 436 mm | `-Item spine` |
| Swing tag | `Swing Tag.dc.html` | A4 | 70 x 120 mm, chamfered head, 5 mm punch | `-Item tag` |
| Product labels | `Product Labels.dc.html` | A4 x 4 | 71 x 48 mm patch, 55 x 36 mm ruled box | `-Item labels` |
| Mount scaffold | `Mount Scaffold A4.dc.html` | A4 x 3 | 38 x 22 mm reference-offcut slots | `-Item mounts` |

## Binder spine insert

The page masthead turned through 90 degrees: cream band, 38 pt wordmark, slate rule, and the 60 degree
transition into all four area fields in order, so the spine stands for the whole folio. The strip is 436 mm, 16 mm
longer than A3, which is why it prints on A2 with a spare. Measure the binder's spine pocket before printing.
Check that the cream band reads 44 mm on the proof. Trim from the foot end if the pocket is short; the wordmark
is set from the head.

## Swing tag

Two faces printed at true size, glued either side of a 1 to 1.5 mm board core, cut to the outline and punched for
a 7 mm black grosgrain ribbon. The front carries the wordmark, the house mark and the claim. The back is the
completion marker: the product specification, the five care symbols and the care sentence. The sewn labels carry
the same five symbols; change a symbol on one and change it on the other.

## Product labels

Sewn labels for the dress, the overskirt and the collar. All three share one layout: wordmark, piece and size,
fibre content, the five care symbols in the order wash, bleach, tumble dry, natural dry, iron, a one-line care
note for what a symbol cannot say, and the country of origin. Each cell on the print sheets is the finished
71 x 48 mm patch with the 55 x 36 mm ruled box set 10 mm from the left edge and 6 mm from the others; the
allowance is blank. The artwork reaches the fabric one of two ways, so the run is printed twice: sheet 1 as it
reads, for a printable fabric sheet or a label printer, and sheet 2 mirrored, for iron-on transfer paper, which
prints face down. Each sheet's banner states its orientation. Sheet 3 is the unmirrored reading proof at true size
and 150 per cent, sheet 4 the production notes for both. The dress label sits in the left side seam below
the waist, the overskirt label inside the band at the left opening, and the collar label inside the collar stand at
centre back. The three care rows differ because the fibres differ. Page 7 shows the same three labels enlarged for
reading: the same six registers, the same symbols and the same words, at 12 pt with 6.5 mm symbols. Change a word
on one and change it on the other. Dress size is 10, overskirt waist is 68 cm, and collar neck is 38 cm.

## Mount scaffold

Three A4 guides provide 45 reference-offcut slots for the sample display. The slots are 38 x 22 mm and are
independent of the selected images on folio pages 9 to 11. IDs include every marking/material condition,
every edge/hem finish, and the final hook-plus-snap assembly. Full test pieces and before/after records remain
with the display. Print at 100 per cent with margins set to none and check the 100 mm calibration bar before
cutting. The five 50 x 50 mm material swatches remain on folio page 8.

## Props shared with the deck

`slate`, `wine`, `gownSize` and `studentNo` are props on the deck and on each item that uses them. The preview
script passes one set of values to every document so the size on the labels, the size on the tag and the size on
page 7 cannot disagree.
