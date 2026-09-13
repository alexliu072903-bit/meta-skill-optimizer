#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import load_json, write_json


def index_cases(result):
    return {case["id"]: case for case in result["cases"]}


def score(case):
    return {
        "required_rate": case["must_passed"] / case["must_total"],
        "violations": case["must_not_violations"],
        "completed": case["completed"],
        "unnecessary_steps": case.get("unnecessary_steps", 0),
        "critical_failure": case.get("critical_failure", False),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare behavioral result files case by case.")
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    baseline = load_json(args.baseline)
    candidate = load_json(args.candidate)
    old = index_cases(baseline)
    new = index_cases(candidate)
    shared = sorted(set(old) & set(new))
    if not shared:
        raise SystemExit("No shared case ids to compare.")

    comparisons = []
    for case_id in shared:
        before, after = score(old[case_id]), score(new[case_id])
        regressions = []
        improvements = []
        if after["critical_failure"] and not before["critical_failure"]:
            regressions.append("introduced critical failure")
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
    write_json({
        "baseline_variant": baseline["variant"],
        "candidate_variant": candidate["variant"],
        "cases": comparisons,
        "candidate_has_regression": any(item["regressions"] for item in comparisons)
    })


if __name__ == "__main__":
    main()

