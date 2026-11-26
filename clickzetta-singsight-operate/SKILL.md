---
name: clickzetta-singsight-operate
description: |
  Operate a SingSight AI Agent observability project from the command line: query Trace/Span detail through cz-cli for troubleshooting and latency analysis, and use the SingSight Open API to preview evaluation scope, manage evaluators, run and rerun evaluations, schedule recurring evaluations, compare runs, read results, maintain evaluation datasets, and run regression evaluations. Works without the MCP server.

  Triggered when the user says "SingSight trace", "debug agent trace", "span causal chain", "run an evaluation", "rerun the evaluation", "schedule an evaluation", "daily evaluation", "pause the schedule", "compare evaluation runs", "evaluation results", "low-score traces", "evaluation dataset", "regression evaluation", "custom evaluator".

  Keywords: singsight, agent observability, trace, span, evaluation, evaluator, eval job, eval run, rerun, schedule, dataset, regression, llm judge, cz-cli
---

# SingSight Operate

Two kinds of commands cover SingSight trace analysis and evaluation without the MCP server:

- **SQL**: `ss sql` runs `cz-cli sql` pinned to the project's cz-cli profile, workspace, and schema (read-only).
- **Open API**: every other `ss` subcommand calls the SingSight Open API (evaluations, evaluators, datasets).

Below, `ss` means `python3 <skill_dir>/scripts/singsight.py` (Python 3.11+, standard library only).

To connect an agent to SingSight in the first place (sending OpenTelemetry data), use `singsight-install`.

## Before you start

1. Run `ss config`. On `SINGSIGHT_NOT_CONFIGURED`, ask the user to create `~/.clickzetta/singsight.toml` (mode 600) from [references/config.md](references/config.md). Never invent an API key. The key must be an **Access** key; Ingest keys cannot exchange tokens.
2. Run `ss schema-context` for the project schema, tables, columns, partition keys, and query rules (cached for 24 hours; `--refresh` bypasses the cache). The returned `queryRules` name MCP tools; map them to the commands below.

## Commands

| Command | Purpose | MCP tool |
|---|---|---|
| `ss sql "<SQL>"` / `ss sql -f q.sql` | Read-only SQL through cz-cli | `LH_execute_query` |
| `ss schema-context` | Schema, tables, columns, query rules | `singsight_schema_context` |
| `ss filter-options [--filter F]` | Candidate values per filter dimension (max 100 each) | `singsight_list_filter_options` |
| `ss preview (--filter F \| --dataset-id N)` | Matched count and samples, with evaluation semantics | `singsight_preview_eval_scope` |
| `ss evaluators [--page --page-size]` | Available evaluators | `singsight_list_evaluators` |
| `ss create-evaluator --spec S [--yes]` | Create a custom multi-step evaluator (write) | `singsight_create_custom_evaluator` |
| `ss trigger-eval --name --evaluator-id (--filter F \| --dataset-id N) [--no-run] [--yes]` | Create a job and start its first run; consumes quota (write). `--no-run` only creates it | `singsight_trigger_eval` |
| `ss trigger-eval --name --evaluator-id --schedule S [--filter F \| --dataset-id N] [--run-now] [--yes]` | Create a scheduled job; it waits for its first fire, `--run-now` also runs it once now on the latest ended window (write) | none |
| `ss schedule-preview --schedule S [--count N]` | Validate a schedule; next fires and their data windows | none |
| `ss update-schedule JOB --schedule S [--yes]` | Replace a scheduled job's schedule (write) | none |
| `ss pause-schedule JOB [--yes]` / `ss resume-schedule JOB [--yes]` | Pause or resume a schedule (write) | none |
| `ss rerun JOB [--source-run-id R] [--yes]` | Queue another run of a job (scheduled job: run now); consumes quota (write) | none |
| `ss stop-eval JOB [--yes]` | Stop the job's queued or running run (write) | none |
| `ss eval-status JOB [--wait SEC]` | Status, current step, error of the job's latest run | `singsight_get_eval_status` |
| `ss eval-jobs [--page --page-size]` | Evaluation jobs | `singsight_list_eval_jobs` |
| `ss eval-runs JOB [--page --page-size]` | Run history, newest first, with per-run summary (units, errors, average score, pass rate) | none |
| `ss eval-run JOB RUN` | One run, including the evaluator snapshot (steps and prompts) it ran with | none |
| `ss eval-results JOB [--run-id R --order-by F --order ASC\|DESC --min-score --max-score --service-name --page --page-size]` | Per-item scores and reasoning of one run | none |
| `ss datasets` | Evaluation datasets, including `datasetTag` | `singsight_list_datasets` |
| `ss create-dataset --name [--tag --description] [--yes]` | Create an empty dataset (write) | `singsight_create_dataset` |
| `ss add-traces DS (--eval-job-id J [--job-scope --run-id --min-score --max-score] \| --trace-ids IDS) [--yes]` | Import traces asynchronously (write, safe to retry) | `singsight_add_traces_to_dataset` |
| `ss import-status IMPORT [--wait SEC]` | Import status | `singsight_get_dataset_import_status` |
| `ss delete-eval-job JOB [--yes]` | Delete an evaluation job without an active run, with its run history (write, irreversible) | none |
| `ss delete-dataset DS [--yes]` | Delete a dataset and its trace snapshot (write, irreversible) | none |
| `ss delete-evaluator ID [--yes]` | Delete a custom evaluator (write, irreversible) | none |

