# Embedding Models

Alibaba Cloud Bailian supports both text embedding and multimodal embedding in AI Gateway. The two interface types have different endpoints and request bodies.

## 1. Interface overview

| Type | Applicable models | Endpoint |
| --- | --- | --- |
| Text embedding | Qwen Text Embedding V4 and others | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/embeddings` |
| Multimodal embedding | `qwen3-vl-embedding` | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v1/services/embeddings/multimodal-embedding/multimodal-embedding` |

Text embedding uses the OpenAI-compatible protocol. Qwen3 VL Embedding uses the DashScope service-based multimodal embedding protocol.

## 2. Text embedding

### Request endpoint

```text
POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/embeddings
```

Request headers:

```http
Authorization: Bearer <API_KEY>
Content-Type: application/json
```

### Request example

```bash
curl -X POST "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/embeddings" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen/text-embedding-v4",
    "input": [
      "AI Gateway supports unified model calls.",
      "Model routing can follow price, throughput, or latency strategies."
    ],
    "encoding_format": "float"
  }'
```

Python example:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1",
    api_key="<your-api-key>",
)

response = client.embeddings.create(
    model="qwen/text-embedding-v4",
    input=[
        "AI Gateway supports unified model calls.",
        "Model routing can follow price, throughput, or latency strategies.",
    ],
    encoding_format="float",
)

vectors = [item.embedding for item in response.data]
print(len(vectors), len(vectors[0]))
```

### Request fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | string | Yes | Embedding model name. Use the identifier from the Model Market detail page, for example `qwen/text-embedding-v4`. |
| `input` | string / array | Yes | Text to embed. Pass a single string or a string array for batch processing. |
| `encoding_format` | string | No | Vector encoding format. `float` is the common choice. |
| `dimensions` | integer | No | Output vector dimension. Available only when the model supports variable dimensions. |
| `user` | string | No | End-user identifier, for auditing or tracking on the application side. |

### Response fields

```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "index": 0,
      "embedding": [0.0123, -0.0456, 0.0789]
    }
  ],
  "model": "qwen/text-embedding-v4",
  "usage": {
    "prompt_tokens": 20,
    "total_tokens": 20
  }
}
```

| Field | Description |
| --- | --- |
| `data[].embedding` | Vector array. |
| `data[].index` | Corresponds to the position in the input array. |
| `usage.prompt_tokens` | Input token count. |
| `usage.total_tokens` | Total token count. |

## 3. Qwen3 VL Embedding

`qwen3-vl-embedding` is suited for embedding images, text, or combined image-text pairs. Use cases include text-to-image search, image-to-image search, and mixed image-text retrieval.

### Request endpoint

```text
POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v1/services/embeddings/multimodal-embedding/multimodal-embedding
```

Request headers:

```http
Authorization: Bearer <API_KEY>
Content-Type: application/json
```

### Text embedding example

```bash
curl -X POST "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v1/services/embeddings/multimodal-embedding/multimodal-embedding" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-vl-embedding",
    "input": {
      "contents": [
        {
          "text": "Product main image of a white sneaker"
        }
      ]
    }
  }'
```

### Image embedding example

```bash
curl -X POST "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v1/services/embeddings/multimodal-embedding/multimodal-embedding" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-vl-embedding",
    "input": {
      "contents": [
        {
          "image": "https://example.com/product.png"
        }
      ]
    }
  }'
```

### Combined image-text embedding example

```bash
curl -X POST "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v1/services/embeddings/multimodal-embedding/multimodal-embedding" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-vl-embedding",
    "input": {
      "contents": [
        {
          "text": "Product main image, white sneaker, side view",
          "image": "https://example.com/product.png"
        }
      ]
    }
  }'
```

### Request fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | string | Yes | Use the multimodal embedding model name from Model Market, for example `qwen3-vl-embedding`. |
| `input` | object | Yes | Input object. |
| `input.contents` | array | Yes | Array of content to embed. |
| `input.contents[].text` | string | No | Text content. |
| `input.contents[].image` | string | No | Image URL. |
| `parameters` | object | No | Extension parameters. Supported fields depend on the model detail page. |

Notes:

- `text` and `image` can be used individually or together.
- The image URL must be accessible by the model service.
- In production, upload images to a stable, publicly accessible object storage bucket and pass the URL.

## 4. Vector store integration

After embedding, you typically write vectors to a vector database or search engine. Follow these guidelines:

- Vectors indexed and vectors queried must use the same model.
- If the model supports custom `dimensions`, fix the dimension before building the index and do not change it later.
- Whether text and image retrieval can share the same index depends on whether the model maps text and images to the same vector space.
- When indexing, store the original text, image URL, business primary key, model name, vector dimension, and generation time to make index rebuilds easier.
- Control the input size per batch when generating embeddings in bulk to avoid oversized requests or timeouts.

## 5. Common errors

| Issue | Possible cause | Resolution |
| --- | --- | --- |
| Vector dimension mismatch with the vector store | Changed model or `dimensions` | Rebuild the index using the same model |
| Image cannot be embedded | Image URL inaccessible, unsupported format, or file too large | Use a publicly accessible URL and compress the image to within model limits |
| Inconsistent retrieval quality | Text too short, noisy, or model inconsistency between indexing and querying | Clean text, add key fields, and ensure the same model is used for both indexing and querying |
| Batch request fails | Too many inputs per request or request body too large | Send smaller batches and add retry logic |
