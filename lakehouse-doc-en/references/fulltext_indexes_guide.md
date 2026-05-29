# Lakehouse Full-Text Search Usage Guide

***

## Foreword

### Text Retrieval Scenarios You May Encounter

#### Scenario 1: Enterprise Knowledge Base Search System

**Common approaches in Hive/Spark**:

```sql
-- Text search in Hive
SELECT * FROM knowledge_base 
WHERE content LIKE '%Artificial Intelligence%' 
   OR content LIKE '%Machine Learning%' 
   OR content LIKE '%Deep Learning%';

-- Performance issues:
-- 1. Full table scan, cannot use indexes
-- 2. Only exact matching, no semantic search
-- 3. Chinese word segmentation difficulty, poor search results
```

**Technical challenges faced**:

* **Performance limitations**: LIKE queries require full table scans, extremely poor performance with large data volumes
* **Functional limitations**: No word segmentation search, only exact string matching
* **Maintenance complexity**: Manual management of search keywords and synonyms required
* **Scalability difficulties**: Multi-language support requires additional development

#### Scenario 2: Log Analysis and Troubleshooting

**Typical implementation in Elasticsearch**:

```javascript
// Elasticsearch query
{
  "query": {
    "multi_match": {
      "query": "ERROR timeout connection",
      "fields": ["message", "stack_trace"]
    }
  }
}
```

**Common technical pain points**:

* **Architecture complexity**: Requires maintaining a separate search engine system
* **Data synchronization**: Data needs to be synced from the data lake to the search engine
* **Cost issues**: Additional storage and compute resource consumption
* **Consistency risk**: Data sync delay leads to inaccurate search results

### Why Native Full-Text Search Is Needed

Based on the technical challenges from the above scenarios, the design goals of Lakehouse native full-text search are:

**Unified data processing platform**:

* Perform analytical computation and full-text search in the same system
* No need to maintain a separate search engine system
* Strong consistency between data storage and retrieval

**High-performance inverted index**:

* Fast text retrieval based on inverted indexes
* Support for multiple tokenization strategies and languages
* Performance improvement of tens of times over traditional LIKE queries

**Intelligent tokenization and matching**:

* Support for Chinese, English, Unicode, and other tokenizers
* Multiple matching modes including phrase matching, prefix matching, and regex matching
* Automatic case conversion and punctuation filtering

### How to Use This Guide

| Reader Role | Suggested Reading Focus | Expected Takeaway |
| ----- | ------------------ | -------------- |
| Data Engineer | Index creation -> Function usage -> Performance optimization | Master the correct usage of inverted indexes |
| System Architect | Application scenarios -> Architecture comparison -> Migration strategy | Obtain guidance for migrating from traditional search engines |
| Application Developer | Quick start -> Query patterns -> Pitfall avoidance guide | Understand best practices for full-text search |

***

## Quick Start

### Basic Usage Flow

```sql
-- 1. Create a table with an inverted index
CREATE TABLE documents (
    id BIGINT,
    title STRING,
    content STRING,
    created_at TIMESTAMP,
    
    -- Define inverted index at table creation
    INDEX title_idx (title) INVERTED PROPERTIES('analyzer'='keyword'),
    INDEX content_idx (content) INVERTED PROPERTIES('analyzer'='chinese', 'mode'='smart')
);

-- 2. Insert data
INSERT INTO documents VALUES 
(1, 'Singdata Technical Guide', 'Singdata Lakehouse supports vector search and full-text search features', CURRENT_TIMESTAMP());

-- 3. Build index for existing data
BUILD INDEX content_idx ON documents;

-- 4. Execute full-text search query
SELECT id, title FROM documents 
WHERE MATCH_ANY(content, 'full-text search vector search', map('analyzer', 'auto'));

-- 5. Use phrase matching
SELECT id, title FROM documents 
WHERE MATCH_PHRASE(content, 'full-text search features', map('analyzer', 'auto'));
```

***

## Technical Comparison: Traditional Approach vs Native Full-Text Search

### Traditional LIKE Query Approach

```sql
-- Text search using LIKE
SELECT * FROM documents 
WHERE content LIKE '%Artificial Intelligence%' 
   OR content LIKE '%Machine Learning%'
   OR content LIKE '%Deep Learning%';

-- Existing problems:
-- 1. Full table scan, poor performance
-- 2. No word segmentation, only exact matching
-- 3. Case sensitive
-- 4. Cannot handle synonyms
```

### External Search Engine Approach

```yaml
```

Requires maintaining an additional Elasticsearch cluster:

