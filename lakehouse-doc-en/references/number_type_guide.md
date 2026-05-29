# Numeric Types

Singdata Lakehouse supports integer types (TINYINT, SMALLINT, INT, BIGINT) and floating-point / exact decimal types (FLOAT, DOUBLE, DECIMAL).

## Type Comparison

### Integer Types

| Type | Storage | Range | Use Case |
|------|---------|-------|---------|
| `TINYINT` | 1 byte | -128 ~ 127 | Status codes, enum values, small-range flags |
| `SMALLINT` | 2 bytes | -32,768 ~ 32,767 | Year values, small-range counters |
| `INT` | 4 bytes | -2,147,483,648 ~ 2,147,483,647 | General integer IDs, counters |
| `BIGINT` | 8 bytes | -9.2×10¹⁸ ~ 9.2×10¹⁸ | Large-scale IDs, timestamps (milliseconds), cumulative totals |

A CAST that exceeds the range returns NULL (no error):

```SQL
SELECT CAST(128 AS TINYINT);    -- NULL (exceeds 127)
SELECT CAST(32768 AS SMALLINT); -- NULL (exceeds 32767)
```

### Floating-Point and Exact Decimal Types

| Type | Storage | Precision | Use Case |
|------|---------|-----------|---------|
| `FLOAT` | 4 bytes | ~6-7 significant digits | ML feature values, vector elements, approximate real numbers |
| `DOUBLE` | 8 bytes | ~15-17 significant digits | Scientific computing, statistical analysis |
| `DECIMAL(p,s)` | Variable | Exact | Financial amounts, decimals requiring exact calculation |

FLOAT vs DOUBLE precision difference (measured):

```SQL
SELECT
    CAST(3.14159265358979 AS FLOAT)  AS f,   -- 3.1415927410125732 (distortion after 7 digits)
    CAST(3.14159265358979 AS DOUBLE) AS d;   -- 3.14159265358979 (fully preserved)
```

Floating-point precision error example:

```SQL
SELECT CAST(0.1 AS DOUBLE) + CAST(0.2 AS DOUBLE);  -- 0.30000000000000004
SELECT CAST(0.1 AS DECIMAL(2,1)) + CAST(0.2 AS DECIMAL(2,1));  -- 0.3
```

## Related Documentation

- [TINYINT](tinyint.md)
- [SMALLINT](smallint.md)
- [INT](int.md)
- [BIGINT](bigint.md)
- [FLOAT](float.md)
- [DOUBLE](double.md)
- [DECIMAL](decimal.md)
- [Data Types](data-type.md)
- [Data Type Conversion](datatype-conversion.md)
