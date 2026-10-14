# Anthropic Messages Compatible Calls

Some models or endpoints use the Anthropic Messages protocol. Anthropic Messages fields differ from OpenAI Chat Completions fields. Do not reuse an OpenAI request body by simply swapping the endpoint.

## 1. Request endpoint

```text
POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/messages
```

Request headers:

```http
x-api-key: <API_KEY>
anthropic-version: 2023-06-01
Content-Type: application/json
```

`<API_KEY>` is your AI Gateway API key.

## 2. Basic request example

```bash
curl -X POST "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/messages" \
  -H "x-api-key: $API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "anthropic/claude-opus-4.6",
    "max_tokens": 1024,
    "system": "You are a professional, accurate, and concise enterprise AI assistant.",
    "messages": [
      {
        "role": "user",
        "content": "Explain the model routing capability of AI Gateway."
      }
    ]
  }'
```

Python example:

```python
import anthropic

client = anthropic.Anthropic(
    base_url="https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1",
    api_key="<your-api-key>",
)

message = client.messages.create(
    model="anthropic/claude-opus-4.6",
    max_tokens=1024,
    system="You are a professional, accurate, and concise enterprise AI assistant.",
    messages=[
        {"role": "user", "content": "Explain the model routing capability of AI Gateway."}
    ],
)

print(message.content[0].text)
```

## 3. Request fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | string | Yes | Model name. Use the identifier shown on the Model Market detail page. |
| `messages` | array | Yes | Conversation message array. In the Messages protocol, system instructions go in the top-level `system` field, not in `messages`. |
| `max_tokens` | integer | Yes | Maximum output token count. Anthropic Messages typically requires this field explicitly. |
| `system` | string / array | No | System instructions that set the model's identity, constraints, and output format. |
| `stream` | boolean | No | Whether to stream the response. |
| `temperature` | number | No | Sampling temperature. |
| `top_p` | number | No | Nucleus sampling parameter. |
| `top_k` | integer | No | Number of candidate tokens to sample. Support depends on the model. |
| `stop_sequences` | array | No | Stop generation sequences. |
| `metadata` | object | No | Business metadata. |
| `tools` | array | No | Tool definition list. |
| `tool_choice` | object | No | Tool selection strategy. |
| `thinking` | object | No | Extended thinking configuration. Available only when the model and endpoint support it. |

## 4. messages format

Anthropic Messages `messages` contains only user and assistant turns. Put system instructions in the top-level `system` field.

```json
{
  "model": "anthropic/claude-opus-4.6",
  "max_tokens": 1024,
  "system": "Output only valid JSON. Do not output Markdown.",
  "messages": [
    {
      "role": "user",
      "content": "Extract ticket information: customer reports model call error 429."
    }
  ]
}
```

Multi-turn conversation example:

```json
{
  "model": "anthropic/claude-opus-4.6",
  "max_tokens": 1024,
  "system": "You are an enterprise knowledge base assistant.",
  "messages": [
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
      "content": "Please add permission management capabilities."
    }
  ]
}
```

## 5. Multimodal input

If the model supports image input, pass an array in `content`.

```json
{
  "model": "anthropic/claude-opus-4.6",
  "max_tokens": 1024,
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Describe the content of this image."
        },
        {
          "type": "image",
          "source": {
            "type": "url",
            "url": "https://example.com/image.png"
          }
        }
      ]
    }
  ]
}
```

Support for `url`, Base64, and image size and count limits depends on the model. Check the model detail page.

## 6. Streaming output

```bash
curl -N -X POST "$AI_GATEWAY_OPENAI_BASE_URL/messages" \
  -H "x-api-key: $API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "anthropic/claude-opus-4.6",
    "max_tokens": 1024,
    "messages": [
      {
        "role": "user",
        "content": "Explain step by step how to integrate AI Gateway."
      }
    ],
    "stream": true
  }'
```

Streaming returns SSE events. The client must handle incremental text, tool calls, and end events by event type.

## 7. Tool calling

```json
{
  "model": "anthropic/claude-opus-4.6",
  "max_tokens": 1024,
  "messages": [
    {
      "role": "user",
      "content": "Query the shipping status for order 202606150001."
    }
  ],
  "tools": [
    {
      "name": "get_order_status",
      "description": "Query shipping status by order ID",
      "input_schema": {
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
  "tool_choice": {
    "type": "auto"
  }
}
```

Compared with OpenAI tool calling, Anthropic tool definitions use `input_schema`, and the tool choice field also differs.

## 8. Response fields

Typical response:

```json
{
  "id": "msg_xxx",
  "type": "message",
  "role": "assistant",
  "model": "anthropic/claude-opus-4.6",
  "content": [
    {
      "type": "text",
      "text": "AI Gateway centrally manages model access, authentication, routing, and usage statistics."
    }
  ],
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 35,
    "output_tokens": 26
  }
}
```

| Field | Description |
| --- | --- |
| `content` | Output content array. Text content is usually at `content[0].text`. |
| `stop_reason` | Stop reason: `end_turn`, `max_tokens`, `stop_sequence`, `tool_use`. |
| `usage.input_tokens` | Input token count. |
| `usage.output_tokens` | Output token count. |

## 9. Differences from OpenAI Chat Completions

| Item | OpenAI Chat Completions | Anthropic Messages |
| --- | --- | --- |
| Endpoint | `/gateway/v1/chat/completions` | `/gateway/v1/messages` |
| Auth header | `Authorization: Bearer <API_KEY>` | `x-api-key: <API_KEY>` |
| System instructions | `role: system` in `messages` | Top-level `system` field |
| Max output | `max_tokens` | `max_tokens`, typically required |
| Stop sequences | `stop` | `stop_sequences` |
| Tool schema | `tools[].function.parameters` | `tools[].input_schema` |