```yaml
version: '3'
services:
  elasticsearch:
    image: elasticsearch:7.14.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
```

```python
```

Data sync script needed:

```python
from elasticsearch import Elasticsearch

def sync_data_to_es():
    # Read data from data lake
    # Convert format
    # Sync to Elasticsearch
    pass
```

### Lakehouse Native Full-Text Search

```sql
-- One-stop solution
CREATE TABLE documents (
    id BIGINT,
    content STRING,
    INDEX content_idx (content) INVERTED PROPERTIES('analyzer'='chinese')
);

-- Use built-in functions directly
SELECT * FROM documents 
WHERE MATCH_ALL(content, 'Artificial Intelligence Machine Learning', map('analyzer', 'auto'));
```

### Solution Comparison Summary

| Feature | LIKE Query | External Search Engine | Lakehouse Full-Text Search | Advantage |
| ----- | -------- | ------ | ------------- | ------------- |
| Performance | Very poor (full table scan) | Excellent | Excellent (inverted index) | High performance without external systems |
| Architecture complexity | Simple | Complex | Simple | Unified platform, reduced ops cost |
| Data consistency | Strong | Eventual | Strong | Avoids data sync delay |
| Development cost | Low | High | Medium | Reduced integration work |
| Tokenization support | None | Rich | Rich | Native multi-language tokenization |
| Maintenance cost | Low | High | Low | No need to maintain a separate search cluster |

***

## Inverted Index Core Concepts

### Inverted Index Principles

**Basic concepts**:

* **Dictionary**: Stores the list of unique words that appear across all documents
* **Posting List**: Records which documents each word appears in and position information

**Build process**:

1. **Tokenization**: Split document content into words or phrases
2. **Normalization**: Lowercase conversion, stop word removal, and other processing
3. **Build dictionary**: Assign a unique ID to each word
4. **Build posting list**: Record the mapping between words and documents

### Index Creation Syntax

#### Define Index at Table Creation

```sql
CREATE TABLE table_name (
    column_definitions,
    INDEX index_name (column_name) INVERTED 
    [COMMENT 'description'] 
    PROPERTIES(
        'analyzer'='english|chinese|keyword|unicode',
        'mode'='smart|max_word'  -- Only supported for Chinese tokenizer
    )
);
```

#### Add Index to Existing Table

```sql
CREATE INVERTED INDEX [IF NOT EXISTS] index_name 
ON TABLE [schema.]table_name(column_name)
[COMMENT 'description'] 
PROPERTIES(
    'analyzer'='english|chinese|keyword|unicode',
    'mode'='smart|max_word'
);
```

### Supported Data Types

| Data Type Category | Specific Types | PROPERTIES Required | Description |
| ------ | --------------------------------------------- | -------------- | ----------- |
| Numeric types | TINYINT, SMALLINT, INT, BIGINT, FLOAT, DOUBLE | No | Used to accelerate equality and range queries |
| Date types | DATE, TIMESTAMP | No | Used to accelerate time range queries |
| String types | STRING, VARCHAR, CHAR | Yes | Must specify tokenizer |

***

## Tokenizer Details

### Tokenizer Type Comparison

#### keyword Tokenizer

```sql
SELECT TOKENIZE('Singdata Lakehouse Technical Guide', map('analyzer', 'keyword'));
-- Result: ["Singdata Lakehouse Technical Guide"]
```

* **Characteristics**: No tokenization, preserves complete string
* **Applicable scenarios**: Exact matching, ID fields, status fields
* **Performance**: Best, direct string matching

#### english Tokenizer

```sql
SELECT TOKENIZE('Singdata Lakehouse Technical Guide', map('analyzer', 'english'));
-- Result: ["singdata", "lakehouse", "technical", "guide"]
```

* **Characteristics**: Identifies ASCII alphanumeric characters, lowercases, filters punctuation
* **Applicable scenarios**: Pure English content
* **Performance**: Excellent, optimized for English

#### chinese Tokenizer

```sql
SELECT TOKENIZE('Singdata Lakehouse Technical Guide', map('analyzer', 'chinese'));
-- Result: ["singdata", "lakehouse", "technical", "guide"]
```

* **Characteristics**: Supports mixed Chinese and English, intelligent tokenization
* **Applicable scenarios**: Chinese documents, mixed Chinese-English content
* **Tokenization modes**:
  * `smart`: Intelligent tokenization, coarse granularity, high accuracy
  * `max_word`: Maximum tokenization, fine granularity, high recall

#### unicode Tokenizer

