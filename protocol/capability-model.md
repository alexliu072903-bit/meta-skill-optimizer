# Capability Model

Use this model to describe what a Skill contributes to the system. Do not confuse a file, a Skill, and a capability: one Skill may contain several capabilities, and the same capability may be duplicated across Skills.

## Required fields

Each capability record contains:

- `id`: stable lowercase identifier;
- `source`: file and section where the behavior is declared;
- `purpose`: the user outcome it changes;
- `role`: `workflow`, `judgment`, `context`, `execution`, or `preference`;
- `eligible_scenes`: observable conditions under which it may contribute;
- `activation`: explicit invocation, automatic trigger, dependency call, or always-on rule;
- `inputs`: information or state it requires;
- `outputs`: information, state, action, or constraint it produces;
- `dependencies`: capabilities that must already exist or run;
- `exclusions`: scenes or responsibilities it must not enter;
- `observable_contribution`: the behavioral difference expected when it works.

## System relationships

Classify relationships between capabilities:

- `routes_to`: transfers ownership of the task;
- `provides_to`: supplies context or judgment without taking ownership;
- `requires`: cannot work without the target;
- `overlaps`: produces materially similar behavior;
- `blocks`: prevents the target from activating or completing;
- `supersedes`: intentionally replaces the target.

Do not infer a relationship merely because two files mention the same topic. Cite the relevant declaration or behavioral evidence.

## Structural risks

Report a structural risk when one of these is true:

- two workflow capabilities claim the same scene without a tie-breaker;
- a dependency names a missing or renamed capability;
- an always-on rule contradicts a conditional Skill;
- a capability has no reachable activation path;
- a capability declares value but no observable contribution;
- several capabilities repeat the same mandatory procedure;
- a supporting judgment capability accidentally takes task ownership;
- accumulated constraints remove the autonomy required to complete the task.

Structural risks are hypotheses until a behavioral case demonstrates impact.

