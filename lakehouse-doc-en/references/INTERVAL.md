# INTERVAL

# INTERVAL Data Type

Lakehouse provides the INTERVAL data type to represent the time interval between two dates or times. This article introduces the usage and syntax of the INTERVAL type.

## Description

The INTERVAL data type supports two types of intervals:

* INTERVAL\_YEAR\_MONTH: Represents year-month intervals, using the YEAR and MONTH fields to store the time interval.
* INTERVAL\_DAY\_TIME: Represents day-time intervals, using days, hours, minutes, and seconds, including fractional seconds, to store the interval.

### INTERVAL\_YEAR\_MONTH

#### Syntax Format

| Syntax | Description | Example |
| --- | --- | --- |
| INTERVAL '[+\|-]y-m' YEAR TO MONTH | Specifies both YEAR and MONTH intervals | INTERVAL '2-3' YEAR TO MONTH represents 2 years and 3 months |
| INTERVAL '[+\|-]n' YEAR | Specifies only the YEAR interval | INTERVAL '2' YEAR represents 2 years |
| INTERVAL '[+\|-]n' MONTH | Specifies only the MONTH interval | INTERVAL '3' MONTH represents 3 months |
| INTERVAL '[+\|-]n' QUARTER | Supports quarter as an independent unit | INTERVAL '4' QUARTER represents 4 quarters (i.e., 1 year) |

#### Parameter Description

* year: Value range is [0, 178956970].
* month: Value range is [0, 11] (in YEAR TO MONTH format).
* quarter: Quarter unit identifier. 1 QUARTER = 3 MONTH. Supports any positive or negative integer, automatically converted to MONTH for calculation.

#### Notes

* When specifying only the MONTH interval, the month value can exceed 11, and the excess will be converted to YEAR. For example, `INTERVAL '25' MONTH` is equivalent to 2 years and 1 month.
* The maximum value for INTERVAL\_YEAR\_MONTH is `INTERVAL '178956970-7' YEAR TO MONTH` (approximately 179 million years).

### INTERVAL\_DAY\_TIME

#### Syntax Format

| Syntax | Description | Example |
| --- | --- | --- |
| INTERVAL '[+\|-]n' DAY | Specifies only the DAY interval | INTERVAL '1' DAY represents 1 day |
| INTERVAL '[+\|-]n' HOUR | Specifies only the HOUR interval | INTERVAL '23' HOUR represents 23 hours |
| INTERVAL '[+\|-]n' MINUTE | Specifies only the MINUTE interval | INTERVAL '59' MINUTE represents 59 minutes |
| INTERVAL '[+\|-]n' SECOND | Specifies only the SECOND interval | INTERVAL '59.999' SECOND represents 59.999 seconds |
| INTERVAL '[+\|-]d h' DAY TO HOUR | Specifies both DAY and HOUR | INTERVAL '1 23' DAY TO HOUR represents 1 day and 23 hours |
| INTERVAL '[+\|-]d h:m' DAY TO MINUTE | Specifies DAY, HOUR, and MINUTE | INTERVAL '1 23:59' DAY TO MINUTE represents 1 day, 23 hours, and 59 minutes |
| INTERVAL '[+\|-]d h:m:s' DAY TO SECOND | Specifies DAY, HOUR, MINUTE, and SECOND | INTERVAL '1 23:59:59.999' DAY TO SECOND represents 1 day, 23 hours, 59 minutes, and 59.999 seconds |
| INTERVAL '[+\|-]h:m' HOUR TO MINUTE | Specifies both HOUR and MINUTE | INTERVAL '15:40' HOUR TO MINUTE represents 15 hours and 40 minutes |
| INTERVAL '[+\|-]h:m:s' HOUR TO SECOND | Specifies HOUR, MINUTE, and SECOND | INTERVAL '15:40:32.999' HOUR TO SECOND represents 15 hours, 40 minutes, and 32.999 seconds |
| INTERVAL '[+\|-]m:s' MINUTE TO SECOND | Specifies both MINUTE and SECOND | INTERVAL '40:32.999' MINUTE TO SECOND represents 40 minutes and 32.999 seconds |

#### Parameter Description

* day: Value range is [0, 106751991].
* hour: Value range is [0, 23] (in composite formats).
* minute: Value range is [0, 59] (in composite formats).
* second: Value range is [0, 59.999999999] (in composite formats).

#### Notes

* When specifying only HOUR/MINUTE/SECOND intervals, the corresponding parameter values can exceed the upper limit, and the excess will be converted to a larger unit.
* The maximum value for INTERVAL\_DAY\_TIME is `INTERVAL '106751991 04:00:54.775807' DAY TO SECOND`.

## Multi-Unit Mixed Writing

Multiple units can be specified in a single INTERVAL expression, and the system will automatically combine the values of each unit for calculation:

```sql
SELECT interval 1 year 2 month 3 week 4 day 5 hour 6 minute 7 seconds 8 millisecond 9 microsecond;
```

Supported units include: YEAR, MONTH, WEEK, DAY, HOUR, MINUTE, SECOND (SECONDS), MILLISECOND, MICROSECOND, NANOSECOND.

WEEK is automatically converted to 7 days. MILLISECOND/MICROSECOND/NANOSECOND are converted to the fractional part of seconds.

