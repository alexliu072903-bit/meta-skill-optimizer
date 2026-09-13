#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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

    lock_path = subject / "subject.lock.json"
    source_index = {}
    source_records = []
    if lock_path.is_file():
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        source_records = [{
            "id": item["id"], "kind": item["kind"],
            "present": item["present"], "file_count": item["file_count"]
        } for item in lock.get("sources", [])]
        source_index = {item["id"]: item["kind"] for item in lock.get("sources", [])}

    def source_for(path: Path) -> tuple[str, str]:
        relative = path.relative_to(subject)
        parts = relative.parts
        if len(parts) >= 3 and parts[0] == "sources" and parts[1] in source_index:
            return parts[1], source_index[parts[1]]
        return "subject", "runtime-skills"

    skill_paths = set(subject.rglob("SKILL*.md"))
    if source_index:
        for path in subject.rglob("*.md"):
            _source_id, source_kind = source_for(path)
            if source_kind != "runtime-skills":
                continue
            metadata = frontmatter(path.read_text(encoding="utf-8", errors="replace"))
            if metadata.get("name") and metadata.get("description"):
                skill_paths.add(path)

    skills = []
    for path in sorted(skill_paths):
        text = path.read_text(encoding="utf-8", errors="replace")
        metadata = frontmatter(text)
        source_id, source_kind = source_for(path)
        skills.append({
            "path": str(path.relative_to(subject)),
            "source_id": source_id,
            "source_kind": source_kind,
            "name": metadata.get("name", path.stem.lower()),
            "description": metadata.get("description", ""),
            "declared_references": sorted(set(REFERENCE.findall(text))),
            "bytes": path.stat().st_size,
            "lines": text.count("\n") + 1,
        })
    skill_paths = {item["path"] for item in skills}
    documents = []
    for path in sorted(subject.rglob("*.md")):
        relative = str(path.relative_to(subject))
        if relative in skill_paths:
            continue
        source_id, source_kind = source_for(path)
        text = path.read_text(encoding="utf-8", errors="replace")
        documents.append({
            "path": relative,
            "source_id": source_id,
            "source_kind": source_kind,
            "bytes": path.stat().st_size,
            "lines": text.count("\n") + 1,
        })
    write_json({
        "subject": str(subject),
        "source_count": len(source_records) if source_records else 1,
        "sources": source_records,
        "skill_count": len(skills),
        "skills": skills,
        "instruction_document_count": len(documents),
        "instruction_documents": documents
    })


if __name__ == "__main__":
    main()
