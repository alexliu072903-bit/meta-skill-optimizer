# Meta-Skill Optimizer

[简体中文](README.zh-CN.md)

A small Agent Skill and local toolkit for reviewing and improving a collection of Agent Skills as one behavioral system.

An individual Skill can look excellent while the complete system becomes slower, more rigid, or less decisive. Without Meta-Skill Optimizer, instruction systems are usually edited by intuition. With it, every proposed change is isolated from an immutable Baseline and evaluated with structural evidence and, when comparable execution is available, the same behavioral Cases.

The review mechanism:

- imports Skills, preferences, prompts, and context rules as one complete subject;
- asks what user value each component provides and why it must exist separately;
- preserves the original system as an immutable Baseline;
- isolates every proposed change in a Candidate;
- compares Baseline and Candidate behavior using the same Cases and execution configuration;
- records evidence, regressions, and an `accepted`, `rejected`, or `inconclusive` decision.

The goal is not a prettier collection of prompts. It is a simpler, more capable Agent instruction system with a reviewable reason for every change.

## Use

Make the repository available to Codex or Claude Code as a Skill, then give the Agent the directory:

```text
Review the Skill system in /path/to/skills and optimize it into a better version.
```

The Agent owns the workflow:

```text
read the complete system
→ build the system map
→ find the highest-impact problem
→ create an isolated Candidate
→ run the necessary before-and-after comparison
→ return the Candidate, Diff, and evidence
```

The user does not need to prepare a Manifest, Cases, JSON Results, or CLI commands when the Agent can do that work. The live source remains unchanged; the user decides whether and how to apply the Candidate.

For tool maintenance or custom integration, see the [manual workflow](protocol/manual-workflow.md).

## Repository layout

```text
meta-skill-optimizer/
├── SKILL.md
├── protocol/
│   ├── system-review.md
│   ├── agent-workflow.md
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

The Agent-owned structural review and Candidate workflow are available today. Native Codex and Claude Code adapters for fully isolated behavioral execution are not implemented yet. When comparable execution is unavailable, the Agent must label behavioral impact as unverified rather than claim an observed improvement.

The repository stores Feedback but does not automatically turn it into new Cases or Candidates; that decision belongs to the person using it and their Agent.

## License

MIT
