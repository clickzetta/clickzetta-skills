# Usage and Billing View

Singdata Lakehouse provides two system views for querying usage and billing:

| View | Purpose |
| ---- | ------- |
| `sys.information_schema.instance_usage` | Records SKU consumption and billing details at the workspace level. Data is retained from instance creation onward. The primary source for bill reconciliation and cost attribution. |
| `sys.information_schema.instance_resource_usage` | Extends `instance_usage` by providing `resource_name`-level granularity for select SKUs, making it suitable for viewing usage and cost of individual resources (such as a specific virtual cluster or PIPE). |

Both views require the `instance_admin` role and can be queried across workspaces using three-part notation (e.g., `sys.information_schema.instance_usage`).

***

## instance_usage

`sys.information_schema.instance_usage` records resource consumption and billing details at the instance level. Each row represents the consumption of one SKU during a single billing period (hourly or daily).

### Field Reference

| Field                      | Type      | Description                                                                     |
| -------------------------- | --------- | ------------------------------------------------------------------------------- |
| `account_id`               | int       | Account ID                                                                      |
| `account_name`             | string    | Account name (i.e. the instance name)                                           |
| `instance_id`              | int       | Instance ID                                                                     |
| `region_name`              | string    | Cloud region, e.g. `Alibaba Cloud - East China 2 (Shanghai)`                    |
| `sku_category`             | string    | SKU category — see classification table below                                   |
| `sku_name`                 | string    | Specific SKU name                                                                |
| `workspace_id`             | string    | Workspace ID                                                                    |
| `workspace_name`           | string    | Workspace name                                                                  |
| `measurement_start`        | timestamp | Start of the billing period                                                     |
| `measurement_end`          | timestamp | End of the billing period                                                       |
| `measurements_unit`        | string    | Unit of measurement, e.g. `yuan/cru`, `yuan/GiB/day`, `yuan/gb`, `M Tokens`    |
| `measurements_consumption` | double    | Actual consumption during the period (in the given unit)                        |
| `price_rate`               | string    | Unit price as a string, e.g. `"0.020000"`                                       |
| `amount`                   | double    | Gross amount before discount (consumption × unit price)                         |
| `discount_rate`            | double    | Discount rate: `1` means no discount, `0.8` means 20% off                       |
| `total_after_discount`     | double    | Net amount after discount (the actual billed amount)                            |

***

### SKU Categories

| `sku_category` | `sku_name` examples                                                                                                                        | Description                                           |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------- |
| `compute`      | GP Virtual Cluster, AP Virtual Cluster, Integration Virtual Cluster, Bulk Ingestion, Stream Ingestion, IGS Service, Task Scheduling        | Compute resource consumption, unit: `yuan/cru`        |
| `storage`      | Managed Storage, Retained Managed Storage, Job Temp Storage, Managed User Volume Storage                                                   | Storage usage, unit: `yuan/GB/day` or `yuan/GiB/day`  |
| `network`      | Query Internet Data Transfer                                                                                                               | Public internet egress, unit: `yuan/gb`               |
| `ai`           | AI model calls (multiple models, input/output billed separately)                                                                           | AI function consumption, unit: `M Tokens`             |

***

### Query Examples

### Total cost by SKU category over the last 7 days

```
SELECT
  sku_category,
  SUM(measurements_consumption) AS total_consumption,
  SUM(amount)                   AS amount_before_discount,
  SUM(total_after_discount)     AS total_cost
FROM sys.information_schema.instance_usage
WHERE measurement_start >= CURRENT_DATE() - INTERVAL 7 DAYS
GROUP BY sku_category
ORDER BY total_cost DESC;
```

### Monthly cost ranking by workspace

```
SELECT
  workspace_name,
  SUM(total_after_discount) AS total_cost
FROM sys.information_schema.instance_usage
WHERE measurement_start >= DATE_TRUNC('month', CURRENT_DATE())
GROUP BY workspace_name
ORDER BY total_cost DESC;
```

### Daily cost trend for a specific workspace

```
SELECT
  DATE(measurement_start) AS date,
  sku_category,
  SUM(total_after_discount) AS daily_cost
FROM sys.information_schema.instance_usage
WHERE workspace_name = '<your_workspace>'
  AND measurement_start >= CURRENT_DATE() - INTERVAL 30 DAYS
GROUP BY DATE(measurement_start), sku_category
ORDER BY date DESC, daily_cost DESC;
```

### CRU consumption breakdown for compute clusters

```
SELECT
  workspace_name,
  sku_name,
  DATE(measurement_start)  AS date,
  measurements_consumption AS cru_hours,
  total_after_discount     AS cost
FROM sys.information_schema.instance_usage
WHERE sku_category = 'compute'
  AND measurement_start >= CURRENT_DATE() - INTERVAL 7 DAYS
ORDER BY date DESC, cost DESC;
```

### Workspaces exceeding a storage threshold

