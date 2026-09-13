from __future__ import annotations

import argparse
from pathlib import Path

from .save import RTW3Save
from .version import __version__


def main() -> int:
    parser = argparse.ArgumentParser(prog="privateer", description="Rule the Waves 3 save editor")
    parser.add_argument("--version", action="version", version=f"Privateer {__version__}")
    parser.add_argument("folder", nargs="?", type=Path)
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if args.folder:
        save = RTW3Save.load(args.folder)
        print(save.validate())
        return 0 if save.validate().valid else 1
    from .gui import launch
    launch()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
