# Spark SQL Migration Guide

This document provides a complete guide for migrating from Spark SQL to Lakehouse, covering migration assessment, type mapping, syntax differences, function compatibility, and UDF migration.

## Migration Complexity Assessment

Lakehouse data types, DDL, DML, SELECT syntax, and the vast majority of high-frequency functions are compatible with Spark. For pure SQL ETL and analytics jobs, migration typically requires only minor changes.

**Except for Python/Java UDFs, all migration items are one-time batch replacements or simple rewrites — no logic restructuring required.**

The effort for UDF migration depends on the number of functions — each Python/Java UDF needs to be individually packaged and deployed to a cloud function service. This is the only part of the migration that requires significant investment. If UDF logic can be expressed in SQL, rewriting as a SQL Function significantly reduces the workload.

### Quick Self-Assessment Checklist

Review your job code against the table below to quickly estimate migration effort before starting.

| Check item (search in codebase) | Lakehouse behavior | Usage frequency impact | Effort |
|---|---|---|---|
| None of the items below | DDL, SELECT, UPDATE/DELETE/MERGE fully compatible | — | None |
| `spark.udf.register` / Python UDF / Java UDF | Must be rewritten as External Function, deployed to cloud function service | More UDFs = linearly more work | High |
| `CREATE TEMP VIEW` / `CREATE TEMPORARY VIEW` | Session-level temporary views not supported; must change to CTE or persistent VIEW | High usage means more rewrites, but each change is simple | Low–Medium |
| `aggregate(` / `reduce(` / `session_window(` / `window(` | No equivalent functions; must be manually rewritten | Occasional use has limited impact; core logic dependency requires redesign | Medium |
| SQL UDF (`CREATE FUNCTION`) | Calls require Schema prefix, or configure lookup policy | High-frequency calls can be resolved once with `udf_first` | Low |
| `LATERAL VIEW posexplode` | This syntax not supported; must change to table function syntax | Usually few occurrences; replace one by one | Low |
| `PARTITIONED BY` clause in CTAS | CTAS does not support this clause; must split into CREATE TABLE + INSERT | Usually few occurrences; replace one by one | Low |
| Read/write via Spark Connector | Types auto-mapped; no code changes needed | — | None |

> Except for UDFs, all items in the table have "Low" or "None" effort. Detailed explanations and rewrite examples for each item are in the corresponding sections of this document.

## Type Mapping

When reading and writing data via Spark Connector, Spark types are automatically mapped to Lakehouse types — no manual code changes required.

### Type Mapping Table

| Spark type | Lakehouse type | Notes |
|-----------|---------------|------|
| `BooleanType` | `BOOLEAN` | Auto-mapped |
| `ByteType` | `TINYINT` | Auto-mapped |
| `ShortType` | `SMALLINT` | Auto-mapped |
| `IntegerType` | `INT` | Auto-mapped |
| `LongType` | `BIGINT` | Auto-mapped |
| `FloatType` | `FLOAT` | Auto-mapped |
| `DoubleType` | `DOUBLE` | Auto-mapped |
| `DecimalType` | `DECIMAL(p,s)` | Auto-mapped, precision preserved |
| `StringType` | `STRING` | Auto-mapped |
| `BinaryType` | `BINARY` | Auto-mapped |
| `DateType` | `DATE` | Auto-mapped |
| `TimestampType` | `TIMESTAMP_LTZ` | Timezone-aware type |
| `TimestampNTZType` | `TIMESTAMP_NTZ` | Timezone-naive type (Spark 3.4+) |
| `ArrayType` | `ARRAY<T>` | Auto-mapped, element types recursively mapped |
| `MapType` | `MAP<K,V>` | Auto-mapped, key/value types recursively mapped |
| `StructType` | `STRUCT<...>` | Auto-mapped, field types recursively mapped |

### Timestamp Timezone Notes

Spark's `TimestampType` is timezone-aware by default, corresponding to Lakehouse's `TIMESTAMP_LTZ`. If Spark code uses `TimestampNTZType` (timezone-naive), use `TIMESTAMP_NTZ` when creating tables in Lakehouse to avoid time value shifts from timezone conversion.

## DDL Syntax

### CREATE TABLE Syntax

