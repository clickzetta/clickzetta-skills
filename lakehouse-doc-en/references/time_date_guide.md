# Date/Time Types

Singdata Lakehouse supports four time-related types: DATE, TIMESTAMP, TIMESTAMP_NTZ, and INTERVAL.

## Type Comparison

| Type | Precision | Timezone | Use Case |
|------|-----------|----------|---------|
| `DATE` | Day | No timezone | Birthdays, date dimensions, fields that only need year/month/day |
| `TIMESTAMP` | Microsecond | With timezone (stored as UTC, displayed in local time) | Cross-timezone event times, log timestamps |
| `TIMESTAMP_NTZ` | Microsecond | No timezone (local time stored as-is) | Local business time, scenarios without timezone conversion |
| `INTERVAL` | Variable | — | Represents a time difference; used for date arithmetic |

Key difference between TIMESTAMP and TIMESTAMP_NTZ (measured):

```SQL
-- TIMESTAMP: stored as UTC; input 10:30 Beijing time is stored as 02:30 UTC
SELECT TIMESTAMP '2024-01-15 10:30:00';      -- 2024-01-15T02:30:00.000Z

-- TIMESTAMP_NTZ: stored as-is, no timezone conversion
SELECT TIMESTAMP_NTZ '2024-01-15 10:30:00'; -- 2024-01-15T10:30:00.000Z
```

## Common Operation Examples

```SQL
-- DATE arithmetic
SELECT DATE_ADD(DATE '2024-01-15', 10);                        -- 2024-01-25
SELECT DATEDIFF(DATE '2024-02-01', DATE '2024-01-15');         -- 17

-- INTERVAL arithmetic
SELECT DATE '2024-01-15' + INTERVAL '10' DAY;                 -- 2024-01-25
SELECT DATE '2024-01-15' + INTERVAL '2' MONTH;                -- 2024-03-15

-- Get current time
SELECT CURRENT_DATE();       -- current date
SELECT CURRENT_TIMESTAMP();  -- current timestamp (with timezone)
```

## Related Documentation

- [DATE](date.md)
- [TIMESTAMP](timestamp.md)
- [TIMESTAMP_NTZ](data-types-timestamp-ntz.md)
- [INTERVAL](interval.md)
- [Data Types](data-type.md)
- [Data Type Conversion](datatype-conversion.md)
