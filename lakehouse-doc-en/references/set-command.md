# SET

The `SET` command sets SQL engine parameters for the current session. Parameters take effect only within the **current session** and revert to their default values when the session ends.

## Syntax

```Plain
SET <parameter_name> = <value>
```

> ⚠️ **Note**: `SET` affects only the current session and does not impact other users or future sessions. To persistently configure object properties, use [SET PROPERTIES](set-properties.md).

## Session Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `query_tag` | string | none | Tags queries with a label that can be filtered in job history |
| `schedule_job_queue_priority` | 0–9 | 0 | Job priority; higher values mean higher priority |
| `cz.sql.group.by.having.use.alias.first` | true/false | false | Whether GROUP BY / HAVING prefers column aliases |
| `cz.sql.double.quoted.identifiers` | true/false | false | Whether double quotes act as delimited identifiers (when enabled, double quotes no longer represent strings) |
| `cz.sql.cast.mode` | tolerant/strict | tolerant | CAST conversion mode; in strict mode, conversion failures throw an error |
| `cz.optimizer.enable.mv.rewrite` | true/false | false | Whether to enable Materialized View query rewriting |
| `cz.sql.string.literal.escape.mode` | backslash/quote/quote_backslash | backslash | String escape character mode |
| `cz.sql.arithmetic.mode` | tolerant/strict | tolerant | Whether arithmetic errors throw an exception |
| `cz.sql.timezone` | timezone name | none | Sets the SQL session timezone, e.g. `Asia/Shanghai` or `UTC` |
| `cz.sql.remote.udf.lookup.policy` | builtin_first/udf_first/schema_only | schema_only | Resolution priority between UDFs and built-in functions |
| `cz.sql.type.conversion` | hive | none | Enables Hive-compatible type conversion rules |
| `cz.sql.function.from.unixtime.trim.to.second` | false/true | false | Truncates FROM_UNIXTIME precision to seconds (Hive compatibility) |
| `cz.sql.time.parser.strict.mode` | false/true | false | Strict time parsing mode; throws an error instead of returning NULL when format does not match |
| `cz.sql.cast.string.to.integer.allow.truncate` | false/true | false | Allows truncating decimal digits when casting string to integer (Hive compatibility) |
| `cz.sql.translation.mode` | postgresql/mysql/doris/hive/presto | none | Automatic SQL dialect translation mode (preview feature) |
| `cz.sql.compatible.target` | mysql/pg | none | Specifies the target engine for function compatibility (used with translation.mode) |

## Examples

```SQL
-- Set timezone
SET cz.sql.timezone = 'Asia/Shanghai';

-- Set query tag
SET query_tag = 'etl_job';

-- Enable strict CAST mode
SET cz.sql.cast.mode = strict;

-- Set job priority
SET schedule_job_queue_priority = 5;
```

## Setting Parameters in the Python SDK

```python
from clickzetta import connect

conn = connect(username='', password='', service='...', instance='...', workspace='...', schema='public', vcluster='DEFAULT')
my_param = {'hints': {'cz.sql.timezone': 'UTC+00'}}
cursor = conn.cursor()
cursor.execute("SELECT current_timestamp();", my_param)
```

## Setting Parameters in a JDBC URL

```
jdbc:clickzetta://instance.region.api.clickzetta.com/workspace?schema=public&query_tag=my_app
```

---

## Parameter Details

### query_tag

Once set, all query jobs in the session are tagged with this label, which you can filter in job history:

```SQL
SET query_tag = 'aa';
SELECT 1;

-- Filter in information_schema
SELECT * FROM information_schema.job_history WHERE query_tag = 'aa';

-- Filter in SHOW JOBS
SHOW JOBS WHERE query_tag = 'aa' LIMIT 100;
```

### cz.sql.double.quoted.identifiers

When enabled, double quotes act as delimited identifiers and **no longer represent strings**:

```SQL
SET cz.sql.double.quoted.identifiers = true;
-- "column_name" is now an identifier, not a string
```

### cz.sql.cast.mode

```SQL
-- strict mode: conversion failure throws an error
SET cz.sql.cast.mode = strict;
SELECT CAST('abc' AS INT);  -- error

-- tolerant mode (default): conversion failure returns NULL
SET cz.sql.cast.mode = tolerant;
SELECT CAST('abc' AS INT);  -- NULL
```

### cz.sql.arithmetic.mode

```SQL
-- tolerant mode (default): division by zero returns NULL
SELECT 2/0;  -- NULL

-- strict mode: division by zero throws an error
SET cz.sql.arithmetic.mode = strict;
SELECT 2/0;  -- error
```

### cz.sql.timezone

```SQL
SET cz.sql.timezone = 'Asia/Shanghai';
SELECT NOW();  -- returns time in Asia/Shanghai

SET cz.sql.timezone = 'UTC';
SELECT NOW();  -- returns UTC time
```

### cz.sql.string.literal.escape.mode

```SQL
-- Default backslash mode
SELECT 'Hello \n World!';  -- newline

-- quote mode: use two single quotes to represent one single quote
SET cz.sql.string.literal.escape.mode = QUOTE;
SELECT 'It''s a beautiful day';  -- It's a beautiful day

-- quote_backslash mode: supports both escape styles simultaneously
SET cz.sql.string.literal.escape.mode = quote_backslash;
```

### cz.sql.translation.mode (preview feature)

Automatically translates the specified SQL dialect into native Lakehouse syntax:

```SQL
SET cz.sql.translation.mode = doris;
SELECT DATE_ADD(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR);

-- Used with compatible.target
SET cz.sql.compatible.target = mysql;
SELECT DATE_FORMAT(CURRENT_DATE(), '%x-%v %a %W');
```

### cz.sql.remote.udf.lookup.policy

```SQL
-- Default schema_only: UDFs must be referenced with a schema prefix
SELECT public.my_func();

-- builtin_first: built-in functions take priority
SET cz.sql.remote.udf.lookup.policy = builtin_first;
SELECT my_func();

-- udf_first: UDFs take priority
SET cz.sql.remote.udf.lookup.policy = udf_first;
SELECT my_func();
```

### schedule_job_queue_priority

```SQL
-- Set high priority (0–9, higher value = higher priority)
SET schedule_job_queue_priority = 8;
SELECT * FROM large_table;
```

### cz.sql.time.parser.strict.mode

```SQL
SET cz.sql.time.parser.strict.mode = true;
SELECT TO_TIMESTAMP('2025-08-01', 'yyyy-MM-dd HH');  -- error (format mismatch)

SET cz.sql.time.parser.strict.mode = false;
SELECT TO_TIMESTAMP('2025-08-01', 'yyyy-MM-dd HH');  -- NULL
```

### cz.sql.cast.string.to.integer.allow.truncate

```SQL
SELECT CAST('11.4' AS INT);  -- NULL (default)

SET cz.sql.cast.string.to.integer.allow.truncate = true;
SELECT CAST('11.4' AS INT);  -- 11 (decimal truncated)
```

## Related Documentation

- [SET PROPERTIES](set-properties.md)
- [Data Type Conversion](datatype-conversion.md)
