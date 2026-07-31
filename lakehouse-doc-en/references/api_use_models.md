# Using Models

After selecting a model in Model Market, you can view the endpoint information and call examples for that model and copy the code directly.

AI Gateway supports multiple model types and interface protocols. When integrating, do not select an endpoint based solely on the provider name. You also need to consider the model type and the endpoint's interface type to choose the correct endpoint.

## 1. Find a model endpoint

Go to **Model Market**, click any model to open the detail page, and you will see:

- **Endpoint Management**: Lists the available endpoint names, service providers, status, and billing information for the model.
- **Call Examples**: Provides ready-to-use code examples in curl and Python.

Endpoint names typically follow the format `{provider}@{model_name}@{interface_type}`.

Examples:

- `aliyun_bailian_bj@qwen/qwen3.7-max@open_ai`: Alibaba Cloud Bailian Beijing, OpenAI-compatible interface.
- `volcengine_bj@doubao-seedance-2.0@task`: Volcengine Seedance video task interface.

Before calling, confirm three things:

1. The model name.
2. The endpoint provider.
3. The interface type: `open_ai`, `anthropic`, video generation, image generation, embedding, and so on.

## 2. Endpoint overview

Common call methods in AI Gateway:

| Model type | Applicable models / providers | Endpoint | Auth |
| --- | --- | --- | --- |
| OpenAI-compatible text models (non-Volcengine) | Qwen, DeepSeek, GLM, Kimi, MiniMax, Tencent TokenHub DeepSeek, and others | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/chat/completions` | `Authorization: Bearer <API_KEY>` |
| Anthropic-compatible text models (non-Volcengine) | Models with `anthropic` endpoint type | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/messages` | `x-api-key: <API_KEY>` |
| HappyHorse video generation | `happyhorse-1.0-t2v`, `happyhorse-1.0-i2v`, `happyhorse-1.0-r2v` | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v1/services/aigc/video-generation/video-synthesis` | `Authorization: Bearer <API_KEY>` |
| Alibaba Cloud text embedding | Qwen Text Embedding V4 and other text embedding models | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/embeddings` | `Authorization: Bearer <API_KEY>` |
| Alibaba Cloud multimodal embedding | `qwen3-vl-embedding` | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v1/services/embeddings/multimodal-embedding/multimodal-embedding` | `Authorization: Bearer <API_KEY>` |
| Volcengine text / visual understanding | Doubao text, code, translation, visual understanding models | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3/chat/completions` | `Authorization: Bearer <API_KEY>` |
| Volcengine Seedream image generation | `doubao-seedream-5.0-lite`, `doubao-seedream-4.5`, `doubao-seedream-4.0` | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3/images/generations` | `Authorization: Bearer <API_KEY>` |
| Volcengine Seedance video generation | `doubao-seedance-2.0`, `doubao-seedance-2.0-fast`, `doubao-seedance-1.5-pro`, `doubao-seedance-1.0-pro`, `doubao-seedance-1.0-pro-fast` | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3/contents/generations/tasks` | `Authorization: Bearer <API_KEY>` |
| Volcengine multimodal embedding | `doubao-embedding-vision` | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3/embeddings/multimodal` | `Authorization: Bearer <API_KEY>` |
| Volcengine 3D generation | `doubao-seed3d-2.0`, `Hyper3d-Gen2`, `Hitem3d-2.0` | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3/contents/generations/tasks` | `Authorization: Bearer <API_KEY>` |

Notes:

- Endpoint addresses vary by deployment region. Use the actual example code in the Model Market detail page.
- Text models require you to distinguish between OpenAI-compatible and Anthropic-compatible protocols.
- HappyHorse and Qwen3 VL Embedding are service-based interfaces with paths containing `/gateway/api/v1/services/...`.
- Volcengine models use `/gateway/api/v3/...`.

## 3. curl calls

### OpenAI-compatible interface

For Qwen, DeepSeek, GLM, Kimi, MiniMax, Tencent TokenHub DeepSeek, and other non-Volcengine text models.

```bash
curl -X POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen/qwen3.7-max",
    "messages": [
      {"role": "user", "content": "hello"}
    ]
  }'
```

### Anthropic-compatible interface

For the Claude series or models with `anthropic` endpoint type.

```bash
curl -X POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/messages \
  -H "x-api-key: $API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "anthropic/claude-opus-4.6",
    "messages": [
      {"role": "user", "content": "hello"}
    ],
    "max_tokens": 256
  }'
```

### HappyHorse video generation

```bash
curl -X POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v1/services/aigc/video-generation/video-synthesis \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "happyhorse-1.0-t2v",
    "input": {
      "prompt": "Generate a 5-second video: white data streams flow through a modern office and converge into the AI Gateway logo."
    }
  }'
```

