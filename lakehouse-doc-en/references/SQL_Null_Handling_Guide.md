# Lakehouse Missing Value Filling Guide

## Overview

Data missingness is the most common problem in data cleaning. Singdata Lakehouse provides multiple functions for handling NULL values, including conditional replacement, default value filling, and forward/backward filling. This guide categorizes usage by business scenario to help you quickly master efficient missing value handling methods.

### Quick Navigation

* [Basic NULL Replacement](#basic-null-replacement) -- Use COALESCE to replace null values
* [Two-Value Conditional Replacement](#two-value-conditional-replacement) -- Use IFNULL / NULLIF for simple scenarios
* [Forward/Backward Filling](#forwardbackward-filling) -- Use LAG / LEAD to fill missing values in time series
* [Group Mean Filling](#group-mean-filling) -- Use window functions to fill statistical values by group
* [NULL Value Judgment](#null-value-judgment) -- Correctly handle logical checks on NULL

***

## SQL Commands Covered

| Command/Function | Purpose | Applicable Scenario |
|-----------|------|----------|
| `COALESCE(col1, col2, ...)` | Return the first non-NULL value | Multi-priority default value filling |
| `IFNULL(col, value)` | Return specified value when NULL | Simple default value filling |
| `NULLIF(col, value)` | Return NULL when equal to specified value | Convert specific values to NULL |
| `LAG(col) / LEAD(col)` | Access previous/next row data | Time series forward/backward filling |
| `AVG() OVER (PARTITION BY)` | Group average | Group statistical value filling |
| `IS NULL` / `IS NOT NULL` | NULL value check | Conditional filtering |

***

## Prerequisites

The following examples use a simulated user profile table `user_profiles` containing some missing data:

```sql
-- Create test table
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id INT,
    user_name STRING,
    age INT,
    city STRING,
    last_login DATE
);

-- Insert test data (including NULL values)
INSERT INTO user_profiles VALUES
(1, 'Alice', 28, 'Shanghai', '2024-06-01'),
(2, 'Bob', NULL, 'Beijing', '2024-05-15'),
(3, 'Carol', 35, NULL, '2024-06-02'),
(4, 'David', NULL, NULL, '2024-04-20'),
(5, 'Eve', 22, 'Shanghai', NULL);
```

***

## Basic NULL Replacement

Use the `COALESCE` function to replace NULL values by priority, supporting multiple fallback values.

```sql
-- Use COALESCE to fill missing city information
SELECT 
    user_id,
    user_name,
    COALESCE(city, 'Unknown') as city
FROM user_profiles
ORDER BY user_id;
```

**Result**:

| user_id | user_name | city |
|---------|-----------|------|
| 1 | Alice | Shanghai |
| 2 | Bob | Beijing |
| 3 | Carol | Unknown |
| 4 | David | Unknown |
| 5 | Eve | Shanghai |

### Multi-Priority Filling

`COALESCE` can be chained to try values in order of priority:

```sql
-- Multi-priority filling: prefer city, then user_name, then 'N/A'
SELECT 
    user_id,
    user_name,
    COALESCE(city, user_name, 'N/A') as display_location
FROM user_profiles
ORDER BY user_id;
```

**Result**:

| user_id | user_name | display_location |
|---------|-----------|------------------|
| 1 | Alice | Shanghai |
| 2 | Bob | Beijing |
| 3 | Carol | Carol |
| 4 | David | David |
| 5 | Eve | Shanghai |

***

## Two-Value Conditional Replacement

When only switching between NULL and one default value, `IFNULL` is more concise.

```sql
-- Use IFNULL to fill missing age
SELECT 
    user_id,
    user_name,
    IFNULL(age, 0) as age
FROM user_profiles
ORDER BY user_id;
```

**Result**:

| user_id | user_name | age |
|---------|-----------|-----|
| 1 | Alice | 28 |
| 2 | Bob | 0 |
| 3 | Carol | 35 |
| 4 | David | 0 |
| 5 | Eve | 22 |

### Convert Specific Values to NULL

Use `NULLIF` to convert meaningless placeholder values (e.g., 0, empty string) to NULL:

```sql
-- Convert records with age 0 to NULL (indicating unknown)
SELECT 
    user_id,
    user_name,
    NULLIF(age, 0) as age
FROM user_profiles
ORDER BY user_id;
```

***

## Forward/Backward Filling

In time series data, the previous or next row's value is commonly used to fill current missing values.

```sql
-- Use the previous login time to fill missing values
SELECT 
    user_id,
    user_name,
    last_login,
    LAG(last_login) OVER (ORDER BY user_id) as prev_login,
    COALESCE(last_login, LAG(last_login) OVER (ORDER BY user_id)) as filled_login
FROM user_profiles
ORDER BY user_id;
```

**Result**:

| user_id | user_name | last_login | prev_login | filled_login |
|---------|-----------|------------|------------|--------------|
| 1 | Alice | 2024-06-01 | NULL | 2024-06-01 |
| 2 | Bob | 2024-05-15 | 2024-06-01 | 2024-05-15 |
| 3 | Carol | 2024-06-02 | 2024-05-15 | 2024-06-02 |
| 4 | David | 2024-04-20 | 2024-06-02 | 2024-04-20 |
| 5 | Eve | NULL | 2024-04-20 | 2024-04-20 |

> ⚠️ **Note**: NULL values of numeric types and time types may display as `nan` and `NaT` respectively, but `IS NULL` checks remain valid.

***

## Group Mean Filling

For numeric missing values, the mean or median of the same group is commonly used for filling.

```sql
-- Fill missing age with the average age of users in the same city (grouped by city)
SELECT 
    user_id,
    user_name,
    age,
    city,
    ROUND(AVG(age) OVER (PARTITION BY city), 1) as city_avg_age,
    COALESCE(age, AVG(age) OVER (PARTITION BY city)) as filled_age
FROM user_profiles
ORDER BY user_id;
```

**Result**:

| user_id | user_name | age | city | city_avg_age | filled_age |
|---------|-----------|-----|------|--------------|------------|
| 1 | Alice | 28 | Shanghai | 25 | 28 |
| 2 | Bob | NULL | Beijing | NULL | NULL |
| 3 | Carol | 35 | NULL | NULL | NULL |
| 4 | David | NULL | NULL | NULL | NULL |
| 5 | Eve | 22 | Shanghai | 25 | 22 |

> 💡 **Tip**: If all values within a group are NULL, `AVG` also returns NULL, and `COALESCE` will not fill. You can combine with the global mean: `COALESCE(age, AVG(age) OVER (PARTITION BY city), AVG(age) OVER ())`.

***

## NULL Value Judgment

Correctly handle logical checks on NULL values to avoid common pitfalls.

```sql
-- Correct way to check NULL
SELECT 
    user_id,
    user_name,
    CASE 
        WHEN age IS NULL THEN 'Unknown'
        WHEN age < 18 THEN 'Minor'
        WHEN age < 60 THEN 'Adult'
        ELSE 'Senior'
    END as age_group
FROM user_profiles
ORDER BY user_id;
```

**Result**:

| user_id | user_name | age_group |
|---------|-----------|-----------|
| 1 | Alice | Adult |
| 2 | Bob | Unknown |
| 3 | Carol | Adult |
| 4 | David | Unknown |
| 5 | Eve | Adult |

### Common Pitfall

```sql
-- Wrong: NULL compared with any value returns NULL (not TRUE)
SELECT * FROM user_profiles WHERE age = NULL;  -- Returns 0 rows

-- Correct: Use IS NULL
SELECT * FROM user_profiles WHERE age IS NULL;
```

***

## Clean Up Test Data

After completing missing value handling verification, it is recommended to clean up test tables:

```sql
-- Drop test table
DROP TABLE IF EXISTS user_profiles;
```

> 💡 **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Important Notes

1. **COALESCE vs IFNULL**: `COALESCE` is standard SQL and supports multiple parameters; `IFNULL` supports only two parameters and is a shorthand form of `COALESCE`.
2. **NULL vs Empty String**: `NULL` represents a missing value, while `''` (empty string) is a valid value. Distinguish between them during handling.
3. **Aggregate Functions and NULL**: `COUNT(col)` does not count NULL values; `SUM()` and `AVG()` ignore NULL values.
4. **NULL Value Display**: In Lakehouse, numeric type NULL displays as `nan`, time type NULL displays as `NaT`, but logical checks are unaffected.

***

## Related Documentation

* [Conditional Functions](conditional_function.md)
* [Aggregate Functions](agg_function.md)
* [Window Functions](windowfunction.md)
