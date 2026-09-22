# Folio marking notes

How this repo's folio is marked, by a person or by an AI agent, and what the marking is for. The NESA facts are in
[nesa-marking-facts.md](nesa-marking-facts.md) and are not repeated here. This file is the premise, the local
standards, the placing method, the evidence rules, and the procedure for a rerun. It applies to any agent, Claude,
Copilot, or anything else; there is no per-agent version.

## 1. What this repo is for

The repo is an AI teaching solution. It shows how a Year 12 student can use an AI agent to mark their own major
work against the published criteria while they are still making it. The student learns what a marker looks for,
how an agentic workflow reads a document, and plain computer literacy: version control, a build script, a print
proof, a checklist.

The AI marks. The student makes. That boundary is the point of the exercise, and it matches NESA's rule that HSC
work must be the student's own (facts, section 6).

An agent working in this repo may:

- read the exported PDF and measure it: page count, text size, image sizes, scales, totals
- quote the NESA descriptor a section is judged against and say which dot point the evidence meets or misses
- point at the page, the caption, the number, or the missing mount that holds a mark back
- say what evidence would lift a section to the next range
- check spelling, punctuation, page limits, and cross-references

An agent working on a real student's folio must not:

- write the folio prose, or rewrite it beyond pointing out what a sentence claims without evidence
- draw the sketches, production drawings, or pattern pieces
- invent experiment methods, results, measurements, or conclusions
- generate images and present them as the student's samples, swatches, or photographs
- decide the design

The folio in this repo is fictional, so its prose, plates, and numbers were produced to build the example. That is
allowed here because nothing in it is submitted. A student copying this workflow replaces every generated plate
and every invented result with their own work, and acknowledges AI assistance the way NESA and their school
require.

## 2. The premise the folio is marked under

The folio is written as the finished submission of a fictional student, with no note to the marker. It is marked
as the finished submission: the question is always "what would a NESA marker holding this printed page give it",
never "is this real".

- Every plate is generated and every number is invented. `design-system/assets/plates.json` and the `.prompt.txt`
  files record that. Provenance lives in the repo, never on a printed page. No page says "generated",
  "placeholder", "schematic", or "for an HSC submission I would".
- A generated plate is marked on what it shows and what its caption says. A rendered swatch, a sample photograph,
  or a composite study is accepted as explanatory evidence where its caption is honest about what it is. It is a
  finding only if it shows something other than what the method made, or if the caption misrepresents it.
- The physical samples, the garment, the cover sheet, and the box are outside the PDF. They are recorded as not
  assessable and never guessed at. The folio and the mount scaffold say where the physical pieces sit.
- The textile item's 25 marks are never estimated. A review may say which item criteria the folio evidences.
- Authenticity and certification are never part of the estimate. They are listed under "submission checks outside
  this PDF" and left there.

Only the folio's 25 marks are ever estimated. The target is the top descriptor in every section: 5, 5, 5, and
9 to 10. The marks are a self-assessment, not a prediction, and every review says how far the evidence is from the
target and which fault is in the way.

The premise is worth at most one mark. When the same PDF was read under a strict digital-only premise and under
this one, the gap was one Investigation mark withheld for photographed samples. Everything else that moved a mark
was a fault on the page: a wrong scale chip, a cutting layout that contradicted the cut list, a caption calling a
photograph a drawing. Pick this premise, state it, and hold it for the whole review.

## 3. Local standards above NESA

These go beyond the published criteria (facts, section 9). The folio meets them because they make the top
descriptor easy to evidence. A review checks them and reports them, but marks are placed on the NESA descriptor,
not on these.

| Local standard | Why |
| --- | --- |
| Three experiments per area: materials, equipment, manufacturing processes | Makes "experiments extensively" visible at a glance |
| Aim, Method, Results, Conclusion for every experiment, with a control and a quantified result | Forces a conclusion that stays inside its method |
| Every conclusion names the page where its decision landed | Evidences "modifies design and/or construction as a result" |
| Every feature on a sketch keyed and classified A, F, or A + F | Evidences the functional and aesthetic analysis |
| PMI table for every design idea, in elements and principles vocabulary | Separates "critically analyses" from "describes" |
| Type never smaller than 12 pt, including SVG text and overlay labels | NESA's floor, applied with no exceptions |
| Swatches 50 x 50 mm, labelled, cited from page 6 | A size a marker can read a weave from |
| Every image, sketch, drawing, swatch, and sample numbered and cited in the text | Unreferenced images are decoration |
| Cross-references in one form: Experiment 8, p. 11; Drawing 6.2, p. 6; Image 3, p. 1 | So every reference can be followed |
| Page 6 is the single source for dimensions and pattern modifications | Pages 7, 8, 10, and 12 repeat it and never vary it |
| Writing rules in `AGENTS.md`: plain prose, Australian English, no dashes but the hyphen, straight quotes | The marker reads for evidence, not style |

