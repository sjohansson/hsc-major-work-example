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
python -m compileall -q scripts .agents/skills/canva-sync/scripts .agents/skills/get-nesa-grading-rules/scripts
python -m unittest discover -s scripts -p "test_agent_guards.py"
python scripts/docs_to_wiki.py
python .agents/skills/canva-sync/scripts/canva_sync.py selftest
pwsh scripts/preview.ps1 -Item all -NoOpen
python scripts/print_pdfs.py
python .agents/skills/canva-sync/scripts/canva_sync.py build --verify
```

CI runs the first six. The last three are the visual proof and take a minute; the `Print` workflow runs
`print_pdfs.py` on `main`. The agent guard tests exercise
the Codex hook commands and their file boundaries. `docs_to_wiki.py` builds the wiki pages into `build/wiki/`
and fails on a link in `docs/` that points at nothing. `selftest` runs the whole
Canva pipeline over a one-page fixture deck, so run it after any change under
`.agents/skills/canva-sync/`.

## Commits

Use the Conventional Commits prefixes in
[.github/copilot-commit-message-instructions.md](.github/copilot-commit-message-instructions.md). Keep commits
focused and describe the why in the body.

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
