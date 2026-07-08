# Sync Pipelines — Integration & CDC Detail

Deeper guidance for offline integration (batch) sync and multi-table CDC pipelines. The command skeletons live in `command-reference.md`; this file covers the semantics and gotchas.

## Single-table integration: partition modes

The user must declare a partitioned sink explicitly with `--partitioned`; without it the sink is a plain non-partition table. `--partitioned` auto-creates a `PARTITIONED BY (dt STRING)` sink table. Two mutually-exclusive modes:

- **Static** — `--partitions 'dt=${bizdate}'`: the whole batch is written to one partition value (typically the scheduling date). Use for daily snapshots.
- **Dynamic** — `--dynamic-partition 'dt:source_col'`: each row is routed to a partition by a source column value. The source column must exist in the source table; if it is missing, confirm the correct column with the user before proceeding.

Partition column defaults to `dt`.

## `setup` vs `edit` — what each changes

- `setup` configures source/sink tables (and creates the sink table for single-table). It does NOT change field mapping or sync params on an existing task.
- `edit` changes field mapping / sync params and is applied & saved immediately. It does NOT change source/sink tables.

So: change tables → `setup`; change mapping/params → `edit`.

## Single-table field mapping

`--column-mapping` is a **FULL replace** — include every column row you want to keep. Example:

```bash
cz-cli task integration edit my_sync \
  --column-mapping '[{"source":"id","sink":"id"},{"source":"name","sink":"name"}]' \
  --parallelism 4 --error-limit -1 --m-bytes 8 --split-pk id --where "dt = bizdate"
```

## Multi-table / whole-db mapping and write modes

Multi-table and whole-db modes do not create tables; the running task creates them. Configure via `edit`:

```bash
cz-cli task integration edit my_db_sync \
  --table-mapping '[{"source":"app.orders","sink":"public.orders"}]' \
  --pk-write-mode OVERWRITE --non-pk-write-mode OVERWRITE \
  --schema-rule '{SOURCE_DATABASE}' --table-rule '{SOURCE_DATABASE}_{SOURCE_TABLE}' \
  --parallelism 4 --batch-size 4 --connections 4
```

- `--table-mapping`: maps source `db.table` to sink `schema.table`.
- `--pk-write-mode` / `--non-pk-write-mode`: write strategy for tables with / without a primary key (`OVERWRITE`, etc.).
- `--schema-rule` / `--table-rule`: naming templates for auto-created sink objects. Placeholders: `{SOURCE_DATABASE}`, `{SOURCE_TABLE}`.
- Tuning: `--parallelism`, `--batch-size`, `--connections`.

## CDC per-table operations

For multi-table CDC pipelines (fileType 281, created via `cz-cli task create-realtime-sync`). Get table ids first:

```bash
cz-cli task cdc tables my_pipeline     # returns per-table ids
```

Then operate per-table (`--table-ids` is comma-separated):

```bash
cz-cli task cdc start-table    my_pipeline --table-ids 101,102
cz-cli task cdc stop-table     my_pipeline --table-ids 101
cz-cli task cdc resync-table   my_pipeline --table-ids 101   # re-snapshot
cz-cli task cdc pause-table    my_pipeline --table-ids 101
cz-cli task cdc recover-table  my_pipeline --table-ids 101
cz-cli task cdc offline        my_pipeline                   # whole pipeline → draft
```

- All `task cdc` commands validate fileType 281; other types return `NOT_A_CDC_PIPELINE`.
- These do NOT apply to single-table Kafka streaming tasks (fileType 14) — use `task start` / `task stop` for those.

## Vcluster and scheduling gotchas

- Integration tasks must run on an **INTEGRATION-type vcluster** — pick one from the vcluster list, not the default/GENERAL vc.
- `--where` with date/time scheduling params (e.g. `bizdate`, `$[yyyyMMdd]`, monthly partitions): look up the correct Studio scheduling-parameter syntax first (`cz-cli ai-guide` / docs). Do NOT invent parameter formats.
- Datasource types are auto-resolved from the datasource name/ID; no need to pass type codes.
