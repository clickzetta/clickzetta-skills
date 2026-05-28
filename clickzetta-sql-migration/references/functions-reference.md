# Functions Complete Reference

> With Snowflake / Spark SQL difference annotations

---

## Numeric Functions

```sql
ABS(x)                          -- absolute value
CEIL(x) / CEILING(x)            -- round up
FLOOR(x)                        -- round down
ROUND(x, d)                     -- round to d decimal places
TRUNCATE(x, d)                  -- truncate to d decimal places
MOD(x, y) / x % y               -- modulo
POWER(x, y) / POW(x, y)         -- exponentiation
SQRT(x)                         -- square root
EXP(x)                          -- e^x
LN(x) / LOG(x)                  -- natural logarithm
LOG(base, x)                    -- logarithm with specified base
LOG2(x) / LOG10(x)              -- base-2/base-10 logarithm
SIGN(x)                         -- sign (-1/0/1)
GREATEST(a, b, c, ...)          -- maximum value
LEAST(a, b, c, ...)             -- minimum value
RANDOM() / RAND()               -- random number 0-1
PI()                            -- π
SIN(x) / COS(x) / TAN(x)       -- trigonometric functions
ASIN(x) / ACOS(x) / ATAN(x)    -- inverse trigonometric functions
ATAN2(y, x)                     -- arctangent
DEGREES(x) / RADIANS(x)        -- degree/radian conversion
-- ⚠️ FACTORIAL not supported, use EXP(SUM(LN(n))) instead
-- ⚠️ BIN(x) not supported, use CONV(x, 10, 2) instead
HEX(x)                          -- convert to hexadecimal string
UNHEX(s)                        -- hexadecimal to string
CONV(x, from_base, to_base)     -- base conversion (e.g., CONV(10,10,2) gives '1010')
```

**Differences from Snowflake:**
- Snowflake `SQUARE(x)` → ClickZetta `POWER(x, 2)`
- Snowflake `HAVERSINE(lat1, lon1, lat2, lon2)` → ClickZetta not supported
- Snowflake `WIDTH_BUCKET` → ClickZetta not supported

---

## String Functions

```sql
-- Basic operations
LENGTH(s) / CHAR_LENGTH(s)      -- character length
OCTET_LENGTH(s)                 -- byte length
UPPER(s) / LOWER(s)             -- case conversion
INITCAP(s)                      -- capitalize first letter
TRIM(s) / LTRIM(s) / RTRIM(s)  -- trim whitespace
TRIM(BOTH 'x' FROM s)           -- trim specified character
LPAD(s, n, pad) / RPAD(s, n, pad)  -- padding
REPEAT(s, n)                    -- repeat
REVERSE(s)                      -- reverse
SPACE(n)                        -- n spaces

-- Concatenation
CONCAT(s1, s2, ...)             -- concatenate (NULL propagates)
CONCAT_WS(sep, s1, s2, ...)     -- concatenate with separator (skips NULL)
s1 || s2                        -- concatenation operator

-- Substring
SUBSTR(s, pos) / SUBSTRING(s, pos)
SUBSTR(s, pos, len) / SUBSTRING(s, pos, len)
LEFT(s, n) / RIGHT(s, n)
MID(s, pos, len)                -- same as SUBSTR

-- Search
INSTR(s, substr)                -- find position (1-based, 0 means not found)
LOCATE(substr, s)               -- same as INSTR, different parameter order
LOCATE(substr, s, pos)          -- search from pos
POSITION(substr IN s)           -- ✅ supported, returns substring position (1-based)
FIND_IN_SET(s, list)            -- find in comma-separated list

-- Replace
REPLACE(s, old, new)            -- replace all occurrences
TRANSLATE(s, from_chars, to_chars)  -- character-level replacement
-- ⚠️ OVERLAY syntax not supported, use CONCAT(LEFT(s,pos-1), new, SUBSTR(s,pos+len)) instead

-- Regex
REGEXP_EXTRACT(s, pattern, group)   -- extract matching group
REGEXP_EXTRACT_ALL(s, pattern)      -- extract all matches
REGEXP_REPLACE(s, pattern, repl)    -- regex replace
REGEXP_LIKE(s, pattern)             -- regex match (returns boolean)
RLIKE(s, pattern)                   -- same as REGEXP_LIKE
s RLIKE pattern                     -- operator form
REGEXP_COUNT(s, pattern)            -- match count
REGEXP_SUBSTR(s, pattern)           -- extract first match

-- Split
SPLIT(s, delimiter)             -- split by delimiter, returns ARRAY
SPLIT_PART(s, delimiter, n)     -- get nth split part (1-based)

-- Formatting
FORMAT_STRING(fmt, args...)     -- printf style (e.g., FORMAT_STRING('%d items', 5) → '5 items')
-- ⚠️ FORMAT(number, decimals) number thousand-separator formatting not supported, use ROUND + CAST instead

-- Encoding
BASE64(s) / UNBASE64(s)         -- Base64 encode/decode
MD5(s)                          -- MD5 hash
SHA1(s) / SHA2(s, bits)         -- SHA hash
CRC32(s)                        -- CRC32
ENCODE(s, charset) / DECODE(s, charset)  -- charset encode/decode

-- Other
ASCII(s)                        -- ASCII code of first character
CHAR(n)                         -- ASCII code to character
-- ⚠️ SOUNDEX not supported
-- ⚠️ LEVENSHTEIN not supported, use Python UDF or ZettaPark instead
HAMMING_DISTANCE(s1, s2)        -- Hamming distance (strings)
```

