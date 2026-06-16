# Lakehouse Index Best Practice Guide

## Summary

This guide provides comprehensive best practice recommendations for index usage on the Singdata Lakehouse platform. Through proper indexing strategies, you can significantly improve query efficiency, covering everything from millisecond-level exact lookups to intelligent semantic search across all scenarios.

**Core Benefits**:

* **Complete Functionality**: Supports both traditional retrieval and AI semantic search
* **Query Optimization**: Multi-index coordination reduces full table scans
* **Intelligent Retrieval**: Native support for vector search and semantic retrieval
* **Simplified Operations**: Provides complete index management and troubleshooting processes

***

## 1. Overview and Applicable Scenarios

### 1.1 Index Type Overview

Singdata Lakehouse supports three optimized index types:

| Index Type      | Core Advantage     | Best Use Case        | Technical Feature      |
| --------- | ----------- | ----------- | --------- |
| **Bloom Filter** | Fast existence check | ID exact lookup, fast filtering | Probabilistic data structure  |
| **Inverted Index**  | Intelligent tokenization    | Full-text search, text retrieval   | Multi-language tokenization support  |
| **Vector Index**  | Semantic understanding    | AI applications, similarity search  | HNSW algorithm optimization |

### 1.2 Business Scenario Mapping

**E-commerce Platform**: Product search (Inverted Index) + User profile matching (Vector Index) + Fast filtering (Bloom Filter)

**Intelligent Customer Service**: Knowledge base retrieval (Inverted Index) + Semantic similarity (Vector Index) + User permissions (Bloom Filter)

**Content Recommendation**: Tag matching (Inverted Index) + User preference (Vector Index) + Real-time filtering (Bloom Filter)

***

## 2. Quick Start Guide

### 2.1 Creating Your First Multi-Index Table

**Step 1: Design Table Structure**

```sql
CREATE TABLE ai_knowledge_base (
    doc_id BIGINT,
    title STRING,
    content STRING,
    category STRING,
    tags STRING,
    author_id BIGINT,
    embedding VECTOR(FLOAT, 768),
    view_count INT,
    create_time TIMESTAMP,
    update_time TIMESTAMP,
    
    -- Inverted index: multiple tokenization strategies
    INDEX title_search_idx (title) INVERTED PROPERTIES('analyzer'='unicode'),
    INDEX content_search_idx (content) INVERTED PROPERTIES('analyzer'='chinese'),
    INDEX category_exact_idx (category) INVERTED PROPERTIES('analyzer'='keyword'),
    INDEX tags_search_idx (tags) INVERTED PROPERTIES('analyzer'='chinese'),
    
    -- Vector index: semantic similarity search  
    INDEX embedding_vector_idx (embedding) USING VECTOR PROPERTIES(
        'scalar.type' = 'f32',
        'distance.function' = 'cosine_distance',
        'm' = '16',
        'ef.construction' = '128'
    )
) COMMENT 'AI Knowledge Base - Multi-Index Fused Retrieval';
```

**Step 2: Add Bloom Filter Indexes**

```sql
CREATE BLOOMFILTER INDEX doc_id_bloom_idx ON TABLE ai_knowledge_base(doc_id);
CREATE BLOOMFILTER INDEX author_id_bloom_idx ON TABLE ai_knowledge_base(author_id);
```

**Step 3: Insert Demo Data**

