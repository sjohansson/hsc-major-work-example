---
name: canva-sync
description: Push a repository's HTML deck into a Canva design, one way, and check Canva back against the repository. Use for "sync to Canva", "push the deck to Canva", "update the Canva design", "check Canva against the repo", or when a Canva connector is available and the repository holds a deck with a canva.config.json. Flattens the deck into the shape Canva's importer reads, proves it renders identically in a browser, measures it into an element list, and generates the connector operations page by page. Canva is written to, never read back into the deck.
license: MIT
compatibility: Python 3.12 or newer, Chrome or Edge on PATH, and a Canva MCP connector for the push itself.
metadata:
  version: "1.0.0"
---

# Canva sync

Design in the repository; look at it in Canva. The deck is the source of truth and this skill carries it one way
into a Canva design. An edit made in Canva is reported back as a difference for a person to decide about. It is
never written into the deck, and nothing in this skill can write into the deck: the code refuses, the agents have
no edit tool, and a hook denies the attempt.

## What it does

The deck is real HTML with a real stylesheet: classes, custom properties, `calc()`, pseudo-elements, tables.
Canva's importer reads none of that. It reads a flat tree of boxes with literal inline styles. So the pipeline
resolves the cascade in Python, rewrites the four constructs Canva cannot read, proves the result renders
identically, measures it, and turns the measurements into connector operations.

```text
deck + stylesheet                 the source of truth
      |  build
      v
<output_dir>/canva-import-rev.html   flattened, pages in reverse (the order the importer reads)
      |  verify      renders both in headless Chrome and diffs them pixel for pixel
      |  extract
      v
<output_dir>/canva-layout.json       ordered elements per page, with geometry and style
      |  ops
      v
connector operation arrays        pushed page by page
      ^
      |  check       compares what Canva returned against canva-layout.json
```

`references/how-it-works.md` explains each stage and what crosses into Canva and what does not.

## Commands

Run from the repository root. `PATH_TO_BUNDLE` is wherever this skill folder sits; in this repository it is
`.agents/skills/canva-sync`.

```text
python PATH_TO_BUNDLE/scripts/canva_sync.py doctor [--full]
python PATH_TO_BUNDLE/scripts/canva_sync.py build [--verify] [--pdf]
python PATH_TO_BUNDLE/scripts/canva_sync.py verify [--scale 2] [--keep DIR]
python PATH_TO_BUNDLE/scripts/canva_sync.py extract [--page 07]
python PATH_TO_BUNDLE/scripts/canva_sync.py ops --summary [--json]
python PATH_TO_BUNDLE/scripts/canva_sync.py ops --page 01 --phase elements [--chunk N]
python PATH_TO_BUNDLE/scripts/canva_sync.py ops --page 01 --phase format --from-dump response.json
python PATH_TO_BUNDLE/scripts/canva_sync.py ops --page 05 --phase page
python PATH_TO_BUNDLE/scripts/canva_sync.py probe --tools tools.json
python PATH_TO_BUNDLE/scripts/canva_sync.py check --dump design.json [--refresh-ids]
python PATH_TO_BUNDLE/scripts/canva_sync.py all
python PATH_TO_BUNDLE/scripts/canva_sync.py selftest
```

Every command takes `--config PATH`; without it the config is found by walking up from the working directory.
Every command is non-interactive and prints its payload on stdout and its diagnostics on stderr, so a chunk can
be piped straight into a connector call. Exit codes: `0` did it, `1` ran and the answer is no, `2` bad arguments,
`3` a missing prerequisite. `--help` on any command prints the rest.

## The procedure, gate by gate

Do not skip a gate. Each one exists because the step after it is expensive to undo in someone's Canva account.

1. **doctor.** Stop on any failure and report it. A warning about a missing browser means verify and extract
   cannot run, which means there is no push today.
2. **build --verify.** Stop if any page is over tolerance, and report the `diff-NN.png` paths under
   `<output_dir>/verify/`. A page over tolerance means the flattened copy is not the deck, so pushing it would
   put something else in Canva. Nothing goes past this gate.
3. **extract.**
4. **ops --summary --json.** If `unmapped_assets` is not empty, say which images have no asset id and ask
   whether to push with placeholder rectangles or stop and upload them first. Do not decide this silently.
5. **probe.** List the connector's tools with their input schemas, save that as JSON, and run `probe --tools`.
   Stop on a mismatch, including any `field_problems`. If only the legacy public dialect matches, say so and
   switch to the import-from-URL route in `references/canva-connector.md` rather than pushing operations the
   connector will reject.
6. **Push, one page at a time.** A page with no id yet is added first with `ops --phase page`. For each page:
   open an editing transaction with `read-design`, apply the `elements` chunks in order with `edit-design`, save
   the last response, apply the `format` phase with `--from-dump`, compare the draft thumbnail against
   `<output_dir>/verify/out-NN.png`, show the person the preview, and commit only when they approve. On any
   error, cancel the transaction, report what happened, and stop. Do not carry on to the next page.
   `references/push-loop.md` has the detail, including what to do on the first page of an unverified dialect.
7. **check.** Feed the connector's design JSON to `check --dump -`. On a fresh design use `--refresh-ids` once,
   which writes the design id and page ids into the local id file. Text Canva has that the repository does not
   is reported as a human decision. Never edit the deck to match Canva.

## Report in this order

doctor result; verify's worst page and its percentage; the pages pushed with their operation counts; the probe
result and which dialect was used; the check result; and the paths written. If a gate stopped the run, say which
gate and why, and what would clear it.

## Boundaries

- One way. The repository is the source of truth. A difference found in Canva is reported, never applied to the
  deck, and never worked around by editing the deck to agree with Canva.
- This skill writes only inside the config's `output_dir`, plus the local id file when `--refresh-ids` is asked
  for. `Settings.write_text` refuses anything else and refuses the deck folder outright.
- Do not write the deck's content. Not prose, not plates, not results. Changing what a page says is a person's
  job, made in the deck, and then rebuilt.
- Do not push past a failed gate, and do not raise `--tolerance` or add a `known_residuals` entry to get a page
  through. A residual is recorded only when it is understood and written down.
- Do not invent Canva ids. An unmapped asset is a placeholder or a stop, never a guess.

## References

- `references/how-it-works.md` - the stages, the cascade subset, the four rewrites, what crosses and what does not.
- `references/push-loop.md` - the per-page push, chunking, element ids, and recovering from a failed transaction.
- `references/canva-connector.md` - Canva's public MCP tools, the dialects, the probe, and the import-from-URL route.
- `references/config.md` - every config key, the discovery order, and how to adopt this skill in another repository.
