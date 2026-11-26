# Workflows

`ss` = `python3 <skill_dir>/scripts/singsight.py`. All times are UTC.

## 1. Trace troubleshooting

1. Run `ss schema-context` to confirm the schema (`public` below) and the available columns.
2. Locate failing traces (an `event_time` range is required):

   ```bash
   ss sql "SELECT trace_id, MIN(event_time) AS start_time, COUNT(*) AS spans,
             SUM(CASE WHEN is_error THEN 1 ELSE 0 END) AS error_spans
           FROM public.ai_agent_trace_detail
           WHERE event_time >= TIMESTAMP '2026-11-19 00:00:00' AND event_time < TIMESTAMP '2026-11-20 00:00:00'
           GROUP BY trace_id HAVING SUM(CASE WHEN is_error THEN 1 ELSE 0 END) > 0
           ORDER BY start_time DESC LIMIT 20"
   ```

3. Fetch every span of one trace and rebuild the causal chain from `parent_span_id`:

   ```bash
   ss sql "SELECT span_id, parent_span_id, event_time, service_name, span_name, operation_name,
             event_type, status_code, error_type, status_message, duration_ms
           FROM public.ai_agent_trace_detail
           WHERE event_time >= TIMESTAMP '2026-11-19 00:00:00' AND event_time < TIMESTAMP '2026-11-20 00:00:00'
             AND trace_id = '<trace_id>'
           ORDER BY event_time LIMIT 100"
   ```

4. In the conclusion, name the `span_name` of the user-facing root span (empty `parent_span_id`), its direct children, and the deepest failing span, together with `error_type` and `status_message`. Do not report only `service_name`.
5. For latency, use P95 (`percentile_approx(duration_ms, 0.95)`), not just the average. For user metrics (DAU, retention), query `ai_agent_user_daily`.

## 2. Live evaluation

1. Write a filter file `f.json` (fields in [filter.md](filter.md)) and check value spelling with `ss filter-options --filter @f.json`.
2. `ss preview --filter @f.json`: check `totalTraces` and `sampledTraces`. If too many traces match, narrow the time range or add `--sampling-rate 0.2` (and pass the same rate to trigger-eval).
3. Pick an evaluator: `ss evaluators` (large; use `--full` and browse with `jq '.items[] | {id, name, evaluatorGroup, scoreType}'`).
   To create one, write a spec file:

   ```json
   {
     "name": "Answer Grounding",
     "evaluator_group": "Agent Execution",
     "description": "Whether the answer is grounded in the tool results",
     "evaluator_config": {"step_prompts": [
       {"step": "extract", "prompt": "From the trace, extract the user request, the tool results, and the final answer.\nReturn only valid JSON: {\"request\": \"...\", \"tool_results\": \"...\", \"final_answer\": \"...\"}\n\nTrace:\n{{system:eval_text}}"},
       {"step": "final_result", "prompt": "Decide whether the final answer is supported by the tool results.\n\nExtraction:\n{{output:extract}}\n\nReturn only valid JSON: {\"score\": 0.0, \"reason\": \"1-2 factual sentences.\"}"}
     ]},
     "score_type": "NUMERIC", "score_min": 0, "score_max": 1
   }
   ```

   `{{system:eval_text}}` is the trace text and `{{output:<step>}}` is an earlier step's output. Run `ss create-evaluator --spec @e.json` for the dry run, add `--yes` after the user confirms, and keep the returned `id`.
4. `ss trigger-eval --name "<name>" --evaluator-id <id> --filter @f.json` for the dry run (this consumes evaluation quota); add `--yes` after the user confirms and keep the returned job `id`. To set the job up now and run it later, add `--no-run`; start it with `ss rerun <job>`.
5. `ss eval-status <job> --wait 600` returns once the status is `COMPLETE`, `ERROR`, `STOPPED`, or `ACTIVE` (never run). On timeout the result carries `wait_timed_out: true`; wait again. To cancel, `ss stop-eval <job>` (dry run, confirm, `--yes`); a running run stops after its current step.
6. `ss eval-results <job> --page-size 20` shows scores and reasoning of the latest complete run; `--max-score 0.5` shows only low scores, and `--order-by score --order ASC` puts the lowest first. For the raw conversation, go back to workflow 1 with the `traceId`.
7. If every result is `PARSE_ERROR`, the model returned nothing. `ss eval-run <job> <runId>` shows the `aiModel` used; ask the user to fix the project's LLM evaluation model, then rerun (workflow 3).

## 3. Rerun and compare runs

A job keeps every run. Rerun it to measure judge noise, or after changing the evaluator's prompts.

1. `ss rerun <job>` for the dry run: `target` shows the job and its status. It consumes evaluation quota; add `--yes` after the user confirms. `TARGET_BUSY` means a run is still queued or running.
   - The new run evaluates the job's filter with the evaluator's **current** config.
   - `--source-run-id <run>` reuses that run's data window instead.
