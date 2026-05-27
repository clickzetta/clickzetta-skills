# Task Parameters

> Special Note: The parameter feature is currently in the grayscale stage, and the complete functionality is only available to some customers. You can use the method at the end of this document to verify if it is supported.

## What Are Task Parameters

### Why Do We Need Parameters?

In daily data development, we often encounter scenarios like these:

* Processing the previous day's data each day: `WHERE dt = '2023-09-21'`
* Generating monthly statistics for the previous month: `WHERE month = '2023-08'`
* Querying data for a specific city: `WHERE city = 'Shanghai'`

If dates, cities, and other information are hardcoded, the task cannot dynamically adapt to changes at runtime. **Task parameters** are designed to solve this problem.

### Core Value of Parameters

* **Dynamic replacement**: Automatically replace parameter values when the task runs.
* **Flexible configuration**: Supports constants, time expressions, and system parameters.
* **High reusability**: Define once, use in multiple places.
* **Easy maintenance**: Modify parameters without changing code logic.

### Basic Concepts

| Category           | Concept Name                  | Meaning                                                                                                                                                                                          | Illustration                         |
| ------------------ | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------ |
| Parameter Definition | Custom Parameter              | Refers to parameters that users define and reference in the code. The format is fixed as `${custom parameter name}`.                                                                             | ${my\_param}                         |
| Parameter Assignment | Constant                      | Refers to fixed values, such as strings and numbers, used to assign values to custom parameters.                                                                                                  | abcd or 1234                         |
| Parameter Assignment | System Built-in Parameter     | Refers to a series of parameter expressions built into the system to help users obtain dynamic information that requires calculation, such as the scheduled time of a task instance.              | sys\_plan\_datetime                  |
| Parameter Assignment | System Built-in Time Function | Refers to a series of function expressions built into the system for performing common time conversion calculations.                                                                             | add\_months(yyyy-MM-dd HH\:mm\:ss,N) |

## Quick Start

### Three Steps to Get Started

**Step 1: Use parameters in your code**

```SQL
SELECT * FROM sales_table WHERE city = '${city}' AND dt = '${yesterday}';
```

**Step 2: Configure parameter values**
Click the "Parameters" button, and the system will automatically recognize the two parameters `city` and `yesterday` and allow you to assign values to them:

* `city` = `Shanghai`
* `yesterday` = `$[yyyy-MM-dd, -1d]`

**Step 3: Run and verify**
Click "Run", and the system will replace the parameters and execute:

```SQL
SELECT * FROM sales_table WHERE city = 'Shanghai' AND dt = '2023-09-21';  

-- Assuming today is 2023-09-22
```

### Key Points

* The parameter format is fixed as: `${parameter name}`.
* Parameter names can only contain letters, digits, and underscores.
* Parameters should be defined using built-in parameters or time expressions for assignment, and then referenced in code. Built-in parameters cannot be directly referenced in code.
* During parameter replacement, only the content inside `${}` is replaced.
* If you need quotes in SQL, you must add them yourself, e.g.: `'${city}'`.

## Parameter Types and Scope

The system provides two parameter types, supporting different usage scenarios:

### Task Parameters

**Characteristics**:

* Scope: Current task only
* Use case: Task-specific configuration

**Applicable situations**:

* Parameters unique to a single task
* Scenarios requiring fine-grained control
* Temporary parameter configurations

**Creation methods**:
Method 1: Enter `${custom parameter}` in the script, and the system will automatically add the custom parameter to the "Parameters" dialog.
Method 2: Click the "Parameters" button and enter information in the dialog.

![](.topwrite/assets/image_1740658949338.png =700)

| Configuration Item | Description                       | Example                                            |
| ------------------ | --------------------------------- | -------------------------------------------------- |
| Parameter Name     | Unique identifier for the parameter | city, yesterday                                   |
| Value Source       | Choose "Task" or "Task Group"     | Task                                                |
| Parameter Value    | The actual value of the parameter | Shanghai, $\[yyyy-MM-dd, -1d]                       |
| Encrypt Value      | When checked, the value is displayed as ciphertext | For sensitive information such as passwords         |
| Ignore             | When checked, parameter replacement is skipped | Treats ${var} as plain text                         |

**Example**:
```SQL
-- Use in a specific task

SELECT * FROM table WHERE status = '${task_status}';
```

### Task Group Parameters

**Characteristics**:

* Scope: All tasks within the task group
* Use case: Configuration shared across multiple tasks

**Applicable situations**:

