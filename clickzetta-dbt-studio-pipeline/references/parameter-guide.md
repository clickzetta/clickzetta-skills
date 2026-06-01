# Studio Task Parameter Configuration Guide

## Parameter Types

| Type | Syntax | Example | Description |
|---|---|---|---|
| Static parameter | `{"key": "value"}` | `{"city": "beijing"}` | Fixed value, same on every execution |
| System date parameter | `{"key": "bizdate"}` | `{"dt": "bizdate"}` | Business date automatically injected at scheduling time |
| Expression parameter | `{"key": "$[expr]"}` | `{"yesterday": "$[yyyy-MM-dd,-1d]"}` | Dynamically computed at execution time |

## System Parameter List

| Parameter Name | Meaning | Example Value |
|---|---|---|
| `bizdate` | Business date (scheduling date T-1) | `2024-01-15` |
| `sys_biz_day` | System business day | `20240115` |
| `sys_plan_day` | System plan day | `20240116` |

## Expression Parameter Syntax

```
$[format_string, offset]

Formats:
  yyyy-MM-dd        → 2024-01-15
  yyyyMMdd          → 20240115
  yyyy-MM-dd HH:mm  → 2024-01-15 00:00

Offsets:
  -1d   → subtract 1 day
  -7d   → subtract 7 days
  -1M   → subtract 1 month
  +1d   → add 1 day
```

Examples:
```
$[yyyy-MM-dd,-1d]     → yesterday, e.g. 2024-01-14
$[yyyyMMdd,-7d]       → 7 days ago, e.g. 20240108
$[yyyy-MM-01,-1M]     → first day of last month, e.g. 2024-01-01
```

## Parameter References in SQL

```sql
-- Reference parameters using ${param_name}
SELECT *
FROM orders
WHERE dt = '${bizdate}'
  AND region = '${city}'

-- Date range
WHERE dt BETWEEN '${start_date}' AND '${end_date}'
```

## save-content Parameter Configuration

```bash
# Single system parameter
cz-cli task save-content my_task \
  --content "SELECT * FROM orders WHERE dt = '\${bizdate}'" \
  --params '{"bizdate": "bizdate"}'

# Multiple mixed parameters
cz-cli task save-content my_task \
  --content "..." \
  --params '{
    "bizdate": "bizdate",
    "yesterday": "$[yyyy-MM-dd,-1d]",
    "region": "shanghai"
  }'

# Read SQL from file
cz-cli task save-content my_task \
  --file my_query.sql \
  --params '{"bizdate": "bizdate"}'
```

## Overriding Parameters at execute Time

```bash
# Specify a concrete date for trial runs (validate historical data)
cz-cli task execute my_task \
  --param bizdate=2024-01-01 \
  --param region=beijing \
  --max-wait-seconds 300

# Override SQL content (temporary debugging)
cz-cli task execute my_task \
  --content "SELECT COUNT(*) FROM orders WHERE dt = '\${bizdate}'" \
  --param bizdate=2024-01-01
```

## dbt Incremental SQL Parameterization Rules

| dbt Compiled SQL Pattern | Studio Handling | params Configuration |
|---|---|---|
| `WHERE updated_at > (SELECT MAX(...))` | Keep as-is (self-driving) | No parameters needed |
| `WHERE dt = current_date() - 1` | Replace with `WHERE dt = '${bizdate}'` | `{"bizdate": "bizdate"}` |
| `WHERE dt = '2024-01-01'` (hardcoded) | Replace with `WHERE dt = '${bizdate}'` | `{"bizdate": "bizdate"}` |
| `WHERE dt BETWEEN ... AND ...` | Replace with `WHERE dt = '${bizdate}'` | `{"bizdate": "bizdate"}` |
| No date filter (full load) | Use static SQL directly | No parameters needed |

## Backfill Operations

```bash
# Backfill historical data for a specified date range
# Warning: irreversible — confirm the date range before executing
cz-cli runs refill fct_orders_daily \
  --from "2024-01-01T00:00:00" \
  --to "2024-01-31T23:59:59"

# Add -y to skip confirmation prompt (for use in automation scripts)
cz-cli runs refill fct_orders_daily \
  --from "2024-01-01T00:00:00" \
  --to "2024-01-31T23:59:59" \
  -y
```
