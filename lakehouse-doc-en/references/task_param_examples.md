# Task Parameter Examples

This page provides complete usage examples for task parameters in common business scenarios, including SQL task and Python task examples, plus a FAQ.

> ⚠️ **Note**: The parameter feature is currently in limited rollout and is only available to select users. See the verification method in [Task Parameters](task_param.md#appendix-how-to-verify-full-parameter-support).

## Scenario Examples

### Scenario 1: Processing yesterday's partition data

**Requirement**: Process the previous day's order data every morning.

```sql
INSERT OVERWRITE TABLE order_summary PARTITION(dt='${yesterday}')
SELECT
    order_id,
    SUM(amount)  AS total_amount,
    COUNT(*)     AS order_count
FROM order_detail
WHERE dt = '${yesterday}'
GROUP BY order_id;
```

**Parameter configuration**: `yesterday` = `$[yyyy-MM-dd, -1d]`

If the task runs on 2023-09-22, `${yesterday}` is substituted with `2023-09-21`.

---

### Scenario 2: Generating a monthly report (last month's data)

**Requirement**: Generate last month's sales report on the 1st of each month.

```sql
SELECT
    product_id,
    SUM(sales_amount)       AS total_sales,
    COUNT(DISTINCT user_id) AS unique_users
FROM sales_table
WHERE dt BETWEEN '${last_month_start}' AND '${last_month_end}'
GROUP BY product_id;
```

**Parameter configuration**:
- `last_month_start` = `first_day_of_month('yyyy-MM-dd', '-1mon')`
- `last_month_end` = `last_day_of_month('yyyy-MM-dd', '-1mon')`

If the task runs on 2023-09-01: `last_month_start` → `2023-08-01`, `last_month_end` → `2023-08-31`.

---

### Scenario 3: Weekly report (last Monday through Sunday)

**Requirement**: Generate last week's user activity report every Monday.

```sql
SELECT
    DATE(login_time)        AS login_date,
    COUNT(DISTINCT user_id) AS active_users
FROM user_login_log
WHERE dt BETWEEN '${last_week_monday}' AND '${last_week_sunday}'
GROUP BY DATE(login_time)
ORDER BY login_date;
```

**Parameter configuration**:
- `last_week_monday` = `first_day_of_week('yyyy-MM-dd', '-1w')`
- `last_week_sunday` = `last_day_of_week('yyyy-MM-dd', '-1w')`

If the task runs on 2023-09-25 (Monday): `last_week_monday` → `2023-09-18`, `last_week_sunday` → `2023-09-24`.

---

### Scenario 4: Getting every Tuesday's data

**Requirement**: Periodically analyze Tuesday promotion performance.

```sql
SELECT
    promotion_id,
    SUM(sales_amount) AS tuesday_sales
FROM sales_table
WHERE dt = '${this_tuesday}'
GROUP BY promotion_id;
```

**Parameter configuration**: `this_tuesday` = `get_day_of_week('yyyy-MM-dd', 2)`

- Task runs on 2023-09-22 (Friday) → `2023-09-19` (this Tuesday)
- Task runs on 2023-09-25 (Monday) → `2023-09-26` (this Tuesday)

---

### Scenario 5: Timestamp range query (full-day data)

**Requirement**: Query order data from today 00:00:00 to tomorrow 00:00:00.

```sql
SELECT
    order_id,
    order_time,
    amount
FROM orders
WHERE order_timestamp >= ${today_start}
  AND order_timestamp <  ${tomorrow_start};
```

**Parameter configuration**:
- `today_start` = `biz_timestamp()`
- `tomorrow_start` = `biz_timestamp(1d)`

If the task runs on 2023-09-22: `today_start` → `1695312000000`, `tomorrow_start` → `1695398400000`.

---

### Scenario 6: Using parameters in a Python task

```python
```

String-type parameters need quotes:

```python
yesterday  = '${yesterday}'
task_name  = '${task_name}'

```

Numeric-type parameters do not need quotes:

```python
start_ts   = ${start_ts}

print(f"Processing date: {yesterday}")
print(f"Start timestamp: {start_ts}")

sql = f"""
    SELECT * FROM orders
    WHERE dt = '{yesterday}'
      AND create_time >= {start_ts}
"""
```

**Parameter configuration**:
- `yesterday` = `$[yyyy-MM-dd, -1d]`
- `start_ts` = `biz_timestamp()`
- `task_name` = `sys_task_name`

---

## FAQ

### Q1: What is the difference between manual run and scheduled run parameters?

| Dimension | Manual run | Scheduled run |
| ---- | ---- | ---- |
| Parameter source | Entered manually in the dialog | Values from the saved parameter configuration |
| Scope | This run only | Every scheduled execution |
| Time reference | The moment you click Run | The scheduled plan time |
| `sys_task_*` parameters | Not supported | Supported |
| Use case | Debugging, validation | Automated production runs |

Parameter values entered during a manual run are **not saved** to the parameter configuration.

### Q2: How do I verify that my parameter configuration is correct?

Run the following in a SQL task to see the substituted result directly:

```sql
SELECT '${yesterday}' AS yesterday;
-- Parameter config: yesterday = $[yyyy-MM-dd, -1d]
-- If it returns yesterday's date, the configuration is correct
```

You can also check the execution log to view the actual SQL that ran and confirm the parameters were substituted correctly.

### Q3: How do I handle end-of-month date offset issues?

`$[yyyy-MM-dd, -1mon]` can be ambiguous at month-end (e.g., January 31 minus 1 month). When you specifically need the last day of the previous month, use `last_day_of_month()`:

```sql
-- Recommended: explicitly get the last day of the previous month
last_month_end = last_day_of_month('yyyy-MM-dd', '-1mon')
-- Always returns the last day of the previous month, regardless of the current month's length
```

### Q4: How do I debug complex parameter expressions?

Validate step by step, from simple to complex:

```sql
-- Step 1: verify the basic format
SELECT '${base_date}' AS base_date;
-- base_date = $[yyyy-MM-dd]

-- Step 2: add an offset
SELECT '${offset_date}' AS offset_date;
-- offset_date = $[yyyy-MM-dd, -1mon]

-- Step 3: add multiple offsets
SELECT '${final_date}' AS final_date;
-- final_date = $[yyyy-MM-dd, -1mon, -7d]
```

### Q5: How do I modify an encrypted parameter?

1. Open the parameter configuration and find the encrypted parameter.
2. Uncheck "Encrypt value" — the value is displayed in plain text.
3. Make your changes, then re-check "Encrypt value".

Encryption only affects how the value is displayed; it does not affect how the parameter is substituted at runtime.

---

## Related Documentation

- [Task Parameters](task_param.md) — concepts, quick start, parameter types
- [Task Parameter Syntax Reference](task_param_reference.md) — complete syntax for built-in parameters, time expressions, and time functions
- [Task Development and Scheduling](task-develop.md) — creating and scheduling SQL tasks in Studio
- [Workflow (Composite Task)](composite_task.md) — orchestrate multiple parameterized tasks into a DAG
