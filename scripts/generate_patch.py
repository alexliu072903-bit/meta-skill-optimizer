#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
from pathlib import Path

from common import file_digest


def files(root: Path):
    return {path.relative_to(root): path for path in root.rglob("*") if path.is_file()}


def is_binary(path: Path | None) -> bool:
    if path is None:
        return False
    sample = path.read_bytes()[:8192]
    if b"\0" in sample:
        return True
    try:
        sample.decode("utf-8")
    except UnicodeDecodeError:
        return True
    return False


def text(path: Path | None) -> list[str]:
    if path is None:
        return []
    return path.read_text(encoding="utf-8").splitlines(keepends=True)


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
        old_path, new_path = old.get(relative), new.get(relative)
        if is_binary(old_path) or is_binary(new_path):
            changed = old_path is None or new_path is None or file_digest(old_path) != file_digest(new_path)
            if changed:
                print(f"Binary files baseline/{relative} and candidate/{relative} differ")
            continue
        diff = difflib.unified_diff(
            text(old_path), text(new_path),
            fromfile=f"baseline/{relative}", tofile=f"candidate/{relative}"
        )
        print("".join(diff), end="")


if __name__ == "__main__":
    main()