Spark's CREATE TABLE syntax is highly compatible in Lakehouse. The following syntax is all supported and requires no changes during migration:

```sql
-- Comment syntax
CREATE TABLE orders (
  id INT COMMENT 'primary key',
  name STRING COMMENT 'name'
) COMMENT 'orders table';

-- NOT NULL constraint
CREATE TABLE users (id INT NOT NULL, name STRING);

-- Default values
CREATE TABLE tasks (id INT, status STRING DEFAULT 'pending');

-- Generated columns
CREATE TABLE order_items (
  id INT, price DOUBLE, quantity INT,
  total DOUBLE GENERATED ALWAYS AS (price * quantity)
);

-- Table properties
CREATE TABLE events (id INT) TBLPROPERTIES ('key1' = 'value1');

-- Conditional table creation
CREATE TABLE IF NOT EXISTS backup_table AS SELECT * FROM original_table;
```

### Partitioned Tables

Spark's partition syntax is fully compatible in Lakehouse — no changes needed during migration.

```sql
-- Spark original syntax, fully supported in Lakehouse
CREATE TABLE orders (
  order_id INT,
  customer_id INT,
  amount DOUBLE
) PARTITIONED BY (order_date STRING);
```

Lakehouse additionally supports Iceberg-style partition syntax where the partition column appears in the column list, making semantics clearer:

```sql
-- Lakehouse recommended syntax (Iceberg style)
CREATE TABLE orders (
  order_id INT,
  customer_id INT,
  amount DOUBLE,
  order_date STRING        -- partition column in column list
) PARTITIONED BY (order_date);  -- only declare column name here
```

Both syntaxes produce the same result. Keep the original syntax during migration; use Iceberg style for new tables.

### CTAS

CTAS (Create Table As Select) syntax is mostly compatible in Lakehouse, with the following differences:

**`USING` keyword is optional**

```sql
-- Spark
CREATE TABLE orders_ctas
USING parquet
AS SELECT * FROM orders;

-- Lakehouse (USING can be kept or omitted)
CREATE TABLE orders_ctas
AS SELECT * FROM orders;
```

**CTAS does not support partition clause**

Lakehouse's CTAS syntax does not support the `PARTITIONED BY` clause. To create a partitioned table, create the table first then insert data:

```sql
-- Wrong: CTAS does not support PARTITIONED BY
CREATE TABLE orders_partitioned
PARTITIONED BY (order_date)
AS SELECT * FROM orders;

-- Correct: create table first, then insert
CREATE TABLE orders_partitioned (
  order_id INT,
  customer_id INT,
  amount DOUBLE,
  order_date STRING
) PARTITIONED BY (order_date);

INSERT INTO orders_partitioned
SELECT * FROM orders;
```

### Bucketed Tables

Bucketed table syntax is identical to Spark — no changes needed:

```sql
-- Identical syntax in Spark and Lakehouse
CREATE TABLE users (
  id INT,
  name STRING
) CLUSTERED BY (id) INTO 16 BUCKETS;
```

The `USING parquet` keyword is also optional in Lakehouse.

### Partition Transform Functions

Lakehouse is fully consistent with Spark on partition transform functions — no code changes needed:

| Function | Purpose |
|------|------|
| `years(ts)` | Partition by year |
| `months(ts)` | Partition by month |
| `days(ts)` | Partition by day |
| `hours(ts)` | Partition by hour |
| `bucket(N, col)` | Hash bucketing |
| `truncate(col, W)` | Truncate partitioning |

### Hidden Partitioning

Lakehouse uses a hidden partitioning mechanism similar to Apache Iceberg:

- Partition information is stored in metadata, not dependent on file paths
- Partition strategy can be changed at any time without rewriting data
- No limit on the number of partitions
- The optimizer automatically performs partition pruning at query time

### Dynamic Partition Limit

Lakehouse supports a maximum of 2048 dynamic partitions per task. If the partition count exceeds this limit, consider writing in batches or using Cluster Key instead of partitioning.

## DML Syntax

### INSERT

```sql
-- Fully compatible
INSERT INTO orders VALUES (1, 100, '2024-01-15');
INSERT INTO orders SELECT * FROM staging_orders;
```

### INSERT OVERWRITE