### Alibaba Cloud text embedding

```bash
curl -X POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/embeddings \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen/text-embedding-v4",
    "input": "AI Gateway centrally manages model calls, routing, and usage statistics.",
    "encoding_format": "float"
  }'
```

### Qwen3 VL Embedding

```bash
curl -X POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v1/services/embeddings/multimodal-embedding/multimodal-embedding \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-vl-embedding",
    "input": [
      {
        "type": "image_url",
        "image_url": {"url": "https://example.com/product.png"}
      },
      {
        "type": "text",
        "text": "Product main image"
      }
    ]
  }'
```

### Volcengine Doubao text model

```bash
curl -X POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seed-2.0-pro",
    "messages": [
      {"role": "user", "content": "Describe the role of AI Gateway."}
    ],
    "stream": false
  }'
```

### Volcengine Seedream image generation

```bash
curl -X POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3/images/generations \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seedream-4.0",
    "prompt": "A product illustration of a modern data platform console, clean, professional, tech aesthetic",
    "size": "1024x1024",
    "n": 1
  }'
```

### Volcengine Seedance video generation

```bash
curl -X POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3/contents/generations/tasks \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seedance-2.0",
    "content": [
      {
        "type": "text",
        "text": "Generate a 5-second video: data streams converge into an intelligent hub against a city night skyline."
      }
    ]
  }'
```

### Volcengine multimodal embedding

```bash
curl -X POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3/embeddings/multimodal \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-embedding-vision",
    "input": [
      {
        "type": "image_url",
        "image_url": {"url": "https://example.com/product.png"}
      },
      {
        "type": "text",
        "text": "Product main image"
      }
    ]
  }'
```

### Volcengine 3D generation

```bash
curl -X POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3/contents/generations/tasks \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seed3d-2.0",
    "content": [
      {
        "type": "text",
        "text": "Generate a low-poly style tech-aesthetic robot 3D model."
      }
    ]
  }'
```

## 4. Python calls

### OpenAI-compatible interface

Use the `openai` library and point `base_url` to the AI Gateway endpoint:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1",
    api_key="<your-api-key>",
)

response = client.chat.completions.create(
    model="qwen/qwen3.7-max",
    messages=[{"role": "user", "content": "hello"}],
)
print(response.choices[0].message.content)
```

### Volcengine Doubao text model

Volcengine Doubao text models also use the OpenAI SDK, but `base_url` must point to the Volcengine path:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3",
    api_key="<your-api-key>",
)

response = client.chat.completions.create(
    model="doubao-seed-2.0-pro",
    messages=[{"role": "user", "content": "hello"}],
)
print(response.choices[0].message.content)
```

### Anthropic-compatible interface

Use `requests` to call the Anthropic Messages interface directly:

```python
import requests

url = "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/messages"
headers = {
    "x-api-key": "<your-api-key>",
    "anthropic-version": "2023-06-01",
    "Content-Type": "application/json",
}
payload = {
    "model": "anthropic/claude-opus-4.6",
    "messages": [{"role": "user", "content": "hello"}],
    "max_tokens": 256,
}

resp = requests.post(url, headers=headers, json=payload, timeout=60)
print(resp.status_code)
print(resp.text)
```

You can also use the official `anthropic` SDK with `base_url` pointing to the AI Gateway address:

```python
import anthropic

client = anthropic.Anthropic(
    base_url="https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1",
    api_key="<your-api-key>",
)

message = client.messages.create(
    model="anthropic/claude-opus-4.6",
    max_tokens=256,
    messages=[{"role": "user", "content": "hello"}],
)
print(message.content)
```

## 5. Notes

- Endpoint addresses vary by deployment region. Use the actual example code in Model Market.
- OpenAI-compatible interfaces use `Authorization: Bearer <API_KEY>`.
- Anthropic-compatible interfaces use `x-api-key: <API_KEY>` and require `anthropic-version`.
- The model name must exactly match the model identifier in the Model Market endpoint.
- Create the API key in **API Key Management** in advance and enable the target model.
- Volcengine text, image, video, 3D, and multimodal embedding all use `/gateway/api/v3/...`.
- Non-Volcengine text OpenAI / Anthropic protocols use `/gateway/v1/...`.
- Non-Volcengine service-based interfaces such as HappyHorse and Qwen3 VL Embedding use `/gateway/api/v1/services/...`.
- Video, image, and 3D generation tasks may return an async task ID. Check the model detail page for task status and query methods.

## 7. Related documentation

- [Quick start](quickstart.md): Create an API key and configure routing.
- [Model pricing](pricing-ai-gateway.md): Billing rates for each model.
- [Call LLMs with SQL](lakehouse-ai-sql-analysis.md): Call models through AI_COMPLETE in Lakehouse SQL.
