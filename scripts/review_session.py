#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
from pathlib import Path

from common import ROOT, WORKSPACE, file_digest, load_json, tree_digest, write_json, write_json_file
from compare_results import compare
from import_manifest import import_manifest
from validate_data import validate


ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def ensure_schema(value: dict, schema_name: str) -> None:
    errors = validate(value, load_json(ROOT / "schemas" / schema_name))
    if errors:
        raise SystemExit(f"Schema validation failed: {'; '.join(errors)}")


def session_dir(session_id: str) -> Path:
    if not ID.fullmatch(session_id):
        raise SystemExit("Session id must use lowercase letters, digits, and hyphens.")
    return WORKSPACE / "sessions" / session_id


def load_session(session_id: str) -> tuple[Path, dict]:
    root = session_dir(session_id)
    path = root / "session.json"
    if not path.is_file():
        raise SystemExit(f"Review session not found: {session_id}")
    return root, load_json(path)


def case_records(case_root: Path) -> list[dict]:
    records = []
    seen = set()
    for path in sorted(case_root.glob("*.json")):
        value = load_json(path)
        case_id = value.get("id")
        if not isinstance(case_id, str) or not case_id:
            raise SystemExit(f"Case has no id: {path}")
        if case_id in seen:
            raise SystemExit(f"Duplicate case id: {case_id}")
        seen.add(case_id)
        records.append({"id": case_id, "path": path.name, "digest": file_digest(path)})
    if not records:
        raise SystemExit(f"No case JSON files found: {case_root}")
    return records


def checks_for_result(case: dict) -> dict:
    result = {}
    for item in case.get("behavior_checks", []):
        key = (item.get("kind"), item.get("behavior"))
        if key in result:
            raise SystemExit(f"Duplicate behavior check in result case {case.get('id')}: {key}")
        result[key] = item
    return result


def verify_artifacts(root: Path, session: dict) -> None:
    file_artifacts = [session["manifest"], *session.get("runs", []), *session.get("comparisons", [])]
    if session.get("decision"):
        file_artifacts.append(session["decision"])
    for artifact in file_artifacts:
        path = root / artifact["path"]
        if not path.is_file() or file_digest(path) != artifact["digest"]:
            raise SystemExit(f"Registered artifact changed or is missing: {artifact['path']}")
    tree_artifacts = [session["case_set"], session["baseline"]]
    tree_artifacts.extend(item for item in session["candidates"] if item.get("status") == "sealed")
    for artifact in tree_artifacts:
        path = root / artifact["path"]
        if not path.is_dir() or tree_digest(path) != artifact["digest"]:
            raise SystemExit(f"Registered artifact changed or is missing: {artifact['path']}")


def initialize(args) -> None:
    target = session_dir(args.id)
    if target.exists():
        raise SystemExit(f"Review session already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{args.id}-", dir=target.parent))
    try:
        case_target = temporary / "cases"
        shutil.copytree(args.cases.expanduser().resolve(), case_target)
        records = case_records(case_target)
        manifest_target = temporary / "subject.json"
        shutil.copy2(args.manifest.expanduser().resolve(), manifest_target)
        baseline = temporary / "baseline"
        import_manifest(args.manifest, baseline)
        session = {
            "version": 2,
            "id": args.id,
            "status": "imported",
            "manifest": {"path": "subject.json", "digest": file_digest(manifest_target)},
            "case_set": {
                "path": "cases",
                "digest": tree_digest(case_target),
                "case_ids": [item["id"] for item in records]
            },
            "baseline": {"path": "baseline", "digest": tree_digest(baseline)},
            "candidates": [],
            "runs": [],
            "comparisons": []
        }
        ensure_schema(session, "session.schema.json")
        write_json_file(temporary / "session.json", session)
        temporary.rename(target)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    print(f"Created review session: {target}")


