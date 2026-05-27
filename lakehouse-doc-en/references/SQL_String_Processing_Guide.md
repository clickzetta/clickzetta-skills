# Lakehouse String Processing Guide

## Overview

String processing is one of the most common requirements in log analysis, user behavior analysis, and data cleansing. Singdata Lakehouse provides comprehensive string function support, including substring extraction and concatenation, regex extraction and replacement, fuzzy matching, and string aggregation. This guide is organized by business scenario to help you quickly master efficient string processing methods.

### Quick Navigation

* [Extraction and Concatenation](#scenario-1-extraction-and-concatenation) -- Use SUBSTR / CONCAT / CONCAT_WS to extract domains and build composite keys
* [Regex Extraction](#scenario-2-regex-extraction) -- Use REGEXP_EXTRACT to parse domains, paths, and parameters from URLs
* [Regex Replace and Cleansing](#scenario-3-regex-replace-and-cleansing) -- Use REGEXP_REPLACE to remove special characters and mask phone numbers
* [String Split to Rows](#scenario-4-string-split-to-rows) -- Use SPLIT + LATERAL VIEW EXPLODE to expand comma-separated tags
* [Fuzzy Matching and Filtering](#scenario-5-fuzzy-matching-and-filtering) -- Use LIKE / RLIKE to filter rows by keywords or regex
* [String Aggregation](#scenario-6-string-aggregation) -- Use GROUP_CONCAT / WM_CONCAT to merge multiple rows into a single string
* [Case and Whitespace Handling](#scenario-7-case-and-whitespace-handling) -- Use UPPER / LOWER / TRIM / LENGTH to normalize data

***

## SQL Commands Covered

| Command/Function | Purpose | Use Case |
|-----------|------|----------|
| `SUBSTR()` / `SUBSTRING()` | Extract substring by position | Extract domain, truncate fixed-length fields |
| `CONCAT()` | Concatenate multiple strings | Build composite keys, concatenate fields |
| `CONCAT_WS()` | Concatenate with a delimiter | Concatenate multiple columns into one delimited string |
| `LOCATE()` / `INSTR()` | Find character or substring position | Assist with extraction, locate delimiter positions |
| `REPLACE()` | Literal string replacement | Remove fixed prefixes/suffixes |
| `REGEXP_EXTRACT()` | Extract matching group via regex | Extract fields from URLs/logs |
| `REGEXP_REPLACE()` | Replace matches via regex | Cleanse special characters, mask data |
| `SPLIT()` | Split a string by delimiter into an array | Convert comma-separated tags to an array |
| `LATERAL VIEW EXPLODE()` | Expand an array column into multiple rows | Tag expansion, flatten multi-value fields |
| `LIKE` | Wildcard pattern matching | Keyword filtering |
| `RLIKE` | Regex pattern matching | Complex pattern filtering |
| `GROUP_CONCAT()` | Aggregate multiple rows into a string (supports ORDER BY) | Merge access IDs in order |
| `WM_CONCAT()` | Aggregate multiple rows into a string | Simple multi-row merging |
| `UPPER()` / `LOWER()` | Case conversion | Field normalization, unified formatting |
| `TRIM()` / `LTRIM()` / `RTRIM()` | Remove leading/trailing whitespace | Cleanse user input |
| `LENGTH()` | Return character count of a string | Length validation, filter empty values |

***

## Prerequisites

The following examples use a simulated access log table `doc_str_logs`:

```sql
-- Create test table
CREATE TABLE IF NOT EXISTS doc_str_logs (
    log_id  INT,
    user_id STRING,
    url     STRING,
    tags    STRING,
    content STRING
);

-- Insert test data
INSERT INTO doc_str_logs VALUES
(1, 'u001', 'https://www.example.com/product/detail?id=123',  'tech,mobile,review',    'Hello World! This is a test.'),
(2, 'u002', 'https://shop.example.com/category/shoes?color=red', 'fashion,shoes,sale', '  spaces around  '),
(3, 'u003', 'https://www.example.com/blog/post?tag=python',   'tech,python,tutorial',  'Python is great!'),
(4, 'u001', 'https://api.example.com/v2/users?page=1',        'api,backend,rest',      'API response: {"status":"ok"}'),
(5, 'u004', 'https://www.example.com/search?q=lakehouse',     'data,lakehouse,cloud',  'Lakehouse Data Platform'),
(6, 'u002', 'https://cdn.example.com/images/logo.png',        'image,cdn,static',      'CDN Resource File'),
(7, 'u005', 'https://www.example.com/product/detail?id=456',  'tech,mobile,new',       'Phone: 138-0013-8000, please contact'),
(8, 'u003', 'https://shop.example.com/checkout?order=789',    'order,payment,checkout','Order #789 confirmed!');
```

***

## Scenario 1: Extraction and Concatenation

Extracting domain names from URLs, or concatenating multiple fields into composite keys, are the most common string operations in log processing.

### Extract Domain with SUBSTR + LOCATE

`SUBSTR(str, pos, len)` extracts a substring of specified length starting from the specified position. `LOCATE(substr, str, start)` returns the position of the first occurrence of the substring starting from the `start` position. Using them together allows precise extraction of the domain part of a URL.

`https://` occupies exactly 8 characters, so the domain starts at position 9 and ends at the first slash:

```sql
SELECT
    log_id,
    url,
    SUBSTR(url, 9, LOCATE('/', url, 9) - 9) AS domain
FROM doc_str_logs
ORDER BY log_id;
```

**Execution Results**:

| log_id | url | domain |
|--------|-----|--------|
| 1 | https://www.example.com/product/detail?id=123 | www.example.com |
| 2 | https://shop.example.com/category/shoes?color=red | shop.example.com |
| 3 | https://www.example.com/blog/post?tag=python | www.example.com |
| 4 | https://api.example.com/v2/users?page=1 | api.example.com |
| 5 | https://www.example.com/search?q=lakehouse | www.example.com |
| 6 | https://cdn.example.com/images/logo.png | cdn.example.com |
| 7 | https://www.example.com/product/detail?id=456 | www.example.com |
| 8 | https://shop.example.com/checkout?order=789 | shop.example.com |

### Build Composite Keys with CONCAT

`CONCAT(str1, str2, ...)` concatenates multiple strings into one. Commonly used to create unique identifiers or label row provenance:

```sql
SELECT
    log_id,
    CONCAT(user_id, '@', REGEXP_EXTRACT(url, 'https?://([^/]+)', 1)) AS user_domain_key
FROM doc_str_logs
ORDER BY log_id;
```

**Execution Results**:

| log_id | user_domain_key |
|--------|----------------|
| 1 | u001@www.example.com |
| 2 | u002@shop.example.com |
| 3 | u003@www.example.com |
| 4 | u001@api.example.com |
| 5 | u004@www.example.com |
| 6 | u002@cdn.example.com |
| 7 | u005@www.example.com |
| 8 | u003@shop.example.com |

### Concatenate Multiple Fields with CONCAT_WS

`CONCAT_WS(sep, str1, str2, ...)` concatenates multiple columns with a uniform delimiter. It is cleaner than multiple `CONCAT` calls and automatically skips `NULL` values:

```sql
SELECT
    log_id,
    url,
    CONCAT_WS('|',
        REGEXP_EXTRACT(url, 'https?://([^/]+)', 1),
        REGEXP_EXTRACT(url, 'https?://[^/?]+(/[^?]*)', 1),
        REGEXP_EXTRACT(url, '[?](.*)', 1)
    ) AS url_parts
FROM doc_str_logs
ORDER BY log_id
LIMIT 5;
```

**Execution Results (first 5 rows)**:

| log_id | url | url_parts |
|--------|-----|-----------|
| 1 | https://www.example.com/product/detail?id=123 | www.example.com\|/product/detail\|id=123 |
| 2 | https://shop.example.com/category/shoes?color=red | shop.example.com\|/category/shoes\|color=red |
| 3 | https://www.example.com/blog/post?tag=python | www.example.com\|/blog/post\|tag=python |
| 4 | https://api.example.com/v2/users?page=1 | api.example.com\|/v2/users\|page=1 |
| 5 | https://www.example.com/search?q=lakehouse | www.example.com\|/search\|q=lakehouse |

***

## Scenario 2: Regex Extraction

When URLs or log formats are more complex, `REGEXP_EXTRACT` is more intuitive and maintainable than the `SUBSTR + LOCATE` combination.

`REGEXP_EXTRACT(str, pattern, group_index)` returns the content matched by the `group_index`-th capture group (starting from 1); a `group_index` of 0 returns the entire match.

### Split a URL into Domain, Path, and Query Parameters

```sql
SELECT
    log_id,
    REGEXP_EXTRACT(url, 'https?://([^/?]+)', 1)         AS domain,
    REGEXP_EXTRACT(url, 'https?://[^/?]+(/[^?]*)', 1)   AS path,
    REGEXP_EXTRACT(url, '[?](.*)', 1)                    AS query_string
FROM doc_str_logs
ORDER BY log_id;
```

**Execution Results**:

| log_id | domain | path | query_string |
|--------|--------|------|--------------|
| 1 | www.example.com | /product/detail | id=123 |
| 2 | shop.example.com | /category/shoes | color=red |
| 3 | www.example.com | /blog/post | tag=python |
| 4 | api.example.com | /v2/users | page=1 |
| 5 | www.example.com | /search | q=lakehouse |
| 6 | cdn.example.com | /images/logo.png | (empty) |
| 7 | www.example.com | /product/detail | id=456 |
| 8 | shop.example.com | /checkout | order=789 |

> **Note**: In `[?](.*)`, the `?` is placed inside the character class `[?]` to prevent the regex engine from treating it as a quantifier. URLs without query parameters (such as log_id=6) return an empty string.

### Extract the First Parameter Key and Value from a URL

```sql
SELECT
    log_id,
    REGEXP_EXTRACT(url, '[?&]([^=]+)=([^&]+)', 1) AS param_key,
    REGEXP_EXTRACT(url, '[?&][^=]+=([^&]+)',    1) AS param_value
FROM doc_str_logs
WHERE url LIKE '%?%'
ORDER BY log_id;
```

**Execution Results**:

| log_id | param_key | param_value |
|--------|-----------|-------------|
| 1 | id | 123 |
| 2 | color | red |
| 3 | tag | python |
| 4 | page | 1 |
| 5 | q | lakehouse |
| 7 | id | 456 |
| 8 | order | 789 |

***

## Scenario 3: Regex Replace and Cleansing

`REGEXP_REPLACE(str, pattern, replacement)` replaces all parts of the string matching `pattern` with `replacement`, commonly used for removing noise and masking data.

### Remove Special Characters

Keep Chinese characters, English letters, digits, and spaces; remove punctuation and other special characters:

```sql
SELECT
    log_id,
    content,
    REGEXP_REPLACE(content, '[^a-zA-Z0-9\\u4e00-\\u9fa5 ]', '') AS cleaned
FROM doc_str_logs
ORDER BY log_id;
```

**Execution Results**:

| log_id | content | cleaned |
|--------|---------|---------|
| 1 | Hello World! This is a test. | Hello World This is a test |
| 2 |   spaces around   |   spaces around   |
| 3 | Python is great! | Python is great |
| 4 | API response: {"status":"ok"} | API response statusok |
| 5 | Lakehouse Data Platform | Lakehouse Data Platform |
| 6 | CDN Resource File | CDN Resource File |
| 7 | Phone: 138-0013-8000, please contact | Phone13800138000please contact |
| 8 | Order #789 confirmed! | Order 789 confirmed |

> **Note**: `\u4e00-\u9fa5` is the Unicode range for basic CJK characters, used to preserve Chinese characters in regex.

### Mask Phone Numbers

Replace phone numbers in `NNN-NNNN-NNNN` format with a masked placeholder:

```sql
SELECT
    log_id,
    content,
    REGEXP_REPLACE(content, '[0-9]{3}-[0-9]{4}-[0-9]{4}', 'PHONE_HIDDEN') AS masked
FROM doc_str_logs
ORDER BY log_id;
```

**Execution Results**:

| log_id | content | masked |
|--------|---------|--------|
| 1 | Hello World! This is a test. | Hello World! This is a test. |
| 2 |   spaces around   |   spaces around   |
| 3 | Python is great! | Python is great! |
| 4 | API response: {"status":"ok"} | API response: {"status":"ok"} |
| 5 | Lakehouse Data Platform | Lakehouse Data Platform |
| 6 | CDN Resource File | CDN Resource File |
| 7 | Phone: 138-0013-8000, please contact | Phone: PHONE_HIDDEN, please contact |
| 8 | Order #789 confirmed! | Order #789 confirmed! |

> **Note**: `REGEXP_REPLACE` replaces all matching positions in the string. If the content contains multiple phone numbers, every one will be replaced.

### Remove Fixed Prefixes with REPLACE

For simple literal replacements, `REPLACE(str, search, replacement)` is more efficient than regex:

```sql
SELECT
    log_id,
    REPLACE(url, 'https://', '') AS url_no_scheme
FROM doc_str_logs
ORDER BY log_id
LIMIT 4;
```

**Execution Results (first 4 rows)**:

| log_id | url_no_scheme |
|--------|--------------|
| 1 | www.example.com/product/detail?id=123 |
| 2 | shop.example.com/category/shoes?color=red |
| 3 | www.example.com/blog/post?tag=python |
| 4 | api.example.com/v2/users?page=1 |

***

## Scenario 4: String Split to Rows

When a single column stores multiple values (such as comma-separated tags), you first need to use `SPLIT` to cut it into an array, then use `LATERAL VIEW EXPLODE` to expand the array into multiple rows, enabling tag-based grouping and statistics.

### Expand a Tag Column

```sql
SELECT
    log_id,
    tags,
    tag
FROM doc_str_logs
LATERAL VIEW EXPLODE(SPLIT(tags, ',')) t AS tag
ORDER BY log_id, tag;
```

**Execution Results (first 9 rows)**:

| log_id | tags | tag |
|--------|------|-----|
| 1 | tech,mobile,review | mobile |
| 1 | tech,mobile,review | review |
| 1 | tech,mobile,review | tech |
| 2 | fashion,shoes,sale | fashion |
| 2 | fashion,shoes,sale | sale |
| 2 | fashion,shoes,sale | shoes |
| 3 | tech,python,tutorial | python |
| 3 | tech,python,tutorial | tech |
| 3 | tech,python,tutorial | tutorial |

### Count Tag Frequencies

After expansion, aggregate analysis on tags can be performed:

```sql
SELECT
    tag,
    COUNT(*) AS log_count
FROM doc_str_logs
LATERAL VIEW EXPLODE(SPLIT(tags, ',')) t AS tag
GROUP BY tag
ORDER BY log_count DESC, tag;
```

**Execution Results**:

| tag | log_count |
|-----|-----------|
| tech | 3 |
| mobile | 2 |
| api | 1 |
| backend | 1 |
| cdn | 1 |
| checkout | 1 |
| cloud | 1 |
| data | 1 |
| fashion | 1 |
| image | 1 |
| lakehouse | 1 |
| new | 1 |
| order | 1 |
| payment | 1 |
| python | 1 |
| rest | 1 |
| review | 1 |
| sale | 1 |
| shoes | 1 |
| static | 1 |
| tutorial | 1 |

> **Note**: `SPLIT(tags, ',')` returns a string array. `LATERAL VIEW EXPLODE(...)` expands each element of the array into a separate row, with the expanded column named via `AS tag`.

If you only need to convert the string to an array and count the number of elements without expanding into rows, you can use `SIZE(SPLIT(...))`:

```sql
SELECT
    log_id,
    tags,
    SPLIT(tags, ',')        AS tag_array,
    SIZE(SPLIT(tags, ','))  AS tag_count
FROM doc_str_logs
ORDER BY log_id
LIMIT 4;
```

**Execution Results (first 4 rows)**:

| log_id | tags | tag_array | tag_count |
|--------|------|-----------|-----------|
| 1 | tech,mobile,review | ["tech","mobile","review"] | 3 |
| 2 | fashion,shoes,sale | ["fashion","shoes","sale"] | 3 |
| 3 | tech,python,tutorial | ["tech","python","tutorial"] | 3 |
| 4 | api,backend,rest | ["api","backend","rest"] | 3 |

***

## Scenario 5: Fuzzy Matching and Filtering

### LIKE: Wildcard Matching

`LIKE` uses `%` (any number of characters) and `_` (a single character) as wildcards. Suitable for simple patterns such as path prefixes and keyword containment:

```sql
-- Filter records where the URL path contains /product/
SELECT log_id, url
FROM doc_str_logs
WHERE url LIKE '%/product/%'
ORDER BY log_id;
```

**Execution Results**:

| log_id | url |
|--------|-----|
| 1 | https://www.example.com/product/detail?id=123 |
| 7 | https://www.example.com/product/detail?id=456 |

### RLIKE: Regex Matching

`RLIKE` (equivalent to `REGEXP`) supports full regex syntax and is suitable for complex patterns:

```sql
-- Filter visits from the www or shop subdomain
SELECT log_id, url
FROM doc_str_logs
WHERE url RLIKE '^https://(www|shop)\\.example\\.com'
ORDER BY log_id;
```

**Execution Results**:

| log_id | url |
|--------|-----|
| 1 | https://www.example.com/product/detail?id=123 |
| 2 | https://shop.example.com/category/shoes?color=red |
| 3 | https://www.example.com/blog/post?tag=python |
| 5 | https://www.example.com/search?q=lakehouse |
| 7 | https://www.example.com/product/detail?id=456 |
| 8 | https://shop.example.com/checkout?order=789 |

```sql
-- Filter records where content contains a phone number pattern
SELECT log_id, content
FROM doc_str_logs
WHERE content RLIKE '[0-9]{3}-[0-9]{4}-[0-9]{4}'
ORDER BY log_id;
```

**Execution Results**:

| log_id | content |
|--------|---------|
| 7 | Phone: 138-0013-8000, please contact |

***

## Scenario 6: String Aggregation

Merge multiple rows of strings into a single row, commonly used for generating report summaries or constructing analytical dimensions.

### GROUP_CONCAT: Ordered Aggregation (supports ORDER BY)

`GROUP_CONCAT(expr ORDER BY col SEPARATOR sep)` supports sorting and custom delimiters during merging:

```sql
-- Aggregate access record IDs by user, ordered by log_id ascending
SELECT
    user_id,
    GROUP_CONCAT(log_id ORDER BY log_id SEPARATOR ',') AS log_ids,
    COUNT(*) AS visit_count
FROM doc_str_logs
GROUP BY user_id
ORDER BY user_id;
```

**Execution Results**:

| user_id | log_ids | visit_count |
|---------|---------|-------------|
| u001 | 1,4 | 2 |
| u002 | 2,6 | 2 |
| u003 | 3,8 | 2 |
| u004 | 5 | 1 |
| u005 | 7 | 1 |

```sql
-- Aggregate access tags by user, separated by semicolons
SELECT
    user_id,
    GROUP_CONCAT(tags ORDER BY log_id SEPARATOR '; ') AS all_tags
FROM doc_str_logs
GROUP BY user_id
ORDER BY user_id;
```

**Execution Results**:

| user_id | all_tags |
|---------|----------|
| u001 | tech,mobile,review; api,backend,rest |
| u002 | fashion,shoes,sale; image,cdn,static |
| u003 | tech,python,tutorial; order,payment,checkout |
| u004 | data,lakehouse,cloud |
| u005 | tech,mobile,new |

> **Note**: `DISTINCT` and `ORDER BY` cannot be used together in the same `GROUP_CONCAT` call; doing so will produce an error. To deduplicate results, use a subquery to deduplicate first, then aggregate.

### WM_CONCAT: Concise Syntax

`WM_CONCAT(sep, expr)` is a more concise string aggregation syntax that does not support `ORDER BY`, suitable for scenarios where ordering is not required:

```sql
SELECT
    user_id,
    WM_CONCAT(';', tags) AS all_tags
FROM doc_str_logs
GROUP BY user_id
ORDER BY user_id;
```

**Execution Results**:

| user_id | all_tags |
|---------|----------|
| u001 | tech,mobile,review;api,backend,rest |
| u002 | fashion,shoes,sale;image,cdn,static |
| u003 | tech,python,tutorial;order,payment,checkout |
| u004 | data,lakehouse,cloud |
| u005 | tech,mobile,new |

> **Note**: `WM_CONCAT` does not guarantee aggregation order. If deterministic merge ordering is needed, use `GROUP_CONCAT ... ORDER BY`.

### GROUP_CONCAT DISTINCT: Aggregate Unique Values

Deduplicate and merge the unique domains visited by each user:

```sql
SELECT
    user_id,
    GROUP_CONCAT(DISTINCT REGEXP_EXTRACT(url, 'https?://([^/]+)', 1) SEPARATOR ', ') AS domains
FROM doc_str_logs
GROUP BY user_id
ORDER BY user_id;
```

**Execution Results**:

| user_id | domains |
|---------|---------|
| u001 | www.example.com, api.example.com |
| u002 | shop.example.com, cdn.example.com |
| u003 | www.example.com, shop.example.com |
| u004 | www.example.com |
| u005 | www.example.com |

***

## Scenario 7: Case and Whitespace Handling

Data is often ingested with inconsistent casing or leading/trailing whitespace, requiring normalization before analysis.

### Case Conversion

`UPPER(str)` converts a string to uppercase, `LOWER(str)` to lowercase:

```sql
SELECT
    log_id,
    content,
    UPPER(content) AS upper_content
FROM doc_str_logs
WHERE log_id IN (1, 3, 8)
ORDER BY log_id;
```

**Execution Results**:

| log_id | content | upper_content |
|--------|---------|--------------|
| 1 | Hello World! This is a test. | HELLO WORLD! THIS IS A TEST. |
| 3 | Python is great! | PYTHON IS GREAT! |
| 8 | Order #789 confirmed! | ORDER #789 CONFIRMED! |

### Remove Leading/Trailing Whitespace

`TRIM(str)` removes whitespace from both ends, `LTRIM` removes from the left only, `RTRIM` from the right only:

```sql
SELECT
    log_id,
    content,
    TRIM(content)   AS trimmed,
    LTRIM(content)  AS ltrimmed,
    RTRIM(content)  AS rtrimmed
FROM doc_str_logs
WHERE log_id = 2;
```

**Execution Results**:

| log_id | content | trimmed | ltrimmed | rtrimmed |
|--------|---------|---------|----------|---------|
| 2 |   spaces around   | spaces around | spaces around   |   spaces around |

### Combined Normalization: LOWER + TRIM + LENGTH

Before grouping or JOINing, handle casing and whitespace simultaneously to avoid matching failures due to format differences:

```sql
SELECT
    log_id,
    user_id,
    LOWER(TRIM(user_id))  AS normalized_uid,
    LENGTH(TRIM(content)) AS content_len
FROM doc_str_logs
ORDER BY log_id;
```

**Execution Results**:

| log_id | user_id | normalized_uid | content_len |
|--------|---------|---------------|-------------|
| 1 | u001 | u001 | 28 |
| 2 | u002 | u002 | 13 |
| 3 | u003 | u003 | 16 |
| 4 | u001 | u001 | 29 |
| 5 | u004 | u004 | 14 |
| 6 | u002 | u002 | 7 |
| 7 | u005 | u005 | 21 |
| 8 | u003 | u003 | 21 |

> **Note**: `LENGTH` returns the character count (not byte count). Chinese characters and English characters each count as 1 character.

***

## Clean Up Test Data

After completing string processing verification, it is recommended to clean up the test table:

```sql
DROP TABLE IF EXISTS doc_str_logs;
```

> **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Notes

1. **Escaping `?` in REGEXP_EXTRACT**: In regex, `?` is a quantifier. To match a literal `?`, write it as `[?]` or `\?`. Writing `'?(.*)'` directly will cause a `no argument for repetition operator` error.
2. **REGEXP_REPLACE Does Not Support Backreferences**: Singdata Lakehouse's `REGEXP_REPLACE` does not support capture group backreferences like `$1` or `\1`; the replacement content can only be a literal string.
3. **DISTINCT and ORDER BY Are Incompatible in GROUP_CONCAT**: Using `DISTINCT` and `ORDER BY` together in the same `GROUP_CONCAT` call will produce a `Distinct aggregate call and aggregate call with order by can not coexist` error.
4. **LIKE vs RLIKE Performance**: `LIKE` with wildcards performs better than `RLIKE`; prefer `LIKE` when full regex capabilities are not needed.
5. **LENGTH Counts Characters, Not Bytes**: `LENGTH('CDN Resource File')` returns the character count, not the byte length. For byte length, use `OCTET_LENGTH`.
6. **SPLIT Delimiter Is Regex**: The second argument of `SPLIT(str, pattern)` is a regex pattern. If the delimiter contains special regex characters such as `.` or `|`, they need to be escaped: `SPLIT(str, '\\.')`.

***

## Related Documentation

* [String Functions](string_function.md)
* [Regex Functions](regexp-function.md)
* [LATERAL VIEW](LATERALVIEW.md)
* [Aggregate Functions](agg_function.md)
