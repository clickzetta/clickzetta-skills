# Studio Module Details

> Source: https://www.yunqi.tech/documents/LakehouseStudioTour and other official documentation

---

## Complete Task Type List

| Task Type | Trigger | VCluster | Typical Use |
|---|---|---|---|
| SQL Task | Scheduled / Manual | GP or AP | ETL, Ad-Hoc queries, DDL operations |
| Python Task | Scheduled / Manual | None | ZettaPark data processing, file operations |
| Shell Task | Scheduled / Manual | None | System commands, file processing |
| JDBC Task | Scheduled / Manual | None | Operate MySQL/Hive/ClickHouse, etc. |
| Dynamic Table Task | Wizard-based creation | GP or AP | Declarative incremental computation |
| Offline Sync Task | Scheduled | Integration | Full/incremental batch sync |
| Realtime Sync Task (single table) | Continuous | Integration | Kafka/MySQL/PG realtime write |
| Multi-table Realtime CDC | Continuous | Integration | Full database mirror, sharded table merge |
| Flow Task | Scheduled | Depends on sub-tasks | Wrap multiple tasks for unified scheduling |
| Virtual Node | Scheduled | None | Placeholder node for dependency orchestration |

---

## Task Status Descriptions

| Status | Meaning |
|---|---|
| Published with changes | Task is published to production, but there are local uncommitted changes |
| Published, no changes | Production version matches local version |
| Offline | Task scheduling has been stopped |
| Unpublished | Only in development environment, not released to production |

---

## Scheduling Configuration Key Parameters

### Cron Expression Examples

```
# Run at 2 AM every day
0 2 * * *

# Run every hour
0 * * * *

# Run every 5 minutes
*/5 * * * *

# Run at 1 AM on the 1st of every month
0 1 1 * *
```

### Dependency Strategies

| Strategy | Description | Use Case |
|---|---|---|
| Default | Downstream triggered after upstream's same-day instance completes | Standard ETL pipeline |
| Forward | Downstream triggered by upstream's most recently completed instance | Upstream runs more frequently than downstream |
| Forward-nearest | Downstream triggered by upstream's most recent instance closest in time | High time-alignment requirements |

---

## Built-in Time Functions for Task Parameters

| Expression | Meaning | Example (today: 2024-01-15) |
|---|---|---|
| `$[yyyy-MM-dd]` | Current date | 2024-01-15 |
| `$[yyyy-MM-dd, -1d]` | Yesterday | 2024-01-14 |
| `$[yyyy-MM-dd, +1d]` | Tomorrow | 2024-01-16 |
| `$[yyyyMM]` | Current month | 202401 |
| `$[yyyyMM, -1M]` | Last month | 202312 |
| `$[yyyy-MM-dd HH:mm:ss]` | Current datetime | 2024-01-15 10:30:00 |
| `$[HH:mm:ss]` | Current time (time only) | 10:30:00 |
| `sys_plan_datetime` | Task planned execution time | Built-in system parameter |

---

## Data Quality Six Dimensions

| Dimension | Description | Example Rule |
|---|---|---|
| Completeness | Non-null rate of fields | `user_id` non-null rate ≥ 99% |
| Uniqueness | Primary key / unique key duplicate detection | `order_id` has no duplicates |
| Consistency | Cross-table data consistency | Order table and detail table amounts match |
| Accuracy | Numeric range validity | `age` is between 0 and 150 |
| Validity | Format / enum value legality | `status` is in ['active', 'inactive'] |
| Timeliness | Data update freshness | Data updated before 8 AM every day |

### Trigger Methods

- **Scheduled trigger**: Cron expression, independent of task scheduling
- **Task-bound trigger**: Bound to a SQL/sync task, quality check auto-triggers after task completes
- **Manual trigger**: Execute manually in the Studio UI

---

## Data Catalog Features

### Table Detail Page Six Tabs

| Tab | Content |
|---|---|
| Details | DDL statement (one-click copy), permission management entry |
| Fields | Column name / type / description / primary key / standardized tags |
| Preview | 100-row data preview (requires SELECT permission + specified VCluster) |
| Lineage | Upstream/downstream table relationship graph (data lineage) |
| Jobs | Query history related to this table |
| Upload | Upload local files directly to the table |

### Search Filter Conditions

- Object type: Table / View / Materialized View
- Workspace / Schema
- Creation time range
- Owner

---

## Operations Monitoring Alerts

### Built-in Alert Rules

| Rule | Trigger Condition |
|---|---|
| Scheduled task instance failure | Task instance execution failed |
| Data quality check failure | Quality rule validation failed |
| Pipe delay alert | Kafka/OSS Pipe consumption delay exceeds threshold |
| Sync task failure | Offline/realtime sync task error |
| Custom rule | User-defined SQL condition |

### Alert Notification Channels

- Lark webhook
- WeCom (Enterprise WeChat) webhook
- Email (some versions)

---

## Data Sync Supported Data Sources (partial)

### Offline Sync (Batch)

MySQL · PostgreSQL · SQL Server · Oracle · Aurora · PolarDB · ClickHouse · Hive · HDFS · OSS/S3/COS · Lakehouse

### Realtime Sync (CDC)

MySQL (Binlog) · PostgreSQL (WAL) · Kafka (JSON/Avro/CSV)

### Connection Methods

- Public network direct connection
- SSH Tunnel (connect to databases in VPC)
- Private network connection (PrivateLink)

---

## Using Data Sources in Python Tasks

Studio Python tasks have the built-in `clickzetta-dbutils` package, which allows direct use of pre-configured data sources:

```python
from clickzetta import dbutils

# Use a pre-configured Lakehouse data source
conn = dbutils.get_connection('my_lakehouse_datasource')
cursor = conn.cursor()
cursor.execute("SELECT * FROM my_schema.my_table LIMIT 10")
rows = cursor.fetchall()
print(rows)

# Use a pre-configured MySQL data source
mysql_conn = dbutils.get_connection('my_mysql_datasource')
```
