---
name: clickzetta-pipeline-review
description: |
  Comprehensive review and diagnosis of ClickZetta Lakehouse data pipelines. Starting from any entry point
  (task name / schema / table name / business domain keyword), autonomously discovers all pipeline objects
  (Studio tasks, Lakehouse tables, pipeline objects, run records), identifies missing scheduling dependencies,
  DDL idempotency issues, layer skipping, Dynamic Table anti-patterns, and other common problems.
  Delivers prioritized fix recommendations and executes them.

  Trigger when the user says: "review pipeline", "check data pipeline", "pipeline diagnosis",
  "pipeline has issues", "task failed", "data is wrong", "pipeline review", "check ETL",
  "pipeline health check", "data lineage check", "pipeline overview", "pipeline audit",
  "task dependency check", "DT refresh failing", "data inconsistency", "pipeline not working".
  Keywords: pipeline review, diagnosis, task dependency, data lineage, DT health, pipeline discovery
---

# ClickZetta Data Pipeline Review Guide

## Wizard: Collect Required Information

On receiving a review request, **do not start exploring immediately**. Collect required information first, then launch the five-phase process.

Ask two questions: (1) Review scope — full review (discover all issues, complete report), targeted diagnosis (specific issue type: task dependencies / DT refresh failures / data inconsistency), or quick health check (P0 issues only, conclusion in 5 minutes)? (2) Execution permission — read-write (can execute fixes, recommended) or read-only (report only, no fixes)?

Pipeline entry point (domain / task name / schema / table name) and known symptoms can be inferred from context or asked after.

| Review scope | Permission | Strategy |
|---|---|---|
| Full review | Read-write | Run all five phases, ask before executing fixes |
| Full review | Read-only | Run all five phases, output report, no fixes |
| Targeted diagnosis | Either | Run only the relevant phase checks |
| Quick health check | Either | Check P0 issues only (missing deps, DT failures), conclude in 5 min |

**If the user has already provided sufficient information (e.g. "review the shenyu_gateway pipeline, full review, can fix"), proceed directly to Phase 1.**

---

## Five-Phase Review Process

```
Discover → Analyze → Identify Issues → Execute Fixes → Verify
```

---

## Phase 1: Discover (Pipeline Overview)

### Entry Point Recognition

| User provides | Expand direction |
|---|---|
| Business domain keyword (e.g. "shenyu_gateway") | Search Studio tasks and Lakehouse schemas simultaneously |
| Studio task name / directory | Read task scripts → find involved tables → find upstream/downstream tasks |
| Lakehouse table name / schema | Find tasks writing to this table → find DTs/tasks reading from it |
| Pipeline object (Pipe/DT/Stream) | Find source and target tables → find associated tasks |
| Error message / run ID | Locate task first → then expand overview |

### Explore Four Layers

**Layer 1 — Studio task layer**
```bash
cz-cli task list-folders
cz-cli task list --folder <folder>
cz-cli task content <task_id>   # focus on: task_type, cron_express, task_dependencies, edit_state
```

**Layer 2 — Lakehouse object layer**
```sql
SHOW SCHEMAS;
SHOW TABLES IN <schema>;
SHOW TABLES IN <schema> WHERE is_dynamic;
SHOW PIPES;
SHOW TABLE STREAMS;
```

**Layer 3 — Run record layer** (config = "should be", run records = "actually is")
```bash
cz-cli runs list --task <task_name> --limit 10
cz-cli runs logs <run_id>
cz-cli runs stats --task <task_name>
```

**Layer 4 — Pipeline object status layer**
```sql
SHOW DYNAMIC TABLE REFRESH HISTORY <schema>.<table> LIMIT 10;
DESC PIPE <pipe_name>;
SELECT COUNT(*) FROM <stream_name>;
```

### Discovery Output

```
Pipeline overview:
- Studio tasks: N (list name, type, status, cron)
- ODS layer: N tables
- DWD layer: N tables
- DWS/ADS layer: N Dynamic Tables
- Pipeline objects: Pipe × N, Table Stream × N
- Run records: last N runs, success rate X%
```

---

## Phase 2: Analyze (Deep Read)

```bash
cz-cli task content <task_id>
# Focus on: task_dependencies, cron_express, edit_state (20=DRAFT, 30=PUBLISHED), task_type
```

**Sync task run mode determination (cannot rely on a single field):**

| Field | Cannot determine alone | Needs combined judgment |
|---|---|---|
| `readMode: BINLOG` | ❌ Does not mean CDC real-time | Also check cron_express, pkWriteMode, run records |
| `pkWriteMode: OVERWRITE` | Overwrite write → offline batch | Confirm with cron and run records |
| Run records show only 1 manual trigger | → Scheduled trigger may not be working | Confirm cron is firing correctly |

**Combined judgment rules:**
- `cron_express` has value + `pkWriteMode: OVERWRITE` + run records show scheduled triggers → **offline batch sync**
- `cron_express` empty + task in continuous running state → **real-time sync (CDC/Kafka)**
- All run records are manual triggers → **scheduling not working, investigate**

---

## Phase 3: Identify Issues

### Checklist (by priority)

**🔴 P0 — Missing scheduling dependencies**

```bash
cz-cli task content <task_id>
# Check if task_dependencies field is empty array []
```

- ETL transform task `task_dependencies` is empty → **P0, must fix**
- Downstream starts executing before upstream sync completes → reads stale or empty data
- Run record timeline is chaotic (multiple manual triggers, abnormal intervals) → typical symptom of missing dependencies

**🔴 P0 — Dynamic Table refresh continuously failing**

```sql
SHOW DYNAMIC TABLE REFRESH HISTORY <schema>.<table> LIMIT 10;
-- status shows consecutive FAILED → P0
```