Lakehouse supports three `INSERT OVERWRITE` modes, but the default semantics differ from Spark — pay attention during migration:

**Overwrite the entire table**

```sql
-- Clear the table and write new data
INSERT OVERWRITE orders VALUES (1, 100, '2024-01-15');
```

**Static partition overwrite**

```sql
-- Overwrite only the specified partition; other partitions are unaffected
INSERT OVERWRITE orders PARTITION (order_date='2024-01-15')
SELECT order_id, customer_id, amount FROM staging WHERE order_date='2024-01-15';
```

**Dynamic partition overwrite**

Without specifying a partition value, the system automatically overwrites all partitions touched by this write; untouched partitions are preserved. This is consistent with Spark's `spark.sql.sources.partitionOverwriteMode=dynamic` behavior:

```sql
-- Overwrite only partitions present in the SELECT result; other partitions are preserved
INSERT OVERWRITE orders
SELECT order_id, customer_id, amount, order_date FROM staging;
```

> ⚠️ Note: Spark 2.x defaults `partitionOverwriteMode` to `static` (overwrite entire table); Spark 3.x changed the default to `dynamic`. Lakehouse's `INSERT OVERWRITE` defaults to dynamic partition overwrite semantics, consistent with Spark 3.x. When migrating from Spark 2.x, if the original code relies on static mode (full table overwrite), change to `TRUNCATE TABLE` + `INSERT INTO`.

### UPDATE / DELETE

```sql
-- Fully compatible
UPDATE orders SET status = 'shipped' WHERE id = 1;
DELETE FROM orders WHERE status = 'cancelled';
```

### MERGE INTO

```sql
-- Fully compatible
MERGE INTO orders AS target
USING staging_orders AS source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET target.amount = source.amount
WHEN NOT MATCHED THEN INSERT (id, amount, order_date) VALUES (source.id, source.amount, source.order_date);
```

## SELECT Queries

### Fully Compatible Syntax

The following common Spark SQL syntax is fully compatible in Lakehouse — no changes needed:

| Syntax | Example | Status |
|------|------|------|
| Backtick column references | ``SELECT `id`, `name` FROM t`` | ✅ |
| String concatenation | `SELECT 'Hello' \|\| ' ' \|\| 'World'` | ✅ |
| CASE WHEN | `CASE WHEN x > 0 THEN 'positive' END` | ✅ |
| GROUP BY positional reference | `GROUP BY 1, 2` | ✅ |
| ORDER BY positional reference | `ORDER BY 1 DESC` | ✅ |
| HAVING with alias | `HAVING total > 100` | ✅ |
| LIMIT | `LIMIT 10` | ✅ |
| VALUES clause | `SELECT * FROM VALUES (1, 'a'), (2, 'b') AS t(id, name)` | ✅ |
| JOIN ... USING | `JOIN b USING (id)` | ✅ |
| CROSS JOIN | `CROSS JOIN` | ✅ |
| RLIKE / REGEXP | `'abc' RLIKE '^[a-z]+$'` | ✅ |
| NULLIF / NVL | `NULLIF(a, b)`, `NVL(col, 'default')` | ✅ |
| EXCEPT / INTERSECT | `SELECT ... EXCEPT SELECT ...` | ✅ |
| QUALIFY | `QUALIFY ROW_NUMBER() = 1` | ✅ |
| Implicit type conversion | `WHERE str_col = 123` | ✅ |
| Division by zero | `SELECT 1/0` → `NULL` | ✅ |

### Correlated Subqueries

Lakehouse fully supports correlated subqueries, including referencing outer columns in `EXISTS`/`NOT EXISTS`. Syntax is identical to Spark — no changes needed:

```sql
-- Fully compatible, no rewrite needed
SELECT id FROM orders a
WHERE EXISTS (SELECT 1 FROM customers b WHERE b.id = a.customer_id);

SELECT id FROM orders a
WHERE NOT EXISTS (SELECT 1 FROM blacklist b WHERE b.order_id = a.id);
```

## Window Functions

Lakehouse is fully compatible with Spark SQL window functions — syntax is identical:

```sql
SELECT
  id,
  amount,
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) AS rn,
  SUM(amount) OVER (PARTITION BY user_id ORDER BY created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM orders;
```

