# Multimodal Embedding

This guide shows how to call Volcengine `doubao-embedding-vision` for text, image, and video multimodal embedding.

## 1. Multimodal embedding

Applicable models:

- `doubao-embedding-vision`

Request endpoint:

```text
POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3/embeddings/multimodal
```

This endpoint differs from OpenAI `/embeddings`. It supports text, image, and video as multimodal inputs.

### Text embedding

```bash
curl -X POST "$AI_GATEWAY_VOLC_BASE_URL/embeddings/multimodal" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-embedding-vision",
    "input": [
      {
        "type": "text",
        "text": "AI Gateway supports unified model calls, routing, and usage statistics."
      }
    ],
    "encoding_format": "float",
    "dimensions": 1024
  }'
```

### Image embedding

```bash
curl -X POST "$AI_GATEWAY_VOLC_BASE_URL/embeddings/multimodal" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-embedding-vision",
    "input": [
      {
        "type": "image_url",
        "image_url": {
          "url": "https://example.com/product.png"
        }
      }
    ],
    "encoding_format": "float",
    "dimensions": 1024
  }'
```

### Mixed video, image, and text embedding

```bash
curl -X POST "$AI_GATEWAY_VOLC_BASE_URL/embeddings/multimodal" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-embedding-vision",
    "input": [
      {
        "type": "video_url",
        "video_url": {
          "url": "https://example.com/demo.mp4"
        }
      },
      {
        "type": "image_url",
        "image_url": {
          "url": "https://example.com/product.png"
        }
      },
      {
        "type": "text",
        "text": "Generate a unified vector from the video and image."
      }
    ],
    "encoding_format": "float",
    "dimensions": 1024
  }'
```

### Request fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | string | Yes | Multimodal embedding model name, for example `doubao-embedding-vision`. |
| `input` | array | Yes | Array of content to embed. |
| `input[].type` | string | Yes | Input type: `text`, `image_url`, or `video_url`. |
| `input[].text` | string | Conditionally required | Text content. |
| `input[].image_url.url` | string | Conditionally required | Image URL. |
| `input[].video_url.url` | string | Conditionally required | Video URL. |
| `encoding_format` | string | No | Vector encoding format. `float` is the common choice. |
| `dimensions` | integer | No | Output vector dimension. Support for variable dimensions depends on the model detail page. |

Response example:

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
  "model": "doubao-embedding-vision",
  "usage": {
    "prompt_tokens": 32,
    "total_tokens": 32
  }
}
```

Vector store integration guidelines:

- Vectors used for indexing and querying must use the same model and the same vector dimension.
- If you set `dimensions`, fix the dimension before building the index and do not change it later.
- Image and video URLs must be publicly accessible. Use stable object storage addresses.
- Control input size per batch to avoid oversized requests or timeouts.
