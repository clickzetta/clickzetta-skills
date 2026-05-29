## Overview

Lakehouse supports vector types, vector search functions, and vector indexes, enabling vector retrieval scenarios through vector search functions. The vector data type is an ordered collection of numerical values with fixed dimensions. Vectors can represent various data types, such as vector embeddings obtained from large language models (LLM), image or facial vector embeddings, financial time series, spatial coordinates, velocity, color, etc. Using the vector data type makes it easier to insert, load, and query vectors.

Lakehouse provides vector types and vector index retrieval. Vectors are structured numerical representations that modern deep learning techniques can create from unstructured data (such as text and images), while preserving the semantic concepts of similarity and dissimilarity in the geometric structure of the generated vectors. Lakehouse offers the VECTOR type to store these transformed vectors, and building indexes can improve vector search performance.

## Vector Features Supported by Lakehouse

* **Vector Storage**: Store vectors using the `VECTOR` type.
* **Vector Indexing**: Build vector indexes using the HNSW (Hierarchical Navigable Small World) algorithm to accelerate computation.
* **Distance Calculation**: Support various functions to calculate vector similarity, including functions like `L2_DISTANCE` and `COSINE_DISTANCE`.

## Usage Considerations

* The current version of the vector type does not support comparison operations, so it cannot be used in `ORDER BY` or `GROUP BY` clauses.
* The current client does not implement the vector type, but it is supported in the SQL engine. Therefore, when you execute a select result that includes the vector type, an error will occur: Unsupported data type: VECTOR\_TYPE.
* The performance of vector indexing is directly related to memory cache and disk cache. It is recommended to use a separate VC. Mixing with other scenarios may compete for cache and result in performance not meeting expectations.

## Lakehouse Vector Usage

**Creating Vectors**

```SQL

CREATE TABLE test_vector1 (
    vec vector(float, 4),
    id int,
    index test_vector1_vec_idx  (vec) using vector properties (
        "scalar.type" = "f32",
        "distance.function" = "l2_distance"
    )
);
```

properties supports specifying parameters, refer to [Create Vector Index Documentation](create-vector-index.md)

**Insert Data**

* Use SQL to insert

```SQL
INSERT INTO test_vector1 (vec, id) VALUES
    (vector(0.1, 0.2, 0.3, 0.4), 1),
    (vector(0.5, 0.6, 0.7, 0.8), 2),
    (vector(0.9, 1.0, 1.1, 1.2), 3),
    (vector(1.3, 1.4, 1.5, 1.6), 4),
    (vector(1.7, 1.8, 1.9, 2.0), 5),
    (vector(2.1, 2.2, 2.3, 2.4), 6),
    (vector(2.5, 2.6, 2.7, 2.8), 7),
    (vector(2.9, 3.0, 3.1, 3.2), 8),
    (vector(3.3, 3.4, 3.5, 3.6), 9),
    (vector(3.7, 3.8, 3.9, 4.0), 10);
```

* If you are writing to the Lakehouse through an external system, the current Lakehouse does not support direct writing of vectors. You can write it as an array, and then use `insert overwrite select cast (array_col as vector)` for conversion.
  * ```SQL
    CREATE  TABLE arraytable (vec ARRAY,id int);
    SELECT vec::VECTOR(FLOAT, 3)
    FROM arraytable;
    ```
* If the data is in object storage, you can directly use volume to import the vector type

**Vector Retrieval**

```SQL
SELECT id, l2_distance(vec, vector(1,2,3,4)) AS dist FROM test_vector1 WHERE l2_distance(vec, vector(1,2,3,4)) < 4.0 ORDER BY dist LIMIT 5;
```

When you need to confirm whether the vector index is effective, you can use the `EXPLAIN SELECT ...` syntax to check if the TableScan operator contains the term vector\_index\_search\_type.