## 4. Placing a mark

1. Read the section's top range, dot point by dot point.
2. For each dot point, find the evidence on the page: the image, the dimension, the mounted sample, the table row.
   A claim without evidence on the page scores as if it were not made.
3. If every dot point has evidence and nothing on the page contradicts it, the section is in that range. Give the
   top mark. Give the bottom mark of the range when one dot point is met in words but the plate, number, or mount
   beside it does not support the words.
4. If one dot point is met only at a lower range and the rest are met at the top, use NESA's combination
   sentence: the section sits at the boundary between the two ranges, which is 3 for a five-mark section and 8 or
   6 for the ten-mark section. Say which dot point pulled it down.
5. If two or more dot points are met only at the lower range, the section is in the lower range.
6. Record the dot point at issue, quoted, in the summary table, so the next reviewer can see which sentence the
   mark hangs on.

Faults are not additive. Three nits under one dot point are one fault. A fault a marker with a ruler or a
calculator would find (a scale chip, a total, a gathering ratio, a collar longer than its neckline) is a
contradiction, not a nit, because it makes the marker doubt every number around it. Three independent
contradictions under one dot point make that dot point "elementary standard", not "professional standard", and the
section goes to the combination rule.

## 5. Evidence rules that decide most marks

- **The plate beats the caption.** If a caption says "study drawing" and the plate reads as a photograph, the
  section is marked on the photograph and the caption becomes a finding. Words cannot upgrade a picture.
- **A stated scale is a claim.** Measure it. Shoulder to hem at 1:10 is 112 mm for 112 cm. A wrong chip is worse
  than no chip.
- **Re-add every total.** Costing, gathering ratios (tier length over carrier length), band length (waist plus
  overlap), tier positions against skirt length.
- **Follow every cross-reference.** "Experiment 6" must exist, and "step 4 on page 8" must say what the
  conclusion says it says.
- **A mount must show what the method made.** A 40 cm seam sample is not a whole skirt on a form. Eight finishes
  tested means eight samples shown, or a sentence saying where the other four are.
- **A conclusion stays inside its method.** "Does not fray" is what 48 hours on a hanger can show; "outlasts" is
  not.
- **Care agrees everywhere.** Page 7 labels, the page 12 table, the swing tag, and the product labels say the same
  thing for the same fibre.
- **Page limits are absolute.** Anything past a section's pages is invisible to the mark.
- **Do not penalise the format.** A rendered plate, a digital drawing, or a monochrome sketch is not a fault. A
  teaching folio may be explanatory. Penalise weak reasoning, unsupported claims, mismatches between method and
  conclusion, and missing explanation.

## 6. What to penalise and what not to

Penalise:

- a claim about materials, construction, or results that the page does not evidence
- a plate, number, or mount that contradicts the words beside it
- a design step with no reason, or an experiment whose result changed nothing
- a conclusion that outruns its method
- a missing required element: a label field, a subheading, a dimension, a view, a swatch
- a breach of a page rule: text under 12 pt, a name, a page over the limit

Do not penalise:

- a generated or rendered plate whose caption says what it is
- a digital or monochrome drawing
- the absence of a physical mount in a PDF, when the folio says where the physical piece is
- the absence of a local standard from section 3, when the NESA dot point is still evidenced
- style, unless it costs legibility

Do not reopen a decision the folio has already settled unless the premise in section 2 has changed. Two examples:
the teaching disclosure on page 1 was declined because provenance lives in the repo, not the folio; a ruler in
every sample photograph was declined because the methods state the grid and the sample sizes.

## 7. Rerunning the NESA analysis

The artefact is always the exported PDF in the repo root, never the HTML or a preview. Record its export date, size,
and SHA-256 so the next review knows which file it compared.

