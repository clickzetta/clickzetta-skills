# Usage and Billing View

`sys.information_schema.instance_usage` is a system view in Singdata Lakehouse that records resource consumption and billing details at the instance level. Each row represents the consumption of one SKU during a single billing period (hourly or daily), making it the primary source for bill reconciliation, cost attribution, and usage trend analysis.

Data is retained from instance creation onward.

***

## Field Reference

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

## SKU Categories

| `sku_category` | `sku_name` examples                                                                                                                        | Description                                           |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------- |
| `compute`      | GP Virtual Cluster, AP Virtual Cluster, Integration Virtual Cluster, Bulk Ingestion, Stream Ingestion, IGS Service, Task Scheduling        | Compute resource consumption, unit: `yuan/cru`        |
| `storage`      | Managed Storage, Retained Managed Storage, Job Temp Storage, Managed User Volume Storage                                                   | Storage usage, unit: `yuan/GB/day` or `yuan/GiB/day`  |
| `network`      | Query Internet Data Transfer                                                                                                               | Public internet egress, unit: `yuan/gb`               |
| `ai`           | AI model calls (multiple models, input/output billed separately)                                                                           | AI function consumption, unit: `M Tokens`             |

***

## Query Examples

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

## Notes

* `storage` SKUs are measured at **daily** granularity; all other categories are measured **hourly**.
* Data is not real-time — there is approximately a 4-hour delay before records appear.
* `price_rate` is a string type. Cast it before arithmetic: `CAST(price_rate AS DOUBLE)`.
* `total_after_discount` is the final billed amount. `amount` is the pre-discount gross. The difference is the discount applied.

> ⚠️ **Note**: This view requires a user with the `instance_admin` role connected to the `sys` workspace. If your current workspace is not `sys`, use the three-part notation `sys.information_schema.instance_usage` to query across workspaces. Users without `instance_admin` will get empty results.
