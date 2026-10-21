---
name: clickzetta-schema-evolution-impact
description: |
  Read-only ClickZetta schema evolution impact analysis: identify writers and readers, trace column provenance, and assess downstream compatibility across one layer, a chosen depth, or all reachable layers.

  Trigger when the user asks "can this column type change", "schema evolution impact", "who writes or reads this table", or "trace downstream field usage".

  Keywords: schema evolution, impact analysis, column type, lineage, downstream, timestamp, compatibility
---

# Schema Evolution Impact Analysis

Use read-only evidence to distinguish execution failures, silent result changes, unaffected consumers, and insufficient evidence. Cover type, value format/unit, precision/timezone, nullability, rename/drop, partition, and output-contract changes. Respond in the user's language.

This skill investigates a proposed change; it does not apply it.

## Quick Start

Choose the investigation stage from the request:

| Request | Action |
|---|---|
| "Who writes this table?" | Match `job_history.output_objects`; inspect actual write SQL and ingestion evidence. |
| "Who reads it?" | Match `input_objects`; aggregate outputs in SQL, retain queries with no output, and cross-check visible definitions/tasks/DQC. |
| "How are these columns used?" | Fetch complete definitions and resolve each expression's actual source, including CTEs and UNION branches. |
| "Only one layer" / "two layers" / "all layers" | Use depth `1` / `2` / `all` from an explicit depth-zero root; follow the traversal rules below. |
| "Can the type change?" | Separate engine support, value migration, fixed intermediate schemas, and consumer compatibility. |
| "No queries" | Use existing evidence only; report its age and missing items. |

Use the profile/workspace already supplied. SQL reads use `--limit 0 --no-truncate` and a finite timeout:

```sh
# Read the current table, Dynamic Table, or materialized-view definition.
cz-cli -p <profile> --workspace <workspace> sql \
  'SHOW CREATE TABLE <schema>.<table>' --limit 0 --no-truncate --timeout 60
```

For history aggregation, [scripts/history_query.py](scripts/history_query.py) generates SQL without contacting a database:

```sh
# Generate a reader query; timestamps use the documented query-session timezone.
python3 <skill-dir>/scripts/history_query.py --direction readers \
  --object demo.raw.events --start '2026-10-13 00:00:00' \
  --end '2026-10-20 00:00:00'
```

## Investigation Boundaries

- Execute only permitted read-only metadata, history, task, and rule queries. Never run returned CREATE statements, ALTER/DML, refreshes, grants, task changes, or temporary-object/UDF creation.
- Respect the requested stage, time window, depth, CLI flags, and model/data restrictions. A targeted question does not authorize a full platform audit. User instructions override this skill.
- Prefer metadata/history over scanning the fact table. Use cached complete evidence, fixed `[start, end)` timestamps, partition pruning, server-side aggregation, and bounded batches.
- Match complete object-list members. Substring matching can confuse corrections, similarly named tables, and SQL LIKE wildcards. A job matching two roots must retain both edges.
- Keep current DDL, task draft, published version, and observed execution separate. For ordinary tables, DDL describes the schema; actual writer SQL or versioned task content describes provenance.
- Distinguish available, confirmed empty, permission denied, failed, truncated, not queried, and unverified-version evidence. A missing channel cannot become "no dependency."
- If the main writer cannot be established, explicitly say **"not found"** (Chinese: **"查不到"**). Name the role to consult: ingestion/metering writer owner, pipeline owner, or platform audit owner. Do not infer ownership from a table creator or a few SQL jobs.

## Downstream Depth and Cost

Support one layer, a specified number of layers, or recursive `all`. If unspecified, collect the direct layer while clarifying the intended depth; do not label it full coverage.

Before recursion, warn: **"Recursive discovery queries history, definitions, tasks, and DQC at each layer; the query volume can be very large."** State the window and batching plan. If all layers were already requested, continue without another permission gate.

Use breadth-first traversal, batch each frontier, cache definitions by object/version, retain all edges, and detect cycles. Track renamed/transformed columns and row-set/aggregation effects, not just unchanged projections. Stop at the chosen depth; for `all`, continue until the reachable frontier is exhausted. On permissions, incomplete pagination, interruption, or a user budget limit, save the checkpoint and report partial completion. "All" means within the stated evidence channels, visibility, and history window.

## Optional Semantic Judgment

Deterministic queries and rules establish facts. When semantic judgment is needed, prefer an already configured and available TypeSafe/Jev client; otherwise try an available low-cost Flash-class model. If none works, continue rules/current-agent analysis and mark unresolved items for human review.

Do not require Jev, configure credentials, buy services, install clients, launch subagents, or silently upgrade to an expensive model for fallback. Respect explicit no-model/no-external-data restrictions. Log actual provider/model and request outcomes; configuration or a mock response is not a real model call. See [model judgment](references/model-judgment.md) for the two-stage contract.

## References — Load Only What the Stage Needs

| Reference | Read when |
|---|---|
| [Investigation workflow](references/investigation.md) | Finding writers/readers, choosing traversal scope, or deciding whether evidence is sufficient. |
| [Queries and CLI](references/queries-and-cli.md) | Building history queries, collecting DDL/task evidence, handling flags, pagination, or network failures. |
| [Column impact](references/column-impact.md) | Resolving lineage and type/unit/contract behavior. |
| [Troubleshooting](references/troubleshooting.md) | Checking common false conclusions and recovery paths. |
| [Model judgment](references/model-judgment.md) | Using optional Jev or low-cost fallback models. |
| [Acceptance](references/acceptance.md) | Running offline tests, blind behavior evaluation, model evaluation, or authorized live probes. |

For authoritative engine syntax/type rules, consult `lakehouse-doc-en`; never assume another engine's implicit casts. Do not invoke mutation-oriented lineage workflows that create helper UDFs during this read-only investigation.

## Deliverable

Match the current question, rather than always producing a full report:

- Writers/readers: objects/tasks, evidence source, time window, and uncovered channels.
- Column use: one row per consumer/column or branch, exact provenance, operation, output type/contract, and a supporting code fragment.
- Observations: problem / possible cause / next handling by query template, deterministic code, model, or human.
- Impact: per consumer `execution_failure`, `silent_result_change`, `unaffected`, or `insufficient_evidence`, with facts, assumptions, evidence, and missing items.
- Recursive results: depth, paths, visited/pending counts, query totals, completion boundary, and resumable gaps.

Record evidence time, full object/column, query window/timezone, source Job ID or task/definition version, fragment location, and status. Save only authorized local artifacts; exclude credentials and unnecessary business rows. A scoped compatibility result is not authorization to deploy.

This standalone package contains an agent workflow and a SQL generator, not an autonomous recursive database collector or a preconfigured model client.
