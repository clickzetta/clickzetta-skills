# Compute Cluster Cache

Lakehouse uses caching technology to accelerate query performance and efficiency. The platform provides three types of caches to improve query performance:

1. Query Result Cache (ResultCache)

2. Metadata Cache (MetadataCache)

3. Compute Cluster Local Disk Cache (Virtual Cluster Local Disk Cache)

![](.topwrite/assets/image_1729739810389.png)

Among them:

Metadata Cache and Query Result Cache services belong to the service layer and can be shared within the workspace.

Compute Cluster Local Disk Cache is stored on the local nodes of the cluster and can only be used when using the specified virtual cluster.

In the storage-compute separation architecture of Lakehouse, data is stored in object storage. To address network request latency and improve response speed in analytical scenarios, we adopt caching strategies. Compute Cluster Cache stores frequently accessed data on local nodes, thereby accelerating queries.

Compute Cluster Cache is divided into two types:

1. **Active Cache**: Manually cache tables to the compute cluster through commands. Each time the compute cluster starts, these pre-cached tables will be automatically loaded. Currently, only AP type clusters are supported. Suitable scenarios include BI report queries, which can significantly reduce query latency and improve data processing speed.
2. **Passive Cache**: During the first query, Lakehouse automatically caches the read files to the compute cluster. Subsequent queries involving the same table files will directly utilize the cache, speeding up the query process. Supports both GP and AP type clusters. For the second and subsequent queries, if they involve the initially cached tables, the cache will be directly hit.

## Usage

1. **Proactive Caching Table Method**:

    ```SQL
    ALTER VCLUSTER default SET PRELOAD_TABLES="schema1.table1,schema2.table2";
    ```

    If you need to add a new table to the cache:

    ```SQL
    ALTER VCLUSTER default SET PRELOAD_TABLES="schema1.table1,schema2.table2,schema3.table3";
    ```

## **Viewing Cache Status**:

When tables are loaded into the compute cluster using the `ALTER..PRELOAD_TABLES` command, there may be a delay in the update of the cache status displayed by `SHOW PRELOAD`. However, the cached tables are actually effective. Under normal circumstances, this delay is about 10 minutes.

1. **Active Cache Table Method**:

* Display the preload table/partition status of the current virtual cluster:

```SQL
SHOW PRELOAD CACHED STATUS;
```

* Display the preload table/partition status of the specified virtual cluster:

```SQL
SHOW VCLUSTER preload_ap_vc_test PRELOAD CACHED STATUS;
```

* Filter preload status information by table name:

```SQL
SHOW VCLUSTER preload_ap_vc_test PRELOAD CACHED STATUS WHERE table LIKE '%x_test';
```

* Display the preloaded cache summary information of the virtual cluster:

```SQL
SHOW EXTENDED PRELOAD CACHED STATUS;
```

## Precautions

* The cluster supports automatic start and stop. When the cluster stops, the cached tables will be automatically released. In AP type clusters, the pre-cached tables will be automatically loaded upon restart.
* After executing the cache command, only newly written data will be cached.

^
