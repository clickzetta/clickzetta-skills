# VECTOR Type

VECTOR is the native vector data type in Singdata Lakehouse, used for storing and computing high-dimensional floating-point arrays. It is the core data structure for AI applications — text, images, and audio processed by embedding models are converted into vectors, stored in VECTOR columns, and then retrieved via vector similarity search to find semantically similar content.

## Feature Overview

**When to use VECTOR**:
- Building RAG (Retrieval-Augmented Generation) knowledge bases to store document embeddings
- Image/audio similarity search
- User/item feature vectors in recommendation systems
- Any query scenario requiring "semantic similarity" rather than "exact match"

**Differences from ARRAY**:
| Feature | VECTOR | ARRAY |
|---------|--------|-------|
| **Purpose** | Optimized for vector similarity search | General-purpose collection type |
| **Dimension** | Fixed dimension | Dynamic length |
| **Element type** | Numeric only (`float`, `int`, `tinyint`) | Any type |
| **Index support** | Supports HNSW vector index acceleration | Not supported |

---

## Syntax and Definition

```Plain
vector(scalar_type, dimension)
vector(dimension)
```

- `scalar_type`: vector element type, optional, defaults to `float`. Supports `tinyint`, `int`, `float`
- `dimension`: vector dimension (number of elements), required

**Table creation example**:

```SQL
CREATE TABLE doc_embeddings (
    doc_id   BIGINT,
    content  STRING,
    vec_1536 vector(float, 1536),  -- OpenAI text-embedding-3-small output dimension
    vec_512  vector(512),          -- Default float, dimension 512
    vec_int8 vector(tinyint, 128)  -- Quantized vector, saves storage
);
```

---

## Vector Operations and Functions

Lakehouse provides a set of built-in functions for vector computation.

### 1. Distance and Similarity Calculation

This is the core of vector search, used to measure how close two vectors are.

| Function | Description | Use Case |
|----------|-------------|----------|
| `L2_DISTANCE(v1, v2)` | Euclidean distance; smaller value means more similar | Image, audio feature matching |
| `COSINE_DISTANCE(v1, v2)` | Cosine distance; smaller value means more similar | Text semantic similarity (most common) |
| `INNER_PRODUCT(v1, v2)` | Inner product; larger value means more similar | Similarity of normalized vectors |

**Example**:

```SQL
SELECT 
    l2_distance(vector(1, 2), vector(3, 4)) AS l2_dist,       -- Result: 2.828
    cosine_distance(vector(1, 2), vector(3, 4)) AS cos_dist;  -- Result: 0.016
```

### 2. Vector Normalization

`l2_normalize(v)` scales a vector to a unit vector (magnitude of 1).

> ⚠️ **Note**: The normalization function requires floating-point input. If you pass an `int` type vector, the result may be truncated to 0.

```SQL
-- Correct: ensure input is float type
SELECT l2_normalize(vector(3.0, 4.0)); 
-- Result: [0.6, 0.8]

-- Incorrect: int vector normalizes to [0, 0]
SELECT l2_normalize(vector(3, 4)); 
```

### 3. Dot Product

`dot_product(v1, v2)` computes the dot product of two vectors.

```SQL
SELECT dot_product(vector(1, 2), vector(3, 4)); 
-- Result: 1*3 + 2*4 = 11
```

---

## Advanced Query Examples

### Scenario 1: Semantic Similarity Search

Find the Top K documents most similar to a query vector.

```SQL
-- Assume query_vec is the vector produced by embedding the user's input
SELECT
    doc_id,
    content,
    COSINE_DISTANCE(vec_1536, CAST('[0.12, 0.34, ...]' AS vector(1536))) AS dist
FROM doc_embeddings
WHERE COSINE_DISTANCE(vec_1536, CAST('[0.12, 0.34, ...]' AS vector(1536))) < 0.3
ORDER BY dist
LIMIT 5;
```

### Scenario 2: Extracting Vectors from JSON

If embedding results are stored or transmitted in JSON format, use `json_extract` to extract and convert to VECTOR.

```SQL
-- Note: directly querying a VECTOR column may raise an error; cast to STRING to view
SELECT 
    CAST(
        CAST(json_extract_string(parse_json('{"vec": [0.1, 0.2, 0.3]}'), '$.vec') 
        AS vector(3)) 
    AS STRING) AS vec_from_json;
```

### Scenario 3: Real-time Generation with AI_EMBEDDING

Use the `ai_embedding` function to convert text directly to vectors for end-to-end semantic search.

```SQL
-- Compute the query text vector in real time and perform search
SELECT 
    doc_id, 
    content,
    COSINE_DISTANCE(vec_1536, ai_embedding('endpoint:my_model', 'user query text')) AS dist
FROM doc_embeddings
ORDER BY dist
LIMIT 5;
```

> ⚠️ **Note**: Using `ai_embedding` requires pre-configuring an AI model endpoint.

---

## Type Conversion

| Conversion Direction | Method | Notes |
|---------------------|--------|-------|
| STRING → VECTOR | `CAST('[1,2,3]' AS vector(3))` | String format is `[v1, v2, ...]`; extra spaces are ignored |
| ARRAY → VECTOR | `CAST(arr AS vector(n))` | Array length must match dimension n; otherwise returns NULL |
| VECTOR → ARRAY | Implicit conversion | Can be passed directly to functions that accept ARRAY arguments |
| VECTOR → STRING | `CAST(vec AS STRING)` | Output format is `[1, 2, 3]` (comma followed by space) |

**Conversion examples**:

```SQL
-- ARRAY → VECTOR (dimension matches)
SELECT CAST(array(1.0, 2.0, 3.0) AS vector(3));  -- Success

-- ARRAY → VECTOR (dimension mismatch, returns NULL)
SELECT CAST(array(1.0, 2.0) AS vector(3));  -- NULL

-- VECTOR implicitly converted to ARRAY for computation
SELECT array_append(vector(1, 2, 3), 4);  -- [1, 2, 3, 4]
```

---

## Vector Index Acceleration

For large-scale vector data, it is recommended to create a vector index to accelerate ANN (Approximate Nearest Neighbor) search:

```SQL
-- Create HNSW vector index
CREATE VECTOR INDEX idx_vec ON doc_embeddings (vec_1536)
USING HNSW
PROPERTIES (
    "metric_type" = "cosine"
);
```

See [Create Vector Index](create-vector-index.md) for details.

---

## Performance Optimization Tips

1. **Quantized storage**: For storage-sensitive scenarios, use `tinyint` type quantized vectors (e.g., `vector(tinyint, 128)`). Storage is only 1/4 of `float`, and computation is faster.
2. **Scalar pre-filtering**: Before vector search, apply scalar conditions first (e.g., `WHERE category = 'AI'`) to reduce the number of vectors participating in distance computation and improve query efficiency.
3. **Query limitations**:
    - VECTOR columns do not support `ORDER BY`, `GROUP BY`, or `DISTINCT`.
    - Directly selecting a vector column (`SELECT vector_col`) may raise an error; use `CAST(vector_col AS STRING)` to view data.

---

## Related Documents

- [Vector Search Guide](vector-search.md)
- [Create Vector Index](create-vector-index.md)
- [AI_EMBEDDING Function](ai_embedding.md)
- [Data Types](data-type.md)
