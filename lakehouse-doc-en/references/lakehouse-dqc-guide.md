# Data Quality Checks (DQC): SQL-Driven Automated Validation

Your data pipeline is running — but is the data actually correct? Are row counts consistent? Do critical fields contain null values? Are aggregated metrics reasonable? These are questions every data engineer faces every day. Singdata Lakehouse's Data Quality Check (DQC) uses pure SQL to implement automated validation, integrating quality monitoring into the data pipeline so that problems are caught before they impact downstream consumers.

This article uses the NHL Medallion architecture as an example to demonstrate how to build a complete DQC framework across the Bronze → Silver → Gold three-layer model.

---

## DQC Core Concepts

```
  Data Pipeline                          DQC Gate
  ────────────                          ─────────
  Bronze (raw data)   ── after load ──→  row count + freshness
         │
         ▼
  Silver (clean DT)   ── after refresh ──→  null rate + uniqueness + value range
         │
         ▼
  Gold (aggregate DT) ── after refresh ──→  aggregation consistency + volatility
         │
         ▼
     BI / Apps         ←── consume PASS only
```

DQC is not a one-time activity — it is an **automated process embedded in the pipeline**. After each data refresh, checks run automatically and results are written to a `dqc_results` table, with anomalies exposed through a monitoring DT.

---

## SQL Commands Used

| Command / Function | Purpose | Use case |
|------------|------|---------|
| `CREATE SCHEMA` | Create a dedicated DQC layer | Isolate quality check tables |
| `CREATE TABLE` | Create a DQC results table | Store the history of each check run |
| `INSERT INTO ... SELECT` | Write DQC check results | One record per check |
| `CASE WHEN` | Determine PASS/WARN/FAIL | Core logic for all check rules |
| `COUNT(*)` / `SUM(CASE WHEN)` | Row count, conditional count | Row count validation, null rate, uniqueness |
| `MIN` / `MAX` | Value range upper and lower bounds | Value range checks, freshness checks |
| `CREATE DYNAMIC TABLE` | Create a DQC dashboard DT | Auto-refresh quality status summary |
| `REFRESH DYNAMIC TABLE` | Manually trigger DT refresh | Initialize data after first creation |

---

## DQC Check Types

| Type | Description | Example |
|---|---|---|
| **Row count consistency** | Whether upstream and downstream row counts match | Bronze team_info(33) = Silver dim_team(33) |
| **Null rate** | Proportion of NULL values in critical fields | goals null rate should be 0% |
| **Uniqueness** | Whether ID fields contain duplicates | player_id should be unique |
| **Value range** | Whether numeric values fall within reasonable bounds | goals >= 0, save_pct in [0,1] |
| **Freshness** | Whether data has been updated to the latest | Latest season >= 2019 |
| **Aggregation consistency** | Whether summary metrics are self-consistent | wins + losses = games played |
| **Referential integrity** | JOIN key match rate | skater_stats.player_id exists in player_info |

---

## Creating the DQC Results Table

```sql
CREATE SCHEMA IF NOT EXISTS dqc COMMENT 'Data Quality Check layer';

CREATE TABLE dqc.dqc_results (
    check_id    STRING    COMMENT 'Check ID, e.g. DQC-001',
    check_name  STRING    COMMENT 'Check type: row_match/null_rate/uniqueness...',
    layer       STRING    COMMENT 'Data layer: bronze/silver/gold',
    metric      STRING    COMMENT 'Metric name',
    expected    STRING    COMMENT 'Expected value or range',
    actual      STRING    COMMENT 'Actual value',
    status      STRING    COMMENT 'PASS / WARN / FAIL',
    detail      STRING    COMMENT 'Check description',
    checked_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
) COMMENT 'DQC check results table';
```

---

## Defining Check Rules

### Row Count Consistency

Verify that the Silver layer dimension table row count matches the Bronze source table:

```sql
INSERT INTO dqc.dqc_results (check_id, check_name, layer, metric, expected, actual, status, detail)
SELECT 'DQC-001', 'dim_row_match', 'silver', 'dim_team_rows',
    CAST((SELECT COUNT(*) FROM nhl_game_data.team_info) AS STRING),
    CAST((SELECT COUNT(*) FROM silver.dim_team) AS STRING),
    CASE WHEN (SELECT COUNT(*) FROM nhl_game_data.team_info)
            = (SELECT COUNT(*) FROM silver.dim_team)
         THEN 'PASS' ELSE 'FAIL' END,
    'Bronze team_info row count should match Silver dim_team';
```