* Parameters shared by multiple tasks (e.g., project code, environment identifier)
* Global configurations (e.g., database name)
* Parameters that need unified management

**Creation method**:
On the task group page, click "Parameters", then click "New" in the dialog, and fill in the parameter name and value.

![](/.topwrite/assets/image_1760699887513.png =680)

If you want to use a task group parameter in a specific task, you need to explicitly switch the value source in the task parameter definition to indicate that the parameter value comes from the task group.

![](/.topwrite/assets/image_1760699557999.png =680)

**Example**:
```SQL
-- Task group parameter: db_name = warehouse_prod

-- Task A
SELECT * FROM ${db_name}.table_a;

-- Task B
SELECT * FROM ${db_name}.table_b;

-- Both tasks use the same db_name parameter
```

## Two Parameter Configuration Methods

### Method 1: Code-Based Auto-Detection

Enter `${parameter name}` directly in the script, and the system will automatically detect and add it to the parameter list.

**Advantages**: Quick, intuitive, less prone to parameter name typos.
```SQL
-- Enter the following code
SELECT * FROM table WHERE city = '${city}' AND dt = '${dt}';
-- System automatically detects the city and dt parameters
```

### Method 2: Manual Creation Before Use

Click the "Parameters" button, then click "New" in the dialog, and manually enter parameter information.

**Advantages**: Parameters can be predefined, suitable for well-planned scenarios.

## Parameter Effects Under Different Run Modes

### Ad-Hoc Run (Clicking the "Run" Button)

* A dialog prompts you to enter parameter values

  ![](/.topwrite/assets/image_1761284431760.png =680)

* Takes effect only for this run, does not affect saved parameter configurations

* Suitable for debugging and verification

### Scheduled Run (Automatic Scheduled Execution)

* Uses saved parameter configurations
* Dynamically calculates parameter values based on the schedule time
* Suitable for production environments

## System Built-in Parameters

The system provides a set of commonly used parameters that can be directly used for parameter assignment without manual calculation.

Please note that built-in parameters cannot be directly referenced in code.

### Date and Time Parameters

| Parameter Name       | Format                    | Description                                       | Example (Reference time 2023-09-22 18:00:00) |
| -------------------- | ------------------------- | ------------------------------------------------- | -------------------------------------------- |
| bizdate              | yyyyMMdd                  | Business date (scheduled time - 1 day)            | 20230921                                     |
| sys\_biz\_day        | yyyy-MM-dd                | Business date                                     | 2023-09-21                                   |
| sys\_biz\_datetime   | yyyy-MM-dd HH\:mm\:ss     | Business datetime                                 | 2023-09-21 18:00:00                          |
| sys\_plan\_day       | yyyy-MM-dd                | Scheduled date                                    | 2023-09-22                                   |
| sys\_plan\_datetime  | yyyy-MM-dd HH\:mm\:ss     | Scheduled datetime                                | 2023-09-22 18:00:00                          |
| sys\_plan\_timestamp | 13-digit timestamp        | Scheduled timestamp (milliseconds)                | 1695463200000                                |

### Task Information Parameters

| Parameter Name     | Description     | Example     | Notes                          |
| ------------------ | --------------- | ----------- | ------------------------------ |
| sys\_task\_id      | Task ID         | 1002        | Only supported during scheduled run |
| sys\_task\_name    | Task name       | demo\_task  | Only supported during scheduled run |
| sys\_task\_owner   | Task owner      | UAT\_TEST   | Only supported during scheduled run |

### Usage Examples

```SQL
-- Example 1: Using business date
SELECT * FROM table WHERE dt = '${dt}';
-- Parameter config: dt = sys_biz_day
-- Schedule time 2023-09-22, actual execution: WHERE dt = '2023-09-21'

-- Example 2: Using scheduled timestamp
SELECT * FROM table WHERE create_time >= ${start_ts};
-- Parameter config: start_ts = sys_plan_timestamp
-- Result: WHERE create_time >= 1695463200000

-- Example 3: Using in Python tasks
task_id = '${task_id}'
print(f"Current task ID: {task_id}")
-- Parameter config: task_id = sys_task_id
```

### Usage Suggestions

1. **Business date scenarios**: Prefer `bizdate` or `sys_biz_day`
2. **When hours, minutes, and seconds are needed**: Use `sys_biz_datetime` or `sys_plan_datetime`
3. **Timestamp calculations**: Use `sys_plan_timestamp`
4. **Audit logs**: Use `sys_task_*` series parameters to record task information

