# Alibaba Cloud Models: Overview

This guide shows how to call Alibaba Cloud Bailian models through AI Gateway. AI Gateway exposes a unified endpoint, API key, access control, routing, and usage statistics; you do not need to call Alibaba Cloud Bailian endpoints directly.

Create an API key in **API Key Management** before calling, and confirm the key has permission to call the target model.

## 1. Base addresses

Alibaba Cloud Bailian models use two main address types in AI Gateway.

| Type | Base URL / Endpoint | Use case |
| --- | --- | --- |
| OpenAI-compatible base URL | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1` | Chat Completions, Responses, text embedding |
| OpenAI Chat Completions | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/chat/completions` | Qwen, DeepSeek, GLM, Kimi, MiniMax, and other text and visual understanding models |
| Responses API | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/responses` | Models that support the Responses protocol |
| Anthropic Messages | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/messages` | Models with an Anthropic-type endpoint |
| Text Embedding | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/embeddings` | Qwen Text Embedding V4 and other text embedding models |
| Qwen3 VL Embedding | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v1/services/embeddings/multimodal-embedding/multimodal-embedding` | `qwen3-vl-embedding` multimodal embedding model |
| HappyHorse video generation | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v1/services/aigc/video-generation/video-synthesis` | `happyhorse-1.0-t2v`, `happyhorse-1.0-i2v`, `happyhorse-1.0-r2v` |

Notes:

- Alibaba Cloud Bailian text models, Tencent TokenHub text models, and other non-Volcengine text models use `/gateway/v1/...`.
- Do not use `/gateway/api/v1/chat/completions` for Alibaba Cloud text models.
- HappyHorse video generation and Qwen3 VL Embedding are service-based interfaces; their paths contain `/gateway/api/v1/services/...`.
- Volcengine models use `/gateway/api/v3/...`. Do not mix them with Alibaba Cloud Bailian paths.

## 2. Authentication

OpenAI-compatible endpoints use `Authorization: Bearer <API_KEY>`.

```http
Authorization: Bearer <API_KEY>
Content-Type: application/json
```

Anthropic Messages-compatible endpoints use `x-api-key`.

```http
x-api-key: <API_KEY>
anthropic-version: 2023-06-01
Content-Type: application/json
```

`<API_KEY>` is the key created in AI Gateway's **API Key Management** page, not the DashScope API key from your Alibaba Cloud account.

## 3. Models and interface types

| Model category | Example models | Recommended interface |
| --- | --- | --- |
| Qwen text / reasoning | `qwen3.7-max`, `qwen3.6-max-preview`, `qwen3-max`, `qwen3.6-plus`, `qwen3.5-plus`, `qwen3.6-flash`, `qwen3.5-flash` | OpenAI Chat Completions; Responses when supported |
| Third-party text models | `MiniMax/MiniMax-M2.7`, `MiniMax-M2.5`, `deepseek-r1`, `deepseek-v3.2`, `deepseek-v4-flash`, `deepseek-v4-pro`, `glm-4.7`, `glm-5`, `glm-5.1`, `kimi-k2.5`, `kimi-k2.6` | OpenAI Chat Completions |
| Visual understanding | Qwen multimodal models that accept image input | OpenAI Chat Completions with text and images in `messages.content` |
| Text embedding | Qwen Text Embedding V4 and others | OpenAI Embeddings |
| Multimodal embedding | `qwen3-vl-embedding` | Qwen3 VL Embedding service-based interface |
| Video generation | `happyhorse-1.0-t2v`, `happyhorse-1.0-i2v`, `happyhorse-1.0-r2v` | HappyHorse video generation service-based interface |

Model names are authoritative as shown on the **Model Market** detail page. Some models may include a namespace in the endpoint, for example `qwen/qwen3.7-max`. Keep the exact identifier when copying from examples.

## 4. General call steps

1. Go to **Model Market**.
2. Search for the target model, for example `qwen3.7-max` or `happyhorse-1.0-t2v`.
3. Open the model detail page and review the endpoint status, service provider, billing method, and call examples.
4. In **API Key Management**, create or select an API key and enable the target model.
5. Select the correct endpoint and request body based on the model type.
6. After sending a request, review call volume, tokens, costs, and errors in **Usage Statistics**.

## 5. Environment variables

```bash
export AI_GATEWAY_OPENAI_BASE_URL="https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1"
export AI_GATEWAY_SERVICE_BASE_URL="https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v1"
export API_KEY="<your-api-key>"
```

The examples below use these environment variables.

## 6. Minimal working examples

### Chat Completions

```bash
curl -X POST "$AI_GATEWAY_OPENAI_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen/qwen3.7-max",
    "messages": [
      {"role": "user", "content": "Describe AI Gateway in one sentence."}
    ]
  }'
```

### Embedding

```bash
curl -X POST "$AI_GATEWAY_OPENAI_BASE_URL/embeddings" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen/text-embedding-v4",
    "input": "AI Gateway provides unified model calls, routing, and usage statistics.",
    "encoding_format": "float"
  }'
```

### HappyHorse video generation

```bash
curl -X POST "$AI_GATEWAY_SERVICE_BASE_URL/services/aigc/video-generation/video-synthesis" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-DashScope-Async: enable" \
  -d '{
    "model": "happyhorse-1.0-t2v",
    "input": {
      "prompt": "A 5-second product demo video showing data flowing into AI Gateway and being routed."
    },
    "parameters": {
      "size": "1280*720"
    }
  }'
```

## 7. Common notes

- Endpoint addresses may vary by deployment region. Use the examples on the Model Market detail page as the authoritative reference.
- OpenAI-compatible, Anthropic Messages, and DashScope service-based endpoints have different request body structures. Do not reuse the same request body by simply swapping the model name.
- Image, video, and file URLs in multimodal inputs must be accessible by the model provider. Local paths, private network addresses, and browser-session-dependent URLs typically do not work.
- Advanced capabilities such as structured output, tool calling, web search, and extended thinking are not supported by all models. Check the model detail page and the relevant sections of this guide.
- If a request fails, check the `code`, `message`, and `request_id` fields in the response body. Use the error code reference and usage statistics to investigate.