You can also use string form to specify values for each unit segment:

```sql
SELECT interval '30' year '25' month '-100' day '40' hour '80' minute '299.889987299' second;
```

## Expression Writing

The `INTERVAL expr unit` form is supported, where expr can be any expression (not limited to literals), with multi-unit mixing:

```sql
-- Simple arithmetic expression
SELECT interval 1+2 year AS res;
-- Result: 3-0

-- Parenthesized expression
SELECT interval (-30) day;
-- Result: -30 00:00:00.000000000

-- Function call as value
SELECT interval -(1) days abs(-2) hours;
-- Result: -0 22:00:00.000000000

-- Multi-unit mixed expression
SELECT interval 3 hours 2+3 minutes sin(1) seconds;
-- Result: 0 03:05:00.841470000

-- Referencing column values
SELECT interval i second i millisecond i microseconds FROM VALUES(1) t(i);
-- Result: 0 00:00:01.001001000

-- Year-month type expression
SELECT interval 1+1 year 2+2 month;
-- Result: 2-4
```

## Flexible Writing

INTERVAL supports multiple flexible writing styles:

```sql
-- Use WEEK unit directly
SELECT interval 7 week;
-- Result: 49 00:00:00.000000000

-- Number written inside a string
SELECT interval '7' week;
-- Result: 49 00:00:00.000000000

-- Both number and unit written inside a string
SELECT interval '7 week';
-- Result: 49 00:00:00.000000000
```

## INTERVAL Type Operations

The INTERVAL type supports arithmetic operations with numeric types, date-time types, and string types.

### Basic Arithmetic Operations

```sql
-- Multiplication and division
SELECT INTERVAL 4 DAY * 2, INTERVAL 4 DAY / 2;
-- Result: 8 00:00:00.000000000    2 00:00:00.000000000

-- Timestamp subtraction yields INTERVAL
SELECT timestamp '2019-10-15' - timestamp '2019-10-14';
-- Result: 1 00:00:00.000000000

-- Date/Timestamp plus or minus INTERVAL
SELECT timestamp '2020-10-10' + INTERVAL 1 DAY, date '2020-10-10' + INTERVAL 1 MONTH;
-- Result: 2020-10-11 00:00:00     2020-11-10
```

### Operations Between INTERVAL Types

```sql
-- Adding and subtracting INTERVALs of the same type
SELECT interval '2-2' year to month + interval '3' month;
-- Result: 2-5

SELECT interval '99 11:22:33.123456789' day to second + interval '10 9:8' day to minute;
-- Result: 109 20:30:33.123456789
```

### Comparison Operations

```sql
SELECT INTERVAL 1 DAY < INTERVAL 2 DAY;
-- Result: true

SELECT INTERVAL '1' YEAR < INTERVAL '1' MONTH;
-- Result: false

SELECT INTERVAL '-1-1' YEAR TO MONTH = INTERVAL '-13' MONTH;
-- Result: true
```

### Mathematical Functions

```sql
-- Absolute value
SELECT abs(INTERVAL '-10' YEAR);
-- Result: 10-0

SELECT abs(INTERVAL -'1 02:03:04.123' DAY TO SECOND);
-- Result: 1 02:03:04.123000000

-- Sign function
SELECT signum(INTERVAL '-10' DAY);
-- Result: -1.0

SELECT signum(INTERVAL '0-0' YEAR TO MONTH);
-- Result: 0.0
```

### Operations with NULL

```sql
SELECT interval '2' year + null;
-- Result: NULL

SELECT null + interval '2' hour;
-- Result: NULL
```

### String and INTERVAL Operations

Supports adding and subtracting strings that conform to the INTERVAL format with INTERVAL values:

```sql
SELECT '4 12:12:12' + interval '4 22:12' day to minute;
```

## Constructor Functions

### make\_ym\_interval

Constructs an INTERVAL\_YEAR\_MONTH value:

```sql
SELECT make_ym_interval(1);        -- 1 year
-- Result: 1-0

SELECT make_ym_interval(1, 2);     -- 1 year and 2 months
-- Result: 1-2
```

### make\_dt\_interval

Constructs an INTERVAL\_DAY\_TIME value:

```sql
SELECT make_dt_interval(1);              -- 1 day
-- Result: 1 00:00:00.000000000

SELECT make_dt_interval(1, 2);           -- 1 day and 2 hours
-- Result: 1 02:00:00.000000000

SELECT make_dt_interval(1, 2, 3);        -- 1 day, 2 hours, and 3 minutes
-- Result: 1 02:03:00.000000000

SELECT make_dt_interval(1, 2, 3, 4.005006);  -- 1 day, 2 hours, 3 minutes, and 4.005006 seconds
-- Result: 1 02:03:04.005006000
```

## Notes

* INTERVAL\_YEAR\_MONTH and INTERVAL\_DAY\_TIME are two different types and cannot be directly added or subtracted. For example, `interval '2-2' year to month + interval '3' day` will report an error.
* INTERVALs of different types cannot be compared. For example, `INTERVAL 1 MONTH > INTERVAL 20 DAYS` will report an error.
* The INTERVAL type does not support storage in Iceberg-format tables.