Checks to run before reading a word:

- Page count and size on every page; pages per section against 2, 3, 3, 4.
- Smallest text span on every page, including SVG text and overlay labels, against the 12 pt floor.
- Placed size of every image; swatches about 50 x 50 mm.
- Footer clearance: the lowest body text on each page against the footer.
- The costing total.
- Curly quotes, en and em dashes, and the `AGENTS.md` banned words in the extracted text.
- Drawn extent of every plate that carries a scale chip, against the dimension written on it.

Then:

1. Read each section against its descriptor in NESA's order. Mark Investigation, Experimentation and Evaluation
   first and hardest; it is worth as much as any two others.
2. Follow every cross-reference. Re-add every total. Check that sizes, fibre content, and care agree between
   page 6, page 7, page 12, the labels, and the tag.
3. Open every image and read every caption. Placeholders count as missing evidence.
4. Fill the compliance audit, then the section table, then list findings by marks at stake.
5. If a previous review exists, finish with a status table for every one of its findings, so nothing is silently
   dropped. Continue its finding numbers.

Write the review to `build/reviews/nesa-grading-review-<date>.md`. The `build/` folder is ignored by git, and
reviews are working output, not documentation. If a review changes a rule, the rule changes in this file or in
`nesa-marking-facts.md`, and the folio change is recorded in the CHANGELOG. A review on its own takes no CHANGELOG
entry.

Run `npx markdownlint-cli2` and cspell on the review before handing it over.

### Compliance audit

| Rule | Status | Evidence |
| --- | --- | --- |
| No student name anywhere; student number only | | |
| Font 12 pt or larger everywhere, including tables, captions, and drawing labels | | |
| Text clear, legible, and distinct from the background | | |
| A3 or A4 consistently, one side only | | |
| Section page limits met; NESA order kept; no cover page counted | | |
| Every image numbered and referenced in the text | | |
| Nothing that must be unfolded or flipped; all mounts flat | | |
| Swatches about 5 x 5 cm, labelled | | |
| Commercial patterns acknowledged on page 6 and on the cover sheet | | |
| Packaging within the size rule; box untaped | | |

### Section table

| Section | Max | Range | Dot point at issue | Mark | Achievable | What holds it back |
| --- | --- | --- | --- | --- | --- | --- |
| Design Inspiration (pages 1 to 2) | 5 | | | | | |
| Visual Design Development (pages 3 to 5) | 5 | | | | | |
| Manufacturing Specification (pages 6 to 8) | 5 | | | | | |
| Investigation, Experimentation and Evaluation (pages 9 to 12) | 10 | | | | | |
| Total | 25 | | | | | |

### Findings

One row per finding: ID, priority, page, where on the page, the finding, the fix, and the source line in
`design-system/Folio Deck.dc.html` or the css file where the fix goes. Order by marks at stake. The usual pattern
is that the writing is already in the top range and the marks are lost to evidence: a wrong scale, a mount that
shows the wrong thing, a claim that does not survive checking. Fix those before polishing prose.

- P0: marks directly at stake (missing evidence, breached rule).
- P1: internal consistency (a number or a name that differs between pages).
- P2: insurance and polish (a caption, a credit, a nit in the type).
- P3: print and submission logistics.

### Submission checks outside this PDF

Every review ends with the checks a marker would make on the physical submission, without scoring them: the
technical description matches the finished item, the physical samples sit in the scaffold slots as the captions
read, the cover sheet names the commercial pattern and any outsourcing, the labels and tag agree with the final
fibre content and care, the print is one-sided at 100 per cent with one drawing measured with a ruler before
binding, and the box is under 0.2 cubic metres, no side over 1.2 m, untaped.

## 8. History

Between 20 and 22 September 2026 the folio was reviewed six times and revised twice. The first reviews found the
marks in the evidence, not the writing: schematic pattern pieces, under-dimensioned drawings, an unnamed pattern,
6 pt text on a true-size tag, swatches captioned as placeholders. The revisions redrew the drawings as vectors at
stated scales, completed the experiment matrices, separated cut from finished dimensions, fixed the collar and
band geometry, and made every caption describe the plate in its box. The final review placed every section in its
top range. The CHANGELOG records the folio changes; the dated review files were working output and were removed
when this file was written.
