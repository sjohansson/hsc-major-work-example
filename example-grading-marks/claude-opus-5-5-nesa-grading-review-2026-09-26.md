# NESA grading review, 26 September 2026

<!-- cspell:words AEST Skia piqué Piqué -->

The Raven's Ledger, HSC Textiles and Design Major Textiles Project, supporting documentation (the folio). This is a
self-assessment of the folio's 25 marks against the published NESA criteria. It is not a prediction of an HSC
result, and the textile item's 25 marks are not estimated.

Rules used: `docs/nesa-marking-facts.md` and `docs/folio-marking-notes.md`, read in full before the PDF was opened.
The facts were checked against NESA's pages on 22 September 2026, four days before this run, so no source check was
repeated.

## Result

| Section | Max | Mark | Range | Achievable |
| --- | --- | --- | --- | --- |
| Design Inspiration | 5 | 5 | 4 to 5 | 5 |
| Visual Design Development | 5 | 5 | 4 to 5 | 5 |
| Manufacturing Specification | 5 | 4 | 4 to 5 | 5 |
| Investigation, Experimentation and Evaluation | 10 | 9 | 9 to 10 | 10 |
| Total | 25 | 23 | | 25 |

Every section sits in its top range. Two marks are lost, both to evidence a marker can check: the dress flats 6.1 and
6.2 draw the skirt hem at half its stated 1:10 width, and three sample plates on pages 9 to 11 show something other
than what their methods made.

## 1. Artefact record and premise

| Field | Value |
| --- | --- |
| File | `output/1-the-ravens-ledger-folio.pdf` |
| Export date | 24 September 2026, 15:12 AEST (embedded creation date 2026-09-24 05:12:19 UTC); committed in `50ae9b2` |
| Producer | Chrome 154, Skia/PDF m154 |
| Size | 104,287,839 bytes |
| SHA-256 | `05b68f950a1ac465ccfc90650e199086b9e32c3d565dd74919470327fb03113b` |
| Pages | 12, each 297.0 x 420.2 mm (A3 portrait) |

Comparison with the previous marked file (`build/print/folio.pdf`, 23 September 2026, SHA-256 `0ace9ca1...f172c`):
the extracted text of all 12 pages is identical, and the 150 dpi renders match on every sampled pixel. The source
`design-system/Folio Deck.dc.html` has no commit since `de58bf7`. The two files differ only in print metadata. Every
page was still re-rendered, opened, and read for this review, and the key measurements were repeated.

Premise (notes, section 2): the folio is marked as the finished submission of a fictional student, as a NESA marker
holding the printed pages would read it. Every plate is generated and every number invented; that provenance lives in
the repo and no page mentions it. A generated plate is marked on what it shows and what its caption says, never for
being digital, and is a finding only when it shows something other than what the method made. The physical samples,
the garment, the cover sheet, and the box are outside the PDF and are not assessable. The target is 5, 5, 5, and 9 to
10.

Output location: on the requester's instruction this review is written to `marks/`, not `build/reviews/`. The
measurements are in `marks/2026-09-26/`: `audit.json` (page sizes, span sizes, placed images, dash and quote counts,
footer clearance, costing, page 6 scale checks), `scale-p06.json`, and `measure.py`. The page renders and span dumps
stayed out of the repository. `marks/` is not ignored by git, unlike `build/`.

## 2. Compliance audit

