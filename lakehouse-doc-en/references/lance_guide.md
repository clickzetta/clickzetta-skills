# Lance External Tables

## Overview

Lance is a columnar storage format designed for machine learning, with native support for vector data and ANN (Approximate Nearest Neighbor) indexes. Lakehouse reads Lance datasets stored on OSS directly via the external table mechanism, enabling vector similarity search without any data migration.

Use cases: vector retrieval, image/text semantic search, RAG knowledge base queries, recommendation system candidate recall.

## SQL Commands Involved

| Command / Function                      | Purpose                                                    | When to Use                                      |
| --------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------ |
| `CREATE STORAGE CONNECTION`             | Create OSS access credentials                              | Run once when first connecting to OSS            |
| `CREATE EXTERNAL TABLE ... USING LANCE` | Mount a Lance dataset as an external table                 | Run once per Lance dataset                       |
| `DESCRIBE TABLE`                        | View column definitions and vector dimensions              | Verify that the schema matches the Lance file    |
| `SHOW CREATE TABLE`                     | Reverse-engineer the full DDL                              | Troubleshoot LOCATION / CONNECTION configuration |
| `cosine_distance(a, b)`                 | Cosine distance, range \[0, 2], smaller means more similar | Text/image semantic similarity search            |
| `l2_distance(a, b)`                     | Euclidean distance, range \[0, +∞)                         | Spatial distance, image feature matching         |

***

## Prerequisites

All examples in this guide are based on the following test dataset:

* OSS path: `oss://lakehouse-hz-daily/clickzetta/lance/test_lance_1024_cosine_small.lance`
* Row count: 8,192 rows
* Vector dimensions: 1,024 (float32)
* Index type: cosine ANN

> ⚠️ **Note**: The Lakehouse cluster must be on the same cloud provider as the OSS bucket (Alibaba Cloud in this example). Cross-cloud access (e.g., a Tencent Cloud cluster accessing Alibaba Cloud OSS) will result in query timeouts due to network connectivity issues.

***

## Scenario 1: Create a Lance External Table

### Create a Storage Connection

```SQL
CREATE STORAGE CONNECTION IF NOT EXISTS conn_oss
  TYPE oss
  ENDPOINT   = 'oss-cn-hangzhou.aliyuncs.com'
  ACCESS_ID  = '<your-access-key-id>'
  ACCESS_KEY = '<your-access-key-secret>';
```

Verify the connection was created successfully:

```SQL
DESCRIBE CONNECTION conn_oss;
```

Sample output:

```
info_name  | info_value
-----------+------------------------------
name       | conn_oss
type       | OSS
enabled    | ENABLED
ACCESS_ID  | LTAI5t********************
ENDPOINT   | oss-cn-hangzhou.aliyuncs.com
```

### Create the Lance External Table

```SQL
CREATE EXTERNAL TABLE IF NOT EXISTS `doc_lance_cosine` (
  `id`        bigint,
  `key`       string,
  `type`      string,
  `meta`      string,
  `timestamp` timestamp,
  `tag`       string,
  `k_id`      string,
  `source`    string,
  `vec`       vector(float, 1024)
) USING LANCE
LOCATION 'oss://lakehouse-hz-daily/clickzetta/lance/test_lance_1024_cosine_small.lance'
CONNECTION conn_oss;
```

**Key parameter notes**:

* `USING LANCE`: Specifies the format as Lance.
* `LOCATION`: The OSS path pointing to the root of the `.lance` directory (which must contain a `_versions/` subdirectory).
* `CONNECTION`: References the name of an already-created Storage Connection.
* `vector(float, N)`: The vector column type. `N` must exactly match the dimension of the `fixed_size_list` in the Lance file; otherwise queries will return NULL.

> ⚠️ **Note**: The path specified in `LOCATION` must be a valid Lance dataset (containing a `_versions/` directory). If the path does not exist, you will get the error: `Dataset at path xxx was not found: Not found: xxx/_versions`. You can validate the path in advance with the following script:
>
> ```bash
> python3 -c "
> import oss2
> auth = oss2.Auth('<access_id>', '<access_key>')
> bucket = oss2.Bucket(auth, 'https://oss-cn-hangzhou.aliyuncs.com', '<bucket>')
> for obj in oss2.ObjectIterator(bucket, prefix='your/path.lance/', delimiter='/'):
> print(obj.common_prefix)  # should include _versions/
> "
> ```

Verify the external table was created successfully:

```SQL
SHOW TABLES LIKE 'doc_lance_cosine';
```

Sample output:

```
schema_name | table_name       | is_external
------------+------------------+------------
public      | doc_lance_cosine | true
```

***

## Scenario 2: Basic Data Reading

### Row Count

```SQL
SELECT COUNT(*) AS row_count FROM doc_lance_cosine;
```

Sample output:

```
row_count
---------
8192
```

### Read Scalar Columns

```SQL
SELECT id, key, source FROM doc_lance_cosine LIMIT 5;
```

Sample output:

