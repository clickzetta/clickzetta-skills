# Data Type Conversion

Lakehouse supports two kinds of type conversion: explicit conversion, specified by the user via the `CAST` function or `::` operator; and implicit conversion, performed automatically by the system during arithmetic operations, comparisons, function calls, and similar contexts.

## Explicit Conversion

Lakehouse supports two equivalent explicit type conversion syntaxes:

```SQL
CAST(a AS INT)
a::INT
```

Example:

```SQL
SELECT '123'::INT, '3.14'::DOUBLE, '2024-01-15'::DATE;
-- Returns: 123 | 3.14 | 2024-01-15
```

The table below shows conversion support between types.

- 🟢 Implicit conversion supported (system executes automatically during operations or comparisons; explicit CAST also works)
- 🔵 Explicit conversion only (must use CAST or `::`)
- 🔴 Explicit conversion only, and may return NULL on overflow in lenient mode
- ✗ Not supported

| Source\Target  | Tinyint | Smallint | Int | Bigint | Float | Double | Decimal | String | Date | Timestamp\_ltz | Timestamp\_ntz | Interval | Boolean | Binary | Array | Map | Struct | Vector | Bitmap |
| -------------- | ------- | -------- | --- | ------ | ----- | ------ | ------- | ------ | ---- | -------------- | -------------- | -------- | ------- | ------ | ----- | --- | ------ | ------ | ------ |
| Tinyint        | 🟢       | 🟢        | 🟢   | 🟢      | 🟢     | 🟢      | 🟢       | 🟢      | ✗    | 🔵              | ✗              | ✗        | 🔵       | ✗      | ✗     | ✗   | ✗      | ✗      | ✗      |
| Smallint       | 🔴       | 🟢        | 🟢   | 🟢      | 🟢     | 🟢      | 🟢       | 🟢      | ✗    | 🔵              | ✗              | ✗        | 🔵       | ✗      | ✗     | ✗   | ✗      | ✗      | ✗      |
| Int            | 🔴       | 🔴        | 🟢   | 🟢      | 🟢     | 🟢      | 🟢       | 🟢      | ✗    | 🔵              | ✗              | ✗        | 🔵       | ✗      | ✗     | ✗   | ✗      | ✗      | ✗      |
| Bigint         | 🔴       | 🔴        | 🔴   | 🟢      | 🟢     | 🟢      | 🟢       | 🟢      | ✗    | 🔵              | ✗              | ✗        | 🔵       | ✗      | ✗     | ✗   | ✗      | ✗      | ✗      |
| Float          | 🔴       | 🔴        | 🔴   | 🔴      | 🟢     | 🟢      | 🔴       | 🟢      | ✗    | 🔵              | ✗              | ✗        | 🔵       | ✗      | ✗     | ✗   | ✗      | ✗      | ✗      |
| Double         | 🔴       | 🔴        | 🔴   | 🔴      | 🔴     | 🟢      | 🔴       | 🟢      | ✗    | 🔵              | ✗              | ✗        | 🔵       | ✗      | ✗     | ✗   | ✗      | ✗      | ✗      |
| Decimal        | 🔴       | 🔴        | 🔴   | 🔴      | 🔴     | 🟢      | 🔴       | 🟢      | ✗    | 🔵              | ✗              | ✗        | 🔵       | ✗      | ✗     | ✗   | ✗      | ✗      | ✗      |
| String         | 🔴       | 🔴        | 🔴   | 🔴      | 🔴     | 🔴      | 🔴       | 🟢      | 🟢    | 🟢              | 🟢              | 🟢        | 🟢       | 🔴      | ✗     | ✗   | ✗      | 🔴      | ✗      |
| Date           | ✗       | ✗        | ✗   | ✗      | ✗     | ✗      | ✗       | 🟢      | 🟢    | 🟢              | 🟢              | ✗        | ✗       | ✗      | ✗     | ✗   | ✗      | ✗      | ✗      |
| Timestamp\_ltz | 🔴       | 🔴        | 🔴   | 🔴      | 🔴     | 🔴      | 🔴       | 🟢      | 🔵    | 🟢              | 🔵              | ✗        | ✗       | ✗      | ✗     | ✗   | ✗      | ✗      | ✗      |
| Timestamp\_ntz | ✗       | ✗        | ✗   | ✗      | ✗     | ✗      | ✗       | 🟢      | 🟢    | 🟢              | 🟢              | ✗        | ✗       | ✗      | ✗     | ✗   | ✗      | ✗      | ✗      |
| Interval       | ✗       | ✗        | ✗   | ✗      | ✗     | ✗      | ✗       | 🟢      | ✗    | ✗              | ✗              | 🟢        | ✗       | ✗      | ✗     | ✗   | ✗      | ✗      | ✗      |
| Boolean        | 🔵       | 🔵        | 🔵   | 🔵      | 🔵     | 🔵      | 🔵       | 🟢      | ✗    | ✗              | ✗              | ✗        | 🟢       | ✗      | ✗     | ✗   | ✗      | ✗      | ✗      |
| Binary         | ✗       | ✗        | 🔵   | 🔵      | ✗     | ✗      | ✗       | 🔵      | ✗    | ✗              | ✗              | ✗        | ✗       | 🟢      | ✗     | ✗   | ✗      | ✗      | ✗      |
| Array          | ✗       | ✗        | ✗   | ✗      | ✗     | ✗      | ✗       | 🔵      | ✗    | ✗              | ✗              | ✗        | ✗       | ✗      | 🔴     | ✗   | ✗      | 🔵      | ✗      |
| Map            | ✗       | ✗        | ✗   | ✗      | ✗     | ✗      | ✗       | 🔵      | ✗    | ✗              | ✗              | ✗        | ✗       | ✗      | ✗     | 🔴   | ✗      | ✗      | ✗      |
| Struct         | ✗       | ✗        | ✗   | ✗      | ✗     | ✗      | ✗       | 🔵      | ✗    | ✗              | ✗              | ✗        | ✗       | ✗      | ✗     | ✗   | 🔴      | ✗      | ✗      |
| Vector         | ✗       | ✗        | ✗   | ✗      | ✗     | ✗      | ✗       | ✗      | ✗    | ✗              | ✗              | ✗        | ✗       | ✗      | 🔵     | ✗   | ✗      | 🔴      | ✗      |
| Bitmap         | ✗       | ✗        | ✗   | ✗      | ✗     | ✗      | ✗       | ✗      | ✗    | ✗              | ✗              | ✗        | ✗       | ✗      | ✗     | ✗   | ✗      | ✗      | 🔴      |