**Differences from Snowflake:**
- Snowflake `CHARINDEX(substr, s)` → ClickZetta `INSTR(s, substr)` or `LOCATE(substr, s)` (different parameter order!)
- Snowflake `EDITDISTANCE(s1, s2)` → ClickZetta does not support LEVENSHTEIN, use Python UDF
- Snowflake `STRTOK(s, delim, n)` → ClickZetta `SPLIT_PART(s, delim, n)`
- Snowflake `ILIKE(s, pattern)` → ClickZetta `ILIKE` ✅ also supported!
- Snowflake `CONTAINS(s, substr)` → ClickZetta `INSTR(s, substr) > 0`
- Snowflake `STARTSWITH(s, prefix)` → ClickZetta `s LIKE 'prefix%'` or `STARTSWITH(s, prefix)`
- Snowflake `ENDSWITH(s, suffix)` → ClickZetta `s LIKE '%suffix'` or `ENDSWITH(s, suffix)`

---

## Date/Time Functions

```sql
-- Get current time
CURRENT_DATE()                  -- current date
CURRENT_TIMESTAMP() / NOW()     -- current timestamp (with timezone)
CURRENT_TIME()                  -- current time
LOCALTIMESTAMP()                -- local timestamp

-- Extract parts
YEAR(dt) / MONTH(dt) / DAY(dt)
HOUR(dt) / MINUTE(dt) / SECOND(dt)
DAYOFWEEK(dt)                   -- 1=Sunday, 7=Saturday
DAYOFMONTH(dt)                  -- same as DAY
DAYOFYEAR(dt)                   -- day of year
WEEKOFYEAR(dt)                  -- week of year
QUARTER(dt)                     -- quarter (1-4)
EXTRACT(YEAR FROM dt)           -- standard SQL extraction
-- ⚠️ DATE_PART('year', dt) not supported, use EXTRACT or YEAR(dt) instead

-- Date arithmetic
DATE_ADD(dt, n)                 -- add n days
DATE_SUB(dt, n)                 -- subtract n days
dt + INTERVAL n DAY             -- add n days (standard SQL)
dt - INTERVAL n DAY             -- subtract n days
dt + INTERVAL '1-2' YEAR TO MONTH  -- add 1 year 2 months
ADDDATE(dt, n)                  -- same as DATE_ADD
SUBDATE(dt, n)                  -- same as DATE_SUB
ADD_MONTHS(dt, n)               -- add n months
MONTHS_BETWEEN(dt1, dt2)        -- month difference

-- Date difference
DATEDIFF(end_dt, start_dt)      -- two-parameter form: returns day difference (end first)
DATEDIFF(unit, start_dt, end_dt) -- three-parameter form: specify unit (day/hour/month etc.), Snowflake-compatible
TIMESTAMPDIFF(unit, dt1, dt2)   -- difference in specified unit

-- Truncation
DATE_TRUNC('year', dt)          -- truncate to year
DATE_TRUNC('month', dt)         -- truncate to month
DATE_TRUNC('day', dt)           -- truncate to day
DATE_TRUNC('hour', dt)          -- truncate to hour
DATE_TRUNC('week', dt)          -- truncate to week (Monday)
TRUNC(dt, 'MM')                 -- Oracle-style truncation

-- Formatting
DATE_FORMAT(dt, 'yyyy-MM-dd')   -- format to string
DATE_FORMAT(dt, 'yyyy-MM-dd HH:mm:ss')
TO_CHAR(dt, 'YYYY-MM-DD')       -- same as DATE_FORMAT

-- Conversion
TO_DATE('2024-01-01')           -- string to date
TO_DATE('2024-01-01', 'yyyy-MM-dd')
TO_TIMESTAMP('2024-01-01 12:00:00')
TO_TIMESTAMP('2024-01-01', 'yyyy-MM-dd')
CAST('2024-01-01' AS DATE)
CAST('2024-01-01 12:00:00' AS TIMESTAMP)
FROM_UNIXTIME(unix_ts)          -- Unix timestamp to timestamp
FROM_UNIXTIME(unix_ts, fmt)     -- to formatted string
UNIX_TIMESTAMP()                -- current Unix timestamp
UNIX_TIMESTAMP(dt)              -- date to Unix timestamp
UNIX_TIMESTAMP(s, fmt)          -- string to Unix timestamp

-- Other
LAST_DAY(dt)                    -- last day of month
NEXT_DAY(dt, 'Monday')          -- next specified day of week
MAKE_DATE(year, month, day)     -- construct date (note: MAKE_DATE not MAKEDATE)
ADD_MONTHS(dt, n)               -- add n months
MONTHS_BETWEEN(dt1, dt2)        -- month difference
TIMESTAMPDIFF(unit, dt1, dt2)   -- difference in specified unit (e.g., TIMESTAMPDIFF(MONTH, ...))
FROM_UTC_TIMESTAMP(ts, tz)      -- UTC to specified timezone
TO_UTC_TIMESTAMP(ts, tz)        -- specified timezone to UTC
-- ⚠️ CONVERT_TZ(dt, from_tz, to_tz) not supported, use FROM_UTC_TIMESTAMP/TO_UTC_TIMESTAMP instead
-- ⚠️ MAKEDATE(year, dayofyear) not supported, use MAKE_DATE(year, month, day) instead
-- ⚠️ MAKETIME / PERIOD_ADD / PERIOD_DIFF not supported
```

