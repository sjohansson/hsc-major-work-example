# Claude NESA grading review

<!-- cspell:words AEST Skia piqué Piqué -->

Marked by Claude (Claude Code, the `nesa-assessor` agent) on 23 September 2026, from the print of `main` at
`de58bf7`. This is one agent's scoring; other agents publish theirs in their own `nesa-grading-review-<agent>.md`
page. It is a reading of one export and goes stale when the folio changes. The dated working copy and every
measurement sit in `build/reviews/`, which is not committed.

The Raven's Ledger, HSC Textiles and Design Major Textiles Project, supporting documentation (the folio). This is a
self-assessment of the folio's 25 marks against the published NESA criteria. It is not a prediction of an HSC
result, and the textile item's 25 marks are not estimated.

Rules used: [docs/nesa-marking-facts.md](nesa-marking-facts.md) and
[docs/folio-marking-notes.md](folio-marking-notes.md), read in full before the PDF was opened. The facts
were checked against NESA's pages on 22 September 2026, one day before this run, so no source check was repeated.

## Result

| Section | Max | Mark | Range | Achievable |
| --- | --- | --- | --- | --- |
| Design Inspiration | 5 | 5 | 4 to 5 | 5 |
| Visual Design Development | 5 | 5 | 4 to 5 | 5 |
| Manufacturing Specification | 5 | 4 | 4 to 5 | 5 |
| Investigation, Experimentation and Evaluation | 10 | 9 | 9 to 10 | 10 |
| Total | 25 | 23 | | 25 |

Every section sits in its top range. Two marks are lost, and both are lost to evidence a marker can check, not to the
writing. The front and back flats (drawings 6.1 and 6.2) are true to their 1:10 scale everywhere except the skirt
hem, which is drawn at half its stated width. Three sample plates on pages 9 to 11 show something other than what
their methods made.

## 1. Artefact record and premise

### The file that was marked

| Field | Value |
| --- | --- |
| File | `build/print/folio.pdf` |
| Printed | 23 September 2026, 20:16:45 AEST (embedded creation date 2026-09-23 10:16:24 UTC) |
| Producer | HeadlessChrome 153, Skia/PDF m153, via `scripts/print_pdfs.py` |
| Size | 104,287,847 bytes |
| SHA-256 | `0ace9ca136dd2305079f23715b10737c49337c825ce6af9fd20edfd4747f172c` |
| Pages | 12, each 297.0 x 420.2 mm (A3 portrait) |
| Source state | `main` at `de58bf7`, after the last design-system commits (`b9c00af`, `8c48324`, `9902a00`) |

The four production items were read from the same print run and measured. They are not scored.

| Item | File | Bytes | SHA-256 | Pages |
| --- | --- | --- | --- | --- |
| Binder spine insert | `build/print/binder-spine.pdf` | 335,828 | `e48d185f0f5734c7f5cef3c01c82caa631fe52a86051051f667e3ccb6c6e2f9c` | 1, A2 |
| Swing tag | `build/print/swing-tag.pdf` | 138,291 | `b4d7b806fc090a0171295f46dda606231eeab0daf07c08f18d54a7c11b76331d` | 1, A4 |
| Product labels | `build/print/product-labels.pdf` | 177,027 | `baa85d887ee1a993082357d4009eb34d8ccbc19cb44740e88ec60de767db376e` | 4, A4 |
| Mount scaffold | `build/print/mount-scaffold.pdf` | 71,894 | `692204cbba26a8957eecac19dc365e548e0a86411716638206e98dd336840813` | 3, A4 |

### Why `build/print/` and not `output/`

The agent's default artefact is the PDF in `output/`. This run departs from that default on the owner's instruction,
and the departure is justified by the files themselves:

- `output/The Raven's Ledger - Folio deck, twelve pages, A3 297 x 420 mm.pdf` is **stale**. It is 104,295,558 bytes,
  SHA-256 `092107d2fd94e09f1378ae2f6d54a53b825ee89d9ff15b1d62427f545032adf3`, file date 22 September 2026 17:35
  AEST, embedded creation date 2026-09-22 07:34:39 UTC. It predates commit `b9c00af` (page 7 labels) and commit
  `8c48324` (standfirst reword).
- A text and pixel comparison confirms it. Against the marked file, the stale export has the old page 1 standfirst.
  Its image 1 caption calls a photographic plate "my study drawing". Page 2 credits image 8 to a museum record
  that the current folio does not claim. Page 7 has the old label layout with no symbol row. The page 9 plate
  caption "2.4 Piqué, wash 3" names a sample that does not exist. Page 11 lacks the pointer from Experiment 8 to
  plate 9.4. Marking it would have scored faults that the current source no longer has.
- `output/folio-codex-review-2026-09-23.pdf` appeared in `output/` during this run (untracked, embedded creation
  2026-09-23 11:16:12 UTC, SHA-256 `641c5d73ec644eeffe2e2679e85ca40410ea59f1b06cf9b925b10e8d48040a3d`). It belongs to
  another agent's run and was not marked.

Before this review is relied on, refresh `output/` from `build/print/folio.pdf`, or compare SHA-256 values, so that
the folder the agent treats as the current export matches what was marked.

Working tree note: the tree was clean when the run started. During the run, `docs/folio-marking-notes.md` gained an
uncommitted paragraph about where published reviews go, and `docs/nesa-grading-review-copilot.md` appeared. Neither
changes how a mark is placed, and neither was used here.

### Premise

The folio is marked as the finished submission of a fictional student, as a NESA marker holding the printed pages
would read it (notes, section 2). Every plate is generated and every number is invented. That provenance lives in the
repo, and no page mentions it. A generated or rendered plate is marked on what it shows and what its caption says,
never penalised for being digital. It is a finding only when it shows something other than what the method made, or
when its caption misrepresents it. The physical samples, the garment, the cover sheet, and the box are outside the PDF
and are recorded as not assessable. The target is 5, 5, 5, and 9 to 10.