🔴 conversions return NULL on overflow in lenient mode rather than raising an error. You can enable strict mode via `SET cz.sql.cast.mode=strict`, which causes overflow to raise an error directly. You can also use the [`TRY_CAST`](datatype-cast.md) function, which returns NULL on error.

- Numeric overflow (e.g., `CAST(18.234 AS DECIMAL(4,3))`): lenient mode returns NULL, strict mode raises an error
- FLOAT to INTEGER: truncates the decimal part
- FLOAT/DOUBLE to DECIMAL: explicit CAST required; in expressions, mixed Float/Double and Decimal operations produce DOUBLE
- DECIMAL to DOUBLE: implicitly supported (Decimal is automatically promoted to DOUBLE when mixed with floating-point types in expressions)
- TIMESTAMP to DATE: discards the time portion (explicit CAST required)
- All numeric types to Timestamp_ltz: the number is interpreted as a Unix timestamp (seconds)
- Timestamp_ltz to numeric types: extracts the Unix timestamp (seconds); explicit CAST required, may return NULL on overflow
- Binary to Int/Bigint: explicit CAST required; interpreted as an integer in big-endian byte order (only 32-bit and larger integer types supported)
- Array/Map/Struct support element type conversion within the same family; use angle-bracket syntax to specify the target element type:

  ```SQL
  SELECT CAST(ARRAY(1, 2, 3) AS ARRAY<BIGINT>);
  SELECT CAST(MAP('a', 1) AS MAP<STRING, BIGINT>);
  SELECT CAST(named_struct('a', 1) AS STRUCT<a:BIGINT>);
  ```

