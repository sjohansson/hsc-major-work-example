# HSC Textiles Major Work Example

A fully fictional example of a Year 12 HSC Textiles and Design major work folio, built as a design system so
the deliverable can be previewed, printed at true size, pushed to Canva, and checked against the NESA marking
criteria while it is being written.

## Why this exists

This came about after watching several Year 12 cohorts work through their major projects. Working day to day
with AI solution design, I was curious whether one could build something that mimics the NESA markers while the
student is still working on the deliverables.

The point is not to present a dress, or any real HSC submission. It is to design a system that gives continuous
feedback on the folio, making sure it covers everything the marking guidelines expect, and to see how far
software design patterns carry when applied to a written portfolio unit of work.

Nobody has submitted anything based on this repo. Everything in it is invented: the student, the school, the
student number, the garment, the sources, the experiments and the results.

## Design brief

The folio documents the design and making of a school dance dress in the spirit of the one worn by Wednesday
Addams at the Rave'N dance in the Netflix series *Wednesday* (season 1). The portfolio covers that one dress
only, no other garments or accessories.

Every design artefact must hold to the Addams aesthetic: a 1900s to 1950s look and feel, with selected plates
presented in black and white, in the manner of the original 1960s television series.

Public references, for inspiration only. No stills or press photographs are stored in this repo.

- <https://www.netflix.com/tudum/videos/wednesday-dance-scene-jenna-ortega-video>
- <https://www.netflix.com/tudum/videos/jenna-ortega-ranks-her-gloriously-gothic-wednesday-outfits>

## What is in the repo

| Folder | Holds |
| --- | --- |
| `design-system/` | The twelve-page A3 folio deck and the four production items (binder spine, swing tag, product labels, mount scaffold) as `.dc.html` design components, their stylesheets, the two runtime files, and the Canva config. |
| `design-system/assets/` | Placeholder plates generated from `plates.json`. Swap in real artwork with the same filenames. |
| `docs/` | NESA marking facts, the folio marking notes, the brand kit, print specifications, the production items, the Canva sync and the agents. |
| `scripts/` | `preview.ps1` (static preview and true-size print proof), `make_placeholder_plates.py`. |
| `.agents/` | The agents and skills, written for any host. `.github/agents/` and `.claude/agents/` hold the Copilot and Claude Code wrappers. See [docs/agents.md](docs/agents.md). |
| `.agents/skills/canva-sync/` | The Canva sync, as a self-contained agent skill. One way: the repo is the source of truth. |
| `build/` | Generated output. Ignored by git. |

## Quick start

```pwsh
pwsh scripts/preview.ps1 -Item folio          # opens the deck in a browser; Ctrl+P prints at 100%
python -m pip install -r requirements.txt
python .agents/skills/canva-sync/scripts/canva_sync.py doctor   # check the setup
python .agents/skills/canva-sync/scripts/canva_sync.py all      # flatten, verify against the deck, extract, summarise
```

See [AGENTS.md](AGENTS.md) for the rules, [docs/print-specifications.md](docs/print-specifications.md) for the
print run, and [docs/canva-sync.md](docs/canva-sync.md) for the Canva round trip.

## Licence

Code, stylesheets and scripts are MIT (see [LICENSE](LICENSE)). The folio prose and generated plates are
released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Names of television programmes and
characters referenced as inspiration belong to their owners.
