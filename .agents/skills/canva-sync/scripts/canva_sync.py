#!/usr/bin/env python3
"""canva-sync entry point. See canva_sync/cli.py for the command list."""

import sys

from canva_sync.cli import main

if __name__ == "__main__":
    sys.exit(main())