```
id     | key     | source
-------+---------+---------
912569 | key_934 | source_7
912608 | key_941 | source_4
912645 | key_287 | source_5
912648 | key_322 | source_8
912678 | key_862 | source_2
```

### Read the Vector Column

```SQL
SELECT id, vec FROM doc_lance_cosine LIMIT 1;
```

Sample output (vector values truncated):

```
id     | vec
-------+--------------------------------------------------------------
912569 | [0.5198276, 0.46438155, 0.032661837, 0.2069788, ... (1024 dims)]
```

### Filter by Scalar Column

```SQL
SELECT id, key, source
FROM   doc_lance_cosine
WHERE  source = 'source_1'
LIMIT  5;
```

Sample output:

```
id     | key     | source
-------+---------+---------
912959 | key_902 | source_1
913180 | key_377 | source_1
913430 | key_714 | source_1
913438 | key_643 | source_1
913582 | key_235 | source_1
```

### Group-by Aggregation

```SQL
SELECT source, COUNT(*) AS cnt
FROM   doc_lance_cosine
GROUP  BY source
ORDER  BY cnt DESC;
```

Sample output:

```
source   | cnt
---------+----
source_7 | 892
source_5 | 839
source_6 | 817
source_4 | 817
source_8 | 816
source_2 | 813
source_0 | 805
source_3 | 803
source_9 | 799
source_1 | 791
```

10 source groups, 8,192 total rows, with a fairly even distribution (approximately 800 rows per group).

***

## Scenario 3: Vector Similarity Search

### Top-K Cosine Distance Search

Query the 20 most similar records to a given vector using the `cosine_distance` function — smaller values indicate greater similarity.

```SQL
SELECT key,
       id,
       cosine_distance(
         vec,
         [-0.017264263704419136, 0.003988612908869982, -0.06441465020179749,
          -- ... 1024 float values total
         ]
       ) AS dist
FROM   doc_lance_cosine
WHERE  cosine_distance(
         vec,
         [-0.017264263704419136, 0.003988612908869982, -0.06441465020179749,
          -- ... 1024 float values total
         ]
       ) <= 1000.0
ORDER  BY dist
LIMIT  20;
```

`WHERE cosine_distance(...) <= 1000.0` is a loose threshold used to trigger Lance's ANN index acceleration. In production, you can tighten the threshold based on your similarity requirements (e.g., `<= 0.3`).

### Verify Vector Distance Function Accuracy

Use self-similarity to verify correctness (the cosine distance between a vector and itself should be close to 0):

```SQL
SELECT id, cosine_distance(vec, vec) AS self_dist
FROM   doc_lance_cosine
LIMIT  3;
```

Sample output:

```
id     | self_dist
-------+------------------------
912569 | 5.960464477539063e-8
912608 | -1.1920928955078125e-7
912645 | -1.1920928955078125e-7
```

All self-similarity absolute values are below `1e-6`, which is consistent with float32 precision expectations (theoretical value is 0; floating-point error is within the normal range).

***

## Scenario 4: Hybrid Filter Queries

Vector distance filtering and scalar column filtering can be combined. Use scalar conditions to narrow the candidate set first, then sort by vector distance.

```SQL
SELECT key,
       id,
       source,
       cosine_distance(vec, vec) AS dist
FROM   doc_lance_cosine
WHERE  source = 'source_1'
  AND  cosine_distance(vec, vec) <= 1.0
ORDER  BY dist
LIMIT  5;
```

Sample output:

```
key     | id     | source   | dist
--------+--------+----------+------------------------
key_902 | 912959 | source_1 | -1.1920928955078125e-7
key_377 | 913180 | source_1 | -1.1920928955078125e-7
key_714 | 913430 | source_1 | -1.1920928955078125e-7
key_643 | 913438 | source_1 | -1.1920928955078125e-7
key_235 | 913582 | source_1 | -1.1920928955078125e-7
```

Only rows with `source = 'source_1'` are returned, confirming that both the scalar filter and the vector distance filter are applied correctly.

***

## Important Notes

* **Vector dimensions must match exactly**: The `N` in `vector(float, N)` in the DDL must exactly match the length of `fixed_size_list` in the Lance file. If dimensions do not match, queries will not error but the vector distance column will return NULL.

* **Timestamp column type mapping**: The `timestamp` type in Lance may be mapped to `bigint` (Unix timestamp in seconds) in Lakehouse. The actual type shown by `SHOW CREATE TABLE` is determined by system inference; declaring `timestamp` in the DDL does not affect data reading.

* **Lance version**: The current supported format is Lance v2 (`TBLPROPERTIES('lance.version'='2')`).

* **Cross-cloud networking**: The Lakehouse cluster and the OSS bucket must be on the same cloud provider. Cross-cloud access (e.g., a Tencent Cloud cluster accessing Alibaba Cloud OSS) will cause query timeouts (default 300s) due to network connectivity issues.

***

## Related Documentation

* [Create Storage Connection](create-storage-connection.md)
* [Create External Table](create-external-table.md)
* [Vector Search and RAG Application Guide](sql_vector_search_guide.md)
* [Vector Function Reference](vector-functions.md)

^
