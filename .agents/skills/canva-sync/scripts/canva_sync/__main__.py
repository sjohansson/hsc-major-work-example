"""Allow `python -m canva_sync` from this scripts folder."""

import sys

from .cli import main

sys.exit(main())
