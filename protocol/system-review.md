# Whole-System Review

Review every declared file together before changing any one of them. The goal is not perfect mechanical coupling; it is a system whose parts are individually justified and collectively coherent.

Before evaluating utility, classify each file's audience using [audience-separation.md](audience-separation.md). Human methodology and Agent Runtime require different success criteria; apparent duplication across them is not automatically a Runtime conflict.

## Stage 1 — Model the whole system

Start with the system purpose and map every file to the function it claims to perform. Use a control-system lens only where it clarifies real behavior:

- `purpose`: the user outcome the complete system tries to improve;
- `inputs and disturbances`: user requests, incomplete context, external changes, and uncertainty;
- `sensing`: research, retrieval, context, or observation capabilities;
- `control`: capabilities that choose direction, scope, priority, or next action;
- `execution`: capabilities that create an artifact or change external state;
- `state`: durable decisions, preferences, progress, or memory;
- `feedback`: evidence and correction that change later behavior;
- `constraints`: safety, authority, scope, and expression boundaries.

One file may serve more than one function, but every additional responsibility increases coupling and needs evidence. Record missing functions, duplicated ownership, and open loops, but do not optimize them yet.

## Stage 2 — Establish component utility

Start every component with the [Two-Question Quick Gate](quick-gate.md):

1. What core value does it provide to the user?
2. Why must it exist as an independent component?

Archive components with no user value. Merge or demote useful content that lacks a standalone reason. Run the detailed review below only for independent components or when evidence is genuinely insufficient.

Review every file, including files that are not discoverable Skills. For each file ask:

1. What real problem and scene justify its existence?
2. What behavior should be better with it than without it?
3. Is that difference observable in a representative case?
4. What rigidity, latency, context load, maintenance, or autonomy cost does it add?
5. Is its useful behavior distinct, or would the base Agent or another simpler instruction already provide it?

For `human-methodology`, replace the behavioral-delta test with: does this material help a person understand, challenge, teach, or evolve the method? Do not require a human document to justify itself as an always-loaded Runtime instruction.

Use a no-component or simpler-instruction comparison when behavior is uncertain. "Well written" and "contains good ideas" are not evidence of utility.

Assign one provisional verdict:

- `keep`: distinct net value is supported;
- `revise`: the underlying capability is useful, but the current implementation weakens it;
- `merge`: useful behavior exists but does not justify a separate file;
- `delete`: representative behavior is equivalent or better without it;
- `unproven`: evidence is insufficient; do not silently treat it as useful or useless.

## Stage 3 — Review interactions among useful components

Only after component utility is established, analyze relationships among `keep`, `revise`, and `merge` components:

- overlap and duplicate ownership;
- trigger competition and shadowing;
- contradictory instructions or priorities;
- broken inputs, outputs, dependencies, and handoffs;
- accumulated constraints that reduce autonomy;
- missing feedback or state transitions;
- behavior that is useful alone but loses value in the full system.

Do not spend integration effort making an unjustified component fit better.

## Stage 4 — Optimize and regress

Propose the smallest portfolio change that improves the system: add, strengthen, reroute, merge, split, demote, or delete. Re-run the affected component cases first, then the full-system cases. Reject a locally positive change when it harms a more important system outcome.

## Required review artifact

Produce:

1. one whole-system map;
2. one component review for every included file;
3. an interaction review limited to components with supported utility;
4. bounded optimization proposals with acceptance and rejection evidence.
