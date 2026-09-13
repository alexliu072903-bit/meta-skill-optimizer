#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

from common import WORKSPACE, load_json, require_empty_or_missing
from import_subject import IGNORED_NAMES


KINDS = {
    "runtime-skills", "preference", "project-instructions",
    "context-provider", "human-methodology", "prompt-library", "other"
}
ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def resolve_path(value: str, manifest_path: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = manifest_path.parent / path
    return path.resolve()


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def matches(path: Path, patterns: list[str]) -> bool:
    value = path.as_posix()
    return any(
        path.match(pattern)
        or (pattern.startswith("**/") and path.match(pattern[3:]))
        or value == pattern
        for pattern in patterns
    )


def excluded(path: Path) -> bool:
    return any(part in IGNORED_NAMES for part in path.parts) or path.name.endswith(".pyc")


def copy_source(source: Path, target: Path, includes: list[str], excludes: list[str]) -> None:
    if source.is_symlink():
        raise SystemExit(f"Refusing to import symbolic link: {source}")
    if source.is_file():
        relative = Path(source.name)
        if includes and not matches(relative, includes):
            return
        if excludes and matches(relative, excludes):
            return
        target.mkdir(parents=True)
        shutil.copy2(source, target / source.name)
        return
    target.mkdir(parents=True)
    for path in sorted(source.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(source)
        if excluded(relative):
            continue
        if includes and not matches(relative, includes):
            continue
        if excludes and matches(relative, excludes):
            continue
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)


def main() -> None:
    parser = argparse.ArgumentParser(description="Import a multi-source Agent system into an isolated baseline.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--destination", type=Path, default=WORKSPACE / "baseline")
    args = parser.parse_args()

    manifest_path = args.manifest.expanduser().resolve()
    manifest = load_json(manifest_path)
    if manifest.get("version") != 1:
        raise SystemExit("Subject manifest version must be 1.")
    if not ID.fullmatch(str(manifest.get("id", ""))):
        raise SystemExit("Subject id must use lowercase letters, digits, and hyphens.")
    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources:
        raise SystemExit("Subject manifest must contain at least one source.")

    seen: set[str] = set()
    resolved = []
    for item in sources:
        source_id = str(item.get("id", ""))
        kind = item.get("kind")
        if not ID.fullmatch(source_id):
            raise SystemExit(f"Invalid source id: {source_id}")
        if source_id in seen:
            raise SystemExit(f"Duplicate source id: {source_id}")
        seen.add(source_id)
        if kind not in KINDS:
            raise SystemExit(f"Invalid source kind for {source_id}: {kind}")
        source = resolve_path(str(item.get("path", "")), manifest_path)
        required = item.get("required", True)
        if not source.exists() and required:
            raise SystemExit(f"Missing required source: {source}")
        if source.exists() and not (source.is_file() or source.is_dir()):
            raise SystemExit(f"Unsupported source type: {source}")
        resolved.append((item, source, required))

    destination = args.destination.expanduser().resolve()
    require_empty_or_missing(destination)
    sources_root = destination / "sources"
    sources_root.mkdir(parents=True)
    locked_sources = []
    for item, source, required in resolved:
        source_id = item["id"]
        record = {
            "id": source_id,
            "kind": item["kind"],
            "declared_path": item["path"],
            "resolved_path": str(source),
            "required": required,
            "present": source.exists(),
            "description": item.get("description", ""),
            "include": item.get("include", []),
            "exclude": item.get("exclude", []),
            "files": []
        }
        if source.exists():
            target = sources_root / source_id
            copy_source(source, target, record["include"], record["exclude"])
            for path in sorted(target.rglob("*")):
                if path.is_file() and not path.is_symlink():
                    record["files"].append({
                        "path": str(path.relative_to(target)),
                        "bytes": path.stat().st_size,
                        "sha256": digest(path)
                    })
        record["file_count"] = len(record["files"])
        locked_sources.append(record)

    lock = {"version": 1, "subject_id": manifest["id"], "sources": locked_sources}
    (destination / "subject.lock.json").write_text(
        json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Imported composite baseline: {destination}")
    for source in locked_sources:
        state = f"{source['file_count']} files" if source["present"] else "missing optional"
        print(f"  {source['id']} ({source['kind']}): {state}")


if __name__ == "__main__":
    main()
