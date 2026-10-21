# Troubleshooting and False Conclusions

| Issue | Likely cause | Prevention / next step |
|---|---|---|
| A few SQL writes are named the primary writer of a huge table | SQL history omits service/streaming writes; stock and recent flow differ | Inspect available ingestion/audit channels; if unsupported say "not found" / "查不到" and consult the writer, ingestion, or audit owner. |
| information_schema.jobs fails | Wrong metadata view | Use job_history where verified; confirm metadata once instead of retrying a nonexistent view. |
| History appears empty | Wrong pt_date format, window, timezone, or visibility | Verify each separately; confirmed empty differs from failed/unqueried. |
| SELECT * or alias consumers disappear | Literal column-name prefilter | Discover table candidates first, then resolve columns. |
| Corrections/similar names match the root | Substring matching or LIKE underscores | Use exact complete-name membership with the actual list representation. |
| A job reading two roots loses an edge | CASE selects only the first root | Use a source-set JOIN or UNION ALL; count unique jobs separately from edges. |
| Hundreds of apparent downstream tables | Per-refresh internal objects | Preserve raw lists and evidence-backed mappings to business outputs; unresolved objects remain gaps. |
| Reads with no output are lost | Empty output_objects filtered away | Inspect their actual SQL. Missing query_tag does not prove manual execution. |
| Full SQL appears complete but is not | CLI, server, or message truncation | SQL --limit 0 --no-truncate; save raw JSON locally and verify upstream pagination. |
| task content / job result rejects flags | SQL flags applied to another subcommand | Follow supported help; do not silently drop the user's flag constraint. Label alternatives' limitations. |
| Network failures generate many jobs | Unlimited retries or concurrent failing reads | Use the approved connection path and finite retry; retain original IDs and cancellation uncertainty. |
| CREATE IF NOT EXISTS is used as actual type evidence | Task text confused with current schema | Fetch current DDL; separately record draft/published/execution versions. |
| A /1000 expression is attributed to the wrong source | Same-named alias or another UNION branch | Trace aliases/CTEs/branch positions and quote enough context. |
| An unchanged output is called unaffected | Fixed intermediate schema, UNION coercion or output contract ignored | Separate expression pass-through, output type, and downstream compatibility. |
| TIMESTAMP change is declared certain to fail | Assumed engine behavior | Verify native rules; otherwise report the known millisecond assumption and unknown runtime outcome. |
| Missing DQC or task evidence becomes "none" | Error/permission/not-queried collapsed into empty | Preserve distinct statuses; missing critical evidence cannot support safety. |
| Seven-day history is called complete lineage | Dormant/static/external readers absent | Cross-check visible definitions/tasks/DQC and state unobserved channels. |
| Depth one is hard-coded | A previous request became a universal limit | Support 1/N/all; respect the current request. |
| Recursive discovery becomes enormous or loops | Repeated scans, cycles, no cache | Warn query volume may be very large; breadth-first batching, deduplication and checkpointing. |
| Recursion stops after transformations | Only direct pass-through columns are followed | Track renamed/conversion outputs, billing aggregates and row-set effects; unknown paths remain pending. |
| "All layers complete" despite a gap | Queue/budget/permission state hidden | Save unexpanded nodes; report partial completion and evidence boundaries. |
| Jev absence blocks analysis | Optional model treated as required | Prefer available Jev; otherwise try configured cheap models, then rules/current-agent analysis with unknowns. |
| Cheap-model fallback silently uses expensive services | Model availability/cost guessed | Use currently exposed low-cost model IDs; do not buy/configure services or upgrade silently. |
| Noul becomes bool(p) or model confidence proves completeness | Probability confused with truth/evidence | Apply evaluated thresholds after deterministic evidence checks; middle values require review. |
| Flash confidence is reported as TypeSafe probability | Incompatible model contracts | Keep actual categories/evidence; leave unavailable probabilities null and evaluate each provider separately. |
| Config/mocks count as real calls | No client-boundary instrumentation | Record attempts/success/errors/provider/version; unavailable/uninvoked clients have no successful calls. |