### Previous reviews

No formal previous review exists in `build/reviews/`; the folder was empty before this run, so there is no status
table and finding numbers start at F1. Older working folders were glanced at for continuity only:
`build/nesa-review-2026-09-22/`, `build/folio-grading-review/`, `build/grading-review/`, and
`build/folio-revision-2026-09-22/`. They hold page renders, extracted text, and `audit.json` measurements, but no
review text or findings list, so nothing carries over.

## 2. Compliance audit

| Rule | Status | Evidence |
| --- | --- | --- |
| No student name anywhere; student number only | Pass | "Student No. 12345678" in every page footer and on all four items; no name found in any text layer |
| Font 12 pt or larger everywhere, including tables, captions, and drawing labels | Pass | Smallest span on every folio page is 12.0 pt; 0 spans under 12 pt across 1,471 spans. Drawing labels on pages 6 and 7 and the enlarged labels on page 7 are live text at 12 pt |
| Text clear, legible, and distinct from the background | Pass | Black text on off-white throughout; table heads are dark text on muted fills; callout numbers on the sketch plates sit in white circles with a black outline |
| A3 or A4 consistently, one side only | Pass | 12 pages, all 297.0 x 420.2 mm; one side is a print instruction (submission checks) |
| Section page limits met; NESA order kept; no cover page counted | Pass | Pages 1 to 2 Design Inspiration, 3 to 5 Visual Design Development, 6 to 8 Manufacturing Specification, 9 to 12 Investigation, Experimentation and Evaluation; 2, 3, 3, 4; no title or contents page |
| Every image numbered and referenced in the text | Pass | Images 1 to 8, sketches 1A to 3C, final design 4A to 4C, drawings 6.1 to 6.6, pattern pieces 1 to 15, swatches 8.1 to 8.5, and sample plates by ID are all numbered and cited |
| Nothing that must be unfolded or flipped; all mounts flat | Pass in the PDF | No fold-outs. Physical mounts are outside the PDF |
| Swatches about 5 x 5 cm, labelled | Pass | Swatches 8.1 to 8.5 measure 50.0 x 50.0 mm, each captioned with fibre and weight |
| Commercial patterns acknowledged on page 6 and on the cover sheet | Pass on page 6 | "Harrow and Vane 2140, view B, size 10 supplies the bodice and sleeve"; costed on page 8. Cover sheet not assessable |
| Packaging within the size rule; box untaped | Not assessable | Outside the PDF |
| Writing rules: no en or em dashes, straight quotes, banned words, Australian English | Pass | 0 en dashes, 0 em dashes, 0 curly quotes, 0 banned words, 0 US spellings in the extracted text of all 12 pages |
| Footer clearance | Pass, tight | Lowest body text 398.1 mm (pages 3 and 12); page 4 table border 400.0 mm; footer rule about 402.9 mm. Nothing overlaps |
| Costing total re-added | Pass | 16 lines sum to $229.15, as stated; every quantity times unit price is correct |

## 3. Section table

| Section | Max | Range | Dot point at issue | Mark | Achievable | What holds it back |
| --- | --- | --- | --- | --- | --- | --- |
| Design Inspiration (pages 1 to 2) | 5 | 4 to 5 | None | 5 | 5 | Nothing; one date nit (F10) |
| Visual Design Development (pages 3 to 5) | 5 | 4 to 5 | None | 5 | 5 | Nothing on the page; a premise risk on plates 4A to 4C (concerns) |
| Manufacturing Specification (pages 6 to 8) | 5 | 4 to 5 | "produces drawings that clearly reflect the textile item(s) and which are of professional standard" | 4 | 5 | F1: flats 6.1 and 6.2 draw the 240 cm hem at 60 mm, half its 1:10 width |
| Investigation, Experimentation and Evaluation (pages 9 to 12) | 10 | 9 to 10 | "Experiments with materials, equipment and manufacturing processes applicable to the item and modifies design and/or construction as a result of the experimentation" | 9 | 10 | F2 to F4: plates 2.2, 4.4, and 9.4 do not show what their methods made |
| Total | 25 | | | 23 | 25 | |

## 4. Pre-read measurements

Measured with PyMuPDF 1.28 before any prose was read. Numbers are in `build/reviews/2026-09-23/audit.json`; one PNG
(150 dpi) and one text file per page sit beside it, and every page image was opened.

| Check | Result |
| --- | --- |
| Page count and size | 12 pages, 297.0 x 420.2 mm each |
| Pages per section | 2, 3, 3, 4 against 2, 3, 3, 4 |
| Smallest text span | 12.0 pt on every page |
| Placed images | Page 1: four plates 56 x 84 mm. Page 2: four plates about 78 x 57 mm. Pages 3 to 5: sketches and final views 35 to 78 mm wide. Page 8: five swatches 50.0 x 50.0 mm. Pages 9 to 11: sample plates 40.5 x 24 mm (one 84 x 24 mm, one 40.5 x 32 mm) |
| Footer clearance | Lowest body text 379.9 to 398.1 mm; closest drawn edge 400.0 mm (page 4 table); footer rule about 402.9 mm |
| Costing | $229.15 re-added exactly |
| Dashes, quotes, banned words | None found |
| Text layer | Page 6 extracts "flat" and "finished" with ligature glyphs; invisible on paper, noted only |

Scale chips measured against their written dimensions:

| Drawing | Stated scale | Dimension checked | Expected on the page | Measured | Result |
| --- | --- | --- | --- | --- | --- |
| 6.1 Front | 1:10 | Shoulder to hem 112 cm | 112 mm | 112.1 mm | True |
| 6.1 Front | 1:10 | Shoulder width 36 cm | 36 mm | 36.1 mm | True |
| 6.1 Front | 1:10 | Half bust 44 cm | 44 mm | 44.1 mm | True |
| 6.1 Front | 1:10 | Half waist 34 cm | 34 mm | 34.1 mm | True |
| 6.1 Front | 1:10 | Half hip 48 cm | 48 mm | about 42 mm at hip level | Short |
| 6.1 Front | 1:10 | Half hem 120 cm (hem 240 cm) | 120 mm | 60.1 mm | **Half size** |
| 6.2 Back | 1:10 | Half hem 120 cm | 120 mm | 58.4 mm | **Half size** |
| 6.4 Overskirt | 1:20 | Half hem 132 cm (hem 264 cm) | 66 mm | 66.1 mm | True |
| 6.4 Overskirt | 1:20 | Waist to lower tier edge 68 cm | 34 mm | 34.5 mm | True |
| 6.3 Stand | 1:5 | Stand 38 cm; snaps 4, 14, 24, 34 cm | 76 mm; 8, 28, 48, 68 mm | 76 mm; 8.1, 28.1, 48.1, 68.2 mm | True |
| 6.3 Collar | 1:10 | Centre back depth 7 cm | 7 mm | 7.0 mm | True |
| 6.5 Band overlap | 1:5 | Overlap 15 cm x band 4 cm; snaps 5 and 10 cm | 30 x 8 mm; 10 and 20 mm | 30.1 x 8.0 mm; 10 and 20 mm | True |
| 6.6 Cuff section | 1:2 | Bead 4 mm | 2 mm | 2.0 mm | True |
| Page 7 skirt panel 11 | 1:15 | Hem 60 cm; depth 68 cm | 40 mm; 45.3 mm | 39.5 mm; 45.6 mm | True |
| Page 7 carrier 10 | 1:15 | Hem 66 cm | 44 mm | 44 mm | True |
| Page 7 cuff 6 | 1:15 | Cut 27 x 11 cm | 18 x 7.3 mm | 18 x 7.4 mm | True |
| Page 7 tulle layout | 1:50 | Roll 700 x 300 cm; tiers 342, 412, 512 cm | 140 x 60 mm; 68.4, 82.4, 102.4 mm | 140 x 60 mm; 68.5, 82.3, 102 mm | True |
| Page 7 satin layout | 1:50 | 300 cm x 75 cm folded | 60 x 15 mm | 60 x 15.3 mm | True |

Totals and ratios re-added:

- Tiers gather 2.5 to 1: 340 to 136, 410 to 164, and 510 to 204 cm. Experiment 5 tests the same ratio (100 cm to 40 cm).
- Carrier: four gores, 34 cm top and 66 cm hem, give 136 and 264 cm. Tier start lines at 14 and 34 cm fall on the
  flare at exactly 164 and 204 cm (136 + 128 x 14/64 and 136 + 128 x 34/64).
- Skirt: four panels at 17, 24, and 60 cm give waist 68, hip 96, and hem 240 cm, matching page 6.
- Band: 83 cm finished is 68 cm waist plus 15 cm overlap; 85 cm cut less two 1 cm turns gives 83 cm.
- Cuff: 22 cm closed plus 2 cm overlap is 24 cm flat; plus two 1.5 cm seams is 27 cm cut. Cuff depth 4 x 2 + 1.5 x 2
  is 11 cm cut.
- Sleeve: 54 cm plus the 4 cm cuff is 58 cm. Neck and stand are both 38 cm. The four collar snaps plus two overlap
  snaps equal the one pack of six on the costing.
- The lower tier ends at 34 + 34 = 68 cm below the waist, level with the 68 cm satin hem.

## 5. Investigation, Experimentation and Evaluation (pages 9 to 12), marked first

### Mark: 9 out of 10, range 9 to 10

The section meets every dot point of the top range in its words, its tables, and its cross-references. Nine
experiments cover three per area, each has a control and a quantified result, and each conclusion names the page
where its decision landed. Page 12 evaluates filament polyester, monofilament nylon, and staple cotton against a
stage costume's needs and names their limits. It sits at the bottom of the range, not the top, because of notes
section 4, step 3: the first dot point is met in words, but three plates beside the words show something other than
what the method made. Plates 2.2 show whole collars on a shirt and a bib, not 12 cm test sections. Plate 4.4 shows
tulle caught against satin in a tulle-to-tulle trial. Plate 9.4 shows the band split at centre back, where the band
is continuous and closes at the left side. These three faults sit under one dot point, so together they cost one
mark, not three.

### Dot point by dot point

| Top-range dot point (quoted) | Status | Evidence | Why |
| --- | --- | --- | --- |
| "Experiments with materials, equipment and manufacturing processes applicable to the item and modifies design and/or construction as a result of the experimentation" | Partly met | Materials: Experiments 1 to 3 (p. 9). Equipment: 4 to 6 (p. 10). Processes: 7 to 9 (p. 11). Each is on the item's own fabrics. Decisions land: Exp 1 to the 7 m tulle order (p. 8); Exp 2 to the collar label (p. 7); Exp 3 to the matte face (p. 6); Exp 4 to overskirt step 5 (p. 8); Exp 5 to the cord gathers (p. 8, overskirt step 4); Exp 6 to dress step 2 (p. 8); Exp 7 to the 25 mm braid hem (p. 6); Exp 8 to three hooks plus two snaps (6.5, p. 6); Exp 9 to the invisible zip (pattern modification table, p. 6). Three design changes on page 5 cite Experiments 8 and 9 | The experimenting and the modifying are thorough. Three plates do not show what their methods made (F2, F3, F4). The plate beats the caption, so a marker who looks closely doubts those three results |
| "provides thorough details of materials, equipment and manufacturing processes used and justifies their use on the basis of comprehensive investigations" | Met | Methods give sample sizes (100 x 16 cm strips; 20 x 20 cm squares; 40 cm seams), needle 70/10, 2.5 mm stitch, polyester thread, controls (1.1, 2.1, 3.1, 4.1, 5.1), and fixed conditions (lamp, exposure, detergent dose). Results are numbers: 4 cm and 9 cm stand-off; drift 11, 6, and 1 mm; intervals within 3 mm of 8 cm; 5 cm hem stand-off; changes of 52, 48, and 47 seconds. Prices were compared per metre ($4.50, $6.50, $9.80) | Nine controlled trials with measured outcomes are "comprehensive", and every conclusion stays inside its method: "does not establish all-night comfort", "establishes shape, not long-term durability", and "three runs do not establish service life" |
| "evaluates the properties and performance of the fabric, yarn and fibres used in relation to the end-purpose" | Met | Page 12 names fibre, yarn, and fabric for each component (polyester continuous-filament crepe satin; nylon monofilament net; cotton staple piqué). It ties each to a stage need (dark at 3 m and 10 m, movement, a separately washed white collar) and to its limit (heat sensitivity, snagging, creasing, warmth). The component table links fibre, observed performance, experiment, and care. It separates fibre from construction: "Fibre alone did not predict the result" | This is evaluation "in relation to the end-purpose", the phrase that separates 9 to 10 from 7 to 8. One claim outruns page 9: "The satin and crepe samples were both polyester". Experiment 3 never states the fibre of samples 3.1 to 3.4 (F7). It is a nit, not a fault that moves the mark |