```sql
SELECT TOKENIZE('Singdata Lakehouse Technical Guide', map('analyzer', 'unicode'));
-- Result: ["singdata", "lakehouse", "technical", "guide"]
```

* **Characteristics**: Supports all Unicode characters
* **Applicable scenarios**: Multi-language mixed content
* **Performance**: Relatively slower, but broadest support range

### Tokenization Mode Details

Only the Chinese tokenizer supports tokenization modes:

```sql
-- smart mode: Intelligent tokenization
SELECT TOKENIZE('Natural Language Processing Technology', map('analyzer', 'chinese', 'mode', 'smart'));
-- Result: ["Natural Language", "Processing", "Technology"]

-- max_word mode: Maximum tokenization
SELECT TOKENIZE('Natural Language Processing Technology', map('analyzer', 'chinese', 'mode', 'max_word'));
-- Result: ["Natural", "Language", "Natural Language", "Processing", "Technology"]
```

**Selection guidance**:

* **Short text matching**: Use `smart` mode for higher accuracy
* **Full-text search**: Use `max_word` mode for higher recall

***

## Full-Text Search Functions

### Function Overview

| Function Name | Purpose | Return Type | Applicable Scenario |
| --------------------- | ------- | ------- | ------ |
| TOKENIZE | Tokenization test | ARRAY | Verify tokenization results |
| MATCH_ALL | Match all keywords | BOOLEAN | Exact search |
| MATCH_ANY | Match any keyword | BOOLEAN | Broad search |
| MATCH_PHRASE | Phrase matching | BOOLEAN | Order-sensitive search |
| MATCH_PHRASE_PREFIX | Phrase prefix matching | BOOLEAN | Autocomplete |
| MATCH_REGEXP | Regex matching | BOOLEAN | Pattern matching |

### TOKENIZE - Tokenization Test Function

```sql
TOKENIZE(input, option)
```

**Purpose**: Tokenize text using the specified tokenizer, used to verify tokenization results

**Parameters**:

* `input`: Text to tokenize
* `option`: Tokenization options, e.g., `map('analyzer', 'chinese')`

**Usage example**:

```sql
-- Test different tokenizer effects
SELECT 
    'keyword' as analyzer,
    TOKENIZE('Machine Learning Algorithm', map('analyzer', 'keyword')) as tokens
UNION ALL
SELECT 
    'chinese',
    TOKENIZE('Machine Learning Algorithm', map('analyzer', 'chinese'))
UNION ALL
SELECT 
    'unicode',
    TOKENIZE('Machine Learning Algorithm', map('analyzer', 'unicode'));
```

### MATCH_ALL - Match All Function

```sql
MATCH_ALL(column, query, option)
```

**Purpose**: Requires documents to contain all tokenized results from the query text

**Logic**: AND relationship, all words must be present

**Usage example**:

```sql
-- Find documents containing both "Machine Learning" and "Algorithm"
SELECT id, title FROM documents 
WHERE MATCH_ALL(content, 'Machine Learning Algorithm', map('analyzer', 'auto'));
```

### MATCH_ANY - Match Any Function

```sql
MATCH_ANY(column, query, option)
```

**Purpose**: Documents need only contain any single token from the query text

**Logic**: OR relationship, any word present is sufficient

**Usage example**:

```sql
-- Find documents containing "AI" or "Machine Learning" or "Deep Learning"
SELECT id, title FROM documents 
WHERE MATCH_ANY(content, 'AI Machine Learning Deep Learning', map('analyzer', 'auto'));
```

### MATCH_PHRASE - Phrase Matching Function

```sql
MATCH_PHRASE(column, query, option)
```

**Purpose**: Requires documents to contain the query phrase, with word order consistent and continuous

**Characteristics**:

* Order-sensitive
* Requires consecutive occurrence
* Case-insensitive

**Usage example**:

```sql
-- Find documents containing the phrase "Natural Language Processing"
SELECT id, title FROM documents 
WHERE MATCH_PHRASE(content, 'Natural Language Processing', map('analyzer', 'auto'));

-- Counterexample: will not match "Natural Language Processing" (not consecutive)
-- Counterexample: will not match "Language Natural Processing" (wrong order)
```

### MATCH_PHRASE_PREFIX - Phrase Prefix Matching

```sql
MATCH_PHRASE_PREFIX(column, query, option)
```

**Purpose**: First n-1 words matched as phrase, last word matched as prefix

**Applicable scenarios**: Search suggestions, autocomplete

**Usage example**:

