# Runner Contract

Meta-Skill Optimizer uses one shared contract for two supported execution targets: Codex and Claude Code. A Runner executes prepared tasks and returns auditable result bundles.

Do not add generic adapters for other Agent Runtimes. A Codex or Claude Code adapter must reproduce the subject's native instruction discovery and activation behavior; injecting every instruction into one prompt is not an equivalent evaluation because it bypasses eligibility and routing.

## Input

After editing a draft Candidate, seal it before preparing runs:

```bash
python3 scripts/review_session.py seal-candidate <session-id> <candidate-name>
```

`review_session.py plan` then emits tasks containing:

- `session_id` and `variant`;
- an isolated `subject_path` and SHA-256 `subject_digest`;
- a `case_path`, `case_id`, and `case_digest`;
- the shared `case_set_digest`.

The Runner must use the same model, settings, authorization, and supplied context for comparable variants. It must not reveal the candidate's intended improvement to the evaluated Agent unless the Case itself requires that context.

## Output

Combine all Case executions for one variant into a result bundle conforming to `schemas/result.schema.json`. Preserve:

- the raw Agent output;
- every required and forbidden behavior;
- `pass`, `fail`, or `inconclusive` for each behavior;
- concise evidence that another reviewer can inspect;
- non-empty runtime and model identity;
- a `configuration_digest` covering settings, authorization, and supplied execution context held constant across variants;
- completion, unnecessary steps, critical failures, and notes.

The Runner may execute the Agent automatically, but open-ended behavioral judgments must remain auditable. It must not replace evidence with a scalar score or claim access to hidden model reasoning.

## Registration

Register a completed bundle with:

```bash
python3 scripts/review_session.py register-run <session-id> <result.json>
```

Registration rejects unknown variants, changed Subjects, changed Case sets, duplicate Case IDs, and missing Cases.

After registering comparable runs, create the session-owned Comparison with:

```bash
python3 scripts/review_session.py compare <session-id> --candidate <candidate-name>
```

Do not make a final decision from an unregistered terminal output.
