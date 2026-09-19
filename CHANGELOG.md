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

## [0.1.0] - 2026-09-19

### Added

- Folio design system: twelve-page A3 deck, binder spine, swing tag, product labels and mount scaffold as
  `.dc.html` design components with print-true stylesheets.
- `scripts/preview.ps1` static preview and print-proof builder.
- Canva pipeline under `scripts/canva/`: flatten, verify, extract, ops and check, driven by
  `design-system/canva.config.json`.
- Placeholder plate generator and `design-system/assets/plates.json` image manifest.
- Repo docs: NESA folio requirements, brand kit, print specifications, production items, Canva pipeline,
  self-assessment method.

### Removed

- Everything from the private predecessor project: the original garment, its photographs, drawings and pattern
  pieces, the real student number, commercial sewing patterns, other students' folios and NESA exam PDFs.
- Tooling config copied from an unrelated Astro site (pnpm, Biome, Vitest, Playwright, Azure).