```sql
-- Insert complete demo data including embedding vectors
INSERT INTO ai_knowledge_base (doc_id, title, content, category, tags, author_id, embedding, view_count, create_time, update_time) VALUES

-- AI-related documents (similar vector pattern: higher values in first dimensions)
(1001, 'Singdata Vector Database Technology Deep Dive', 
'Singdata Lakehouse provides advanced vector database functionality, supporting high-dimensional vector storage and retrieval. Using HNSW algorithm for high-performance approximate nearest neighbor search, suitable for AI recommendation systems, image recognition, natural language processing and other scenarios. Vector indexes support multiple similarity calculation methods including cosine distance and Euclidean distance.', 
'Technical Documentation', 'Vector Database AI Machine Learning HNSW Algorithm', 2001, 
ARRAY[0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1] || ARRAY_REPEAT(0.1, 760)::ARRAY<FLOAT>, 
1250, timestamp '2024-05-20 10:00:00', timestamp '2024-05-25 15:30:00'),

(1002, 'AI Large Model Training Platform Architecture Design', 
'Building an AI large model training platform based on Singdata Lakehouse, using distributed storage and computing architecture. The platform supports TB-level training data management, providing full-process support for data preprocessing, feature engineering, model training, and model deployment. Integrated with mainstream deep learning frameworks such as PyTorch and TensorFlow.', 
'Architecture Design', 'AI Large Models Distributed Training Deep Learning', 2002, 
ARRAY[0.75, 0.65, 0.55, 0.45, 0.35, 0.25, 0.15, 0.05] || ARRAY_REPEAT(0.05, 760)::ARRAY<FLOAT>, 
980, timestamp '2024-05-21 14:20:00', timestamp '2024-05-26 09:15:00'),

-- Recommendation system document (AI-related, vector similarity)
(1003, 'Real-Time Recommendation System Best Practices', 
'This document introduces a real-time recommendation system implementation based on Singdata Lakehouse, processing millions of user interactions per second and providing sub-hundred-millisecond personalized recommendations. Core components include feature storage, vector similarity matching, online learning algorithms, etc.', 
'Best Practices', 'Recommendation System Real-Time Computing Feature Engineering Online Learning', 2003, 
ARRAY[0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0] || ARRAY_REPEAT(0.08, 760)::ARRAY<FLOAT>, 
2100, timestamp '2024-05-22 16:45:00', timestamp '2024-05-26 11:20:00'),

-- Search engine document (different vector pattern: higher values in middle dimensions)
(1004, 'Intelligent Search Engine Optimization Strategies', 
'Detailed introduction of an intelligent search engine implementation based on Singdata Lakehouse, including inverted index construction, query understanding, relevance ranking, personalized recommendation and other core technologies. The system supports mixed Chinese-English search, with semantic understanding capabilities, able to handle synonym and near-synonym queries, providing precise and relevant search results.', 
'Technical Documentation', 'Search Engine Inverted Index Semantic Understanding Relevance Ranking', 2001, 
ARRAY_REPEAT(0.1, 300)::ARRAY<FLOAT> || ARRAY[0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2] || ARRAY_REPEAT(0.1, 460)::ARRAY<FLOAT>, 
1680, timestamp '2024-05-23 13:10:00', timestamp '2024-05-26 14:45:00'),

-- Performance optimization document (different vector pattern: higher values in later dimensions)
(1005, 'Data Lakehouse Unified Performance Tuning Guide', 
'A complete performance tuning guide for the Singdata Lakehouse unified platform, covering storage optimization, query optimization, indexing strategies, partition design and other key technologies. Through proper data modeling and index design, query performance can be improved by 10-100x. Particularly suitable for OLAP analysis, real-time reports, data mining and other scenarios.', 
'Performance Tuning', 'Data Lakehouse Performance Optimization Query Acceleration Index Strategy', 2004, 
ARRAY_REPEAT(0.05, 600)::ARRAY<FLOAT> || ARRAY[0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55] || ARRAY_REPEAT(0.1, 160)::ARRAY<FLOAT>, 
3200, timestamp '2024-05-24 11:30:00', timestamp '2024-05-26 16:00:00'),

-- Machine learning document (AI-related, vector similarity)
(1006, 'Deep Learning Model Deployment Practices', 
'A complete guide for deep learning model deployment on the Singdata Lakehouse platform, supporting automated deployment of mainstream framework models such as TensorFlow and PyTorch. Includes enterprise-grade features such as model version management, A/B testing, performance monitoring, and elastic scaling.', 
'Technical Documentation', 'Deep Learning Model Deployment TensorFlow PyTorch', 2002, 
ARRAY[0.72, 0.62, 0.52, 0.42, 0.32, 0.22, 0.12, 0.02] || ARRAY_REPEAT(0.08, 760)::ARRAY<FLOAT>, 
890, timestamp '2024-05-25 09:30:00', timestamp '2024-05-26 10:15:00'),

-- Data governance document (new category)
(1007, 'Enterprise Data Governance and Security Compliance', 
'An enterprise-grade data governance solution based on Singdata Lakehouse, providing data lineage tracking, permission management, sensitive data masking, audit logs and other functionalities. Compliant with international standards including GDPR and SOX.', 
'Data Governance', 'Data Governance Permission Management Compliance Data Security', 2005, 
ARRAY_REPEAT(0.08, 200)::ARRAY<FLOAT> || ARRAY[0.6, 0.5, 0.4, 0.3, 0.2, 0.1] || ARRAY_REPEAT(0.05, 562)::ARRAY<FLOAT>, 
1450, timestamp '2024-05-25 14:20:00', timestamp '2024-05-26 12:30:00'),

-- Real-time computing document (related to recommendation system)
(1008, 'Streaming Computing Engine Architecture Design', 
'The design and implementation of the Singdata Lakehouse streaming computing engine, supporting millisecond-level data processing latency. Can integrate with components such as Kafka and Flink, providing exactly-once semantics and automatic fault recovery capabilities.', 
'Architecture Design', 'Streaming Computing Real-Time Processing Kafka Flink', 2003, 
ARRAY[0.65, 0.55, 0.45, 0.35, 0.25, 0.15, 0.05, 0.0] || ARRAY_REPEAT(0.06, 760)::ARRAY<FLOAT>, 
1200, timestamp '2024-05-26 08:45:00', timestamp '2024-05-26 13:20:00');
```

