# Column Provenance and Impact Rules

## Resolve Origins Before Classifying Use

The unit is consumer + column + branch/expression. Preserve both the direct input and root provenance.

1. Bind complete table identities/aliases; resolve CTEs, nested projections, and SELECT * using actual schemas.
2. Align UNION columns by position, not by branch aliases. Record each branch's actual source type and common-type/coercion evidence.
3. Distinguish a JOIN from the target column being its key. Joining account/SKU dimensions does not mix their time columns into the target expression.
4. A column can affect predicates, aggregation, ordering, or window selection without appearing in output.
5. A same-named output can be generated from unrelated date/hour fields or another source.
6. Missing schemas, truncated SQL, dynamic SQL, unsupported parser syntax, or opaque UDF behavior remain unknown.

Suggested origin labels: raw_only, raw_mixed, other, unknown. "Contains a raw-source branch" differs from "all branches originate in raw."

An unchanged projection is a direct column reference or rename only. CAST, arithmetic, formatting, concatenation, and aggregation do not qualify. For UNION, classify branch projections separately from common-type coercion. An unchanged expression does not establish unchanged output type: a DT or ordinary table may declare BIGINT explicitly.

## Classify Unit and Contract Dependencies

| Category | Evidence to identify |
|---|---|
| Milliseconds to seconds | The target integer divided by 1000 before a seconds-based function. |
| Millisecond duration | End minus start interpreted as milliseconds, divided by 3600000/60000, including billing/measurement effects. |
| Offset/threshold | Adding/subtracting millisecond constants or comparison to epoch-millisecond values. |
| Precision/timezone | Truncation, session-dependent functions, TIMESTAMP family, precision, and timezone contracts. |
| Selection/key | WHERE, JOIN, GROUP BY, ORDER BY, window partition/order, and deduplication effects. |
| Output contract | Projection, declared intermediate type, serialized form, external field mapping. |

Token/CPU scaling by 1000 is not timestamp arithmetic. UNIX_TIMESTAMP differences after formatting can be seconds, not original integer milliseconds. A similarly named VC-source column must not be attributed to the raw source.

Follow transformations and indirect effects during recursive field-impact analysis; a seconds alias or an aggregated billing amount can still propagate a root change.

## Assign Work to the Right Mechanism

| Mechanism | Responsibility |
|---|---|
| Query template | Actual definitions, types, history, task/DQC configuration, visibility, pagination and errors. |
| Deterministic code / SQL AST | Exact identity membership, counts/deduplication, type comparison, branch alignment, known engine rules; preserve parser failures. |
| Optional model | Resolve bounded semantic ambiguity in provided SQL, classify use/provenance, verify a candidate quote supports a claim. Prefer available Jev, otherwise low-cost Flash-class models. |
| Human/system owner | Unrecorded writers, external contracts, opaque code, unavailable engine rules and audit gaps. |

## Per-consumer Impact

Supply an explicit change plan: which layers change, whether intermediate declarations migrate, how old values convert, timezone/precision, and authoritative engine rules or verified compatibility evidence.

- execution_failure: provided rules support compile/runtime/schema-contract failure.
- silent_result_change: execution is supported but values, precision, timezone, grouping, selection, or output semantics change.
- unaffected: supplied evidence supports unchanged execution and output contract in the stated scope.
- insufficient_evidence: a necessary definition, source type, conversion plan, or engine rule is missing.

Seeing /1000 establishes a millisecond assumption, not whether TIMESTAMP division fails or implicitly converts. Do not import another engine's behavior.

Aggregate findings without discarding known risks or unknowns. A confirmed failing expression can establish failure while other gaps remain listed; absent a failure, unresolved critical compatibility cannot become unaffected. A consumer result is not an all-system safety decision or permission to deploy.