```
SELECT
  workspace_name,
  sku_name,
  DATE(measurement_start)  AS date,
  measurements_consumption AS storage_gib
FROM sys.information_schema.instance_usage
WHERE sku_category = 'storage'
  AND measurements_consumption > 100
  AND measurement_start >= CURRENT_DATE() - INTERVAL 7 DAYS
ORDER BY storage_gib DESC;
```

### AI function token consumption

```
SELECT
  workspace_name,
  sku_name,
  SUM(measurements_consumption) AS total_tokens_m,
  SUM(total_after_discount)     AS total_cost
FROM sys.information_schema.instance_usage
WHERE sku_category = 'ai'
GROUP BY workspace_name, sku_name
ORDER BY total_cost DESC;
```

***

### Notes

* `storage` SKUs are measured at **daily** granularity; all other categories are measured **hourly**.
* Data is not real-time — there is approximately a 4-hour delay before records appear.
* `price_rate` is a string type. Cast it before arithmetic: `CAST(price_rate AS DOUBLE)`.
* `total_after_discount` is the final billed amount. `amount` is the pre-discount gross. The difference is the discount applied.

> ⚠️ **Note**: This view requires a user with the `instance_admin` role connected to the `sys` workspace. If your current workspace is not `sys`, use the three-part notation `sys.information_schema.instance_usage` to query across workspaces. Users without `instance_admin` will get empty results.

## instance_resource_usage

`sys.information_schema.instance_resource_usage` provides usage and billing details for non-AI SKUs within the current customer instance. Compared to `instance_usage`, which aggregates by workspace, this view exposes a `resource_name` dimension for select SKUs — making it suitable for viewing usage and cost at the level of individual resources.

The following SKUs are broken down to `resource_name`: `task_schedule`, `bulk_ingestion`, `external_network`, `igs_upsert_v1`, `stream_ingestion`, `vc_ap_event`, `vc_gp_event`, `vc_integration_event`. All other non-AI SKUs remain at workspace granularity with `resource_name` as `NULL`. Results are scoped to the current customer instance; no additional filter on `instance_id` is needed.

### Field Reference

The fields below reflect the current view definition. Verify exact types and column order by running `DESCRIBE` in your target environment.

| Field | Type | Description |
| ----- | ---- | ----------- |
| `account_id` | BIGINT | Account ID |
| `account_name` | STRING | Account name |
| `instance_id` | BIGINT | Instance ID |
| `region_name` | STRING | Region where the instance is located |
| `sku_category` | STRING | SKU category, e.g. `compute`, `storage`, `network` |
| `sku_code` | STRING | SKU code |
| `sku_name` | STRING | SKU display name |
| `workspace_id` | BIGINT | Workspace ID |
| `workspace_name` | STRING | Workspace name |
| `measurement_start` | TIMESTAMP | Start of the measurement window |
| `measurement_end` | TIMESTAMP | End of the measurement window |
| `measurements_unit` | STRING | Unit of measurement |
| `measurements_consumption` | DOUBLE | Actual consumption within the measurement window |
| `price_rate` | DECIMAL | Unit price |
| `amount` | DOUBLE | Gross amount before discount |
| `discount_rate` | DOUBLE | Discount rate |
| `total_after_discount` | DOUBLE | Net amount after discount |
| `payable_amount` | DOUBLE | Payable amount |
| `precision_diff` | DOUBLE | Rounding difference |
| `billing_unit` | STRING | Billing unit |
| `billing_mode` | STRING | Billing mode |
| `resource_name` | STRING | Resource name; `NULL` for workspace-level records |

### Query Examples

**Resource-level usage and cost for select SKUs**

```sql
SELECT
  workspace_name,
  sku_code,
  resource_name,
  measurement_start,
  measurement_end,
  measurements_consumption,
  total_after_discount,
  payable_amount
FROM sys.information_schema.instance_resource_usage
WHERE sku_code IN (
  'task_schedule', 'bulk_ingestion', 'external_network', 'igs_upsert_v1',
  'stream_ingestion', 'vc_ap_event', 'vc_gp_event', 'vc_integration_event'
)
  AND measurement_start >= CURRENT_DATE() - INTERVAL 7 DAYS
ORDER BY measurement_start DESC, workspace_name, sku_code, resource_name;
```

**Workspace-level summary for SKUs without resource granularity**

```sql
SELECT
  workspace_name,
  sku_code,
  SUM(measurements_consumption) AS total_consumption,
  SUM(total_after_discount)     AS total_after_discount
FROM sys.information_schema.instance_resource_usage
WHERE resource_name IS NULL
GROUP BY workspace_name, sku_code
ORDER BY total_after_discount DESC;
```

**Daily cost breakdown for a specific virtual cluster**

```sql
SELECT
  DATE(measurement_start) AS date,
  sku_code,
  measurements_consumption,
  measurements_unit,
  total_after_discount
FROM sys.information_schema.instance_resource_usage
WHERE resource_name = '<your_vcluster_name>'
  AND measurement_start >= CURRENT_DATE() - INTERVAL 30 DAYS
ORDER BY date DESC;
```