```SQL
PhysicalTableSink()
  PhysicalLocalSort_L3($10)
    PhysicalShuffleRead()
      PhysicalShuffleWrite_SINGLETON()
        PhysicalLocalSort_L3($10)
          PhysicalCalc(NVL($4292967295, L2_DISTANCE($0, [1,2,3,4])), LT(_TRY_TO_FLOAT64(#0), 3.020000), $1) as [1, 10]
            PhysicalTableScan(test_vector1, LT(_TRY_TO_FLOAT64(NVL(@4292967295, L2_DISTANCE(#0, [1,2,3,4]))), 3.020000, expr_key=4292967295, limit=3, vector_index_search_type=ann), F4M:LT(_TRY_TO_FLOAT64(L2_DISTANCE(#0, [1,2,3,4])), 3.020000), GEN:[L2_DISTANCE(#0, [1,2,3,4]) as 4292967295], vec, id) as [0, 1, 4292967295]
```

When the vector index is not effective, it will degrade to brute force search.

## Using with Inverted Indexes Simultaneously

The vector index can only solve the vector search problem. When combined with other field-related filtering conditions, it will directly degrade to a brute force algorithm. To solve this problem, there are generally two approaches.

1. First perform vector search in a subquery, and then execute other field filtering conditions in the outer query. Although this solution has fast query performance, if the filtering of non-vector fields is relatively high, the final output result is often less than the number of data expected by the user, or even empty.

```SQL
SELECT id, doc, dist FROM (
    SELECT id, doc, l2_distance(vec, vector(1,2,3,4)) as dist FROM some_table WHERE l2_distance(vec, vector(1,2,3,4)) < 1000 ORDER BY dist LIMIT 100
) WHERE doc like '%hello%';
```

```markdown
2. Build an inverted index on commonly used non-vector fields and use it together with vector search:
```

```SQL
-- Create table
CREATE TABLE test_vector1 (
    vec vector(float, 4),
    index test_vector1_vec_idx  (vec) using vector properties (
        "scalar.type" = "f32",
        "distance.function" = "l2_distance"
    ),
    doc string,
    index test_vector1_doc_idx on (doc) using inverted properties ('analyzer' = 'keyword');,
    id int
) ;

-- Query
SET cz.sql.index.prewhere.enabled=true; -- Currently, the switch needs to be set, and it will be enabled by default in future versions
SELECT id, doc, l2_distance(vec, vector(1,2,3,4)) as dist FROM some_table WHERE match_regexp(doc, '.*hello.*', map('analyzer', 'keyword')) AND l2_distance(vec, vector(1,2,3,4)) < 1000 ORDER BY dist LIMIT 100
```

In the above example, the execution process is: first, use the inverted index to filter out the matching rows based on `match_regexp(doc, '.*hello.*', map('analyzer', 'keyword'))`, and then perform vector search on the matching rows.

## Parameters Supported in Vector Search Queries

|                                                       |               |                                                                                                                                                                 |
| ----------------------------------------------------- | ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name                                                  | Default Value | Notes                                                                                                                                                           |
| cz.storage.parquet.vector.index.read.memory.cache     | false         | Whether to use memory cache                                                                                                                                     |
| cz.storage.parquet.vector.index.read.local.cache      | false         | Whether to use local SSD cache                                                                                                                                  |
| cz.storage.parquet.vector.index.read.vectors.ondemand | adaptive      | Whether to load vector index on demand (slower than using memory cache)                                                                                         |
| cz.storage.parquet.vector.index.write.parallel        | 0             | Whether to enable parallel writing, 0 means off, 8 means 8 threads writing. Note that the performance improvement is not proportional to the number of threads. |

Usage example. Select to execute together when using SQL query

```SQL
SET cz.sql.index.prewhere.enabled=true; -- Currently, you need to set the switch, and it will be enabled by default in future versions
SELECT id, doc, l2_distance(vec, vector(1,2,3,4)) as dist FROM some_table WHERE match_regexp(doc, '.*hello.*', map('analyzer', 'keyword')) AND l2_distance(vec, vector(1,2,3,4)) < 1000 ORDER BY dist LIMIT 100
```

## Billing

* Storage Resources: The vector index will create vector index files, and both the index files and data files are stored in object storage, with unified billing.

^
