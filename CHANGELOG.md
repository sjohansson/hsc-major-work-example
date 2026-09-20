# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- Commit prefix to Changelog heading (1:1 mapping)

  feat:        Added        New features
  refactor:    Changed      Changes to existing functionality
  deprecated:  Deprecated   Soon-to-be removed features
  removed:     Removed      Now removed features
  fix:         Fixed        Bug fixes
  security:    Security     Vulnerability fixes
  chore:       (omitted)    Maintenance, tooling, config
  docs:        (omitted)    Documentation-only changes

  Append ! for breaking changes: feat!:, fix!:, removed!: etc. -->

## [Unreleased]

### Changed

- Folio pages 1 to 5 now start from the 2022 dance dress and use the 1905, 1926 and 1955 sources as
  corrections to it. The tiered skirt is a detachable overskirt on a hooked band, so one costume serves the dance
  and the school scene; Experiment 8 tests the band closure. Plates 1 to 4 and 7 renumbered to match.

### Added

- Design notes page (`design-system/meta/design-process.html`) in the preview build: the design process, the type,
  the house mark, rules, plates, and the full colour system as live specimens, with a ledger for later changes.
  The Colour chapter includes token values, derivation, contrast ratios, usage, and four masthead transitions.

### Removed

- Separate colour notes page and `preview.ps1 -Item colour`; all details are in the design notes.

- `design-system/explorations/`. The masthead exploration was a single rejected option and the colour sheet
  carried stale names and no `emph` token; the colour details now sit in the design notes Colour chapter.

## [0.1.0] - 2025-07-01

### Added

- Folio design system: twelve-page A3 deck, binder spine, swing tag, product labels and mount scaffold as
  `.dc.html` design components with print-true stylesheets.
- `scripts/preview.ps1` static preview and print-proof builder.
- Canva pipeline under `scripts/canva/`: flatten, verify, extract, ops and check, driven by
  `design-system/canva.config.json`.
- Placeholder plate generator and `design-system/assets/plates.json` image manifest.
- Repo docs: NESA folio requirements, brand kit, print specifications, production items, Canva pipeline,
  self-assessment method.
