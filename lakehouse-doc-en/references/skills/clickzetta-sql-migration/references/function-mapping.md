# Function Mapping: Snowflake / Spark / Databricks → ClickZetta

> Comprehensive mapping table for functions that **differ** between systems, plus a list of unsupported functions and their workarounds.
> For the full ClickZetta function reference, refer to the official ClickZetta Lakehouse documentation.

---

## Conditional Functions

| Snowflake | Spark / Databricks | ClickZetta | Notes |
|---|---|---|---|
| `IFF(cond, a, b)` | `IF(cond, a, b)` | `IF(cond, a, b)` | ClickZetta does not support `IFF` |
| `ZEROIFNULL(x)` | — | `COALESCE(x, 0)` or `NVL(x, 0)` | |
| `NULLIFZERO(x)` | — | `NULLIF(x, 0)` | |
| `BOOLAND(a, b)` | — | `a AND b` | use boolean operator |
| `BOOLOR(a, b)` | — | `a OR b` | |
| `DECODE(...)` | `DECODE(...)` | `DECODE(...)` | ✅ all supported |
| `NULLIF` / `COALESCE` / `NVL` | same | same | ✅ all supported |

---

## Date / Time Functions

| Snowflake | Spark / Databricks | ClickZetta | Notes |
|---|---|---|---|
| `DATEADD(day, n, dt)` | `DATE_ADD(dt, n)` | `DATEADD(day, n, dt)` ✅ or `DATE_ADD(dt, n)` ✅ | both syntaxes work |
| `DATEDIFF(day, start, end)` | `DATEDIFF(end, start)` | `DATEDIFF(day, start, end)` ✅ or `DATEDIFF(end, start)` ✅ | both supported, but **2-arg form has reversed order from Snowflake** |
| `DATE_TRUNC('month', dt)` | `DATE_TRUNC('month', dt)` | same | ✅ identical |
| `TO_DATE(s)` / `TO_TIMESTAMP(s)` | same | same | ✅ identical |
| `CONVERT_TIMEZONE(tz, dt)` | `from_utc_timestamp(dt, tz)` | `FROM_UTC_TIMESTAMP(dt, tz)` / `TO_UTC_TIMESTAMP(dt, tz)` | |
| `SYSDATE()` / `GETDATE()` | `current_timestamp()` | `CURRENT_TIMESTAMP()` or `NOW()` | both supported |
| `TIMESTAMPADD(unit, n, dt)` | — | `dt + INTERVAL n unit` | |
| `LAST_DAY(dt)` | `last_day(dt)` | `LAST_DAY(dt)` | ✅ identical |
| `MONTHS_BETWEEN(d1, d2)` | `months_between(d1, d2)` | `MONTHS_BETWEEN(d1, d2)` | ✅ identical |
| `YEAR(dt)` / `MONTH(dt)` / `DAY(dt)` | same | same | ✅ identical |
| `DATE_PART('year', dt)` | `date_part('year', dt)` | ❌ not supported | use `EXTRACT(YEAR FROM dt)` or `YEAR(dt)` |
| `MAKEDATE(year, dayofyear)` | — | ❌ not supported | use `MAKE_DATE(year, month, day)` |
| `CONVERT_TZ(dt, from, to)` | — | ❌ not supported | use `FROM_UTC_TIMESTAMP` / `TO_UTC_TIMESTAMP` |

---

## String Functions

| Snowflake | Spark / Databricks | ClickZetta | Notes |
|---|---|---|---|
| `CHARINDEX(sub, s)` | `instr(s, sub)` | `INSTR(s, sub)` | ⚠️ **parameter order is reversed from Snowflake** |
| `EDITDISTANCE(s1, s2)` | `levenshtein(s1, s2)` | ❌ `LEVENSHTEIN` not supported | use Python UDF / ZettaPark |
| `SOUNDEX(s)` | `soundex(s)` | ❌ not supported | no alternative |
| `STRTOK(s, delim, n)` | `split(s, delim)[n-1]` | `SPLIT_PART(s, delim, n)` | |
| `ILIKE` | `ilike` | `ILIKE` | ✅ all supported |
| `RLIKE` / `REGEXP_LIKE` | `rlike` | `RLIKE` / `REGEXP_LIKE` | ✅ all supported |
| `CONTAINS(s, sub)` | `contains(s, sub)` | `INSTR(s, sub) > 0` | |
| `STARTSWITH(s, p)` | `startswith(s, p)` | `STARTSWITH(s, p)` ✅ or `s LIKE 'p%'` | both supported |
| `ENDSWITH(s, p)` | `endswith(s, p)` | `ENDSWITH(s, p)` ✅ or `s LIKE '%p'` | both supported |
| `INITCAP(s)` | `initcap(s)` | `INITCAP(s)` | ✅ identical |
| `REGEXP_SUBSTR(s, p)` | `regexp_extract(s, p, 0)` | ❌ `REGEXP_SUBSTR` not supported | use `REGEXP_EXTRACT(s, '(p)')` |
| `OVERLAY(s PLACING new FROM pos)` | `overlay(...)` | ❌ not supported | use `CONCAT(LEFT(s, pos-1), new, SUBSTR(s, pos+len))` |
| `FORMAT(num, decimals)` | — | ❌ thousand-separator format not supported | use `ROUND` + `CAST` |

