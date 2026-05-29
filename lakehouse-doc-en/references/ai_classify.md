# AI_CLASSIFY

`AI_CLASSIFY` is an AI text/image classification function provided by Singdata Lakehouse. It automatically assigns input content to user-defined categories — no model training, no prompt writing. One line of SQL is all it takes.

---

## Syntax

```sql
AI_CLASSIFY(model, content, labels [, options])
```

| Parameter | Type | Required | Description |
|------|------|------|------|
| `model` | STRING | Yes | Model identifier; supports `endpoint:` and `connection:` sources |
| `content` | STRING or image reference | Yes | Text to classify, or `GET_PRESIGNED_URL(...) AS image` |
| `labels` | ARRAY | Yes | Category array: `ARRAY('category1', 'category2', ...)` |
| `options` | JSON literal | No | Optional parameters (timeout, concurrency, model params) |

**Return value:** STRING — the best-matching category name (plain string, not JSON).

---

## model Parameter

### Method 1: API Gateway Endpoint (Recommended)

A platform administrator pre-configures model services in the API Gateway. Regular users reference them with the `endpoint:` prefix, without needing to know the underlying connection details.

```sql
'endpoint:<endpoint_name>'

-- Examples
'endpoint:qwen3.5-plus'
'endpoint:qwen3-max-preview'
```

### Method 2: API Connection Object

Users create their own connection objects via `CREATE API CONNECTION`, suitable for custom service addresses, authentication keys, or private deployment models.

```sql
-- Create a connection object
CREATE API CONNECTION conn_bailian
    TYPE ai_function
    PROVIDER = 'bailian'
    BASE_URL = 'https://dashscope.aliyuncs.com/api/v1'
    API_KEY = 'sk-xxxxxxxxxxxxxxxxxxxxxxxx';

-- Reference with connection: prefix
SELECT AI_CLASSIFY('conn_bailian:qwen3.5-plus', 'iPhone', ARRAY('electronics', 'clothing', 'food'));
```

`CREATE API CONNECTION` field descriptions:

| Field | Description |
|------|------|
| `TYPE` | Fixed as `ai_function` |
| `PROVIDER` | Model provider identifier, e.g. `'bailian'`, `'openai'`, `'anthropic'` |
| `BASE_URL` | Base API URL of the model service |
| `API_KEY` | Authentication key for calling the service |

---

## Quick Start

```sql
-- Text classification
SELECT AI_CLASSIFY(
    'endpoint:qwen3.5-plus',
    'iPhone',
    ARRAY('electronics', 'clothing', 'food')
);
-- Returns: electronics
```

---

## Use Cases

### Case 1: Product Classification

```sql
SELECT
    product_name,
    AI_CLASSIFY('endpoint:qwen3.5-plus', product_desc, ARRAY('electronics', 'clothing', 'food')) AS category
FROM products;
```

| product_name | category |
|-------------|---------|
| iPhone | electronics |
| Dior dress | clothing |
| Oreo cookies | food |

### Case 2: Image Classification

```sql
SELECT
    relative_path,
    AI_CLASSIFY(
        'endpoint:qwen3.5-plus',
        (GET_PRESIGNED_URL(USER VOLUME, relative_path, 36000) AS image),
        ARRAY('electronics', 'menswear', 'womenswear', 'food', 'automotive')
    ) AS classification
FROM (SHOW USER VOLUME DIRECTORY SUBDIRECTORY 'images/products');
```

### Case 3: News Classification

```sql
SELECT
    headline,
    AI_CLASSIFY('endpoint:qwen3.5-plus', headline, ARRAY('tech', 'sports', 'finance', 'entertainment')) AS topic
FROM news_articles;
```

### Case 4: Customer Support Ticket Routing

```sql
SELECT
    ticket_id,
    AI_CLASSIFY(
        'endpoint:qwen3.5-plus',
        description,
        ARRAY('payment issue', 'shipping issue', 'product quality', 'account issue', 'feature request')
    ) AS department
FROM support_tickets;
```

### Case 5: Batch Classification with options

```sql
SELECT
    product_name,
    AI_CLASSIFY(
        'endpoint:qwen3.5-plus',
        product_desc,
        ARRAY('electronics', 'clothing', 'food'),
        JSON '{"model.params":{"enable_thinking":false},"response.timeout":"300","task.concurrency":"12"}'
    ) AS category
FROM products;
```

