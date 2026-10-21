# Investigation Workflow

## Define the Change and Scope

Record the target, affected columns, old/new physical types or value formats, profile/workspace, fixed history window/timezone, depth (`1`, `N`, `all`), table-level versus field-impact traversal, and permitted channels/models.

For epoch-millisecond BIGINT to TIMESTAMP, distinguish:
1. Only the root schema changes; existing ordinary tables/DTs retain their declared schemas.
2. Intermediate schemas also migrate and consumers receive TIMESTAMP.
3. How existing values preserve instants, precision, and timezone semantics.

Do not assume automatic type propagation. A value-format change is not a physical type change; report unsupported request types rather than disguising them as ALTER_TYPE. A column name or a large integer does not establish its unit.

## A. Identify Writers

Match full members of `output_objects`. Aggregate by inputs, actor, job type/subtype, status, and task attribution. Inspect actual write SQL. Interpret inserted/updated/deleted metrics according to their semantics; separate failures, retries, overwrite, and backfill. Job frequency does not explain current table size.

SQL history may omit direct service writes, SDK ingestion, CDC, Pipes, or streaming paths. Where available, inspect read-only ingestion configuration and audit evidence. Otherwise say **"Main writer: not found"** / **"主要写入方：查不到"**, and identify the ingestion/service owner, pipeline owner, or platform audit role that can confirm. A table creator or SQL submitting account is not necessarily the writer owner.

## B. Identify Readers

Match `input_objects`, aggregate raw `output_objects` in SQL, and retain empty outputs. Cross-check current visible DT/MV/view definitions, versioned Studio tasks, and DQC. For full impact work, also consider streams, Pipes, synchronization source/sink mappings, BI, and application contracts where authorized and exposed.

History establishes observed reads in the window; current definitions establish current references. Neither proves all dependencies. Monthly tasks or external applications may be absent from a seven-day window.

Do not prefilter history by the column's literal name: SELECT *, views, and aliases can hide field references.

Classify outputs as:
- stable business objects;
- internal refresh/delta outputs, mapped only with evidence;
- queries without output objects, whose SQL still needs inspection;
- unresolved internal objects, retained as gaps.

No query_tag does not prove an ad hoc human query.

## C. Inspect Each Column

Read actual source schemas, then:
- DT/MV: current complete SHOW CREATE TABLE.
- Ordinary table: actual DDL plus writer SQL or versioned Studio content.
- View: current view definition or a supported SHOW CREATE VIEW.
- DQC: rule SQL, parameters, enabled state, and scope.

For each output/branch record source expressions, actual source types, casts, arithmetic/units, duration/offset use, predicates/joins/grouping/window keys, unchanged projection, and declared output type. A fragment alone is insufficient without its alias/CTE context.

## D. Traverse One, N, or All Layers

The requested root is depth zero. A pass-through object's own UNION/JOIN definition is part of its investigation, not an extra consumer layer.

Warn before recursion that query volume can be very large. Explain the window, known roots, and caching/batching strategy; do not invent a total estimate. An explicit all-layers request authorizes continuation within its read-only scope, without repeated confirmations.

For each frontier:
1. Inspect roots' generation definitions, UNION positions and other sources' actual types.
2. Separate the presence of a JOIN from use of the affected column in its predicate.
3. Batch exact `input_objects` membership queries, retaining every matched source edge.
4. Fetch/cache direct consumers' definitions or execution SQL, and analyze field use.
5. At depth 1/N, stop at the requested boundary. In all mode, enqueue newly reachable consumers.

### Efficiency, Cycles, and Completion

- Use breadth-first traversal with a fixed time window. Split large source sets into bounded batches; do not repeat full-window scans per object when batching works.
- Save frontier, visited state, all edges, evidence versions, first depth, and paths. Multiple parents and cycles retain their edges without infinite traversal.
- Deduplicate table discovery by object; cache definitions by object/version. Deduplicate field analysis by object/version/affected-field-or-effect set. A later path introducing a new affected field still needs analysis, using cached DDL.
- Field-impact traversal follows renamed/transformed outputs, billing aggregates, predicates, and row-set changes. Do not stop just because projection is no longer unchanged. Prune only a proven non-propagating branch; unknown branches stay pending. Table-level traversal does not use field pruning.
- Report per-layer/cumulative objects, edges, query attempts, cache hits, duration, and next frontier size. Respect user-specified query/time budgets without inventing an undisclosed "all layers" cap.
- On permission/pagination failures, interruption, or an execution limit, checkpoint unexpanded objects and report partial completion. Resume only the remaining frontier/gaps.
- Declare recursive completion only when the reachable queue is exhausted without unresolved expansion gaps, scoped to visibility/window/channels. Empty history alone does not establish a leaf if static definitions were not covered.

Reading a source schema to resolve a current-layer UNION/JOIN does not increase consumer-search depth. A one-layer request must not expand into a recursive audit.

## E. Is There Enough Evidence to Change It?

Answer separately:
- Which dependencies and risks are established?
- Does the engine support this in-place type change, according to authoritative rules?
- Is historical conversion specified?
- Are writers, intermediate schemas, consumers, DQC, and external contracts covered?

Absence of /1000 does not establish safety: UNION coercion, ordering/deduplication, partitioning, serialization, and fixed output schemas can still matter. "SELECT * passes it through" is a propagation signal.

## Evidence and Checkpoints

Use an authorized local directory for a manifest, exact queries, CLI JSON where allowed, versioned definitions, findings, and report. Record source/channel, timestamps/timezone/window, command category, result/error, Job ID, pagination/truncation, file/fragment references, and hashes/versions. Do not include credentials.

Reusing complete cached evidence is efficient; label its age. Do not silently promote old definitions or task drafts to current published truth.
