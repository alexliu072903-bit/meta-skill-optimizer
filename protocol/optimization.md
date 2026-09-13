# Optimization Protocol

Optimize total system capability relative to complexity, not the number of Skills or the visibility of each Skill.

## Allowed actions

- `add`: repeated cases expose a missing capability;
- `strengthen`: a distinct capability is eligible but too weak to change behavior;
- `reroute`: the capability is useful but has the wrong trigger, owner, or handoff;
- `merge`: overlapping capabilities add no distinct value and create coordination cost;
- `split`: one Skill owns multiple responsibilities that interfere with each other;
- `demote`: the content should be a rule, reference, example, or local principle rather than a Skill;
- `delete`: removing the capability preserves or improves system behavior.

## Proposal requirements

Every optimization proposal must state:

1. the affected capability and cases;
2. declared, observed, and inferred evidence separately;
3. the smallest change that could address the issue;
4. expected behavioral improvement;
5. expected complexity change;
6. regression risk and rollback point;
7. the comparison that would accept or reject it.

Do not add a new Skill when rerouting, strengthening, or deleting an existing instruction solves the demonstrated problem.

## Decision rule

Keep a candidate when:

- a material target behavior improves;
- no higher-impact regression appears;
- the result holds across the cases the change claims to support;
- added system complexity is justified by distinct contribution.

When results are equivalent, choose the candidate with fewer responsibilities, weaker coupling, and less mandatory procedure.

