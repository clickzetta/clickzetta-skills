# Understanding and Using Result Cache

## Introduction

Singdata Lakehouse uses caching technology to accelerate query performance and efficiency. The platform provides three types of Cache to improve query performance.

1. Query Result Cache
2. Metadata Cache
3. Virtual Cluster Local Disk Cache

The three cache types operate at different layers: Metadata Cache and Query Result Cache belong to the service layer and are shared within the workspace, while Virtual Cluster Local Disk Cache is stored on the local nodes of a specific cluster and is only available when using that cluster.

Among them:

* Metadata Cache and Query Result Cache services belong to the service layer and can be shared within the workspace.
* Virtual Cluster Local Disk Cache is stored on the local nodes of the cluster and can only be used when using the specified virtual cluster.

This article will introduce the working principles of the caches and how to use them.

## Result Cache

When executing queries in Singdata Lakehouse, query results that meet certain conditions will be automatically retained for a period of time and will be cleared after the period ends. These temporarily stored query results are called Query Result Cache.

Result Cache needs to meet the following conditions to be reused:

* The underlying data of the tables used in the query does not change. If the data in any table used in the query changes, the result cache cannot be used;
* The query does not include queries on views. If the query object contains views, the query result cache is not supported;
* The newly initiated SQL query statement can exactly match the previously executed query in syntax;
* The query does not include non-deterministic functions (e.g., CURRENT\_TIMESTAMP()), user-defined functions (UDF);
* The previous Result Cache has not expired and been deleted.

## Result Cache Expiration Period

After the result cache is successfully created, the default retention period is 24 hours.

If subsequent queries using the query result cache are run within 24 hours, the result cache expiration time will be extended by an additional 24 hours. Otherwise, after 24 hours, the query result cache will be cleared.

## Enabling and Disabling Result Cache

Use the parameter `cz.sql.enable.shortcut.result.cache` at the SESSION level to enable or disable it, as shown below.
```Python
--Enable result cache
set cz.sql.enable.shortcut.result.cache=true;

--Disable result cache
set cz.sql.enable.shortcut.result.cache=false;
```
Note: As of April 2024, the Result Cache feature in the Lakehouse version is in public beta and not enabled by default. It will be enabled by default in future versions.

## Constraints and Limitations

Cache retention period: 24 hours

Maximum number of jobs supported for caching in a single workspace: 100,000

Result cache size limit: Unlimited. Results less than or equal to 10MB will be cached in the control layer memory cache, while results exceeding 10MB will be persisted in the storage layer (object storage files).

Non-deterministic functions and UDF query results are not supported for result caching.

## Result Cache Demonstration

To demonstrate query result caching, first enable the result cache and execute an SQL query in Singdata Lakehouse. Then rerun the same query to verify if the new query reuses the result cache for acceleration.
```Python
 --Enable result cache
set cz.sql.enable.shortcut.result.cache=true;

 select
        l_returnflag,
        l_linestatus,
        sum(l_quantity) as sum_qty,
        sum(l_extendedprice) as sum_base_price,
        sum(l_extendedprice * (1 - l_discount)) as sum_disc_price,
        sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge,
        avg(l_quantity) as avg_qty,
        avg(l_extendedprice) as avg_price,
        avg(l_discount) as avg_disc,
        count(*) as count_order
from
        tpch_100g_new.lineitem
where
        l_shipdate <= date '1998-12-01' - interval '85' day
group by
        l_returnflag,
        l_linestatus
order by
        l_returnflag,
        l_linestatus
;
```
The first execution took 12.1 seconds. By checking the Job Profile, we can see that the job read a large amount of data from the disk.


The second time this query was executed, the job reused the result cache from the previous query and returned the result within 15ms.

When viewing the Job Profile of the job, you can see in the execution plan on the diagnostics page that the job used "JOB RESULT REUSE", indicating that it directly returned the cached result data without re-scanning storage.