***

## Time Expression Details

Time expressions are the core feature of the parameter system, supporting flexible time formatting and offset calculations.

### Basic Syntax

```Plain
$[time format]                    # Basic formatting
$[time format, offset]             # With offset
$[time format, offset1, offset2, ...]  # Multiple offsets
```

### Time Format Elements

Time expressions follow the **ISO-8601 standard** and are strictly case-sensitive.

| Element | Meaning              | Example     |
| ------- | -------------------- | ----------- |
| yyyy    | Four-digit year      | 2023        |
| yy      | Two-digit year       | 23          |
| MM      | Two-digit month (01-12) | 09          |
| dd      | Two-digit day (01-31)   | 22          |
| HH      | 24-hour format hour (00-23) | 18     |
| mm      | Minute (00-59)       | 59          |
| ss      | Second (00-59)       | 49          |
| .SSS    | Millisecond          | 0.377       |
| ZZ      | Time zone            | +08:00      |

### Common Format Combinations

```SQL
$[yyyy-MM-dd]                         → 2023-09-22
$[yyyyMMdd]                           → 20230922
$[yyyy/MM/dd]                         → 2023/09/22
$[yyyy-MM-dd HH:mm:ss]                → 2023-09-22 18:00:00
$[yyyyMMddHHmmss]                     → 20230922180000
$[HH:mm:ss]                           → 18:00:00
$[yyyy-MM-dd HH:mm:ss.SSSZZ]          → 2023-09-22 18:00:00.377+08:00
```

### Common Mistakes

```SQL
❌ $[YYYY-MM-DD]           # Uppercase Y is not supported
❌ $[yyyy-mm-dd]           # Lowercase m is minute, not month
❌ $[yyyy-MM-dd hh:mm:ss]  # Lowercase h is 12-hour format
✅ $[yyyy-MM-dd HH:mm:ss]  # Correct format
```

### Time Offsets

Supports adding and subtracting time using intuitive unit abbreviations.

| Unit        | Abbreviation | Full Name          | Example |
| ----------- | ------------ | ------------------ | ------- |
| Millisecond | ms           | milli/millisecond  | 400ms   |
| Second      | s            | sec/second         | 400s    |
| Minute      | m            | min/minute         | 3m      |
| Hour        | h            | hour               | 1h      |
| Day         | d            | day                | 2d      |
| Month       | mon          | month              | 1mon    |
| Year        | y            | year               | -1y     |

### Offset Examples

```SQL
-- Single offset
$[yyyy-MM-dd, -1d]                           → Yesterday
$[yyyy-MM-dd, 1d]                            → Tomorrow
$[yyyy-MM-dd, -1mon]                         → Same day last month
$[yyyy-MM-dd, -1y]                           → Same day last year
$[HH:mm:ss, -1h]                             → 1 hour ago
$[HH:mm:ss, 30m]                             → 30 minutes later

-- Multiple offsets (calculated in order)
$[yyyy-MM-dd, -1y, -1mon, -1d]               → Last year, last month, yesterday
$[yyyy-MM-dd HH:mm:ss, -1d, -2h, -30m]       → Yesterday minus 2 hours minus 30 minutes
$[yyyyMMdd, 1mon, -7d]                       → Next month minus 7 days
```

### Full Examples

Assuming the current scheduled time is: **2023-09-22 18:30:00**

```SQL
-- Basic format
SELECT '${today}' as today;
-- Parameter config: today = $[yyyy-MM-dd]
-- Result: 2023-09-22

-- Yesterday
SELECT '${yesterday}' as yesterday;
-- Parameter config: yesterday = $[yyyy-MM-dd, -1d]
-- Result: 2023-09-21

-- Same day last month
SELECT '${last_month}' as last_month;
-- Parameter config: last_month = $[yyyy-MM-dd, -1mon]
-- Result: 2023-08-22

-- Last year yesterday
SELECT '${last_year_yesterday}' as last_year_yesterday;
-- Parameter config: last_year_yesterday = $[yyyy-MM-dd, -1y, -1d]
-- Result: 2022-09-21

-- Hours, minutes, seconds
SELECT '${current_time}' as current_time;
-- Parameter config: current_time = $[HH:mm:ss]
-- Result: 18:30:00

-- 1 hour ago
SELECT '${one_hour_ago}' as one_hour_ago;
-- Parameter config: one_hour_ago = $[HH:mm:ss, -1h]
-- Result: 17:30:00
```

***

## Built-in Time Functions