**Step 4: Verify Data and Indexes**

```sql
-- Check data insertion status
SELECT COUNT(*) as total_records FROM ai_knowledge_base;

-- Verify index creation
DESC TABLE EXTENDED ai_knowledge_base;
-- Check the index field to confirm all indexes are created

-- View data overview
SELECT doc_id, title, category, author_id, view_count 
FROM ai_knowledge_base 
ORDER BY doc_id;
```

### 2.2 Basic Query Patterns

**Pattern 1: Exact ID Lookup (Bloom Filter)**

```sql
SELECT doc_id, title, author_id, view_count
FROM ai_knowledge_base
WHERE author_id = 2001
ORDER BY view_count DESC;

-- Expected results:
-- doc_id: 1004, title: "Intelligent Search Engine Optimization Strategies", view_count: 1680
-- doc_id: 1001, title: "Singdata Vector Database Technology Deep Dive", view_count: 1250
```

**Pattern 2: Category Exact Match (keyword inverted index)**

```sql
SELECT doc_id, title, category, view_count
FROM ai_knowledge_base 
WHERE category = 'Technical Documentation'
ORDER BY view_count DESC;

-- Expected result: returns 3 technical documentation records
```

**Pattern 3: Content Search (chinese inverted index)**

```sql
SELECT doc_id, title, view_count
FROM ai_knowledge_base
WHERE content LIKE '%platform%'
ORDER BY view_count DESC;

-- Expected result: returns documents containing "platform"
```

**Pattern 4: Semantic Search (Vector Index)**

```sql
-- AI semantic similarity search
WITH query_vector AS (
  SELECT ARRAY[0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1] || ARRAY_REPEAT(0.1, 760)::ARRAY<FLOAT> as qv
)
SELECT 
    a.doc_id, 
    a.title, 
    COSINE_DISTANCE(a.embedding, q.qv) as similarity_score
FROM ai_knowledge_base a, query_vector q
WHERE a.embedding IS NOT NULL
ORDER BY similarity_score ASC
LIMIT 3;

-- Expected result: sorted by semantic similarity, AI-related documents rank highest
```