Supported window functions: `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`, `LAG()`, `LEAD()`, `FIRST_VALUE()`, `LAST_VALUE()`, `NTILE()`, `SUM() OVER()`, `AVG() OVER()`, and more.

## Table-Generating Functions

Lakehouse supports common Spark table-generating functions:

| Function | Supported | Notes |
|------|------|------|
| `explode()` | ✅ | Fully compatible; supports both `LATERAL VIEW` and table function syntax |
| `posexplode()` | ⚠️ | `AS (pos, val)` alias syntax supported; `LATERAL VIEW ... AS pos, val` syntax not supported — see below |
| `inline()` | ✅ | Direct call |
| `stack()` | ✅ | Direct call |
| `json_tuple()` | ✅ | Fully compatible; supports `LATERAL VIEW` syntax |

```sql
-- explode: both syntaxes supported
SELECT id, item FROM orders LATERAL VIEW explode(items) t AS item;
SELECT id, item FROM orders, explode(items) AS t(item);

-- posexplode: AS (pos, val) alias syntax supported
SELECT pos, val FROM posexplode(ARRAY('a', 'b', 'c')) AS t(pos, val);
-- Returns: (0,'a'), (1,'b'), (2,'c')

-- posexplode: LATERAL VIEW AS pos, val syntax not supported; must rewrite
-- Spark syntax (not supported):
-- SELECT pos, val FROM t LATERAL VIEW posexplode(items) tmp AS pos, val
-- Lakehouse rewrite:
SELECT pos, val FROM t, posexplode(items) AS tmp(pos, val);

-- inline/stack/json_tuple: direct calls
SELECT inline(ARRAY(named_struct('a', 1), named_struct('a', 2)));
SELECT stack(2, 'a', 1, 'b', 2);
SELECT a, b FROM json_tuple('{"a":1,"b":2}', 'a', 'b') AS j(a, b);
```

## JSON Processing Functions

| Spark function | Lakehouse function | Notes |
|-----------|---------------|------|
| `from_json(str, schema)` | `from_json(str, schema)` | ✅ Fully compatible, returns STRUCT type |
| `to_json(struct)` | `to_json(expr)` | ✅ Fully compatible |
| `get_json_object(str, path)` | `get_json_object(str, path)` | ✅ Fully compatible |
| `json_tuple(str, path1, path2)` | `json_tuple(str, path1, path2)` | ✅ Fully compatible |
| `parse_json(str)` | `parse_json(str)` | ✅ Lakehouse-specific, returns JSON type |

```sql
-- from_json fully compatible
SELECT from_json('{"a":1}', 'a INT').a;

-- get_json_object fully compatible
SELECT get_json_object('{"a":{"b":123}}', '$.a.b');

-- parse_json also available (returns JSON type)
SELECT parse_json('{"a":1}')['a'];
```

## Temporary Views and CTEs

### Temporary Views

Lakehouse **does not support** `TEMPORARY VIEW` / `TEMP VIEW` syntax — this is an important difference from Spark.

Spark's TEMP VIEW is a session-level object that is automatically destroyed when the session ends. Lakehouse has no equivalent session-level view. Two options for migration:

**Option 1: Change to a persistent VIEW (suitable for logic reused multiple times)**

```sql
-- Spark
CREATE OR REPLACE TEMP VIEW temp_orders AS SELECT * FROM orders WHERE status = 'active';

-- Lakehouse: change to a persistent view; requires write permission on the Schema
CREATE OR REPLACE VIEW my_schema.temp_orders AS SELECT * FROM orders WHERE status = 'active';
```

> ⚠️ Persistent VIEWs are written to the Schema and are not automatically cleaned up when the session ends. They must be manually `DROP VIEW`'d or managed through table lifecycle policies.

**Option 2: Change to a CTE (suitable for temporary logic within a single query)**

```sql
-- Spark
CREATE OR REPLACE TEMP VIEW daily_orders AS
  SELECT order_date, SUM(amount) AS total FROM orders GROUP BY order_date;

SELECT * FROM daily_orders WHERE total > 1000;

-- Lakehouse: change to CTE, logic inlined in the query
WITH daily_orders AS (
  SELECT order_date, SUM(amount) AS total FROM orders GROUP BY order_date
)
SELECT * FROM daily_orders WHERE total > 1000;
```