| Rule | Status | Evidence |
| --- | --- | --- |
| No student name anywhere; student number only | Pass | "Student No. 12345678" in every footer; no name in any text layer |
| Font 12 pt or larger everywhere, including tables, captions, and drawing labels | Pass | 1,471 text spans; smallest 12.0 pt on every page; 0 under 12 pt. Drawing labels on pages 6 and 7 are live text |
| Text clear, legible, and distinct from the background | Pass | Dark text on off-white; table heads dark on muted fills |
| A3 or A4 consistently, one side only | Pass | 12 pages, all 297.0 x 420.2 mm; one-sided printing is a submission check |
| Section page limits met; NESA order kept; no cover page counted | Pass | Pages 1 to 2, 3 to 5, 6 to 8, 9 to 12: 2, 3, 3, 4; no title or contents page |
| Every image numbered and referenced in the text | Pass | Images 1 to 8, sketches 1A to 3C, final design 4A to 4C, drawings 6.1 to 6.6, pieces 1 to 15, swatches 8.1 to 8.5, sample plates by ID |
| Nothing that must be unfolded or flipped; all mounts flat | Pass in the PDF | No fold-outs; physical mounts outside the PDF |
| Swatches about 5 x 5 cm, labelled | Pass | Swatches 8.1 to 8.5 placed at 50.0 x 50.0 mm, each captioned with fibre |
| Commercial patterns acknowledged on page 6 and on the cover sheet | Pass on page 6 | "Harrow and Vane 2140, view B, size 10 supplies the bodice and sleeve"; costed on page 8. Cover sheet not assessable |
| Packaging within the size rule; box untaped | Not assessable | Outside the PDF |
| Writing rules: dashes, quotes, banned words | Pass | 0 en dashes, 0 em dashes, 0 curly quotes, 0 banned words in all 12 pages |
| Footer clearance | Pass, tight | Lowest body text 398.1 mm (pages 3 and 12); footer rule about 402.5 mm |
| Costing total re-added | Pass | 16 lines sum to $229.15 as stated; every quantity times unit price correct |

## 3. Section table

| Section | Max | Range | Dot point at issue | Mark | Achievable | What holds it back |
| --- | --- | --- | --- | --- | --- | --- |
| Design Inspiration (pages 1 to 2) | 5 | 4 to 5 | None | 5 | 5 | Nothing; one date nit (F10) |
| Visual Design Development (pages 3 to 5) | 5 | 4 to 5 | None | 5 | 5 | Nothing on the page; sleeve fullness nit (F9) |
| Manufacturing Specification (pages 6 to 8) | 5 | 4 to 5 | "produces drawings that clearly reflect the textile item(s) and which are of professional standard" | 4 | 5 | F1: 6.1 and 6.2 draw the 240 cm hem at 60 mm, half its 1:10 width |
| Investigation, Experimentation and Evaluation (pages 9 to 12) | 10 | 9 to 10 | "Experiments with materials, equipment and manufacturing processes applicable to the item and modifies design and/or construction as a result of the experimentation" | 9 | 10 | F2 to F4: plates 2.2, 4.4, and 9.4 do not show what their methods made |
| Total | 25 | | | 23 | 25 | |

## 4. Pre-read measurements

Measured with PyMuPDF 1.28 before any prose was read; every page rendered at 150 dpi and opened.

| Check | Result |
| --- | --- |
| Page count and size | 12 pages, 297.0 x 420.2 mm |
| Pages per section | 2, 3, 3, 4 against 2, 3, 3, 4 |
| Smallest text span | 12.0 pt on every page |
| Placed images | p. 1 four plates 56 x 84 mm; p. 2 four plates about 78 x 57 mm; p. 3 sketches 35 x 62 mm; pp. 4 and 5 plates 78 x 111 and 73 x 105 mm; p. 8 five swatches 50.0 x 50.0 mm; pp. 9 to 11 sample plates 40.5 x 24 mm (one 84 x 24, one 40.5 x 32) |
| Costing | $229.15 re-added exactly |
| Dashes, quotes, banned words | None |

Scale checks on page 6, from the vector paths:

