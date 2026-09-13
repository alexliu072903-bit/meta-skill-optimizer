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
        {"id": "flat-skill", "kind": "runtime-skills", "path": str(root / "tests/fixtures/flat-skill.md")},
        {"id": "invalid-skill", "kind": "runtime-skills", "path": str(root / "tests/fixtures/invalid-skill.md")},
        {"id": "prefer", "kind": "preference", "path": str(root / "tests/fixtures/prefer.md")},
        {"id": "methodology", "kind": "human-methodology", "path": str(root / "tests/fixtures/methodology.md")},
        {"id": "prompts", "kind": "prompt-library", "path": str(root / "tests/fixtures/prompts.md")},
        {"id": "optional-context", "kind": "context-provider", "path": str(temp / "missing"), "required": False}
    ]
}
(temp / "subject.json").write_text(json.dumps(manifest))
(temp / "session-cases").mkdir()
(temp / "session-cases/case.json").write_text(json.dumps({
    "version": 1,
    "id": "session-case",
    "request": "Complete the synthetic task.",
    "must_behaviors": ["Complete the task"],
    "must_not_behaviors": ["Add an unnecessary step"],
    "rationale": "Exercises the review-session lifecycle."
}))
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
assert composite["source_count"] == 7
assert composite["skill_count"] == 2
assert {item["name"] for item in composite["skills"]} == {"alpha", "flat-skill"}
assert composite["instruction_document_count"] == 4
assert {item["source_kind"] for item in composite["instruction_documents"]} == {"runtime-skills", "preference", "human-methodology", "prompt-library"}

