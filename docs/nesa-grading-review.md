# NESA grading reviews by different AI agents

<!-- cspell:words AEST Astra Antigravity -->

The folio can be marked by any AI agent that can read a PDF and follow written instructions. This page puts four of
those markings side by side. All four marked the same export against the same rules on the same day, and they did
not all agree. That is the point of the page: an AI marking is one reader's judgement, not a verdict, and a
different agent or model will have its own view on what is right or wrong with the pages it is marking.

The full reviews are stored in [example-grading-marks/](../example-grading-marks/), one file per agent and model.
They are a snapshot of one export and go stale when the folio changes.

## What was marked

| Field | Value |
| --- | --- |
| File | `output/1-the-ravens-ledger-folio.pdf`, 12 A3 pages |
| Exported | 24 September 2026, 15:12 AEST |
| Size | 104,287,839 bytes |
| SHA-256 | `05b68f950a1ac465ccfc90650e199086b9e32c3d565dd74919470327fb03113b` |
| Marked | 26 September 2026 |
| Rules | [nesa-marking-facts.md](nesa-marking-facts.md) and [folio-marking-notes.md](folio-marking-notes.md) |

Every review records the same SHA-256, so every agent read identical pages. Only the folio's 25 marks are scored.
The textile item's 25 marks, the physical samples, the cover sheet and the packaging are outside the PDF, and no
agent estimated them.

## The marks

| Agent (host) | Model | Design Inspiration /5 | Visual Design Development /5 | Manufacturing Specification /5 | Investigation, Experimentation and Evaluation /10 | Total /25 | Review |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Code | Claude Opus 5.5 | 5 | 5 | 4 | 9 | **23** | [Markdown](../example-grading-marks/claude-opus-5-5-nesa-grading-review-2026-09-26.md) |
| Codex | GPT-6 Astra | 5 | 5 | 4 | 9 | **23** | [Markdown](../example-grading-marks/codex-gpt-6-astra-nesa-grading-review-2026-09-26.md), [JSON](../example-grading-marks/codex-gpt-6-astra-nesa-grading-review-2026-09-26.json) |
| GitHub Copilot | GPT-6 Luna | 5 | 5 | 4 | 9 | **23** | [Markdown](../example-grading-marks/copilot-gpt-6-luna-nesa-grading-review-2026-09-26.md) |
| Google Antigravity | Gemini 3.8 Flash | 5 | 5 | 5 | 10 | **25** | [Markdown](../example-grading-marks/antigravity-gemini-3-8-flash-nesa-grading-review-2026-09-26.md) |

Three agents give 23 and one gives 25. All four put every section in its top mark range, and all four give full
marks for Design Inspiration and Visual Design Development. The disagreement is in the two sections where a marker
has to measure and compare, not only read.

## Where they agree and where they differ

### Manufacturing Specification: 4 or 5

Claude, Codex and Copilot each measured the dress flats on page 6 (drawings 6.1 and 6.2). At the stated 1:10 scale
the skirt hem is about 60 mm wide, but half of a 240 cm hem should be 120 mm. The shoulder-to-hem length on the same
drawings is true to scale, so the error is inside one view. All three withhold 1 mark for it.

They do not frame it the same way. Claude and Copilot treat it as a plain scale error. Codex says the finding depends
on reading 6.1 and 6.2 as flat drawings, and offers the fix of stating a draped-view convention as an alternative to
redrawing.

Gemini gives 5. It checked the 112 mm shoulder-to-hem length and the scale of drawing 6.4, and describes the drawings
as having "exact dimensional consistency". It did not report the hem width.

### Investigation, Experimentation and Evaluation: 9 or 10

Three agents withhold 1 mark because some sample photos on pages 9 to 11 do not show what their experiment's method
made. They agree on the principle but pick different photos:

| Sample photo | Claude | Codex | Copilot | Gemini |
| --- | --- | --- | --- | --- |
| Experiment 2 (p. 9): whole collars, not the 12 cm test sections | Costs the mark | Costs the mark | Costs the mark | Not raised |
| Plate 4.4 (p. 10): tulle caught against satin in a tulle-to-tulle trial | Costs the mark | Costs the mark | Costs the mark | Not raised |
| Plate 9.4 (p. 11): band shown split at centre back, but it closes at the side | Costs the mark | Not raised | Raised as a labelling question, no mark | Not raised |

Claude also says a stricter reading of the marking notes would count these as three separate faults and give 8, and
explains why it chose 9. Gemini gives 10: it reads the nine experiments, their controls and their numeric results as
meeting every top-range point, and raises no photo mismatch.

### Other findings

None of these costs a mark in any review. They show how differently each agent read the same pages.

| Finding | Claude | Codex | Copilot | Gemini |
| --- | --- | --- | --- | --- |
| Experiment 9 reports a fourth condition, "9.4 With band", that its method never describes (p. 11) | Yes | | Yes | |
| "The satin and crepe samples were both polyester" is not supported by Experiment 3 (p. 12) | Yes | | Yes | |
| Image 2 is dated "c. 1905" but the cited record says 1902 to 1904 (pp. 1 to 2) | Yes | | Yes | |
| Plate 1.2 is front-on, so its grid cannot show the stated stand-off (p. 9) | Yes | | | |
| No page says where the physical samples are or how they are numbered (pp. 9 to 11) | Yes | | | |
| Sleeves in the final design look fuller than pattern piece 5 (p. 5) | Yes | | | |
| Body text sits close to the footer rule on four pages | Yes | | Noted in its audit, passed | |
| Drawing 6.6 "Cuff section" could be misread as a pattern piece (p. 6) | | | | Yes |
| Drawing 6.4's SVG scaling could confuse an automated measuring tool (p. 6) | | | | Yes |
| Experiment 1 would benefit from a rehearsal-length wear trial (p. 9) | | | | Yes |

Claude reports the most findings and Codex the fewest; Codex keeps to the three that affect the mark. Gemini's
findings are different in kind: advice on captions, file internals and extra testing rather than mismatches between
the pages.

## What this shows

- **A marking is a reading, not a fact.** Four agents, one PDF and one set of rules produced two totals and four
  different findings lists. The same agent run again, or the same model in a different host, can also land
  differently.
- **Agreement is a stronger signal than any single mark.** A fault that three independent agents found and measured,
  like the hem width or plate 4.4, is very likely real. A fault that only one agent raised is worth a look, not an
  automatic fix.
- **A higher mark is not a better review.** Gemini's 25 comes from not reporting the hem width, which the other three
  measured. Check the evidence behind a mark, not only the number.
- **A person decides.** Each finding names a page and what to measure. Take a ruler to the printed page or open the
  plate before changing anything in the folio.

## Run your own

Any agent can run this marking. The rules are plain Markdown in the repo, so the agent does not need anything
special:

- **With a marking agent set up in this repo:** Claude Code, GitHub Copilot and Codex each have a `nesa-assessor`
  agent (see [agents.md](agents.md)). Ask it to "mark the folio" or "grade the PDF". It writes its review to
  `build/reviews/`.
- **With any other agent or model:** point it at the rules and the PDF, for example:

  ```text
  Read docs/nesa-marking-facts.md and docs/folio-marking-notes.md in full. Then mark
  output/1-the-ravens-ledger-folio.pdf against them as a NESA marker would, evidence first, and write the review
  to example-grading-marks/<host>-<model>-nesa-grading-review-<date>.md.
  ```

To add a result to this page, save the review in `example-grading-marks/` under that naming pattern, then add a row
to the marks table and a column to the findings tables. Check that the review records the same SHA-256 as the others.
A review of a different export is a new comparison, not another row in this one.
