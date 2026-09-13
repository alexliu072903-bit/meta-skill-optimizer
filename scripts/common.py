#!/usr/bin/env python3
from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = Path(os.environ.get("MSO_WORKSPACE", ROOT / "workspace")).expanduser().resolve()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def require_empty_or_missing(path: Path) -> None:
    if path.exists():
        if not path.is_dir():
            raise SystemExit(f"Expected a directory but found another file type: {path}")
        if any(path.iterdir()):
            raise SystemExit(f"Refusing to overwrite non-empty directory: {path}")


def file_digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def tree_digest(root: Path) -> str:
    value = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file() and not item.is_symlink()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        value.update(len(relative).to_bytes(8, "big"))
        value.update(relative)
        digest = bytes.fromhex(file_digest(path))
        value.update(digest)
    return value.hexdigest()


def write_json_file(path: Path, value: Any) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
