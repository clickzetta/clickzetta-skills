# DBT Practice Series

dbt (Data Build Tool) is currently the most popular data transformation tool. It brings software engineering best practices — version control, testing, documentation, and modularity — into data modeling. You write transformation logic in SQL, and dbt handles dependency management, incremental computation, data quality testing, and documentation generation.

Singdata Lakehouse natively supports dbt through the `dbt-clickzetta` adapter, and provides several Singdata-specific capabilities on top of standard dbt features:

| Capability | Description |
|---|---|
| Dynamic Table | Declarative incremental computation; the system automatically refreshes on a schedule with no external orchestration needed |
| Table Stream | Row-level change capture (CDC), tracking INSERT/UPDATE/DELETE |
| Automatic index creation | Automatically creates Bloomfilter / inverted / vector indexes when a table is built |
| Zero-copy clone | Clone a table in milliseconds with no extra storage, ideal for CI/CD environment isolation |
| VCluster per-model | Assign a compute cluster to individual models, isolating ETL write resources from aggregation query resources |

---

## Companion Projects

All code in this series comes from the following three directly runnable open-source projects — these are not made-up examples:

**[jaffle-shop-clickzetta](https://github.com/clickzetta/jaffle-shop-clickzetta)**
A coffee shop order dataset — the Singdata Lakehouse version of the official dbt sample project. Includes 6 seed tables, 6 staging views, 7 mart tables, 27 data tests, and 3 unit tests. Great for getting started quickly; from zero to running in about 1 minute.

**[snowflake-dbt2lakehouse-dbt](https://github.com/clickzetta/snowflake-dbt2lakehouse-dbt)**
A TPC-H order data warehouse migrated from Snowflake to Singdata Lakehouse. Covers advanced scenarios including Dynamic Table, Table Stream CDC, incremental pipelines, and SCD dimension tables. Uses the built-in TPC-H shared dataset in Singdata Lakehouse (150 million order rows) — no data import needed.

**[dbt-clickzetta examples](https://github.com/clickzetta/dbt-clickzetta)** (`examples/` directory)
A feature demonstration project for the dbt-clickzetta adapter, covering all supported materialization types and advanced features.

**[bigquery2lakehouse-retail](https://github.com/clickzetta/bigquery2lakehouse-retail)**
A UK e-commerce retail dataset migrated from BigQuery + Airflow + Cosmos + Soda to Singdata Lakehouse. Covers dbt-bigquery syntax differences, Dynamic Table materialization, and Studio Tasks replacing Airflow orchestration. Data is loaded via dbt seed — no GCS or service account configuration needed.

---

Choose your entry point based on your situation:

**New to dbt and want to get up and running quickly**
→ Start with [DBT Quickstart (Jaffle Shop)](eco_integration/dbt-jaffle-shop-quickstart.md) — get a complete project running in 30 minutes

**Already have a dbt project and want to understand incremental processing**
→ [DBT Incremental Processing in Practice](dbt-incremental.md) — strategy selection and real code for 4 strategies

**Want to use Dynamic Table or Table Stream for real-time pipelines**
→ [DBT Real-Time Data Pipeline in Practice](dbt-realtime-pipeline.md)

**Want to add tests to your data pipeline**
→ [DBT Data Quality in Practice](dbt-data-quality.md) — data test + unit test, verified 30/30 passing

**Want to use Singdata-specific features like indexes, clone, and VCluster**
→ [DBT Advanced Features in Practice](dbt-advanced-features.md)

**Migrating from Snowflake**
→ [DBT Snowflake Migration in Practice: TPC-H Data Warehouse Pipeline](dbt-snowflake-to-clickzetta-migration.md)

**Migrating from BigQuery**
→ [DBT BigQuery Migration in Practice: Retail Data Warehouse Pipeline](dbt-bigquery-to-clickzetta-migration.md)

---

## Series Articles

- [DBT Incremental Processing in Practice](dbt-incremental.md) — merge / append / delete+insert / insert_overwrite strategies, incremental filter patterns, schema change handling
- [DBT Real-Time Data Pipeline in Practice](dbt-realtime-pipeline.md) — Dynamic Table auto-refresh, Table Stream CDC, Stream offset management
- [DBT Data Quality in Practice](dbt-data-quality.md) — data test + unit test, verified 30/30 passing
- [DBT Snowflake Migration in Practice: TPC-H Data Warehouse Pipeline](dbt-snowflake-to-clickzetta-migration.md) — 6 platform differences, full coverage of Dynamic Table, Stream CDC, Surrogate Key, Python model
- [DBT BigQuery Migration in Practice: Retail Data Warehouse Pipeline](dbt-bigquery-to-clickzetta-migration.md) — eliminating GCS + Airflow + Cosmos, Dynamic Table materialization, Studio Tasks orchestration

---

## Version Requirements

It is recommended to use **dbt-clickzetta >= 1.7.10**, which fixes all known issues:

| Version | Key Fixes |
|---|---|
| 1.6.2 | seed `float8` type error, timestamp seed hang, unit test `safe_cast` syntax error |
| 1.6.3 | `this.database` returning `None` in macros |
| 1.6.5 | Stream system column injection generating invalid SQL; `SELECT * EXCEPT(...)` working correctly |
| 1.7.0 | seed switched to COPY INTO, 3-5x speed improvement |
| 1.7.5 | `dbt seed --full-refresh` reporting "already exists"; unit test DROP TABLE on VIEW error |
| 1.7.10 | unit test `cast(null as string not null)` syntax error; Python model support improvements |

---

## Related Documentation

- [DBT ClickZetta Adapter Usage Guide](eco_integration/dbt.md)
- [DBT Quickstart (Jaffle Shop)](eco_integration/dbt-jaffle-shop-quickstart.md)
- [DBT Development in Practice (Table Stream + Dynamic Table)](use-dbt-dev.md)
- [dbt-clickzetta GitHub](https://github.com/clickzetta/dbt-clickzetta)
