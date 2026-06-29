# Databricks Unity Catalog Federation Query Practice

Singdata Lakehouse queries tables in Databricks Unity Catalog directly through an External Catalog. Data stays in Databricks' S3 storage without moving — Lakehouse handles SQL execution and result delivery. This guide uses an AWS environment as an example and walks through the complete configuration process from scratch.

![](.topwrite/assets/15-databricks-federation.svg)

---

## Prerequisites

- Databricks workspace: Unity Catalog support required (Free Edition already supports it)
- Singdata Lakehouse instance: must be on the **same cloud platform** (both AWS) as the Databricks data storage (S3)
- Tools: cz-cli with the corresponding AWS profile pre-configured

---

## SQL Commands Involved

| Command | Purpose |
|---------|---------|
| `CREATE CATALOG CONNECTION` | Store Databricks OAuth M2M authentication credentials |
| `CREATE EXTERNAL CATALOG` | Create an external catalog pointing to Databricks Unity Catalog |
| `SHOW SCHEMAS IN` | List schemas in a Databricks Catalog |
| `SHOW TABLES IN` | List tables in a schema |
| `SELECT` | Query Databricks table data |
| `INSERT` | Append data (append only; UPDATE / DELETE not supported) |

---

## Databricks Configuration

> 💡 **Account Console vs Workspace**: Databricks has two different entry points. `https://accounts.cloud.databricks.com` is the **Account Console**, which manages organization, users, service principals, and other account-level settings. `https://dbc-xxx.cloud.databricks.com` is the **Workspace**, used for data development. The following SP configuration is done in Account Console; permission grants are done in the Workspace.

### Create a Service Principal

Open `https://accounts.cloud.databricks.com` → **User management** → **Service principals** → **Add service principal**, and give it a recognizable name (e.g., `lakehouse_connector`).

> If `https://accounts.cloud.databricks.com` redirects directly into a Workspace, you may be using the Community Edition, which does not support Unity Catalog and cannot proceed. The Free Edition supports Unity Catalog and can use this feature normally.

After creating the SP, click its name to enter the details page and complete the following:

1. **Roles** tab → Enable **Account admin**
2. **Principal information** tab → Record the **Application ID** (this is the `CLIENT_ID` used later, in UUID format)
3. **Credentials & secrets** tab → **Generate secret** → Record the complete **Secret** generated (this is the `CLIENT_SECRET` used later)

> **Note**: The Application ID is visible on both the SP list page and the Principal information tab. The Secret is only shown in full at generation time — save it immediately. Secrets have an `Expires at` expiration time; after expiry you must generate a new one and update the Catalog Connection.

### Add the SP to the Workspace

In the Databricks Workspace → **Settings** → **Identity and access** → **Service Principals** → **Add service principal**, and add the SP you just created.

> **Note**: The SP must satisfy three conditions simultaneously for authentication to succeed: Account Admin role + added to Workspace + Catalog/Schema permissions. Missing any one of these will result in an `invalid_client` error.

### Enable Metastore External Data Access

In the Databricks Workspace → **Catalog** → gear icon → **Metastore** → **Details** tab → find **External data access** → enable the toggle.

Without this option enabled, querying data will produce:

```
PermissionDenied: External Data Access from non Databricks Compute environment is disabled for metastore
```

### Grant Catalog and Schema Permissions

In Databricks Catalog Explorer, grant the following permissions to the SP:

- **Catalog level**: `USE CATALOG`
- **Schema level**: `USE SCHEMA`, `SELECT`, `EXTERNAL USE SCHEMA`

> `EXTERNAL USE SCHEMA` is a required permission for federation queries. It can be granted in the regular Permissions panel; no SQL execution is needed.

