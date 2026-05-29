## RRF Algorithm Principles

### **What is RRF?**

**Reciprocal Rank Fusion** is a multi-retrieval result fusion algorithm that merges results from multiple retrieval systems through reciprocal rank weighting.

**Core Formula**:

```undefined
RRF Score = Sigma (1 / (k + rank_i))
```

* `rank_i`: The document's rank in the i-th retrieval system
* `k`: Smoothing constant (typically set to 60 to avoid division by zero)

### **Why RRF Is Needed**

|                   |                        |                        |                       |
| ----------        | -----------------      | -------------          | ---------             |
| **Retrieval Method** | **Advantages**       | **Disadvantages**       | **Typical Use Cases** |
| **Full-Text Search** | Precise keyword matching, strong interpretability | Cannot understand semantics, poor synonym recall | Exact queries, proper nouns |
| **Vector Search** | Semantic understanding, good synonym recall | Poor exact matching, may deviate from keywords | Semantic queries, fuzzy search |
| **RRF Hybrid**    | Combines advantages of both, 90%+ recall rate | Requires reasonable weight configuration | Comprehensive retrieval needs |

## Core Product Capabilities

* AI Function: In Singdata Lakehouse, Functions can be called using standard SQL, completing AI service construction by calling AI Gateway large models.

  * Data Processing: Provides AI_EMBEDDING operators to process unstructured data into structured data storage, enabling automatic embedding without external algorithms.
  * Data Retrieval and Analysis: Provides AI_COMPLETE and other operators, enabling data reasoning, question summarization, translation, and other capabilities using SQL.

* Dynamic Table: Supports incremental refresh mode for automatic processing of unstructured data, computing only incremental data each time, effectively reducing redundant computation and lowering resource utilization.

* Vector Search: Supports standard SQL vector search for similarity search, scene recognition, etc., of unstructured data, allowing free vector + scalar retrieval in a single query.

* Full-Text Search: Achieves efficient retrieval of unstructured data through inverted indexes and tokenization mechanisms, supporting rich retrieval methods such as keyword matching and phrase search.

## Implementation Steps

### **Step 1: Create Base Data Table**

```SQL
CREATE TABLE documents (    
doc_id BIGINT PRIMARY KEY,    
title STRING,    
content STRING,    
author STRING,    
category STRING,    
publish_time STRING,    
update_time STRING,    
word_count INT,    
doc_type STRING  -- article/video/audio/product
)COMMENT 'Document metadata table';
```

### **Step 2: Create Full-Text Search Index**
```SQL
-- Create inverted index for content (full-text search)
CREATE INVERTED INDEX idx_content_fulltext ON TABLE documents(content)
COMMENT 'Content full-text search index'
PROPERTIES( 'analyzer'='chinese','mode'='smart');

-- Create inverted index for title
CREATE INVERTED INDEX idx_title_fulltext ON TABLE documents(title)
COMMENT 'Title full-text search index'
PROPERTIES('analyzer'='chinese','mode'='smart');

-- Verify indexes
SHOW INDEX FROM documents;
```

### **Step 3: Create Vector Embedding Dynamic Table (Automatic Processing)**

```SQL
-- Create dynamic table: automatically generate vector embeddings for new documents
CREATE OR REPLACE DYNAMIC TABLE document_embeddings(    
doc_id BIGINT,    
title_embedding VECTOR(FLOAT, 1024),    
content_embedding VECTOR(FLOAT, 1024),    
embedding_model STRING,   
embedding_version STRING,    
created_time TIMESTAMP,    
-- High-precision scenario configuration (for AI applications requiring high accuracy)
INDEX high_precision_idx(title_embedding) USING VECTOR 
PROPERTIES(    
'scalar.type' = 'f32',    
'distance.function' = 'cosine_distance',    
'm' = '32',                    -- Increase neighbor count for higher precision
'ef.construction' = '256',     -- Increase candidate set for higher quality
'compress.codec' = 'zstd'      -- Enable compression to save space
),     
-- High-performance scenario configuration (for real-time applications requiring speed)
INDEX high_speed_idx(content_embedding) USING VECTOR 
PROPERTIES(    
'scalar.type' = 'f16',    
'distance.function' = 'l2_distance',   
 'm' = '32',                    -- Increase neighbor count for higher precision
'ef.construction' = '256',     -- Increase candidate set for higher quality
'compress.codec' = 'zstd'      -- Enable compression to save space
)
)COMMENT 'Automatic vector embedding generation table'
PROPERTIES('data_lifecycle'='30') REFRESH INTERVAL 5 MINUTE VCLUSTER default_ap 
AS SELECT    d.doc_id,    
-- Generate title vector (using AI_EMBEDDING function)
AI_EMBEDDING( 
'endpoint:text-embedding-v4',
d.title,
JSON '{"input": "text","embedding.dimension": "1024"}' 
) as title_embedding,   
-- Generate content vector (truncated to first 8000 characters)
AI_EMBEDDING( 
'endpoint:text-embedding-v4',
 LEFT(d.content, 8000), 
JSON '{ "input": "text", "embedding.dimension": "1024"  }' 
) as content_embedding,  
'text-embedding-v4' as embedding_model,    
'v4' as embedding_version,    
CURRENT_TIMESTAMP() as created_time
FROM documents d
WHERE d.content IS NOT NULL  AND LENGTH(d.content) > 0;
```