***

## 3. Index Selection Decision Framework

### 3.1 Decision Tree

```
Query Requirement Analysis
+-- Need exact ID lookup?
|   +-- YES -> Bloom Filter Index
|       +-- Single table query -> Single Bloom Filter
|       +-- Join query -> Multiple Bloom Filters
+-- Need text content search?
|   +-- Exact category matching -> keyword tokenization + inverted index
|   +-- Chinese content search -> chinese tokenization + inverted index
|   +-- Multilingual processing -> unicode tokenization + inverted index
|   +-- Compound text query -> Multi-inverted index combination
+-- Need semantic similarity search?
|   +-- YES -> Vector Index + other index filtering
+-- Complex business queries?
    +-- Multi-index fusion strategy
```

### 3.2 Tokenizer Selection Guide

**Actual Tokenization Effect Comparison**:

```sql
-- Verify different tokenizer effects
SELECT 
    'chinese' as analyzer,
    TOKENIZE('Singdata Lakehouse Data Platform', map('analyzer', 'chinese')) as tokens
UNION ALL
SELECT 
    'unicode' as analyzer,
    TOKENIZE('Singdata Lakehouse Data Platform', map('analyzer', 'unicode')) as tokens  
UNION ALL
SELECT 
    'keyword' as analyzer,
    TOKENIZE('Singdata Lakehouse Data Platform', map('analyzer', 'keyword')) as tokens;
```

**Selection Principles**:

* **category, status fields** -> keyword (exact match, zero overhead)
* **Chinese content, description** -> chinese (intelligent tokenization, semantic understanding)
* **Mixed-language title, name** -> unicode (general support, fine-grained search)

***

## 4. Advanced Query Patterns and Optimization

### 4.1 Multi-Index Fusion Query

**Scenario: AI Intelligent Retrieval System**

```sql
-- Vector semantic search + inverted index filtering + bloom filter
WITH query_vector AS (
  SELECT ARRAY[0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1] || ARRAY_REPEAT(0.1, 760)::ARRAY<FLOAT> as qv
)
SELECT 
    a.doc_id, 
    a.title, 
    a.category,
    a.view_count,
    COSINE_DISTANCE(a.embedding, q.qv) as similarity_score
FROM ai_knowledge_base a, query_vector q
WHERE a.category IN ('Technical Documentation', 'Best Practices', 'Architecture Design')  -- inverted index category filtering
AND a.embedding IS NOT NULL  
AND a.view_count > 500  -- quality filtering
ORDER BY similarity_score ASC  -- semantic similarity first
LIMIT 5;

-- Expected result: returns the most semantically relevant high-quality documents
```

### 4.2 Demo Data Details

**Dataset Overview**: 8 technical documents covering 5 categories, 5 authors, all documents contain 768-dimensional embedding vectors

| Category       | Count | Representative Document                 | Avg Views |
| -------- | --- | --------------------- | ----- |
| **Technical Documentation** | 3 | Vector Database, Intelligent Search Engine, Deep Learning Deployment | 1,273 |
| **Architecture Design** | 2 | AI Large Model Training Platform, Streaming Computing Engine      | 1,090 |
| **Best Practices** | 1 | Real-Time Recommendation System                | 2,100 |
| **Data Governance** | 1 | Enterprise Data Governance and Security Compliance           | 1,450 |
| **Performance Tuning** | 1 | Data Lakehouse Unified Performance Tuning           | 3,200 |

**Vector Design Notes**:

* **AI-related documents**(1001,1002,1003,1006): Higher values in early dimensions, forming similar vector patterns
* **Search engine document**(1004): Higher values in middle dimensions, differentiated vector pattern
* **Performance tuning document**(1005): Higher values in later dimensions, facilitating vector similarity search verification

