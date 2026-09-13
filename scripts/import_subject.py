#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from common import WORKSPACE, require_empty_or_missing


IGNORED_NAMES = {
    ".git", ".DS_Store", ".env", "__pycache__", "node_modules",
    "sync.log", "credentials.json", "secrets.json"
}


def ignored(_directory: str, names: list[str]) -> set[str]:
    return {name for name in names if name in IGNORED_NAMES or name.endswith(".pyc")}


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy a Skill system into the ignored baseline workspace.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--destination", type=Path, default=WORKSPACE / "baseline")
    args = parser.parse_args()

    source = args.source.expanduser().resolve()
    destination = args.destination.expanduser().resolve()
    if not source.is_dir():
        raise SystemExit(f"Source is not a directory: {source}")
    if source == destination or source in destination.parents:
        raise SystemExit("Destination must not be the source or a child of the source.")
    require_empty_or_missing(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, ignore=ignored, dirs_exist_ok=False)
    print(f"Imported isolated baseline: {destination}")


if __name__ == "__main__":
    main()

