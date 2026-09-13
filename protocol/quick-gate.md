# Two-Question Quick Gate

Use this gate before a detailed component review.

## Question 1 — What is the core user value?

State one concrete outcome the component provides to the user. Do not answer with its mechanism, file format, internal stage, or a generic phrase such as "improves efficiency."

Treat verified repeated use and user-supplied provenance as value evidence. Do not infer ownership, authority, or usage from how complete or polished the component appears.

If no concrete user value can be identified:

- verdict: `archive`;
- stop reviewing integration, triggers, or implementation details.

If the value is plausible but unsupported:

- verdict: `needs-evidence`;
- define the smallest representative comparison that could prove or reject it.

## Question 2 — Why must it exist separately?

A component deserves an independent Skill or Runtime file only when at least one of these is true:

- it has a distinct, discriminating trigger;
- it produces a distinct user-visible outcome or external action;
- it owns state or an artifact that adjacent components do not own;
- it requires specialized tools, references, safety boundaries, or deterministic execution;
- merging it would make another component less coherent or less reliable.

"The content is good," "the method is complete," and "it might be useful" are not standalone reasons.

If value exists but standalone existence is not justified:

- verdict: `merge-or-demote`;
- preserve the useful content in the appropriate Runtime component, conditional reference, human methodology, state store, or prompt library.

If both questions pass:

- verdict: `independent`;
- continue to the detailed Component Review and later interaction analysis.

## Output

```text
Component:
Core user value:
Value evidence:
Standalone reason:
Quick verdict: independent / merge-or-demote / archive / needs-evidence
Next action:
```
