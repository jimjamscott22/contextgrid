"""
ContextGrid - Personal project tracker
Entry point for the CLI application
"""

import sys
from cli import main


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