```sql
-- Find phrases starting with "Data An" (e.g., "Data Analysis", "Data Annotation")
SELECT id, title FROM documents 
WHERE MATCH_PHRASE_PREFIX(content, 'Data An', map('analyzer', 'auto'));
```

### MATCH_REGEXP - Regex Matching Function

```sql
MATCH_REGEXP(column, query, option)
```

**Purpose**: Perform regex matching on tokenization results

**Usage example**:

```sql
-- Find documents containing words ending with "ing"
SELECT id, title FROM documents 
WHERE MATCH_REGEXP(content, '.*ing', map('analyzer', 'auto'));

-- Find documents containing digits
SELECT id, title FROM documents 
WHERE MATCH_REGEXP(content, '.*[0-9].*', map('analyzer', 'auto'));
```

### Important Parameter Notes

#### analyzer Option

**Recommended `auto` parameter**:

```sql
map('analyzer', 'auto')  -- Automatically matches the column's tokenizer settings
```

**Manually specifying tokenizer**:

```sql
map('analyzer', 'chinese')
map('analyzer', 'chinese', 'mode', 'smart')
```

> ⚠️ **Note**: The tokenizer in the function must match the tokenizer used when creating the index; otherwise, the index cannot be leveraged for acceleration!

***

## Index Management

### Index Lifecycle

#### 1. Create Index

```sql
-- Method 1: Create at table creation
CREATE TABLE documents (
    id BIGINT,
    content STRING,
    INDEX content_idx (content) INVERTED PROPERTIES('analyzer'='chinese')
);

-- Method 2: Create for existing table
CREATE INVERTED INDEX content_idx ON TABLE documents(content) 
PROPERTIES('analyzer'='chinese', 'mode'='smart');
```

#### 2. Build Index (Important!)

```sql
-- Build index for existing data (synchronous task)
BUILD INDEX content_idx ON documents;

-- Build index by partition
BUILD INDEX content_idx ON documents 
WHERE partition_date >= '2024-01-01';
```

> ⚠️ **Note**:

* `CREATE INDEX` only takes effect for new data
* Existing data requires `BUILD INDEX` to leverage the index
* Building an index consumes compute resources; it is recommended to perform during off-peak hours

#### 3. View Index

```sql
-- List all indexes on a table
SHOW INDEX FROM table_name;

-- View index details (if supported by the environment)
DESC INDEX index_name;
DESC INDEX EXTENDED index_name;  -- Includes size information
```

#### 4. Drop Index

```sql
DROP INDEX index_name ON table_name;
```

**Drop characteristics**:

* Metadata deleted immediately
* Index files cleaned up asynchronously
* Does not affect the data itself

### Index Performance Tuning

#### Partitioned Table Index Strategy

```sql
-- Recommended approach for large table partition building
BUILD INDEX content_idx ON large_table 
WHERE year = '2024' AND month = '01';

BUILD INDEX content_idx ON large_table 
WHERE year = '2024' AND month = '02';
-- Build partition by partition to avoid excessive resource consumption
```

#### Storage Cost Optimization

```sql
-- View index storage occupancy (if supported)
DESC INDEX EXTENDED index_name;

-- Choose appropriate tokenizer based on business needs
-- keyword: Least storage, exact match only
-- chinese: Medium storage, supports intelligent tokenization
-- unicode: Most storage, supports all languages
```

***

## Application Scenario Design

### Enterprise Knowledge Base System

```sql
-- Knowledge base table design
CREATE TABLE knowledge_base (
    doc_id BIGINT PRIMARY KEY,
    title STRING,
    content STRING,
    category STRING,
    tags STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    
    -- Multi-level index design
    INDEX title_keyword_idx (title) INVERTED PROPERTIES('analyzer'='keyword'),
    INDEX content_chinese_idx (content) INVERTED PROPERTIES('analyzer'='chinese', 'mode'='smart'),
    INDEX tags_unicode_idx (tags) INVERTED PROPERTIES('analyzer'='unicode')
);

-- Multi-dimensional search query
SELECT doc_id, title FROM knowledge_base 
WHERE MATCH_ANY(content, 'AI Machine Learning', map('analyzer', 'auto'))
   OR MATCH_ANY(tags, 'AI ML', map('analyzer', 'auto'))
ORDER BY updated_at DESC LIMIT 20;
```

### Log Analysis System

