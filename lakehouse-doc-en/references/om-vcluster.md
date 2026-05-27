# VCluster

A Virtual Cluster (VCluster) is the Lakehouse's **elastic compute resource unit**, providing CPU and memory resources for SQL queries, ETL tasks, and streaming analytics. Storage and compute are fully separated, so VClusters can be independently scaled up or down without affecting data.

## Core Concepts

**Separation of Storage and Compute**: Data is stored in object storage, while VClusters are only responsible for computation. Multiple VClusters can access the same data simultaneously without interfering with each other.

**On-Demand Elasticity**: VClusters can be started, stopped, and resized at any time, with no compute charges incurred when stopped.

## Cluster Types

| Type | Code | Suitable Scenarios |
|------|------|---------|
| General Purpose (GP) | `GP-1` and above | Mixed workloads, daily development and queries |
| Analytical Processing (AP) | `AP-1` and above | Large-scale analytical queries, sizes are powers of 2 |

## Horizontal Scaling (Concurrent Scaling)

When concurrent query volume exceeds a single cluster's processing capacity, horizontal scaling can be enabled to automatically launch additional compute replicas to share the load, automatically scaling back after queries complete.

## Quick Operations

```sql
-- Create a VCluster
CREATE VCLUSTER my_cluster SIZE = 'GP-4';

-- Switch the current cluster
USE VCLUSTER my_cluster;

-- Adjust the size
ALTER VCLUSTER my_cluster SET SIZE = 'GP-8';

-- Suspend (stop billing)
ALTER VCLUSTER my_cluster SUSPEND;
```

## Related Documentation

- [VCluster Detailed Description](virtual-cluster.md)
- [Concurrent Scaling](concurrency_scaling.md)
- [Size Specifications](vcluster_size_description.md)
