# AGENTS.md

Rules for anyone, human or agent, working on this repo. Read all of it before touching the folio or the scripts.

## Marking rule for agents

This project is a fictional HSC Textiles and Design folio built as an AI teaching solution: the student makes the
work, the AI marks it against the published criteria. An agent never writes folio prose, draws plates, or invents
results for a real student. It marks, measures, and points at evidence.

Two documents govern any marking, review, or grading task. Read both before assessing a page, a claim, or an
evidence issue:

- [docs/nesa-marking-facts.md](docs/nesa-marking-facts.md): what NESA marks, the mark ranges verbatim, the page
  rules, and what NESA does not require.
- [docs/folio-marking-notes.md](docs/folio-marking-notes.md): the premise this folio is marked under, the local
  standards, how a mark is placed, the evidence rules, and the rerun procedure.

The Copilot agent in `.github/agents/nesa-assessor.agent.md` runs the marking procedure and the
`get-nesa-grading-rules` skill in `.github/skills/` loads the two documents. Both defer to the documents; a rule
changes in the documents, never in the agent.

In short: the folio is marked as the finished submission a marker holds. A generated plate is marked on what it
shows and what its caption says, and is never penalised for being digital. The physical samples and the garment
are outside the PDF and are never guessed at. Marks are lost to unsupported claims, contradictions a ruler would
find, and missing required elements, not to format.

## What this repo is

A fictional HSC Textiles and Design Major Textiles Project folio: twelve A3 pages plus four physical production
items (binder spine insert, swing tag, product labels, mount scaffold). The pages are `.dc.html` design components
rendered by `design-system/deck-stage.js` and `design-system/support.js`, styled by `design-system/deck.css` and
one stylesheet per item. `scripts/preview.ps1` renders them to static HTML for a browser and a true-size print
proof. `scripts/canva.py` flattens the deck for Canva and checks it back.

Everything is invented. Never add a real student name, student number, school, teacher, or a photograph of a real
person. Never add copyrighted material (commercial patterns, screen stills, magazine scans, exam papers, other
students' folios). Link to public sources instead. The design brief is in `README.md`.

## Writing rules

The folio text is written by a fictional Year 12 student, first person, and is marked against
`docs/nesa-marking-facts.md`. Every sentence has to earn its place inside the page limits.

- Plain prose. Short sentences. Say the thing, then stop.
- No AI jargon and no marketing-speak. Banned: "delve", "leverage", "unlock", "seamless", "robust", "journey",
  "game-changer", "it's worth noting", "at the end of the day".
- Compare generated prose/texts/items with what is generally referred to as "AI Slop" and reword the text to more human language
- Cut adjectives that add nothing. Cut sentences that restate the previous one.
- Concrete over abstract: real measurements, real test results, real failures.
- Headings are plain and descriptive.
- NESA section names are used verbatim and never paraphrased: Design Inspiration, Visual Design Development,
  Manufacturing Specification, Investigation, Experimentation and Evaluation.
- Type is never smaller than 12 pt on a folio page. If a page is crowded, cut words.

### Language

- Australian English, always: colour, organise, behaviour, licence (noun), practise (verb), program.
- Dates in prose read day month year, for example 13 September 2026. Dates in data files stay ISO (`YYYY-MM-DD`).

### Punctuation and typography

- Never use an em dash or an en dash. Only the plain hyphen-minus `-`, with a space either side when it stands in
  for a dash.
- Plain straight quotes. No curly quotes.
- Oxford comma.
- One space after a full stop.

## Repo layout

- `design-system/` the deck, the items, their css, the two runtime files, `canva.config.json`, and `assets/`.
- `design-system/assets/plates.json` lists every image slot. `scripts/make_placeholder_plates.py` generates the
  SVGs from it. Real artwork replaces a placeholder by keeping its filename.
- `design-system/meta/` the design notes page (the design process, the graphic elements as live specimens, and a
  ledger of changes, with the full colour system, token derivation, and masthead transitions).
  Built by `preview.ps1 -Item meta`.
- `docs/` NESA marking facts, folio marking notes, brand kit, print specs, production items, Canva pipeline,
  and design rationale.
- `scripts/` `preview.ps1`, `canva.py` and the `canva/` package, `make_placeholder_plates.py`.
- `build/` generated output, ignored by git. Nothing generated is ever committed.
- `design-system/canva.local.json` holds Canva design, page and asset ids. Ignored by git. The committed template
  is `canva.local.example.json`.

## Commands

```pwsh
pwsh scripts/preview.ps1 -Item folio|spine|tag|labels|mounts|meta|all [-Guides] [-Bleed] [-NoOpen]
python scripts/canva.py build [--verify] [--pdf]
python scripts/canva.py extract
python scripts/canva.py ops --page 01 --phase elements|format
python scripts/canva.py check --dump read-design.json
python scripts/canva.py all
python scripts/make_placeholder_plates.py
npx markdownlint-cli2 "**/*.md"
npx -p cspell -p @cspell/dict-en-au cspell --no-progress "**/*.md"
python -m compileall -q scripts
```

Setup: `python -m venv .venv`, `pip install -r requirements.txt`. Chrome or Edge on `PATH`, or `CHROME_PATH` set,
for anything under `canva.py`. CI (`.github/workflows/ci.yml`) runs markdownlint, cspell and compileall.

## Load-bearing constraints

These are documented in the css comments and `docs/brand-kit.md`. Do not change them casually.

- The A4 items import at `793 x 1122` px, deliberately rounded down. Rounding up pushes the page box past the
  sheet and the browser scales the whole document.
- `deck-stage.js` writes `@page` from the `x-import` size. There is no `@page` rule in any css file.
- `.page` is pinned to 420 mm. Nothing on an A4 item reuses it.
- `margin-left: calc(-1 * var(--m2-slant))` positions the masthead area block. Any property in that expression
  must always carry a unit. A unitless `0` invalidates the declaration and opens a 15 mm gap.
- Area colours are fill and rule colours, never text colours. Only the `emph` token may colour text, and it is
  derived: `color-mix(in srgb, <accent> 80%, #1A1A1A)`, written out literally with its measured contrast ratio.
- Every css comment that records a measured width for the wordmark or a label is keyed to the string's length.
  Change the string, re-measure in the preview, update the comment.

## Commits

Follow `.github/copilot-commit-message-instructions.md` (Conventional Commits mapped to Keep a Changelog).

## Code style

- Two-space indent for html, css, json and markdown. Four spaces for Python and PowerShell. Line width 120.
- Comments follow the same prose rules as the folio: short, plain, no dashes other than `-`.
- Do not add tooling, config or abstractions the task did not ask for.
