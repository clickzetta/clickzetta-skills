# Clustered Key and Sorted Key

When creating a table, specifying data distribution and sorting methods using the `CLUSTERED BY` and `SORTED BY` clauses can significantly improve performance in specific query scenarios.

## Syntax

```SQL
CREATE TABLE table_name (
    column_definitions
)
[CLUSTERED BY (col_name [, col_name ...]) [SORTED BY (col_name [ASC|DESC] [, ...])] INTO num BUCKETS]
[PARTITIONED BY (col_name data_type [, ...])];
```

## Parameter Description

| Parameter | Required | Description |
|------|------|------|
| `CLUSTERED BY (col_name, ...)` | No | Specifies the clustering key columns. The system computes a hash on these column values and distributes data across buckets. |
| `SORTED BY (col_name [ASC\|DESC], ...)` | No | Specifies the sorting key columns within each bucket. Data is stored in this order within each bucket. Ascending by default. |
| `INTO num BUCKETS` | Required with `CLUSTERED BY` | Specifies the number of buckets. It is recommended that each bucket holds approximately 128 MB–1 GB of data. |

## Clustered Key Description

The clustered key determines how data is distributed across buckets. The system computes a hash on the clustered key column values, and data with the same hash value falls into the same bucket.

**Criteria for selecting clustered keys:**

- Choose columns with a wide range of values and few duplicates to achieve even data distribution and avoid data skew.
- If a column is frequently used as a `JOIN` key in queries, setting it as the clustered key enables Bucket Join, significantly improving JOIN performance.
- When no clustered key is specified, the system defaults to 256 buckets.
- Too many buckets result in a large number of small files, impacting metadata management and I/O efficiency. Too few buckets fail to fully utilize parallel processing capabilities.

## Sorted Key Description

The sorted key defines the physical sort order of data within each bucket. For queries that filter or sort by the sorted key, pre-sorted data reduces the scan range and improves query performance.

- Each sort column can be specified as `ASC` (ascending, default) or `DESC` (descending).
- Sorted keys have some impact on write performance. Sorting during large-scale data writes consumes additional resources.

## Bucket Count and Compute Cluster Concurrency

The number of buckets is linked to the compute cluster's CRU size and instance count:

- **Bucket count determines the granularity of parallel query processing**: different query requests can run in parallel across different buckets. Too few buckets become a bottleneck for parallel processing, so even with sufficient compute cluster size (CRU) and instance count, the cluster cannot be fully utilized. Increasing the bucket count appropriately improves query concurrency.
- **Bucket count affects load balancing across instances**: the clustering strategy determines how data is distributed across compute instances. With a well-chosen clustering key and sufficient buckets, data is distributed evenly across instances; with too few buckets or a poorly chosen clustering key (causing data skew), some instances become overloaded while others sit idle.

> 💡 **Tip**: There is no exact formula relating bucket count to CRU size and instance count — adjust based on actual data volume and query patterns through testing. A useful rule of thumb is to set the bucket count to a multiple of 8 (e.g., 8, 16, 32, 64...), which aligns well with the cluster's parallel processing granularity. In addition, Analytics (AP) compute clusters support multi-instance auto-scaling and automatically adjust the instance count based on actual query load, so you don't need to find an exact match between bucket count and instance count.

## Examples

1. Create an orders table clustered by `customer_id` and sorted by `order_date`:

```SQL
CREATE TABLE orders_clustered (
    order_id    BIGINT,
    customer_id INT,
    product     STRING,
    amount      DECIMAL(10, 2),
    order_date  DATE
)
CLUSTERED BY (customer_id)
SORTED BY (order_date DESC)
INTO 64 BUCKETS;
```

When querying by `customer_id`, the system only needs to scan the corresponding bucket without a full table scan:

```SQL
SELECT * FROM orders_clustered WHERE customer_id = 1001;
```

2. Create a table with a multi-column clustered key, suitable for multi-dimensional JOIN scenarios:

```SQL
CREATE TABLE transaction_records (
    transaction_id BIGINT,
    customer_id    INT,
    product_id     INT,
    amount         DECIMAL(10, 2),
    transaction_date DATE
)
CLUSTERED BY (customer_id, product_id)
SORTED BY (transaction_date ASC)
INTO 128 BUCKETS;
```

3. Specify only the clustered key without a sorted key:

```SQL
CREATE TABLE sales_data (
    sale_id    INT,
    product_id INT,
    region     STRING,
    amount     DECIMAL(10, 2)
)
CLUSTERED BY (product_id)
INTO 50 BUCKETS;
```

4. Combine partitioning and clustering (data is clustered within each partition):

```SQL
CREATE TABLE logs_partitioned (
    log_id   BIGINT,
    user_id  INT,
    action   STRING,
    log_time TIMESTAMP
)
PARTITIONED BY (log_date DATE)
CLUSTERED BY (user_id)
INTO 32 BUCKETS;
```

## Notes

- `SORTED BY` must be used together with `CLUSTERED BY` and cannot be specified alone.
- It is recommended to estimate the number of buckets based on data volume: aim for approximately 128 MB–1 GB of data per bucket.
- Clustered keys and sorted keys cannot be modified via `ALTER TABLE` after table creation. The table must be recreated.
- For partitioned tables, clustering is performed independently within each partition, and the bucket count applies to each partition.
