# cz-cli Command Reference

Use `cz-cli <command> --help` for authoritative options. This reference is a compact command map for common operations.

## SQL and Jobs

```bash
cz-cli sql "<statement>"                  # Execute SQL, sync by default
cz-cli sql "<statement>" --async          # Return job_id immediately for large/long-running queries
cz-cli sql status <job-id>                # Check async SQL job status
cz-cli job status <job-id>                # Job status and summary
cz-cli job result <job-id>                # Fetch job result set
cz-cli job profile <job-id>               # Flattened job profile basics; use --raw for raw content
```

## Schemas and Tables

```bash
cz-cli schema list [--like <pattern>]
cz-cli schema describe <name>
cz-cli schema create <name>
cz-cli schema drop <name>

cz-cli table list [--schema <name>]
cz-cli table describe <name>
cz-cli table preview <name>
cz-cli table stats <name>
cz-cli table history [name]
cz-cli table create "<ddl>"
cz-cli table drop <name>
```

## Workspaces and Profiles

```bash
cz-cli workspace current
cz-cli status
cz-cli profile list
```

## Studio Tasks

```bash
cz-cli task list
cz-cli task create <name> --type <TYPE>       # SQL/PYTHON/SHELL/SPARK/FLOW/MERGE
cz-cli task content <task>                    # Draft script, config, params, input_params, output_params
cz-cli task save-content <task> --file <f>    # Save task script; --params JSON sets runtime params
cz-cli task save-config <task>                # Save non-cron config: retry, deps, VC, schema, timeout; --param key=value merges params
cz-cli task save-merge <task>                 # Save MERGE rule content and upstream schedule dependencies
cz-cli task save-cron <task>                  # Save cron schedule config
cz-cli task lineage <task>                    # Parse outputs/dependencies; returns save_payload
cz-cli task deps <task>                       # Draft dependencies
cz-cli task deploy <task>                     # Publish/deploy; alias: online
cz-cli task undeploy <task>                   # Undeploy; alias: offline
cz-cli task execute <task>                    # Ad-hoc execution
cz-cli task delete <task>                     # Delete draft/offline task
cz-cli task flow dag <task>                   # Get flow DAG
cz-cli task flow node-save <task> --name N    # Save node script/params; supports --param, --flow-param, --output-param, --input-param
```

For standalone task params:

```bash
cz-cli task save-content <task> --file script.sql --params '{"city":"beijing","dt":"bizdate","yd":"$[yyyy-MM-dd,-1d]"}'
cz-cli task save-config <task> --param city=shanghai --param tenant=acme
```

`save-content --params` stores params while saving content. `save-config --param key=value` merges overrides with existing task params and preserves script content. System params such as `bizdate`, `sys_plan_day`, and `sys_biz_datetime` are auto-detected for JSON `--params` values.

For flow node params:

```bash
cz-cli task flow node-save <flow> --name upstream --output-param result_value
cz-cli task flow bind <flow> --upstream upstream --downstream downstream
cz-cli task flow node-save <flow> --name downstream --input-param up_value=upstream
cz-cli task flow node-save <flow> --name worker --param city=beijing --flow-param bizdate
```

`--output-param key` declares an output value as `$[output]`. `--input-param key=upstreamNodeName` resolves the upstream node id from the flow DAG, so create/bind nodes before using it. `--flow-param key` marks a child node param as inherited from the parent flow execution params (`ref=2`).

For merge tasks:

```bash
cz-cli task create merge_task --type MERGE --folder <folder>
cz-cli task save-merge merge_task --dependency upstream_task --status SUCCESS --status FAILED --status SKIPPED
```

`save-merge` writes the merge rule content and saves the upstream task as a schedule dependency. `--status` is repeatable or comma-separated. `SKIPPED` only applies to upstream if/condition tasks.

For manual output tables, quote JSON as one argument:

```bash
cz-cli task save-config <task> --outputs replace --output-tables '[{"outputTableName":"ws.table","refTableName":"ws.public.table"}]'
```

## Runs and Attempts

```bash
cz-cli runs list [--task <name>]
cz-cli runs detail <id>
cz-cli runs wait <id>
cz-cli runs logs <id>
cz-cli runs deps <task>                       # Published dependencies
cz-cli runs stop <id>
cz-cli runs refill <task> --from D --to D     # D is YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS
cz-cli runs rerun <id>
cz-cli runs stats

cz-cli attempts list [id]
cz-cli attempts log [id]
```

## Datasources

```bash
cz-cli datasource list [--type <type>] [--name <filter>]
cz-cli datasource catalogs <name_or_id>
cz-cli datasource objects <name_or_id> <catalog>
cz-cli datasource describe <name_or_id> <catalog> <object>
cz-cli datasource test <name_or_id>
cz-cli datasource sample <name_or_id> <catalog> <object>
```

## AI Gateway

```bash
cz-cli ai-gateway key list
cz-cli ai-gateway key create <alias>
cz-cli ai-gateway key upsert <alias>
cz-cli ai-gateway key get <ref>
cz-cli ai-gateway key set-quota --ref R --period P --quota N
cz-cli ai-gateway key enable <ref>
cz-cli ai-gateway key disable <ref>
cz-cli ai-gateway key delete <ref>
cz-cli ai-gateway model list [ref]
```

Useful key flags:

- `key list`: `--alias`, `--key`, `--status 1|0`, `--mine`, `--reveal`
- `key create/upsert`: `--period daily|weekly|monthly|total`, `--quota N`, `--route-type default|provider|byok`, `--providers <id ...>`, `--provider-sort price|throughput|latency`, `--private-keys <alias ...>`, `--add-to-llm [name]`, `--use`
- `key get`: `<ref>` can be an alias, masked key, or key value; supports `--add-to-llm [name]` and `--use`
- `key delete`: `--remove-from-llm`

## Integration sync (`cz-cli task integration`)

Configure offline data-integration (batch sync) task content. Create the task skeleton first, then configure its content:

```bash
# 1) Create the task skeleton (single-table → INTEGRATION; multi/whole-db → MULTI_DI)
cz-cli task create my_sync --type INTEGRATION
cz-cli task create my_db_sync --type MULTI_DI

# 2) Configure content
#    single-table: creates the sink table from the source DDL + generates a default field mapping
cz-cli task integration setup my_sync --sync-type single \
  --source-datasource my_mysql --source-schema app --source-table orders \
  --sink-datasource lakehouse --sink-schema public --sink-table orders
#    single-table PARTITION (opt-in via --partitioned; default behavior is a plain non-partition table):
#      static  — whole batch to one partition value; auto-creates PARTITIONED BY (dt STRING):
cz-cli task integration setup my_sync --sync-type single \
  --source-datasource my_mysql --source-schema app --source-table orders \
  --sink-datasource lakehouse --sink-schema public --sink-table orders_di \
  --partitioned --partitions 'dt=${bizdate}'
#      dynamic — per-row routing by a source column (must exist in the source table):
cz-cli task integration setup my_sync --sync-type single \
  --source-datasource my_mysql --source-schema app --source-table orders \
  --sink-datasource lakehouse --sink-schema public --sink-table orders_di \
  --partitioned --dynamic-partition 'dt:create_time'
#    multi-table: one job per table (no table creation; the running task creates them)
cz-cli task integration setup my_db_sync --sync-type multi \
  --source-datasource my_mysql --source-schema app --source-tables orders,users,items \
  --sink-datasource lakehouse --sink-schema public
#    whole-db: mirror entire databases
cz-cli task integration setup my_db_sync --sync-type whole_db \
  --source-datasource my_mysql --source-schema app --source-dbs app,inventory \
  --sink-datasource lakehouse --sink-schema public

# 3) Inspect current config (read before editing)
cz-cli task integration show my_sync

# 4) Edit field mapping / sync params (applied & saved immediately — no UI needed)
#    single-table — column-mapping is a FULL replace (include every row to keep):
cz-cli task integration edit my_sync \
  --column-mapping '[{"source":"id","sink":"id"},{"source":"name","sink":"name"}]' \
  --parallelism 4 --error-limit -1 --m-bytes 8 --split-pk id --where "dt = bizdate"
#    multi/whole-db — table mapping + write modes + naming rules + grouping strategy:
cz-cli task integration edit my_db_sync \
  --table-mapping '[{"source":"app.orders","sink":"public.orders"}]' \
  --pk-write-mode OVERWRITE --non-pk-write-mode OVERWRITE \
  --schema-rule '{SOURCE_DATABASE}' --table-rule '{SOURCE_DATABASE}_{SOURCE_TABLE}' \
  --parallelism 4 --batch-size 4 --connections 4
```

Notes:
- `setup` does NOT change field mapping/params on an existing task — use `edit`. `edit` does NOT change source/sink tables — use `setup`.
- Partition tables (single-table) must be declared explicitly via `--partitioned`; see `sync-pipelines.md` for the static vs dynamic partition details.
- Datasource types are auto-resolved from the datasource name/ID; no need to pass type codes.
- `--where` with date/time scheduling params (e.g. `bizdate`, `$[yyyyMMdd]`): look up the correct Studio scheduling-parameter syntax first (`cz-cli ai-guide` / docs). Do NOT invent parameter formats.
- Integration tasks must execute on an INTEGRATION-type vcluster — pick one via the vcluster list, not the default/GENERAL vc.

## CDC pipeline lifecycle (`cz-cli task cdc`)

For multi-table CDC pipelines (MULTI_REALTIME, fileType 281 — created via `cz-cli task create-realtime-sync`). These commands manage the pipeline and its per-table incremental sync. They do NOT apply to single-table Kafka streaming tasks (fileType 14) — use `task start` / `task stop` for those.

```bash
# List CDC pipeline tasks
cz-cli task cdc list --name my_pipeline

# List the tables in a pipeline — returns the per-table ids used by the *-table ops below
cz-cli task cdc tables my_pipeline

# Per-table incremental sync control (--table-ids is comma-separated ids from 'task cdc tables')
cz-cli task cdc start-table my_pipeline --table-ids 101,102
cz-cli task cdc stop-table my_pipeline --table-ids 101
cz-cli task cdc resync-table my_pipeline --table-ids 101   # re-snapshot
cz-cli task cdc pause-table my_pipeline --table-ids 101
cz-cli task cdc recover-table my_pipeline --table-ids 101

# Take the whole pipeline offline (back to draft)
cz-cli task cdc offline my_pipeline
```

Notes:
- All `task cdc` commands validate the task is fileType 281; running them on any other type returns a `NOT_A_CDC_PIPELINE` error with guidance.
- Get table ids from `task cdc tables` first — the `*-table` ops require them.
