# Manual Workflow

Use this only for debugging, maintaining, or integrating the deterministic tools. Ordinary users should give the Agent a directory and let it own these steps.

## Declare and initialize

```bash
cp subject.example.json subject.local.json
python3 scripts/validate_data.py subject.local.json schemas/subject.schema.json
python3 scripts/review_session.py init my-review \
  --manifest subject.local.json \
  --cases benchmark/cases
```

## Create and seal a Candidate

```bash
python3 scripts/review_session.py candidate my-review simpler-system
# Edit only workspace/sessions/my-review/candidates/simpler-system.
python3 scripts/review_session.py seal-candidate my-review simpler-system
python3 scripts/review_session.py plan my-review > workspace/run-plan.json
```

## Register, compare, and decide

```bash
python3 scripts/review_session.py register-run my-review baseline-result.json
python3 scripts/review_session.py register-run my-review candidate-result.json
python3 scripts/review_session.py compare my-review --candidate simpler-system
python3 scripts/review_session.py decide my-review --candidate simpler-system \
  --verdict accepted --reason "Improved behavior without a material regression."
```

The Result contract is defined in [runner.md](runner.md). A recorded decision does not apply the Candidate to the live source.