```sql
-- Application log table
CREATE TABLE application_logs (
    log_id BIGINT,
    timestamp TIMESTAMP,
    level STRING,
    message STRING,
    stack_trace STRING,
    source_ip STRING,
    
    INDEX message_idx (message) INVERTED PROPERTIES('analyzer'='english'),
    INDEX stack_trace_idx (stack_trace) INVERTED PROPERTIES('analyzer'='keyword')
) PARTITIONED BY (DATE(timestamp));

-- Troubleshooting query
SELECT log_id, timestamp, message FROM application_logs 
WHERE DATE(timestamp) >= CURRENT_DATE() - INTERVAL '7' DAY
  AND level = 'ERROR'
  AND MATCH_ANY(message, 'timeout connection database', map('analyzer', 'auto'))
ORDER BY timestamp DESC;
```

### E-Commerce Product Search

```sql
-- Product information table
CREATE TABLE products (
    product_id BIGINT,
    name STRING,
    description STRING,
    brand STRING,
    category STRING,
    tags STRING,
    price DECIMAL(10,2),
    
    INDEX name_chinese_idx (name) INVERTED PROPERTIES('analyzer'='chinese', 'mode'='max_word'),
    INDEX desc_chinese_idx (description) INVERTED PROPERTIES('analyzer'='chinese', 'mode'='max_word'),
    INDEX brand_keyword_idx (brand) INVERTED PROPERTIES('analyzer'='keyword')
);

-- Product search query
SELECT product_id, name, price FROM products 
WHERE MATCH_ANY(name, 'phone smart camera', map('analyzer', 'auto'))
   OR MATCH_ANY(description, 'phone smart camera', map('analyzer', 'auto'))
ORDER BY price;
```

### Content Management System

```sql
-- Article content table
CREATE TABLE articles (
    article_id BIGINT,
    title STRING,
    content STRING,
    author STRING,
    publish_date DATE,
    status STRING,
    
    INDEX title_chinese_idx (title) INVERTED PROPERTIES('analyzer'='chinese'),
    INDEX content_chinese_idx (content) INVERTED PROPERTIES('analyzer'='chinese', 'mode'='smart'),
    INDEX author_keyword_idx (author) INVERTED PROPERTIES('analyzer'='keyword')
);

-- Content search
SELECT article_id, title, author FROM articles 
WHERE status = 'published'
  AND publish_date >= CURRENT_DATE() - INTERVAL '30' DAY
  AND MATCH_PHRASE(content, 'technology development trends', map('analyzer', 'auto'))
ORDER BY publish_date DESC;
```

***

## Important Pitfall Avoidance Guide

### Tokenizer Consistency Issue

#### Common Error: Tokenizer Mismatch

```sql
-- ❌ Error example: Index uses chinese tokenizer, query uses english tokenizer
CREATE TABLE docs (
    content STRING,
    INDEX content_idx (content) INVERTED PROPERTIES('analyzer'='chinese')
);

SELECT * FROM docs 
WHERE MATCH_ANY(content, 'test', map('analyzer', 'english'));
-- Result: Cannot leverage index, poor performance
```

#### Correct Approach:

```sql
-- ✅ Solution 1: Use auto parameter (recommended)
SELECT * FROM docs 
WHERE MATCH_ANY(content, 'test', map('analyzer', 'auto'));

-- ✅ Solution 2: Manually match the index tokenizer
SELECT * FROM docs 
WHERE MATCH_ANY(content, 'test', map('analyzer', 'chinese'));
```

### Index Build Pitfalls

#### The Necessity of BUILD INDEX

```sql
-- ❌ Common error: Forgetting to build index
CREATE INVERTED INDEX content_idx ON TABLE existing_table(content) 
PROPERTIES('analyzer'='chinese');

-- Query directly (only effective for new data, existing data cannot leverage index)
SELECT * FROM existing_table 
WHERE MATCH_ANY(content, 'keyword', map('analyzer', 'auto'));
```

#### Correct Index Build Process

```sql
-- ✅ Complete process
-- 1. Create index
CREATE INVERTED INDEX content_idx ON TABLE existing_table(content) 
PROPERTIES('analyzer'='chinese');

-- 2. Build index (required!)
BUILD INDEX content_idx ON existing_table;

-- 3. Verify index
SHOW INDEX FROM existing_table;

-- 4. Execute query
SELECT * FROM existing_table 
WHERE MATCH_ANY(content, 'keyword', map('analyzer', 'auto'));
```

### Query Performance Pitfalls

#### Performance Limitations for Sub-Second Queries

According to the official documentation: **In most cases, inverted indexes do not significantly improve performance for queries with sub-second execution times**.

