# AI_CONTEXT_LENGTH

## Function

Estimates the number of tokens consumed by the input content when calling a specified AI function, **without making any API calls**.

The calculation is performed entirely locally, making it suitable for cost estimation before a real call, filtering out overly long texts, or monitoring dataset size. It incurs no API fees and does not trigger rate limiting.

---

## Syntax

```sql
AI_CONTEXT_LENGTH(function_name, args...)
```

| Parameter | Type | Description |
|------|------|------|
| `function_name` | STRING constant | The target AI function name; case-insensitive, e.g., `'AI_COMPLETE'` |
| `args...` | Same as target function | Corresponds to the target function's parameters — **omit model and options**, keep all others |

**Return value**: `INT`, the estimated token count; returns NULL when the first content argument is NULL; returns 0 for an empty string.

---

## Parameter Mapping by Function

| Target function call | AI_CONTEXT_LENGTH syntax |
|-------------|----------------------|
| `AI_COMPLETE(model, content)` | `AI_CONTEXT_LENGTH('AI_COMPLETE', content)` |
| `AI_EMBEDDING(model, text)` | `AI_CONTEXT_LENGTH('AI_EMBEDDING', text)` |
| `AI_EXTRACT(model, content, labels)` | `AI_CONTEXT_LENGTH('AI_EXTRACT', content, labels)` |
| `AI_CLASSIFY(model, content, labels)` | `AI_CONTEXT_LENGTH('AI_CLASSIFY', content, labels)` |
| `AI_SUMMARIZE(model, content, max_words)` | `AI_CONTEXT_LENGTH('AI_SUMMARIZE', content, max_words)` |
| `AI_SENTIMENT(model, content)` | `AI_CONTEXT_LENGTH('AI_SENTIMENT', content)` |
| `AI_TRANSLATE(model, content, to_lang)` | `AI_CONTEXT_LENGTH('AI_TRANSLATE', content, to_lang)` |
| `AI_FIX_GRAMMAR(model, content)` | `AI_CONTEXT_LENGTH('AI_FIX_GRAMMAR', content)` |
| `AI_MASK(model, content, labels)` | `AI_CONTEXT_LENGTH('AI_MASK', content, labels)` |
| `AI_SIMILARITY(model, text1, text2)` | `AI_CONTEXT_LENGTH('AI_SIMILARITY', text1, text2)` |

> **Not supported**: `AI_TRANSCRIBE` — audio content cannot have its token count calculated via text. Passing this function name will result in a runtime error (CZLH-67000).

---

## Usage Examples

### 1. Estimate the token count of a single text

```sql
SELECT AI_CONTEXT_LENGTH('AI_COMPLETE', 'Hello, please introduce vector databases');
-- Returns: 7
```

### 2. Filter out overly long texts before calling

Avoid runtime errors caused by exceeding the model's context length limit:

```sql
SELECT doc_id, AI_SUMMARIZE('conn_openai:gpt-4o-mini', content, 50) AS summary
FROM documents
WHERE AI_CONTEXT_LENGTH('AI_SUMMARIZE', content, 50) BETWEEN 10 AND 3000;
```

### 3. Analyze token distribution across a dataset to estimate costs

```sql
SELECT
  COUNT(*)                                         AS doc_count,
  AVG(AI_CONTEXT_LENGTH('AI_COMPLETE', content))   AS avg_tokens,
  MAX(AI_CONTEXT_LENGTH('AI_COMPLETE', content))   AS max_tokens,
  SUM(AI_CONTEXT_LENGTH('AI_COMPLETE', content))   AS total_tokens
FROM documents;
```

### 4. Functions with labels (labels token consumption is included)

```sql
SELECT AI_CONTEXT_LENGTH(
  'AI_EXTRACT',
  'John, 25 years old, lives in Beijing',
  ARRAY['name', 'age', 'city']
);
-- Returns: 135
```

### 5. Route to different models based on token count

Use a smaller model for short texts to save costs; automatically switch to a larger model for long texts:

```sql
SELECT
  doc_id,
  CASE
    WHEN AI_CONTEXT_LENGTH('AI_COMPLETE', content) <= 4000
      THEN AI_COMPLETE('conn_openai:gpt-4o-mini', content)
    ELSE
      AI_COMPLETE('conn_openai:gpt-4o', content)
  END AS reply
FROM documents;
```

### 6. Special input behavior

