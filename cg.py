#!/usr/bin/env python3
"""
Entry point for ContextGrid CLI.
"""

import sys
from pathlib import Path

# Add src to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src import cli

if __name__ == "__main__":
    sys.exit(cli.main())