2. `ss eval-status <job> --wait 600`.
3. `ss eval-runs <job>` lists runs newest first, each with `runNo`, `status`, `triggerSource`, `unitCount`, `errorCount`, `avgScore`, `passRate`, and `promptHash`. Runs with different `promptHash` used different evaluator configs; `ss eval-run <job> <runId>` shows the exact steps and prompts.
4. Compare two runs trace by trace:

   ```bash
   # --full writes each result to a file and prints its path as output_file
   ss eval-results <job> --run-id <run_a> --order-by traceId --order ASC --page-size 100 --full
   ss eval-results <job> --run-id <run_b> --order-by traceId --order ASC --page-size 100 --full
   jq -n --slurpfile a <file_a> --slurpfile b <file_b> '
     ($a[0].items | map({(.traceId): .score}) | add) as $x
     | ($b[0].items | map({(.traceId): .score}) | add) as $y
     | [($x + $y) | keys[] | {traceId: ., a: $x[.], b: $y[.]}]
     | map(select(.a != .b))'
   ```

   A page holds at most 100 items; use `--page` for more. Join on `traceId`, not row position: the two runs cover the same traces only when the filter, data window, and sampling rate are unchanged. Runs marked `legacy: true` predate run tracking and may mix several executions.

## 4. Dataset regression

A dataset is a static snapshot of traces, useful for comparing evaluators or agent versions on fixed samples.

1. `ss datasets` lists existing datasets. Create one with `ss create-dataset --name "<name>" [--tag <tag>]` (dry run, confirm, `--yes`). `datasetTag` cannot change after creation.
2. Add traces, preferably from an evaluation job:

   ```bash
   # low-score samples from a live evaluation (latest complete run; --run-id <run> for another)
   ss add-traces <dataset_id> --eval-job-id <job> --max-score 0.5
   # every trace matched by that job's filter
   ss add-traces <dataset_id> --eval-job-id <job> --job-scope FILTER
   # a few hand-picked traces (at most 100)
   ss add-traces <dataset_id> --trace-ids <id1>,<id2> --time-start 2026-11-19T00:00:00Z --time-end 2026-11-20T00:00:00Z
   ```

   Check each dry run and add `--yes` after confirmation. The source job must evaluate live traces, not a dataset. Traces already in the dataset are skipped, so retries are safe.
3. `ss import-status <import_id> --wait 300` until `SUCCEEDED` (see `addedTraces` / `addedSpans`) or `FAILED`.
4. Inspect the dataset (partitioned by `dataset_tag`; no time range needed):

   ```bash
   ss sql "SELECT trace_id, MIN(event_time) AS start_time, COUNT(*) AS spans
           FROM public.ai_agent_eval_dataset_detail WHERE dataset_tag = '<datasetTag>'
           GROUP BY trace_id ORDER BY start_time LIMIT 100"
   ```

5. `ss preview --dataset-id <id>`, then `ss trigger-eval --name "<name>" --evaluator-id <id> --dataset-id <id>` (dry run, confirm, `--yes`).
6. After changing the evaluator, `ss rerun <job>` on the same job and compare its runs (workflow 3). The traces are a fixed snapshot, so score changes come from the evaluator, not from new data. To compare two different evaluators, trigger one job per evaluator and compare `eval-results` across jobs by `traceId`.

## 5. Scheduled evaluation

A scheduled job evaluates a new data window on every fire, for example yesterday's traces each night. Schedule fields are in [schedule.md](schedule.md).

1. Build the filter as in workflow 2, without `time_start` / `time_end`.
2. `ss schedule-preview --schedule @schedule.json` and show the user the next fires and the window each evaluates (always the previous full period). Say how often it fires: every fire consumes evaluation quota.
3. Preview one window of data: `ss preview --filter` with the filter plus `time_start` / `time_end` taken from `recentFire.windowStart` / `windowEnd`.
4. `ss trigger-eval --name <name> --evaluator-id <id> --schedule @schedule.json --filter @filter.json` for the dry run; `--yes` after the user confirms. The job waits for its first fire (`nextFireAt`); add `--run-now` to also run it once now on the latest window that has ended.
5. Follow it with `ss eval-runs <job>`: scheduled runs have `triggerSource: SCHEDULE`, `scheduledFireAt`, and their window. Compare runs as in workflow 3; check `promptHash` before reading a score change as an agent change.
6. Maintain it:
   - `ss pause-schedule <job>` / `ss resume-schedule <job>`. On resume, fires missed while paused are caught up (at most 24 besides the latest).
   - `ss update-schedule <job> --schedule @schedule.json` replaces the schedule; fires restart from now.
   - `ss rerun <job> --source-run-id <run>` re-evaluates one fire's window, for example a `SKIPPED` or `ERROR` run.
   - Resuming or editing makes you the schedule owner: later fires run with your permission. If `scheduleMessage` says the owner lost permission, someone with execution permission resumes it.

## 6. Cleanup

Delete test objects in dependency order, each with a dry run and user confirmation first. Deleting a job also deletes its run history; result rows already in Lakehouse stay.

```bash
ss delete-eval-job <job>
ss delete-dataset <dataset_id>
ss delete-evaluator <evaluator_id>
```