### Marks fulfilled

- 9 marks. All three dot points of the top range are evidenced on the page, the cross-references hold (each "page
  N" and "Experiment N" was followed and says what the conclusion claims), and the evaluation is explicitly tied to
  the end-use.

### Marks missed

- 1 mark, under the first dot point. Plates 2.2 and 2.2 after wash 3 (p. 9) show whole pointed collars, the first on
  a black shirt with a button placket and the second on a flat bib. The method made "three 12 cm collar sections"
  photographed "on black satin under one warm lamp". The two plates also differ in carrier and weave scale, so they do
  not read as a before and after of one sample (F2).
- Plate 4.4 "Caught tulle" (p. 10) shows net caught against black satin. The method is "three 40 cm seams in the
  selected tulle", joining tulle to its tulle carrier (F3).
- Plate 9.4 "Selected" (p. 11) shows a vertical break through the band at centre back. The band is one 83 cm piece
  that closes with a 15 cm overlap at the left side (4B, p. 5; 6.5, p. 6). Experiment 8's note, "The closed band is
  photographed at 9.4", points at a view that shows neither the hooks, the snaps, nor the overlap (F4).

### Potential improvements

Described for the student to apply; nothing here is folio wording.

- Replace the two Experiment 2 plates with photographs of the actual 12 cm sections, before and after three washes,
  on the same black satin board under the same lamp. If only the piqué pair is shown, keep the caption saying so.
- Replace plate 4.4 with the tulle-to-tulle seam from the standard-foot trial, showing the caught area.
- Replace plate 9.4 with a view where the band is continuous over the zip. Add a plate of the left-side closure
  (three hooks and bars, two snaps on the 15 cm overlap), or point Experiment 8's note at a plate that shows it.
- Either record the fibre content of samples 3.1 to 3.4 in the Experiment 3 method or table, or narrow the page 12
  sentence to what page 9 shows.
- Show plate 1.2 side-on against the 1 cm grid, as plate 1.3 already is, so the 4 cm stand-off can be read from the
  plate the caption describes (F5).

## 6. Design Inspiration (pages 1 to 2)

### Mark: 5 out of 5, range 4 to 5

Both pages communicate clearly and meet all four dot points. Page 1 states the focus area (costume), explains why
costume shapes every decision, and justifies the one innovation that runs through the folio: a convertible
two-scene costume. The graded tiers, the long sleeve with a satin cuff, and the belt that becomes a carrying band are
each traced to a source image. Page 2 analyses the screen source, the 1964 series, three periods of black dress, and
two techniques, and says what each contributed and what was rejected. A collage of eight numbered, captioned plates
supports it, and the plates are honestly described as rendered or composite studies.

### Dot point by dot point

| Top-range dot point (quoted) | Status | Evidence | Why |
| --- | --- | --- | --- |
| "explains the relationship of the design inspiration to the nominated focus area" | Met | p. 1 "Relevance to the focus area": "The focus area of my Major Textiles Project is costume. Costume establishes a character before dialogue or action"; the stage reads at "performance distance under gym lighting" | Explains, not just names: the audience, the distance, the light, and why the item is not daywear |
| "justifies particular creative and/or innovative design ideas or techniques developed from the design inspiration" | Met | p. 1 "Creativity and innovation": overskirt on a hooked band plus snap-on collar gives two scenes from one garment, with the median 48 second change (Experiment 8). Tiers graded 18, 26, and 34 cm; cap sleeve to long sheer sleeve after image 2; buckle removed and belt becomes the carrying band | Each idea has a source and a reason, and the reason is tested later |
| "critically analyses and explains the relationship of the design inspiration to the historical/cultural or contemporary factors that have contributed to the design and manufacture of the item(s)" | Met | p. 2: the screen dress "was built for a camera at close range and for one scene"; the 1964 series' tonal range explains the colourless scheme; the 1905, 1926, and 1955 dresses each give one feature and the rest is rejected ("without a rigid period silhouette"); jet beading and horsehair braid set a surface and a manufacturing method (Experiment 7) | Critical rather than descriptive: it says what failed for a stage and what was kept, and links a period technique to a tested manufacturing choice |
| "supports written information through communication techniques such as collages of pictures, samples from various sources or graphical communication techniques, presented in a contemporary manner" | Met | Images 1 to 8, each numbered, captioned with a "Read for" line, and cited in the text; attribution note with The Met accession numbers and the screen reference, accessed 22 September 2026 | The collage carries the argument; each caption says what to look at |

### Marks fulfilled

- 5 marks. Every dot point is evidenced and nothing on the two pages contradicts another page.

### Marks missed

- None. One nit does not move the mark: image 2 is captioned "c. 1905" and the section head reads "1905 to 1955",
  while the cited record is "The Met, mourning dress, 1902-1904". The caption says the plate is a composite study, so
  this is honest, but a reader following the citation meets a different date (F10).

### Potential improvements

- Align the image 2 date with the cited record, or add to the note that the composite study is dated to the later
  period on purpose.
- Nothing else is needed for the mark. See the concerns section for the likeness risk on images 1, 6, and 7.

## 7. Visual Design Development (pages 3 to 5)

### Mark: 5 out of 5, range 4 to 5

The three pages develop one idea in order: a copy of the screen dress (Design One), a reaction against it (Design
Two), a synthesis (Design Three), and a final design that fixes the fault all three share. Each design has keyed
front and back sketches, a feature key classified A, F, or A + F, a modifications list that names what changed and
why, and a plus, minus, interesting table in elements and principles vocabulary. The final justification cites the
experiments that forced the last changes. This is critical analysis, not description.

### Dot point by dot point

| Top-range dot point (quoted) | Status | Evidence | Why |
| --- | --- | --- | --- |
| "includes appropriately labelled high quality sketches/drawings that clearly indicate the link between inspiration and design" | Met | Sketches 1A to 1C, 2A to 2C, 3A to 3C: front and back for each design, a detail view for each, rendered to suggest satin and tulle; numbered callouts match each key. Captions and modifications cite images 1, 2, 3, 4, and 7 | Labelled on the feature, front and back, fabric suggested; the link to inspiration is written beside each sketch |
| "explains the inspiration, development and evaluation of design ideas" | Met | Design One: "Drawn from image 1". Design Two: "takes the 1905 mourning source (image 2) whole". Design Three: "takes the mood of Design Two and the skirt of Design One". Final: six modifications, each with its reason | Each step names its source, what changed, and the evaluation that caused it |
| "critically analyses the functional and aesthetic aspects of the design, considering strengths and weaknesses, with reference to the elements and principles of design" | Met | PMI tables on pp. 3 to 5 use rhythm, contrast, emphasis, line, direction, unity, and proportion ("Four uneven tiers have no rhythm"; "The buckle is the one point of emphasis under hall light, and the wrong one"; "Three equal tiers repeat one interval; grading them would give the repeat a direction"). Functional minuses: a lapped zip ridge, a raw sleeve end stretching, heat, and snagging | Strengths and weaknesses of both kinds, in design vocabulary, with consequences |
| "provides evidence of creativity throughout concept development" | Met | The convertible overskirt and detachable collar come out of the Design Three observation "With the collar on it is her school dress from the waist up and her dance dress from the waist down" | The idea is shown being found, not asserted |
| "presents the development of ideas and concepts in a logical and sequential way" | Met | One, Two, Three, Final, each citing its parent; page 5 closes the loop to pages 6 and 9 to 11 | A marker can follow the sequence without turning back |

### Marks fulfilled

- 5 marks. All five dot points are met, and the page evidence is consistent with pages 1, 2, and 6.

### Marks missed

- None on the page. Plates 4A to 4C are photographs of a finished dress on a form rather than sketches. Their
  captions do not call them drawings, so under the premise this is not a fault, but see the concerns section.

### Potential improvements

- To secure the mark against a marker who expects the final design to be drawn, add front and back sketches of the
  final design in the same style as 3A and 3B, if space allows on page 5, and keep 4A to 4C as the evidence of the
  made garment.
- Check that the sleeve fullness in 4A to 4C matches the straight, tapered sleeve in 6.1 and pattern piece 5 (p. 7).
  The plates read fuller at the forearm than a 28 cm sleeve hem eased into a 24 cm cuff (F9).

## 8. Manufacturing Specification (pages 6 to 8)

### Mark: 4 out of 5, range 4 to 5

The section is detailed and almost entirely consistent. The description gives every finished measurement. The
pattern modification table gives each change with its reason. The cut schedule separates cut from finished sizes.
Pattern pieces are drawn at 1:15 with grain lines and notches, and the cutting layouts at 1:50 measure true. The
technical production plan has all five required elements, and the costing re-adds exactly. The three product labels
carry all five required fields. It sits at the bottom of the top range because one dot point is met in words but
not by the drawing beside it. Flats 6.1 and 6.2 carry a 1:10 chip and are true at the shoulder, bust, and waist,
but the skirt hem is drawn 60 mm wide. At the same half-girth convention the hem of 240 cm should be 120 mm, and the
overskirt in 6.4 is drawn exactly that way. A marker with a ruler finds the dress hem narrower than the overskirt hem
that page 6 says "clears" it, by a factor the numbers do not allow.

### Dot point by dot point

| Top-range dot point (quoted) | Status | Evidence | Why |
| --- | --- | --- | --- |
| "describes item(s) accurately and in detail" | Met | p. 6 Description: size 10; fabrics with swatch references 8.1 to 8.5; princess seams, faced round neck, four skirt panels, 40 cm invisible zip, neck hook, four collar snaps, cuff button on a 2 cm overlap, 4 mm jet beads, 25 mm braid in a 2 cm hem. Finished measures in cm. Pattern named and the drafted pieces listed | Every measure agrees with pages 5, 7, 8, and 12 and with the labels and tag |
| "produces drawings that clearly reflect the textile item(s) and which are of professional standard" | Partly met | 6.1 and 6.2 (front and back, 1:10, grain arrow, fully dimensioned); 6.3 to 6.6 details at 1:5, 1:10, 1:20, and 1:2; page 7 pattern pieces at 1:15 with grain, fold, notches, and original versus changed edges; cutting layouts at 1:50. All measured true except the 6.1 and 6.2 skirt: hem 60.1 and 58.4 mm against 120 mm, and hip about 42 mm against 48 mm | Professional standard means "in proportion and, where appropriate for the item, to scale". One ruler contradiction on the main flats is a fault, not a nit (F1). It is one fault, repeated front and back, so the section drops to the bottom of the range, not below it |
| "includes all the required details in the technical production plan" | Met | p. 8: swatches 8.1 to 8.5 at 50 x 50 mm; quantities (3 m satin, 7 m tulle, 0.5 m piqué); notions; itemised and total cost of $229.15; order of construction in three streams (dress 8 steps, overskirt 7, collar 5) citing experiments; timeline February to July | All five NESA elements present and internally consistent |
| "includes a product label that contains all the required aspects appropriate to the selected focus area" | Met | p. 7: three labels (dress, overskirt, collar), each with brand (The Raven's Ledger), size (size 10; waist 68 cm; neck 38 cm), fibre content, care symbols in the order wash, bleach, tumble dry, dry, iron plus a note, and "Made in Australia". Symbols agree with the page 12 care table: hand wash, no bleach, no tumble dry, dry flat in shade, cool iron (dress); iron crossed (overskirt); machine wash 30 gentle, line dry, warm iron (collar) | All five fields, per piece, at 12 pt, and consistent with the fibre evaluation (facts, section 8) |

### Production items against the folio

| Check | Folio | Item | Agrees |
| --- | --- | --- | --- |
| Brand | The Raven's Ledger (p. 7) | Labels, tag, spine: The Raven's Ledger | Yes |
| Size | Size 10; waist 68 cm; neck 38 cm (pp. 6, 7) | Labels sheet 1 and 3: the same; tag back: the same | Yes |
| Fibre | Polyester crepe satin, nylon tulle sleeves; nylon tulle on a polyester band; 100% cotton (p. 7); piqué (p. 8) | Labels: identical. Tag: identical, adds "piqué" | Yes |
| Care wording | p. 7 notes and p. 12 table | Labels: identical wording. Tag: "Dress and overskirt: hand wash cold separately, collar off. Do not bleach or wring. Dry flat in shade. Cool iron on the reverse of the satin only; never iron the tulle. Do not tumble dry. Collar: machine wash cold, gentle; line dry; warm iron." | Yes in words |
| Care symbols | p. 7: wash, bleach, tumble dry, dry flat in shade, iron | Labels: identical symbols and order. Tag: wash, bleach, tumble dry, **cool iron, dry flat without the shade mark** | **No** (F6) |
| Country | Made in Australia | Labels: Made in Australia. Tag: Made by hand in Australia | Yes |
| Label fields and size | "six lines at 55 mm wide" (p. 7) | Labels sheet 3: "Every label runs the same six lines"; ruled box measured 55.0 x 36.0 mm on a 71 x 48 mm patch | Yes |
| Label placement | Dress side seam, overskirt band, collar stand (p. 7) | Labels sheet 4: left side seam, inside the band at the left opening, inside the stand at centre back | Yes |
| 12 pt rule | Page 7 labels at 12.0 pt | Items are not folio pages: tag down to 6 pt, labels 6.5 pt, scaffold 9 pt, spine 10 pt | Not applicable to items; page 7 carries the enlargement |
| Closures | 3 hooks, 2 snaps, 15 cm overlap; four collar snaps (pp. 6, 8) | Tag: "3 hooks + 2 snaps", "four snaps" | Yes |
| Scaffold slots against captions | Plates and tables on pp. 9 to 11 | Scaffold: 1.1 to 1.3 plus **1.4 "Mid-weight at rest"**, which has no row, plate, or text in Experiment 1. 2.1 to 2.3 and "2.2 Pique, after wash 3" (folio: "Piqué"). 3.1 to 3.4, 4.1 to 4.4, and 5.1 to 5.4 match. 6.1S to 6.4T match "all eight conditions". 7.1T to 7.4S match "All eight outcomes". 8.1 to 8.5 and 9.1 to 9.4 match | One extra slot (F5); one missing accent (F12) |
| Scaffold scale | Offcuts 38 x 22 mm; bar 100 mm | Slots measured 37.8 x 21.7 mm; bar 100 mm in ten 10 mm bands | Yes |
| Tag and spine sizes | Not in the folio | Tag 69.9 x 119.7 mm (stated 70 x 120), punch 5.05 mm about 11 mm from the head; spine art box about 65 x 442 mm (stated) | Yes |

### Marks fulfilled

- 4 marks. Description, technical production plan, and product label are fully met, and every drawing except the two
  flats' skirt measures true.

### Marks missed

- 1 mark, to F1. The dress flats show a skirt that is not the one pages 6 and 7 specify: the hem is half width and the
  hip is short. Because 6.4 draws the overskirt hem at true width, the page itself exposes the difference.

### Potential improvements

- Redraw the skirt on 6.1 and 6.2 so that at 1:10 the half hip measures 48 mm and the half hem 120 mm. That is wider
  than the present 80 mm drawing box, so widen the box or reduce the flats to 1:15 or 1:20 and change the chip to
  match. Then re-measure every dimension written on the flats.
- Reorder the swing tag's symbol row to wash, bleach, tumble dry, dry, iron, and use the dry-flat-in-shade symbol that
  the labels use (F6). The tag is unscored, but facts section 8 asks that care agree everywhere.

## 9. Findings

Ordered by marks at stake. The source line is where a human applies the fix; nothing here is folio prose.

| ID | Priority | Page | Where on the page | Finding | Fix | Source |
| --- | --- | --- | --- | --- | --- | --- |
| F1 | P0 | 6 | Drawings 6.1 and 6.2, skirt | At the stated 1:10, the hem measures 60.1 mm (front) and 58.4 mm (back). Half of the 240 cm hem is 120 mm, and the same drawing is true to half-girth at the waist (34.1 mm), bust (44.1 mm), and shoulder (36.1 mm). Hip is about 42 mm against 48 mm. Drawing 6.4 draws the 264 cm overskirt hem at a true 66 mm, so the dress hem looks less than half the overskirt's, not 91 per cent of it. Costs 1 Manufacturing Specification mark | Redraw the skirt to the pattern (hip 48 mm, hem 120 mm at 1:10), or change the scale of both flats and their chips so the full hem fits; re-measure every written dimension | `design-system/assets/production-front.svg`, `design-system/assets/production-back.svg`; placed at `design-system/Folio Deck.dc.html` line 1051 |
| F2 | P0 | 9 | Experiment 2, plates "2.2 Piqué" and "2.2 Piqué, after wash 3" | Method: "three 12 cm collar sections ... photographed each on black satin". The plates show whole pointed collars, the first on a black shirt with a button placket and the second on a flat bib, with different weave scale. They do not show the sample the method made, or one sample before and after | Replace with photographs of the 12 cm sections on the satin board under the same lamp, before and after | `design-system/Folio Deck.dc.html` lines 1513 to 1516 (`assets/exp2-2.png`, `assets/exp2-4.png`); method at line 1486 |
| F3 | P0 | 10 | Experiment 4, plate "4.4 Caught tulle" | Aim and method join tulle tier to tulle carrier ("three 40 cm seams in the selected tulle"). The plate shows net caught against black satin | Replace with the standard-foot tulle-to-tulle seam at the caught point | `design-system/Folio Deck.dc.html` lines 1630 to 1631 (`assets/exp4-4.png`) |
| F4 | P1 | 11 | Plate 9.4 and the Experiment 8 note | Plate 9.4 shows a vertical break through the band at centre back. The band is one 83 cm piece that closes at the left side (4B, 6.5). Experiment 8's note, "The closed band is photographed at 9.4", points at a view with no hooks, snaps, or overlap. Grouped with F2 and F3 under one dot point: together they cost 1 Investigation mark | Replace 9.4 with the band continuous over the zip; add or point to a plate of the left-side overlap with its three hooks and two snaps | `design-system/Folio Deck.dc.html` line 1825 (note), lines 1861 to 1862 (`assets/exp9-4.png`) |
| F5 | P1 | 9 and scaffold | Experiment 1; scaffold sheet 1 | The scaffold has a slot "1.4 Mid-weight at rest" with no counterpart in the folio's Experiment 1 table, plates, or text. Plate 1.2 is front-on, so its 4 cm stand-off cannot be read from the grid the note describes, while plate 1.3 is side-on | Either add 1.4 (the side-on at-rest view) to the folio and use it as the 1.2 plate, or remove the scaffold slot | `design-system/Mount Scaffold A4.dc.html` line 49; `design-system/Folio Deck.dc.html` lines 1474 to 1478 |
| F6 | P1 | Swing tag (item) | Back face, care symbol row | The row runs wash, bleach, tumble dry, iron, dry, and the dry symbol is plain dry flat with no shade mark. The tag's own text, the three labels, and page 7 say "dry flat in shade" and use the order wash, bleach, tumble dry, dry, iron | Reorder the symbols and use the shade variant the labels use | `design-system/Swing Tag.dc.html` lines 100 to 111 |
| F7 | P2 | 12 | Second column, "Fibre alone did not predict the result" | "The satin and crepe samples were both polyester" is not stated anywhere in Experiment 3's method or table on page 9 | State the sample fibres on page 9, or limit the page 12 sentence to what page 9 records | `design-system/Folio Deck.dc.html` line 1907; Experiment 3 method at line 1525 |
| F8 | P2 | 9 to 11 | Area headers or result notes | The folio never says where the physical samples are. The scaffold is titled "sample display" and Experiment 6 says "I kept sample pieces", but no page tells the marker that the physical samples sit with the folio, by ID. The premise relies on "The folio and the mount scaffold say where the physical pieces sit" | Add one pointer on page 9 (or in each area header) naming the sample display and its numbering | `design-system/Folio Deck.dc.html` near line 1432 (page 9 header) |
| F9 | P2 | 5 | Plates 4A to 4C, sleeves | The plates show a sleeve fuller at the forearm, gathered into the cuff. Flat 6.1 and pattern piece 5 show a straight, tapered sleeve (-2 cm wide; 28 cm hem into a 24 cm cuff) | Check that the plates match the pattern, or record the ease in the description | `design-system/Folio Deck.dc.html` line 798 (4A caption) |
| F10 | P2 | 1 and 2 | Image 2 caption; page 2 section head and note | Image 2 is dated "c. 1905" and the head reads "1905 to 1955". The cited record is "The Met, mourning dress, 1902-1904" | Align the dates, or say the composite is dated to the later period on purpose | `design-system/Folio Deck.dc.html` line 69 |
| F11 | P3 | 3, 4, 5, 12 | Bottom of the PMI tables and the page 12 closing paragraph | Clearance to the footer rule is 2.9 to 4.8 mm. The page 4 table border sits at 400.0 mm, 0.1 mm past the 399.9 mm content box that `deck.css` records. Nothing overlaps in this print, but one added line would paint over the footer | Hold the pages at their present length; cut words before adding any | `design-system/deck.css` lines 196 and 455 to 462 |
| F12 | P3 | Items | Scaffold sheet 1; labels sheet 3 | The scaffold says "Pique" where the folio says "Piqué". Labels sheet 3 says "Both take it from the gownSize prop", which is a code term on a printed sheet | Match the folio spelling; replace the code term with plain words | `design-system/Mount Scaffold A4.dc.html` lines 58 and 64; `design-system/Product Labels.dc.html` line 635 |

## 10. Concerns

Risks a real marker, or a reader of this published review, might react to. None of them is scored above.

- **Every plate is generated, and most read as photographs.** Under the premise (notes, section 2) that is accepted,
  and it was held for the whole review. A real student's folio would carry their own photographs of their own
  samples. The notes record that a strict digital-only reading cost one Investigation mark in an earlier comparison.
  The same risk applies here: a marker who reads pages 9 to 11 as renders could withhold a mark for photographed
  samples, on top of F2 to F4.
- **Plates can carry details nobody checked.** F2, F3, F4, and F9 are all cases where a generated image shows
  something the method or pattern did not make. Rendered evidence needs the same scrutiny as a measured drawing.
  Captions are honest, so the fault is in what the plate shows, not in what the caption claims.
- **Likeness and copyright.** Images 1, 6, and 7 are "rendered screen studies" of a commercial screen property. Image
  6 shows a family group in the recognisable style of the 1964 cast. `AGENTS.md` bans photographs of real people
  and screen stills. These are neither, but a reader will not always know that, and a published review draws
  attention to them. This is not a marking deduction. It is a decision for the repo owner before publication.
- **The final design is shown as a made garment.** Plates 4A to 4C are photographs of a finished dress on a form, in
  Visual Design Development. A marker might read the final design as reverse-engineered from the item rather than
  designed. The sketches on pages 3 and 4 and the justification on page 5 answer that, so no mark was withheld.
- **The flats are the one measured drawing a marker checks first.** Shoulder to hem is the obvious ruler check, and
  it passes. F1 only shows when the hem width is measured. A marker who does not measure it would give 5. A marker
  who does, and reads 6.4 beside it, would not.
- **Small type on the physical items.** The swing tag goes down to 6 pt and the sewn labels to 6.5 pt. They are not
  folio pages, and page 7 reproduces the labels at 12 pt, so the folio passes. The 2025 marker feedback mentions
  "accurate care labels at the required text size", so a marker holding the garment might still comment.
- **The artefact is not the one the agent defaults to.** This review marks `build/print/folio.pdf`, and `output/`
  still holds a stale export. Until `output/` is refreshed, a rerun with no path will mark the stale file and report
  faults that are already fixed.
- **The run was not isolated.** Other agents wrote to `docs/` and `output/` while this review ran. Nothing they wrote
  was used, and the marked file's SHA-256 is recorded above.
- **This is a self-assessment.** It places evidence against descriptors. It does not know the state marking centre's
  standard for 2026, and it cannot see the physical submission.

## 11. Recommendations, in priority order

1. Fix F1: redraw or rescale the skirt on flats 6.1 and 6.2 so every written dimension measures true. This alone
   secures the fifth Manufacturing Specification mark.
2. Fix F2, F3, and F4: replace the three plates that do not show their method's sample, and give Experiment 8 a
   plate of the actual left-side closure. This secures the tenth Investigation mark.
3. Fix F5 and F8 together: reconcile the scaffold's 1.4 slot with the folio, and add one pointer telling the marker
   where the physical samples sit and how they are numbered.
4. Fix F6 so the tag's symbols agree with the labels and page 7, then reprint the tag.
5. Fix F7, F9, and F10 as insurance: each is a claim a careful marker could follow and find unsupported.
6. Fix F12 and leave F11 as a standing constraint: no page 3, 4, 5, or 12 edit may add a line.
7. Refresh `output/` from the print that was marked, and record the SHA-256 at the top of the next review.

## 12. Submission checks outside this PDF

Unscored. A marker would check these on the physical submission.

- The finished item matches the page 6 description exactly: size 10, finished measures, 40 cm invisible zip and
  neck hook, four collar snaps at 4, 14, 24, and 34 cm, three hooks and two snaps on a 15 cm overlap, 25 mm braid in a
  2 cm hem, tiers 18, 26, and 34 cm deep set at 0, 14, and 34 cm.
- The physical samples sit in the mount scaffold slots under the IDs the folio uses, flat and labelled: 1.1 to 1.3
  (resolve 1.4, F5), 2.1 to 2.3, 3.1 to 3.4, 4.1 to 4.4, 5.1 to 5.4, 6.1S to 6.4T, 7.1T to 7.4S, 8.1 to 8.5, and
  9.1 to 9.4. Full test pieces, the before and after records, and the final closure assembly are with the display, as
  the scaffold says.
- The Major Textiles Project Cover Sheet is at the front. It names the Harrow and Vane 2140 pattern and any outside
  help, and it acknowledges AI assistance the way NESA and the school require (facts, section 6).
- The sewn labels in the dress side seam, overskirt band, and collar stand, and the swing tag, agree with the final
  fibre content and care. Reprint the tag after F6.
- The folio is printed one-sided at 100 per cent on A3. Before binding, measure one drawing with a ruler: 6.1 should
  read 112 mm shoulder to hem, and after F1 the hem width too.
- The binder spine insert is trimmed to 59 x 436 mm, measured against the actual spine pocket first.
- The box is under 0.2 cubic metres with no side over 1.2 m, is not taped or wrapped, and holds nothing framed under
  glass or rigid plastic.
- Authenticity and certification are the student's and the school's, and are not part of this estimate.

## 13. What the folio evidences for the textile item (not estimated)

The item's 25 marks are never estimated. The folio makes these item criteria visible to a marker who was not in the
room:

- Appropriateness for the focus area and end use: pages 1, 2, and 5 argue a stage costume read at distance, with two
  scenes and a quick change timed at a median of 48 seconds.
- Creativity and innovation from the decision-making process: the convertible overskirt and detachable collar come
  out of the Design Three observation on page 4 and are tested in Experiment 8.
- Degree of difficulty: about 12.6 m of tulle tiers gathered 2.5 to 1 onto a flared four-gore carrier, an invisible
  zip, a detachable interfaced collar and stand on snaps, beaded interfaced cuffs, and a braid-supported hem.
- Management of the project to completion: the February to July timeline on page 8 and the final checks table on
  page 12.

## Working files

`build/reviews/2026-09-23/` holds `measure.py` and `crop.py` (the measurement scripts), `audit.json` (every
measurement quoted above), `page-01.png` to `page-12.png` and `page-01.txt` to `page-12.txt`, span dumps, renders and
text of the four items, zoom crops of the plates at issue, and renders of stale pages 1, 7, and 9 for the artefact
comparison.