In addition to time expressions, the system also provides a rich set of time functions for handling more complex time calculation scenarios.

### Month-Related Functions

#### `first_day_of_month()` - First Day of the Current Month

**Syntax**:

```Plain
first_day_of_month()                        # Default format yyyy-MM-dd
first_day_of_month(format)                  # Specify format
first_day_of_month(format, duration)        # With offset
```

**Examples**:
```SQL
-- First day of the current month
SELECT '${month_start}' as month_start;
-- Parameter config: month_start = first_day_of_month()
-- Assuming current date is 2023-09-22, result: 2023-09-01

-- First day of last month
SELECT '${last_month_start}' as last_month_start;
-- Parameter config: last_month_start = first_day_of_month('yyyy-MM-dd', '-1mon')
-- Result: 2023-08-01

-- Custom format
SELECT '${month_start_yyyymmdd}' as month_start_yyyymmdd;
-- Parameter config: month_start_yyyymmdd = first_day_of_month('yyyyMMdd')
-- Result: 20230901
```

#### `last_day_of_month()` - Last Day of the Current Month

**Syntax**:

```Plain
last_day_of_month()                         # Default format yyyy-MM-dd
last_day_of_month(format)                   # Specify format
last_day_of_month(format, duration)         # With offset
```

**Examples**:
```SQL
-- Last day of the current month
SELECT '${month_end}' as month_end;
-- Parameter config: month_end = last_day_of_month()
-- Assuming current date is 2023-09-22, result: 2023-09-30

-- Last day of last month
SELECT '${last_month_end}' as last_month_end;
-- Parameter config: last_month_end = last_day_of_month('yyyy-MM-dd', '-1mon')
-- Result: 2023-08-31

-- Used for monthly report statistics
SELECT * FROM table WHERE dt BETWEEN '${month_start}' AND '${month_end}';
-- month_start = first_day_of_month()
-- month_end = last_day_of_month()
```

### Week-Related Functions

In the system, **Monday is the first day of each week, and Sunday is the last day**.

#### `first_day_of_week()` - First Day of the Current Week (Monday)

**Syntax**:

```Plain
first_day_of_week()                         # Default format yyyy-MM-dd
first_day_of_week(format)                   # Specify format
first_day_of_week(format, duration)         # With offset
```

**Examples**:

```SQL
-- This Monday
SELECT '${week_start}' as week_start;
-- Parameter config: week_start = first_day_of_week()
-- Assuming current date is 2023-09-22 (Friday), result: 2023-09-18

-- Last Monday
SELECT '${last_week_start}' as last_week_start;
-- Parameter config: last_week_start = first_day_of_week('yyyy-MM-dd', '-1w')
-- Result: 2023-09-11
```

#### `last_day_of_week()` - Last Day of the Current Week (Sunday)

**Syntax**:

```Plain
last_day_of_week()                          # Default format yyyy-MM-dd
last_day_of_week(format)                    # Specify format
last_day_of_week(format, duration)          # With offset
```

**Examples**:
```SQL
-- This Sunday
SELECT '${week_end}' as week_end;
-- Parameter config: week_end = last_day_of_week()
-- Assuming current date is 2023-09-22 (Friday), result: 2023-09-24

-- Last Sunday
SELECT '${last_week_end}' as last_week_end;
-- Parameter config: last_week_end = last_day_of_week('yyyy-MM-dd', '-1w')
-- Result: 2023-09-17

-- Used for weekly report statistics
SELECT * FROM table WHERE dt BETWEEN '${week_start}' AND '${week_end}';
-- week_start = first_day_of_week()
-- week_end = last_day_of_week()
```

#### `day_of_week()` - Returns the Day of the Week

**Syntax**:

```Plain
day_of_week()                               # Today's day of the week
day_of_week(duration)                       # Day of the week after offset
```

**Return value**: Integer 1-7 (1 = Monday, 7 = Sunday)

**Examples**:
```SQL
-- Check what day of the week today is
SELECT ${weekday} as weekday;
-- Parameter config: weekday = day_of_week()
-- Assuming today is 2023-09-25 (Monday), result: 1

-- What day of the week was yesterday
SELECT ${yesterday_weekday} as yesterday_weekday;
-- Parameter config: yesterday_weekday = day_of_week('-1d')
-- Result: 7 (Sunday)

-- Using in Python
weekday = ${weekday}
if weekday == 1:
    print("Today is Monday")
-- Parameter config: weekday = day_of_week()
```

#### `get_day_of_week()` - Get the Date of a Specific Day of the Week

