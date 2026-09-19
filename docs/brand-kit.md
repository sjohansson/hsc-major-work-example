# Brand kit

The Rave'ns Ledger, Major Textiles Project folio, HSC Textiles and Design. This is the specification of record
for the folio's identity: names, colours, type and the masthead construction. The implementation is
`design-system/deck.css`, whose comments record the measurements behind each choice, and the swatch sheet is
`design-system/explorations/color-theme.html`. The reasons are in [design-rationale.md](design-rationale.md).

## Section names

Section names follow NESA's Major Textiles Project marking guidelines exactly (see
[nesa-folio-requirements.md](nesa-folio-requirements.md), Part A.1). Two rulings:

1. "Design Inspiration" is singular.
1. "Investigation, Experimentation and Evaluation" uses "and", never "&". The ampersand is reserved for period
   titles, which are the folio's own naming and not NESA-facing.

| Pages | NESA section (official) | Period title (masthead) | Area colourway |
| --- | --- | --- | --- |
| 1 to 2 | Design Inspiration | *The Sources, Gathered* | Slate |
| 3 to 5 | Visual Design Development | *The Designs, Weighed* | Bone |
| 6 to 8 | Manufacturing Specification | *The Making* | Ash |
| 9 to 12 | Investigation, Experimentation and Evaluation | *Trials & Proofs* | Wine |

The full official name is used verbatim in the dateline on all twelve pages. The section name a marker looks for
is never paraphrased, and never only in the footer.

## Colour

Four structural tokens: Ink `#1A1A1A`, Paper `#FEFBFC`, Cream `#F5EFE2` (the masthead band), and the two brand
colours sampled from the garment, which arrive as props: `slate` `#4A4E69` (the rule under the wordmark) and
`wine` `#8C3B4A` (the NESA-designated second colour for pattern modifications on page 7).

Each folio chapter (area) carries its own colourway of five tokens:

- field: pale panel fill; the masthead chapter-transition block
- border: full-strength token for rules, borders and accents; table header-row fills
- accent: deeper tone for fine detail; plate corner dots
- tint: near-white wash; table cell fills and large backgrounds
- emph: the accent taken down to text contrast; coloured type only

| Area | field | border | accent | tint | emph | emph on paper |
| --- | --- | --- | --- | --- | --- | --- |
| I Slate | `#C8C9D6` | `#7C7F9E` | `#6A6D86` | `#EFF0F3` | `#5A5C70` | 6.38 : 1 |
| II Bone | `#DAD2C7` | `#A6957A` | `#8D7F69` | `#F4F2EF` | `#766B59` | 5.08 : 1 |
| III Ash | `#C9D4DA` | `#7F98A8` | `#6D818E` | `#F0F3F5` | `#5C6C77` | 5.28 : 1 |
| IV Wine | `#D8C1C6` | `#A26B78` | `#8A5C67` | `#F4EDEF` | `#744F58` | 6.80 : 1 |

Field, accent and tint are derived from the border: field is the border mixed 42 per cent over white, tint 12 per
cent over white, accent the border mixed 82 per cent towards ink. `emph` is the accent mixed 80 per cent towards
ink, `color-mix(in srgb, <accent> 80%, #1A1A1A)`, written out as a literal so it survives without `color-mix()`
and so a marker's contrast check lands on a number in the file. If a border is re-sampled, re-derive all four and
re-measure `emph`; every value must stay above 4.5 : 1 on paper.

**Contrast rules.** Area tokens are fill-and-rule colours, never text colours. Text over a fill is always Ink,
and only ever over field or tint. Border may sit behind table header text. `emph` is the only token that may
colour type, and its one use is the last clause of the closing statement on page 12.

**Component mapping.** Per page, the area class recolours exactly these components and nothing else: the
masthead chapter-transition block (field), table header rows (border), table cells (tint), plate corner dots
(accent), and the section-title stub rules on pages 5 and 12 (border). Kept in brand colours, not area colours:
the slate rule under the wordmark, the house mark (ink only), and the wine that marks pattern modifications on
pages 6 to 8. Production drawings and pattern pieces stay pure ink linework.