- Vector supports mutual conversion with Array (specify element type: `CAST(vec AS ARRAY<FLOAT>)`, `CAST(arr AS VECTOR(FLOAT, n))`); Vector to String output is not usable and is treated as unsupported
- Bitmap does not support any CAST conversion; use dedicated functions: `to_bitmap()` (integer to Bitmap), `string_to_bitmap()` (string to Bitmap), `bitmap_to_string()` (Bitmap to string)

## Literal Syntax

A literal is syntax that directly represents a typed value in SQL without going through CAST conversion.

### Basic Type Literals

| Type | Literal Syntax | Example |
|------|---------------|---------|
| TINYINT | Number followed by `Y` | `1Y` |
| SMALLINT | Number followed by `S` | `100S` |
| BIGINT | Number followed by `L` | `9999999999L` |
| FLOAT | Number followed by `F` | `3.14F` |
| DOUBLE | Number followed by `D` | `3.14D` |
| DECIMAL | Number followed by `BD` | `3.14BD` |
| BOOLEAN | Written directly | `true`, `false` |
| BINARY | `X'hex'` | `X'41424344'` |
| DATE | `DATE'yyyy-MM-dd'` | `DATE'2024-01-15'` |
| TIMESTAMP | `TIMESTAMP'yyyy-MM-dd HH:mm:ss'` | `TIMESTAMP'2024-01-15 08:30:00'` |
| TIMESTAMP_NTZ | `TIMESTAMP_NTZ'yyyy-MM-dd HH:mm:ss'` | `TIMESTAMP_NTZ'2024-01-15 08:30:00'` |
| INTERVAL | `INTERVAL 'value' unit` | `INTERVAL '3' DAY` |

### Complex Type Constructors

| Type | Constructor Syntax | Example |
|------|--------------------|---------|
| ARRAY | `ARRAY(v1, v2, ...)` | `ARRAY(1, 2, 3)` |
| MAP | `MAP(k1, v1, k2, v2, ...)` | `MAP('a', 1, 'b', 2)` |
| STRUCT | `named_struct('field_name', value, ...)` | `named_struct('id', 1, 'name', 'Alice')` |
| VECTOR | `vector(v1, v2, ...)` | `vector(1.0, 2.0, 3.0)` |

### Notes for INSERT

During INSERT writes, **strings are not implicitly converted to DATE/TIMESTAMP/TIMESTAMP_NTZ**; you must use a literal prefix or CAST:

```SQL
-- Error: string cannot be implicitly converted to date
INSERT INTO t VALUES ('2024-01-15');

-- Correct approach 1: literal prefix
INSERT INTO t VALUES (DATE'2024-01-15');

-- Correct approach 2: CAST
INSERT INTO t VALUES (CAST('2024-01-15' AS DATE));
```

> ⚠️ **Note**: This differs from behavior in SELECT — in SELECT, strings can match date columns via implicit conversion, but INSERT VALUES does not allow this and will raise an error directly.

## Implicit Conversion

When two values of different types are involved in arithmetic operations, comparisons, or operations like COALESCE/CASE/UNION, Lakehouse automatically promotes the lower-priority type to the higher-priority type according to type precedence.

![](/.topwrite/assets/06-implicit-cast.svg)

Solid arrows in the diagram indicate implicit widening paths (lower precision automatically promoted to higher precision); dashed arrows indicate that a type can be implicitly converted to STRING.

**Main rules:**

