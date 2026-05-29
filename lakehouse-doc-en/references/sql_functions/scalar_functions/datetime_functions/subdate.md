# SUBDATE

## Overview

Subtracts a number of days or a time interval from a date, returning the resulting date or timestamp. Equivalent to `DATE_SUB`.

## Syntax

```Plain
SUBDATE(<date>, <days>)
SUBDATE(<date>, INTERVAL <value> <unit>)
```

## Parameters

- `<date>`: DATE or TIMESTAMP type, used as the base date.
- `<days>`: Integer, the number of days to subtract.
- `INTERVAL <value> <unit>`: A time interval. Supported units include DAY, WEEK, MONTH, and others.

Returns NULL if any argument is NULL.

## Examples

```sql
-- Subtract an integer number of days
SELECT subdate('2024-02-01', 7);
-- 2024-01-25

-- Subtract an INTERVAL (days)
SELECT subdate('2024-02-01', INTERVAL 1 DAY);
-- 2024-01-31

-- Subtract an INTERVAL (weeks)
SELECT subdate('2024-02-01', INTERVAL 2 WEEK);
-- 2024-01-18

-- Subtract an INTERVAL (months)
SELECT subdate('2024-02-01', INTERVAL 1 MONTH);
-- 2024-01-01

-- TIMESTAMP input
SELECT subdate('2024-02-01 12:00:00', 3);
-- 2024-01-29

-- NULL handling
SELECT subdate(NULL, 7);
-- NULL
```

## Related Documentation

- [DATE_ADD](sql_functions/scalar_functions/datetime_functions/date_add.md) — date addition
- [DATEDIFF](sql_functions/scalar_functions/datetime_functions/datediff.md) — calculates the difference between two dates