---

## Aggregate Functions

| Snowflake | Spark / Databricks | ClickZetta | Notes |
|---|---|---|---|
| `LISTAGG(col, ',') WITHIN GROUP (ORDER BY col)` | `concat_ws(',', collect_list(col))` | `GROUP_CONCAT(col ORDER BY col SEPARATOR ',')` | |
| `ARRAY_AGG(col) WITHIN GROUP (ORDER BY col)` | `array_agg(col)` (no ordering) | `ARRAY_AGG(col)` | ⚠️ `WITHIN GROUP` not supported |
| `OBJECT_AGG(key, value)` | `map_from_entries(...)` | `MAP_AGG(key, value)` | |
| `APPROX_COUNT_DISTINCT(col)` | `approx_count_distinct(col)` | `APPROX_COUNT_DISTINCT(col)` | ✅ identical |
| `MEDIAN(col)` | — | `MEDIAN(col)` | ✅ identical |
| `BITAND_AGG / BITOR_AGG / BITXOR_AGG` | — | `BIT_AND / BIT_OR / BIT_XOR` | |
| `REGR_SLOPE / REGR_INTERCEPT` | — | ❌ not supported | manually compute via `CORR` + `STDDEV` |

---

## Array / Object Functions

| Snowflake | Spark / Databricks | ClickZetta | Notes |
|---|---|---|---|
| `ARRAY_CONSTRUCT(...)` | `array(...)` | `ARRAY(...)` | |
| `OBJECT_CONSTRUCT('k', v, ...)` | `named_struct('k', v, ...)` or `map(...)` | `named_struct('k', v, ...)` ✅ or `MAP(...)` | |
| `ARRAY_SIZE(arr)` | `size(arr)` | `SIZE(arr)` ✅ or `ARRAY_SIZE(arr)` ✅ | both supported |
| `ARRAY_CONTAINS(val, arr)` | `array_contains(arr, val)` | `ARRAY_CONTAINS(arr, val)` | ⚠️ **Snowflake parameter order reversed** |
| `OBJECT_KEYS(obj)` | `map_keys(map)` | `MAP_KEYS(map)` | |
| `FLATTEN(arr)` | `flatten(arr)` | `FLATTEN(arr)` | ✅ for array of arrays |
| `LATERAL FLATTEN(input => arr)` | `LATERAL VIEW EXPLODE(arr)` | `LATERAL VIEW EXPLODE(arr)` | ⚠️ Snowflake → Hive-style syntax change |
| `STRUCT(1 AS id, 'a' AS name)` (Spark) | same | `named_struct('id', 1, 'name', 'a')` | ⚠️ ClickZetta `STRUCT` does not accept `AS` for named fields |
| `TO_ARRAY(expr)` | — | ❌ not supported | use `ARRAY(expr)` or `CAST(... AS ARRAY<T>)` |
| `MAP_FROM_ZIP(keys, values)` | — | ❌ not supported | use `MAP_FROM_ARRAYS(keys, values)` |

ClickZetta supports higher-order functions (Spark style) which Snowflake does not:

```sql
SELECT TRANSFORM(skills, x -> UPPER(x)) FROM emp;
SELECT FILTER(scores, x -> x > 90) FROM students;
SELECT EXISTS(scores, x -> x > 100) FROM students;
SELECT FORALL(scores, x -> x >= 0) FROM students;
SELECT ZIP_WITH(a, b, (x, y) -> x + y) FROM t;
```

`AGGREGATE` / `REDUCE` (Spark names) are not supported — use `ARRAY_AGG` + aggregate functions instead.

---

## JSON / Semi-structured Access

```sql
-- Snowflake (colon syntax + double-colon cast)
SELECT data:address:city AS city FROM users;
SELECT data:age::INT AS age FROM users;
SELECT data:phoneNumbers[0]:number FROM users;

-- ClickZetta (bracket syntax)
SELECT data['address']['city'] AS city FROM users;
SELECT CAST(data['age'] AS INT) AS age FROM users;
SELECT data['phoneNumbers'][0]['number'] FROM users;

-- ClickZetta also accepts :: cast operator
SELECT data['amount']::DOUBLE AS amount FROM orders;
```