`--filter`, `--spec`, `--schedule`, and `--evaluator-params` accept inline JSON, `@path`, or `-` (stdin). See [references/filter.md](references/filter.md) for filter fields. `--trace-ids` accepts a comma-separated list or `@path`. Add `--project NAME` when the config has several projects.

## Rules

- **SQL**: query only tables in the schema returned by `schema-context`. `ai_agent_trace_detail` requires an `event_time` range; `ai_agent_eval_dataset_detail` requires `dataset_tag = '<datasetTag>'`. Add `LIMIT` (at most 100) to detail queries. Do not pass `--write`; this skill is read-only on Lakehouse.
- **Writes** (`create-evaluator`, `trigger-eval`, `rerun`, `stop-eval`, `update-schedule`, `pause-schedule`, `resume-schedule`, `create-dataset`, `add-traces`, and the three `delete-*`): run without `--yes` first to get the `dry_run` request. Show the key parameters (name, evaluator, data source, sample size) to the user, and after they confirm, rerun the exact same command with `--yes`.
- **Deletes** only when the user explicitly asks to delete that object. The dry run returns `target` (name, status, trace count, ...) and `irreversible: true`; confirm each target with the user. Delete in dependency order: eval jobs, then datasets, then evaluators. The script refuses a dataset or evaluator still referenced by eval jobs (`TARGET_IN_USE`, with the job ids), built-in evaluators (`BUILT_IN_EVALUATOR`), unfinished jobs, and datasets with imports in progress (`TARGET_BUSY`). Deleting an eval job removes only the job record; result rows already written to Lakehouse stay.
- **Before triggering an evaluation**, run `ss preview` with the same filter or dataset and tell the user the matched count.
- **Runs**: a job can run many times; each run keeps its own results. A job has at most one queued or running run (`rerun` refuses with `TARGET_BUSY`). A rerun evaluates the job's filter (or the dataset's current contents) with the evaluator's **current** config; `--source-run-id` reuses that run's data window. `eval-results` and `add-traces --job-scope RESULTS` default to the latest `COMPLETE` run; pass `--run-id` to read another one. Before comparing two runs, check `promptHash` in `eval-runs`: a different hash means the evaluator changed between them.
- **Scheduled jobs** fire on `--schedule` ([references/schedule.md](references/schedule.md)); each fire is one run that evaluates one data window, so the filter carries no `time_start` / `time_end` / `date_range_days`, and granularity is TRACE or SPAN. Each fire evaluates the previous full period (a daily 02:00 fire: the previous day 00:00 ~ 24:00); there is no window setting, and the server rejects unknown schedule fields. Traces and spans count toward the window they end in, so a trace is scored only after it has finished. Run `ss schedule-preview` first and show the user the next fires and their windows. Every fire consumes quota; say how often it fires. A fire while the previous run is still going is recorded as a `SKIPPED` run. Whoever creates, edits or resumes the schedule becomes its owner, and fires run with the owner's permission; if the owner loses it, the schedule pauses and `scheduleMessage` says why. `rerun` on a scheduled job runs it once now on the latest window that has ended; `--source-run-id` re-evaluates that run's window (for example a `SKIPPED` or `ERROR` fire). `add-traces --job-scope FILTER` is not available for scheduled jobs; use `RESULTS` with `--run-id`.
- **Job status** is that of its latest run: `ACTIVE` (created with `--no-run`, never run), `QUEUED`, `RUNNING`, `STOPPING`, `COMPLETE`, `ERROR`, `STOPPED`. Scheduled jobs also have `scheduleStatus` (`ACTIVE`, `PAUSED`, `ENDED`) and `nextFireAt`. An `ERROR` whose message says the run was interrupted means the executing instance went away; rerun the job.
- **Do not hand-write evaluation SQL**; evaluations run only through `trigger-eval`.
- **Adding traces to a dataset**: prefer `--eval-job-id` (for example, only low scores with `--max-score 0.5`). The source job must evaluate live traces, not a dataset. `--trace-ids` is capped at 100 and meant for a few hand-picked traces; do not pass large SQL results one by one.
- **Time** is always UTC ISO 8601 with a timezone (for example `2026-11-19T00:00:00Z`); say it is UTC when showing times to the user.

