---
name: get-nesa-grading-rules
description: Load the marking reference for this repo before any grading, marking, or review task
---

# Get NESA grading rules

Read `docs/nesa-marking-facts.md` for what NESA marks and the mark ranges, then `docs/folio-marking-notes.md` for
the premise, the placing method, the evidence rules, and the rerun procedure. Use both as the marking reference
for any grading activity.

The facts file was checked against the NESA pages it lists on 22 September 2026. If a rerun is more than a term
later, open those pages again and note any change before marking.

`scripts/review_guard.py` is a pre-tool hook for any host that has one. It denies a write aimed outside
`build/reviews/`, so an assessor can write its review and nothing else. `--path FILE` checks one path by hand.
