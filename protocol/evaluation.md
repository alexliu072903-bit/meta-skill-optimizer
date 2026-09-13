# Evaluation Protocol

Evaluation asks first whether each component improves representative work, then whether the useful components improve or weaken one another. It is not another conversational phase and it does not score writing style in isolation.

## Evaluation order

For a complete system review:

1. map all included files and their claimed roles;
2. compare each component against no component or the simplest reasonable instruction in its intended scenes;
3. assign a provisional component verdict using `schemas/component-review.schema.json`;
4. analyze interactions only among components whose useful behavior is supported;
5. evaluate bounded portfolio changes against the complete baseline.

"Component utility" does not mean removing all context and testing a file in a vacuum. Supply the minimum context and dependencies required by its intended job, while withholding unrelated Meta Skills.

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
- `no-component`: the representative task without the component under review;
- `component`: the same task with that component and only its required context;
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

A component is useful only when it improves a material behavior enough to justify its costs. A candidate system is better only when it improves at least one material behavior without introducing a more important regression. Prefer the simpler component or system when behavioral results are equivalent.

Do not average away a critical failure. Report per-case regressions before aggregate scores.

## Attribution limits

Observed correlation does not prove internal reasoning. Say that a capability changed the output only when the controlled comparison supports it. Otherwise describe the result as consistent with an influence or as inconclusive.