**Syntax**:

```Plain
get_day_of_week(format, whichDay)                      # Day of week in the current week
get_day_of_week(format, whichDay, duration)            # Day of week in the offset week
```

**Parameter description**:

* `format`: The format of the returned date
* `whichDay`: 1-7, representing Monday to Sunday
* `duration`: Optional, time offset

**Examples**:
```SQL
-- This Tuesday
SELECT '${this_tuesday}' as this_tuesday;
-- Parameter config: this_tuesday = get_day_of_week('yyyy-MM-dd', 2)
-- Assuming current date is 2023-09-22 (Friday), result: 2023-09-19

-- Last Wednesday
SELECT '${last_wednesday}' as last_wednesday;
-- Parameter config: last_wednesday = get_day_of_week('yyyy-MM-dd', 3, '-1w')
-- Result: 2023-09-13

-- Next Friday
SELECT '${next_friday}' as next_friday;
-- Parameter config: next_friday = get_day_of_week('yyyy-MM-dd', 5, '1w')
-- Result: 2023-09-29

-- Tuesday of yesterday's week
SELECT '${tuesday_of_yesterday_week}' as tuesday_of_yesterday_week;
-- Parameter config: tuesday_of_yesterday_week = get_day_of_week('yyyy-MM-dd', 2, '-1d')
-- Assuming today is 2023-09-25 (Monday), yesterday is 2023-09-24 (Sunday), yesterday's week is last week
-- Result: 2023-09-19
```

#### `week_of_month()` - Week of the Current Month

**Syntax**:

```Plain
week_of_month()                             # Which week of the current month today falls in
week_of_month(duration)                     # Which week of the month after offset
```

**Return value**: Integer, representing the week number within the month

**Examples**:
```SQL
-- Which week of the current month is today
SELECT ${week_num} as week_num;
-- Parameter config: week_num = week_of_month()
-- Assuming today is 2023-09-22, result: 4 (4th week)

-- Which week of the month was the same day last month
SELECT ${last_month_week} as last_month_week;
-- Parameter config: last_month_week = week_of_month('-1mon')
```

#### `week_of_year()` - Week of the Current Year

**Syntax**:

```Plain
week_of_year()                              # Which week of the current year today falls in
week_of_year(duration)                      # Which week of the year after offset
```

**Return value**: Integer, representing the week number within the year

**Examples**:
```SQL
-- Which week of the current year is today
SELECT ${week_of_year} as week_of_year;
-- Parameter config: week_of_year = week_of_year()
-- Assuming today is 2023-09-22, result: 38 (38th week)

-- Which week of the year was the same day last year
SELECT ${last_year_week} as last_year_week;
-- Parameter config: last_year_week = week_of_year('-1y')
```

### Timestamp Functions

#### `timestamp()` - Millisecond Timestamp

**Syntax**:

```Plain
timestamp()                                 # Current scheduled timestamp
timestamp(offset1, offset2, ...)            # Timestamp with offsets
```

**Return value**: 13-digit millisecond timestamp

**Examples**:
```SQL
-- Current timestamp
SELECT ${current_ts} as current_ts;
-- Parameter config: current_ts = timestamp()
-- Assuming current time is 2023-09-22 18:00:00, result: 1695463200000

-- Yesterday same time timestamp
SELECT ${yesterday_ts} as yesterday_ts;
-- Parameter config: yesterday_ts = timestamp(-1d)
-- Result: 1695376800000

-- One week ago minus 2 hours timestamp
SELECT ${ts} as ts;
-- Parameter config: ts = timestamp(-1w, -2h)
```

#### `biz_timestamp()` - Business Timestamp (Based on 00:00:00)

**Syntax**:

```Plain
biz_timestamp()                             # Today 00:00:00 timestamp
biz_timestamp(offset1, offset2, ...)        # With offsets
```

**Return value**: 13-digit millisecond timestamp, calculated based on 00:00:00 of the current day

***

## Quick Reference Tables

### Common Time Parameters Quick Reference