| Drawing | Stated scale | Dimension | Expected | Measured | Result |
| --- | --- | --- | --- | --- | --- |
| 6.1 Front | 1:10 | Shoulder to hem 112 cm | 112 mm | 112.1 mm (outline and bracket) | True |
| 6.1 Front | 1:10 | Front hem, half of 240 cm | 120 mm | 60.1 mm | **Half size** |
| 6.2 Back | 1:10 | Shoulder to hem 112 cm | 112 mm | 112.1 mm | True |
| 6.2 Back | 1:10 | Back hem, half of 240 cm | 120 mm | about 60 mm (hem line plus the dimension ticks read 66.9 mm) | **Half size** |
| 6.4 Overskirt | 1:20 | Front hem, half of 264 cm | 66 mm | about 66 mm (69.2 mm including stroke ends) | True |
| 6.4 Overskirt | 1:20 | Waist to lower tier edge 68 cm | 34 mm | 34.4 mm | True |

Totals and ratios re-added: tiers 340, 410, and 510 cm to 136, 164, and 204 cm are 2.5 to 1; four gores at 34 and
66 cm give 136 and 264 cm; four skirt panels at 17, 24, and 60 cm give waist 68, hip 96, and hem 240 cm; band 83 cm
is 68 cm waist plus 15 cm overlap; cuff 22 cm closed plus 2 cm overlap is 24 cm flat, plus two 1.5 cm seams is 27 cm
cut; sleeve 54 cm plus 4 cm cuff is 58 cm.

## 5. Investigation, Experimentation and Evaluation (pages 9 to 12), marked first

### Mark: 9 out of 10, range 9 to 10

Nine experiments, three per area, each with a control, a quantified result, and a conclusion that names the page
where its decision landed. Page 12 evaluates filament polyester, monofilament nylon, and staple cotton against the
stage end-use and names their limits. The section sits at the bottom of the range under notes section 4, step 3:
the first dot point is met in words, but three plates beside the words show something other than what the method
made. The three sit under one dot point, so they cost one mark, not three.

Reading used: notes section 4 says three independent contradictions under one dot point make it "elementary
standard" and trigger the combination rule. That sentence is written for ruler and calculator faults. F2 to F4 are
plate-against-method faults: they weaken confidence in three results but do not remove the experimenting or the
modifying, which every conclusion evidences. The dot point is therefore read as met at the bottom of the top range,
not as met only at 7 to 8. A stricter marker who applied the combination rule would give 8.

| Top-range dot point (quoted) | Status | Evidence | Why |
| --- | --- | --- | --- |
| "Experiments with materials, equipment and manufacturing processes applicable to the item and modifies design and/or construction as a result of the experimentation" | Partly met | Materials 1 to 3 (p. 9), equipment 4 to 6 (p. 10), processes 7 to 9 (p. 11), all on the item's own fabrics. Decisions land: Exp 1 to the 7 m tulle order (p. 8); Exp 2 to the collar label (p. 7); Exp 3 to the matte face (p. 6); Exp 4 to overskirt step 5 (p. 8); Exp 5 to the cord gathers; Exp 6 to dress step 2; Exp 7 to the braid hem (p. 6); Exp 8 to three hooks plus two snaps (6.5); Exp 9 to the invisible zip (p. 6) | Thorough, but plates 2.2, 4.4, and 9.4 contradict their methods (F2 to F4). The plate beats the caption |
| "provides thorough details of materials, equipment and manufacturing processes used and justifies their use on the basis of comprehensive investigations" | Met | Sample sizes, needle 70/10, 2.5 mm stitch, controls 1.1, 2.1, 3.1, 4.1, 5.1, fixed light and exposure; numeric results (4 and 9 cm stand-off; drift 11, 6, 1 mm; intervals within 3 mm; changes 52, 48, 47 s); prices per metre | Conclusions stay inside their methods: "does not establish all-night comfort", "establishes shape, not long-term durability", "three runs do not establish service life" |
| "evaluates the properties and performance of the fabric, yarn and fibres used in relation to the end-purpose" | Met | p. 12 names fibre, yarn, and fabric per component, ties each to a stage need and a limit, and tabulates fibre, observed performance, experiment, and care | Evaluation is "in relation to the end-purpose". One sentence outruns page 9 (F7), a nit |