This design ensures the verifiability of vector search: AI-related documents cluster together, while documents on different topics have noticeable vector differences.

### 4.3 Layered Query Architecture

```
Query Request
    |
+---> Bloom Filter (fast filtering, exclude large amounts of irrelevant data)
    |
+---> keyword Inverted Index (exact category matching)
    |
+---> chinese/unicode Inverted Index (intelligent text search)
    |
+---> Vector Index (semantic similarity computation)
    |
+---> Business Condition Filtering (range queries, sorting, pagination)
    |
+---> Final Result Set
```

***

## 5. Index Management and Configuration

### 5.1 Index Management Operations

**Index Creation Best Practices**:

< date '2024-02-01';
```

**Index Status Check**:

```sql
-- View complete index information
DESC TABLE EXTENDED your_table_name;

-- View table creation statement
SHOW CREATE TABLE your_table_name;

-- Check index list
SHOW INDEX FROM your_table_name;
```

### 5.2 Vector Index Parameter Configuration

**Vector Index Parameter Details**:

| Parameter                    | Recommended Value        | Affecting Factor     | Usage Advice              |
| --------------------- | ---------- | -------- | ----------------- |
| `m`                   | 16-64      | Accuracy vs Memory   | Use 32+ for high accuracy, 16 for performance |
| `ef.construction`     | 128-512    | Build Quality vs Time | Recommend 256+ for production        |
| `scalar.type`         | f32/f16    | Accuracy vs Storage   | Generally use f32, f16 for large scale    |
| `distance.function`   | cosine/l2  | Semantic vs Spatial Distance | Use cosine for text, l2 for images   |
| `compress.codec`      | zstd/none  | Storage vs Compute   | Use zstd when storage-sensitive         |
| `reuse.vector.column` | true/false | Storage Optimization     | Recommend true for large-scale deployment       |

**High Accuracy vs High Performance Configuration Comparison**:

```sql
-- High accuracy scenario configuration (suitable for AI applications requiring high accuracy)
CREATE VECTOR INDEX high_precision_idx ON TABLE vectors(embedding)
PROPERTIES(
    'scalar.type' = 'f32',
    'distance.function' = 'cosine_distance',
    'm' = '32',                    -- Increase neighbor count for higher accuracy
    'ef.construction' = '256',     -- Increase candidate set for higher quality
    'compress.codec' = 'zstd'      -- Enable compression to save space
);

-- High performance scenario configuration (suitable for real-time applications requiring high speed)
CREATE VECTOR INDEX high_speed_idx ON TABLE vectors(embedding)
PROPERTIES(
    'scalar.type' = 'f16',         -- Half precision to reduce memory usage
    'distance.function' = 'l2_distance',
    'm' = '16',                    -- Reduce neighbor count for higher speed
    'ef.construction' = '128',
    'reuse.vector.column' = 'true' -- Reuse column data to save storage
);
```

***

## 6. Common Issues and Troubleshooting

### 6.1 Index Creation Issues

**Issue 1: Vector Index Creation Failed**

```
Error message: Vector dimension mismatch
Solution: Check whether the VECTOR(FLOAT, n) definition matches the actual data dimension
```

**Issue 2: Bloom Filter Not Taking Effect**

```
Reason: A newly created Bloom filter index only takes effect on new data; existing data requires BUILD INDEX
Solution: Run BUILD INDEX on existing data
```

**Issue 3: Poor Chinese Tokenization Results**

```
Reason: Wrong tokenizer used
Solution: Use 'analyzer'='chinese' for Chinese content, 'keyword' for exact matching

-- Verify tokenization effect
SELECT TOKENIZE('test text', map('analyzer', 'chinese')) as chinese_tokens,
       TOKENIZE('test text', map('analyzer', 'keyword')) as keyword_tokens;