The CTE approach requires no permissions and creates no persistent objects — it is the simplest replacement.

### CTEs (WITH Clause)

CTE syntax is identical to Spark — no changes needed.

## Function Compatibility

### Fully Compatible Functions

The following common Spark SQL functions are fully compatible in Lakehouse:

**Array functions**: `split`, `regexp_replace`, `regexp_extract`, `concat_ws`, `size`, `array_sort`, `sort_array`, `array_contains`, `array_position`, `slice`, `sequence`, `flatten`, `arrays_zip`, `array_repeat`, `array_distinct`, `array_union`, `array_intersect`, `array_except`, `arrays_overlap`, `array_min`, `array_max`, `array_join`, `array_remove`, `cardinality`, `reverse`, `element_at`

**Map functions**: `map_keys`, `map_values`, `map_from_arrays`, `map_concat`, `str_to_map`, `map_filter`, `transform_keys`, `transform_values`, `map_zip_with`, `map_from_entries`, `element_at`

**Higher-order functions**: `transform`, `filter`, `exists`, `forall`, `zip_with`

**Aggregate functions**: `collect_list`, `collect_set`, `first`, `last`, `approx_count_distinct`, `percentile`, `percentile_approx`, `corr`, `covar_pop`, `covar_samp`

**String functions**: `split`, `regexp_replace`, `regexp_extract`, `concat_ws`

**Date functions**: `date_format`, `to_date`, `current_date`, `current_timestamp`

**Conditional functions**: `CASE WHEN`, `NULLIF`, `NVL`, `IFNULL`, `COALESCE`, `TRY_CAST`, `TRY_ELEMENT_AT`

**Other functions**: `typeof`, `named_struct`, `monotonically_increasing_id`, `current_database`, `current_schema`, `current_user`, `version`, `raise_error`, `assert_true`, `aes_encrypt`, `aes_decrypt`

### Unsupported Functions

The following Spark SQL functions are not supported in Lakehouse and must be replaced during migration:

| Spark function | Alternative | Notes |
|-----------|---------|------|
| `aggregate(arr, init, merge)` | Use subquery or UDF | Array aggregation |
| `reduce(arr, init, merge)` | Same as above | Array reduction |
| `nanvl(x, y)` | `CASE WHEN isnan(x) THEN y ELSE x END` | NaN handling |
| `bin(n)` | `conv(n, 10, 2)` | Binary conversion |
| `hash(x)` | `murmurhash3_32(x)` or `sha2(x, 256)` | Hash function |
| `xxhash64(x)` | `murmurhash3_32(x)` | 64-bit hash |
| `shuffle(arr)` | Not supported | Random array shuffle |
| `array_sort(arr, comparator)` | Single-argument version only | Custom sort |
| `soundex(str)` | Not supported | Phonetic encoding |
| `levenshtein(s1, s2)` | Not supported | Edit distance |
| `overlay(str, replace, pos)` | Not supported | String replacement |
| `sentences(str)` | Not supported | Sentence splitting |
| `session_window(ts, gap)` | Manually compute using `LAG`/`LEAD` | Session window |
| `window(ts, interval)` | Not supported | Time window |
| `width_bucket(v, min, max, n)` | Not supported | Bucketing function |
| `histogram_numeric(col, n)` | Not supported | Numeric histogram |
| `kurtosis(col)` | Not supported | Kurtosis |
| `skewness(col)` | Not supported | Skewness |
| `reflect(class, method, args)` | Not supported | Java reflection |
| `java_method(class, method, args)` | Not supported | Java method call |
| `xpath_string(xml, xpath)` | Not supported | XML parsing |
| `input_file_name()` | Not supported | File name |
| `input_file_block_start()` | Not supported | File block start |
| `spark_partition_id()` | Not supported | Spark partition ID |
| `entries_to_map(keys, values)` | `map_from_arrays(keys, values)` | Map construction |
| `length(array)` | `size(array)` or `cardinality(array)` | Array length |

## UDF Migration

Spark supports multiple UDF types. Lakehouse provides two corresponding mechanisms: **SQL Function** (pure SQL logic) and **External Function** (Python/Java code).

