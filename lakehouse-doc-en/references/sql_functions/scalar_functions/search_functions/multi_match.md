# MULTI_MATCH

```Plain
MULTI_MATCH(inverted_column, keyword1, keyword2, ...)
```

### Description

`MULTI_MATCH` is an alias for `MATCH_ANY`; both have identical semantics. Only columns with an Inverted Index can use this function. It performs multi-keyword full-text search on the target column and returns `true` if any keyword matches.

The difference from `MATCH_ANY`: `MATCH_ANY` combines multiple keywords into a single `query` string and passes it to the analyzer for tokenization before matching; `MULTI_MATCH` accepts multiple independent keyword arguments directly — each argument is treated as an independent term without analyzer tokenization — making it suited for exact term matching.

Calling `MULTI_MATCH` on a column without an Inverted Index returns `null`.

### Parameters

* **inverted\_column**: A column that has an Inverted Index (`USING INVERTED`). Returns `null` when called on a regular column.
* **keyword1, keyword2, ...**: One or more keywords as string literals. Returns `true` if any keyword matches the column value.

> ⚠️ **Note**: The target column must have an Inverted Index created in advance. Without one, the function returns `null` rather than raising an error, and no rows are filtered.

### Return Value

* When the column has an Inverted Index: `boolean` — returns `true` on match, `false` otherwise.
* When the column has no Inverted Index: `null`.

### Examples

**Prerequisites: create a table with an Inverted Index**

```sql
CREATE TABLE doc_articles (
  id     INT,
  title  STRING,
  body   STRING,
  INDEX  idx_body (body) USING INVERTED PROPERTIES("parser" = "unicode")
);

INSERT INTO doc_articles VALUES
  (1, 'Intro to SQL',   'SQL is a language for relational databases'),
  (2, 'Python Basics',  'Python is easy to learn and widely used'),
  (3, 'Cloud Storage',  'Object storage scales automatically in the cloud'),
  (4, 'SQL and Python', 'Combine SQL queries with Python for data analysis');

BUILD INDEX idx_body ON doc_articles;
```

**Scenario 1: single-keyword match**

```sql
SELECT id, title
FROM doc_articles
WHERE MULTI_MATCH(body, 'SQL');
```

```
+----+----------------+
| id | title          |
+----+----------------+
| 1  | Intro to SQL   |
| 4  | SQL and Python |
+----+----------------+
```

**Scenario 2: multi-keyword match (returns a row if any keyword hits)**

```sql
SELECT id, title
FROM doc_articles
WHERE MULTI_MATCH(body, 'Python', 'cloud');
```

```
+----+----------------+
| id | title          |
+----+----------------+
| 2  | Python Basics  |
| 3  | Cloud Storage  |
| 4  | SQL and Python |
+----+----------------+
```

Rows where `body` contains "Python" or "cloud" (case-insensitive) are returned.

**Scenario 3: calling on a column without an Inverted Index (returns null)**

```sql
SELECT MULTI_MATCH('hello world', 'hello', 'world');
```

```
+------+
| res  |
+------+
| null |
+------+
```

Calling on a string literal (no Inverted Index) returns `null` without raising an error.

### Notes

* The target column must have `CREATE INDEX ... USING INVERTED` executed and `BUILD INDEX` completed in advance; otherwise the function returns `null`.
* Keyword matching is case-insensitive.
* `MULTI_MATCH` and `MATCH_ANY` have identical semantics and are interchangeable. `MATCH_ANY` additionally supports an `option` (analyzer) parameter; `MULTI_MATCH` does not accept that parameter.
* Regular expressions and fuzzy matching are not supported. Use `MATCH_REGEXP` for regex-based full-text search.

### Related Documentation

* [MATCH_ANY](match_any.md)
* [MATCH_ALL](match_all.md)
* [MATCH_PHRASE](match_phrase.md)
* [MATCH_REGEXP](match_regexp.md)
* [Index Best Practices](../../../index-manager.md)
