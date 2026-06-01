# Studio Task Operation SOP

## Task Type Reference

| Type | Purpose | Requires Cron |
|---|---|---|
| SQL | ETL transformation, data quality checks | Yes |
| PYTHON | Python script tasks | Yes |
| SHELL | Shell script tasks | Yes |
| FLOW | Multi-task orchestration DAG | Yes |
| INTEGRATION | Data sync (single table) | Yes |
| MULTI_DI | Data sync (multiple tables) | Yes |
| REALTIME | Real-time sync | No (runs continuously) |

## Task Directory Structure

```
{prefix}_elt/
├── 00_ddl/           # DDL CREATE statements for all models (CREATE VIEW/TABLE AS ...)
├── 01_staging/       # Staging layer (view DDL, DRAFT, not scheduled)
├── 02_marts/         # Marts layer (table/incremental DDL, DRAFT + scheduled PUBLISHED)
├── 03_snapshots/     # Snapshot layer (DRAFT + scheduled PUBLISHED)
└── 04_dqc/           # Data quality checks (SQL, optional)
```

**Purpose of 00_ddl**: Stores the complete DDL for each model — it serves as the "specification" for the data pipeline. Team members can view the CREATE statement for every table directly in Studio, making it easy to review schema definitions, manually rebuild tables, and troubleshoot field issues.

## Full Task Creation Workflow

```bash
# 1. Create directories
cz-cli task create-folder {prefix}_elt
cz-cli task create-folder {prefix}_elt/02_marts

# 2. Create task
cz-cli task create fct_orders \
  --type SQL \
  --folder {prefix}_elt/02_marts \
  --description "Order fact table, incremental merge, bizdate parameterized"

# 3. Upload SQL content (with parameters)
cz-cli task save-content fct_orders \
  --content "SELECT ... WHERE dt = '\${bizdate}'" \
  --params '{"bizdate": "bizdate"}'

# 4. Configure scheduling
cz-cli task save-cron fct_orders --cron "0 0 3 * * ?"

# 5. Configure run parameters
cz-cli task save-config fct_orders \
  --retry-count 3 \
  --retry-interval 5 \
  --retry-unit m \
  --vc default_ap \
  --timeout 60 \
  --timeout-unit m

# 6. Configure dependencies
cz-cli task save-config fct_orders \
  --deps replace \
  --dep-tasks '[{"taskId": 123, "taskName": "stg_orders"}]'

# 7. Validate (trial run)
cz-cli task execute fct_orders \
  --param bizdate=2024-01-01 \
  --max-wait-seconds 300

# 8. Deploy
cz-cli task deploy fct_orders
```

## Cron Expression Reference

| Scenario | Cron Expression | Notes |
|---|---|---|
| Daily at 02:00 | `0 2 * * ?` | After data sync completes |
| Daily at 02:30 | `30 2 * * ?` | Staging layer |
| Daily at 03:00 | `0 3 * * ?` | Marts layer |
| Daily at 03:30 | `30 3 * * ?` | DQC check |
| Every hour | `0 * * * ?` | Near-real-time scenarios |
| Every 30 minutes | `*/30 * * * ?` | High-frequency scenarios |

> Cron format: `minute hour day month weekday` (5 fields) or `second minute hour day month weekday year` (7 fields)

## Task Status Reference

| Status | Meaning | Available Operations |
|---|---|---|
| DRAFT | Draft, not deployed | save-content, save-cron, save-config, deploy |
| PUBLISHED | Deployed, scheduling active | execute, undeploy |
| OFFLINE | Taken offline | deploy, delete |

## Run Monitoring Commands

```bash
# View recent run history
cz-cli runs list

# Wait for a run to complete
cz-cli runs wait <run_id>

# View run logs
cz-cli runs logs <run_id>

# View run dependencies
cz-cli runs deps <run_id>

# Re-run a failed instance
cz-cli runs rerun <run_id>

# Backfill historical data
cz-cli runs refill <task_name> \
  --from "2024-01-01T00:00:00" \
  --to "2024-01-31T23:59:59"
```
