# View Compute Cluster Information (DESC VCLUSTER)

## Description

This command displays detailed information about a Lakehouse compute cluster (VCluster), including cluster type, status, size, auto-scaling configuration, and more.

## Syntax

```sql
DESC [VCLUSTER] [EXTENDED] <vc_name>;
-- or
DESCRIBE [VCLUSTER] [EXTENDED] <vc_name>;
```

## Parameters

| Parameter | Description |
|---|---|
| `DESC` / `DESCRIBE` | Equivalent keywords, interchangeable |
| `VCLUSTER` | Optional keyword |
| `EXTENDED` | Optional. When specified, returns an additional `properties` field |
| `vc_name` | Name of the compute cluster |

## Examples

### Example 1: View basic compute cluster information

```sql
DESC VCLUSTER default;
+-------------------------------+---------------------------+
| info_name                     | info_value                |
+-------------------------------+---------------------------+
| name                          | DEFAULT                   |
| creator                       | qiliang                   |
| created_time                  | 2026-04-23 19:35:56.865   |
| last_modified_time            | 2026-05-19 22:25:07.487   |
| comment                       | MCP test vcluster         |
| vcluster_type                 | GENERAL                   |
| state                         | SUSPENDED                 |
| scaling_policy                | N/A                       |
| min_vcluster_size             | 1                         |
| max_vcluster_size             | 1                         |
| current_vcluster_size         | 0                         |
| auto_resume                   | true                      |
| auto_suspend_in_second        | 60                        |
| running_jobs                  | 0                         |
| queued_jobs                   | 0                         |
| provision_mode                | SERVERLESS                |
+-------------------------------+---------------------------+
```

### Example 2: View extended compute cluster information

```sql
DESC VCLUSTER EXTENDED default;
```

The `EXTENDED` mode additionally returns the `properties` field, showing the cluster's configuration attributes.

## Return Fields

| Field | Description |
|---|---|
| `vcluster_type` | Cluster type: `GENERAL` (general purpose), `ANALYTICS` (analytics), `SYNC` (sync) |
| `state` | Cluster state: `RUNNING`, `SUSPENDED`, `RESUMING`, etc. |
| `scaling_policy` | Scaling policy: `STANDARD` or `N/A` (elastic scaling not supported) |
| `min_vcluster_size` / `max_vcluster_size` | Cluster size range (number of CRUs) |
| `current_vcluster_size` | Current size |
| `auto_resume` | Whether auto-resume is enabled |
| `auto_suspend_in_second` | Auto-suspend timeout (seconds) |
| `running_jobs` / `queued_jobs` | Number of running / queued jobs |
| `provision_mode` | Provisioning mode: `SERVERLESS` |

## Related Documents

- [CREATE VCLUSTER](create_cluster.md)
- [ALTER VCLUSTER](alter-vcluster.md)
- [DROP VCLUSTER](drop-vcluster.md)
- [SHOW VCLUSTERS](show-vclusters.md)
