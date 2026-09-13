#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

from common import WORKSPACE, require_empty_or_missing


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an isolated candidate from the baseline.")
    parser.add_argument("name")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", args.name):
        raise SystemExit("Candidate name must use lowercase letters, digits, and hyphens.")

    baseline = WORKSPACE / "baseline"
    destination = WORKSPACE / "candidates" / args.name
    if not baseline.is_dir():
        raise SystemExit(f"Missing baseline: {baseline}")
    require_empty_or_missing(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(baseline, destination)
    print(f"Created candidate: {destination}")


if __name__ == "__main__":
    main()