## Type

Two families. Fraunces Black (opsz 9 to 144, weight 900) is the display face, used only in the wordmark, section
titles and the plate-number roundels. PT Serif is the text face for everything a marker reads. Body 12.5 pt at
1.3 leading; tables, captions, keys, drawing labels and the running foot 12 pt; the standfirst and closing
statement 16 pt at 1.4. The kit has no style below 12 pt. The swing tag reverse reproduced on page 7 is artwork
at 1 : 1 and is the only place smaller type appears.

## The house mark

One ornament for the whole set: a simplified nightshade flower between two bars, held in `design-system/assets/house-mark.svg`,
ink only. It appears in the running foot on all twelve pages, in the ornamented rule that closes the opening and
closing statements, on the binder spine and on the swing tag, and nowhere else. It is sized by its ink, not its
file: `--mark-h` is the height of the drawn band and the box is scaled to deliver it (see `.mark-band` in
`deck.css`).

## Masthead

The cream band carries the wordmark at 38 pt with the slate rule beneath, and ends after the wordmark in a 60
degree clipped edge. The area field block, fixed at 122 mm wide, begins on that same edge and carries the
right-aligned dateline in two registers: the official NESA section name in PT Serif bold caps, 12 pt, 0.11 em
letterspacing, over the period title in PT Serif italic, 12 pt. The block is top-aligned so the section name
starts at the same height on every page and a two-line name grows downward. Line breaks are authored, never
wrapped: only "Investigation, Experimentation / and Evaluation" breaks.

Slant geometry: horizontal run = band height / tan 60 degrees, about 0.577 times the band height, 15 mm at the
default 26 mm band. The slant is derived from the band height so the angle holds if the band is retuned within
22 to 28 mm.

**The area block width is constrained at both ends.** Measured on the A3 page at the specified sizes with the
previous twenty character wordmark:

- Upper bound: page minus cream padding-left minus wordmark width. At 38 pt the old wordmark measured 143.3 mm,
  giving 297.1 - 25 - 143.3 = 128.8 mm. Above this the wordmark is clipped by the 60 degree edge.
- Lower bound: widest dateline line plus the 60 degree edge at that line plus right padding, 87.2 + 12.4 + 15 =
  114.6 mm. Below this the longest section name collides with the slant.

122 mm sits inside that window. The Raven's Ledger is two characters shorter than the wordmark those figures
were measured with, so the upper bound has moved out, not in, and 122 mm still clears. Re-measure the wordmark
width in the preview before shipping any change to the wordmark, its size, the dateline wording, the 25 mm
binding margin, or the display face, and update the figures here and in `deck.css`.

**Implementation hazard.** The area block is positioned by `margin-left: calc(-1 * var(--m2-slant))`. CSS
`calc()` cannot add or subtract a unitless number from a length, so any custom property in that expression must
always carry a unit. A bare `0` invalidates the declaration, the negative margin is dropped, and the two 60 degree
edges spring apart by the full slant.

## Rules and plates

The double rule under the masthead is 0.53 mm over a 0.12 mm hairline, 0.9 mm apart, full width. 0.53 mm rather
than 0.4 mm because 0.4 mm is 1.51 px on a 1x screen and snapped to one row on half the pages, collapsing the
pair to a doubled hairline. Plates on pages 1 to 5 carry a 0.4 mm outer frame, a 0.12 mm inner frame 1.8 mm
inside it, and four 1.6 mm corner dots in the area accent. Drawings on pages 6 to 8 sit in a 0.3 mm single box
with no dots.

## Compliance guardrails

These override every aesthetic rule above.

- Nothing below 12 pt on a folio page.
- No student name anywhere. Student number only, in the running foot.
- Twelve A3 pages, one side, in NESA order, with the section page limits met.
- Production drawings and pattern pieces in ink line only, with the designated second colour for modifications.
- Every image numbered and cited; no copyrighted still reproduced without a licence.
