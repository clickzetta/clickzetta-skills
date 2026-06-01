# INFORMATION SCHEMA

INFORMATION SCHEMA is Lakehouse's built-in metadata query interface, based on the ANSI SQL-92 standard. It lets you query metadata such as tables, views, job history, and permissions using standard SQL, with no additional tools required.

---

## Contents

| Page | Description |
|------|------|
| [Instance-level INFORMATION SCHEMA](instance-information_schema.md) | Instance-level metadata across workspaces; requires INSTANCE ADMIN permission; accessed via `SYS.information_schema` |
| [Workspace-level INFORMATION SCHEMA](workspace-informationschema-summary.md) | Metadata for tables, views, job history, etc. in the current workspace; requires the workspace_admin role |

---

## Two Access Scopes

| Scope | Access Path | Permission Required | Typical Use |
|-------|-------------|---------------------|-------------|
| Instance-level | SYS.information_schema.&lt;view_name&gt; | INSTANCE ADMIN | View metadata across all workspaces; view records of deleted objects |
| Workspace-level | information_schema.&lt;view_name&gt; | workspace_admin | View table schemas, job history, and permission assignments in the current workspace |

## Choosing Between INFORMATION SCHEMA and SHOW / DESC

| Scenario | Recommended Approach | Notes |
|----------|----------------------|-------|
| View real-time status of a single object | `SHOW` / `DESC` | **Returns results immediately**; suitable for checking current state of tables, columns, clusters, and jobs |
| Aggregate statistics or cross-object analysis | `information_schema` | Supports standard SQL with `JOIN`, `GROUP BY`, `ORDER BY`; **data has ~15-minute delay** |
| View deleted objects | Instance-level `SYS.information_schema` or `SHOW TABLES HISTORY` | Instance-level views use `delete_time` to identify deleted objects |
| Cost analysis | `SYS.information_schema.instance_usage` / `storage_metering` | Includes CRU, storage, network, and other billing fields |
| File deduplication and tracking for imports | `load_history('schema.table')` | View COPY/Pipe file import history; retained for 7 days |

> ⚠️ **Note**: `information_schema` view data has approximately a 15-minute delay and does not reflect the latest state. To check the current real-time state of an object, use commands such as `SHOW TABLES`, `DESC TABLE`, or `SHOW JOBS`.

---

## Common Queries

**View all tables in the current workspace**

```SQL
SELECT table_name, table_type, create_time
FROM information_schema.tables
ORDER BY create_time DESC;
```

**View job history (last 24 hours)**

```SQL
SELECT job_id, status, start_time, end_time, execution_time, virtual_cluster
FROM information_schema.job_history
WHERE start_time >= CURRENT_DATE() - INTERVAL 1 DAY
ORDER BY start_time DESC
LIMIT 50;
```

**View all tables across the instance (requires INSTANCE ADMIN)**

```SQL
SELECT table_schema, table_name, create_time
FROM SYS.information_schema.tables
WHERE delete_time IS NULL
ORDER BY table_schema, table_name;
```

## Asset Inventory SQL

**View all schemas in the current workspace**

```SQL
SELECT catalog_name, schema_name, type, schema_creator, create_time, comment
FROM information_schema.schemas
ORDER BY schema_name;
```

**View all tables with size and row count**

```SQL
SELECT table_schema, table_name, table_type, row_count, bytes
FROM information_schema.tables
ORDER BY bytes DESC;
```

**View detailed column information**

```SQL
SELECT table_schema, table_name, column_name, data_type, is_nullable, comment
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, column_name;
```

**View sort key recommendations**

```SQL
SELECT schema_name, table_name, col, statement, ratio, insert_time
FROM information_schema.sortkey_candidates
ORDER BY ratio DESC;
```

**Find the 10 largest tables**

```SQL
SELECT table_schema, table_name, row_count, bytes
FROM information_schema.tables
WHERE table_type IN ('MANAGED_TABLE', 'EXTERNAL_TABLE')
ORDER BY bytes DESC
LIMIT 10;
```

**Find tables without comments**

```SQL
SELECT table_schema, table_name
FROM information_schema.tables
WHERE comment IS NULL OR comment = '';
```

**Find columns without comments**

```SQL
SELECT table_schema, table_name, column_name
FROM information_schema.columns
WHERE (comment IS NULL OR comment = '')
  AND table_schema NOT IN ('information_schema');
```

**Count tables and total storage per schema**

```SQL
SELECT table_schema,
       COUNT(*) AS table_count,
       SUM(bytes) AS total_storage
FROM information_schema.tables
GROUP BY table_schema
ORDER BY total_storage DESC;
```

**View all workspaces in the instance (requires INSTANCE ADMIN)**

```SQL
SELECT workspace_name, workspace_creator, create_time, comment
FROM sys.information_schema.workspaces
WHERE delete_time IS NULL
ORDER BY create_time DESC;
```

**View all schemas in the instance (requires INSTANCE ADMIN)**

```SQL
SELECT catalog_name, schema_name, type, schema_creator, create_time
FROM sys.information_schema.schemas
WHERE delete_time IS NULL
ORDER BY catalog_name, schema_name;
```

**View instance usage (requires INSTANCE ADMIN)**

```SQL
SELECT workspace_name, sku_name, measurements_consumption, amount, measurement_start
FROM sys.information_schema.instance_usage
WHERE measurement_start >= CURRENT_DATE() - INTERVAL 7 DAY
ORDER BY amount DESC;
```

---

## Notes

- View data has approximately a 15-minute delay and is not suitable for real-time monitoring (see the selection guide above)
- All views are read-only and cannot be modified or deleted
- Avoid `SELECT *` in scheduled tasks; specify explicit columns to prevent errors caused by view schema changes
- Deleted objects in instance-level views are retained for 60 days; use `delete_time IS NULL` to filter for existing objects

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [Instance-level INFORMATION_SCHEMA Overview](instance-information-schema-summary.md) | Access methods, usage restrictions, and query examples for instance-level views |
| [Instance-level INFORMATION_SCHEMA View List](instance-information-schema.md) | Field descriptions for all instance-level views |
| [Workspace-level INFORMATION_SCHEMA Overview](workspace-informationschema-summary.md) | Permission requirements, usage notes, and query examples for workspace-level views |
| [Workspace-level INFORMATION_SCHEMA View List](workspace-information_schema-views.md) | Field descriptions for all workspace-level views |
| [Analyzing Job History with job_history](job_history_analysis_with_information_schema.md) | Practical guide for analyzing resource usage and performance bottlenecks using the job_history view |
| [Permission Inventory and Optimization Best Practices](security-system-inventory-based-information-schema.md) | Inventory and optimize permission configurations using views such as object_privileges, roles, and users |
| [Security Compliance Audit Guide](security_compliance_audit_guide.md) | Complete solution for compliance auditing (e.g., ISO 27001, SOC 2) using information_schema |
| [Billing Anomaly Analysis and Troubleshooting](lakehouse_billing_anomaly_alert_configuration_guide.md) | Analyze billing anomalies using the instance_usage and storage_metering views |