If you have a SQL execution environment (Notebook or SQL Warehouse), you can also use GRANT commands (replace `<application-id>` with the SP's Application ID in UUID format):

```sql
GRANT USE CATALOG ON CATALOG workspace
    TO `<application-id>`;

GRANT USE SCHEMA ON SCHEMA workspace.table_types_demo
    TO `<application-id>`;

GRANT SELECT ON SCHEMA workspace.table_types_demo
    TO `<application-id>`;

-- Required permission for federation queries
GRANT EXTERNAL USE SCHEMA ON SCHEMA workspace.table_types_demo
    TO `<application-id>`;
```

---

## Create a Catalog Connection

```sql
CREATE CATALOG CONNECTION IF NOT EXISTS databricks_conn
    TYPE databricks
    HOST = 'https://<workspace-url>.cloud.databricks.com'
    CLIENT_ID = '<application-id>'
    CLIENT_SECRET = '<oauth-secret>'
    ACCESS_REGION = '<s3-bucket-region>';
```

> **`ACCESS_REGION` should be the region of the S3 bucket, not the Databricks workspace region.**
>
> These are often different — the region selected when creating the Databricks workspace and the region of the S3 bucket where data is actually stored may not match. Using the wrong value causes query timeouts or `PermanentRedirect` errors.
>
> **How to confirm the S3 bucket region**: In the Databricks Workspace → left sidebar **Catalog** → click any table → in the right panel find the **Details** tab (or expand the properties panel on the right after clicking the table name) → check the **Storage Location** field, e.g., `s3://my-bucket/path/`. Then go to the AWS S3 Console, search for this bucket, and check its **AWS Region** attribute.

Verify the connection:

```sql
SHOW CATALOG CONNECTIONS;
```

---

## Create an External Catalog

```sql
CREATE EXTERNAL CATALOG IF NOT EXISTS databricks_catalog
    CONNECTION databricks_conn
    OPTIONS ('catalog' = '<databricks-catalog-name>');
```

The value of `catalog` is the name of the catalog in Databricks Unity Catalog. In the Databricks Workspace → left sidebar **Catalog** icon → expand the left panel. Catalogs listed under **My organization** are the available ones (e.g., `workspace`, `main`, `hive_metastore`).

Verify:

```sql
SHOW SCHEMAS IN databricks_catalog;
```

Sample output:

```
schema_name
-----------
default
information_schema
table_types_demo
```

---

## Querying Data

```sql
-- View table list
SHOW TABLES IN databricks_catalog.table_types_demo;

-- Query data
SELECT * FROM databricks_catalog.table_types_demo.orders_external LIMIT 10;
```

---

## Federation Queries: Cross-Platform SQL Analysis

The core value of federation queries is: **Lakehouse can directly query and join Databricks data, and can also write Databricks data into Lakehouse local tables** — all without any data migration.

### Scenario 1: JOIN Between Databricks Tables

`orders_external` (orders) and `customers_external` (customers) are joined via `customer_id` to calculate the order count and total spend per customer. Both tables have a `price` field of type `DECIMAL(10,2)`, requiring no conversion:

```sql
SELECT
    c.customer_name,
    c.country,
    c.loyalty_tier,
    COUNT(o.order_id)  AS order_count,
    SUM(o.price)       AS total_revenue
FROM databricks_catalog.table_types_demo.orders_external o
JOIN databricks_catalog.table_types_demo.customers_external c
    ON o.customer_id = c.customer_id
GROUP BY c.customer_name, c.country, c.loyalty_tier
ORDER BY total_revenue DESC;
```

Query results:

| customer_name | country   | loyalty_tier | order_count | total_revenue |
|---------------|-----------|--------------|-------------|---------------|
| Alice Chen    | China     | Gold         | 2           | 1698.99       |
| Frank Liu     | China     | Silver       | 1           | 299.99        |
| Carol Zhang   | China     | Platinum     | 2           | 249.98        |
| David Lee     | Singapore | Bronze       | 1           | 129.99        |
| Emma Wang     | China     | Silver       | 1           | 89.99         |

### Scenario 2: Low Inventory Alert

`inventory_delta` records inventory by warehouse (fields: `product_id`, `warehouse_location`, `quantity_available`). Query products with inventory below a threshold, summarized by warehouse:

```sql
SELECT
    warehouse_location,
    COUNT(*)                     AS low_stock_products,
    MIN(quantity_available)      AS min_stock,
    AVG(quantity_available)      AS avg_stock
FROM databricks_catalog.table_types_demo.inventory_delta
WHERE quantity_available < 200
GROUP BY warehouse_location
ORDER BY min_stock;
```

Query results:

| warehouse_location | low_stock_products | min_stock | avg_stock |
|--------------------|--------------------|-----------|-----------|
| Warehouse A        | 1                  | 50        | 50.0      |
| Warehouse B        | 2                  | 75        | 112.5     |

### Scenario 3: Writing Databricks Data to Lakehouse

Federation query results can be written directly into Lakehouse local tables for data consolidation. In the example below, `public` is a Lakehouse local schema (not Databricks) — replace it with your actual local schema name:

```sql
-- Extract completed orders from Databricks into a Lakehouse local table
CREATE TABLE public.orders_from_databricks AS
SELECT
    order_id,
    customer_id,
    order_date,
    product_name,
    CAST(price AS DECIMAL(10,2)) AS price,
    status
FROM databricks_catalog.table_types_demo.orders_external
WHERE status = 'Delivered';
```

Query the local table with no network overhead:

```sql
SELECT * FROM public.orders_from_databricks;
```

| order_id | customer_id | order_date | product_name    | price   | status    |
|----------|-------------|------------|-----------------|---------|-----------|
| 2006     | 1005        | 2026-05-20 | Webcam HD       | 89.99   | Delivered |
| 2001     | 1001        | 2026-05-15 | Laptop Pro      | 1299.99 | Delivered |
| 2004     | 1001        | 2026-05-18 | Monitor 27inch  | 399.00  | Delivered |

### Scenario 4: Dynamic Table Consuming Databricks Data

Use Databricks data as the upstream source for a Dynamic Table to periodically aggregate into Lakehouse. `public` is a Lakehouse local schema — replace it with your actual local schema name:

```sql
CREATE OR REPLACE DYNAMIC TABLE public.orders_daily_summary
REFRESH INTERVAL 1 HOUR VCLUSTER DEFAULT
COMMENT 'Daily order summary aggregated from Databricks'
AS
SELECT
    order_date,
    COUNT(*)                             AS order_count,
    SUM(CAST(price AS DECIMAL(10,2)))    AS total_revenue,
    AVG(CAST(price AS DECIMAL(10,2)))    AS avg_order_value
FROM databricks_catalog.table_types_demo.orders_external
GROUP BY order_date;
```

Query after the first refresh:

```sql
REFRESH DYNAMIC TABLE public.orders_daily_summary;
SELECT * FROM public.orders_daily_summary ORDER BY order_date;
```

| order_date | order_count | total_revenue | avg_order_value |
|------------|-------------|---------------|-----------------|
| 2026-05-15 | 1           | 1299.99       | 1299.99         |
| 2026-05-17 | 1           | 49.99         | 49.99           |
| 2026-05-18 | 1           | 399.00        | 399.00          |
| 2026-05-19 | 1           | 129.99        | 129.99          |
| 2026-05-20 | 1           | 89.99         | 89.99           |
| 2026-06-04 | 2           | 499.98        | 249.99          |

> **Note**: When a Dynamic Table references an External Catalog table, every refresh is a full scan because Databricks tables do not support Table Stream. For large data volumes, it is recommended to first snapshot the data into a local table using `CREATE TABLE ... AS SELECT`, then build the Dynamic Table on the local table.

---

## Supported Table Types

Not all Databricks tables can be queried from Lakehouse. Support depends on the table's storage type:

| Table Type | Format | Supported | Notes |
|------------|--------|-----------|-------|
| `TABLE_DELTA_EXTERNAL` | Delta | Yes | Fully supported, recommended |
| `TABLE_DELTA` | Delta | Yes | Fully supported |
| `TABLE_EXTERNAL` (Delta format) | Delta | Yes | Supported |
| `TABLE_EXTERNAL` (Parquet/CSV/JSON) | Non-Delta | No | Reports `unsupported databricks table format` |
| `TABLE_DB_STORAGE` | Managed Delta | No | Cross-platform access not supported |
| `VIEW` | — | No | Driver compatibility issue |

**Key conclusion**: Only **Delta format** tables support federation queries, whether External or regular Delta tables. External tables in Parquet, CSV, or JSON format are currently not supported.

When creating tables in Databricks, prefer Delta format:

```sql
-- Recommended: Delta External Table
CREATE TABLE catalog.schema.my_table
USING DELTA
LOCATION 's3://my-bucket/my-table/';

-- Not recommended (Lakehouse cannot query this)
CREATE TABLE catalog.schema.my_table
USING PARQUET
LOCATION 's3://my-bucket/my-table/';
```

---

## Common Error Troubleshooting

### `invalid_client`

OAuth authentication failed. Check in order:

1. Has the SP enabled **Account admin** in Account Console → **Roles**?
2. Has the SP been added in Workspace → **Settings** → **Service Principals**?
3. Is the `CLIENT_SECRET` the complete value (not a masked value like `50db****7f61`)? Go to Account Console → SP → **Credentials & secrets** to generate a new one.
4. Has the Secret expired? Check the `Expires at` field on the **Credentials & secrets** page. If expired, generate a new Secret and re-run `CREATE CATALOG CONNECTION`.

### `PermissionDenied: External Data Access ... is disabled`

The Metastore has not enabled external data access. In the Databricks Workspace → Catalog → gear icon → Metastore → **External data access** → enable.

### `PermissionDenied: User does not have USE CATALOG`

The SP does not have Catalog access permission. In Databricks Catalog Explorer, find the corresponding Catalog → Permissions → Grant → add `USE CATALOG` for the SP.

### `PermissionDenied: User does not have EXTERNAL USE SCHEMA`

The SP does not have external access permission for the Schema. In Databricks Catalog Explorer → Schema → Permissions → Grant → add `USE SCHEMA`, `SELECT`, and `EXTERNAL USE SCHEMA` for the SP.

### `NotFound: Catalog 'main' does not exist`

The catalog name specified in `OPTIONS ('catalog' = ...)` does not exist. Open the Databricks Workspace → Catalog panel to check the actual catalog names.

### Query Timeout (300 seconds) or `PermanentRedirect`

`ACCESS_REGION` is incorrect; S3 requests are being redirected. Check the table's actual storage location (Catalog Explorer → table details → Storage Location), confirm the S3 bucket's region, and recreate the Catalog Connection.

### `unsupported databricks table format {} [PARQUET/CSV/JSON]`

The table uses a non-Delta format, which is currently not supported for querying from Lakehouse. Recreate the table in Databricks using Delta format, or convert the data to a Delta table.

### `Table cannot be accessed from outside of Databricks Compute Environment ... kind being TABLE_DB_STORAGE`

The table is a Databricks Managed Table — data is stored in Databricks-controlled storage and does not support direct cross-platform access. The table must first be converted to an External Table in Databricks before it can be queried.

---

## Important Notes

| Note | Description |
|------|-------------|
| **Cloud platform restriction** | Databricks' S3 storage must be on the same cloud platform as the Lakehouse instance (both AWS). Databricks on GCP/Azure cannot be interconnected with an AWS Lakehouse. |
| **Region consistency** | `ACCESS_REGION` must match the S3 bucket's region, not the workspace region. |
| **Read-only restriction** | External Catalogs are read-only — writing data from Lakehouse to Databricks (INSERT/UPDATE/DELETE) is not supported. The reverse (writing Databricks data into Lakehouse) is fully supported; see Scenario 3. |
| **Version requirement** | Requires a version that supports Unity Catalog. Free Edition is supported; Community Edition is not. |
| **Save your Secret** | The OAuth Secret is only shown in full at generation time — save it immediately. If lost, you must generate a new one. |

---

## Related Documentation

- [Create Catalog Connection](create-catalog-connection.md) — Complete DDL syntax and parameter descriptions
- [Create Databricks External Catalog](create-external-catalog.md) — External Catalog DDL syntax
- [Federation Query Usage Guide](sql_external_catalog_guide.md) — Complete federation query examples