- Integer chain (precision low to high): `TINYINT → SMALLINT → INT → BIGINT`
- Integer mixed with `DECIMAL`: when the target DECIMAL's integer digits are sufficient to hold the integer type, the integer is promoted to that DECIMAL; otherwise implicit conversion does not apply
- Any integer or `DECIMAL` mixed with `FLOAT`/`DOUBLE`: the result is uniformly promoted to `DOUBLE` (`FLOAT` is also upgraded to `DOUBLE` during implicit promotion)
- `DATE` can be implicitly promoted to `TIMESTAMP_LTZ` or `TIMESTAMP_NTZ`
- `TIMESTAMP_NTZ` can be implicitly promoted to `TIMESTAMP_LTZ`; when DATE is mixed with both TIMESTAMP types, `TIMESTAMP_LTZ` takes priority
- When `STRING` is mixed with other types, STRING is attempted to be converted to that type (including INTEGER, DECIMAL, FLOAT/DOUBLE, DATE, TIMESTAMP, BOOLEAN, INTERVAL; conversion failure silently returns NULL)
- `NULL` can be implicitly converted to any type
- `ARRAY`, `MAP`, `STRUCT`, `BINARY`, `VECTOR`, `BITMAP` only accept implicit conversion from NULL

**Scenario examples:**

Arithmetic — integer mixed with BIGINT, automatically promoted to BIGINT:

```SQL
SELECT typeof(100 + 9999999999L);
-- Returns: bigint
```

Comparison — DATE compared with TIMESTAMP, DATE automatically promoted to TIMESTAMP_LTZ:

```SQL
SELECT CAST('2024-01-15' AS DATE) < TIMESTAMP '2024-01-15 12:00:00';
-- Returns: true
```

UNION ALL — TINYINT mixed with INT, result column type promoted to INT:

```SQL
SELECT typeof(a) FROM (
  SELECT 1Y AS a
  UNION ALL
  SELECT 1000
) t;
-- Returns: int
```

COALESCE — INT mixed with DECIMAL, result promoted to DECIMAL:

```SQL
SELECT typeof(COALESCE(1, 3.14BD));
-- Returns: decimal(12,2)
```

Lakehouse uses lenient mode by default: implicit conversion failures return NULL rather than raising an error. You can enable strict mode via `SET cz.sql.cast.mode=strict`.

## Type Conversion Notes

### Mixed Type Conversion

In lenient mode, the following common patterns require attention — mixed type conversion failures return NULL rather than raising an error:

**UNION ALL with mixed types**

When strings and numbers are mixed, the system attempts to convert strings to numeric values according to type priority; rows that cannot be converted become NULL:

```SQL
SELECT 'abc' UNION ALL SELECT 123;
-- Result: NULL, 123 ('abc' cannot be converted to numeric, silently becomes NULL)
```

Recommended approach: explicitly unify types

```SQL
SELECT CAST('abc' AS STRING) UNION ALL SELECT CAST(123 AS STRING);
-- Result: 'abc', '123'
```

**COALESCE with mixed types**

`COALESCE` derives a common type by type priority; string arguments may be converted to numeric:

```SQL
SELECT COALESCE('abc', 123);
-- Result: 123 ('abc' fails to convert to numeric, becomes NULL, skipped, returns 123)

SELECT COALESCE(NULL, 'abc', 123);
-- Result: 123 (same as above, 'abc' converted to numeric fails, becomes NULL)
```

**CASE branches with inconsistent types**

When return value types differ across branches, the system attempts to convert to a common type; branches that fail conversion return NULL:

```SQL
SELECT CASE WHEN 1=1 THEN 'abc' ELSE 123 END;
-- Result: NULL ('abc' cannot be converted to numeric, that branch becomes NULL)
```

Recommended approach:

```SQL
SELECT CASE WHEN 1=1 THEN 'abc' ELSE CAST(123 AS STRING) END;
-- Result: 'abc'
```

> ⚠️ **Note**: All three scenarios above fail silently — no error is raised, NULL is returned directly. In ETL or reporting logic, mixed-type UNION/COALESCE/CASE is a common source of NULL pollution. It is recommended to explicitly CAST to a unified type before use.

### String to Numeric Types

