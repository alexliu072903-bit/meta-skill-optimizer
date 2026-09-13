---
name: meta-skill-optimizer
description: Evaluate and improve a collection of Agent Skills as one behavioral system. Use when Skills are individually useful but may be redundant, unreachable, conflicting, diluted, or collectively weaker than expected; when comparing baseline and candidate Skill combinations; or when deciding whether to add, strengthen, reroute, merge, split, demote, or delete a capability. Do not use for ordinary single-Skill authoring or for silently modifying a live Skill installation.
---

# Meta-Skill Optimizer

Optimize the behavior of the complete Skill system, not the apparent quality or activity of every individual Skill.

## Start safely

1. Read [protocol/safety.md](protocol/safety.md).
2. When behavior depends on multiple instruction sources, read [protocol/subject-manifest.md](protocol/subject-manifest.md) and import a composite subject.
3. Work only on an isolated copy under `workspace/` unless the user explicitly authorizes another test location.
4. Preserve an immutable baseline. Put each proposed change in a separate candidate.
5. Never apply a candidate to the source automatically. Produce a patch for review.

For work that spans import, Candidate creation, behavior runs, and a decision, use `scripts/review_session.py` so every artifact remains connected to one versioned Review Session. Read [protocol/runner.md](protocol/runner.md) before preparing or registering behavior runs.

## Choose the needed operation

- For a fast first-pass decision on any component, read [protocol/quick-gate.md](protocol/quick-gate.md) and answer only its two questions before deeper review.
- When a subject mixes complete human methods with executable Agent instructions, read [protocol/audience-separation.md](protocol/audience-separation.md) before judging verbosity or duplication.
- For a complete portfolio review, read [protocol/system-review.md](protocol/system-review.md) and follow its stage gates in order.
- For inventory, reachability, role, overlap, or dependency analysis, read [protocol/capability-model.md](protocol/capability-model.md).
- For behavioral cases, baseline/candidate runs, ablation, and comparison, read [protocol/evaluation.md](protocol/evaluation.md).
- For deciding whether to add, strengthen, reroute, merge, split, demote, or delete, read [protocol/optimization.md](protocol/optimization.md).

Do not load every protocol for a narrow request.

Do not begin interaction optimization merely because files overlap. First establish whether each component provides net value in its intended scene. A component that is not useful does not deserve integration work.

## Evidence boundary

Separate three kinds of evidence:

- `declared`: what the files say should happen;
- `observed`: what happened in a recorded run;
- `inferred`: the most likely explanation for the difference.

Static inspection can identify structural risks, but it cannot prove behavioral contribution. A behavioral claim requires a representative case and a comparable run.

## Core decision

For each capability, determine:

```text
exists → eligible → activated → influenced behavior
→ produced observable value → added positive marginal contribution
```

Silence outside the intended scene is healthy. A capability does not need to be frequently visible; it needs to create a stable, distinct, verifiable improvement when relevant.

## Close the loop

Do not stop at a static recommendation when the task asks whether a Candidate is better. Preserve raw outputs and behavior evidence, compare identical Case sets, and record one outcome: `accepted`, `rejected`, or `inconclusive`. A recorded decision never applies the Candidate to the source automatically.

## Output

Return only findings that can change the system. For each proposal include:

- evidence and affected cases;
- current system behavior;
- proposed optimization action;
- expected improvement and complexity change;
- regression risk;
- the patch or exact files to change;
- the evidence that would reject the proposal.
