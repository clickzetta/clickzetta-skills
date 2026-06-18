# Studio Task Troubleshooting

## Common Issues

| Issue | Cause | Solution |
|---|---|---|
| `SCHEDULE_TASK_HAD_CHILDREN_NODES_EXCEPTION` | DDL task configured with Cron or dependencies | Clear DDL task scheduling config, demote to DRAFT |
| Task publish failed, circular dependency | Task A depends on B, B depends on A | Check dependency chain, remove circular dependencies |
| Sync task keeps failing, no clear error | Column type incompatibility (e.g., BIT(1)→BOOLEAN fails) | Check column type mapping, use broad types in ODS |
| Full database sync task cannot run after creation | MULTI_DI task missing column mapping config | Enter Studio UI to configure source/target mapping, then republish |
| ETL task not triggered on time | Upstream sync task failed, dependency not satisfied | Fix upstream sync task first, then manually trigger ETL |
| DWS layer data not updated | Mistakenly created scheduled task but Dynamic Table not refreshing | Delete redundant scheduled task, confirm Dynamic Table status is RUNNING |
| Task run succeeded but data is empty | SQL logic issue (LEFT JOIN filter in wrong position) | LEFT JOIN right-table filter conditions must be in the ON clause, not WHERE |

---

## Sync Task Troubleshooting

### Common Sync Errors

| Error | Cause | Solution |
|---|---|---|
| `NO_COLUMNS: Cannot fetch columns for <db>.<table>` | Source table doesn't exist in that database | Verify table name + database/schema. For PG: `cz-cli datasource objects uat_pg public` to list tables. For SQL Server: check schema is `dbo` (not `public`) |
| `EXECUTE_FAILED: Job FAILED — ROOT CAUSE: invalid input syntax for type date: "${bizdate}"` | `${bizdate}` not resolved on manual execute | **`${bizdate}` only resolves during scheduled runs.** For ad-hoc testing, use hardcoded date: `WHERE created_at >= '2026-01-01'::date` |
| `EXECUTE_FAILED: Job FAILED — ROOT CAUSE: syntax error at WHERE ""` | Empty string WHERE passed to save-offline-sync (now intercepted by CLI) | Remove the `where` key from params, or use `writeMode=OVERWRITE` for full reload |
| Sync task execute takes 30-80s even for small tables | Each execute runs a Flink Yarn job (provisioning overhead + job submission) | Normal behavior — plan for latency in test cycles |
| OVERWRITE sync leaves old rows after WHERE change | **OVERWRITE + 0 source rows = target NOT truncated.** Engine skips truncate when source produces 0 rows | First incremental run after full load: verify WHERE covers at least 1 day of data. If target must be cleared: `TRUNCATE TABLE <target>` before running sync |
| Sync task `edit_state=published` after `undeploy` | Sync tasks have different state machine than Python tasks; `undeploy` sets `cdc_status=stopped` but `edit_state` may still show `published` | Check `task status` → `cdc_status` for actual runtime state (not `edit_state`). `undeploy` + `cdc_status=offline` = safe to delete |
| `create-offline-sync` fails but task remains | Source table not found → error, but task was already created. (Fixed in latest CLI — orphan tasks now auto-deleted) | If using older CLI: `cz-cli task list --folder <folder>` to find orphan, `cz-cli task delete <id> -y` |
| `Cannot delete folder: 数据文件夹存在文件` | Residual tasks still in folder | `cz-cli task list --folder <folder>` to list remaining tasks, delete each, then retry folder delete |

### VC (Virtual Cluster) Issues

| Error | Cause | Solution |
|---|---|---|
| Sync task deploy OK but execute hangs or fails silently | INTEGRATION VC is SUSPENDED after 60s of inactivity (auto_suspend) | `cz-cli sql --sync "DESC VCLUSTER <name>"` → if `state=SUSPENDED`: `cz-cli sql --sync "ALTER VCLUSTER <name> RESUME" --write` |
| `SHOW VCLUSTERS` doesn't show `vcluster_type` | SHOW returns summary; DESC shows full details | Use `DESC VCLUSTER <name>` to check `vcluster_type=INTEGRATION` |
| No INTEGRATION VC available | Not created for this workspace | `CREATE VCLUSTER IF NOT EXISTS sync_vc VCLUSTER_TYPE=INTEGRATION VCLUSTER_SIZE=1 AUTO_RESUME=TRUE;` |
| `save-offline-sync` / `deploy` rejects vcluster name | Must use INTEGRATION-type VC, not default query VC | List INTEGRATION VCs with `DESC VCLUSTER` and use `--vc <name>` |

---

## Type Mapping — All Source Databases

### MySQL → Lakehouse

| MySQL Type | ❌ Don't Use | ✅ ODS Layer Use | DWD Layer Conversion |
|---|---|---|---|
| `BIT(1)` | `BOOLEAN` | `TINYINT` | `CAST(col AS BOOLEAN)` |
| `DATETIME` | `DATETIME` | `TIMESTAMP` | Use directly |
| `ENUM('a','b')` | `ENUM` | `STRING` | Use directly |
| `TEXT` / `LONGTEXT` | `TEXT` | `STRING` | Use directly |
| `DECIMAL(p,s)` | `FLOAT` | `DECIMAL(p,s)` | Use directly |
| `TINYINT(1)` | `BOOLEAN` | `TINYINT` | `CAST(col AS BOOLEAN)` |

