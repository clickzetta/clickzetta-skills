# Full-Text Search and Text Analysis Guide

> **Scenario**: Tokenize, keyword-match, regex-search, and phrase-search unstructured text such as logs, articles, and product descriptions.
>
> **Core functions**: `tokenize` (text tokenization), `match_any` (any-word match), `match_phrase` (exact phrase match), `match_phrase_prefix` (prefix phrase match), `match_regexp` (regular expression match).

---

## Quick Reference

| Function | Purpose | Use Case | Index Required |
|---|---|---|---|
| `tokenize` | Tokenize text | Word frequency statistics, tag extraction, text preprocessing | No |
| `match_any` | Any-word match (OR logic) | Broad search, keyword filtering | Yes (inverted index) |
| `match_phrase` | Exact phrase match | Finding fixed phrases, error messages | Yes (inverted index) |
| `match_phrase_prefix` | Prefix phrase match | Search suggestions, autocomplete | Yes (inverted index) |
| `match_regexp` | Regular expression match | Complex pattern extraction, log format parsing | No |

---

## Prerequisites

All examples in this guide use the following test data:

```sql
-- System log and document table
CREATE TABLE search_docs (
  id BIGINT,
  title VARCHAR(500),
  content VARCHAR(1000),
  log_level VARCHAR(20),
  log_message VARCHAR(500)
);

INSERT INTO search_docs VALUES
  (1, 'Singdata Lakehouse Introduction', 'Singdata Lakehouse is a modern data platform that supports real-time analytics and AI applications.', 'INFO', 'System started successfully.'),
  (2, 'Data Pipeline Development', 'Use Dynamic Table to build real-time data pipelines, enabling data flow from ODS to ADS.', 'ERROR', 'Connection timeout to database.'),
  (3, 'User Behavior Analysis', 'Use BITMAP functions to achieve efficient user overlap analysis and precision marketing.', 'WARN', 'High memory usage detected.'),
  (4, 'SQL Function Reference', 'This document covers the various SQL functions supported by Singdata Lakehouse, including aggregate, window, and scalar functions.', 'DEBUG', 'Query execution plan generated.'),
  (5, 'Vector Search Applications', 'Use vector similarity search to implement semantic matching and recommendation systems.', 'INFO', 'Vector index rebuilt.'),
  (6, 'Data Security and Compliance', 'Supports row- and column-level access control, dynamic data masking, and audit logging.', 'ERROR', 'Authentication failed for user admin.'),
  (7, 'Performance Optimization Best Practices', 'Improve performance through small file compaction, result caching, and query rewriting.', 'WARN', 'Disk space running low.'),
  (8, 'Multi-Table Real-Time Sync', 'Use CDC technology to achieve real-time data synchronization from MySQL to Lakehouse.', 'INFO', 'CDC stream processing started.'),
  (9, 'External Data Federation Query', 'Query external data sources such as Hive and Iceberg directly via External Catalog.', 'DEBUG', 'External catalog metadata refreshed.'),
  (10, 'AI Model Integration', 'Call large language models directly in SQL for text generation and sentiment analysis.', 'INFO', 'AI model endpoint connected.');
```

> ⚠️ **Note**: The `match_*` functions **require** an inverted index on the target column to work. Without one, you will get a `cannot infer analyzer` error.
>
> **Recommended approach**: Declare the index directly in the CREATE TABLE DDL so that data is indexed automatically on insert:
> ```sql
> CREATE TABLE search_docs (
>   id BIGINT,
>   content VARCHAR(1000),
>   INDEX idx_content(content) USING INVERTED PROPERTIES('analyzer' = 'chinese')
> );
> ```
>
> If you need to add an index to an existing table, you must trigger a manual build:
> ```sql
> CREATE INVERTED INDEX idx_content ON TABLE search_docs(content) PROPERTIES('analyzer' = 'chinese');
> BUILD INDEX idx_content ON search_docs;  -- build for existing data
> ```

---

## Scenario 1: Text Tokenization and Word Frequency Statistics (tokenize)

### Problem

Tokenize mixed Chinese/English text and count the most frequent terms.

