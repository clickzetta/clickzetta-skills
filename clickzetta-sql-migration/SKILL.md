---
name: clickzetta-sql-migration
description: |
  Migration guide for SQL workloads moving to ClickZetta Lakehouse from Snowflake,
  Databricks, or Spark SQL. Covers object concept mapping, syntax differences,
  function mapping tables, MERGE INTO limitations, the strict implicit type
  conversion rule, and migration pitfalls. Use this skill ONLY for migration or
  cross-platform comparison questions. For native ClickZetta SQL syntax (DDL,
  DML, DQL, functions) reference the ClickZetta Lakehouse documentation.
  Triggered when the user mentions migration source platforms (Snowflake,
  Databricks, Delta Lake, Spark SQL) together with ClickZetta, asks "how do I
  write X (from Snowflake/Spark) in ClickZetta", asks about specific Snowflake
  or Spark functions/syntax (IFF, ARRAY_SIZE, LISTAGG, FLATTEN, METADATA$ACTION,
  TARGET_LAG, APPLY CHANGES INTO, ZORDER, WITH RECURSIVE, WHEN NOT MATCHED BY
  SOURCE, OBJECT_CONSTRUCT, VARIANT colon syntax, CHARINDEX, ZEROIFNULL,
  DATEADD/DATEDIFF parameter order), asks about implicit type conversion errors,
  or asks about compatibility/differences between ClickZetta and these
  platforms.
  Keywords: Snowflake migration, Databricks migration, Spark SQL migration,
  Snowflake to ClickZetta, Databricks to ClickZetta, vs Snowflake, vs Spark,
  vs Databricks, syntax differences, function mapping, implicit type conversion,
  WHEN NOT MATCHED BY SOURCE, APPLY CHANGES INTO, WITH RECURSIVE, METADATA$ACTION,
  TARGET_LAG, FLATTEN, IFF, LISTAGG, OBJECT_CONSTRUCT, VARIANT, CHARINDEX
---

# ClickZetta SQL Migration Guide

Use this skill when migrating SQL workloads from Snowflake, Databricks (Delta Lake), or Spark SQL to ClickZetta Lakehouse, or when answering "how does ClickZetta differ from <other system>" questions.

For native ClickZetta SQL syntax that does not differ from standard SQL, refer to the ClickZetta Lakehouse documentation.

## Reference Documents

| Document | When to read |
|---|---|
| [Snowflake migration guide](references/migration-snowflake.md) | Migrating from Snowflake — object mapping, type mapping, syntax + function differences |
| [Databricks migration guide](references/migration-databricks.md) | Migrating from Databricks/Delta Lake — APPLY CHANGES, ZORDER, WHEN NOT MATCHED BY SOURCE alternatives |
| [vs Snowflake summary](references/vs-snowflake.md) | Cross-platform comparison summary |
| [vs Spark SQL summary](references/vs-spark.md) | Cross-platform comparison summary |
| [DML differences](references/dml-differences.md) | INSERT/UPDATE/DELETE/MERGE/COPY syntax that differs from other systems (concise migration view) |
| [Implicit type conversion](references/implicit-type-conversion.md) | The #1 migration error — strict CAST rules for INSERT/UPDATE |
| [Function mapping](references/function-mapping.md) | Function-by-function mapping tables (Snowflake/Spark/Databricks → ClickZetta) and unsupported functions |
| [DDL reference](references/ddl-reference.md) | Detailed DDL syntax — kept for migration completeness; for native ClickZetta DDL prefer the official documentation |
| [DML reference](references/dml-reference.md) | Detailed DML syntax — kept for migration completeness; for native ClickZetta DML prefer the official documentation |
| [DQL reference](references/dql-reference.md) | Detailed DQL syntax — kept for migration completeness; for native ClickZetta DQL prefer the official documentation |
| [Functions reference](references/functions-reference.md) | Detailed function list — kept for migration completeness; for native ClickZetta functions prefer the official documentation |

---

## ⚠️ Most Common Migration Pitfalls (Quick Reference)

