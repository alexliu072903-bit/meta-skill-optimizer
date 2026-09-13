# Evaluation Protocol

Evaluation asks whether a Skill-system change improves representative work. It is not another conversational phase and it does not score writing style in isolation.

## Case contract

Every case must specify:

- a realistic user request and only the context normally available;
- `must_behaviors`: observable behaviors required for success;
- `must_not_behaviors`: regressions or harmful behaviors;
- optional capabilities expected to be eligible;
- a short rationale for why the case is representative.

Do not encode the desired wording of the answer. Judge behavior and outcome.

## Comparable variants

Use only the variants needed to answer the current question:

- `baseline`: the unchanged complete Skill system;
- `ablation`: baseline with one capability removed or disabled;
- `candidate`: baseline with one bounded change;
- `isolated`: one capability used alone, only when diagnosing dilution or shadowing.

Keep the user request, supplied context, model/runtime settings, and authorization constant across comparable runs. Record any unavoidable difference.

## Observation

For each run, record:

- whether every `must_behavior` occurred;
- whether any `must_not_behavior` occurred;
- task completion and meaningful user control;
- unnecessary questions, stops, handoffs, or duplicated work;
- which capability contributions are directly observable;
- runtime/model metadata and evaluator notes.

Use `schemas/result.schema.json` for stored results.

## Comparison

A candidate is better only when it improves at least one material behavior without introducing a more important regression. Prefer the simpler system when behavioral results are equivalent.

Do not average away a critical failure. Report per-case regressions before aggregate scores.

## Attribution limits

Observed correlation does not prove internal reasoning. Say that a capability changed the output only when the controlled comparison supports it. Otherwise describe the result as consistent with an influence or as inconclusive.