def create_candidate(args) -> None:
    root, session = load_session(args.id)
    verify_artifacts(root, session)
    if not ID.fullmatch(args.name):
        raise SystemExit("Candidate name must use lowercase letters, digits, and hyphens.")
    if any(item["name"] == args.name for item in session["candidates"]):
        raise SystemExit(f"Candidate already exists: {args.name}")
    destination = root / "candidates" / args.name
    destination.parent.mkdir(exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{args.name}-", dir=destination.parent))
    shutil.rmtree(temporary)
    try:
        shutil.copytree(root / session["baseline"]["path"], temporary)
        temporary.rename(destination)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    session["candidates"].append({
        "name": args.name,
        "path": f"candidates/{args.name}",
        "digest": tree_digest(destination),
        "status": "draft"
    })
    session["status"] = "candidate-ready"
    ensure_schema(session, "session.schema.json")
    write_json_file(root / "session.json", session)
    print(f"Created session candidate: {destination}")


def seal_candidate(args) -> None:
    root, session = load_session(args.id)
    verify_artifacts(root, session)
    candidate = next((item for item in session["candidates"] if item["name"] == args.name), None)
    if not candidate:
        raise SystemExit(f"Unknown candidate: {args.name}")
    if candidate.get("status") == "sealed":
        raise SystemExit(f"Candidate is already sealed: {args.name}")
    candidate["digest"] = tree_digest(root / candidate["path"])
    candidate["status"] = "sealed"
    session["status"] = "candidate-ready"
    ensure_schema(session, "session.schema.json")
    write_json_file(root / "session.json", session)
    print(f"Sealed candidate: {args.name} ({candidate['digest']})")


def build_plan(args) -> None:
    root, session = load_session(args.id)
    verify_artifacts(root, session)
    variants = [{"name": "baseline", **session["baseline"]}] + [
        item for item in session["candidates"] if item.get("status") == "sealed"
    ]
    if args.variant:
        variants = [item for item in variants if item["name"] == args.variant]
        if not variants:
            raise SystemExit(f"Unknown variant: {args.variant}")
    cases = case_records(root / session["case_set"]["path"])
    tasks = []
    for variant in variants:
        variant_path = root / variant["path"]
        actual_digest = tree_digest(variant_path)
        if actual_digest != variant["digest"]:
            raise SystemExit(f"Variant digest changed since registration: {variant['name']}")
        for case in cases:
            tasks.append({
                "session_id": session["id"],
                "variant": variant["name"],
                "subject_path": str(variant_path),
                "subject_digest": variant["digest"],
                "case_path": str(root / session["case_set"]["path"] / case["path"]),
                "case_id": case["id"],
                "case_digest": case["digest"]
            })
    write_json({
        "version": 1,
        "session_id": session["id"],
        "case_set_digest": session["case_set"]["digest"],
        "tasks": tasks
    })


def register_run(args) -> None:
    root, session = load_session(args.id)
    verify_artifacts(root, session)
    result = load_json(args.result)
    ensure_schema(result, "result.schema.json")
    if result.get("version") != 2 or result.get("session_id") != session["id"]:
        raise SystemExit("Result version or session id does not match.")
    if result.get("case_set_digest") != session["case_set"]["digest"]:
        raise SystemExit("Result case-set digest does not match the session.")
    variants = {"baseline": session["baseline"]}
    variants.update({item["name"]: item for item in session["candidates"]})
    variant = variants.get(result.get("variant"))
    if not variant:
        raise SystemExit(f"Unknown result variant: {result.get('variant')}")
    if result.get("variant") != "baseline" and variant.get("status") != "sealed":
        raise SystemExit("A Candidate must be sealed before its run can be registered.")
    if result.get("subject_digest") != variant["digest"]:
        raise SystemExit("Result subject digest does not match the registered variant.")
    expected_cases = case_records(root / session["case_set"]["path"])
    expected = {item["id"]: item["digest"] for item in expected_cases}
    expected_behaviors = {}
    for item in expected_cases:
        case = load_json(root / session["case_set"]["path"] / item["path"])
        expected_behaviors[item["id"]] = {
            ("must", behavior) for behavior in case["must_behaviors"]
        } | {
            ("must_not", behavior) for behavior in case["must_not_behaviors"]
        }
    actual = {}
    for item in result.get("cases", []):
        if item["id"] in actual:
            raise SystemExit(f"Duplicate result case id: {item['id']}")
        actual[item["id"]] = item["case_digest"]
        actual_behaviors = set(checks_for_result(item))
        if actual_behaviors != expected_behaviors.get(item["id"], set()):
            raise SystemExit(f"Behavior checks do not match Case definition: {item['id']}")
    if actual != expected:
        raise SystemExit("Result cases or case digests do not match the session.")
    destination = root / "runs" / f"{result['variant']}.json"
    destination.parent.mkdir(exist_ok=True)
    if destination.exists():
        raise SystemExit(f"Run already registered: {destination}")
    shutil.copy2(args.result, destination)
    session["runs"].append({
        "variant": result["variant"],
        "path": f"runs/{result['variant']}.json",
        "digest": file_digest(destination)
    })
    if "baseline" in {item["variant"] for item in session["runs"]} and len(session["runs"]) >= 2:
        session["status"] = "evaluated"
    ensure_schema(session, "session.schema.json")
    write_json_file(root / "session.json", session)
    print(f"Registered run: {destination}")


def compare_runs(args) -> None:
    root, session = load_session(args.id)
    verify_artifacts(root, session)
    if args.candidate not in {item["name"] for item in session["candidates"]}:
        raise SystemExit(f"Unknown candidate: {args.candidate}")
    runs = {item["variant"]: item for item in session["runs"]}
    missing = {"baseline", args.candidate} - set(runs)
    if missing:
        raise SystemExit(f"Comparison requires registered runs for: {sorted(missing)}")
    result = compare(
        load_json(root / runs["baseline"]["path"]),
        load_json(root / runs[args.candidate]["path"])
    )
    ensure_schema(result, "comparison.schema.json")
    comparison_dir = root / "comparisons"
    comparison_dir.mkdir(exist_ok=True)
    destination = comparison_dir / f"{args.candidate}.json"
    if destination.exists():
        raise SystemExit(f"Comparison already exists: {destination}")
    write_json_file(destination, result)
    session["comparisons"].append({
        "candidate": args.candidate,
        "path": f"comparisons/{args.candidate}.json",
        "digest": file_digest(destination)
    })
    session["status"] = "compared"
    ensure_schema(session, "session.schema.json")
    write_json_file(root / "session.json", session)
    write_json(result)


def decide(args) -> None:
    root, session = load_session(args.id)
    verify_artifacts(root, session)
    if args.candidate not in {item["name"] for item in session["candidates"]}:
        raise SystemExit(f"Unknown candidate: {args.candidate}")
    comparison_record = next(
        (item for item in session["comparisons"] if item["candidate"] == args.candidate), None
    )
    if not comparison_record:
        raise SystemExit("Decision requires a registered comparison for the Candidate.")
    comparison = load_json(root / comparison_record["path"])
    recommendation = comparison["recommendation"]
    if args.verdict == "accepted" and recommendation != "accepted" and not args.override_comparison:
        raise SystemExit(
            f"Comparison recommends {recommendation}; use --override-comparison to accept with an explicit audit record."
        )
    decision = {
        "version": 2,
        "session_id": session["id"],
        "candidate": args.candidate or "",
        "decision": args.verdict,
        "reason": args.reason,
        "case_ids": session["case_set"]["case_ids"],
        "follow_up": args.follow_up or "",
        "comparison": comparison_record["path"],
        "comparison_digest": comparison_record["digest"],
        "comparison_recommendation": recommendation,
        "override_comparison": args.override_comparison
    }
    ensure_schema(decision, "feedback.schema.json")
    feedback_dir = root / "feedback"
    feedback_dir.mkdir(exist_ok=True)
    feedback_path = feedback_dir / "decision.json"
    if feedback_path.exists():
        raise SystemExit("A decision already exists for this session.")
    write_json_file(feedback_path, decision)
    session["decision"] = {"path": "feedback/decision.json", "digest": file_digest(feedback_path)}
    session["status"] = args.verdict
    ensure_schema(session, "session.schema.json")
    write_json_file(root / "session.json", session)
    print(f"Recorded {args.verdict} decision; no source files were modified.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage an auditable Meta-Skill review session.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init")
    init.add_argument("id")
    init.add_argument("--manifest", type=Path, required=True)
    init.add_argument("--cases", type=Path, required=True)
    init.set_defaults(run=initialize)

    candidate = subparsers.add_parser("candidate")
    candidate.add_argument("id")
    candidate.add_argument("name")
    candidate.set_defaults(run=create_candidate)

    seal = subparsers.add_parser("seal-candidate")
    seal.add_argument("id")
    seal.add_argument("name")
    seal.set_defaults(run=seal_candidate)

    plan = subparsers.add_parser("plan")
    plan.add_argument("id")
    plan.add_argument("--variant")
    plan.set_defaults(run=build_plan)

    register = subparsers.add_parser("register-run")
    register.add_argument("id")
    register.add_argument("result", type=Path)
    register.set_defaults(run=register_run)

    comparison = subparsers.add_parser("compare")
    comparison.add_argument("id")
    comparison.add_argument("--candidate", required=True)
    comparison.set_defaults(run=compare_runs)

    decision = subparsers.add_parser("decide")
    decision.add_argument("id")
    decision.add_argument("--candidate", required=True)
    decision.add_argument("--verdict", choices=["accepted", "rejected", "inconclusive"], required=True)
    decision.add_argument("--reason", required=True)
    decision.add_argument("--follow-up")
    decision.add_argument("--override-comparison", action="store_true")
    decision.set_defaults(run=decide)

    args = parser.parse_args()
    args.run(args)


if __name__ == "__main__":
    main()
