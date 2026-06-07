#!/usr/bin/env python3
"""Bootstrap entry point — adds project root to path, then delegates to src.main."""
import sys
from pathlib import Path

_proj_root = Path(__file__).resolve().parent
if str(_proj_root) not in sys.path:
    sys.path.insert(0, str(_proj_root))


def main():
    from src.main import main as _main
    _main()


if __name__ == "__main__":
    main()