Marks missed: 1, under the first dot point.

- Plates "2.2 Piqué" and "2.2 Piqué, after wash 3" (p. 9, right column) show whole pointed collars, the first on a
  black shirt with a button placket, the second on a bib. The method made "three 12 cm collar sections" photographed
  "on black satin under one warm lamp" (F2).
- Plate "4.4 Caught tulle" (p. 10, right column) shows net caught against black satin. The method is "three 40 cm
  seams in the selected tulle", tulle to tulle (F3).
- Plate "9.4 Selected" (p. 11, right column) shows a vertical break through the band at centre back. The band is one
  83 cm piece that closes at the left side (4B, p. 5; 6.5, p. 6), and Experiment 8's note "The closed band is
  photographed at 9.4" points at a view with no hooks, snaps, or overlap (F4).

What would lift it to 10: plates that show the 12 cm sections before and after washing on the satin board, the
tulle-to-tulle seam at the caught point, and the band continuous over the zip with a view of the left-side closure.

## 6. Design Inspiration (pages 1 to 2)

### Mark: 5 out of 5, range 4 to 5

| Top-range dot point (quoted) | Status | Evidence |
| --- | --- | --- |
| "explains the relationship of the design inspiration to the nominated focus area" | Met | p. 1 "Relevance to the focus area": costume, a stage read "at performance distance under gym lighting", not daywear |
| "justifies particular creative and/or innovative design ideas or techniques developed from the design inspiration" | Met | p. 1 "Creativity and innovation": convertible overskirt and snap-on collar, tested at a median 48 s (Experiment 8); graded tiers 18, 26, 34 cm; long sheer sleeve; belt becomes the band |
| "critically analyses and explains the relationship of the design inspiration to the historical/cultural or contemporary factors that have contributed to the design and manufacture of the item(s)" | Met | p. 2: what the screen dress did for a camera and failed for a stage; the 1964 tonal range; what each of the 1905, 1926, and 1955 studies gives and what is rejected; jet beading and horsehair braid linked to Experiment 7 |
| "supports written information through communication techniques such as collages of pictures, samples from various sources or graphical communication techniques, presented in a contemporary manner" | Met | Images 1 to 8, numbered, each with a "Read for" caption, cited in the text; sources note with accession numbers |

One nit does not move the mark: image 2 is dated "c. 1905" while the cited record is "1902-1904" (F10).

## 7. Visual Design Development (pages 3 to 5)

### Mark: 5 out of 5, range 4 to 5

| Top-range dot point (quoted) | Status | Evidence |
| --- | --- | --- |
| "includes appropriately labelled high quality sketches/drawings that clearly indicate the link between inspiration and design" | Met | Sketches 1A to 3C: front, back, and detail, numbered callouts matching each key, fabric suggested; sources cited per design |
| "explains the inspiration, development and evaluation of design ideas" | Met | Design One from image 1; Two from image 2; Three combines them; the final lists six modifications, each with a reason |
| "critically analyses the functional and aesthetic aspects of the design, considering strengths and weaknesses, with reference to the elements and principles of design" | Met | PMI tables in rhythm, emphasis, contrast, line, direction, unity; functional minuses (zip ridge, raw sleeve end, heat, snagging); A, F, and A + F keys |
| "provides evidence of creativity throughout concept development" | Met | The convertible idea is found in the Design Three "Interesting" column, p. 4 |
| "presents the development of ideas and concepts in a logical and sequential way" | Met | One, Two, Three, Final, each naming its parent; p. 5 points to pp. 6 and 9 to 11 |

Plates 4A to 4C are photographs of a made dress on a form. Their captions do not call them drawings, so under the
premise this is not a fault. The sleeves in the plates read fuller than pattern piece 5 (F9), a nit.

## 8. Manufacturing Specification (pages 6 to 8)

