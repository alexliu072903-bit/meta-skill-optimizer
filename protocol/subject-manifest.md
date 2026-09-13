# Subject Manifest

A behavioral subject is the complete set of instruction sources that can materially affect the runs being compared. A folder of Meta Skills is often only one source.

Use `schemas/subject.schema.json` and `subject.example.json` to declare the subject. Supported source kinds are:

- `runtime-skills`: discoverable or explicitly invoked Skills;
- `preference`: always-on personal behavior and expression rules;
- `project-instructions`: repository or task-scoped Agent instructions;
- `context-provider`: a capability that retrieves or writes context;
- `human-methodology`: philosophy, rationale, examples, and complete methods intended primarily for people;
- `other`: a relevant instruction source that does not fit the above types.

## Inclusion rule

Include a source only when it is normally available in at least one representative case and could change the Agent's decision or behavior. Do not import unrelated memory, entire repositories, logs, or secrets for completeness.

Mark a source `required: false` only when its absence should not block import. A missing optional source is recorded in `subject.lock.json`; a missing required source stops before any baseline is created.

For a directory source, optional `include` and `exclude` arrays select relative paths with glob patterns. Use them when one canonical directory contains files with different runtime roles. Exclusion wins over inclusion. Files omitted by selectors are not copied and cannot affect analysis.

## Import result

`scripts/import_manifest.py` copies each source into:

```text
workspace/baseline/
├── subject.lock.json
└── sources/
    ├── <source-id>/
    └── ...
```

The lock records the resolved source path, source type, selectors, copied file count, and SHA-256 digest of every copied regular file. It remains inside the ignored workspace and must not be committed.

The manifest defines evaluation inputs; it does not establish instruction priority. Record precedence as a capability relationship only when the runtime or an authoritative instruction source actually defines it.
