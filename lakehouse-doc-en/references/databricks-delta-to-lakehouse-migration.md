# Databricks Delta Tables → Lakehouse Migration Guide

Data on Databricks can almost entirely be migrated to Singdata Lakehouse. There are two complementary paths: **federated direct read** (data stays in place, query Databricks tables directly from Lakehouse) and **Studio built-in sync** (move various table types into Lakehouse native format). All 7 table types have been tested and pass, with row counts and field values fully consistent.

Full code on GitHub: [databricks2lakehouse-delta](https://github.com/clickzetta/databricks2lakehouse-delta)

---

## Conclusion First

**Two paths** — selection rule: if federated read is available (External Delta), use federation + CTAS; for everything else, use Studio built-in sync.

| Table Type | Federated Read | Studio Sync | Recommended Path |
|---|:---:|:---:|---|
| **External Delta** | ✅ Tested | ✅ Tested | Federated read (no data movement) or CTAS landing |
| **Managed Delta** | ❌ | ✅ Tested | Studio built-in sync |
| **Parquet External** | ❌ | ✅ Tested | Studio built-in sync |
| **CSV External** | ❌ | ✅ Tested | Studio built-in sync |
| **JSON External** | ❌ | ✅ Tested | Studio built-in sync |
| **Managed Iceberg** | ❌ | ✅ Tested | Studio built-in sync |
| **View** | ❌ | ✅ Tested (materialized as table) | Studio built-in sync |

---

## Technical Background

Databricks uses Unity Catalog three-level naming (`catalog.schema.table`), with data stored in two categories:
- **External tables**: Data files reside in the customer's own S3/ADLS; Databricks only manages metadata
- **Managed tables**: Data files reside in Databricks managed storage, inaccessible externally

This difference determines the scope of federated reads — only External Delta tables can be directly queried via Lakehouse External Catalog federation. Managed tables must be migrated via Studio sync jobs.

---

![](.topwrite/assets/anim-33-databricks-delta-migration.svg)

---

## Path A: Federated Direct Read (External Delta Only)

Federated read queries Databricks tables directly via Lakehouse External Catalog with **no data movement**, suitable for parallel access during transition or PoC validation.

### Configuration (one-time)

```sql
-- Step 1: Create a Catalog Connection to Databricks
CREATE CATALOG CONNECTION IF NOT EXISTS databricks_conn
TYPE = DATABRICKS_UNITY_CATALOG
PROPERTIES (
    'host' = 'https://dbc-xxxx.cloud.databricks.com',
    'catalog' = 'workspace'
    -- Authentication parameters configured via Studio UI
);

-- Step 2: Create External Catalog (federation entry point)
CREATE EXTERNAL CATALOG IF NOT EXISTS databricks_new_catalog
USING CONNECTION databricks_conn;
```

### Federated Query

```sql
-- Query Databricks tables directly (cross-region/cross-cloud supported, via public internet)
SELECT * FROM databricks_new_catalog.table_types_demo.customers_external;
SELECT COUNT(*) FROM databricks_new_catalog.table_types_demo.orders_external;

-- CTAS: land the federated table as a Lakehouse native table (optional)
CREATE TABLE delta_migration.customers AS
SELECT * FROM databricks_new_catalog.table_types_demo.customers_external;
```

### Federated Read Limitations

Federated read **only supports External Delta format**. Test results:

| Table Tested | Format | Result |
|---|---|---|
| `customers_external` | External Delta | ✅ 7 rows, schema/types correct |
| `orders_external` | External Delta | ✅ 8 rows, aggregation correct |
| `inventory_delta` | External Delta | ✅ 4 rows |
| `customers_managed` | Managed Delta | ❌ Data in Databricks managed storage, no external access |
| `products_parquet` | External Parquet | ❌ `unsupported databricks table format [PARQUET]` |
| `suppliers_csv` | External CSV | ❌ `unsupported databricks table format [CSV]` |
| `shipments_iceberg` | Managed Iceberg | ❌ S3 400 (data in Databricks managed bucket) |
| `customer_orders_view` | View | ❌ Not supported |

---

## Path B: Studio Built-in Sync (Handles All Table Types)

Studio has a built-in Databricks data source with visual sync task configuration to move all table types into Lakehouse native format.

### Configuration Steps

1. Studio UI → Data Integration → New Data Source → Select Databricks
2. Enter Databricks Workspace URL + authentication info (Service Principal)
3. New sync task → Select source tables → Configure target schema → Execute

### Test Results (All 7 Table Types SUCCEED)

Sync tasks were run against all table types in the `table_types_demo` schema in a real Databricks environment (AWS us-east-1, Unity Catalog). All succeeded:

| Source Table | Type | Result | Duration | Source Rows | Target Rows | Consistent |
|---|---|:---:|:---:|:---:|:---:|:---:|
| `customers_managed` | Managed Delta | ✅ | ~88s | 7 | 7 | ✅ |
| `customers_external` | External Delta | ✅ | ~84s | 7 | 7 | ✅ |
| `products_parquet` | Parquet | ✅ | ~87s | 5 | 5 | ✅ |
| `suppliers_csv` | CSV | ✅ | ~93s | 3 | 3 | ✅ |
| `product_reviews_json` | JSON | ✅ | ~109s | 3 | 3 | ✅ |
| `shipments_iceberg` | Managed Iceberg | ✅ | ~92s | 5 | 5 | ✅ |
| `customer_orders_view` | View | ✅ | ~86s | 8 | 8 | ✅ |

> Single task duration is 84–109 seconds (including sync cluster cold start), largely independent of data volume. Estimate total migration time linearly based on table count.

### Data Consistency Verification

**Field-level row-by-row comparison** was performed on 5 tables (Databricks SDK reads source, cz-cli reads target). Findings:

- `products_parquet`, `product_reviews_json`, `shipments_iceberg`, `suppliers_csv`: **All fields fully consistent**
- `customers_external`, `suppliers_csv`: email/contact_email fields show masked values on the Lakehouse side (e.g., `a***@example.com`)

> Masking is the Lakehouse workspace's **read-time column masking policy** automatically matching by column name. The data itself is migrated intact. To see plaintext values, use a role with appropriate permissions or query in a schema without a masking policy bound.

---

## Delta-Specific Feature Handling

| Feature | Migration Impact |
|---|---|
| **Deletion Vectors (DV)** | ✅ Federated read correctly recognizes DVs; deleted rows are not returned. Data state is consistent after sync to Lakehouse |
| **Change Data Feed (CDF)** | Current data syncs normally. CDF incremental consumption interface (`table_changes()`) has no equivalent in Lakehouse → rebuild incremental pipelines using Lakehouse Table Stream |
| **Liquid Clustering** | Does not affect data content. After migration to Lakehouse, rebuild layout optimization using Lakehouse `CLUSTER BY` or indexing mechanisms |

---

## Connectivity Notes

- **Cross-region/cross-cloud supported**: Both federated read and Studio sync use the public internet. Tested: Lakehouse AWS Singapore ↔ Databricks us-east-1 cross-region, cross-cloud connectivity confirmed
- **Only hard limitation**: `COPY INTO`/`Pipe` object storage connections cannot cross cloud providers (e.g., an Alibaba Cloud instance cannot connect to AWS S3), but this affects direct S3 file reads, not reading tables via Databricks External Catalog

---

## Notes

- **Managed tables cannot be federated**: Managed Delta/Iceberg data resides in Databricks managed storage with no external access — must use Studio sync
- **Parquet/CSV/JSON External tables cannot be federated**: External Catalog currently only supports Delta format; use Studio sync for other formats
- **Array columns not yet supported for sync**: Columns with `ARRAY<...>` types are not yet supported by Studio sync tasks. Convert them to STRING using `to_json()` on the source side before syncing
- **Configure sync tasks table by table**: Studio's built-in Databricks data source does not yet support bulk schema-wide sync; configure each table individually. Scripts can be used to batch-generate configurations

## Related Documentation

### Federated Query

- [External Catalog Overview](external-catalog-concept.md): External Catalog federated query principles
- [Federated Query Guide](SQL_External_Catalog_Guide.md): SQL syntax and usage examples

### Data Ingestion

- [Data Ingestion Overview](streaming_data_pipeline_overview.md): Full ingestion solution landscape
- [COPY INTO](copy-into.md): Bulk load from object storage
- [Pipe (Continuous Ingestion)](pipe-overview.md): Continuously monitor object storage for new files

### Other Migration Guides

- [Databricks Notebook → Lakehouse Migration Guide](databricks-notebook-to-studio-migration.md)
- [Databricks DLT → Lakehouse Migration Guide](databricks-dlt-to-lakehouse-migration.md)
- [Databricks Jobs → Lakehouse Studio Migration Guide](databricks-jobs-to-studio-migration.md)
- [Databricks Unity Catalog → Lakehouse Migration Guide](databricks-uc-governance-to-lakehouse-migration.md)