### Mark: 4 out of 5, range 4 to 5

| Top-range dot point (quoted) | Status | Evidence | Why |
| --- | --- | --- | --- |
| "describes item(s) accurately and in detail" | Met | p. 6: size 10, fabrics with swatch references, construction features, finished measures, the named pattern and the drafted pieces, a modification table with reasons, a cut schedule separating cut from finished | Every figure agrees with pp. 5, 7, 8, and 12 |
| "produces drawings that clearly reflect the textile item(s) and which are of professional standard" | Partly met | 6.1 and 6.2 front and back, 1:10, grain arrows, dimensioned; 6.3 to 6.6 details; p. 7 pieces at 1:15 with grain, fold, notches; layouts at 1:50. All measured true except the skirt of 6.1 and 6.2: hem 60 mm against 120 mm | "In proportion and ... to scale" fails on the main flats. One fault, repeated front and back (F1). The page exposes it: the overskirt hem in 6.4 is drawn true, so the dress hem the overskirt "clears" looks less than half as wide |
| "includes all the required details in the technical production plan" | Met | p. 8: swatches 8.1 to 8.5 at 50 x 50 mm; quantities; notions; itemised costs and a $229.15 total that re-adds; order of construction in three streams citing experiments; timeline | All five NESA elements present |
| "includes a product label that contains all the required aspects appropriate to the selected focus area" | Met | p. 7: three labels with brand, size, fibre content, care symbols and text, "Made in Australia", all at 12 pt; care agrees with the p. 12 table | All five fields, per piece |

What would lift it to 5: redraw the skirt on 6.1 and 6.2 so the hem measures 120 mm and the hip 48 mm at 1:10, or
reduce both flats to a scale that fits the box and change the chips to match.

## 9. Findings

Ordered by marks at stake. The fix is described; a person applies it. Nothing here is folio wording.

| ID | Priority | Page | Where on the page | Finding | Fix | Source |
| --- | --- | --- | --- | --- | --- | --- |
| F1 | P0 | 6 | Drawings 6.1 and 6.2, skirt | At 1:10 the hem measures 60.1 mm; half of 240 cm is 120 mm. The same flats are true at shoulder to hem (112.1 mm). 6.4 draws its 264 cm hem true. Costs 1 Manufacturing Specification mark | Redraw the skirt to the pattern at 1:10 (hip 48 mm, hem 120 mm) or rescale both flats and chips; re-measure every written dimension | `design-system/assets/production-front.svg`, `production-back.svg`; placed at `design-system/Folio Deck.dc.html` line 1051 |
| F2 | P0 | 9 | Experiment 2 plates | Plates show whole collars on a shirt and a bib, not the 12 cm sections on black satin the method made; the two plates are not one sample before and after | Show the actual sections, before and after, on the same board and lamp | `design-system/Folio Deck.dc.html` lines 1513 to 1516 |
| F3 | P0 | 10 | Plate 4.4 "Caught tulle" | Shows net caught against satin in a tulle-to-tulle trial | Show the tulle-to-tulle seam at the caught point | `design-system/Folio Deck.dc.html` line 1630 |
| F4 | P1 | 11 | Plate 9.4 and the Experiment 8 note | 9.4 shows the band split at centre back; the band is continuous and closes at the left side. The Experiment 8 note points to 9.4 for the closed band. With F2 and F3, costs 1 Investigation mark | Show the band continuous over the zip; add or point to a view of the left-side overlap | `design-system/Folio Deck.dc.html` lines 1825 and 1861 |
| F5 | P1 | 9 | Experiment 1 plate 1.2 | Plate 1.2 is front-on, so the 4 cm stand-off cannot be read from the grid the note describes; 1.3 is side-on. The scaffold 1.4 slot (previous review) was not rechecked | Show 1.2 side-on against the grid | `design-system/Folio Deck.dc.html` lines 1474 to 1478 |
| F7 | P2 | 12 | Second column, "Fibre alone did not predict the result" | "The satin and crepe samples were both polyester" is not stated in Experiment 3 on p. 9 | State the sample fibres on p. 9 or narrow the sentence | `design-system/Folio Deck.dc.html` line 1907; method line 1525 |
| F8 | P2 | 9 to 11 | Area headers | No page says where the physical samples sit or how they are numbered | Add one pointer to the sample display on p. 9 | `design-system/Folio Deck.dc.html` near line 1432 |
| F9 | P2 | 5 | Plates 4A to 4C, sleeves | Sleeves read fuller at the forearm than pattern piece 5 (28 cm hem into a 24 cm cuff) | Check the plates against the pattern, or record the ease | `design-system/Folio Deck.dc.html` line 798 |
| F10 | P2 | 1 and 2 | Image 2 caption; p. 2 head | "c. 1905" against the cited "1902-1904" record | Align the dates or say why they differ | `design-system/Folio Deck.dc.html` line 69 |
| F13 | P2 | 11 | Experiment 9 method and table | The method makes "three 40 cm plackets"; the table and plate report a fourth condition, 9.4 "With band", with no method | Add the band condition to the method or drop the row | `design-system/Folio Deck.dc.html` line 1833 |
| F11 | P3 | 3, 4, 5, 12 | Bottom of PMI tables; p. 12 closing | Lowest text at 398.1 mm against a footer rule at about 402.5 mm; one added line would overlap | Cut words before adding any | `design-system/deck.css` |