### Null Rate

```sql
INSERT INTO dqc.dqc_results (check_id, check_name, layer, metric, expected, actual, status, detail)
SELECT 'DQC-003', 'null_rate', 'silver', 'skater_goals_null_pct',
    '=0',
    CAST(ROUND(SUM(CASE WHEN goals IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS STRING),
    CASE WHEN SUM(CASE WHEN goals IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) = 0
         THEN 'PASS' ELSE 'WARN' END,
    'Silver fact_skater_stats.goals should have no NULLs'
FROM silver.fact_skater_stats;
```

> **PASS vs WARN vs FAIL severity levels**:
> - `PASS`: Fully meets expectations
> - `WARN`: Deviation within tolerance, needs attention but should not block (e.g., null rate < 1%)
> - `FAIL`: Severely out of range, should block downstream consumption

### Uniqueness

```sql
INSERT INTO dqc.dqc_results (check_id, check_name, layer, metric, expected, actual, status, detail)
SELECT 'DQC-005', 'uniqueness', 'silver', 'dim_player_id_unique',
    'TRUE',
    CAST(CASE WHEN COUNT(*) = COUNT(DISTINCT player_id) THEN 'TRUE' ELSE 'FALSE' END AS STRING),
    CASE WHEN COUNT(*) = COUNT(DISTINCT player_id) THEN 'PASS' ELSE 'FAIL' END,
    'Silver dim_player.player_id should be unique'
FROM silver.dim_player;
```

### Value Range

```sql
INSERT INTO dqc.dqc_results (check_id, check_name, layer, metric, expected, actual, status, detail)
SELECT 'DQC-006', 'value_range', 'silver', 'skater_goals_positive',
    '>=0',
    CAST(MIN(goals) AS STRING),
    CASE WHEN MIN(goals) >= 0 THEN 'PASS' ELSE 'FAIL' END,
    'Silver fact_skater_stats.goals should not be negative'
FROM silver.fact_skater_stats;
```

### Freshness

```sql
INSERT INTO dqc.dqc_results (check_id, check_name, layer, metric, expected, actual, status, detail)
SELECT 'DQC-008', 'freshness', 'bronze', 'max_season',
    '>=2019',
    CAST(MAX(season) AS STRING),
    CASE WHEN MAX(season) >= 2019 THEN 'PASS' ELSE 'WARN' END,
    'Bronze latest season should not be earlier than 2019'
FROM nhl_game_data.game;
```

---

## DQC Dashboard

Aggregate `dqc_results` into a Dynamic Table dashboard for a one-stop view of quality status across layers:

```sql
CREATE OR REPLACE DYNAMIC TABLE dqc.dqc_dashboard
REFRESH INTERVAL 1 DAY VCLUSTER DEFAULT
COMMENT 'DQC Dashboard - quality status summary by layer'
AS
SELECT
    layer,
    COUNT(*) AS total_checks,
    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) AS pass_cnt,
    SUM(CASE WHEN status = 'WARN' THEN 1 ELSE 0 END) AS warn_cnt,
    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) AS fail_cnt,
    ROUND(SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS pass_rate
FROM dqc.dqc_results
GROUP BY layer;
```

**View the dashboard:**

```sql
SELECT * FROM dqc.dqc_dashboard ORDER BY layer;
```

---

## Validation Results

Running 10 DQC checks on the NHL Medallion architecture (Bronze: 10 tables → Silver: 4 DTs → Gold: 5 DTs):

| ID | Type | Layer | Metric | Expected | Actual | Status |
|---|---|---|---|---|---|---|
| DQC-001 | Row count | silver | dim_team_rows | 33 | 33 | PASS |
| DQC-002 | Row count | silver | dim_player_rows | 3925 | 3925 | PASS |
| DQC-003 | Null | silver | goals_null_pct | =0 | 0.00% | PASS |
| DQC-004 | Null | silver | player_name_null_pct | <1% | 0.00% | PASS |
| DQC-005 | Uniqueness | silver | player_id_unique | TRUE | TRUE | PASS |
| DQC-006 | Value range | silver | goals >= 0 | >=0 | 0 | PASS |
| DQC-007 | Value range | silver | points >= 0 | >=0 | 0 | PASS |
| DQC-008 | Freshness | bronze | max_season | >=2019 | 2020 | PASS |
| DQC-009 | Aggregation | gold | unique_seasons | >0 | 19 | PASS |
| DQC-010 | Aggregation | gold | wins >= 0 | >=0 | 0 | PASS |