| Snowflake | ClickZetta |
|---|---|
| `data:key` | `data['key']` |
| `data[0]:key` | `data[0]['key']` |
| `data:key::TYPE` | `CAST(data['key'] AS TYPE)` or `data['key']::TYPE` |
| `PARSE_JSON(s)` | `PARSE_JSON(s)` ✅ identical |
| `TO_VARIANT(x)` | `PARSE_JSON(TO_JSON(x))` |
| `TO_JSON(x)` | `TO_JSON(x)` ✅ identical |
| `IS_NULL_VALUE(json:key)` | `data['key'] IS NULL` |

---

## System / Context Functions

| Snowflake | Spark / Databricks | ClickZetta | Notes |
|---|---|---|---|
| `CURRENT_DATABASE()` | `current_database()` | `CURRENT_WORKSPACE()` | concept rename |
| `CURRENT_WAREHOUSE()` | — | `CURRENT_VCLUSTER()` | concept rename |
| `CURRENT_ROLE()` | `current_user()` | `CURRENT_USER()` | no role function |
| `CURRENT_SCHEMA()` | `current_database()` | `CURRENT_SCHEMA()` | ✅ |
| — | — | `CURRENT_INSTANCE_ID()` | ClickZetta-specific |

---

## Type Conversion Functions

| Snowflake | Spark / Databricks | ClickZetta | Notes |
|---|---|---|---|
| `TRY_TO_NUMBER(s)` / `TRY_TO_DATE(s)` | `try_cast(s AS ...)` | `TRY_CAST(s AS ...)` | |
| `TO_VARIANT(x)` | — | `PARSE_JSON(TO_JSON(x))` | |
| `CAST(...)` / `::TYPE` | `CAST(...)` / `::TYPE` | `CAST(...)` / `::TYPE` | ✅ all supported |

---

## Functions with No Direct ClickZetta Equivalent

| Function | Source | Workaround |
|---|---|---|
| `SOUNDEX(s)` | Snowflake | None |
| `EDITDISTANCE` / `LEVENSHTEIN` | Snowflake / Spark | Python UDF |
| `JSON_ARRAY_LENGTH` | various | `SIZE(CAST(json AS ARRAY<STRING>))` |
| `JSON_OBJECT_KEYS` | various | manually parse |
| `REGEXP_SUBSTR` | Snowflake | `REGEXP_EXTRACT(s, '(p)')` |
| `GENERATE_SERIES(s, e)` / `RANGE(n)` | various | `EXPLODE(SEQUENCE(s, e))` |
| `TABLESAMPLE (n PERCENT)` | various | `ORDER BY RAND() LIMIT n` |
| `ST_*` geospatial functions | various | None — geospatial not supported |
| `TO_IPV4` / IP address functions | various | None |
| `HLL_APPROX` | various | `APPROX_COUNT_DISTINCT(col)` |
| `BITAND(a, b)` / `BITOR(a, b)` / `BITXOR(a, b)` | various | bitwise operators `&` / `\|` / `^` |
| `INITCAP(s)` (in versions that miss it) | — | `CONCAT(UPPER(SUBSTR(s,1,1)), LOWER(SUBSTR(s,2)))` |
| `SQUARE(x)` | Snowflake | `POWER(x, 2)` |
| `HAVERSINE(...)` | Snowflake | None |
| `WIDTH_BUCKET(...)` | Snowflake | None |
| `FACTORIAL(n)` | various | `EXP(SUM(LN(generate)))` over a sequence |
| `BIN(x)` | various | `CONV(x, 10, 2)` |

---

## Vector Functions (ClickZetta-Specific)

ClickZetta has native vector functions for similarity search, which Snowflake/Spark do not provide:

```sql
L2_DISTANCE(v1, v2)             -- Euclidean distance
COSINE_DISTANCE(v1, v2)         -- Cosine distance
DOT_PRODUCT(v1, v2)             -- Dot product
HAMMING_DISTANCE(v1, v2)        -- Hamming distance (binary)
JACCARD_DISTANCE(v1, v2)        -- Jaccard distance
BINARY_QUANTIZE(v)              -- float vector → binary
VECTOR(v1, v2, ...)             -- construct vector
```

If migrating from Snowflake Cortex Search or Databricks Vector Search, redesign around these primitives + the `VECTOR INDEX` (see ClickZetta Lakehouse documentation).