F6 and F12 concern the swing tag, the scaffold, and the labels sheet, which were not part of this request; see the
status table.

## 10. Submission checks outside this PDF

Unscored.

- The finished item matches the page 6 description: size 10, 40 cm invisible zip and neck hook, four collar snaps at
  4, 14, 24, and 34 cm, three hooks and two snaps on a 15 cm overlap, 25 mm braid in a 2 cm hem, tiers 18, 26, and 34
  cm set at 0, 14, and 34 cm.
- The physical samples sit in the scaffold slots under the folio's IDs, flat and labelled.
- The cover sheet is at the front, names Harrow and Vane 2140 and any outside help, and acknowledges AI assistance as
  NESA and the school require.
- The sewn labels and the swing tag agree with the final fibre content and care.
- The folio prints one-sided at 100 per cent on A3; measure 6.1 with a ruler before binding (112 mm shoulder to hem,
  and the hem width after F1).
- The box is under 0.2 cubic metres, no side over 1.2 m, untaped, nothing under glass.
- Authenticity and certification are the student's and the school's and are not part of this estimate.

## 11. Status of the previous review's findings

Previous review: `build/reviews/nesa-grading-review-2026-09-23.md`. The folio pages are unchanged, so every folio
finding stands.

| ID | Previous finding | Status on 26 September 2026 |
| --- | --- | --- |
| F1 | 6.1 and 6.2 hem at half width | Open, re-measured (60.1 mm) |
| F2 | Experiment 2 plates show whole collars | Open, seen on the render |
| F3 | Plate 4.4 tulle against satin | Open, seen on the render |
| F4 | Plate 9.4 band split at centre back | Open, seen on the render |
| F5 | Scaffold slot 1.4; plate 1.2 front-on | Plate 1.2 part open; scaffold part not rechecked |
| F6 | Swing tag symbol order and dry-flat symbol | Not rechecked; the tag is outside this request and changed in `d63ae8c` |
| F7 | "both polyester" unsupported on p. 9 | Open |
| F8 | No pointer to the physical samples | Open; no page mentions a sample display |
| F9 | 4A to 4C sleeve fullness | Open |
| F10 | Image 2 date | Open |
| F11 | Footer clearance tight | Open, standing constraint |
| F12 | Scaffold "Pique"; code term on labels sheet | Not rechecked; items outside this request |
| F13 | New | Experiment 9 fourth condition without a method |
