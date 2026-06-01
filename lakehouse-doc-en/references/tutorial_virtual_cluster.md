# Manage Compute Resources

Singdata Lakehouse uses a storage-compute separation architecture — storage and compute scale independently and elastically. A compute cluster (VCluster) is the compute unit that executes all SQL jobs. It is billed by actual runtime and automatically stops when idle, incurring no charges.

---

## Three Cluster Types

| Type | Use case | Spec unit | Elasticity |
|------|---------|---------|---------|
| **General Purpose (GP)** | ETL batch processing, offline jobs | 1–256 CRU, step 1 | Vertical scaling: configure `MIN_VCLUSTER_SIZE` / `MAX_VCLUSTER_SIZE`, auto-adjusts spec based on load |
| **Analytical (AP)** | BI reports, ad-hoc queries, high-concurrency online queries | 1–256 CRU, must be a power of 2 (1/2/4/8/16…) | Horizontal scaling: configure `MIN_REPLICAS` / `MAX_REPLICAS`, auto-adds/removes instances based on concurrency (up to 10) |
| **Integration** | Real-time/offline data integration tasks | 0.25–256 CRU | Vertical scaling: configure `MIN_VCLUSTER_SIZE` / `MAX_VCLUSTER_SIZE`, auto-adjusts spec based on load |

> **Selection principle**: Use General Purpose for ETL, Analytical for BI and online queries, Integration for data sync tasks. Multiple clusters can be created in the same workspace to isolate resources for different workloads.

![](/.topwrite/assets/10-vcluster-elasticity.svg)

Singdata Lakehouse compute cluster elasticity operates at three levels:

**GP (General Purpose) — Vertical elasticity**: Single cluster spec auto-scales with load, from 1 CRU up to 256 CRU. Automatically scales up during peak load and scales back down after the peak; automatically stops billing after idle timeout. Suitable for ETL and other scenarios where a single job needs to consume full resources.

**AP (Analytical) — Horizontal elasticity**: When concurrent query count reaches the current instance limit, new instances (Replicas) are automatically added, up to 10 instances, linearly increasing total concurrency capacity. Instances are automatically reduced when concurrency drops; in-flight queries are not affected. Suitable for BI reports and high-concurrency online query scenarios.

**Integration — Fine-grained vertical elasticity**: Minimum spec of 0.25 CRU, precisely matching the actual load of sync tasks, with extremely high resource utilization and costs that scale linearly with task count. Suitable for real-time CDC and offline integration tasks.

All three cluster types support **second-level cold start** (auto-wake on job submission), **auto-stop when idle** (no billing), and **no interruption to in-flight jobs during scaling**.

---

## This Section

| Page | Description |
|------|------|
| [Using Lakehouse Compute Clusters](working_with_vclusters.md) | Cluster creation, start/stop, spec adjustment, SQL operations, and best practices for common use cases |
| [Supporting Multi-Concurrent Queries with Horizontal Elastic Scaling](concurrency_scaling.md) | How multi-instance scaling works for Analytical clusters and hands-on tutorial |

---

## Common Operations

### View Clusters

```sql
-- View all clusters in the current workspace
SHOW VCLUSTERS;

-- View only running clusters
SHOW VCLUSTERS WHERE state = 'RUNNING';

-- View detailed configuration of a specific cluster (spec, status, job count, etc.)
DESC VCLUSTER my_cluster;
```

### Switch Clusters

```sql
-- Switch the current session to a specific cluster
USE VCLUSTER my_cluster;

-- Confirm the currently active cluster
SELECT CURRENT_VCLUSTER();
```

> ⚠️ **Note**: In the Studio interface, it is recommended to switch clusters using the dropdown menu at the top of the page. If you run `USE VCLUSTER` in the SQL editor, you must select that statement together with the subsequent SQL before running.

### Start and Stop

```sql
-- Start a cluster
ALTER VCLUSTER my_cluster RESUME;

-- Stop a cluster (waits for current jobs to complete)
ALTER VCLUSTER my_cluster SUSPEND;

-- Force stop (immediately terminates all running jobs)
ALTER VCLUSTER my_cluster SUSPEND FORCE;
```

### Adjust Specifications

```sql
-- General Purpose: fixed spec
ALTER VCLUSTER my_gp_cluster SET VCLUSTER_SIZE = 4;

-- General Purpose: enable elastic scaling (min 2 CRU, max 8 CRU)
ALTER VCLUSTER my_gp_cluster SET MIN_VCLUSTER_SIZE = 2 MAX_VCLUSTER_SIZE = 8;

-- Analytical: adjust instance count range (horizontal scaling)
ALTER VCLUSTER my_ap_cluster SET MIN_REPLICAS = 1 MAX_REPLICAS = 4;

-- Analytical: adjust max concurrency per instance
ALTER VCLUSTER my_ap_cluster SET MAX_CONCURRENCY = 16;
```

### View Cluster Jobs

```sql
-- View all jobs in a specific cluster
SHOW JOBS IN VCLUSTER my_cluster;

-- View jobs running longer than 2 minutes
SHOW JOBS IN VCLUSTER my_cluster WHERE execution_time > INTERVAL 2 MINUTE;

-- View failed jobs
SHOW JOBS WHERE status = 'FAILED' LIMIT 20;
```

### Configure Auto-Suspend

```sql
-- Auto-suspend after 60 seconds idle (recommended for ETL clusters)
ALTER VCLUSTER etl_cluster SET AUTO_SUSPEND_IN_SECOND = 60;

-- Auto-suspend after 30 minutes idle (recommended for BI query clusters, preserves cache)
ALTER VCLUSTER bi_cluster SET AUTO_SUSPEND_IN_SECOND = 1800;

-- Never auto-suspend
ALTER VCLUSTER my_cluster SET AUTO_SUSPEND_IN_SECOND = -1;
```

### Configure Cache Preloading (Analytical clusters only)

```sql
-- Preload hot tables into cluster local SSD to accelerate BI queries
ALTER VCLUSTER bi_cluster SET PRELOAD_TABLES = "dws.daily_sales,dws.user_profile";

-- View preload status
SHOW PRELOAD CACHED STATUS;
```

### Set Job Timeout

```sql
-- Limit single job execution to 10 minutes (prevents runaway queries from consuming resources)
ALTER VCLUSTER my_cluster SET QUERY_RUNTIME_LIMIT_IN_SECOND = 600;
```

---

## Related Documentation

| Document | Description |
|------|------|
| [Compute Cluster](virtual-cluster.md) | Core concepts, spec selection reference table, Web UI screenshots |
| [Compute Resource DDL](compute-resource-ddl.md) | Full syntax for CREATE / ALTER / DROP VCLUSTER |
| [Compute Cluster Cache](vc_cache.md) | How active and passive caching work |
| [SHOW JOBS](show-jobs.md) | View and filter job records |
| [Compute Cluster Spec Code Change Description](vcluster_size_description.md) | Old vs. new spec code mapping table |