**All PASS, 100% pass rate.**

---

## Integrating with the Data Pipeline

### Option 1: Manual trigger (suitable for development validation)

```sql
-- Run all DQC checks, then view results
SELECT check_id, status, metric, actual
FROM dqc.dqc_results
WHERE status != 'PASS';  -- show anomalies only
```

### Option 2: Dynamic Table automated execution

Wrap DQC check logic in a Dynamic Table to automatically re-run after each source table refresh:

```sql
-- DQC check DT: null rate monitoring
CREATE OR REPLACE DYNAMIC TABLE dqc.skater_null_monitor
REFRESH INTERVAL 1 DAY VCLUSTER DEFAULT
COMMENT 'Silver layer player stats null rate monitoring'
AS
SELECT
    'DQC-003' AS check_id,
    'null_rate' AS check_name,
    'silver' AS layer,
    'skater_goals_null_pct' AS metric,
    '=0' AS expected,
    CAST(ROUND(SUM(CASE WHEN goals IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS STRING) AS actual,
    CASE WHEN SUM(CASE WHEN goals IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) = 0
         THEN 'PASS' ELSE 'WARN' END AS status
FROM silver.fact_skater_stats;
```

> **Note**: DQC results in DT mode are overwritten with each REFRESH. To retain historical records, INSERT results into the `dqc_results` table instead of using a DT.

### Option 3: Studio task scheduling

Create a DQC task in Studio with a Cron schedule and dependency on the ETL task:

```
00_sync (Cron 02:00)
    ↓
04_etl (Cron 02:30, depends on 00)
    ↓
05_dqc (Cron 03:00, depends on 04)  ← DQC runs after ETL completes
```

If DQC finds a FAIL, you can configure Studio alert rules to send notifications.

---

## DQC Checklist

| Layer | Must check after load | Recommended checks |
|---|---|---|
| **Bronze** | Row count >= source, latest data date | `_op` distribution (I/U/D), file count |
| **Silver** | Row count <= Bronze, critical field NULL < 1%, ID unique | LEFT JOIN match rate, value range, type conversion success rate |
| **Gold** | Aggregation results non-null, metrics >= 0 | Period-over-period change < 20%, TOP N results reasonable |

---

## Integrating with Alerts

```sql
-- Query all FAIL checks
SELECT * FROM dqc.dqc_results WHERE status = 'FAIL';

-- Query anomaly summary for the current check run
SELECT layer,
    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) AS fails,
    SUM(CASE WHEN status = 'WARN' THEN 1 ELSE 0 END) AS warns
FROM dqc.dqc_results
WHERE checked_at > CURRENT_TIMESTAMP() - INTERVAL 1 DAY
GROUP BY layer
HAVING SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) > 0;
```

You can configure in Studio: any FAIL in DQC task results → trigger WeCom/DingTalk/Feishu notification.

---

## Notes

| Note | Description |
|---|---|
| **DQC results table should be a regular table** | Retaining historical records enables trend analysis; DTs overwrite history |
| **WARN does not block, FAIL should block** | WARN means "needs attention"; FAIL means "cannot be published" |
| **DQC checks have their own cost** | Each check is a full table scan; keep the number of checks manageable (3-5 per layer recommended) |
| **Thresholds need business calibration** | NULL tolerance varies across business domains; use historical data to establish a baseline first |
| **Mind the timezone in freshness checks** | `CURRENT_TIMESTAMP()` is UTC, which may differ from the business timezone |

---

## Related Documentation

- [Medallion Pure-SQL DT Architecture](lakehouse-medallion-sql-dt-guide.md) — Bronze → Silver → Gold three-layer modeling
- [Volume + Pipe Data Lake Acceleration](lakehouse-volume-pipe-acceleration-guide.md) — Data ingestion pipeline
- [AI-Enhanced Data Analysis](lakehouse-ai-sql-analysis.md) — Calling LLMs in SQL for intelligent analysis
- [Studio Task Scheduling](task_scheduling.md) — DQC task Cron configuration
- [Monitoring and Alerting](monitoring_and_alerting.md) — Configuring DQC anomaly notifications
