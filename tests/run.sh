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
python3 - "$ROOT" "$TMP_DIR" <<'PY'
import json
import sys
from pathlib import Path

root, temp = map(Path, sys.argv[1:])
manifest = {
    "version": 1,
    "id": "synthetic-system",
    "sources": [
        {"id": "skills", "kind": "runtime-skills", "path": str(root / "tests/fixtures/subject"), "include": ["alpha/SKILL.md"]},
        {"id": "prefer", "kind": "preference", "path": str(root / "tests/fixtures/prefer.md")},
        {"id": "methodology", "kind": "human-methodology", "path": str(root / "tests/fixtures/methodology.md")},
        {"id": "prompts", "kind": "prompt-library", "path": str(root / "tests/fixtures/prompts.md")},
        {"id": "optional-context", "kind": "context-provider", "path": str(temp / "missing"), "required": False}
    ]
}
(temp / "subject.json").write_text(json.dumps(manifest))
PY
python3 "$ROOT/scripts/validate_data.py" "$TMP_DIR/subject.json" "$ROOT/schemas/subject.schema.json"
python3 "$ROOT/scripts/import_manifest.py" "$TMP_DIR/subject.json" --destination "$TMP_DIR/composite"
python3 "$ROOT/scripts/inventory.py" "$TMP_DIR/composite" > "$TMP_DIR/composite-inventory.json"
python3 "$ROOT/scripts/validate_data.py" "$ROOT/benchmark/cases" "$ROOT/schemas/case.schema.json"
python3 - "$TMP_DIR" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
inventory = json.loads((root / "inventory.json").read_text())
assert inventory["skill_count"] == 2
assert inventory["skills"][0]["name"] == "alpha"

composite = json.loads((root / "composite-inventory.json").read_text())
assert composite["source_count"] == 5
assert composite["skill_count"] == 1
assert composite["skills"][0]["name"] == "alpha"
assert composite["instruction_document_count"] == 3
assert {item["source_kind"] for item in composite["instruction_documents"]} == {"preference", "human-methodology", "prompt-library"}

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
(root / "component-review.json").write_text(json.dumps({
    "id": "alpha",
    "source": "alpha/SKILL.md",
    "claimed_purpose": "Improve a synthetic task behavior",
    "representative_scenes": ["synthetic case"],
    "expected_behavior_delta": "Produce the required synthetic behavior",
    "costs": ["additional instruction context"],
    "evidence": [],
    "verdict": "unproven",
    "reason": "No behavioral comparison has run yet",
    "interaction_review_ready": False
}))
(root / "quick-gate.json").write_text(json.dumps({
    "id": "alpha",
    "source": "alpha/SKILL.md",
    "core_user_value": "Provide one observable synthetic outcome",
    "value_evidence": [],
    "standalone_reason": "It may require a distinct trigger, but evidence is not available yet",
    "verdict": "needs-evidence",
    "next_action": "Run the smallest no-component versus component comparison"
}))
(root / "baseline.json").write_text(json.dumps(baseline))
(root / "candidate.json").write_text(json.dumps(candidate))
PY
python3 "$ROOT/scripts/validate_data.py" "$TMP_DIR/quick-gate.json" "$ROOT/schemas/quick-gate.schema.json"
python3 "$ROOT/scripts/validate_data.py" "$TMP_DIR/component-review.json" "$ROOT/schemas/component-review.schema.json"
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