| Requirement              | Parameter Configuration                                     | Example Result (Reference 2023-09-22) |
| ------------------------ | ----------------------------------------------------------- | ------------------------------------- |
| Today                    | $\[yyyy-MM-dd] or sys\_plan\_day                            | 2023-09-22                            |
| Yesterday                | $\[yyyy-MM-dd, -1d] or sys\_biz\_day                        | 2023-09-21                            |
| Tomorrow                 | $\[yyyy-MM-dd, 1d]                                          | 2023-09-23                            |
| Same day last week       | $\[yyyy-MM-dd, -7d]                                         | 2023-09-15                            |
| Same day last month      | $\[yyyy-MM-dd, -1mon]                                       | 2023-08-22                            |
| Same day last year       | $\[yyyy-MM-dd, -1y]                                         | 2022-09-22                            |
| First day of this month  | first\_day\_of\_month()                                     | 2023-09-01                            |
| Last day of this month   | last\_day\_of\_month()                                      | 2023-09-30                            |
| First day of last month  | first\_day\_of\_month('yyyy-MM-dd', '-1mon')                | 2023-08-01                            |
| Last day of last month   | last\_day\_of\_month('yyyy-MM-dd', '-1mon')                 | 2023-08-31                            |
| This Monday              | first\_day\_of\_week()                                      | 2023-09-18                            |
| This Sunday              | last\_day\_of\_week()                                       | 2023-09-24                            |
| Last Monday              | first\_day\_of\_week('yyyy-MM-dd', '-1w')                   | 2023-09-11                            |
| Last Sunday              | last\_day\_of\_week('yyyy-MM-dd', '-1w')                    | 2023-09-17                            |
| This Tuesday             | get\_day\_of\_week('yyyy-MM-dd', 2)                         | 2023-09-19                            |
| Last Wednesday           | get\_day\_of\_week('yyyy-MM-dd', 3, '-1w')                  | 2023-09-13                            |
| Last year yesterday      | $\[yyyy-MM-dd, -1y, -1d]                                    | 2022-09-21                            |

### Common Format Quick Reference

| Format Requirement                | Parameter Configuration                | Example Result      |
| --------------------------------- | -------------------------------------- | ------------------- |
| yyyyMMdd                          | $\[yyyyMMdd]                           | 20230922            |
| yyyy-MM-dd                        | $\[yyyy-MM-dd]                         | 2023-09-22          |
| yyyy/MM/dd                        | $\[yyyy/MM/dd]                         | 2023/09/22          |
| yyyyMMddHHmmss                    | $\[yyyyMMddHHmmss]                     | 20230922180000      |
| yyyy-MM-dd HH\:mm\:ss             | $\[yyyy-MM-dd HH\:mm\:ss]              | 2023-09-22 18:00:00 |
| HH\:mm\:ss                        | $\[HH\:mm\:ss]                         | 18:00:00            |
| Millisecond timestamp             | timestamp()                            | 1695463200000       |
| Second timestamp                  | unix\_timestamp()                      | 1695463200          |

### System Parameters Quick Reference

| Parameter Name        | Description                                     | Format                    | Scheduled Run | Ad-Hoc Run |
| --------------------- | ----------------------------------------------- | ------------------------- | ------------- | ---------- |
| bizdate               | Business date (scheduled time - 1 day)          | yyyyMMdd                  | Yes           | Yes        |
| sys\_biz\_day         | Business date                                   | yyyy-MM-dd                | Yes           | Yes        |
| sys\_biz\_datetime    | Business datetime                               | yyyy-MM-dd HH\:mm\:ss     | Yes           | Yes        |
| sys\_plan\_day        | Scheduled date                                  | yyyy-MM-dd                | Yes           | Yes        |
| sys\_plan\_datetime   | Scheduled datetime                              | yyyy-MM-dd HH\:mm\:ss     | Yes           | Yes        |
| sys\_plan\_timestamp  | Scheduled timestamp                             | 13-digit milliseconds     | Yes           | Yes        |
| sys\_task\_id         | Task ID                                         | Integer                   | Yes           | No         |
| sys\_task\_name       | Task name                                       | String                    | Yes           | No         |
| sys\_task\_owner      | Task owner                                      | String                    | Yes           | No         |

### Offset Unit Quick Reference

| Unit        | Abbreviation | Full Name          | Example |
| ----------- | ------------ | ------------------ | ------- |
| Millisecond | ms           | milli/millisecond  | 400ms   |
| Second      | s            | sec/second         | 30s     |
| Minute      | m            | min/minute         | 15m     |
| Hour        | h            | hour               | 2h      |
| Day         | d            | day                | -1d     |
| Week        | w            | week               | -1w     |
| Month       | mon          | month              | -1mon   |
| Year        | y            | year               | -1y     |

### Time Function Quick Reference