### SQL Implementation

```sql
-- Tokenize using the Chinese analyzer
SELECT 
  id,
  title,
  tokenize(content, map('analyzer', 'chinese')) AS tokens
FROM search_docs
WHERE id IN (1, 2, 3);
```

**Output**:

| id | title | tokens |
|----|-------|--------|
| 1 | Singdata Lakehouse Introduction | singdata:lakehouse:modern:data:platform:real-time:analytics:ai:applications |
| 2 | Data Pipeline Development | dynamic:table:real-time:data:pipeline:ods:ads:data:flow |
| 3 | User Behavior Analysis | bitmap:functions:efficient:user:overlap:analysis:precision:marketing |

### Word Frequency Statistics in Practice

```sql
-- Expand tokenization results and count the top 10 most frequent terms
SELECT token, COUNT(*) AS freq
FROM (
  SELECT tokenize(content, map('analyzer', 'chinese')) AS token_array
  FROM search_docs
),
LATERAL VIEW explode(token_array) t AS token
WHERE LENGTH(token) > 1  -- filter single characters
GROUP BY token
ORDER BY freq DESC
LIMIT 10;
```

**Output**:

| token | freq |
|-------|------|
| data | 4 |
| real-time | 3 |
| analysis | 2 |
| support | 2 |
| ... | ... |

> **Key note**: `tokenize` returns an array type. You need to use `explode` to expand it into multiple rows before aggregating.

---

## Scenario 2: Regular Expression Matching (match_regexp)

### Problem

Extract specific error codes or IP addresses from log messages.

### SQL Implementation

```sql
-- Match logs containing "timeout" or "failed"
SELECT id, log_level, log_message
FROM search_docs
WHERE match_regexp(log_message, '(?i)(timeout|failed)');
```

**Output**:

| id | log_level | log_message |
|----|-----------|-------------|
| 2 | ERROR | Connection timeout to database. |
| 6 | ERROR | Authentication failed for user admin. |

> ⚠️ **Note**: `(?i)` makes the match case-insensitive. `match_regexp` does not require an inverted index and performs regex matching directly on the string.

### Extracting Key Information from Logs

```sql
-- Extract the error type (assuming format: "ERROR: [Type] message")
SELECT 
  id,
  log_message,
  -- Use regexp_extract to capture the content before "failed"
  regexp_extract(log_message, '([A-Za-z]+) failed', 1) AS error_type
FROM search_docs
WHERE match_regexp(log_message, 'failed');
```

---

## Scenario 3: Full-Text Keyword Search (match_any / match_phrase)

> **Prerequisite**: An inverted index must be created on the `content` column.
> ```sql
> CREATE INVERTED INDEX idx_content ON TABLE search_docs(content);
> ```

### `match_any`: Any-Word Match (OR Logic)

```sql
-- Search for documents containing "data", "pipeline", or "real-time"
-- Note: the third parameter must specify the analyzer, matching the index configuration
SELECT id, title, content
FROM search_docs
WHERE match_any(content, 'data pipeline real-time', map('analyzer', 'chinese'));
```

**Use case**: Broad search — a document matches if it contains any one of the keywords.

### `match_phrase`: Exact Phrase Match

```sql
-- Search for documents containing the exact phrase "real-time data"
SELECT id, title, content
FROM search_docs
WHERE match_phrase(content, 'real-time data', map('analyzer', 'chinese'));
```

**Use case**: Finding fixed phrases, error messages, or proper nouns.

### `match_phrase_prefix`: Prefix Phrase Match

```sql
-- Search for phrases starting with "real-time d"
SELECT id, title, content
FROM search_docs
WHERE match_phrase_prefix(content, 'real-time d', map('analyzer', 'chinese'));
```

**Use case**: Search suggestions, autocomplete, fuzzy prefix matching.

---

## Scenario 4: End-to-End Example — Log Analysis and Alerting

### Problem

Quickly locate ERROR-level critical failures from a large volume of logs and analyze the distribution of error types.

### SQL Implementation

