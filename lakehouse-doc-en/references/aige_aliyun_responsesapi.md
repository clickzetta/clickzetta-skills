# Responses API

Responses API is OpenAI's next-generation response interface that unifies text, multimodal input, structured output, and tool calling. Some Alibaba Cloud Bailian models support Responses API. When calling through AI Gateway, use the AI Gateway endpoint and API key.

If the Model Market detail page does not show a Responses example, use Chat Completions instead.

## 1. Request endpoint

```text
POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/responses
```

Request headers:

```http
Authorization: Bearer <API_KEY>
Content-Type: application/json
```

## 2. Basic request example

```bash
curl -X POST "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/responses" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen/qwen3.7-max",
    "input": "Summarize the three core capabilities of AI Gateway."
  }'
```

Python example:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1",
    api_key="<your-api-key>",
)

response = client.responses.create(
    model="qwen/qwen3.7-max",
    input="Summarize the three core capabilities of AI Gateway.",
)

print(response.output_text)
```

## 3. Request fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | string | Yes | Model name. Use the identifier copied from the Model Market detail page. |
| `input` | string / array | Yes | User input. Can be a simple string or a multi-turn, multimodal content array. |
| `instructions` | string | No | Similar to the `system` instruction in Chat Completions. Sets model behavior. |
| `stream` | boolean | No | Whether to enable streaming output. |
| `temperature` | number | No | Sampling temperature. Higher values produce more random output. |
| `top_p` | number | No | Nucleus sampling parameter. |
| `max_output_tokens` | integer | No | Maximum output token count. Responses API uses this field to control output length. |
| `metadata` | object | No | Custom business metadata for auditing, tracking, or statistics. |
| `response_format` | object | No | Structured output configuration. Support depends on the model. |
| `tools` | array | No | Tool definition list. |
| `tool_choice` | string / object | No | Tool selection strategy. |
| `parallel_tool_calls` | boolean | No | Whether to allow parallel tool calls. Support depends on the model. |
| `previous_response_id` | string | No | Links to the previous Responses turn. Support depends on the gateway and model. |
| `store` | boolean | No | Whether to store the response. Set based on your compliance policy in enterprise scenarios. |

## 4. input formats

### String input

Suited for single-turn text tasks.

```json
{
  "model": "qwen/qwen3.7-max",
  "input": "Translate this sentence into English: AI Gateway supports unified model governance."
}
```

### Multi-turn input

```json
{
  "model": "qwen/qwen3.7-max",
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
      "content": "Please organize these capabilities into a table."
    }
  ]
}
```

### Multimodal input

Models that support multimodal input accept text and images in `content`.

```json
{
  "model": "qwen/qwen3.6-plus",
  "input": [
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "Identify the main objects in the image and output JSON."
        },
        {
          "type": "input_image",
          "image_url": "https://example.com/image.png"
        }
      ]
    }
  ]
}
```

Multimodal field support, image count, and size limits depend on the model detail page.

## 5. Streaming output

```bash
curl -N -X POST "$AI_GATEWAY_OPENAI_BASE_URL/responses" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen/qwen3.7-max",
    "input": "Explain the AI Gateway integration process step by step.",
    "stream": true,
    "max_output_tokens": 1024
  }'
```

The client reads output as SSE events. Different SDKs wrap Responses streaming events differently. Encapsulate the parsing logic separately in your application code.

## 6. Structured output

```json
{
  "model": "qwen/qwen3.7-max",
  "instructions": "Output only valid JSON. Do not output Markdown.",
  "input": "Extract ticket information: customer reports API call error 429, affecting production.",
  "response_format": {
    "type": "json_object"
  }
}
```

Validate the JSON Schema on the application side to avoid downstream errors from unexpected model output.

## 7. Tool calling

```json
{
  "model": "qwen/qwen3.7-max",
  "input": "Query the model call cost for customer c_1001 over the past 7 days.",
  "tools": [
    {
      "type": "function",
      "name": "query_customer_cost",
      "description": "Query customer model call costs",
      "parameters": {
        "type": "object",
        "properties": {
          "customer_id": {
            "type": "string"
          },
          "days": {
            "type": "integer"
          }
        },
        "required": ["customer_id", "days"]
      }
    }
  ],
  "tool_choice": "auto"
}
```

The basic tool calling flow is the same as Chat Completions: the model first returns a tool call intent, the application executes the tool, then passes the result back to the model for the final answer.

## 8. Response parsing

The Responses API response structure differs from Chat Completions. The SDK typically exposes `output_text` directly. In raw JSON, iterate over `output`.

Example structure:

```json
{
  "id": "resp_xxx",
  "object": "response",
  "model": "qwen/qwen3.7-max",
  "output": [
    {
      "type": "message",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "AI Gateway's core capabilities include unified access, routing governance, and usage statistics."
        }
      ]
    }
  ],
  "usage": {
    "input_tokens": 32,
    "output_tokens": 24,
    "total_tokens": 56
  }
}
```

Field descriptions:

| Field | Description |
| --- | --- |
| `id` | Response ID. Used for multi-turn chaining or troubleshooting. |
| `output` | Output content array. May contain text, tool calls, and other types. |
| `output_text` | SDK shortcut field for plain text output. |
| `usage.input_tokens` | Input token count. |
| `usage.output_tokens` | Output token count. |
| `usage.total_tokens` | Total token count. |

## 9. When to use Responses vs Chat Completions

| Scenario | Recommended |
| --- | --- |
| Existing OpenAI Chat Completions code | Chat Completions |
| Maximum compatibility needed | Chat Completions |
| Unified text, multimodal, and tool capabilities | Responses |
| Need SDK features such as `client.responses.create` | Responses |
| Model detail page has no Responses example | Chat Completions |
