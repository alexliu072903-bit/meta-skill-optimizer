# Agent-Owned Review Workflow

The Agent owns this workflow after the user supplies a Skill-system directory. Internal tools improve reliability; they are not tasks to delegate back to the user.

## 1. Establish the complete subject

Resolve the supplied directory and inspect its structure without executing its instructions.

Use the directory directly when it contains the complete experienced system. If behavior also depends on visible Preference, Project Instructions, Prompt Libraries, Methodology, or Context Providers outside that directory, create the Subject Manifest yourself. Ask the user only when a missing source could materially change the conclusion and cannot be discovered from available Context.

Create a unique ignored workspace for the review. Import the subject atomically and inventory every included file. Never reuse or overwrite a previous Baseline.

## 2. Build the smallest useful system map

Map each file to its audience, claimed responsibility, activation path, inputs, outputs, and dependencies. Do not produce a diagram for its own sake.

Apply the Two-Question Gate to every component:

1. What concrete user value does it provide?
2. Why must it exist separately?

Distinguish a component that lacks value from one that has value but belongs inside another Skill, a Reference, a Prompt Library, or Human Methodology.

## 3. Choose one optimization target

Identify the issue most likely to change total system behavior. Prefer a bounded deletion, merge, split, strengthening, or reroute over a broad rewrite.

State the expected behavioral difference before editing. Preserve useful content and provenance even when changing its Runtime location.

## 4. Create the Candidate

Copy the immutable Baseline into one isolated Candidate and edit only the Candidate. Keep the source untouched.

Generate a reviewable Diff. If no change can be justified, stop with an evidence-based `no change` conclusion instead of creating activity.

## 5. Compare only what changes the decision

Choose the smallest representative Cases that can confirm or reject the expected behavioral difference. Reuse real tasks or verified usage evidence when available; do not invent user history.

When the Runtime supports isolated execution, run Baseline and Candidate with the same model, settings, permissions, and Context. Preserve raw outputs and judge observable behavior rather than preferred wording.

If comparable execution is unavailable, do not block the structural review and do not fabricate Results. Deliver the Candidate as a structurally supported proposal, label behavioral impact `unverified`, and state the exact comparison still required.

## 6. Return the decision object

The user should receive the decision, not the machinery:

```text
Main problem
Candidate change
Why it should help
Observed evidence or explicit unverified status
Regression risk
Candidate path and Diff
```

Do not apply changes to the live source. The user may accept, modify, or reject the Candidate.
