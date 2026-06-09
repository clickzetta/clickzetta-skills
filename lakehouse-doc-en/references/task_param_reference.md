# Task Parameter Syntax Reference

This page is the complete syntax reference for task parameters, covering system built-in parameters, time expressions, and built-in time functions in detail.

> ⚠️ **Note**: The parameter feature is currently in limited rollout and is only available to select users. See the verification method in [Task Parameters](task_param.md#appendix-how-to-verify-full-parameter-support).

## System Built-in Parameters

The system provides a set of commonly used parameters that you can use directly for parameter assignment — no manual calculation needed.

> ⚠️ Built-in parameters **cannot be referenced directly in code**. You must first assign them to a custom parameter in the parameter configuration, then reference the custom parameter in your code.

### Date and Time Parameters

| Parameter name       | Format               | Description                                | Example (reference time: 2023-09-22 18:00:00) |
| -------------------- | -------------------- | ------------------------------------------ | --------------------------------------------- |
| `bizdate`            | yyyyMMdd             | Business date (scheduled time minus 1 day) | 20230921                                      |
| `sys_biz_day`        | yyyy-MM-dd           | Business date                              | 2023-09-21                                    |
| `sys_biz_datetime`   | yyyy-MM-dd HH\:mm:ss | Business datetime                          | 2023-09-21 18:00:00                           |
| `sys_plan_day`       | yyyy-MM-dd           | Scheduled date                             | 2023-09-22                                    |
| `sys_plan_datetime`  | yyyy-MM-dd HH\:mm:ss | Scheduled datetime                         | 2023-09-22 18:00:00                           |
| `sys_plan_timestamp` | 13-digit timestamp   | Scheduled timestamp (milliseconds)         | 1695463200000                                 |

### Task Information Parameters

| Parameter name   | Description | Example    | Notes              |
| ---------------- | ----------- | ---------- | ------------------ |
| `sys_task_id`    | Task ID     | 1002       | Scheduled run only |
| `sys_task_name`  | Task name   | demo\_task | Scheduled run only |
| `sys_task_owner` | Task owner  | UAT\_TEST  | Scheduled run only |

### Usage Examples

```sql
-- Filter partitions by business date
SELECT * FROM table WHERE dt = '${dt}';
-- Parameter config: dt = sys_biz_day
-- Scheduled time 2023-09-22, actual execution: WHERE dt = '2023-09-21'

-- Use the scheduled timestamp
SELECT * FROM table WHERE create_time >= ${start_ts};
-- Parameter config: start_ts = sys_plan_timestamp
-- Result: WHERE create_time >= 1695463200000
```

### Usage Recommendations

* **Business date scenarios**: prefer `bizdate` or `sys_biz_day`
* **When hours, minutes, and seconds are needed**: use `sys_biz_datetime` or `sys_plan_datetime`
* **Timestamp calculations**: use `sys_plan_timestamp`
* **Audit logging**: use the `sys_task_*` parameters to record task information

***

## Time Expressions

Time expressions support flexible time formatting and offset calculations and are the core feature of the parameter system.

### Basic Syntax

```Plain
$[time_format]                    # Basic formatting
$[time_format, offset]             # With offset
$[time_format, offset1, offset2, ...]  # Multiple offsets (applied in sequence)
```

### Time Format Elements

Time expressions follow the **ISO-8601 standard** and are strictly case-sensitive.

| Element | Meaning                 | Example |
| ------- | ----------------------- | ------- |
| `yyyy`  | Four-digit year         | 2023    |
| `yy`    | Two-digit year          | 23      |
| `MM`    | Two-digit month (01-12) | 09      |
| `dd`    | Two-digit day (01-31)   | 22      |
| `HH`    | 24-hour hour (00-23)    | 18      |
| `mm`    | Minute (00-59)          | 59      |
| `ss`    | Second (00-59)          | 49      |
| `.SSS`  | Millisecond             | 0.377   |
| `ZZ`    | Time zone               | +08:00  |

> ⚠️ Common mistakes: `YYYY` (uppercase Y is not supported), `yyyy-mm-dd` (lowercase m is minute, not month), `hh` (lowercase h is 12-hour format). Correct form: `yyyy-MM-dd HH:mm:ss`.

### Common Format Combinations

```sql
$[yyyy-MM-dd]                → 2023-09-22
$[yyyyMMdd]                  → 20230922
$[yyyy/MM/dd]                → 2023/09/22
$[yyyy-MM-dd HH:mm:ss]       → 2023-09-22 18:00:00
$[yyyyMMddHHmmss]            → 20230922180000
$[HH:mm:ss]                  → 18:00:00
$[yyyy-MM-dd HH:mm:ss.SSSZZ] → 2023-09-22 18:00:00.377+08:00
```

### Time Offsets

| Unit        | Abbreviation | Full name         | Example |
| ----------- | ------------ | ----------------- | ------- |
| Millisecond | ms           | milli/millisecond | 400ms   |
| Second      | s            | sec/second        | 30s     |
| Minute      | m            | min/minute        | 15m     |
| Hour        | h            | hour              | 2h      |
| Day         | d            | day               | -1d     |
| Week        | w            | week              | -1w     |
| Month       | mon          | month             | -1mon   |
| Year        | y            | year              | -1y     |

### Offset Examples

```sql
$[yyyy-MM-dd, -1d]              → Yesterday
$[yyyy-MM-dd, 1d]               → Tomorrow
$[yyyy-MM-dd, -1mon]            → Same day last month
$[yyyy-MM-dd, -1y]              → Same day last year
$[HH:mm:ss, -1h]                → 1 hour ago

-- Multiple offsets (applied in sequence)
$[yyyy-MM-dd, -1y, -1mon, -1d]  → Last year, last month, yesterday
$[yyyyMMdd, 1mon, -7d]          → Next month minus 7 days
```

***

## Built-in Time Functions

These handle calculation scenarios that time expressions cannot express directly, such as "first day of this month" or "last Sunday."

### Month Functions

#### `first_day_of_month()` — First day of the current month

```Plain
first_day_of_month()                     # Default format yyyy-MM-dd
first_day_of_month(format)               # Specify format
first_day_of_month(format, duration)     # With offset
```

```sql
-- First day of the current month
month_start = first_day_of_month()              → 2023-09-01

-- First day of last month
last_month_start = first_day_of_month('yyyy-MM-dd', '-1mon')  → 2023-08-01

-- Custom format
month_start = first_day_of_month('yyyyMMdd')    → 20230901
```

#### `last_day_of_month()` — Last day of the current month

```Plain
last_day_of_month()                      # Default format yyyy-MM-dd
last_day_of_month(format)                # Specify format
last_day_of_month(format, duration)      # With offset
```

```sql
-- Last day of the current month
month_end = last_day_of_month()                          → 2023-09-30

-- Last day of last month
last_month_end = last_day_of_month('yyyy-MM-dd', '-1mon') → 2023-08-31
```

### Week Functions

> Monday is the first day of the week and Sunday is the last day.

#### `first_day_of_week()` — First day of the current week (Monday)

```Plain
first_day_of_week()                      # Default format yyyy-MM-dd
first_day_of_week(format)                # Specify format
first_day_of_week(format, duration)      # With offset
```

```sql
-- This Monday (assuming current date is 2023-09-22, Friday)
week_start = first_day_of_week()                         → 2023-09-18

-- Last Monday
last_week_start = first_day_of_week('yyyy-MM-dd', '-1w') → 2023-09-11
```

#### `last_day_of_week()` — Last day of the current week (Sunday)

```Plain
last_day_of_week()                       # Default format yyyy-MM-dd
last_day_of_week(format)                 # Specify format
last_day_of_week(format, duration)       # With offset
```

```sql
-- This Sunday
week_end = last_day_of_week()                            → 2023-09-24

-- Last Sunday
last_week_end = last_day_of_week('yyyy-MM-dd', '-1w')    → 2023-09-17
```

#### `day_of_week()` — Returns the day of the week

```Plain
day_of_week()           # Today's day of the week (returns 1-7, 1=Monday, 7=Sunday)
day_of_week(duration)   # Day of the week after offset
```

```sql
weekday = day_of_week()      → 5 (Friday)
weekday = day_of_week('-1d') → 4 (yesterday was Thursday)
```

#### `get_day_of_week()` — Get the date of a specific day of the week

```Plain
get_day_of_week(format, whichDay)           # That day of the current week (1=Monday, 7=Sunday)
get_day_of_week(format, whichDay, duration) # That day of the offset week
```

```sql
-- This Tuesday (assuming current date is 2023-09-22, Friday)
this_tuesday = get_day_of_week('yyyy-MM-dd', 2)          → 2023-09-19

-- Last Wednesday
last_wednesday = get_day_of_week('yyyy-MM-dd', 3, '-1w') → 2023-09-13

-- Next Friday
next_friday = get_day_of_week('yyyy-MM-dd', 5, '1w')     → 2023-09-29
```

#### `week_of_month()` — Week number within the current month

```Plain
week_of_month()           # Which week of the month today falls in (returns integer)
week_of_month(duration)   # Which week of the month after offset
```

#### `week_of_year()` — Week number within the current year

```Plain
week_of_year()            # Which week of the year today falls in (returns integer)
week_of_year(duration)    # Which week of the year after offset
```

### Timestamp Functions

#### `timestamp()` — Millisecond timestamp

```Plain
timestamp()                      # Millisecond timestamp of the current scheduled time (13 digits)
timestamp(offset1, offset2, ...) # With offsets
```

```sql
current_ts   = timestamp()    → 1695463200000 (2023-09-22 18:00:00)
yesterday_ts = timestamp(-1d) → 1695376800000
```

#### `biz_timestamp()` — Business timestamp (based on 00:00:00)

```Plain
biz_timestamp()                      # Millisecond timestamp of today at 00:00:00 (13 digits)
biz_timestamp(offset1, offset2, ...) # With offsets
```

```sql
today_start     = biz_timestamp()    → 1695312000000 (2023-09-22 00:00:00)
yesterday_start = biz_timestamp(-1d) → 1695225600000
```

***

## Quick Reference

### Common Time Requirements

| Requirement              | Parameter configuration                     | Example result (reference: 2023-09-22) |
| ------------------------ | ------------------------------------------- | -------------------------------------- |
| Today                    | `$[yyyy-MM-dd]` or `sys_plan_day`           | 2023-09-22                             |
| Yesterday                | `$[yyyy-MM-dd, -1d]` or `sys_biz_day`       | 2023-09-21                             |
| Same day last week       | `$[yyyy-MM-dd, -7d]`                        | 2023-09-15                             |
| Same day last month      | `$[yyyy-MM-dd, -1mon]`                      | 2023-08-22                             |
| First day of this month  | `first_day_of_month()`                      | 2023-09-01                             |
| Last day of this month   | `last_day_of_month()`                       | 2023-09-30                             |
| First day of last month  | `first_day_of_month('yyyy-MM-dd', '-1mon')` | 2023-08-01                             |
| Last day of last month   | `last_day_of_month('yyyy-MM-dd', '-1mon')`  | 2023-08-31                             |
| This Monday              | `first_day_of_week()`                       | 2023-09-18                             |
| This Sunday              | `last_day_of_week()`                        | 2023-09-24                             |
| Last Monday              | `first_day_of_week('yyyy-MM-dd', '-1w')`    | 2023-09-11                             |
| Last Sunday              | `last_day_of_week('yyyy-MM-dd', '-1w')`     | 2023-09-17                             |
| This Tuesday             | `get_day_of_week('yyyy-MM-dd', 2)`          | 2023-09-19                             |
| Last year yesterday      | `$[yyyy-MM-dd, -1y, -1d]`                   | 2022-09-21                             |
| Today at 00:00 timestamp | `biz_timestamp()`                           | 1695312000000                          |
| Current timestamp        | `timestamp()`                               | 1695463200000                          |

### Time Function Quick Reference

| Function               | Purpose                                         | Return type      |
| ---------------------- | ----------------------------------------------- | ---------------- |
| `first_day_of_month()` | First day of the current month                  | Date string      |
| `last_day_of_month()`  | Last day of the current month                   | Date string      |
| `first_day_of_week()`  | First day of the current week (Monday)          | Date string      |
| `last_day_of_week()`   | Last day of the current week (Sunday)           | Date string      |
| `day_of_week()`        | Day of the week (1-7)                           | Integer          |
| `week_of_month()`      | Week number within the current month            | Integer          |
| `week_of_year()`       | Week number within the current year             | Integer          |
| `get_day_of_week()`    | Date of a specific day of the week              | Date string      |
| `timestamp()`          | Millisecond timestamp (based on scheduled time) | 13-digit integer |
| `biz_timestamp()`      | Millisecond timestamp (based on 00:00:00)       | 13-digit integer |
| `unix_timestamp()`     | Second timestamp                                | 10-digit integer |
| `biz_unix_timestamp()` | Business second timestamp                       | 10-digit integer |
| `biz_format()`         | Business time formatting                        | String           |

***

## Related Documentation

* [Task Parameters](task_param.md) — concepts, quick start, parameter types
* [Task Parameter Examples](task_param_examples.md) — complete business scenarios for daily, monthly, and weekly reports
* [Task Development and Scheduling](task-develop.md) — creating and scheduling SQL tasks in Studio

^
