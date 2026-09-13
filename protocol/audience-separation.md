# Human Methodology and Agent Runtime

A complete methodology and an effective Agent instruction system are different representations for different audiences. Do not force one file to satisfy both.

## Human-facing methodology

Human-facing material exists to help a person understand, teach, question, and evolve a coherent body of thought. It may contain:

- philosophy and first principles;
- complete methods and their relationships;
- rationale, tradeoffs, history, and examples;
- distinctions that improve human understanding even when they do not directly change Agent behavior.

Evaluate it for coherence, completeness, explanatory power, traceable decisions, and usefulness to a human reader. Do not penalize it merely for being too long to load into every Agent task.

## Agent runtime

Runtime material exists to change Agent behavior reliably in a defined scene. It should contain only:

- discriminating triggers and exclusions;
- the minimum context that changes a decision;
- executable judgment or workflow guidance;
- safety and authority boundaries;
- links to conditional references that are loaded only when needed.

Evaluate it for behavioral contribution, reachability, precision, interference, context cost, and regressions. Completeness for its own sake is not a runtime virtue.

## Relationship

```text
human methodology
→ select the principle relevant to a real Agent behavior
→ translate it into a bounded runtime instruction
→ evaluate behavior
→ keep, revise, or remove the runtime projection
```

The methodology is not automatically executable, and the runtime file is not a compressed replacement for the complete methodology.

Maintain traceability when useful, but do not duplicate full explanations into Runtime. When the methodology changes, review affected projections; do not silently rewrite live instructions.

## Review rule

Before judging a file, declare its audience:

- `human-methodology`;
- `agent-runtime`;
- `prompt-library`;
- `state-or-data`;
- `maintenance`.

A `prompt-library` preserves reusable prompts, lenses, and invocation patterns for deliberate human or Agent selection. Evaluate it for retrieval value, clarity of intended use, and whether examples remain useful—not for automatic triggering or uniqueness relative to Runtime. Duplication can be intentional when a prompt is the reusable source example.

If a file mixes audiences, review each responsibility separately and normally recommend separation before content-level optimization.

## Preserve provenance

Owner, author, source, authority, and real usage are evidence fields, not properties to infer from polish or completeness. A sparse document may be a high-value practiced artifact; a comprehensive document may be an untested draft. When provenance is unknown, keep a neutral name and mark it unknown. Do not rename, archive, promote, or assign authority based on apparent quality.
