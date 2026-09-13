#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import ROOT, load_json, write_json
from validate_data import validate


def validate_bundle(value, label):
    errors = validate(value, load_json(ROOT / "schemas/result.schema.json"))
    if errors:
        raise SystemExit(f"Invalid {label} result bundle: {'; '.join(errors)}")


def index_unique(items, label):
    result = {}
    for item in items:
        key = item["id"]
        if key in result:
            raise SystemExit(f"Duplicate {label} id: {key}")
        result[key] = item
    return result


def checks(case):
    result = {}
    for item in case["behavior_checks"]:
        key = (item["kind"], item["behavior"])
        if key in result:
            raise SystemExit(f"Duplicate behavior check in {case['id']}: {key}")
        result[key] = item
    return result


def score(case):
    items = checks(case)
    must = [item for (kind, _), item in items.items() if kind == "must"]
    must_not = [item for (kind, _), item in items.items() if kind == "must_not"]
    return {
        "required_rate": sum(item["outcome"] == "pass" for item in must) / len(must) if must else 1.0,
        "violations": sum(item["outcome"] == "fail" for item in must_not),
        "inconclusive": sum(item["outcome"] == "inconclusive" for item in items.values()),
        "completed": case["completed"],
        "unnecessary_steps": case.get("unnecessary_steps", 0),
        "critical_failure": case.get("critical_failure", False),
    }


def compare(baseline, candidate):
    validate_bundle(baseline, "baseline")
    validate_bundle(candidate, "candidate")
    if baseline.get("version") != 2 or candidate.get("version") != 2:
        raise SystemExit("Both result bundles must use version 2.")
    if baseline["session_id"] != candidate["session_id"]:
        raise SystemExit("Result bundles belong to different review sessions.")
    if baseline["case_set_digest"] != candidate["case_set_digest"]:
        raise SystemExit("Case-set digests differ; comparison would be invalid.")
    for field in ("runtime", "model", "configuration_digest"):
        if baseline[field] != candidate[field]:
            raise SystemExit(f"{field.replace('_', ' ').title()} differs; comparison would be invalid.")

    old = index_unique(baseline["cases"], "baseline case")
    new = index_unique(candidate["cases"], "candidate case")
    if set(old) != set(new):
        missing = sorted(set(old) - set(new))
        extra = sorted(set(new) - set(old))
        raise SystemExit(f"Case sets differ; missing={missing}, extra={extra}")

    comparisons = []
    for case_id in sorted(old):
        if old[case_id]["case_digest"] != new[case_id]["case_digest"]:
            raise SystemExit(f"Case digest differs for {case_id}.")
        if set(checks(old[case_id])) != set(checks(new[case_id])):
            raise SystemExit(f"Behavior checks differ for {case_id}.")
        before, after = score(old[case_id]), score(new[case_id])
        regressions = []
        improvements = []
        if after["critical_failure"] and not before["critical_failure"]:
            regressions.append("introduced critical failure")
        elif before["critical_failure"] and not after["critical_failure"]:
            improvements.append("resolved critical failure")
        if before["completed"] and not after["completed"]:
            regressions.append("task no longer completed")
        elif not before["completed"] and after["completed"]:
            improvements.append("task now completed")
        if after["inconclusive"] > before["inconclusive"]:
            regressions.append("more inconclusive behavior checks")
        elif after["inconclusive"] < before["inconclusive"]:
            improvements.append("fewer inconclusive behavior checks")
        if after["required_rate"] < before["required_rate"]:
            regressions.append("lower required-behavior rate")
        elif after["required_rate"] > before["required_rate"]:
            improvements.append("higher required-behavior rate")
        if after["violations"] > before["violations"]:
            regressions.append("more forbidden-behavior violations")
        elif after["violations"] < before["violations"]:
            improvements.append("fewer forbidden-behavior violations")
        if after["unnecessary_steps"] > before["unnecessary_steps"]:
            regressions.append("more unnecessary steps")
        elif after["unnecessary_steps"] < before["unnecessary_steps"]:
            improvements.append("fewer unnecessary steps")
        comparisons.append({
            "id": case_id,
            "baseline": before,
            "candidate": after,
            "improvements": improvements,
            "regressions": regressions,
            "verdict": "regressed" if regressions else ("improved" if improvements else "equivalent")
        })
    has_regression = any(item["regressions"] for item in comparisons)
    has_inconclusive = any(item["candidate"]["inconclusive"] for item in comparisons)
    has_improvement = any(item["improvements"] for item in comparisons)
    recommendation = "rejected" if has_regression else (
        "inconclusive" if has_inconclusive or not has_improvement else "accepted"
    )
    return {
        "version": 2,
        "session_id": baseline["session_id"],
        "baseline_variant": baseline["variant"],
        "candidate_variant": candidate["variant"],
        "cases": comparisons,
        "candidate_has_regression": has_regression,
        "candidate_has_inconclusive": has_inconclusive,
        "candidate_has_improvement": has_improvement,
        "recommendation": recommendation
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare auditable behavioral result bundles case by case.")
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    write_json(compare(load_json(args.baseline), load_json(args.candidate)))


if __name__ == "__main__":
    main()
