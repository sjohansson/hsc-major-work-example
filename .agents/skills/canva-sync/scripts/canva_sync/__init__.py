"""canva-sync: flatten a deck, verify it pixel for pixel, and push it to Canva one way.

The steps are build, verify, extract, ops, check, plus the guards probe, doctor,
selftest and guard. Nothing here writes to the deck; see config.Settings.write_text.
"""

NAME = "canva-sync"
VERSION = "1.0.0"

# How the docs and generated-file headers spell the entry point. The bundle can
# sit anywhere, so this is the script name rather than a path; SKILL.md carries
# the repository-relative form.
COMMAND = "canva_sync.py"