**Differences from Snowflake:**
- Snowflake `DATEADD(day, n, dt)` → ClickZetta `DATEADD(day, n, dt)` ✅ also supported; or use `DATE_ADD(dt, n)` / `dt + INTERVAL n DAY`
- Snowflake `DATEDIFF(day, start, end)` → ClickZetta `DATEDIFF(day, start, end)` ✅ three-parameter form also supported; or use `DATEDIFF(end, start)` two-parameter form (returns days)
- Snowflake `DATE_TRUNC('day', dt)` → ClickZetta same
- Snowflake `TO_DATE(s)` → ClickZetta same
- Snowflake `CONVERT_TIMEZONE(from, to, ts)` → ClickZetta `FROM_UTC_TIMESTAMP` / `TO_UTC_TIMESTAMP`
- Snowflake `CONVERT_TIMEZONE(tz, dt)` → ClickZetta `CONVERT_TZ(dt, from_tz, to_tz)`
- Snowflake `SYSDATE()` / `GETDATE()` → ClickZetta `CURRENT_TIMESTAMP()` / `NOW()`
- Snowflake `TIMESTAMPADD(unit, n, dt)` → ClickZetta `dt + INTERVAL n unit`

**Differences from Spark SQL:**
- Most functions are the same; ClickZetta is compatible with Spark date functions

---

## Conditional Functions

```sql
-- IF
IF(condition, true_val, false_val)

-- CASE WHEN
CASE WHEN cond1 THEN val1
     WHEN cond2 THEN val2
     ELSE default_val
END

-- Simple CASE
CASE status
    WHEN 'A' THEN 'Active'
    WHEN 'I' THEN 'Inactive'
    ELSE 'Unknown'
END

-- NULL handling
COALESCE(a, b, c)               -- first non-NULL value
NVL(a, b)                       -- return b if a is NULL (same as IFNULL)
IFNULL(a, b)                    -- same as NVL
NULLIF(a, b)                    -- return NULL if a=b, otherwise return a
NVL2(a, b, c)                   -- return b if a is not NULL, otherwise c
ISNULL(a)                       -- is NULL (returns boolean)
ISNOTNULL(a)                    -- is not NULL

-- DECODE (Oracle/Hive style)
DECODE(expr, val1, res1, val2, res2, ..., default)

-- Type checking
TYPEOF(expr)                    -- returns type name as string
```

**Differences from Snowflake:**
- Snowflake `IFF(cond, a, b)` → ClickZetta `IF(cond, a, b)`
- Snowflake `ZEROIFNULL(x)` → ClickZetta `COALESCE(x, 0)` or `NVL(x, 0)`
- Snowflake `NULLIFZERO(x)` → ClickZetta `NULLIF(x, 0)`
- Snowflake `BOOLAND(a, b)` / `BOOLOR(a, b)` → ClickZetta `a AND b` / `a OR b`

---

## Aggregate Functions