| Function                | Functionality                                   | Example                                                       |
| ----------------------- | ----------------------------------------------- | ------------------------------------------------------------- |
| first\_day\_of\_month() | First day of the current month                  | first\_day\_of\_month('yyyy-MM-dd', '-1mon')                  |
| last\_day\_of\_month()  | Last day of the current month                   | last\_day\_of\_month()                                        |
| first\_day\_of\_week()  | First day of the current week (Monday)          | first\_day\_of\_week('yyyy-MM-dd')                            |
| last\_day\_of\_week()   | Last day of the current week (Sunday)           | last\_day\_of\_week()                                         |
| day\_of\_week()         | Returns day of week (1-7)                       | day\_of\_week('-1d')                                          |
| week\_of\_month()       | Week of the current month                       | week\_of\_month()                                             |
| week\_of\_year()        | Week of the current year                        | week\_of\_year()                                              |
| get\_day\_of\_week()    | Get the date of a specific day of the week      | get\_day\_of\_week('yyyy-MM-dd', 2, '-1w')                    |
| timestamp()             | Millisecond timestamp                           | timestamp(-1d)                                                |
| biz\_timestamp()        | Business timestamp (00:00:00)                   | biz\_timestamp(-1d)                                           |
| unix\_timestamp()       | Second timestamp                                | unix\_timestamp()                                             |
| biz\_unix\_timestamp()  | Business second timestamp                       | biz\_unix\_timestamp()                                        |
| biz\_format()           | Business time formatting                        | biz\_format('yyyy-MM-dd', -1d)                                |

***

## Practical Scenario Examples

### Scenario 1: Processing Yesterday's Partition Data

**Requirement**: Process the previous day's order data every morning

```SQL
-- SQL task
INSERT OVERWRITE TABLE order_summary PARTITION(dt='${yesterday}')
SELECT 
    order_id,
    SUM(amount) as total_amount,
    COUNT(*) as order_count
FROM order_detail
WHERE dt = '${yesterday}'
GROUP BY order_id;
```

**Parameter configuration**:

* `yesterday` = `$[yyyy-MM-dd, -1d]`

**Explanation**: Assuming the task runs on 2023-09-22, the parameter is replaced with `2023-09-21`

***

### Scenario 2: Generating Monthly Report (Last Month's Data Statistics)

**Requirement**: Generate the previous month's sales report on the 1st of each month

```SQL
-- SQL task
SELECT 
    product_id,
    SUM(sales_amount) as total_sales,
    COUNT(DISTINCT user_id) as unique_users
FROM sales_table
WHERE dt BETWEEN '${last_month_start}' AND '${last_month_end}'
GROUP BY product_id;
```

**Parameter configuration**:

* `last_month_start` = `first_day_of_month('yyyy-MM-dd', '-1mon')`
* `last_month_end` = `last_day_of_month('yyyy-MM-dd', '-1mon')`

**Explanation**: Assuming execution on 2023-09-01

* `last_month_start` → `2023-08-01`
* `last_month_end` → `2023-08-31`

***

### Scenario 3: Weekly Report Statistics (Last Monday to Sunday)

**Requirement**: Generate last week's user activity report every Monday

```SQL
-- SQL task
SELECT 
    DATE(login_time) as login_date,
    COUNT(DISTINCT user_id) as active_users
FROM user_login_log
WHERE dt BETWEEN '${last_week_monday}' AND '${last_week_sunday}'
GROUP BY DATE(login_time)
ORDER BY login_date;
```

**Parameter configuration**:

* `last_week_monday` = `first_day_of_week('yyyy-MM-dd', '-1w')`
* `last_week_sunday` = `last_day_of_week('yyyy-MM-dd', '-1w')`

**Explanation**: Assuming execution on 2023-09-25 (Monday)

* `last_week_monday` → `2023-09-18` (last Monday)
* `last_week_sunday` → `2023-09-24` (last Sunday)

***

### Scenario 4: Getting Every Tuesday's Data

**Requirement**: Periodically analyze the effect of Tuesday promotions

```SQL
-- SQL task
SELECT 
    promotion_id,
    SUM(sales_amount) as tuesday_sales
FROM sales_table
WHERE dt = '${this_tuesday}'
GROUP BY promotion_id;
```

**Parameter configuration**:

* `this_tuesday` = `get_day_of_week('yyyy-MM-dd', 2)`

**Explanation**:

* If the task runs on 2023-09-22 (Friday) → `2023-09-19` (this Tuesday)
* If the task runs on 2023-09-25 (Monday) → `2023-09-26` (this Tuesday)

***

### Scenario 5: Timestamp Range Query (Query Today's Full-Day Data)