```sql
-- ❌ Not ideal for inverted index scenarios
-- 1. Small tables (fewer than hundreds of rows)
-- 2. Queries already executing in <1 second
-- 3. Simple equality queries

-- ✅ Suitable for inverted index scenarios
-- 1. Large data tables (10,000+ rows)
-- 2. Complex text searches
-- 3. Multi-keyword matching
```

#### Unsupported Query Patterns

```sql
-- ❌ Not supported: Type conversion on the column
SELECT * FROM docs 
WHERE MATCH_ANY(CAST(id AS STRING), '123', map('analyzer', 'auto'));

-- ✅ Supported: Type conversion on the query value
SELECT * FROM docs 
WHERE MATCH_ANY(content, CAST(123 AS STRING), map('analyzer', 'auto'));

-- ❌ Not supported: External tables
-- Inverted indexes do not support external tables
```

### Storage Cost Pitfalls

#### Index Storage Overhead

```sql
-- Inverted indexes create additional index files
-- Storage cost = Original data + Index files

-- Optimization suggestions:
-- 1. Only create indexes for columns that truly need searching
-- 2. Choose appropriate tokenizer based on query patterns
-- 3. Regularly clean up unnecessary indexes
```

#### Tokenizer Selection Strategy

| Tokenizer | Index Size | Query Performance | Feature Richness | Recommended Scenario |
| ------- | ---- | ---- | ----- | -------- |
| keyword | Smallest | Fastest | Exact match | IDs, statuses, tags |
| english | Small | Fast | English tokenization | Pure English content |
| chinese | Medium | Medium | Chinese tokenization | Chinese documents |
| unicode | Largest | Relatively slow | Full language support | Multi-language mixed |

***

## Performance Optimization

### Query Optimization Strategies

#### 1. Choose Query Functions Wisely

```sql
-- Choose appropriate functions based on business needs
-- Exact search: Use MATCH_ALL
SELECT * FROM docs WHERE MATCH_ALL(content, 'Machine Learning Algorithm', map('analyzer', 'auto'));

-- Broad search: Use MATCH_ANY  
SELECT * FROM docs WHERE MATCH_ANY(content, 'AI Machine Learning Deep Learning', map('analyzer', 'auto'));

-- Phrase search: Use MATCH_PHRASE
SELECT * FROM docs WHERE MATCH_PHRASE(content, 'Natural Language Processing', map('analyzer', 'auto'));
```

#### 2. Combined Query Optimization

```sql
-- ✅ Recommended: Use full-text search as the primary filter condition
SELECT * FROM documents 
WHERE MATCH_ANY(content, 'keyword', map('analyzer', 'auto'))
  AND category = 'tech'  -- Secondary filtering on top of full-text search
  AND created_at >= '2024-01-01';
```

#### 3. Paginated Query Optimization

```sql
-- ✅ Efficient paginated query
SELECT id, title FROM documents 
WHERE MATCH_ANY(content, 'keyword', map('analyzer', 'auto'))
ORDER BY id  -- Sort by primary key
LIMIT 20 OFFSET 0;

-- -- Avoid deep pagination
-- -- LIMIT 20 OFFSET 10000; -- Performance degrades as offset increases
```

### Index Optimization Strategies

#### 1. Partitioned Table Index Management

```sql
-- Build index gradually by partition
BUILD INDEX content_idx ON large_table 
WHERE year = '2024' AND month = '06';

-- Monitor build progress
-- Job Profile can be used to view progress
```

#### 2. Index Maintenance Strategy

```sql
-- Regularly check index status
SHOW INDEX FROM table_name;

-- For frequently updated tables, index rebuild may be needed
DROP INDEX old_idx ON table_name;
CREATE INVERTED INDEX new_idx ON TABLE table_name(column) 
PROPERTIES('analyzer'='chinese');
BUILD INDEX new_idx ON table_name;
```

### System Resource Optimization

#### 1. Compute Resource Configuration

* **Index building**: Use larger Virtual Clusters for BUILD INDEX operations
* **Query execution**: Use smaller Virtual Clusters for daily queries
* **Mixed workloads**: Separate index building and query workloads

#### 2. Storage Resource Optimization

```sql
-- Monitor index storage occupancy (if supported)
DESC INDEX EXTENDED index_name;

-- Clean up unnecessary indexes
DROP INDEX unused_idx ON table_name;
```

***

## Migration Strategy

### Migrating from Traditional LIKE Queries

#### Migration Assessment

**Scenarios suitable for migration**:

* Frequent text search queries
* Large data tables (10,000+ rows)
* Complex multi-keyword searches
* Scenarios requiring Chinese tokenization

