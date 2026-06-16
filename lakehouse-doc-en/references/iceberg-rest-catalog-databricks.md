# Accessing Databricks Iceberg Tables via Iceberg REST Catalog

Singdata Lakehouse accesses Iceberg-format tables in Databricks Unity Catalog through the Iceberg REST Catalog protocol. Metadata is synchronized in real time, and data remains in the original S3 storage without any migration.

![](.topwrite/assets/anim-16-iceberg-rest-databricks.svg)

---

## Prerequisites

- Databricks workspace: Unity Catalog must be enabled
- Singdata Lakehouse instance: must be on the same cloud platform (both AWS) as the Databricks data storage (S3)
- Iceberg table data stored in an **S3 bucket you control**, with cross-account read permissions configured for the Lakehouse
- Databricks Service Principal: OAuth Client ID and Secret already obtained

---

## Databricks-Side Preparation

### 1. Obtain OAuth Credentials

Go to `https://accounts.cloud.databricks.com` → **Service principals** → create or select a Service Principal → **Credentials & secrets** → record the Application ID (Client ID) and Secret.

### 2. Grant Catalog Permissions

```sql
GRANT USE CATALOG ON CATALOG <catalog_name> TO `<application-id>`;
GRANT USE SCHEMA ON SCHEMA <catalog_name>.<schema_name> TO `<application-id>`;
GRANT SELECT ON SCHEMA <catalog_name>.<schema_name> TO `<application-id>`;
GRANT EXTERNAL USE SCHEMA ON SCHEMA <catalog_name>.<schema_name> TO `<application-id>`;
```

### 3. Enable Metastore External Data Access

Databricks Workspace → **Catalog** → gear icon → **Metastore** → **External data access** → enable.

### 4. Iceberg Table Format Requirements (Critical)

> ⚠️ **Note**: Only Iceberg-format tables can be queried via Iceberg REST Catalog. Tables in Delta, Parquet, CSV, and other formats are visible in `SHOW TABLES`, but `SELECT` will return `table not found`.

| Table Format | SHOW TABLES | SELECT | Notes |
|--------------|-------------|--------|-------|
| **Iceberg** | ✅ | ✅ | The only supported type |
| Delta | ✅ | ❌ | Metadata visible, cannot query |
| Parquet / CSV / JSON | ✅ | ❌ | Same as above |

Creating an Iceberg table in Databricks:

```sql
CREATE TABLE catalog.schema.my_iceberg_table
USING ICEBERG
LOCATION 's3://your-bucket/path/';
```

### 5. S3 Storage Requirements

Iceberg table data must be in an **S3 bucket you control**. Tables in Databricks-managed storage (`s3://dbstorage-prod-*`) have accessible metadata, but data queries will return `S3 403 Forbidden`.

The Lakehouse AWS account also needs read access to the S3 bucket. You can obtain the Lakehouse AWS account ID through technical support.

---

## Create a Catalog Connection

```sql
CREATE CATALOG CONNECTION IF NOT EXISTS databricks_iceberg_conn
TYPE ICEBERG_REST
URI = 'https://<workspace>.cloud.databricks.com/api/2.1/unity-catalog/iceberg-rest'
OAUTH_SERVER_URI = 'https://<workspace>.cloud.databricks.com/oidc/v1/token'
ACCESS_REGION = '<s3-bucket-region>'
OAUTH_CLIENT_ID = '<oauth-client-id>'
OAUTH_CLIENT_SECRET = '<oauth-client-secret>'
OAUTH_SCOPE = 'all-apis'
WAREHOUSE = '<databricks-catalog-name>';
```

### Parameter Reference

| Parameter | Required | Description |
|-----------|----------|-------------|
| `TYPE` | Yes | Fixed as `ICEBERG_REST` — do not add `=` |
| `URI` | Yes | Iceberg REST API endpoint — note the **new path** `/iceberg-rest`, not the old path `/iceberg` |
| `OAUTH_SERVER_URI` | **Yes** | Databricks OAuth token endpoint. Different path from URI — omitting it causes `Credential was not sent` |
| `ACCESS_REGION` | Yes | Region of the S3 bucket, not the Databricks workspace region |
| `OAUTH_CLIENT_ID` | Yes | Service Principal Application ID (UUID format) |
| `OAUTH_CLIENT_SECRET` | Yes | Service Principal OAuth Secret |
| `OAUTH_SCOPE` | Yes | Fixed as `all-apis` |
| `WAREHOUSE` | Yes | Catalog name in Databricks Unity Catalog (e.g., `workspace`, `main`) |

> ⚠️ **Note**: `TYPE = ICEBERG_REST` will cause a syntax error. The correct form omits `=`: `TYPE ICEBERG_REST`

---

## Create an External Catalog

```sql
CREATE EXTERNAL CATALOG databricks_iceberg_catalog
  CONNECTION databricks_iceberg_conn;
```

> Note: Iceberg REST Catalog does not require `OPTIONS ('catalog' = '...')` — the warehouse was already specified in the connection above.

---

## Verification

```sql
-- Verify connectivity
SHOW SCHEMAS IN databricks_iceberg_catalog;

-- List tables
SHOW TABLES IN databricks_iceberg_catalog.<schema>;

-- Describe table structure
DESC TABLE databricks_iceberg_catalog.<schema>.<iceberg_table>;

-- Query data
SELECT * FROM databricks_iceberg_catalog.<schema>.<iceberg_table> LIMIT 10;
```

---

## Common Errors

### `Credential was not sent or was of an unsupported type`

`OAUTH_SERVER_URI` is not set. The Databricks OAuth token endpoint and the Iceberg REST endpoint are at different paths and must be specified separately.

### Legacy Iceberg endpoints deprecated

`URI` is using the old path `/iceberg`. Change to the new path `/iceberg-rest`.

### Must provide 'warehouse' parameter

`WAREHOUSE` is not set. Databricks' new Iceberg REST API requires the catalog name to be explicitly specified.

### S3 403 Forbidden

The Iceberg table data is in Databricks-managed storage (`s3://dbstorage-prod-*`), which Lakehouse does not have permission to read. You need to migrate the table data to a user-controlled S3 bucket and configure cross-account permissions.

### table or view not found (on SELECT)

The table is not in Iceberg format (it may be Delta / Parquet / CSV). `SHOW TABLES` displays all formats, but only Iceberg-format tables can be queried with `SELECT`.

---

## Management

```sql
-- View connection details
DESC CONNECTION databricks_iceberg_conn;

-- Drop Catalog
DROP CATALOG databricks_iceberg_catalog;

-- Drop connection
DROP CONNECTION databricks_iceberg_conn;
```

---

## Related Documentation

- [Create Catalog Connection](create-catalog-connection.md) — Full DDL syntax
- [Databricks Unity Catalog Federated Query Practice](databricks-external-catalog-practice.md) — TYPE DATABRICKS approach
- [External Catalog Federated Query](SQL_External_Catalog_Guide.md)