baseline = {
    "version": 2, "session_id": "comparison-test", "variant": "baseline",
    "runtime": "synthetic-runner", "model": "synthetic-model", "configuration_digest": "e" * 64,
    "subject_digest": "a" * 64, "case_set_digest": "b" * 64,
    "cases": [{
        "id": "case-1", "case_digest": "c" * 64, "raw_output": "baseline output",
        "behavior_checks": [
            {"behavior": "Complete", "kind": "must", "outcome": "fail", "evidence": "missing"},
            {"behavior": "Do not detour", "kind": "must_not", "outcome": "fail", "evidence": "detour"}
        ],
        "completed": True, "unnecessary_steps": 2, "observable_contributions": []
    }]
}
candidate = {
    "version": 2, "session_id": "comparison-test", "variant": "candidate",
    "runtime": "synthetic-runner", "model": "synthetic-model", "configuration_digest": "e" * 64,
    "subject_digest": "d" * 64, "case_set_digest": "b" * 64,
    "cases": [{
        "id": "case-1", "case_digest": "c" * 64, "raw_output": "candidate output",
        "behavior_checks": [
            {"behavior": "Complete", "kind": "must", "outcome": "pass", "evidence": "present"},
            {"behavior": "Do not detour", "kind": "must_not", "outcome": "pass", "evidence": "absent"}
        ],
        "completed": True, "unnecessary_steps": 1, "observable_contributions": ["synthetic"]
    }]
}
(root / "component-review.json").write_text(json.dumps({
    "version": 1,
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
    "version": 1,
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

# Different execution configurations are not comparable.
python3 - "$TMP_DIR/candidate.json" "$TMP_DIR/different-config.json" <<'PY'
import json, sys
from pathlib import Path
source, target = map(Path, sys.argv[1:])
value = json.loads(source.read_text())
value["configuration_digest"] = "f" * 64
target.write_text(json.dumps(value))
PY
if python3 "$ROOT/scripts/compare_results.py" "$TMP_DIR/baseline.json" "$TMP_DIR/different-config.json" >/dev/null 2>&1; then
  echo 'Expected different execution configurations to be incomparable' >&2
  exit 1
fi

# Binary assets are reported without lossy text decoding.
mkdir -p "$TMP_DIR/binary-old" "$TMP_DIR/binary-new"
printf '\000old' > "$TMP_DIR/binary-old/asset.bin"
printf '\000new' > "$TMP_DIR/binary-new/asset.bin"
python3 "$ROOT/scripts/generate_patch.py" "$TMP_DIR/binary-old" "$TMP_DIR/binary-new" > "$TMP_DIR/binary.patch"
grep -q 'Binary files .* differ' "$TMP_DIR/binary.patch"

# Required sources that select no files fail atomically.
python3 - "$ROOT" "$TMP_DIR" <<'PY'
import json, sys
from pathlib import Path
root, temp = map(Path, sys.argv[1:])
value = {
    "version": 1, "id": "empty-selection",
    "sources": [{
        "id": "empty", "kind": "runtime-skills",
        "path": str(root / "tests/fixtures/subject"),
        "include": ["does-not-exist.*"], "required": True
    }]
}
(temp / "empty-subject.json").write_text(json.dumps(value))
PY
if python3 "$ROOT/scripts/import_manifest.py" "$TMP_DIR/empty-subject.json" --destination "$TMP_DIR/empty-baseline" 2>/dev/null; then
  echo 'Expected empty required import to fail' >&2
  exit 1
fi
test ! -e "$TMP_DIR/empty-baseline"

# Full review-session lifecycle: init → candidate → seal → plan → runs → decision.
python3 "$ROOT/scripts/review_session.py" init review-test --manifest "$TMP_DIR/subject.json" --cases "$TMP_DIR/session-cases"
python3 "$ROOT/scripts/review_session.py" candidate review-test candidate-one
printf '\nCandidate change.\n' >> "$MSO_WORKSPACE/sessions/review-test/candidates/candidate-one/sources/skills/alpha/SKILL.md"
python3 "$ROOT/scripts/review_session.py" seal-candidate review-test candidate-one
python3 "$ROOT/scripts/review_session.py" plan review-test > "$TMP_DIR/run-plan.json"
python3 "$ROOT/scripts/validate_data.py" "$MSO_WORKSPACE/sessions/review-test/session.json" "$ROOT/schemas/session.schema.json"
python3 - "$TMP_DIR/run-plan.json" "$TMP_DIR" <<'PY'
import json, sys
from collections import defaultdict
from pathlib import Path
plan_path, temp = Path(sys.argv[1]), Path(sys.argv[2])
plan = json.loads(plan_path.read_text())
groups = defaultdict(list)
for task in plan["tasks"]:
    groups[task["variant"]].append(task)
for variant, tasks in groups.items():
    cases = []
    for task in tasks:
        outcome = "pass" if variant != "baseline" else "fail"
        cases.append({
            "id": task["case_id"], "case_digest": task["case_digest"],
            "raw_output": f"{variant} raw output",
            "behavior_checks": [
                {"behavior": "Complete the task", "kind": "must", "outcome": outcome, "evidence": "synthetic evidence"},
                {"behavior": "Add an unnecessary step", "kind": "must_not", "outcome": "pass", "evidence": "not observed"}
            ],
            "completed": True, "unnecessary_steps": 0,
            "observable_contributions": []
        })
    result = {
        "version": 2, "session_id": plan["session_id"], "variant": variant,
        "runtime": "synthetic-runner", "model": "synthetic-model", "configuration_digest": "e" * 64,
        "subject_digest": tasks[0]["subject_digest"],
        "case_set_digest": plan["case_set_digest"], "cases": cases
    }
    (temp / f"session-{variant}.json").write_text(json.dumps(result))
PY
python3 "$ROOT/scripts/review_session.py" register-run review-test "$TMP_DIR/session-baseline.json"
python3 "$ROOT/scripts/review_session.py" register-run review-test "$TMP_DIR/session-candidate-one.json"
python3 "$ROOT/scripts/review_session.py" compare review-test --candidate candidate-one > "$TMP_DIR/session-comparison.json"
python3 "$ROOT/scripts/validate_data.py" "$TMP_DIR/session-comparison.json" "$ROOT/schemas/comparison.schema.json"
python3 "$ROOT/scripts/review_session.py" decide review-test --candidate candidate-one --verdict accepted --reason 'Synthetic candidate improved the required behavior.'
python3 "$ROOT/scripts/validate_data.py" "$MSO_WORKSPACE/sessions/review-test/session.json" "$ROOT/schemas/session.schema.json"
python3 "$ROOT/scripts/validate_data.py" "$MSO_WORKSPACE/sessions/review-test/feedback/decision.json" "$ROOT/schemas/feedback.schema.json"

# Missing cases cannot be silently compared.
python3 - "$TMP_DIR/session-candidate-one.json" "$TMP_DIR/missing-case.json" <<'PY'
import json, sys
from pathlib import Path
source, target = map(Path, sys.argv[1:])
value = json.loads(source.read_text())
value["cases"] = []
target.write_text(json.dumps(value))
PY
if python3 "$ROOT/scripts/compare_results.py" "$TMP_DIR/session-baseline.json" "$TMP_DIR/missing-case.json" >/dev/null 2>&1; then
  echo 'Expected comparison with a missing Case to fail' >&2
  exit 1
fi

# Baselines and sealed candidates are immutable within a session.
python3 "$ROOT/scripts/review_session.py" init mutation-test --manifest "$TMP_DIR/subject.json" --cases "$TMP_DIR/session-cases"
printf '\nMutation.\n' >> "$MSO_WORKSPACE/sessions/mutation-test/baseline/sources/skills/alpha/SKILL.md"
if python3 "$ROOT/scripts/review_session.py" candidate mutation-test blocked >/dev/null 2>&1; then
  echo 'Expected a mutated baseline to stop the session' >&2
  exit 1
fi
python3 "$ROOT/scripts/review_session.py" init sealed-test --manifest "$TMP_DIR/subject.json" --cases "$TMP_DIR/session-cases"
python3 "$ROOT/scripts/review_session.py" candidate sealed-test sealed-one
python3 "$ROOT/scripts/review_session.py" seal-candidate sealed-test sealed-one
printf '\nMutation.\n' >> "$MSO_WORKSPACE/sessions/sealed-test/candidates/sealed-one/sources/skills/alpha/SKILL.md"
if python3 "$ROOT/scripts/review_session.py" plan sealed-test >/dev/null 2>&1; then
  echo 'Expected a mutated sealed candidate to stop planning' >&2
  exit 1
fi

# Decisions cannot bypass comparisons, and accepting a regression requires an explicit override.
python3 "$ROOT/scripts/review_session.py" init regression-test --manifest "$TMP_DIR/subject.json" --cases "$TMP_DIR/session-cases"
python3 "$ROOT/scripts/review_session.py" candidate regression-test worse-one
python3 "$ROOT/scripts/review_session.py" seal-candidate regression-test worse-one
python3 "$ROOT/scripts/review_session.py" plan regression-test > "$TMP_DIR/regression-plan.json"
python3 - "$TMP_DIR/regression-plan.json" "$TMP_DIR" <<'PY'
import json, sys
from collections import defaultdict
from pathlib import Path
plan, temp = json.loads(Path(sys.argv[1]).read_text()), Path(sys.argv[2])
groups = defaultdict(list)
for task in plan["tasks"]:
    groups[task["variant"]].append(task)
for variant, tasks in groups.items():
    outcome = "pass" if variant == "baseline" else "fail"
    cases = [{
        "id": task["case_id"], "case_digest": task["case_digest"],
        "raw_output": f"{variant} output", "completed": outcome == "pass",
        "behavior_checks": [
            {"behavior": "Complete the task", "kind": "must", "outcome": outcome, "evidence": "synthetic evidence"},
            {"behavior": "Add an unnecessary step", "kind": "must_not", "outcome": "pass", "evidence": "not observed"}
        ]
    } for task in tasks]
    value = {
        "version": 2, "session_id": plan["session_id"], "variant": variant,
        "subject_digest": tasks[0]["subject_digest"], "case_set_digest": plan["case_set_digest"],
        "runtime": "synthetic-runner", "model": "synthetic-model", "configuration_digest": "e" * 64, "cases": cases
    }
    (temp / f"regression-{variant}.json").write_text(json.dumps(value))
PY
python3 "$ROOT/scripts/review_session.py" register-run regression-test "$TMP_DIR/regression-baseline.json"
python3 "$ROOT/scripts/review_session.py" register-run regression-test "$TMP_DIR/regression-worse-one.json"
if python3 "$ROOT/scripts/review_session.py" decide regression-test --candidate worse-one --verdict accepted --reason 'No comparison.' >/dev/null 2>&1; then
  echo 'Expected a decision without a registered comparison to fail' >&2
  exit 1
fi
python3 "$ROOT/scripts/review_session.py" compare regression-test --candidate worse-one >/dev/null
if python3 "$ROOT/scripts/review_session.py" decide regression-test --candidate worse-one --verdict accepted --reason 'Silent regression.' >/dev/null 2>&1; then
  echo 'Expected acceptance of a regression without override to fail' >&2
  exit 1
fi
python3 "$ROOT/scripts/review_session.py" decide regression-test --candidate worse-one --verdict accepted --override-comparison --reason 'Deliberate trade-off.'

# Registered Result artifacts remain immutable through comparison and decision.
cp "$MSO_WORKSPACE/sessions/review-test/runs/candidate-one.json" "$TMP_DIR/registered-run-backup.json"
printf ' ' >> "$MSO_WORKSPACE/sessions/review-test/runs/candidate-one.json"
if python3 "$ROOT/scripts/review_session.py" compare review-test --candidate candidate-one >/dev/null 2>&1; then
  echo 'Expected a changed registered Result to stop the session' >&2
  exit 1
fi
mv "$TMP_DIR/registered-run-backup.json" "$MSO_WORKSPACE/sessions/review-test/runs/candidate-one.json"

echo "All tests passed."