**Scenarios not in a hurry to migrate**:

* Small data tables
* Occasional text queries
* Simple queries already fast (<1 second)

#### Migration Steps

```sql
-- 1. Analyze existing query patterns
-- Identify frequent LIKE queries
SELECT query_text, execution_count 
FROM query_logs 
WHERE query_text LIKE '%LIKE%'
ORDER BY execution_count DESC;

-- 2. Create test table to verify effects
CREATE TABLE docs_test AS SELECT * FROM docs_original LIMIT 1000;

-- 3. Add inverted index
CREATE INVERTED INDEX content_idx ON TABLE docs_test(content) 
PROPERTIES('analyzer'='chinese');

BUILD INDEX content_idx ON docs_test;

-- 4. Performance comparison test
-- Original LIKE query
SELECT COUNT(*) FROM docs_test WHERE content LIKE '%keyword%';

-- Full-text search query
SELECT COUNT(*) FROM docs_test 
WHERE MATCH_ANY(content, 'keyword', map('analyzer', 'auto'));

-- 5. Gradually migrate to production environment
```

### Migrating from External Search Engines

#### Elasticsearch Migration Mapping

| Elasticsearch Query | Lakehouse Full-Text Search | Description |
| --------------------- | --------------------- | ------- |
| `match_all` | `MATCH_ALL` | Match all keywords |
| `match` | `MATCH_ANY` | Match any keyword |
| `match_phrase` | `MATCH_PHRASE` | Phrase matching |
| `match_phrase_prefix` | `MATCH_PHRASE_PREFIX` | Phrase prefix matching |
| `regexp` | `MATCH_REGEXP` | Regex matching |

#### Migration Benefits Assessment

**Architecture simplification benefits**:

* Eliminate 1 separate search engine system
* Unified data storage and retrieval platform
* Reduced operational complexity

**Cost optimization benefits**:

* Reduced additional storage and compute resources
* No data sync ETL processes needed
* Lower total cost of ownership

**Data consistency benefits**:

* Strong consistency guarantees
* No data sync delays
* Real-time search of latest data

### Hybrid Solution Design

For complex enterprise environments, a hybrid approach can be adopted:

```sql
-- Approach 1: Separate by data type
-- Structured queries + Simple text search: Use Lakehouse full-text search
-- Complex semantic search + Recommendation algorithms: Keep Elasticsearch

-- Approach 2: Separate by real-time requirements  
-- Real-time search: Use Lakehouse full-text search
-- Offline analysis: Use Elasticsearch

-- Approach 3: Separate by data volume
-- Large data volumes: Use Lakehouse full-text search
-- Small volume rapid prototyping: Use Elasticsearch
```

***

## Best Practices Summary

### Index Design Best Practices

#### 1. Tokenizer Selection Principles

```sql
-- Choose tokenizer based on data characteristics
CREATE TABLE multilingual_docs (
    id BIGINT,
    title_cn STRING,      -- Chinese title
    title_en STRING,      -- English title  
    content STRING,       -- Mixed content
    tags STRING,          -- Tags (exact match)
    
    INDEX title_cn_idx (title_cn) INVERTED PROPERTIES('analyzer'='chinese', 'mode'='smart'),
    INDEX title_en_idx (title_en) INVERTED PROPERTIES('analyzer'='english'),
    INDEX content_idx (content) INVERTED PROPERTIES('analyzer'='unicode'),
    INDEX tags_idx (tags) INVERTED PROPERTIES('analyzer'='keyword')
);
```

#### 2. Index Maintenance Strategy

```sql
-- Production environment index maintenance process
-- 1. Create index during off-peak hours
CREATE INVERTED INDEX content_idx ON TABLE large_table(content) 
PROPERTIES('analyzer'='chinese');

-- 2. Build index in batches
BUILD INDEX content_idx ON large_table 
WHERE partition_date = '2024-06-01';

-- 3. Verify index effectiveness
SELECT COUNT(*) FROM large_table 
WHERE MATCH_ANY(content, 'test keyword', map('analyzer', 'auto'));

-- 4. Monitor index status
SHOW INDEX FROM large_table;
```

### Query Pattern Best Practices

#### 1. Query Function Selection Guide

