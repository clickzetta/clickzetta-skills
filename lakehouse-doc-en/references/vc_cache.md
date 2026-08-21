# Compute Cluster Cache

Lakehouse uses caching technology to accelerate query performance and efficiency. The platform provides three types of caches to improve query performance:

1. Query Result Cache (ResultCache)

2. Metadata Cache (MetadataCache)

3. Compute Cluster Local Disk Cache (Virtual Cluster Local Disk Cache)

![](.topwrite/assets/image_1729739810389.png)

Among them:

Metadata Cache and Query Result Cache services belong to the service layer and can be shared within the workspace.

Compute Cluster Local Disk Cache is stored on the local nodes of the cluster and can only be used when using the specified Virtual Cluster.

In the storage-compute separation architecture of Lakehouse, data is stored in object storage. To address network request latency and improve response speed in analytical scenarios, we adopt caching strategies. Compute Cluster Cache stores frequently accessed data on local nodes, thereby accelerating queries.

Compute Cluster Cache is divided into two types:

1. **Active Cache**: Manually cache tables to the compute cluster through commands. Each time the compute cluster starts, the latest data or partitions of these pre-cached tables are automatically loaded. Currently, only AP type clusters are supported. Suitable scenarios include BI report queries, which can significantly reduce query latency and improve data processing speed.
2. **Passive Cache**: During the first query, Lakehouse automatically caches the read files to the compute cluster. Subsequent queries involving the same table files will directly utilize the cache, speeding up the query process. Supports both GP and AP type clusters. For the second and subsequent queries, if they involve the initially cached tables, the cache will be directly hit.

## Usage

1. **Active Caching Method**:

```SQL
ALTER VCLUSTER DEFAULT SET PRELOAD_TABLES="schema1.table1,schema2.table2";
```

If you need to add a new table to the cache, you must include all previously configured tables, otherwise the original ones will be overwritten:

```SQL
ALTER VCLUSTER DEFAULT SET PRELOAD_TABLES="schema1.table1,schema2.table2,schema3.table3";
```

`PRELOAD_TABLES` supports wildcards. Use `schema_name.*` to cache all tables under a Schema:

```SQL
-- Cache all tables in the sales Schema, plus the dim_date table in the public Schema
ALTER VCLUSTER bi_vc SET PRELOAD_TABLES="sales.*,public.dim_date";
```

## **Viewing Cache Status**:
When tables are loaded into the compute cluster using the `ALTER..PRELOAD_TABLES` command, there may be a delay in the cache status update displayed by `SHOW PRELOAD`. However, the cached tables are actually already effective. Under normal circumstances, this delay is approximately 10 minutes.


* Display the preload table/partition status of the current Virtual Cluster:

```SQL
SHOW PRELOAD CACHED STATUS;
```

* Display the preload table/partition status of the specified Virtual Cluster:

```SQL
SHOW VCLUSTER preload_ap_vc_test PRELOAD CACHED STATUS;
```

* Filter preload status information by table name:

```SQL
SHOW VCLUSTER preload_ap_vc_test PRELOAD CACHED STATUS WHERE table LIKE '%x_test';
```

* Display the preloaded cache summary information of the Virtual Cluster:

```SQL
SHOW EXTENDED PRELOAD CACHED STATUS;
```

> 💡 **Tip**: The active and passive caches described in this article are both **data caches** (they cache the table's data files), which are a different cache type from the **Query Result Cache**. Data caches require active configuration via `PRELOAD_TABLES` and are only supported on Analytics (AP) clusters. The query result cache, on the other hand, is managed automatically without any configuration and does not support clearing it entirely in one step — see [Understanding and Using Result Cache](result_cache.md) for details.

## Notes

* Active caching (PRELOAD_TABLES) is only supported on **Analytics (AP)** clusters. General Purpose (GP) clusters do not support this feature.
* `PRELOAD_TABLES` is an **overwrite** operation. When adding a new table, you must include all previously configured tables, otherwise they will be removed from preloading.
* The cluster supports automatic start and stop. When the cluster stops, the local cache is automatically released. When an AP cluster restarts, only the most recently written data or partitions are cached.
* After executing the cache command, only newly written data will be cached.
* `SHOW PRELOAD` status updates may have approximately a 10-minute delay, but the cache is already effective.
