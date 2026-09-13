# Meta-Skill Optimizer

[中文](README.zh-CN.md)

**Find out whether your Agent Skills work better together—and improve the system with evidence instead of intuition.**

An individual Skill can look excellent while the complete system becomes slower, more rigid, or less decisive. Meta-Skill Optimizer reviews Skills, preferences, prompts, and context rules as one behavioral system.

## Why use it?

Without this repository, Skill systems are usually improved by reading and editing instructions:

```text
Good-looking guidance → add more rules → growing complexity
→ unclear cause when Agent behavior gets worse
```

With Meta-Skill Optimizer, every change becomes a controlled experiment:

```text
Complete system → immutable Baseline → one Candidate change
→ same Cases → behavioral comparison → keep or revert
```

| Without it | With it |
| --- | --- |
| Judge how each Skill reads | Judge what the whole system does |
| Keep useful-looking content | Require observable user value |
| Change several instructions at once | Test one bounded Candidate |
| Rely on memory and intuition | Compare against an immutable Baseline |
| Accumulate rules | Add, strengthen, reroute, merge, split, demote, or delete with evidence |

The result is not a prettier collection of prompts. It is a simpler, more capable Agent instruction system with a reviewable reason for every change.

## What it does

1. Imports the complete instruction system into a private, isolated workspace.
2. Asks what value each component provides and why it must exist separately.
3. Preserves the original system as an immutable Baseline.
4. Tests one modified Candidate against the same behavioral Cases.
5. Stores raw outputs and evidence, then compares improvements and regressions.
6. Records `accepted`, `rejected`, or `inconclusive` without changing the live source.

## Quick start

Requirements: Python 3 and a local instruction system you are authorized to review.

```bash
git clone https://github.com/alexliu072903-bit/meta-skill-optimizer.git
cd meta-skill-optimizer
cp subject.example.json subject.local.json
# Add every Skill, preference, prompt, and context source that affects behavior.
python3 scripts/validate_data.py subject.local.json schemas/subject.schema.json
python3 scripts/review_session.py init my-review \
  --manifest subject.local.json \
  --cases benchmark/cases
```

Create one Candidate after reviewing the Baseline:

```bash
python3 scripts/review_session.py candidate my-review simpler-system
# Edit only workspace/sessions/my-review/candidates/simpler-system.
python3 scripts/review_session.py seal-candidate my-review simpler-system
python3 scripts/review_session.py plan my-review > workspace/run-plan.json
```

The generated plan is executed by a compatible Agent Runner. Result registration, comparison, decision recording, and patch generation are handled by the repository. See [`protocol/runner.md`](protocol/runner.md) for the Result contract.

```bash
python3 scripts/review_session.py register-run my-review baseline-result.json
python3 scripts/review_session.py register-run my-review candidate-result.json
python3 scripts/review_session.py compare my-review --candidate simpler-system
python3 scripts/review_session.py decide my-review --candidate simpler-system \
  --verdict accepted --reason "Improved behavior without a material regression."
```

## Current status

Meta-Skill Optimizer is experimental.

Available today:

- composite and atomic import;
- whole-system review protocols;
- immutable Baselines and sealed Candidates;
- versioned Cases, Results, Comparisons, and Decisions;
- regression gates and reviewable patches;
- local private workspaces excluded from Git.

Not available yet:

- native Codex and Claude Code execution adapters.

The repository will support only Codex and Claude Code. It does not automatically turn Feedback into new Cases or Candidates; that decision belongs to the person using it and their Agent.

## Documentation

- [`SKILL.md`](SKILL.md) — Agent entrypoint and operation routing
- [`protocol/system-review.md`](protocol/system-review.md) — whole-system review method
- [`protocol/evaluation.md`](protocol/evaluation.md) — behavioral evaluation rules
- [`protocol/runner.md`](protocol/runner.md) — Runner and Result contract
- [`protocol/safety.md`](protocol/safety.md) — isolation, privacy, and source protection

## License

MIT
