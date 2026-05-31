# Studio Task Troubleshooting

## Common Issues

| Issue | Cause | Solution |
|---|---|---|
| `SCHEDULE_TASK_HAD_CHILDREN_NODES_EXCEPTION` | DDL task configured with Cron or dependencies | Clear DDL task scheduling config, demote to DRAFT |
| Task publish failed, circular dependency | Task A depends on B, B depends on A | Check dependency chain, remove circular dependencies |
| Sync task keeps failing, no clear error | Column type incompatibility (e.g., MySQL BIT(1) vs Lakehouse BOOLEAN) | Check column type mapping (see table below) |
| Full database sync task cannot run after creation | MULTI_DI task missing column mapping config | Enter Studio UI to configure source/target mapping, then republish |
| ETL task not triggered on time | Upstream sync task failed, dependency not satisfied | Fix upstream sync task first, then manually trigger ETL |
| DWS layer data not updated | Mistakenly created scheduled task but Dynamic Table not refreshing | Delete redundant scheduled task, confirm Dynamic Table status is RUNNING |
| Task run succeeded but data is empty | SQL logic issue (LEFT JOIN filter in wrong position) | LEFT JOIN right-table filter conditions must be in the ON clause, not WHERE |

## MySQL → Lakehouse Column Type Mapping

| MySQL Type | ❌ Don't Use | ✅ ODS Layer Use | DWD Layer Conversion |
|---|---|---|---|
| `BIT(1)` | `BOOLEAN` | `TINYINT` | `CAST(col AS BOOLEAN)` |
| `DATETIME` | `DATETIME` | `TIMESTAMP` | Use directly |
| `ENUM('a','b')` | `ENUM` | `STRING` | Use directly |
| `TEXT` / `LONGTEXT` | `TEXT` | `STRING` | Use directly |
| `DECIMAL(p,s)` | `FLOAT` | `DECIMAL(p,s)` | Use directly |
| `TINYINT(1)` | `BOOLEAN` | `TINYINT` | `CAST(col AS BOOLEAN)` |

> **ODS layer principle: prefer broad types** — sync successfully first, then do precise type conversion in DWD to avoid sync failures.

## Scheduling Best Practices

### Cron Expression Reference

```
0 2 * * *      # Daily at 02:00 (data sync)
30 2 * * *     # Daily at 02:30 (ETL, 30 min after sync)
0 3 * * *      # Daily at 03:00 (data quality check)
0 * * * *      # Every hour
```

### Dependency Chain Pattern

```
✅ Correct:
00_sync (Cron 02:00)
    ↓ depends on
04_transform (Cron 02:30)
    ↓ depends on
05_dqc (Cron 03:00)

❌ Never include in dependency chain:
- DDL tasks (00_ddl) — run once manually, stay DRAFT
- Dynamic Tables — auto-refresh, no task needed
```

## Multi-environment Management

ClickZetta isolates environments via **Workspace** (dev/staging/prod = different Workspaces). Cross-Workspace migration is currently manual.

- Data source configs, schemas, and VCluster names are independent per Workspace — each must be confirmed and replaced during migration
- No one-click migration tool — recommend contacting **data operations (lh-dba role)** for multi-environment strategy
- Export task scripts with `cz-cli task content <task_id>`, adjust manually, recreate in target Workspace

> Recommended: use schema naming within a single Workspace to differentiate environments (e.g., `ecommerce_ods_dev` vs `ecommerce_ods`) to reduce migration complexity.