```sql
-- NULL input returns NULL
SELECT AI_CONTEXT_LENGTH('AI_COMPLETE', NULL);
-- Returns: NULL

-- Empty string returns 0
SELECT AI_CONTEXT_LENGTH('AI_COMPLETE', '');
-- Returns: 0

-- Case-insensitive; both produce the same result
SELECT AI_CONTEXT_LENGTH('ai_complete', 'test'),
       AI_CONTEXT_LENGTH('AI_COMPLETE', 'test');
-- Returns: 3, 3
```

---

## Error Cases

| Error Scenario | Error Stage | Error Code | Description |
|---------|---------|-------|------|
| `function_name` is a column name or variable | Compile time | CZLH-42000 | Must be a literal constant |
| Unknown function name passed (e.g., `'AI_UNKNOWN'`) | Compile time | CZLH-42000 | Only functions listed in the table above are supported |
| `'AI_TRANSCRIBE'` passed | Runtime | CZLH-67000 | Audio token count cannot be computed from text |

---

## Notes

| Note | Description |
|--------|------|
| `function_name` must be a constant | Cannot be a column name or variable; must be a hardcoded string in SQL |
| Omit model and options | Pass only content parameters; do not pass the model name or options |
| Margin of error | Uses a built-in local tokenizer for estimation; typical deviation from the model's actual billing is less than 5% |
| Deterministic function | The same input always produces the same result; safe to use in materialized views, caching, partition pruning, etc. |
| Zero API overhead | Fully local computation; no requests are made; full-table scans on large tables will not trigger rate limiting or incur fees |
| AI_TRANSCRIBE not supported | Passing this function name will cause a **runtime** (not compile-time) error: CZLH-67000 |

---

## Validation Examples

| Test Case | SQL | Actual Result |
|------|-----|---------|
| Basic usage | `AI_CONTEXT_LENGTH('AI_COMPLETE', 'Hello, please introduce vector databases')` | 7 |
| NULL input | `AI_CONTEXT_LENGTH('AI_COMPLETE', NULL)` | NULL |
| Empty string | `AI_CONTEXT_LENGTH('AI_COMPLETE', '')` | 0 |
| AI_EMBEDDING | `AI_CONTEXT_LENGTH('AI_EMBEDDING', 'hello world')` | 2 |
| AI_EXTRACT + labels | `AI_CONTEXT_LENGTH('AI_EXTRACT', 'John, 25, Beijing', ARRAY['name','age','city'])` | 135 |
| AI_CLASSIFY + labels | `AI_CONTEXT_LENGTH('AI_CLASSIFY', 'This is a technology article', ARRAY['tech','sports','entertainment'])` | 78 |
| AI_SUMMARIZE + max_words | `AI_CONTEXT_LENGTH('AI_SUMMARIZE', 'This is some text that needs to be summarized', 50)` | 38 |
| AI_SENTIMENT | `AI_CONTEXT_LENGTH('AI_SENTIMENT', 'The weather is great today, feeling happy')` | 61 |
| AI_TRANSLATE | `AI_CONTEXT_LENGTH('AI_TRANSLATE', 'Hello world', 'zh')` | 31 |
| AI_FIX_GRAMMAR | `AI_CONTEXT_LENGTH('AI_FIX_GRAMMAR', 'He go to school yesterday')` | 40 |
| AI_MASK + labels | `AI_CONTEXT_LENGTH('AI_MASK', 'John phone: 13800138000', ARRAY['name','phone'])` | 60 |
| AI_SIMILARITY | `AI_CONTEXT_LENGTH('AI_SIMILARITY', 'vector database', 'vector search')` | 7 |
| Case-insensitive | `AI_CONTEXT_LENGTH('ai_complete', 'test case') = AI_CONTEXT_LENGTH('AI_COMPLETE', 'test case')` | 3 = 3 ✓ |
| AI_TRANSCRIBE (should error) | `AI_CONTEXT_LENGTH('AI_TRANSCRIBE', ...)` | Runtime error CZLH-67000 ✓ |
| Unknown function name (should error) | `AI_CONTEXT_LENGTH('AI_UNKNOWN_FUNC', 'test')` | Compile-time error CZLH-42000 ✓ |
| Non-constant function name (should error) | `AI_CONTEXT_LENGTH(col, 'test')` | Compile-time error CZLH-42000 ✓ |