### Migration Comparison

| Spark UDF type | Typical syntax | Lakehouse equivalent | Migration complexity |
|---------------|---------|---------------|-----------|
| SQL UDF (pure expression) | `CREATE FUNCTION f(x INT) RETURNS INT RETURN x * 2` | SQL Function | Low; syntax mostly identical |
| Python UDF (scalar) | `spark.udf.register("f", lambda x: x*2, IntegerType())` | External Function (Python, UDF only) | Medium; must deploy to cloud function service |
| Java UDF | Implement `UDF1<T,R>` etc. or extend Hive `GenericUDF`/`UDF` | External Function (Java) | Medium; must package and deploy; Hive API code can be partially reused |
| Java UDAF | Extend `Aggregator` or `UserDefinedAggregateFunction` | External Function (Java UDAF) | High; aggregation logic must be rewritten |
| Java UDTF | Extend `GenericUDTF` | External Function (Java UDTF) | High; table function logic must be rewritten |
| Python UDAF / Python UDTF | pandas_udf aggregation, yield multiple rows | Not supported; must rewrite in Java or change to SQL Function | High |

### SQL Function (Pure SQL Logic)

Spark SQL UDFs can be directly migrated to Lakehouse SQL Functions — syntax is highly compatible:

```sql
-- Spark SQL UDF
CREATE FUNCTION multiply(x INT, y INT) RETURNS INT RETURN x * y;

-- Lakehouse SQL Function (same syntax)
CREATE FUNCTION my_schema.multiply(x INT, y INT) RETURNS INT RETURN x * y;
```

**Key difference from Spark: Schema prefix required**

Lakehouse SQL Functions are Schema-level objects; calls require a Schema prefix by default:

```sql
-- Error: function not found
SELECT multiply(3, 4);

-- Correct: add Schema prefix
SELECT my_schema.multiply(3, 4);
```

If the original Spark code calls UDFs without a prefix extensively, enable UDF-first lookup to make prefix-free calls work:

```sql
-- After enabling, prefix-free function names are looked up in user UDFs first, then built-in functions
SET cz.sql.remote.udf.lookup.policy = udf_first;

-- Can then call without prefix
SELECT multiply(3, 4);
```

> ⚠️ In `udf_first` mode, if a UDF name matches a built-in function, the UDF overrides the built-in. It is recommended to prefix UDF names with a business identifier (e.g., `biz_multiply`) to avoid conflicts.

SQL Functions also support table functions (returning multiple rows), corresponding to Spark UDTF scenarios expressible in pure SQL:

```sql
-- SQL Function returning multiple rows (table function)
CREATE FUNCTION my_schema.get_employees(dept INT)
RETURNS TABLE(name STRING)
RETURN SELECT name FROM employee WHERE deptno = dept;

SELECT * FROM my_schema.get_employees(10);
```

### External Function (Python/Java Code)

Spark's Python UDFs and Scala/Java UDFs must be migrated to Lakehouse External Functions. External Functions deploy function logic to a cloud function service (Alibaba Cloud FC, Tencent Cloud SCF, or AWS Lambda); Lakehouse calls them via HTTP.

**Supported scope:**
- Python 3.10: UDF (scalar functions) only
- Java 8: UDF, UDAF (aggregate functions), UDTF (table functions)

**Migration steps overview:**

1. Rewrite UDF code as a cloud function Handler (Python 3.10 or Java 8 Hive-style UDF)
2. Package and upload to object storage or a Lakehouse Volume
3. Create an API Connection in Lakehouse (stores cloud function service authentication)
4. Create an External Function and bind the Connection

```sql
-- Step 4: Create External Function (Java UDF example)
CREATE EXTERNAL FUNCTION my_schema.my_upper
  AS 'com.example.GenericUdfUpper'
  USING ARCHIVE 'volume://fc_volume/udfs/my_upper.zip'
  CONNECTION my_fc_conn
  WITH PROPERTIES ('remote.udf.api' = 'java8.hive2.v0');

-- Call the same way as a regular function (Schema prefix required)
SELECT my_schema.my_upper(name) FROM users;
```

