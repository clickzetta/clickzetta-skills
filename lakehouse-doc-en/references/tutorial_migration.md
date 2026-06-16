# Migration Guide

This section collects hands-on guides for migrating existing data systems to Singdata Lakehouse, covering the most common migration paths: Spark/PySpark, Snowflake, SQL syntax, and more.

---

## Migration Path Overview

| Source System | Recommended Path | Documentation |
|---------|---------|------|
| Databricks / PySpark | ZettaPark DataFrame API replacement | [PySpark → ZettaPark Migration in Practice](pyspark-to-zettapark-migration-f1.md) |
| PySpark RDD (legacy code) | RDD → declarative DataFrame/SQL | [RDD → ZettaPark Migration in Practice](rdd-to-zettapark-migration-weblog.md) |
| Spark SQL | SQL syntax comparison migration | [Spark SQL Syntax Migration Guide](migration-spark-sql.md) |
| Spark data engineering projects | Architecture migration best practices | [Spark Data Engineering Migration Best Practices](migrate-spark-data-engineering-best-practices-to-lakehouse.md) |
| Spark jobs (production) | Smooth migration with minimal changes | [Spark Job Smooth Migration Guide](spark-migration-guide.md) |
| Snowflake | ETL Pipeline migration | [Snowflake Real-Time ETL Migration](migrate-snowflake-realtime-etl-to-lakehouse.md) |
| Build Medallion from scratch | Bronze → Silver → Gold modeling | [Building a Medallion Lakehouse from Scratch](medallion-lakehouse-from-scratch.md) |

---

## Choosing a Migration Path

**You have existing PySpark code and want to migrate it directly**

Use the ZettaPark DataFrame API. 90% of your code can be reused as-is, with changes concentrated in 4 areas (import paths, Session creation, `.collect()`, file paths). See [PySpark → ZettaPark Migration in Practice](pyspark-to-zettapark-migration-f1.md) for complete before/after code comparisons and 4 migration notes.

**You have RDD code (Spark 1.x legacy project) and want to migrate to Lakehouse**

See [RDD → ZettaPark Migration in Practice](rdd-to-zettapark-migration-weblog.md). The core change is moving from imperative (`map/reduceByKey/aggregateByKey`) to declarative (`group_by/agg/F.avg()`), resulting in less code and better execution efficiency. Replacing `aggregateByKey` with `F.avg()` yields the greatest reduction in code volume.

**Starting from scratch and want to build a Medallion architecture on Lakehouse**

See [Building a Medallion Lakehouse from Scratch](medallion-lakehouse-from-scratch.md). The guide covers Bronze raw ingestion, Silver cleansing and deduplication, Gold dimensional modeling (including surrogate key generation), and a complete implementation with 22 automated validations.

**Migrating only SQL, not touching the compute layer**

See [Spark SQL Syntax Migration Guide](migration-spark-sql.md) and [Data Type Compatibility Reference](migration-sql-compatibility.md).

**Production Spark jobs requiring minimal downtime**

See [Spark Job Smooth Migration Guide](spark-migration-guide.md), which covers dual-write validation, gradual traffic cutover, and other production migration strategies.

---

## Related Documentation

- [ZettaPark DataFrame API Guide](zettapark-dataframe-guide.md): Complete ZettaPark API reference
- [Data Type Compatibility Reference](migration-sql-compatibility.md): MySQL/PostgreSQL/Hive/Spark type mappings
- [Volume Usage Guide](zettapark-volume-guide.md): File storage path format after migration (`vol://schema.vol/path`)
