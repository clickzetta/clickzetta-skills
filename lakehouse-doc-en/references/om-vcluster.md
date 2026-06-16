# Virtual Cluster (VCluster)

A Virtual Cluster (VCluster) is the Lakehouse's **elastic compute resource unit**, providing CPU and memory resources for SQL queries, ETL jobs, and streaming analytics. Storage and compute are fully separated — data is stored in object storage, and virtual clusters handle only computation. Multiple clusters can access the same data simultaneously without interfering with each other.

Think of a virtual cluster as an "on-demand compute engine" — start it when you need it, stop it when you're done, and pay only for actual usage time. This is fundamentally different from traditional databases, where compute and storage are bound to the same machine and scaling requires data migration. In the Lakehouse, virtual clusters can be created, resized, and paused at any time without affecting any data.

## Cluster Types

| Type | Use Case | Characteristics |
|------|---------|------|
| **General (GENERAL)** | ETL data processing, offline batch jobs | Jobs share resources with fair scheduling; supports elastic scaling |
| **Analytics (ANALYTICS)** | BI queries, ad-hoc analysis, high-concurrency queries | Multi-instance auto-scaling; supports result caching for acceleration |
| **Integration (INTEGRATION)** | Data sync jobs (offline/real-time) | Optimized for integration tasks; multiple jobs share one cluster |

### Selection Guide

| Scenario | Recommended Type | Reason |
|---|---|---|
| Periodic ETL jobs | General | Shared resources, lower cost |
| BI reports / ad-hoc queries | Analytics | Multi-instance concurrency, result caching |
| Data sync jobs | Integration | Optimized for integration tasks |
| Dynamic Table refresh | General (low-frequency, large data volume) or Analytics (high-frequency, small data volume) | Choose based on refresh frequency and data volume |

> ⚠️ **Note**: It is recommended to use a General cluster for Dynamic Table refreshes. Analytics clusters do not support automatic small file compaction during the refresh process.

## Core Mechanisms

**CRU (Compute Resource Unit)**: The Lakehouse's abstract unit for compute resources, abstracting away differences between cloud platforms and CPU architectures. 1 CRU = 1 hour of compute resource consumption.

**Auto start/stop**: Clusters can automatically pause when idle (billing stops) and automatically start when a new job is submitted. Recommended configuration:
- ETL job clusters: set auto-stop to 60 seconds to release resources quickly
- BI query clusters: set auto-stop to 30 minutes or more to leverage caching for query acceleration

**Horizontal scaling (Analytics only)**: When concurrent queries exceed the capacity of a single instance, additional replicas are automatically started to share the load and scaled back down after queries complete.

## Quick Operations

```sql
-- Create a General cluster (1 CRU)
CREATE VCLUSTER my_gp_cluster
    VCLUSTER_SIZE = 1
    VCLUSTER_TYPE = GENERAL
    AUTO_SUSPEND_IN_SECOND = 60;

-- Create an Analytics cluster (2 CRU, up to 2 instances)
CREATE VCLUSTER my_ap_cluster
    VCLUSTER_SIZE = 2
    VCLUSTER_TYPE = ANALYTICS
    MIN_REPLICAS = 1
    MAX_REPLICAS = 2
    AUTO_SUSPEND_IN_SECOND = 1800;

-- Resize a cluster
ALTER VCLUSTER my_gp_cluster SET VCLUSTER_SIZE = 4;

-- Switch the current session to use a specific cluster
USE VCLUSTER my_gp_cluster;

-- Suspend a cluster (billing stops)
ALTER VCLUSTER my_gp_cluster SUSPEND;

-- List all clusters in the current workspace
SHOW VCLUSTERS;
```

> ⚠️ **Note**: VCluster names are automatically converted to **uppercase** when stored (unlike table names and schema names, which are lowercased). For example, a cluster created as `my_gp_cluster` will have the actual name `MY_GP_CLUSTER`. References are case-insensitive, but `SHOW VCLUSTERS` always displays uppercase names.

## Cost Implications

### Compute Cost

- Billed by CRU × hours; no charges when suspended
- Usage under 1 minute is billed as 1 minute
- Setting auto-stop to less than 1 minute may cause frequent start/stop cycles, potentially increasing costs

### Storage Cost

- Virtual clusters themselves do not incur storage costs; data is stored in object storage
- `PRELOAD_TABLES` on Analytics clusters uses local SSD cache space (temporary storage)

> 💡 **Tip**: For detailed billing rules, refer to the [Billing Documentation](billing.md).

## Lifecycle Management

```
Create Cluster → Auto Start → Execute Jobs → Auto Suspend on Idle → Resize / Drop
      ↓               ↓             ↓                  ↓                  ↓
  Specify type   Woken by new job  Consume CRU    Billing stops     Must stop cluster first
```

### Best Practices

1. **Workload isolation**: Use separate clusters for ETL jobs and BI queries to avoid resource contention
2. **Right-sizing**: Start with a small size, then scale up incrementally to the minimum size that meets your SLA
3. **Auto start/stop**: Set ETL clusters to auto-stop after 60 seconds; set BI clusters to 30 minutes or more
4. **Large job isolation**: Use separate clusters for large and small jobs to prevent large jobs from starving small ones

## Related Documentation

- [Virtual Cluster Details](virtual-cluster.md) — Full concepts and Web UI operations
- [Concurrency Scaling](concurrency_scaling.md) — Horizontal scaling for Analytics clusters
- [Size Reference](vcluster_size_description.md) — CRU size comparison table
- [CREATE VCLUSTER](create_cluster.md) — Complete SQL syntax
