# Chat API Compatible Calls

This guide covers Chat API / Chat Completions calls for Volcengine Doubao text, code, character, translation, and visual understanding models.

For new integrations, use **Responses API**. Chat API is suited for these scenarios:

- Your existing code is written against OpenAI Chat Completions and you want to migrate to AI Gateway with minimal changes.
- Your workload only needs text generation, visual understanding, basic structured output, or function calling.
- The target model's detail page does not yet show Responses examples.

Use Responses API if you need web search, image processing, private knowledge base search, MCP, or context caching.

## 1. Text, code, translation, and character models

Text-class models support Chat Completions, but this is not the preferred interface for new Volcengine workloads.

```text
POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3/chat/completions
```

### Basic call

```bash
curl -X POST "$AI_GATEWAY_VOLC_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seed-2.0-pro",
    "messages": [
      {
        "role": "system",
        "content": "You are a professional, accurate, and concise enterprise AI assistant."
      },
      {
        "role": "user",
        "content": "Summarize the value of AI Gateway in three points."
      }
    ],
    "temperature": 0.7,
    "top_p": 0.8,
    "max_tokens": 1024,
    "stream": false
  }'
```

Python example:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3",
    api_key="<your-api-key>",
)

completion = client.chat.completions.create(
    model="doubao-seed-2.0-pro",
    messages=[
        {"role": "system", "content": "You are a professional, accurate, and concise enterprise AI assistant."},
        {"role": "user", "content": "Summarize the value of AI Gateway in three points."},
    ],
    temperature=0.7,
    top_p=0.8,
    max_tokens=1024,
)

print(completion.choices[0].message.content)
```

### Request fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | string | Yes | Model name, for example `doubao-seed-2.0-pro`. Use the identifier from the Model Market detail page. |
| `messages` | array | Yes | Conversation message list. Each message contains `role` and `content`. |
| `stream` | boolean | No | Whether to enable streaming output. |
| `stream_options` | object | No | Streaming configuration. Common use: `include_usage` to return usage at the end of the stream. |
| `temperature` | number | No | Sampling temperature. Higher values produce more varied output; lower values produce more stable output. |
| `top_p` | number | No | Nucleus sampling parameter. Do not adjust both `temperature` and `top_p` by large amounts at the same time. |
| `max_tokens` | integer | No | Maximum output token count. |
| `stop` | string / array | No | Stop generation string. |
| `presence_penalty` | number | No | Topic repetition penalty. |
| `frequency_penalty` | number | No | Word frequency repetition penalty. |
| `response_format` | object | No | Structured output configuration for JSON output. |
| `tools` | array | No | Tool definitions for function calling. |
| `tool_choice` | string / object | No | Tool selection strategy: `auto`, `none`, or a specific tool. |
| `parallel_tool_calls` | boolean | No | Whether to allow parallel tool calls. Depends on the model. |
| `seed` | integer | No | Random seed to improve reproducibility. Depends on the model. |
| `user` | string | No | End-user identifier for auditing and tracking. |

Recommendations:

- For deterministic tasks such as code generation, SQL generation, and translation, use a low `temperature` (for example `0` to `0.3`).
- For creative writing and marketing copy, a higher `temperature` is appropriate.
- Set `max_tokens` explicitly in production to avoid uncontrolled costs and latency.
- Advanced fields such as `tools`, `response_format`, and `seed` are not supported by all models. Verify against the model detail page and test before deploying.

### Streaming output

```bash
curl -N -X POST "$AI_GATEWAY_VOLC_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seed-2.0-pro",
    "messages": [
      {
        "role": "user",
        "content": "Explain the AI Gateway integration process step by step."
      }
    ],
    "stream": true,
    "stream_options": {
      "include_usage": true
    }
  }'
```

Streaming responses return SSE events. The client reads `data:` lines and closes the connection after the end event.

### Structured output

Use `response_format` when your application needs stable result parsing.

```bash
curl -X POST "$AI_GATEWAY_VOLC_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seed-2.0-pro",
    "messages": [
      {
        "role": "system",
        "content": "Output only valid JSON. Do not output Markdown."
      },
      {
        "role": "user",
        "content": "Extract ticket information: customer reports model call error 429, affecting production reports."
      }
    ],
    "response_format": {
      "type": "json_object"
    }
  }'
```

Validate JSON parsing and schema on the application side.

### Tool calling

```json
{
  "model": "doubao-seed-2.0-pro",
  "messages": [
    {
      "role": "user",
      "content": "Query the shipping status for order 202606150001."
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
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
    }
  ],
  "tool_choice": "auto"
}
```

Typical tool calling flow:

1. The client sends the user question and tool definitions.
2. The model returns tool call intent and arguments.
3. The application executes the real tool.
4. The application passes the tool result as a `tool` message to the model.
5. The model generates the final answer based on the tool result.

## 2. Visual understanding models

Applicable models:

- `doubao-seed-1.6-vision`
- `doubao-1.5-vision-pro`

Visual understanding models use Chat Completions. Pass text and images in `messages.content`.

```bash
curl -X POST "$AI_GATEWAY_VOLC_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seed-1.6-vision",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Identify the main content in the image and output JSON: subject, color, scene, and whether it contains text."
          },
          {
            "type": "image_url",
            "image_url": {
              "url": "https://example.com/demo.png"
            }
          }
        ]
      }
    ],
    "response_format": {
      "type": "json_object"
    }
  }'
```

Multi-image comparison example:

```json
{
  "model": "doubao-1.5-vision-pro",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "Compare the differences between the products in these two images."},
        {"type": "image_url", "image_url": {"url": "https://example.com/a.png"}},
        {"type": "image_url", "image_url": {"url": "https://example.com/b.png"}}
      ]
    }
  ]
}
```

Notes:

- Image URLs must be accessible by the model service. Do not use local paths.
- Image count, size, and format limits depend on the model detail page.
- Multiple images increase token consumption, cost, and latency. Compress images and limit the count in production.