```

**Issue 4: Vector Functions Not Available**

```
Error message: COSINE_DISTANCE function not found
Solution: Confirm version support, verify function availability

-- Verify vector functions
SELECT COSINE_DISTANCE(
    ARRAY[0.1, 0.2, 0.3]::ARRAY<FLOAT>
```

### 5.2 Query Optimization Issues

**Diagnostic Process**:

1. Use EXPLAIN to analyze the query plan
2. Check if indexes are being correctly used
3. Analyze data distribution and skew
4. Evaluate index selectivity

**Optimization Strategies**:

```sql
-- Anti-patterns to avoid
WHERE UPPER(category) = 'TECH'           -- Function calls destroy index
WHERE CAST(id AS STRING) = '123'         -- Type conversion affects performance
WHERE content LIKE '%keyword%keyword%'   -- Complex pattern matching

-- Recommended approaches
WHERE category = 'tech'                  -- Direct matching, preprocess data to normalize format
WHERE id = 123                          -- Type matching
WHERE content LIKE '%keyword%'          -- Simple pattern
```

### 5.3 Troubleshooting Checklist

**Index Health Check**:

* [ ] All high-frequency query fields have corresponding indexes
* [ ] Index types match query patterns
* [ ] Tokenizer selection fits data characteristics
* [ ] Vector index parameter configuration is reasonable
* [ ] Index storage space is within acceptable range

**Functional Troubleshooting**:

* [ ] Is the query condition order optimized
* [ ] Are there full table scans
* [ ] Is index selectivity sufficiently high
* [ ] Is data skew affecting queries
* [ ] Are system resources adequate

***

## 7. Advanced Application Scenarios

### 7.1 Enterprise Knowledge Base System

**Architecture Design**:

<= ?                    -- Permission control
AND d.department IN (?, ?, ?)               -- Department filtering
AND d.content LIKE ?                        -- Keyword matching
AND d.status = 'published'                  -- Status filtering
ORDER BY relevance ASC, d.view_count DESC
LIMIT 20;
```

### 7.2 Real-Time Recommendation Engine

**User Profile Matching**:

```sql
-- Personalized recommendation based on vector similarity
WITH user_profile AS (
    SELECT embedding FROM user_vectors WHERE user_id = ?
)
SELECT p.product_id, p.title, 
       COSINE_DISTANCE(p.embedding, u.embedding) as match_score
FROM products p, user_profile u
WHERE p.category_id IN (?)                   -- Interest category
AND p.price_range = ?                       -- Price range
AND p.rating >
```

### 7.2 Intelligent Customer Service System

**Question Similarity Matching**:

```sql
-- FAQ intelligent matching
WITH question_vector AS (
    SELECT get_text_embedding(?) as qv
)
SELECT f.faq_id, f.question, f.answer,
       COSINE_DISTANCE(f.question_embedding, q.qv) as similarity
FROM faq_database f, question_vector q
WHERE f.category = ?                         -- Question category
AND f.status = 'active'                     -- Active status
AND similarity < 0.3                        -- Similarity threshold
ORDER BY similarity ASC
LIMIT 5;
```

***

## 8. Summary and Recommendations

### 8.1 Core Best Practices

1. **Layered Design**: Bloom Filter -> Inverted Index -> Vector Index, combine in descending efficiency order
2. **Precise Selection**: Choose the most suitable index type and parameters based on query patterns
3. **Progressive Optimization**: Start with basic indexes, gradually introduce advanced features as business develops
4. **Continuous Monitoring**: Establish a comprehensive monitoring system to promptly discover and resolve issues

### 8.2 Implementation Path

**Phase 1: Basic Indexing**

* Bloom Filter: Enable fast ID lookups
* keyword Inverted Index: Support exact category matching

**Phase 2: Intelligent Search**

* chinese/unicode Inverted Index: Intelligent text retrieval
* Multi-index combination: Improve query accuracy

**Phase 3: AI Empowerment**

* Vector Index: Semantic search capability
* Fused Retrieval: Traditional indexing + AI technology

***

## Appendix

### A. Reference Command Quick Reference

```sql
-- Create indexes
CREATE BLOOMFILTER INDEX idx_name ON TABLE table_name(column);
CREATE INVERTED INDEX idx_name ON TABLE table_name(column) PROPERTIES('analyzer'='chinese');
CREATE VECTOR INDEX idx_name ON TABLE table_name(column) PROPERTIES(...);

-- Manage indexes
BUILD INDEX idx_name ON table_name;
DROP INDEX idx_name;
SHOW INDEX FROM table_name;

-- Query optimization
TOKENIZE('text', map('analyzer', 'chinese'));
COSINE_DISTANCE(vector1, vector2);
ARRAY_REPEAT(value, count);

-- Table management
DESC TABLE EXTENDED table_name;
SHOW CREATE TABLE table_name;
SELECT COUNT(*) FROM table_name;
```

### B. Complete Verification Checklist

**Environment Preparation Verification**:

* [ ] Table created successfully: `DESC TABLE ai_knowledge_base`
* [ ] Indexes created completely: Check that the returned index field contains all indexes
* [ ] Data inserted successfully: `SELECT COUNT(*) FROM ai_knowledge_base` returns 8
* [ ] Vector data correct: `SELECT doc_id, ARRAY_SIZE(embedding) FROM ai_knowledge_base LIMIT 1` returns 768

**Functional Verification Tests**:

* [ ] Bloom Filter: `WHERE author_id = 2001` responds quickly
* [ ] keyword Index: `WHERE category = 'Technical Documentation'` exact match
* [ ] chinese Index: `WHERE content LIKE '%platform%'` Chinese search
* [ ] Vector Index: COSINE\_DISTANCE query executes normally
* [ ] Tokenization: TOKENIZE function returns correct results
* [ ] BUILD INDEX: Returns OPERATION SUCCEED

### C. Contact Information for Issues

When encountering technical issues, please provide the following information:

* Table structure and index definitions
* Query statements and execution plans
* Error messages and logs
* Data volume scale

***

## D. Environment Cleanup Guide

After completing the demo and learning, follow these steps to clean up created resources:

### Clean Up Demo Environment

```sql
-- 1. Clean up the main demo table (including all indexes)
DROP TABLE IF EXISTS ai_knowledge_base;

-- 2. Clean up potentially created test tables
DROP TABLE IF EXISTS production_table;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS vectors;
DROP TABLE IF EXISTS enterprise_docs;

-- 3. Verify cleanup results
SHOW TABLES LIKE '%knowledge%';
SHOW TABLES LIKE '%production%';
```

### Batch Cleanup Script

```sql
-- Safe cleanup script (with confirmation)
-- View all tables in the current schema
SHOW TABLES;

-- Clean up tables with specific prefixes
DROP TABLE IF EXISTS ai_knowledge_base;
DROP TABLE IF EXISTS test_table_1;
DROP TABLE IF EXISTS demo_table_2;
-- Adjust based on actual table names created

-- Clean up temporary schemas (if a dedicated test schema was created)
-- DROP SCHEMA IF EXISTS index_demo;
```

### Cleanup Notes

**Important Reminders**:

* Dropping a table will also delete all indexes on that table
* Always confirm before executing cleanup operations in production environments
* It is recommended to back up important data before executing cleanup
* If custom schemas were used, you can choose to keep or delete them


^

\*\*Reference Documents\*\*:

\- \[Create Vector Index]\(create-vector-index.md)

\- \[Create Inverted Index]\(create-inverted-index.md)&#x20;

\- \[Create Bloom Filter Index]\(create-bloomfilter-index.md)

\- \[Build Index]\(build-index.md)

\- \[Show Index]\(show-index.md)