### PostgreSQL → Lakehouse

| PG Type | ❌ Don't Use | ✅ ODS Layer Use | DWD Layer Conversion |
|---|---|---|---|
| `varchar` / `text` / `bpchar` | — | `STRING` | Use directly |
| `int2` / `int4` / `int8` | — | `SMALLINT` / `INT` / `BIGINT` | Use directly |
| `serial` / `bigserial` | — | `INT` / `BIGINT` | Use directly |
| `float4` / `float8` | — | `FLOAT` / `DOUBLE` | Use directly |
| `numeric(p,s)` | — | `DECIMAL(p,s)` | Use directly |
| `money` | `FLOAT` | `DECIMAL(19,4)` | Use directly |
| `timestamp` / `timestamptz` | `timestamp_ntz` (INTEGRATION sync engine doesn't support) | `TIMESTAMP` | Use directly |
| `bool` | — | `BOOLEAN` | Use directly |
| `bit(1)` / `bit(n)` | `BOOLEAN` (may cause sync failure) | `STRING` (safe) | `CAST(col AS ...)` in DWD |
| `bytea` | — | `BINARY` | Use directly |
| `vector` (pgvector) | | `STRING` (safe, or `VECTOR(FLOAT, dim)` if dim known) | Confirm dim with user |
| `_text` / `_int4` / `_float8` (arrays) | | `ARRAY<STRING>` / `ARRAY<INT>` / `ARRAY<DOUBLE>` | Underscore prefix → ARRAY |
| `json` / `jsonb` | — | `JSON` | Use directly |

### PG Column Name Case Sensitivity

> ⚠️ PG allows `"a"` (lowercase) and `"A"` (uppercase) as distinct columns, but Lakehouse/Iceberg treats them as the same column name.

| Scenario | PG Source | Lakehouse Sink | Resolution |
|---|---|---|---|
| Case collision | `a` (varchar), `A` (varchar) | Can't create both `a STRING, A STRING` → `column.already.defined` | Rename one column in sink: `uppercase_a STRING COMMENT 'original PG column A'`. Update `columnMapping` in config JSON. |
| Unquoted PG lowercasing | `CreatedAt` → stored as `createdat` in PG | `createdat` | PG folds unquoted identifiers to lowercase — use the folded name |

> **ODS layer principle: prefer broad types** — sync successfully first, then do precise type conversion in DWD to avoid sync failures.

### SQL Server → Lakehouse

| SQL Server Type | ✅ ODS Layer Use | Notes |
|---|---|---|
| `varchar` / `nvarchar` / `text` | `STRING` | |
| `int` / `bigint` / `smallint` | `INT` / `BIGINT` / `SMALLINT` | |
| `datetime` / `datetime2` | `TIMESTAMP` | |
| `bit` | `STRING` (safe) or `BOOLEAN` | Test first with small sample |
| `decimal(p,s)` / `money` | `DECIMAL(p,s)` | |

---

## Scheduling

### Cron Expression Reference (7-Field)

> ⚠️ **Lakehouse uses 7-field cron: `sec min hour day month weekday year`.**
> After saving, storage converts to Quartz format (`?` replaces `*` in day/weekday when one is specified).
> Some instances reject `*` in the hour field — use `0-23` range.

| Conventional (5-field) | Lakehouse 7-field | Meaning |
|---|---|---|
| `0 2 * * *` | `0 0 2 * * * *` | Daily at 02:00 |
| `30 2 * * *` | `0 30 2 * * * *` | Daily at 02:30 |
| `0 * * * *` | `0 0 0-23 * * * *` | Every hour (use range, not `*`) |
| `*/2 * * * *` (every 2h) | `0 0 */2 * * * *` | Every 2 hours |
| `*/10 * * * *` (every 10min) | `0 */10 * * * * *` | Every 10 minutes |

```bash
# Preview what a cron will produce
cz-cli task cron-preview '0 0 6 * * * *'
# → Next 5 run times: 2026-06-19 06:00:00, 2026-06-20 06:00:00, ...
```

### Dependency Chain Pattern

```
✅ Correct:
00_sync (Cron 0 0 2 * * * *)
    ↓ depends on
04_transform (Cron 0 30 2 * * * *)
    ↓ depends on
05_dqc (Cron 0 0 3 * * * *)

❌ Never include in dependency chain:
- DDL tasks (00_ddl) — run once manually, stay DRAFT
- Dynamic Table DDL tasks (03_ddl_dws_ads) — stay DRAFT, no scheduling
- Dynamic Tables themselves — auto-refresh, no Studio task needed
```

---

## Multi-environment Management

ClickZetta isolates environments via **Workspace** (dev/staging/prod = different Workspaces). Cross-Workspace migration is currently manual.

- Data source configs, schemas, and VCluster names are independent per Workspace — each must be confirmed and replaced during migration
- No one-click migration tool — recommend contacting **data operations (lh-dba role)** for multi-environment strategy
- Export task scripts with `cz-cli task content <task_id>`, adjust manually, recreate in target Workspace

> Recommended: use schema naming within a single Workspace to differentiate environments (e.g., `ecommerce_ods_dev` vs `ecommerce_ods`) to reduce migration complexity.
