# Meta-Skill Optimizer

[中文](README.zh-CN.md)

Meta-Skill Optimizer evaluates and improves a group of Agent Skills as one behavioral system.

The problem is not whether each Skill reads well in isolation. The problem is whether each capability remains reachable, distinct, and useful after it enters the complete system—and whether adding, strengthening, rerouting, merging, splitting, demoting, or deleting it improves the whole.

## v0 boundary

v0 supports an evidence-first, human-approved workflow:

1. copy a Skill system into an ignored local workspace;
2. inventory its declared capabilities, roles, and dependencies;
3. define behavioral cases that represent real work;
4. compare an immutable baseline with isolated candidates;
5. recommend a bounded change based on behavioral evidence;
6. produce a reviewable patch.

The source Skill system is never edited. The optimizer does not automatically apply patches, publish private data, or claim that static text inspection proves behavioral improvement.

## Core evaluation

```text
Capability exists
→ Eligible
→ Activated
→ Influenced behavior
→ Produced observable value
→ Added positive marginal contribution
```

A capability does not need to appear frequently. It needs to produce a stable, distinct, verifiable behavioral improvement in the scenes where it matters. The performance of the whole system takes priority over preserving every Skill.

## Repository structure

```text
meta-skill-optimizer/
├── SKILL.md
├── agents/openai.yaml
├── protocol/
├── schemas/
├── subject.example.json
├── scripts/
├── benchmark/
│   ├── cases/
│   ├── expected/
│   └── results/        # ignored
├── tests/fixtures/
└── workspace/          # ignored
```

## First use

When the experienced runtime combines Skills, preferences, project instructions, or context providers, copy `subject.example.json`, declare every relevant source, and import the composite subject:

```bash
cp subject.example.json subject.local.json
# Edit subject.local.json with local source paths.
python3 scripts/validate_data.py subject.local.json schemas/subject.schema.json
python3 scripts/import_manifest.py subject.local.json
python3 scripts/inventory.py workspace/baseline > workspace/inventory.json
```

For a single-directory subject, use the simpler importer:

```bash
python3 scripts/import_subject.py /path/to/source
python3 scripts/inventory.py workspace/baseline > workspace/inventory.json
python3 scripts/validate_data.py benchmark/cases schemas/case.schema.json
```

Create an isolated candidate after the baseline has been imported:

```bash
python3 scripts/new_candidate.py routing-cleanup
```

After producing baseline and candidate result files according to `protocol/evaluation.md`, compare them and generate a patch:

```bash
python3 scripts/compare_results.py baseline.json candidate.json
python3 scripts/generate_patch.py workspace/baseline workspace/candidates/routing-cleanup
```

## Optimization actions

- `Add`: repeated cases expose the same missing capability;
- `Strengthen`: a distinct capability is useful but too weak to affect behavior;
- `Re-route`: the capability is sound, but its trigger, role, or handoff is wrong;
- `Merge`: overlapping capabilities create no distinct value;
- `Split`: one Skill owns responsibilities that interfere with each other;
- `Demote`: the content belongs in a Rule, Reference, or local principle rather than a Skill;
- `Delete`: removing the capability preserves or improves system behavior.

## Safety boundary

Read `protocol/safety.md` before importing private material or applying a proposed change.

- The live Skill directory remains a read-only source during evaluation.
- `workspace/baseline` is immutable after import.
- Every experiment occurs in a separate candidate.
- `workspace/` and `benchmark/results/` are excluded from Git.
- The optimizer generates patches and never writes them back without explicit user authorization.
- Symbolic links are excluded, and a composite import records source kinds and file hashes in the ignored `subject.lock.json`.

## Current limitations

v0 provides isolated import, capability inventory, data validation, candidate management, result comparison, and patch generation. Behavioral model evaluation is performed through `SKILL.md` under the Evaluation Protocol. The repository does not assume a universal cross-model runtime and does not automatically modify live Skills.

## License

MIT
