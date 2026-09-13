#!/usr/bin/env python3
from __future__ import annotations

import json
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
    if path.exists() and any(path.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty directory: {path}")