```sql
WITH error_logs AS (
  SELECT 
    id,
    log_level,
    log_message,
    tokenize(log_message, map('analyzer', 'standard')) AS tokens
  FROM search_docs
  WHERE log_level = 'ERROR'
)
SELECT 
  id,
  log_message,
  -- Classify error type
  CASE 
    WHEN match_regexp(log_message, '(?i)timeout') THEN 'Connection Timeout'
    WHEN match_regexp(log_message, '(?i)failed') THEN 'Authentication Failed'
    ELSE 'Other'
  END AS error_category,
  -- Extract key entities
  filter(tokens, t -> LENGTH(t) > 3) AS important_words
FROM error_logs;
```

**Output**:

| id | log_message | error_category | important_words |
|----|-------------|----------------|-----------------|
| 2 | Connection timeout to database. | Connection Timeout | connection:timeout:database |
| 6 | Authentication failed for user admin. | Authentication Failed | authentication:failed:user:admin |

---

## Common Issues

### 1. `match_*` functions require an inverted index

```sql
-- Wrong: calling match_any without an index
SELECT * FROM search_docs WHERE match_any(content, 'keyword', map('analyzer', 'chinese'));
-- Error: cannot infer analyzer from arguments

-- Correct: declare the index in the CREATE TABLE DDL (recommended)
CREATE TABLE search_docs (
  id BIGINT,
  content VARCHAR(1000),
  INDEX idx_content(content) USING INVERTED PROPERTIES('analyzer' = 'chinese')
);
-- Data is indexed automatically on insert; queries work immediately

-- Or add an index to an existing table
CREATE INVERTED INDEX idx_content ON TABLE search_docs(content) PROPERTIES('analyzer' = 'chinese');
BUILD INDEX idx_content ON search_docs;  -- manually build for existing data
```

### 2. `match_*` functions require the third parameter

```sql
-- Wrong: missing the analyzer parameter
match_any(content, 'keyword')

-- Correct: specify the analyzer, matching the index configuration
match_any(content, 'keyword', map('analyzer', 'chinese'))
match_any(content, 'keyword', map('analyzer', 'auto'))  -- auto-match index configuration
```

### 3. Choosing the right analyzer for `tokenize`

```sql
-- Chinese text must use the 'chinese' analyzer; otherwise tokenization may be incorrect
tokenize('Singdata Lakehouse', map('analyzer', 'chinese'))  
-- Output: singdata:lakehouse

tokenize('Singdata Lakehouse')  -- default analyzer may only recognize English
-- Output: lakehouse
```

### 4. Regular expression syntax

```sql
-- match_regexp uses Java/PCRE regex syntax
match_regexp(log, '(?i)error')  -- (?i) for case-insensitive matching
match_regexp(log, '\\d{3}')     -- match 3 digits (note the escape)
```

### 5. `tokenize` returns an array type

```sql
-- Wrong: comparing an array directly to a string
SELECT * FROM search_docs WHERE tokenize(content) = 'data';

-- Correct: use explode to expand, or use array_contains
SELECT * FROM search_docs WHERE array_contains(tokenize(content), 'data');
```

---

## Performance Optimization Tips

| Scenario | Optimization Strategy |
|---|---|
| Tokenizing large text | Use `SUBSTR` to truncate to the first 1000 characters before tokenizing |
| High-frequency search terms | Create an inverted index to avoid full table scans |
| Regex matching | Use `LIKE` instead of simple regex where possible for better performance |
| Filtering after tokenization | Apply `WHERE` filtering immediately after `tokenize` to reduce intermediate data |

```sql
-- Recommended: filter after tokenizing
SELECT * FROM (
  SELECT id, tokenize(content, map('analyzer', 'chinese')) AS tokens
  FROM search_docs
) WHERE array_contains(tokens, 'data');

-- Not recommended: full table scan then tokenize
SELECT id, tokenize(content) FROM search_docs WHERE content LIKE '%data%';
```

---

## Related Documentation

* [Inverted Index](index_guide.md)
* [String Processing](SQL_String_Processing_Guide.md)
* [Array Explode and Flatten Guide](SQL_Array_Explode_Guide.md)
* [Search Functions Reference](sql_functions/scalar_functions/search_functions/)