| Business Scenario | Recommended Function | Example Query |
| --------- | --------------------- | ------------------ |
| Exact search with multiple keywords | MATCH_ALL | Must contain "AI" and "Machine Learning" |
| Broad topic search | MATCH_ANY | Contains "AI" or "ML" or "Deep Learning" |
| Professional term search | MATCH_PHRASE | Exact match for "Natural Language Processing" |
| Search suggestions / Autocomplete | MATCH_PHRASE_PREFIX | Phrases starting with "Data An" |
| Pattern matching | MATCH_REGEXP | Contains digits or specific formats |

#### 2. Performance-Optimized Query Patterns

```sql
-- Efficient query patterns
-- 1. Leverage partition filtering
SELECT * FROM logs 
WHERE log_date >= '2024-01-01'
  AND MATCH_ANY(message, 'error timeout', map('analyzer', 'auto'));

-- 2. Combine index filtering
SELECT * FROM documents 
WHERE MATCH_ALL(content, 'keyword1 keyword2', map('analyzer', 'auto'))
  AND status = 'active';
```

### Monitoring and Diagnostics

#### 1. Index Effectiveness Verification

```sql
-- Verify if index is being used (via execution plan)
EXPLAIN SELECT * FROM documents 
WHERE MATCH_ANY(content, 'keyword', map('analyzer', 'auto'));

-- Compare LIKE query performance
-- Method: Record query execution time, compare optimization effects
```

#### 2. Common Issue Diagnosis

```sql
-- Check tokenization results
SELECT TOKENIZE('test text', map('analyzer', 'auto'));

-- Check index status
SHOW INDEX FROM table_name;

-- Verify query syntax
SELECT MATCH_ANY('test text', 'keyword', map('analyzer', 'chinese'));
```

***

## Known Limitations and Considerations

### Functional Limitations

#### 1. Unsupported Scenarios

* **External tables**: Inverted indexes do not support external tables
* **Column type conversion**: Forced type conversion on table columns is not supported

#### 2. Query Limitations

```sql
-- ❌ Unsupported query patterns
-- 1. Type conversion on table columns
WHERE MATCH_ANY(CAST(column AS STRING), 'value', map('analyzer', 'auto'))

-- 2. Creating inverted index on external table
CREATE INVERTED INDEX idx ON EXTERNAL_TABLE table_name(column) 
PROPERTIES('analyzer'='chinese');
```

### Performance Considerations

#### 1. Index Build Cost

* BUILD INDEX is a synchronous operation that consumes compute resources
* Large tables are recommended to be built partition by partition
* Recommended to perform during off-peak hours

#### 2. Storage Cost

* Inverted indexes create additional index files
* Index size depends on data volume and tokenizer type
* Need to balance query performance and storage cost

### Operational Considerations

#### 1. Version Compatibility

* Recommend thorough validation in test environments
* Monitor version updates and feature improvements

#### 2. Backup and Recovery

* Index metadata is backed up along with the table structure
* Index files need to be rebuilt
* BUILD INDEX needs to be executed after recovery

## Quick Reference Card

### Tokenizer Selection Quick Reference

```sql
-- Exact matching (IDs, statuses, etc.)
'analyzer'='keyword'

-- Pure English content
'analyzer'='english'

-- Chinese content (recommended)
'analyzer'='chinese', 'mode'='smart'

-- Multi-language mixed
'analyzer'='unicode'

-- Auto matching (recommended)
'analyzer'='auto'
```

### Common Query Templates

```sql
-- 1. Basic text search
SELECT * FROM table_name 
WHERE MATCH_ANY(column, 'keyword', map('analyzer', 'auto'));

-- 2. Exact phrase search
SELECT * FROM table_name 
WHERE MATCH_PHRASE(column, 'exact phrase', map('analyzer', 'auto'));

-- 3. Multi-condition combined search
SELECT * FROM table_name 
WHERE MATCH_ALL(content, 'keyword1 keyword2', map('analyzer', 'auto'))
  AND category = 'target_category';

-- 4. Paginated query
SELECT id, title FROM table_name 
WHERE MATCH_ANY(content, 'keyword', map('analyzer', 'auto'))
ORDER BY id LIMIT 20 OFFSET 0;
```

### Index Management Commands

```sql
-- Create index
CREATE INVERTED INDEX idx_name ON TABLE table_name(column) 
PROPERTIES('analyzer'='chinese');

-- Build index
BUILD INDEX idx_name ON table_name;

-- View index
SHOW INDEX FROM table_name;

-- Drop index
DROP INDEX idx_name ON table_name;
```

***

**Note**: This document is based on Lakehouse product documentation as of June 2025. It is recommended to regularly check the official documentation for the latest updates. Before using in a production environment, be sure to verify the correctness and performance impact of all operations in a test environment.