```sql
-- Basic aggregation
COUNT(*) / COUNT(col) / COUNT(DISTINCT col)
SUM(col) / AVG(col) / MAX(col) / MIN(col)
STDDEV(col) / STDDEV_POP(col) / STDDEV_SAMP(col)
VARIANCE(col) / VAR_POP(col) / VAR_SAMP(col)

-- Boolean aggregation
BOOL_OR(cond)                   -- any one is true
BOOL_AND(cond)                  -- all are true
EVERY(cond)                     -- same as BOOL_AND

-- String aggregation
GROUP_CONCAT(col ORDER BY col SEPARATOR ',')   -- replaces Snowflake LISTAGG
GROUP_CONCAT(DISTINCT col SEPARATOR ',')

-- Array aggregation
ARRAY_AGG(col)                  -- collect into array (includes NULL)
COLLECT_LIST(col)               -- same as ARRAY_AGG
COLLECT_SET(col)                -- collect deduplicated

-- Approximate aggregation
APPROX_COUNT_DISTINCT(col)      -- approximate distinct count (HyperLogLog)
APPROX_PERCENTILE(col, p)       -- approximate percentile

-- Statistical aggregation
CORR(x, y)                      -- correlation coefficient
COVAR_POP(x, y) / COVAR_SAMP(x, y)  -- covariance
-- ⚠️ REGR_SLOPE / REGR_INTERCEPT not supported
-- Alternative: CORR(y,x) * STDDEV(y) / STDDEV(x) to calculate slope

-- Ordered set aggregation
PERCENTILE(col, p)              -- exact percentile
PERCENTILE_APPROX(col, p)       -- approximate percentile
MEDIAN(col)                     -- median
```

**Differences from Snowflake:**
- Snowflake `LISTAGG(col, ',') WITHIN GROUP (ORDER BY col)` → ClickZetta `GROUP_CONCAT(col ORDER BY col SEPARATOR ',')`
- Snowflake `ARRAY_AGG(col) WITHIN GROUP (ORDER BY col)` → ClickZetta `ARRAY_AGG(col)` does not support WITHIN GROUP
- Snowflake `OBJECT_AGG(key, value)` → ClickZetta `MAP_AGG(key, value)`
- Snowflake `BITAND_AGG / BITOR_AGG / BITXOR_AGG` → ClickZetta `BIT_AND / BIT_OR / BIT_XOR`

---

## Type Conversion Functions

```sql
-- Explicit conversion
CAST(expr AS target_type)
expr::target_type               -- shorthand syntax

-- Safe conversion (returns NULL on failure instead of error)
TRY_CAST(expr AS target_type)

-- String conversion
TO_NUMBER(s) / TO_DECIMAL(s)
TO_DOUBLE(s)
TO_BOOLEAN(s)                   -- 'true'/'false'/'1'/'0'

-- Examples
CAST('123' AS INT)
CAST(123 AS STRING)
CAST('2024-01-01' AS DATE)
CAST('[1,2,3]' AS VECTOR(3))    -- string to vector
TRY_CAST('abc' AS INT)          -- returns NULL
```

**Differences from Snowflake:**
- Snowflake `TRY_TO_NUMBER / TRY_TO_DATE` → ClickZetta `TRY_CAST`
- Snowflake `TO_VARIANT(x)` → ClickZetta `PARSE_JSON(TO_JSON(x))`

---

## System/Context Functions

```sql
CURRENT_USER()                  -- current username
CURRENT_WORKSPACE()             -- current workspace
CURRENT_SCHEMA()                -- current schema
CURRENT_VCLUSTER()              -- current compute cluster
CURRENT_INSTANCE_ID()           -- current instance ID
VERSION()                       -- version information
```

**Differences from Snowflake:**
- Snowflake `CURRENT_DATABASE()` → ClickZetta `CURRENT_WORKSPACE()`
- Snowflake `CURRENT_WAREHOUSE()` → ClickZetta `CURRENT_VCLUSTER()`
- Snowflake `CURRENT_ROLE()` → ClickZetta has no direct equivalent

---

## Vector Functions

```sql
-- Distance calculation
L2_DISTANCE(v1, v2)             -- Euclidean distance (smaller = more similar)
COSINE_DISTANCE(v1, v2)         -- Cosine distance (smaller = more similar)
DOT_PRODUCT(v1, v2)             -- Dot product (larger = more similar, requires normalization)
HAMMING_DISTANCE(v1, v2)        -- Hamming distance (binary vectors)
JACCARD_DISTANCE(v1, v2)        -- Jaccard distance

-- Vector operations
BINARY_QUANTIZE(v)              -- binarize float vector
VECTOR(v1, v2, ...)             -- build vector

-- Build vector
SELECT VECTOR(0.1, 0.2, 0.3, 0.4);
SELECT CAST('[0.1, 0.2, 0.3]' AS VECTOR(3));
```
