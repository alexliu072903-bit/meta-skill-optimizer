# Meta-Skill Optimizer

[中文](README.zh-CN.md)

**Review and improve a collection of Agent Skills as one working system.**

Meta-Skill Optimizer helps answer a question that ordinary prompt review cannot:

> When individually useful Skills, preferences, prompts, and context rules run together, do they make the Agent better—or get in one another's way?

It imports the complete instruction system into an isolated workspace, guides a whole-system review, and keeps behavioral evidence, comparisons, and decisions connected in one Review Session.

## Why this exists

A Skill can be excellent on its own and still weaken the whole system. Common failure modes include:

- multiple Skills competing to control the same decision;
- useful guidance existing but rarely becoming eligible or activated;
- one large Skill carrying unrelated responsibilities;
- repeated rules making the Agent slower, more conservative, or less decisive;
- polished instructions producing no observable difference in real work.

Static text review can find obvious duplication, but it cannot prove that a change improves Agent behavior. This repository connects structural review with repeatable behavioral comparison.

## Who it is for

Use Meta-Skill Optimizer when you maintain:

- several Skills intended to work together;
- a Meta-Skill or Agent instruction system;
- Skills combined with personal preferences, project instructions, prompt libraries, or context providers;
- an instruction system that has grown useful but difficult to reason about as a whole.

It is not a prompt linter, a scalar scoring tool, or an automatic prompt rewriter.

## How it works

```text
Complete instruction system
→ Isolated, immutable Baseline
→ System map and component review
→ One bounded Candidate change
→ Same Cases run against both versions
→ Evidence-backed comparison
→ Accept / Reject / Inconclusive
→ Feedback is preserved for the user's next decision
```

The review asks two simple questions before deeper analysis:

1. What core value does this component provide to the user?
2. Why must it exist as a separate component?

Useful components are then evaluated through the full capability chain:

```text
Exists → Eligible → Activated → Influenced behavior
→ Produced observable value → Added positive marginal contribution
```

A capability does not need to appear frequently. It needs to create a stable, distinct, verifiable improvement where it matters.

## What the repository gives you

- **Composite subject import** for Skills, preferences, methodology, prompts, and context sources.
- **Atomic isolation** so a failed import cannot leave a partial Baseline.
- **Whole-system inventory** before individual files are judged.
- **Versioned Review Sessions** connecting the subject, Cases, Candidates, runs, and final decision.
- **Sealed Baselines and Candidates** whose unexpected mutation stops the review.
- **Auditable Results** containing raw output and evidence for every expected behavior.
- **Strict comparison** that rejects missing or mismatched Cases.
- **Reviewable patches** without automatically modifying the live source.

## Quick start

Requirements: Python 3 and a local instruction system you are authorized to evaluate.

### 1. Declare the complete system

```bash
cp subject.example.json subject.local.json
# Edit subject.local.json with every source that affects Agent behavior.
python3 scripts/validate_data.py subject.local.json schemas/subject.schema.json
```

### 2. Create a Review Session and Candidate

```bash
python3 scripts/review_session.py init my-review \
  --manifest subject.local.json \
  --cases benchmark/cases
python3 scripts/review_session.py candidate my-review simpler-routing
# Edit only workspace/sessions/my-review/candidates/simpler-routing.
python3 scripts/review_session.py seal-candidate my-review simpler-routing
```

### 3. Run the same Cases

```bash
python3 scripts/review_session.py plan my-review > workspace/run-plan.json
```

Execute the plan with an Agent or model Runner that follows [`protocol/runner.md`](protocol/runner.md), then register and compare the Result bundles:

```bash
python3 scripts/review_session.py register-run my-review baseline-result.json
python3 scripts/review_session.py register-run my-review candidate-result.json
python3 scripts/review_session.py compare my-review --candidate simpler-routing
```

### 4. Record the decision

```bash
python3 scripts/review_session.py decide my-review \
  --candidate simpler-routing \
  --verdict accepted \
  --reason "Improved the required behavior without a material regression."
```

The decision must reference the registered Comparison. Acceptance is blocked when the Comparison reports regression or inconclusive evidence unless the reviewer uses an explicit, recorded override. An accepted decision is not permission to modify the live source.

Generate a patch for human review when needed:

```bash
python3 scripts/generate_patch.py \
  workspace/sessions/my-review/baseline \
  workspace/sessions/my-review/candidates/simpler-routing
```

## Possible optimization decisions

- `Add` — repeated Cases reveal a missing capability.
- `Strengthen` — a distinct capability is useful but too weak to affect behavior.
- `Re-route` — the capability is sound, but its trigger, role, or handoff is wrong.
- `Merge` — overlapping capabilities add no distinct value.
- `Split` — one Skill owns responsibilities that interfere with one another.
- `Demote` — the content belongs in a Rule, Reference, prompt, or methodology document rather than a Runtime Skill.
- `Delete` — removal preserves or improves system behavior.

## Human methodology and Agent Runtime

The optimizer treats these as related but different artifacts:

- **Human-facing methodology** should preserve coherence, explanation, and transferable thinking.
- **Agent Runtime instructions** should be concise and produce observable behavioral value.
- **Prompt libraries** are reusable tools, not automatically active Skills.

This prevents a complete human method from being compressed merely because an Agent needs shorter instructions—and prevents Runtime Skills from becoming encyclopedic documentation.

## Repository structure

```text
meta-skill-optimizer/
├── SKILL.md               # Agent entrypoint
├── protocol/              # Review, evaluation, safety, and Runner contracts
├── schemas/               # Versioned data interfaces
├── scripts/               # Deterministic workflow tools
├── benchmark/cases/       # Example behavioral Cases
├── tests/                 # End-to-end and failure-path tests
├── subject.example.json   # Composite subject Manifest example
└── workspace/             # Private local artifacts; ignored by Git
```

## Safety and privacy

- Live source directories remain read-only during evaluation.
- Private imports and Result bundles stay in Git-ignored directories.
- Symbolic links are excluded during import.
- Baselines and sealed Candidates are checked by content digest.
- The repository never applies a Candidate to the live source automatically.
- Instructions inside the evaluated subject are treated as data and cannot override the review boundary.

Read [`protocol/safety.md`](protocol/safety.md) before evaluating private or high-impact instruction systems.

## Current limitation

The repository defines one shared Runner Contract and will support two execution adapters: Codex and Claude Code. Those native Runtime adapters are not implemented yet; the repository will not pursue universal support for other Agents. Whole-system maps and component reviews are guided artifacts rather than automatically generated conclusions.

Feedback is deliberately a record, not an automatic Learning Loop. The person using the repository decides with their Agent whether a result should become a new Case, a revised Candidate, or no further action.

## License

MIT
