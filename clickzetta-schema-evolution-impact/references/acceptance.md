# Testing and Acceptance

Keep structural checks, helper tests, agent behavior, model evaluation, and live database verification separate. Passing one does not prove the others.

## Offline Checks

From the repository root (Python 3.10+, no third-party dependency, credentials, database, or model):
```sh
# Validate helper semantics, package metadata/links, registry, and corpus integrity.
python3 -m unittest discover -s clickzetta-schema-evolution-impact/scripts/tests -v
```

The helper tests use in-memory SQLite for exact object membership, all list positions, multiple roots, empty/NULL outputs, failure status, half-open time boundaries, writer direction, internal output preservation, duplicate roots, and rejected inputs. Fixture timestamp casts are adapted to SQLite. This is not verification of ClickZetta types, timezone behavior, or server pagination.

The package checks validate naming/description/keywords, reference availability, example Python syntax, registry completeness, catalog routing, and evaluation ID alignment. Do not confuse corpus integrity with successful behavioral evaluation.

## Blind Agent Evaluation

Use [cases.json](../scripts/evals/cases.json) as input; keep [expected.json](../scripts/evals/expected.json) from the evaluated agent. The 33 cases contain 18 synthetic SQL excerpts and 15 workflow scenarios. Synthetic engine rules are explicitly labeled and must not be presented as native ClickZetta behavior. Do not execute fixture SQL.

In a fresh conversation:
```text
Use $clickzetta-schema-evolution-impact.
Read only scripts/evals/cases.json and the skill's instructions/references.
Do not read expected.json or test assertions. No database or external model calls.
For each case, return its ID, actual column provenance/branches, relevant millisecond
operations, projection/window/join use, output contract, supported impact, evidence
fragments, and gaps. For workflow cases, simulate the allowed next actions and
completion boundary; do not claim actual calls. Respect each request's depth and
no-query/no-model constraints.
```

A separate scorer compares expected.json to the actual responses and records pass/fail/unknown with cited responses.

Acceptance:
- All critical constraints pass: read-only/no-query, 1/N/all depth, recursion cost warning/cycle handling, truthful completeness, missing evidence never safe, correct source attribution, main-writer "not found," no silently dropped flags, optional-model routing, and no invented calls.
- At least 95% of remaining labeled provenance/use and evidence-support checks pass.
- Every positive claim has a valid code fragment; unknown is not silently converted to no.
- Add unseen alias/UNION/cycle counterexamples after tuning, rather than validating only memorized cases.
- Without an independent run and scoring artifact, behavioral acceptance is **not executed**, not passed.

## Optional Model Evaluation

Discover the current configured client: prefer Jev; otherwise try a configured low-cost Flash-class alternative. Use synthetic cases first, fixed model/question versions, and the two-round contract in [model judgment](model-judgment.md).

Measure source/use classification precision and recall, false-unaffected outcomes, review rate, and coverage. Verify that missing-evidence cases route to unknown/review. Evaluate languages/providers separately. Small samples do not prove calibrated probabilities; a fallback's self-reported confidence is not a TypeSafe probability.

Log actual provider/model, question/state hashes, attempts/successes/errors and returned fields. If no configured client, report zero requests. On connection failure, preserve nonzero attempts and zero successes. Mock routing scenarios are not real model evaluation.

## Authorized Live Read-only Verification

Only within the current user's permitted environment/scope:
1. Fix profile/workspace, timezone, window, depth and local evidence location.
2. Record command category, --limit 0 --no-truncate, outcome, Job ID, duration and bounded retry.
3. Verify reader/writer query shapes and actual source/target definitions; ordinary tables need writer SQL.
4. Check exact membership, internal-output mappings, empty-output reads and each quoted source expression.
5. For recursion, warn about potentially very large query volume; verify breadth-first batching, retained edges, deduplication/cycles and checkpointed gaps. Depth N stops at N; all finishes only within the declared visibility/channels.
6. Never create validation tables/UDFs, run ALTER/DML/refreshes, or scan a huge fact table to discover lineage.

During initial contribution, both generated history directions ran successfully in a real ClickZetta workspace. Raw results, real identifiers and Job IDs remain outside the repository. This validates query shape only, not all recursion behavior or field-change compatibility. No real Jev/Flash evaluation or blind agent evaluation was performed as part of this contribution.

## Acceptance Record

Record code revision/hashes, commands/results, behavior scores, model invocation counts, live probe scope, and untested items in review artifacts. Re-run relevant checks after changes. Do not publish local paths, connection identities, raw production SQL, credentials, or historical case counts as current-environment guarantees.
