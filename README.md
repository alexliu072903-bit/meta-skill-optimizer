# Meta-Skill Optimizer

[简体中文](README.zh-CN.md)

A small Agent Skill and local toolkit for reviewing and improving a collection of Agent Skills as one behavioral system.

An individual Skill can look excellent while the complete system becomes slower, more rigid, or less decisive. Without Meta-Skill Optimizer, instruction systems are usually edited by intuition. With it, every proposed change is compared against an immutable Baseline using the same behavioral Cases.

The review mechanism:

- imports Skills, preferences, prompts, and context rules as one complete subject;
- asks what user value each component provides and why it must exist separately;
- preserves the original system as an immutable Baseline;
- isolates every proposed change in a Candidate;
- compares Baseline and Candidate behavior using the same Cases and execution configuration;
- records evidence, regressions, and an `accepted`, `rejected`, or `inconclusive` decision.

The goal is not a prettier collection of prompts. It is a simpler, more capable Agent instruction system with a reviewable reason for every change.

## Use

Clone the repository and declare every instruction source that materially affects Agent behavior:

```bash
git clone https://github.com/alexliu072903-bit/meta-skill-optimizer.git
cd meta-skill-optimizer
cp subject.example.json subject.local.json
# Add local source paths to subject.local.json.
python3 scripts/validate_data.py subject.local.json schemas/subject.schema.json
```

Create a Review Session and one isolated Candidate:

```bash
python3 scripts/review_session.py init my-review \
  --manifest subject.local.json \
  --cases benchmark/cases
python3 scripts/review_session.py candidate my-review simpler-system
# Edit only workspace/sessions/my-review/candidates/simpler-system.
python3 scripts/review_session.py seal-candidate my-review simpler-system
python3 scripts/review_session.py plan my-review > workspace/run-plan.json
```

Execute the Plan with an Agent that follows [`protocol/runner.md`](protocol/runner.md), then register the Results, compare them, and record a decision:

```bash
python3 scripts/review_session.py register-run my-review baseline-result.json
python3 scripts/review_session.py register-run my-review candidate-result.json
python3 scripts/review_session.py compare my-review --candidate simpler-system
python3 scripts/review_session.py decide my-review --candidate simpler-system \
  --verdict accepted --reason "Improved behavior without a material regression."
```

The live source is never modified automatically. Private subjects, Results, and Review Sessions remain in the Git-ignored local `workspace/`.

## Repository layout

```text
meta-skill-optimizer/
├── SKILL.md
├── protocol/
│   ├── system-review.md
│   ├── evaluation.md
│   ├── runner.md
│   └── safety.md
├── schemas/
├── scripts/
├── benchmark/cases/
├── subject.example.json
└── workspace/              # private and ignored by Git
```

Use [`SKILL.md`](SKILL.md) as the Agent entrypoint. The files under `protocol/` contain the detailed review, evaluation, Runner, and safety rules.

## Current boundary

Meta-Skill Optimizer is experimental. Import, isolation, Review Sessions, validation, comparison, decision recording, and patch generation are available today.

Native Codex and Claude Code execution adapters are not implemented yet. The repository will support only these two Runtimes. It stores Feedback but does not automatically turn it into new Cases or Candidates; that decision belongs to the person using the repository and their Agent.

## License

MIT