**Requirement**: Real-time query of order data from today 00:00:00 to the current time

```SQL
-- SQL task
SELECT 
    order_id,
    order_time,
    amount
FROM orders
WHERE order_timestamp >= ${biz_timestamp}
```

***

## FAQ

### Q4: What is the difference between ad-hoc run and scheduled run parameters?

| Dimension            | Ad-Hoc Run                         | Scheduled Run                                      |
| -------------------- | ---------------------------------- | -------------------------------------------------- |
| Parameter source     | Manually entered in the dialog     | Values from parameter configuration                |
| Scope of effect      | Current run only                   | Takes effect for every scheduled execution         |
| Time reference       | Moment when the run is clicked     | Scheduled plan time                                |
| Task info parameters | Not supported (no actual task instance) | Supports sys\_task\_\* series parameters         |
| Applicable scenarios | Debugging, verification            | Automated production environment runs              |

**Note**: Parameter values entered during ad-hoc runs are **not saved** to the parameter configuration. The parameter configuration only saves the assignment logic (expressions or constants).

***

### Q5: How to verify that parameter configuration is correct?

**Use a simple query for verification**

```SQL
SELECT '${lastDay}' as lastDay;
```

Parameter configuration: `lastDay = add_days('yyyy-MM-dd', -1)`

**Check the execution log** After execution, view the actual SQL in the log to confirm that parameters were correctly replaced.

If it returns yesterday's date (e.g., `2023-09-21`), the parameter feature is working correctly.

***

### Q6: How to use parameters in Python tasks?

**Example**:
```Python
# Define parameters (use string variables)
yesterday = '${yesterday}'
start_ts = ${start_ts}
task_name = '${task_name}'

# Use parameters
print(f"Processing date: {yesterday}")
print(f"Start timestamp: {start_ts}")

# Use in SQL
sql = f"""
    SELECT * FROM table 
    WHERE dt = '{yesterday}'
      AND create_time >= {start_ts}
"""
```

**Parameter configuration**:

* `yesterday` = `$[yyyy-MM-dd, -1d]`
* `start_ts` = `biz_timestamp()`
* `task_name` = `sys_task_name`

**Notes**:

* String-type parameters need quotes: `'${yesterday}'`
* Numeric-type parameters do not need quotes: `${start_ts}`

***

### Q7: How to handle end-of-month date offset issues?

**Problem**: January 31 minus 1 month should be December 31, but some months don't have a 31st day

**Solution**: Use the `last_day_of_month()` function

```SQL
-- Recommended approach (explicitly want the last day of the previous month)
SELECT '${last_month_end}' as last_month_end;
-- Parameter config: last_month_end = last_day_of_month('yyyy-MM-dd', '-1mon')
-- Always returns the last day of the previous month
```

***

### Q8: How to debug complex parameter expressions?

**Tip 1: Verify step by step**

```SQL
-- First verify the basic expression
SELECT '${base_date}' as base_date;
-- base_date = $[yyyy-MM-dd]

-- Then add an offset
SELECT '${offset_date}' as offset_date;
-- offset_date = $[yyyy-MM-dd, -1mon]

-- Finally add multiple offsets
SELECT '${final_date}' as final_date;
-- final_date = $[yyyy-MM-dd, -1mon, -7d]
```

**Tip 2: Use comments for explanation**

```SQL
SELECT 
    '${report_start}' as report_start,  -- First day of last month
    '${report_end}' as report_end,      -- Last day of last month
    '${last_year_date}' as last_year_date  -- Same period last year
FROM table;
```

Also add explanations in the parameter configuration for easier future maintenance.

***

### Q9: How to modify encrypted parameters?

**Steps**:

1. Click on the parameter configuration and find the encrypted parameter
2. Uncheck "Encrypt Value"
3. The parameter value will be displayed in plain text and can be modified
4. After modifying, re-check "Encrypt Value"

**Note**: Encryption is only for display purposes and does not affect the actual use of the parameter.

***

## Appendix: How to Verify Full Parameter Feature Support

Use the following verification SQL:

```SQL
SELECT '${lastDay}' as lastDay;
```

**Parameter configuration**:

* For `lastDay`, assign the value `add_days('yyyy-MM-dd', -1)`

**Validation logic**:
```
Check whether parameter replacement and task execution return results are normal.
If the return is normal, it means you are within the grayscale scope and support the full parameter feature; otherwise, it is not supported.
Assuming the current date is 2023-11-12, the normal return value would be 2023-11-11.
```