## Output

- Success: one JSON line on stdout, `{"success": true, "data": ...}`. `eval-results` data includes the `runId` it read. Lists longer than 100 items and strings longer than 4000 characters are truncated and marked `"truncated": true`.
- Results over 48 KB (`--max-bytes` to change), or any result with `--full`, are written to a private file under the cache directory, and stdout returns only `output_file`. Read the parts you need with `jq` or `grep` instead of printing the whole file.
- Failure: one JSON line on stderr, `{"success": false, "code", "message", "retryable", "next_action"}`. Exit code 2 for invalid arguments, 1 otherwise. Retry once when `retryable` is true.
- `ss sql` passes through cz-cli output and exit code.

## Workflows

See [references/workflows.md](references/workflows.md) for steps and example commands:

1. **Trace troubleshooting**: locate failing traces with SQL, rebuild the causal chain from `trace_id` and `parent_span_id`, and report the `span_name` of the user-facing root span, its direct children, and the deepest failing span.
2. **Live evaluation**: build a filter with `filter-options`, `preview`, pick or create an evaluator, `trigger-eval`, `eval-status --wait`, `eval-results`.
3. **Rerun and compare runs**: `rerun`, `eval-status --wait`, `eval-runs` for per-run summaries, then `eval-results --run-id` for each run, trace by trace.
4. **Dataset regression**: `create-dataset`, `add-traces --eval-job-id`, `import-status --wait`, `preview --dataset-id`, `trigger-eval --dataset-id`; rerun that job after each change and compare its runs.
5. **Scheduled evaluation**: `schedule-preview`, `preview` over the latest window, `trigger-eval --schedule`, then follow `eval-runs`; `pause-schedule` / `resume-schedule` / `update-schedule` as needed.

## FAQ

| Issue | Cause | Solution |
|---|---|---|
| `SINGSIGHT_NOT_CONFIGURED` | No config file, unknown project, or missing key | Create `~/.clickzetta/singsight.toml`; pass `--project` |
| `UPSTREAM_AUTH_ERROR` / HTTP 401 | Ingest key used, or key revoked | Use an Access key from the project's API Keys settings |
| `ss sql` reads the wrong data | cz-cli profile points at another workspace | Set `workspace` in the project config; it overrides the profile |
| `WRITE_NOT_ALLOWED` from cz-cli | SQL is not read-only | This skill does not write to Lakehouse; use Open API commands |
| add-traces rejected: job is based on a dataset | Source eval job evaluated a dataset | Use a live-trace eval job, or evaluate that dataset directly |
| `TARGET_IN_USE` on delete | Eval jobs still reference the dataset or evaluator | Delete those jobs first |
| `NOT_SCHEDULED` | The job is manual | Use `rerun`, or create a scheduled job with `trigger-eval --schedule` |
| `TARGET_NOT_ACTIVE` / `TARGET_NOT_PAUSED` | Pausing a schedule that is not active, or resuming one that is not paused | Check `scheduleStatus` with `eval-status` |
| Scheduled runs are all `SKIPPED` | Each run takes longer than the interval between fires | Lower the frequency with `update-schedule`, or recreate the job with a lower `--sampling-rate` |
| `TARGET_BUSY` on rerun | The job already has a queued or running run | `eval-status --wait`, or `stop-eval`, then rerun |
| Every result of a run is `PARSE_ERROR` | The model returned nothing (often a wrong or unavailable LLM evaluation model) | Check `aiModel` in `eval-run`, fix the project's LLM evaluation model, then rerun |
