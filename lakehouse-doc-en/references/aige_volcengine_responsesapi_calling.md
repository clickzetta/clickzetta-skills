# Volcengine Responses API

This guide shows how to call Volcengine models through AI Gateway using Responses API. For new Volcengine integrations covering text generation, visual understanding, structured output, and tool calling, use Responses API rather than Chat API.

## 1. Request endpoint

```text
POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3/responses
```

Request headers:

```http
Authorization: Bearer <API_KEY>
Content-Type: application/json
```

## 2. Why prefer Responses API

Responses API covers a more complete set of capabilities and is the intended interface for text, multimodal input, tool calling, and future advanced features. Chat API is better suited for compatibility with existing OpenAI Chat Completions code.

| Capability | Chat API | Responses API |
| --- | --- | --- |
| Text generation | Supported | Supported |
| Visual understanding | Supported | Supported |
| Structured output | Beta | Beta |
| Function calling | Supported | Supported |
| Web search | Not supported | Supported |
| Image processing | Not supported | Supported |
| Knowledge search | Not supported | Supported |
| Cloud-deployed MCP | Not supported | Supported |
| Context caching | Not supported | Supported; specific model versions depend on Model Market |

Guidance:

- Use Responses API by default for new workloads.
- Existing Chat Completions code can continue using Chat API and migrate later.
- Use Responses API when you need web search, image processing, knowledge search, MCP, or context caching.
- If the Model Market detail page has no Responses example, follow the model detail page.

## 3. Basic text generation

```bash
curl -X POST "$AI_GATEWAY_VOLC_BASE_URL/responses" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seed-2.0-lite",
    "input": "Summarize the three core capabilities of AI Gateway.",
    "max_output_tokens": 512
  }'
```

Python example:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3",
    api_key="<your-api-key>",
)

response = client.responses.create(
    model="doubao-seed-2.0-lite",
    input="Summarize the three core capabilities of AI Gateway.",
    max_output_tokens=512,
)

print(response.output_text)
```

## 4. Request fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | string | Yes | Model name. Use the identifier from the Model Market detail page, for example `doubao-seed-2.0-lite`. |
| `input` | string / array | Yes | Input content. Can be a string or a multi-turn, multimodal array. |
| `instructions` | string | No | System instructions, similar to the `system` message in Chat API. |
| `stream` | boolean | No | Whether to enable streaming output. |
| `temperature` | number | No | Sampling temperature. |
| `top_p` | number | No | Nucleus sampling parameter. |
| `max_output_tokens` | integer | No | Maximum output token count. |
| `response_format` | object | No | Structured output configuration. |
| `tools` | array | No | Tool definitions. |
| `tool_choice` | string / object | No | Tool selection strategy. |
| `parallel_tool_calls` | boolean | No | Whether to allow parallel tool calls. Depends on the model. |
| `metadata` | object | No | Custom business metadata. |
| `previous_response_id` | string | No | Links to the previous response turn. Depends on the model and gateway. |
| `store` | boolean | No | Whether to store the response. Set based on compliance requirements in enterprise scenarios. |

## 5. input formats

### String input

```json
{
  "model": "doubao-seed-2.0-lite",
  "input": "Translate this sentence into English: AI Gateway supports unified model governance.",
  "max_output_tokens": 512
}
```

### Multi-turn input

```json
{
  "model": "doubao-seed-2.0-pro",
  "instructions": "You are an enterprise knowledge base assistant. Keep answers concise and accurate.",
  "input": [
    {
      "role": "user",
      "content": "What capabilities does AI Gateway support?"
    },
    {
      "role": "assistant",
      "content": "Supports unified model access, API key management, routing, and usage statistics."
    },
    {
      "role": "user",
      "content": "Please add BYOK and permission management."
    }
  ]
}
```

### Visual understanding input

Models that support visual input accept text and images in `input`.

```bash
curl -X POST "$AI_GATEWAY_VOLC_BASE_URL/responses" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seed-1.6-vision",
    "input": [
      {
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": "Identify the main content in the image and output JSON."
          },
          {
            "type": "input_image",
            "image_url": "https://example.com/demo.png"
          }
        ]
      }
    ],
    "max_output_tokens": 1024
  }'
```

Notes:

- The image URL must be accessible by the model service. Do not use local paths.
- Image count, size, and format limits depend on the model detail page.
- Visual understanding tasks should also use Responses API.

## 6. Streaming output

```bash
curl -N -X POST "$AI_GATEWAY_VOLC_BASE_URL/responses" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seed-2.0-pro",
    "input": "Explain the AI Gateway integration process step by step.",
    "stream": true,
    "max_output_tokens": 1024
  }'
```

Streaming returns SSE events. The client reads incremental text, tool calls, and end events by event type.

## 7. Structured output

Structured output is still in beta. To get stable JSON, use `response_format` and explicitly instruct in `instructions` to output only JSON.

```bash
curl -X POST "$AI_GATEWAY_VOLC_BASE_URL/responses" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seed-2.0-pro",
    "instructions": "Output only valid JSON. Do not output Markdown.",
    "input": "Extract ticket information: customer reports API call error 429, affecting production reports. Fields: priority, category, summary.",
    "response_format": {
      "type": "json_object"
    },
    "max_output_tokens": 512
  }'
```

Validate JSON parsing and schema on the application side.

## 8. Tool calling

Responses API supports function calling for querying orders, retrieving from a knowledge base, calling internal services, and similar tasks.

```json
{
  "model": "doubao-seed-2.0-pro",
  "input": "Query the shipping status for order 202606150001.",
  "tools": [
    {
      "type": "function",
      "name": "get_order_status",
      "description": "Query shipping status by order ID",
      "parameters": {
        "type": "object",
        "properties": {
          "order_id": {
            "type": "string",
            "description": "Order ID"
          }
        },
        "required": ["order_id"]
      }
    }
  ],
  "tool_choice": "auto"
}
```

Basic flow:

1. The client sends the user question and tool definitions.
2. The model returns tool call intent and arguments.
3. The application executes the real tool.
4. The application passes the tool result back to the model.
5. The model generates the final answer based on the tool result.

## 9. Advanced capabilities

Responses API is the recommended interface for future Volcengine advanced capabilities. The following require confirmation against Model Market and endpoint details:

| Capability | Description |
| --- | --- |
| Web Search | Real-time web search for Q&A that needs current information. |
| Image Process | Image editing, analysis, or multimodal processing. |
| Knowledge Search | Private knowledge base search for enterprise Q&A. |
| MCP | Cloud-deployed MCP tools for unified external tool integration. |
| Context Cache | Context caching for repeated long contexts and multi-turn long sessions. |

When you need these capabilities, choose Responses API and follow the model detail page examples.
