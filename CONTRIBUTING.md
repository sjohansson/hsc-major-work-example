# Contributing

## Ground rules

- Everything in this repo is fictional. Do not add a real student name, student number, school, teacher, or a
  photograph of a real person.
- Do not add third-party material: commercial sewing patterns, screen stills, magazine scans, exam papers or
  other students' work. Link to public sources instead.
- Follow the writing and typography rules in [AGENTS.md](AGENTS.md).

## Setup

```pwsh
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Chrome or Edge must be on `PATH`, or set `CHROME_PATH`, for the Canva pipeline. The preview script only needs a
browser.

## Before opening a pull request

```pwsh
npx markdownlint-cli2 "**/*.md"
npx -p cspell -p @cspell/dict-en-au cspell --no-progress "**/*.md"
python -m compileall -q scripts
pwsh scripts/preview.ps1 -Item all -NoOpen
python .agents/skills/canva-sync/scripts/canva_sync.py build --verify
```

CI runs the first three. The last two are the visual proof and take a minute.

## Commits

Use the Conventional Commits prefixes in
[.github/copilot-commit-message-instructions.md](.github/copilot-commit-message-instructions.md). Keep commits
focused and describe the why in the body.

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
