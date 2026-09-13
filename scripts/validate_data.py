#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from common import load_json


def validate(value, schema, location="$") -> list[str]:
    errors: list[str] = []
    if "const" in schema and value != schema["const"]:
        errors.append(f"{location}: value must equal {schema['const']!r}")
    expected = schema.get("type")
    type_map = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool}
    if expected in type_map and not isinstance(value, type_map[expected]):
        return [f"{location}: expected {expected}"]
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{location}: missing required key '{key}'")
        if schema.get("additionalProperties") is False:
            allowed = set(schema.get("properties", {}))
            for key in value:
                if key not in allowed:
                    errors.append(f"{location}: unexpected key '{key}'")
        for key, child in schema.get("properties", {}).items():
            if key in value:
                errors.extend(validate(value[key], child, f"{location}.{key}"))
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{location}: expected at least {schema['minItems']} items")
        child = schema.get("items")
        if child:
            for index, item in enumerate(value):
                errors.extend(validate(item, child, f"{location}[{index}]"))
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{location}: string is too short")
        if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
            errors.append(f"{location}: value does not match required pattern")
    if isinstance(value, int) and not isinstance(value, bool):
        if value < schema.get("minimum", value):
            errors.append(f"{location}: value is below minimum")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{location}: value is not in enum")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate JSON documents against the repository's supported schema subset.")
    parser.add_argument("target", type=Path)
    parser.add_argument("schema", type=Path)
    args = parser.parse_args()
    schema = load_json(args.schema)
    paths = sorted(args.target.glob("*.json")) if args.target.is_dir() else [args.target]
    if not paths:
        raise SystemExit(f"No JSON documents found: {args.target}")
    failed = False
    for path in paths:
        try:
            errors = validate(load_json(path), schema)
        except (OSError, json.JSONDecodeError) as error:
            errors = [str(error)]
        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  {error}")
        else:
            print(f"PASS {path}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
