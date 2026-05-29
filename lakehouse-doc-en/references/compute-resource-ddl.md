# Compute Resource DDL

Compute cluster (VCluster) DDL commands are used to create, configure, start/stop, and drop compute clusters. All SQL that requires computation (SELECT, DML) runs on a compute cluster.

---

## In This Chapter

| Page | Description |
|------|-------------|
| [CREATE VCLUSTER](create_cluster.md) | Create a general-purpose, analytics, or sync compute cluster |
| [ALTER VCLUSTER](alter-vcluster.md) | Start, stop, or modify cluster properties |
| [DROP VCLUSTER](drop-vcluster.md) | Drop a compute cluster |
| [USE VCLUSTER](use-vcluster.md) | Switch the cluster used by the current session |
| [DESC VCLUSTER](desc-vcluster.md) | View detailed cluster configuration and status |
| [SHOW VCLUSTERS](show-vclusters.md) | List all clusters in the workspace |

---

## Common Operations

### Create a Cluster

```SQL
-- General-purpose (GP): suited for ETL batch processing
CREATE VCLUSTER IF NOT EXISTS my_etl_cluster
  VCLUSTER_TYPE = GENERAL
  VCLUSTER_SIZE = 2
  AUTO_SUSPEND_IN_SECOND = 60
  AUTO_RESUME = TRUE;

-- General-purpose (GP) with auto-scaling enabled
CREATE VCLUSTER IF NOT EXISTS my_etl_cluster
  VCLUSTER_TYPE = GENERAL
  MIN_VCLUSTER_SIZE = 1
  MAX_VCLUSTER_SIZE = 8
  AUTO_SUSPEND_IN_SECOND = 60
  AUTO_RESUME = TRUE;

-- Analytics (AP): suited for BI queries and high-concurrency online queries
CREATE VCLUSTER IF NOT EXISTS my_bi_cluster
  VCLUSTER_TYPE = ANALYTICS
  VCLUSTER_SIZE = 2
  MIN_REPLICAS = 1
  MAX_REPLICAS = 4
  MAX_CONCURRENCY = 8
  AUTO_SUSPEND_IN_SECOND = 120
  AUTO_RESUME = TRUE;
```

### Start and Stop

```SQL
-- Start a cluster
ALTER VCLUSTER IF EXISTS my_cluster RESUME;

-- Stop a cluster (waits for current jobs to complete)
ALTER VCLUSTER IF EXISTS my_cluster SUSPEND;

-- Force stop (immediately terminates all running jobs)
ALTER VCLUSTER IF EXISTS my_cluster SUSPEND FORCE;
```

### Modify Cluster Configuration

```SQL
-- General-purpose: adjust auto-scaling range
ALTER VCLUSTER my_etl_cluster SET MIN_VCLUSTER_SIZE = 1 MAX_VCLUSTER_SIZE = 4;

-- Analytics: adjust replica count range
ALTER VCLUSTER my_bi_cluster SET MIN_REPLICAS = 1 MAX_REPLICAS = 4;

-- Analytics: adjust max concurrency per replica
ALTER VCLUSTER my_bi_cluster SET MAX_CONCURRENCY = 16;

-- Set auto-suspend time (seconds)
ALTER VCLUSTER my_cluster SET AUTO_SUSPEND_IN_SECOND = 300;

-- Set job timeout (seconds)
ALTER VCLUSTER my_cluster SET QUERY_RUNTIME_LIMIT_IN_SECOND = 600;
```

### View Clusters

```SQL
-- List all clusters
SHOW VCLUSTERS;

-- List only running clusters
SHOW VCLUSTERS WHERE state = 'RUNNING';

-- View detailed cluster configuration
DESC VCLUSTER my_cluster;
```

### View Jobs

```SQL
-- View failed jobs
SHOW JOBS WHERE status = 'FAILED' LIMIT 20;
```

### Switch Cluster

```SQL
-- Switch the current session to a specific cluster
USE VCLUSTER my_cluster;
```

### Drop a Cluster

```SQL
DROP VCLUSTER IF EXISTS my_cluster;

-- Force drop (does not wait for running jobs to complete)
DROP VCLUSTER IF EXISTS my_cluster FORCE;
```

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [Managing Compute Resources](tutorial_virtual_cluster.md) | Cluster type selection guide and common operation walkthrough |
| [Compute Cluster Size Code Changes](vcluster_size_description.md) | Mapping between old and new size codes |
| [Compute Cluster Cache](vc_cache.md) | How active and passive caching work |
| [SHOW JOBS](show-jobs.md) | Full syntax for viewing and filtering job records |
