# Meta-Skill Optimizer development

## Learning loop

Use the optimizer on real isolated subjects. When a run exposes a limitation in the optimizer itself, fix the repository, verify the change, and then resume the subject review. Do not work around a repository defect in the private subject.

```text
real subject → repository limitation → bounded repository fix
→ tests → resume subject evaluation
```

## Repository authorization

For this repository, Alex authorizes Codex to commit and push bounded optimizer improvements directly to `origin/main` after relevant tests pass. Report what changed and the commit afterward; no separate push confirmation is required.

This authorization does not apply to:

- imported subjects or anything under `workspace/`;
- Alex's live Meta Skills, preferences, rules, or context repositories;
- applying generated candidate patches;
- publishing private data;
- other repositories.

## Required checks

Before pushing:

1. run `bash tests/run.sh`;
2. run the Skill validator;
3. run `git diff --check`;
4. confirm ignored private workspace content is not staged.