```sql
-- Python UDF example
CREATE EXTERNAL FUNCTION my_schema.clean_phone
  AS 'handler.clean_phone'
  USING FILE 'volume:user://~/clean_phone.zip'
  CONNECTION my_fc_conn
  WITH PROPERTIES ('remote.udf.api' = 'python3.mc.v0');

SELECT my_schema.clean_phone(phone_number) FROM users;
```

> ⚠️ External Function creation syntax differs from SQL Function — parameter types and return types are not declared in the DDL; types are handled internally by the function code. See [CREATE EXTERNAL FUNCTION](create_external_function.md).

### Session-Level UDF Registration

Spark supports dynamically registering UDFs on the Driver (`spark.udf.register`), making them immediately available in the current session. Lakehouse has no equivalent session-level registration mechanism — all functions are persistent Schema objects.

During migration, change `spark.udf.register` registration logic to `CREATE OR REPLACE FUNCTION`, executed once in the deployment script or initialization phase.

## Configuration Parameters

Spark's query optimization parameters are automatically managed by Lakehouse — no manual configuration needed:

| Spark configuration | Lakehouse behavior |
|-----------|---------------|
| `spark.sql.adaptive.enabled` | Adaptive query optimization enabled by default |
| `spark.sql.shuffle.partitions` | Parallelism automatically managed |
| `spark.sql.broadcastTimeout` | Broadcast Join automatically handled |
| `spark.sql.files.maxPartitionBytes` | File splitting automatically optimized |

## DataFrame Write Limitations

When writing to Lakehouse via Spark Connector, note the following limitations:

- Must write all columns; partial column writes are not supported
- Writing to tables with primary keys (PK tables) is not supported
- Write mode supports `append` only; `overwrite` for single partition is not supported

## Migration Checklist

- [ ] Confirm `TimestampType` maps to `TIMESTAMP_LTZ`; `TimestampNTZType` maps to `TIMESTAMP_NTZ`
- [ ] CTAS: `PARTITIONED BY` not supported; split into CREATE TABLE + INSERT
- [ ] `INSERT OVERWRITE`: Lakehouse defaults to dynamic partition overwrite; if original code relies on Spark 2.x static mode (full table overwrite), change to `TRUNCATE TABLE` + `INSERT INTO`
- [ ] `TEMP VIEW`: Not supported; change to persistent `VIEW` or inline `CTE`
- [ ] `posexplode` with `LATERAL VIEW ... AS pos, val` syntax not supported; change to table function syntax `FROM t, posexplode(col) AS tmp(pos, val)`
- [ ] Function compatibility: Check for unsupported functions (e.g., `aggregate`, `reduce`, `hash`, `shuffle`, `session_window`, `window`, `levenshtein`, `overlay`, etc.) — see Function Compatibility section
- [ ] DataFrame writes: Confirm full-column writes; do not use PK tables
- [ ] Dynamic partitions: Confirm single-task partition count does not exceed 2048
- [ ] SQL UDF: Calls require Schema prefix, or configure `cz.sql.remote.udf.lookup.policy = udf_first` for prefix-free compatibility
- [ ] Python/Scala/Java UDF: Migrate to External Function; deploy to cloud function service and create API Connection
- [ ] `spark.udf.register` dynamic registration: Change to `CREATE OR REPLACE FUNCTION`, executed once in deployment script

## Related Documentation

- [PySpark → ZettaPark Migration: F1 Racing Data Engineering Project](pyspark-to-zettapark-migration-f1.md): Complete migration case with 4 required changes and migration notes, 71/71 verified
- [Build a Medallion Three-Layer Warehouse from Scratch on Lakehouse](medallion-lakehouse-from-scratch.md): Bronze → Silver → Gold modeling practice with surrogate key generation and 22 automated validations
- [Data Type Compatibility Reference](migration-sql-compatibility.md): MySQL/PostgreSQL/Hive/Spark type mapping
- [Data Type Conversion](datatype-conversion.md): Explicit and implicit conversion rules
- [Using Spark Connector](spark-connector-use.md): Spark Connector configuration and read/write examples
- [Spark Connector Introduction](spark-connector-summary.md): Spark Connector overview
- [SQL Function](create-sql-function.md): Syntax reference for creating pure SQL UDFs, including `cz.sql.remote.udf.lookup.policy` configuration