**🟡 P1 — DDL idempotency issue**

Dynamic Table DDL should use `CREATE OR REPLACE`, not `DROP + CREATE`:
- Race condition between `DROP` and `CREATE`
- If `CREATE` fails, table is already deleted — data loss

```sql
-- ❌ Race condition risk
DROP DYNAMIC TABLE IF EXISTS schema.table;
CREATE DYNAMIC TABLE schema.table ...;

-- ✅ Atomic operation
CREATE OR REPLACE DYNAMIC TABLE schema.table ...;
```

> ⚠️ `CREATE OR REPLACE` has type change restrictions: field type changes (e.g. `TINYINT → BOOLEAN`) will error. Solution: use `CAST(col AS TINYINT)` to maintain type compatibility, or `DROP` then `CREATE`.

**🟡 P1 — DWS layer skipping DWD and reading ODS directly**

```sql
SHOW CREATE TABLE <dws_schema>.<table>;
-- Check FROM clause — DWS should read from DWD, not ODS
```

Skipping layers causes: duplicate computation (JSON parsing/type conversion already done in DWD), inconsistent metrics, higher maintenance cost.

**🟡 P1 — Dynamic Table definition contains ORDER BY**

```sql
SHOW CREATE TABLE <schema>.<dt_name>;
-- If AS clause contains ORDER BY → remove it
```

`ORDER BY` in DT only affects query results, not storage order. It wastes compute on every refresh with no benefit. Sorting logic belongs at the query layer (BI tools or downstream SQL).

**🟢 P2 — DDL task retains Cron configuration**

```bash
cz-cli task content <ddl_task_id>
# edit_state=20 (DRAFT) but cron_express is not empty → P2
```

DRAFT state won't actually execute, but retaining Cron config misleads maintainers. Clean up when convenient.

**🟢 P2 — Studio task script inconsistent with actual DT definition**

After rebuilding DT directly via SQL, Studio task script does not auto-sync:

```bash
cz-cli task content <task_id>   # read Studio task script
# SHOW CREATE TABLE <schema>.<table>  # read actual DT definition
# If inconsistent, sync Studio task script:
cz-cli task save-content <task_id> --content "<new_sql>"
```

---

## Phase 4: Execute Fixes

### Fix dependency configuration

```bash
cz-cli task save-config <task_id> --deps replace \
  --dep-tasks '[{"taskId":<upstream_id>,"taskName":"<upstream_name>"}]'
cz-cli task deploy <task_id> -y
```

### Fix DT DDL (unify to CREATE OR REPLACE)

```sql
-- Confirm field types first to avoid type change errors
SHOW CREATE TABLE <schema>.<table>;

-- Rebuild (use CAST for type compatibility if needed)
CREATE OR REPLACE DYNAMIC TABLE <schema>.<table>
  REFRESH INTERVAL <n> <unit> vcluster <gp_cluster>
AS
SELECT ...
FROM <dwd_schema>.<table>   -- ensure reading from DWD, not skipping layers
...;   -- remove ORDER BY

-- Trigger immediate first refresh
REFRESH DYNAMIC TABLE <schema>.<table>;
```

### Sync Studio task script

```bash
cz-cli task save-content <task_id> --content "<updated_sql>"
```

### Execution principles

- **Direct SQL operations** (rebuild DT, modify table structure) → execute SQL, confirm with user first
- **Studio task config** (dependencies, Cron, script) → use `cz-cli task save-*` + `deploy`
- **When changing both**: change SQL first (data layer), then sync Studio (config layer)

---

## Phase 5: Verify

```sql
-- 1. Dynamic Table refresh status
SHOW DYNAMIC TABLE REFRESH HISTORY <schema>.<table> LIMIT 5;
-- Confirm latest status = SUCCESS

-- 2. Row counts at each layer
SELECT COUNT(*) FROM <ods_schema>.<table>;
SELECT COUNT(*) FROM <dwd_schema>.<table>;
SELECT COUNT(*) FROM <dws_schema>.<table>;

-- 3. Key field null rate
SELECT ROUND(COUNT(key_field) * 100.0 / COUNT(*), 2) AS non_null_pct FROM <schema>.<table>;
```

```bash
# 4. Confirm task dependencies are in effect
cz-cli task content <task_id>   # task_dependencies should no longer be empty

# 5. Confirm Studio task script is synced
cz-cli task content <task_id>   # script content matches actual DT definition
```

Output review conclusion:
```
Review conclusion:
- Issues found: P0 × N, P1 × N, P2 × N
- Fixed: (list each item)
- Not fixed / recommendations: (list each item with reason)
- Verification: row counts at each layer, DT refresh status
```

---

## Common Issues Quick Reference

| Symptom | Root cause | Investigation command |
|---|---|---|
| ETL task reads stale data | Missing dependency, upstream not complete before downstream starts | `cz-cli task content` → check task_dependencies |
| Run record timeline chaotic | Missing dependency, multiple manual triggers | `cz-cli runs list` → check trigger type |
| DT refresh reports "table already exists" | DROP+CREATE race condition, or CREATE OR REPLACE type conflict | `SHOW CREATE TABLE` → confirm field types |
| DT refresh time doesn't align with expectations | REFRESH INTERVAL based on creation time, not clock-aligned | Run `REFRESH DYNAMIC TABLE` immediately after creation |
| Studio script inconsistent with actual DT | Rebuilt via SQL without syncing Studio | `cz-cli task save-content` to sync |
| Sync task judged as CDC but actually offline | Only checked readMode field, not combined judgment | Combine cron, pkWriteMode, run records |
| DWS data inconsistent with DWD metrics | DWS skipping DWD and reading ODS, duplicate computation | `SHOW CREATE TABLE` → check FROM clause |