| Scenario | Snowflake / Spark / Databricks | ClickZetta |
|---|---|---|
| Implicit string→DATE/TIMESTAMP/BOOLEAN/JSON in INSERT | ✅ allowed | ❌ Error — must use `CAST` or typed literals (`DATE '...'`, `TIMESTAMP '...'`, `TRUE`/`FALSE`, `PARSE_JSON(...)`) |
| `IFF(cond, a, b)` (SF) | — | `IF(cond, a, b)` |
| `ARRAY_SIZE(arr)` (SF) | `size(arr)` (Spark) | `SIZE(arr)` ✅ or `ARRAY_SIZE(arr)` ✅ — both supported |
| `LISTAGG(col, ',') WITHIN GROUP (...)` (SF) | — | `GROUP_CONCAT(col ORDER BY col SEPARATOR ',')` |
| `LATERAL FLATTEN(input => arr)` (SF) | — | `LATERAL VIEW EXPLODE(arr)` |
| `data:key` JSON access (SF) | — | `data['key']` |
| `OBJECT_CONSTRUCT('k', v)` (SF) | `STRUCT(v AS k)` (Spark) | `named_struct('k', v)` |
| `VARIANT` type (SF) | — | `JSON` type |
| `NUMBER(p, s)` (SF) | — | `DECIMAL(p, s)` |
| `CHARINDEX(sub, s)` (SF) | — | `INSTR(s, sub)` ⚠️ parameter order reversed |
| `DATEDIFF(day, start, end)` (SF) | `DATEDIFF(end, start)` (Spark) | both supported, ⚠️ Snowflake order has unit as first arg |
| `WHEN NOT MATCHED BY SOURCE THEN DELETE` (Databricks) | — | ❌ Not supported — use MERGE INTO + separate DELETE |
| `APPLY CHANGES INTO` (DLT) | — | TABLE STREAM + MERGE INTO |
| `WITH RECURSIVE` (SF/Databricks) | ✅ supported | ❌ Not supported — iterate via Python/ZettaPark or pre-build helper tables |
| `BEGIN; COMMIT; ROLLBACK;` (transactions) | ✅ | ❌ Not supported — use MERGE INTO for atomic operations |
| `TARGET_LAG = '1 minute'` for dynamic tables (SF) | — | `REFRESH INTERVAL 1 MINUTE VCLUSTER xx` |
| `METADATA$ACTION` for streams (SF) | — | `__change_type` (values: INSERT / UPDATE_BEFORE / UPDATE_AFTER / DELETE) |
| `OPTIMIZE t ZORDER BY (col)` (Databricks) | — | `OPTIMIZE t` (small file compaction only, no ZORDER) |
| `STRUCT(1 AS id, 'a' AS name)` (Spark) | — | `named_struct('id', 1, 'name', 'a')` |
| `TABLESAMPLE (50 PERCENT)` | — | ❌ PERCENT not supported — use `ORDER BY RAND() LIMIT n` |
| `CREATE SEQUENCE` (SF) | — | ❌ Not supported — use `IDENTITY(seed)` column (BIGINT only) |
| `CREATE TEMPORARY TABLE` (SF) | — | ❌ Not supported — use CTE |
| `CHARINDEX` / `EDITDISTANCE` / `SOUNDEX` (SF) | — | `INSTR` (reversed args) / Python UDF / no equivalent |

---

## Object Concept Mapping

| Snowflake | Databricks | ClickZetta |
|---|---|---|
| DATABASE | Catalog (internal) | WORKSPACE |
| SCHEMA / DATABASE.SCHEMA | Database / Schema | SCHEMA |
| WAREHOUSE | Cluster / SQL Warehouse | VCLUSTER |
| STAGE | External Location | VOLUME (+ STORAGE CONNECTION) |
| STORAGE INTEGRATION | — | STORAGE CONNECTION |
| SNOWPIPE | Auto Loader | PIPE |
| STREAM | (Delta CDF / DLT CDC) | TABLE STREAM |
| DYNAMIC TABLE | DLT (Live Tables) | DYNAMIC TABLE (different syntax) |
| TASK | Job | Studio Task |
| SEQUENCE | — | IDENTITY column |
| SHARE | Delta Sharing | SHARE |
| — | Unity Catalog (federation) | EXTERNAL CATALOG |

---

## Data Type Mapping Quick Reference

| Snowflake | Spark / Databricks | ClickZetta |
|---|---|---|
| `NUMBER(p, s)` / `NUMERIC` | `DECIMAL(p, s)` | `DECIMAL(p, s)` |
| `INTEGER` / `NUMBER(10,0)` | `INT` / `BIGINT` | `INT` / `BIGINT` |
| `VARCHAR(n)` / `TEXT` | `STRING` | `STRING` (recommended) or `VARCHAR(n)` |
| `TIMESTAMP_LTZ` | `TIMESTAMP` | `TIMESTAMP` |
| `TIMESTAMP_NTZ` | `TIMESTAMP_NTZ` | `TIMESTAMP_NTZ` |
| `VARIANT` | — | `JSON` |
| `ARRAY` (untyped) | `ARRAY<T>` | `ARRAY<T>` (must specify element type) |
| `OBJECT` | `MAP<K,V>` / `STRUCT<...>` | `MAP<K,V>` or `STRUCT<...>` |
| `GEOGRAPHY` | — | not supported |
| — | — | `VECTOR(FLOAT, N)` (ClickZetta-specific) |

---

## Migration Workflow Pointers

This skill focuses on **SQL syntax compatibility**. A complete migration involves more than SQL rewrites:

1. **Object mapping** — see table above
2. **Schema/DDL conversion** — see [migration-snowflake.md](references/migration-snowflake.md) and [migration-databricks.md](references/migration-databricks.md)
3. **Data movement** — typically via object storage (S3/OSS) staging + COPY INTO; not covered in detail here
4. **SQL rewrites** — see this skill's reference documents
5. **Application/driver layer** — JDBC, Python connector, BI tool reconnection; refer to `clickzetta-lakehouse-connect` skill
6. **Permission migration** — RBAC concept comparison; refer to `clickzetta-access-control` skill
7. **Performance tuning re-mapping** — Snowflake CLUSTER BY / Databricks ZORDER → ClickZetta partitioning + indexes; refer to `clickzetta-query-optimizer` skill

For end-to-end migration planning, combine this skill with the skills listed above.
