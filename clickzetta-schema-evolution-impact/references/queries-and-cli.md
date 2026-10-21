# Queries and CLI

## Read-only Commands

Use the already supplied profile/workspace. SQL commands default to `--limit 0 --no-truncate` plus a finite timeout. Do not use `--write`, execute returned CREATE statements, or create helper UDFs for lineage.

```sh
# Obtain the current definition; CLI flags do not add a SQL LIMIT to SHOW.
cz-cli -p <profile> --workspace <workspace> sql \
  'SHOW CREATE TABLE <schema>.<table>' --limit 0 --no-truncate --timeout 60

# Run generated, reviewed read-only SQL; store large output in an authorized directory.
cz-cli -p <profile> --workspace <workspace> sql -f <query.sql> \
  --limit 0 --no-truncate --timeout 60
```

Inspect a subcommand's help only when needed. Flags accepted by `sql` are not necessarily accepted by `task content` or `job result`.

## History Query Contract

Use `information_schema.job_history`; do not assume an `information_schema.jobs` view exists. Relevant fields include `job_id`, `job_text`, `start_time`, `pt_date`, `job_creator`, `status`, `job_type`, `job_sub_type`, `query_tag`, `client_info`, `input_objects`, and `output_objects`.

In the verified environment, object fields are comma-separated complete names, whereas `input_tables/output_tables` contain JSON metadata. Confirm delimiter, whitespace, identifier/case behavior, and timestamp/partition representation in a different environment. The helper deliberately accepts only simple, unquoted three-part identifiers; unsupported identifiers require a separately verified matcher, not ad hoc SQL interpolation.

`pt_date` was yyyy-MM-dd, unlike a business partition that might use yyyyMMdd. Document the query-session timezone; use fixed timestamps and partition bounds covering them.

Generate, inspect, then execute:
```sh
# A job matching both roots produces an edge for each root.
python3 <skill-dir>/scripts/history_query.py --direction readers \
  --object demo.billing_dt.effective --object demo.public.events \
  --start '2026-10-13 00:00:00' --end '2026-10-20 00:00:00'

# Writers match output_objects and group input_objects.
python3 <skill-dir>/scripts/history_query.py --direction writers \
  --object demo.raw.events --start '2026-10-13 00:00:00' \
  --end '2026-10-20 00:00:00'
```

The helper:
- uses a source CTE JOIN so multiple roots do not get reduced to a single CASE label;
- matches comma-delimited members with INSTR rather than wildcard LIKE;
- prunes pt_date and applies a half-open timestamp interval;
- aggregates outputs for readers, inputs for writers, and preserves status/empty outputs;
- rejects unsafe/unsupported identifiers and invalid windows;
- generates SQL only, never executes it.

Do not use unescaped LIKE for object membership: even bounded patterns treat underscores as wildcards. For an array/JSON representation, use its verified membership operator instead.

MAX(job_id) and MAX(query_tag) are independent aggregate examples and may come from different rows. Fetch a specific job if their association matters. Counts across multiple roots/outputs are edge observations, not a count of globally unique jobs.

## Completeness and Attribution

Large results should go to local JSON rather than tool-message output, which can truncate independently of CLI settings. Check return code, JSON error fields, columns/rows, pagination, and server limits. `--limit 0` disables the CLI row cap, not every upstream pagination cap. Equal count/returned rows alone does not prove full-channel coverage.

Preserve raw output lists before producing a stable business-object summary. Keep failed attempts separate from successful observed executions. Obtain job_text for outputless queries; retain source aliases when quoting it.

## Known Failure Paths

| Failure | Response |
|---|---|
| task content rejects --no-truncate with "Unknown argument: truncate" | Do not silently remove a user-required flag. Label cached content's age/draft state, or obtain actual execution SQL from authorized history. Neither proves the current published task definition. |
| job result with SQL flags reports "Unknown command: 0" | Check that subcommand's supported syntax; prefer the supported SQL result path instead of repeating the invalid command. |
| FailedToOpenSocket / polling/network failure | Record Job ID, follow the environment's approved network/escalation path, and retry the necessary read at most once for the same cause. Persistent failure becomes a gap. |
| cancellation unconfirmed | Do not claim the server job stopped. Retain the ID for platform follow-up; avoid repeatedly creating replacement jobs. |

Batch independent reads only after the connection path works. Keep dependency-driven follow-ups, approvals, and retries sequential.

## Verification Scope

The generated reader and writer query shapes (including INSTR, source CTE JOIN, timestamp casts, grouping and partition bounds) were exercised in a real ClickZetta workspace during contribution validation. SHOW CREATE TABLE and the column expressions discussed in the workflow were observed in real definitions/executions before anonymization. Keep real identifiers and raw results outside this repository.

Synthetic SQL in the evaluation corpus is explicitly a reasoning fixture, not a supported production SQL example or proof of ClickZetta type behavior. Offline SQLite tests establish membership/window semantics, not ClickZetta runtime compatibility. See [acceptance](acceptance.md) for reproducing the checks.
