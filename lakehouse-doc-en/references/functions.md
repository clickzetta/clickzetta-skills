# SQL Functions

Singdata Lakehouse includes a rich built-in SQL function library covering numeric computation, string processing, time operations, complex types, aggregation and window analysis, as well as specialized functions for AI and analytics scenarios such as vector search and BITMAP audience segmentation.

---

## Function Categories

### Core Computation

| Category | Description |
|----------|-------------|
| [Operators](sql_functions/scalar_functions/math_functions/operators.md) | Arithmetic, comparison, logical, and bitwise operators |
| [Math Functions](math_function.md) | ABS, ROUND, CEIL, FLOOR, POWER, LOG, and other numeric functions |
| [Conditional Functions](conditional_function.md) | IF, IFF, CASE WHEN, COALESCE, NULLIF, NVL, and other conditional expressions |
| [Type Conversion Functions](datatype-cast.md) | CAST, TRY_CAST, and various type conversion functions |

### String and Regex

| Category | Description |
|----------|-------------|
| [String Functions](string_function.md) | CONCAT, SUBSTR, TRIM, REPLACE, SPLIT, LENGTH, and more |
| [Regex Functions](regexp-function.md) | REGEXP_LIKE, REGEXP_EXTRACT, REGEXP_REPLACE, and more |
| [Encryption and Masking Functions](encryption-function.md) | MD5, SHA256, AES encryption/decryption, data masking |
| [Hash Functions](hash.md) | HASH, MURMUR_HASH, and other hash functions |

### Time and Date

| Category | Description |
|----------|-------------|
| [Time Functions](time-function.md) | DATE_ADD, DATE_DIFF, DATE_FORMAT, CONVERT_TIMEZONE, CURRENT_TIMESTAMP, and more |

### Complex Types

| Category | Description |
|----------|-------------|
| [ARRAY Functions](array_function.md) | ARRAY_AGG, ARRAY_CONTAINS, EXPLODE, SORT_ARRAY, and more |
| [MAP Functions](map-function.md) | MAP_KEYS, MAP_VALUES, MAP_CONTAINS_KEY, and more |
| [STRUCT Functions](struct-function.md) | STRUCT construction and field access |
| [JSON Functions](json_function.md) | JSON_VALUE, JSON_EXTRACT, JSON_OBJECT, JSON_ARRAY, and more |
| [Higher-Order Functions](high_order_function.md) | TRANSFORM, FILTER, AGGREGATE, REDUCE, and other lambda functions |

### Aggregation and Window

| Category | Description |
|----------|-------------|
| [Aggregate Functions](agg_function.md) | COUNT, SUM, AVG, MAX, MIN, PERCENTILE, CORR, and more |
| [Window Functions](sql_functions/window_functions/window_clause.md) | ROW_NUMBER, RANK, LAG, LEAD, SUM OVER, NTILE, and more |

### AI and Analytics

**AI Functions** are native AI capabilities in Singdata Lakehouse. They let you call large language models and embedding models directly in SQL — completing text understanding, vectorization, and content generation without leaving the data platform. All AI functions take `model` as the first parameter, in the format `'endpoint:model_name'` (configured via [AI Gateway](AIGateway.md)).

| Function | Description |
|----------|-------------|
| [AI_COMPLETE](AI_COMPLETE.md) | General LLM completion; supports custom prompts; suited for complex reasoning, code generation, and other custom scenarios; supports image input |
| [AI_EMBEDDING](AI_EMBEDDING.md) | Convert text to high-dimensional vectors (`ARRAY<FLOAT>`); used for semantic search, RAG, recommendations, and clustering |
| [AI_CLASSIFY](ai_classify.md) | Classify text or images into user-defined categories; no prompt writing required; supports 29+ languages |
| [AI_EXTRACT](ai_extract.md) | Extract structured JSON from unstructured text or images by specified fields; no prompt writing required |
| [AI_SENTIMENT](ai_sentiment.md) | Sentiment analysis; returns positive / negative / neutral; supports multiple languages |
| [AI_SUMMARIZE](ai_summarize.md) | Generate text summaries; supports `max_words` to control summary length |
| [AI_TRANSLATE](ai_translate.md) | Text translation; source language auto-detected; supports 20+ language pairs |
| [AI_FIX_GRAMMAR](ai_fix_grammar.md) | Automatically fix grammar, spelling, and punctuation errors; supports Chinese, English, and mixed-language text |
| [AI_MASK](ai_mask.md) | Identify and mask PII sensitive information; replaces with `[MASKED]`; labels are user-defined |
| [AI_SIMILARITY](ai_similarity.md) | Compute cosine similarity between two text segments; returns a score in [0, 1] |
| [AI_TRANSCRIBE](ai_transcribe.md) | Transcribe audio files to plain text (ASR); supports Chinese, English, and other languages |

Full documentation and examples: [AI Functions Guide](AI_function_in_SQL.md) · [AI Functions Overview](ai_functions_overview.md) · [AI Gateway Configuration](AIGateway.md)

| Category | Description |
|----------|-------------|
| [Vector Functions](vector-functions.md) | Vector distance computation (cosine_distance, l2_distance, etc.), vector similarity search |
| [Search Functions](search-functions.md) | Full-text search scoring functions; used with inverted indexes |
| [BITMAP Functions](bitmap_function.md) | BITMAP_AND, BITMAP_OR, BITMAP_CARDINALITY, and other audience segmentation and UV statistics functions |

### Database and System

| Category | Description |
|----------|-------------|
| [Context Functions](context_function.md) | CURRENT_USER, CURRENT_DATABASE, VERSION, and other session information functions |
| [Table Functions](table_function.md) | EXPLODE, GENERATE_SERIES, UNNEST, and other table-returning functions |
| [File Functions](file_functions.md) | Volume file operation functions |
| [Partition Functions](partition-func.md) | Partition pruning and partition metadata query functions |

### Other

| Category | Description |
|----------|-------------|
| [GEO Functions](geo.md) | Geospatial computation: distance, coordinate conversion, etc. |
| [IP Functions](ip_function.md) | IP address parsing, geolocation lookup, etc. |
| [BIT Functions](bit_function.md) | BIT_COUNT, SHIFTLEFT, SHIFTRIGHT, and other bitwise operation functions |

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [Data Types](data-type-guide.md) | Type descriptions to understand function input and output types |
| [SQL Functions Usage Guide](sql_functions_guide.md) | Quick function reference and usage tips for common scenarios |
| [AI Functions (AI_COMPLETE / AI_EMBEDDING)](AI_function_in_SQL.md) | Call LLMs and vector embeddings in SQL |
