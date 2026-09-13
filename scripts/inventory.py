#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from common import write_json


FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
FIELD = re.compile(r"^([a-zA-Z0-9_-]+):\s*(.*)$")
REFERENCE = re.compile(r"(?:\$|`)([a-z][a-z0-9-]{1,63})(?:`)?")


def frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER.search(text)
    if not match:
        return {}
    result: dict[str, str] = {}
    current = None
    for line in match.group(1).splitlines():
        field = FIELD.match(line)
        if field:
            current, value = field.groups()
            result[current] = value.strip().strip('"\'')
        elif current and line.startswith((" ", "\t")):
            result[current] = f"{result[current]} {line.strip()}".strip()
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Inventory Skill entrypoints without executing subject instructions.")
    parser.add_argument("subject", type=Path)
    args = parser.parse_args()
    subject = args.subject.expanduser().resolve()
    if not subject.is_dir():
        raise SystemExit(f"Subject is not a directory: {subject}")

    skills = []
    for path in sorted(subject.rglob("SKILL*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        metadata = frontmatter(text)
        skills.append({
            "path": str(path.relative_to(subject)),
            "name": metadata.get("name", path.stem.lower()),
            "description": metadata.get("description", ""),
            "declared_references": sorted(set(REFERENCE.findall(text))),
            "bytes": path.stat().st_size,
            "lines": text.count("\n") + 1,
        })
    write_json({"subject": str(subject), "skill_count": len(skills), "skills": skills})


if __name__ == "__main__":
    main()

