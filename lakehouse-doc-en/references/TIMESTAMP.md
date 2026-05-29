# TIMESTAMP

`TIMESTAMP` (also known as `TIMESTAMP_LTZ`, Local Time Zone) is a timezone-aware timestamp type with microsecond precision. All operations execute in the current session's timezone, and output is based on the service's timezone (UTC+8 by default).

If you do not need timezone awareness, use `TIMESTAMP_NTZ` (timezone-free timestamp).

## Syntax

```Plain
TIMESTAMP
TIMESTAMP_LTZ
```

Both are equivalent and represent a timestamp with local timezone.

## Precision and Storage

| Attribute | Value |
|-----------|-------|
| Precision | Up to microseconds (μs) |
| Timezone | Local timezone (LTZ) |

Actual precision depends on the timestamp precision at write time; microsecond positions are typically stored as milliseconds in the current version.

## Literal Syntax

```SQL
SELECT TIMESTAMP '2024-01-15 10:30:00';
-- Returns: 2024-01-15 10:30:00

SELECT TIMESTAMP '2024-01-15 10:30:00.123';
-- Returns: 2024-01-15 10:30:00.123 (millisecond precision)

SELECT TIMESTAMP '2024-01-15 10:30:00.123456';
-- Returns: 2024-01-15 10:30:00.123 (microsecond precision; current version stores to milliseconds)
```

## Type Conversion

### String to TIMESTAMP

Multiple input formats are supported and automatically recognized:

```SQL
-- Standard format
SELECT CAST('2024-01-15 10:30:00' AS TIMESTAMP);
-- Returns: 2024-01-15 10:30:00

-- ISO 8601 format (Z indicates UTC)
SELECT CAST('2024-01-15T10:30:00Z' AS TIMESTAMP);
-- Returns: 2024-01-15 18:30:00 (UTC converted to UTC+8)

SELECT CAST(NULL AS TIMESTAMP);
-- Returns: NULL
```

### Integer (Unix Timestamp in Seconds) to TIMESTAMP

```SQL
SELECT CAST(1705289400 AS TIMESTAMP);
-- Returns: approximately 2024-01-15 11:30:00 (depends on timezone)
```

### TIMESTAMP to Other Types

```SQL
-- To DATE (time portion truncated)
SELECT CAST(TIMESTAMP '2024-01-15 10:30:00' AS DATE);
-- Returns: 2024-01-15

-- To STRING
SELECT CAST(TIMESTAMP '2024-01-15 10:30:00' AS STRING);
-- Returns: 2024-01-15 10:30:00

-- To Unix timestamp (seconds)
SELECT unix_timestamp(TIMESTAMP '2024-01-15 10:30:00');
-- Returns: integer (seconds, depends on timezone)
```

## Common Functions

```SQL
-- Current timestamp (non-deterministic, returns a different value each time)
SELECT CURRENT_TIMESTAMP();

-- Calculate the number of days between two timestamps
SELECT datediff(TIMESTAMP '2024-01-15 10:30:00', TIMESTAMP '2024-01-14 10:30:00');
-- Returns: 1

-- Add 1 day to a timestamp
SELECT TIMESTAMP '2024-01-15 10:30:00' + INTERVAL 1 DAY;
-- Returns: 2024-01-16 10:30:00
```

## NULL Handling

```SQL
SELECT CAST(NULL AS TIMESTAMP);
-- Returns: NULL

SELECT CAST(NULL AS TIMESTAMP) + INTERVAL 1 DAY;
-- Returns: NULL
```

## Notes

- TIMESTAMP is timezone-aware; writes and reads are affected by the current session timezone. Use `TIMESTAMP_NTZ` when timezone awareness is not needed.
- The `Z` in ISO 8601 format indicates UTC; it is converted to the current session timezone for display.
- `CURRENT_TIMESTAMP()` is a non-deterministic function and cannot be used as a timestamp argument for `TABLE_CHANGES` (a literal is required).
- Timestamp subtraction returns an INTERVAL object, not an integer. To get the difference in seconds or days, use `datediff()` or `unix_timestamp()`.

## Related Documents

- [TIMESTAMP_NTZ](data-types-timestamp-ntz.md): timezone-free timestamp
- [DATE](date.md): date-only type
- [INTERVAL](interval.md): time interval type
- [Time Types](time_date_guide.md)