String to INT/BIGINT only accepts pure integer format:

```SQL
SELECT CAST('123' AS INT);       -- 123 (normal)
SELECT CAST(' 123 ' AS INT);     -- 123 (leading/trailing spaces ignored)
SELECT CAST('00123' AS INT);     -- 123 (leading zeros ignored)
SELECT CAST('1.0' AS INT);       -- NULL (contains decimal point, not supported)
SELECT CAST('1e10' AS INT);      -- NULL (scientific notation, not supported)
SELECT CAST('+123' AS INT);      -- NULL (plus sign not supported; '-123' works normally)
SELECT CAST('' AS INT);          -- NULL (empty string)
```

> To convert a string containing a decimal point, first convert to DOUBLE then to INT: `CAST(CAST('1.0' AS DOUBLE) AS INT)`

### String to BOOLEAN

String to BOOLEAN only recognizes specific true/false strings (leading/trailing spaces are automatically ignored, case-insensitive):

| Input | Result | Notes |
|-------|--------|-------|
| `'true'`, `'t'`, `'yes'`, `'y'`, `'1'` | true | True values (case-insensitive) |
| `'false'`, `'f'`, `'no'`, `'n'`, `'0'` | false | False values (case-insensitive) |
| `'2'`, `'abc'`, `''`, etc. | NULL | Other values return NULL |

### DECIMAL Overflow Behavior

When a DECIMAL conversion exceeds the target precision range, lenient mode returns NULL:

```SQL
SELECT CAST(18.234 AS DECIMAL(4,3));  -- NULL (max value 9.999, 18.234 overflows)
SELECT CAST(9.999 AS DECIMAL(3,2));   -- NULL (rounds to 10.00, exceeds range)
SELECT CAST(9.995 AS DECIMAL(4,2));   -- 10.00 (half-up rounding)
```

### Invalid Date/Time

CAST of an invalid date or time returns NULL rather than raising an error:

```SQL
SELECT CAST('2024-02-30' AS DATE);              -- NULL (February has no 30th)
SELECT CAST('2024-01-15 25:00:00' AS TIMESTAMP); -- NULL (hour out of range)
```

### Implicit Conversion in Comparisons

When strings are compared with numbers, the string is attempted to be converted to numeric; conversion failure returns NULL:

```SQL
SELECT '123' = 123;    -- true ('123' successfully converted to 123)
SELECT 'abc' > 123;    -- NULL ('abc' cannot be converted to numeric)
SELECT '+123' = 123;   -- NULL (plus sign not supported)
```

### Array Constructor Type Requirements

The `ARRAY()` constructor requires all elements to be the same type; mixed types raise an error:

```SQL
SELECT ARRAY(1, 2, 3);          -- OK: array<int>
SELECT ARRAY(1, 'a', true);     -- Error: inputs to function array() should be the same type
```

### Limitations of Numeric to TIMESTAMP Conversion

Integers can only be converted to TIMESTAMP_LTZ (interpreted as Unix timestamps); direct conversion to TIMESTAMP_NTZ is not supported:

```SQL
SELECT CAST(1705278600 AS TIMESTAMP);      -- 2024-01-15 08:30:00 (TIMESTAMP_LTZ)
SELECT CAST(1705278600 AS TIMESTAMP_NTZ);  -- Error
```

### INTERVAL String Format

CAST for INTERVAL only supports pure numeric strings:

```SQL
SELECT CAST('3' AS INTERVAL DAY);          -- 3 days (normal)
SELECT CAST('3 days' AS INTERVAL DAY);     -- NULL (text units not supported)
SELECT CAST(86400 AS INTERVAL DAY);        -- Error (integer direct conversion not supported)
```

## Examples

Implicit conversion — DECIMAL and DOUBLE operation, result promoted to DOUBLE:

```SQL
SELECT typeof(10BD + 3.14D);
-- Returns: double
```

Explicit conversion — convert string to INT:

```SQL
SELECT CAST('123' AS INT);
-- Returns: 123
```
