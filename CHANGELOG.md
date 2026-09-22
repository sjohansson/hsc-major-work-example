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

- The Canva pipeline is now a self-contained agent skill at `.agents/skills/canva-sync/`, configured by a
  `canva.config.json` it discovers rather than by fixed relative paths, so the same folder can be copied into
  another repository unchanged. **Breaking:** `scripts/canva.py` is gone; the entry point is
  `python .agents/skills/canva-sync/scripts/canva_sync.py <command>`. `canva.config.json` and
  `canva.local.json` moved to the repository root.

### Added

- `canva-sync` agent skill with `SKILL.md`, four reference documents, a JSON schema for the config, connector
  dialect files and a one-page fixture deck.
- Agents for both hosts: `.github/agents/canva-sync.agent.md` for GitHub Copilot and
  `.claude/agents/canva-sync.md` for Claude Code. Neither can edit a file in this repository.
- `doctor`, which checks everything the pipeline needs and names what is missing; `selftest`, which runs the
  whole pipeline over the fixture deck and proves nothing outside the output folder was written; `guard`, a
  PreToolUse hook that denies a write aimed outside the output folder.
- Connector dialects, so the operation vocabulary is a data file rather than code, and `probe`, which checks a
  connector's tool list against the configured dialect before anything is pushed.
- CI installs the Canva dependencies and runs `doctor` and `selftest` against the fixture deck.

### Removed

- **Breaking:** the `ornament` config key and the two-shape fallback it drew for an unmapped house mark. The
  mark it drew was a design revision out of date. An unmapped mark is now an ordinary placeholder rectangle.

### Fixed

- A `::before` or `::after` carrying `content` text lost that text in the flattened export, and the element
  materialised as a `div` inside a `<p>`, which closed the paragraph and moved every line below it down the
  page. The text is now read back, CSS escapes and all, and materialised as a `span`.
- The masthead field was drawn at a fixed 122 mm when the area block had no explicit width. It now spans the
  block whatever the page geometry.
- The stylesheet path, the page ground colour, the pattern tone and the assets folder were hard-coded in the
  flattener. All four come from the config.

## [0.1.0] - 2025-07-01
