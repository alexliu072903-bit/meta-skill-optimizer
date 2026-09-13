#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
from pathlib import Path


def files(root: Path):
    return {path.relative_to(root): path for path in root.rglob("*") if path.is_file()}


def text(path: Path | None) -> list[str]:
    if path is None:
        return []
    return path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a reviewable unified diff without modifying the source.")
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    baseline = args.baseline.resolve()
    candidate = args.candidate.resolve()
    if not baseline.is_dir() or not candidate.is_dir():
        raise SystemExit("Both baseline and candidate must be directories.")
    old, new = files(baseline), files(candidate)
    for relative in sorted(set(old) | set(new)):
        diff = difflib.unified_diff(
            text(old.get(relative)), text(new.get(relative)),
            fromfile=f"baseline/{relative}", tofile=f"candidate/{relative}"
        )
        print("".join(diff), end="")


if __name__ == "__main__":
    main()

