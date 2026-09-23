<!-- markdownlint-disable MD033 MD041 -->
<!-- The wiki Home page. scripts/docs_to_wiki.py rewrites the links and replaces the index mark with every doc. -->

<p align="center">
  <img src="../../design-system/assets/house-mark.svg" alt="The Raven's Ledger house mark" width="96">
</p>

<h1 align="center">The Raven's Ledger</h1>

<p align="center">
  <em>A fictional HSC Textiles and Design major work, marked by an AI while it is still being written.</em>
</p>

<p align="center">
  <img src="../../design-system/assets/final_front.png" alt="Final design 4A, front, on the form" width="250">
  <img src="../../design-system/assets/final_back.png" alt="Final design 4B, back, on the form" width="250">
  <img src="../../design-system/assets/final_collar.png" alt="Final design 4C, overskirt off and collar on" width="250">
</p>

<p align="center"><sub>Final designs 4A, 4B and 4C: the dance, the back, and the change.</sub></p>

## Welcome

This wiki goes with a twelve-page A3 folio for a school dance dress, inspired by the dress Wednesday Addams wears
to the Rave'N dance. The student, the school, the dress, and every test result are invented. Nobody has
submitted any of it.

The dress is only the test case. The real question is this: can the folio be built like software, so a student
gets marker-style feedback every time a page changes, instead of once, after it is handed in?

## How it works

```mermaid
flowchart LR
  A["Student writes and draws<br/>the folio pages"] --> B["Design system renders<br/>twelve A3 pages"]
  B --> C["Print proof at true size<br/>and a copy in Canva"]
  B --> D["nesa-assessor agent marks<br/>the PDF against NESA criteria"]
  D --> E["Review with evidence<br/>and page references"]
  E --> A
```

- **The student makes the work.** Every word and plate in the folio belongs to the student. An agent never writes
  folio prose or draws a plate.
- **The pages are code.** Each page is a design component with a shared stylesheet, so type sizes, colours and
  page limits are checked, not eyeballed.
- **The AI marks.** The `nesa-assessor` agent reads the exported PDF against the published marking guidelines and
  reports what a marker would find: unsupported claims, contradictions, and missing required elements.

## The folio, section by section

The four sections use NESA's names word for word. Each one has a period title in the masthead and its own
colourway.

| | Section | Pages | What it holds |
| --- | --- | --- | --- |
| <img src="../../design-system/assets/i1.png" alt="Study drawing of the dance dress" width="110"> | **Design Inspiration**<br/>*The Sources, Gathered* | 1 to 2 | Study drawings of the dress and its period sources: 1905 mourning dress, 1926 tulle, 1955 party dress, jet beading. |
| <img src="../../design-system/assets/s3a.png" alt="Sketch 3A, front" width="110"> | **Visual Design Development**<br/>*The Designs, Weighed* | 3 to 5 | Sketches, the options weighed against each other, and the final design. |
| <img src="../../design-system/assets/draw_front.png" alt="Drawing 6.1, front flat" width="110"> | **Manufacturing Specification**<br/>*The Making* | 6 to 8 | Flat drawings, pattern pieces with modifications, cutting layouts, and the materials list. |
| <img src="../../design-system/assets/exp5-2.png" alt="Experiment 5.2, ruffler foot" width="110"> | **Investigation, Experimentation and Evaluation**<br/>*Trials & Proofs* | 9 to 12 | Nine experiments with four trials each, the results, and the evaluation. |

## Materials

<p align="center">
  <img src="../../design-system/assets/swatch_satin.png" alt="Black crepe satin" width="150">
  <img src="../../design-system/assets/swatch_tulle.png" alt="Black nylon tulle" width="150">
  <img src="../../design-system/assets/swatch_pique.png" alt="White cotton pique" width="150">
  <img src="../../design-system/assets/swatch_trims.png" alt="Horsehair braid, grosgrain, and petersham" width="150">
  <img src="../../design-system/assets/swatch_notions.png" alt="Zip, hooks and bars, snaps, and jet beads" width="150">
</p>

<p align="center"><sub>Crepe satin, nylon tulle, cotton pique, trims, and notions.</sub></p>

## From trial to pattern

<p align="center">
  <img src="../../design-system/assets/exp1-1.png" alt="Experiment 1.1, soft tulle, gathered" width="250">
  <img src="../../design-system/assets/layout.png" alt="Cutting layout, 1 : 20" width="200">
  <img src="../../design-system/assets/pattern_front.png" alt="Bodice front pattern pieces, 1 : 10" width="300">
</p>

<p align="center"><sub>A gathered tulle trial, the cutting layout, and the bodice front with its modification in wine.</sub></p>

## Production items

The folio lives in a binder, and the dress leaves with a swing tag. Both are drawn by the same stylesheet as the
pages, so they carry the same masthead, rules, and house mark.

<p align="center">
  <img src="images/binder-spine.png" alt="Binder spine insert, 436 x 59 mm, laid on its side" width="820">
</p>

<p align="center"><sub>The binder spine insert, laid on its side. The four bands are the four folio sections.</sub></p>

<p align="center">
  <img src="images/swing-tag-front.png" alt="Swing tag, front" width="210">
  <img src="images/swing-tag-back.png" alt="Swing tag, back, with contents and care" width="210">
</p>

<p align="center"><sub>The swing tag, 70 x 120 mm, front and back.</sub></p>

<p align="center"><sub>These two are rendered from the design system each time the wiki is published.</sub></p>

## Where to start

- New here? Read the [design rationale](../design-rationale.md) for why the folio looks the way it does.
- Marking something? Read the [NESA marking facts](../nesa-marking-facts.md) and the
  [folio marking notes](../folio-marking-notes.md) first. They govern every review.
- Printing or making? The [print specifications](../print-specifications.md) and
  [production items](../production-items.md) cover paper, binding, the swing tag, and the labels.
- Curious about the agents? [Agents in this repo](../agents.md) shows how one agent runs on Copilot, Claude Code,
  and Codex.

## Every page

<!-- wiki-index -->

## About this wiki

Everything here is fictional. The plates are generated study drawings and stand in for the student's own artwork.
No real student, school, or screen still appears anywhere. The wiki is rebuilt from the
[docs/ folder](../../docs) on every push to `main`, so edit the repository, not the wiki.