---

## Multilingual Support

AI_CLASSIFY natively supports classification in **29+ languages** based on the model you choose, including:

| Language family | Supported languages |
|------|---------|
| CJK | Chinese, Japanese, Korean |
| Latin | English, French, Spanish, Portuguese, German, Italian |
| Southeast Asian | Vietnamese, Thai, Indonesian |
| Other | Arabic, Russian, Polish, Dutch, Turkish, and more |

### Same-language classification

Input and labels in the same language:

```sql
-- Japanese
SELECT AI_CLASSIFY('endpoint:qwen3.5-plus',
    '東京オリンピックで日本は金メダル27個を獲得しました',
    ARRAY('テクノロジー', 'スポーツ', '金融', 'エンタメ')
);
-- Returns: スポーツ

-- Arabic
SELECT AI_CLASSIFY('endpoint:qwen3.5-plus',
    'أعلن البنك المركزي عن رفع أسعار الفائدة',
    ARRAY('تقنية', 'مالية', 'رياضة', 'ترفيه')
);
-- Returns: مالية
```

### Cross-language classification

Input and labels can be in different languages:

```sql
-- Chinese input + English labels
SELECT AI_CLASSIFY('endpoint:qwen3.5-plus',
    '特斯拉发布了全新的自动驾驶系统',
    ARRAY('technology', 'sports', 'finance', 'entertainment')
);
-- Returns: technology

-- English input + Chinese labels
SELECT AI_CLASSIFY('endpoint:qwen3.5-plus',
    'Bitcoin surged past 150000 as institutional investors poured billions',
    ARRAY('科技', '体育', '金融', '娱乐')
);
-- Returns: 金融
```

---

## options Parameter

```sql
JSON '{"model.params":{"enable_thinking":false},"response.timeout":"300","task.concurrency":"12"}'
```

| Parameter | Type | Description |
|------|------|------|
| `model.params.enable_thinking` | boolean | Set to `false` to disable thinking mode for faster responses (recommended for batch classification) |
| `response.timeout` | string (seconds) | Per-call timeout |
| `task.concurrency` | string (integer) | Batch processing concurrency |

---

## NULL and Empty Input Behavior

| Input | Return value | Notes |
|------|--------|------|
| content is NULL | NULL | NULL is passed through |
| content is empty string | `""` | Returns empty string (not NULL) |
| Normal text | Matching category name | Plain string |

> ⚠️ **Note**: An empty string returns `""` rather than NULL. If you need consistent handling, add `NULLIF(result, '')` to your query.

---

## Best Practices

1. **Use descriptive category names** — Use meaningful names (e.g. "electronics" rather than "cat_1"). The model understands categories through semantic meaning.

2. **Keep the number of categories reasonable** — 2–10 categories works best. Too many categories may reduce accuracy.

3. **Disable thinking for speed** — For batch classification, set `enable_thinking:false` to significantly reduce response time.

4. **Filter before classifying** — For large tables, use `WHERE` to narrow the scope first, avoiding unnecessary model calls.

5. **Leverage cross-language capability** — Labels can be in English even when input is in another language, making downstream processing consistent.

6. **Image classification** — Pass images via `GET_PRESIGNED_URL(USER VOLUME, path, expiry) AS image`; the model classifies based on image content.

7. **Guard against empty strings** — For columns that may contain empty strings, add `WHERE content IS NOT NULL AND content != ''` before classifying.

---

## Limitations

| Item | Description |
|--------|------|
| Model parameter | An endpoint must be specified |
| Minimum labels | 1 (recommended ≥ 2; with a single label, that label is always returned) |
| Maximum labels | Recommended ≤ 20; too many reduces accuracy |
| Return value | Single label (one category name string) |
| Image input | Must use `GET_PRESIGNED_URL(...) AS image` syntax |
| Quota | Subject to AI Gateway tenant token quota limits |

---

## Error Handling

| Error scenario | Error message | Resolution |
|---------|---------|---------|
| Endpoint does not exist | `CZLH-67000 No available endpoints found` | Check that the endpoint name is correct |
| Quota exceeded | `Tenant quota exceeded` | Contact your administrator to increase quota |
| Image not found | `Failed to fetch image from URL` | Check the Volume file path |
