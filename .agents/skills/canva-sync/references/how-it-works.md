# How the flattening works

Read this when a page comes out wrong, when a verify difference needs explaining, or before changing anything
under `scripts/canva_sync/`.

## The problem

A deck written properly is a stylesheet-backed document: classes, custom properties, `calc()`,
pseudo-elements, real `<table>` elements. Canva's HTML import reads none of that. It reads a flat tree of boxes
with literal inline styles, so everything the browser would resolve at render time has to be resolved first.

Doing that by hand is what goes wrong: the hand-written copy and the deck drift, and nobody notices until the
copy is a whole design revision behind. Making the export a build product means the two cannot drift. Running
`verify` before every push means a drift is a failed gate rather than a surprise in Canva.

## The stages

### build

1. Lifts each `<section>` out of the deck and substitutes the `{{ prop }}` values from the config.
2. Runs the stylesheet cascade in Python, so every element ends up with one literal `style` attribute and no
   class. The order is: selector matching, specificity, source order, the element's own inline style, then
   `!important` declarations last.
3. Reduces `calc()` and custom properties to literal lengths, inheriting variables down the tree.
4. Materialises `::before` and `::after` as real elements. A decorative one becomes a `div`; one carrying
   `content` text becomes a `span`, because a `div` inside a `<p>` closes the paragraph when the export is
   parsed back.
5. Rewrites the four constructs Canva cannot read (below).
6. Writes `canva-import-rev.html` with the pages in reverse order, which is the order Canva's importer reads.

The cascade understands descendant and child combinators (`a b`, `a > b`), compound selectors,
`:first-child`, `:last-child`, and `::before` / `::after`. Sibling combinators (`+`, `~`) and other
pseudo-classes are not supported: a rule that uses one stops the build with the offending selector named,
rather than being dropped silently. `doctor` reports the same thing before a build starts.

The cascade has no user-agent stylesheet. A browser's own defaults - `th` is bold, `p` has margins - are not
applied, so a deck that relies on them will flatten differently from how it renders. State them in the
stylesheet.

### verify

Renders every page twice in the same headless browser: once as the real deck against the real stylesheet, once
as the flattened export with no stylesheet at all, and diffs the two images pixel for pixel. This is the only
check that matters, because every mistake the flattening can make is silent: a selector that fails to match
drops a rule, a mis-reduced `calc()` moves a box by a millimetre, a table converted to a grid loses a hairline.

Pages are compared at 96 dpi, which puts an A3 sheet at 1123 x 1588 px and a hairline at about half a pixel.
A channel difference of 16/255 or less is not counted, because antialiasing along type edges is real and
unavoidable; what is being looked for is displaced or missing geometry. The default tolerance is 0.35 per cent
of a page's pixels, raised per page by `known_residuals`.

A `known_residuals` entry is a promise that the difference is understood. Write down why, in the repository's
own Canva document. Adding one to get a page through a gate is the failure mode this whole tool exists to
prevent.

### extract

Renders the flattened export and asks the browser where everything landed, in the Canva page's pixel
coordinate space. The result is an ordered element list per page: shapes with paths, images with asset names,
texts with geometry, size, weight, colour, alignment and line height.

### ops

Turns the element list into abstract operations, then spells them for one connector. See
`canva-connector.md`.

### check

The read direction. Takes the JSON a connector returns for the design and compares it with the element list:
text the repository has and Canva lacks, text Canva has and the repository lacks, and asset ids the local map
does not know. It reports; it never writes back into the deck.

`check` maps Canva pages to page labels by position. A page inserted by hand in Canva shifts every comparison
after it, and the report will look like wholesale disagreement. Check the page count first.

## The four rewrites

| Construct | Why | Becomes |
| --- | --- | --- |
| `clip-path` | Canva has no clipping | The mitred seam is painted as a border triangle: a zero-size box with a transparent left border and a coloured bottom border paints exactly the polygon the clip cut. Drawn as two boxes instead, the join leaves a sub-pixel seam. |
| `<table>` | Canva has no table | A CSS grid with measured column widths, explicit cell borders, and a background box per cell. |
| `column-count` | Canva has no multicol | The browser is asked where it broke the text, and each column becomes its own box. The block must carry `column-count` in its inline style, which is how the measure pass finds it. |
| `writing-mode: vertical-rl` | Canva has no vertical text | A horizontal box rotated 90 degrees, placed so the rotated ink lands exactly on the vertical box the browser measured. |

## What crosses into Canva and what does not

Crosses: geometry, stacking order, colours, text content, sizes, weights, italics, alignment, line heights, and
any image with a mapped asset id.

Does not cross:

- Font families. The format operation has no family parameter, so text lands in Canva's default face at the
  right size and weight. Apply the real faces from a Canva brand kit.
- Hatched or patterned fills, which flatten to the single tone in `pattern_fill`.
- Any image with no asset id, which becomes a placeholder rectangle in the `placeholder` colours.

## Still deck-shaped

The structural rewrites know which classes carry them through `rewrite_classes`, so another deck can name them
its way. The rewrites themselves are fixed: a clipped pair becomes border triangles, a vertical label becomes a
rotated box. A deck that makes its masthead some other way needs a new rewrite, not a new class name.
