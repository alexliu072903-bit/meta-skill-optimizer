#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/meta-skill-optimizer-test.XXXXXX")"
trap 'rm -rf "$TMP_DIR"' EXIT
export MSO_WORKSPACE="$TMP_DIR/workspace"

python3 "$ROOT/scripts/inventory.py" "$ROOT/tests/fixtures/subject" > "$TMP_DIR/inventory.json"
python3 "$ROOT/scripts/import_subject.py" "$ROOT/tests/fixtures/subject"
python3 "$ROOT/scripts/new_candidate.py" synthetic-change
printf '\nCandidate-only line.\n' >> "$MSO_WORKSPACE/candidates/synthetic-change/alpha/SKILL.md"
python3 "$ROOT/scripts/generate_patch.py" "$MSO_WORKSPACE/baseline" "$MSO_WORKSPACE/candidates/synthetic-change" > "$TMP_DIR/candidate.patch"
test -s "$TMP_DIR/candidate.patch"
python3 "$ROOT/scripts/validate_data.py" "$ROOT/benchmark/cases" "$ROOT/schemas/case.schema.json"
python3 - "$TMP_DIR" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
inventory = json.loads((root / "inventory.json").read_text())
assert inventory["skill_count"] == 2
assert inventory["skills"][0]["name"] == "alpha"

baseline = {
    "variant": "baseline",
    "cases": [{
        "id": "case-1", "must_passed": 1, "must_total": 2,
        "must_not_violations": 1, "completed": True,
        "unnecessary_steps": 2, "observable_contributions": []
    }]
}
candidate = {
    "variant": "candidate",
    "cases": [{
        "id": "case-1", "must_passed": 2, "must_total": 2,
        "must_not_violations": 0, "completed": True,
        "unnecessary_steps": 1, "observable_contributions": ["synthetic"]
    }]
}
(root / "baseline.json").write_text(json.dumps(baseline))
(root / "candidate.json").write_text(json.dumps(candidate))
PY
python3 "$ROOT/scripts/validate_data.py" "$TMP_DIR/baseline.json" "$ROOT/schemas/result.schema.json"
python3 "$ROOT/scripts/validate_data.py" "$TMP_DIR/candidate.json" "$ROOT/schemas/result.schema.json"
python3 "$ROOT/scripts/compare_results.py" "$TMP_DIR/baseline.json" "$TMP_DIR/candidate.json" > "$TMP_DIR/comparison.json"
python3 - "$TMP_DIR/comparison.json" <<'PY'
import json
import sys

result = json.load(open(sys.argv[1]))
assert result["candidate_has_regression"] is False
assert result["cases"][0]["verdict"] == "improved"
PY

echo "All tests passed."