**AI_EMBEDDING Function Syntax**:
```sql
AI_EMBEDDING( 'endpoint:endpoint_name', -- Required: Model endpoint
input_text,                             -- Required: Input text (can be a field)
JSON '{                                 -- Optional: Model hyperparameters
        "input": "text",
        "embedding.dimension": "1024" 
         }'
)
```

**Dynamic Table Syntax**:
```SQL
-- Dynamic table standard syntax (direct SELECT, no INSERT INTO required)
CREATE DYNAMIC TABLE table_name
COMMENT 'Description'
PROPERTIES('data_lifecycle'='days')
REFRESH INTERVAL time_interval VCLUSTER cluster_name
AS SELECT ...;
```

### **Step 4: Implement RRF Hybrid Retrieval Query**

```sql
-- RRF hybrid retrieval query
WITH
-- Full-text search results
fulltext_search AS (
SELECT
doc_id,
title,
content,
category,
publish_time,
-- Full-text search score (based on keyword match degree)
ROW_NUMBER() OVER (ORDER BY SCORE() DESC) as fulltext_rank
FROM documents
WHERE multi_match(title,content, 'data data asset data quality data lineage', str_to_map('analyzer:chinese,minimum_should_match:67%'))
LIMIT 100
)
-- Vector search results
,vector_search AS (
SELECT
d.doc_id,
d.title,
d.content,
d.category,
d.publish_time,
-- Vector similarity score
COSINE_DISTANCE(
e.content_embedding,
AI_EMBEDDING(
    'endpoint:text-embedding-v4',
    'Architecture design principles of modern big data platforms, including data collection, storage, computing, and service layers',
    JSON '{
        "input": "query",
        "embedding.dimension": "1024"
}')) as vector_score,
ROW_NUMBER() OVER (ORDER BY COSINE_DISTANCE(
    e.content_embedding,
    AI_EMBEDDING(
        'endpoint:text-embedding-v4',
        'Architecture design principles of modern big data platforms, including data collection, storage, computing, and service layers',
        JSON '{
            "input": "query",
            "embedding.dimension": "1024"
}')) ASC
) as vector_rank
FROM documents d
JOIN document_embeddings e ON d.doc_id = e.doc_id
WHERE d.content IS NOT NULL
LIMIT 100
),
-- RRF score calculation
rrf_calculation AS (
SELECT
COALESCE(f.doc_id, v.doc_id) as doc_id,
COALESCE(f.title, v.title) as title,
COALESCE(f.content, v.content) as content,
COALESCE(f.category, v.category) as category,
COALESCE(f.publish_time, v.publish_time) as publish_time,
v.vector_score,
f.fulltext_rank,
v.vector_rank,
-- RRF Score calculation
(1.0 / (60 + COALESCE(f.fulltext_rank, 1000))) +
(1.0 / (60 + COALESCE(v.vector_rank, 1000))) as rrf_score
FROM fulltext_search f
FULL OUTER JOIN vector_search v ON f.doc_id = v.doc_id
)
-- Final results
SELECT
doc_id,
title,
content,
category,
publish_time,
vector_score,
fulltext_rank,
vector_rank,
rrf_score,
-- Rank explanation
CASE WHEN fulltext_rank IS NOT NULL AND vector_rank IS NOT NULL THEN 'Hybrid Hit'
WHEN fulltext_rank IS NOT NULL THEN 'Full-Text Only'
WHEN vector_rank IS NOT NULL THEN 'Vector Only'
ELSE 'Unknown'
END as hit_type
FROM rrf_calculation
ORDER BY rrf_score DESC
LIMIT 20;
```
