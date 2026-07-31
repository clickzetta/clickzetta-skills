# DeepSeek Anthropic Messages Compatible Calls

This guide shows how to call Tencent TokenHub DeepSeek models through AI Gateway using the Anthropic Messages compatible protocol. Use this approach if your existing workload already uses the Anthropic SDK, Claude Code, or Messages protocol.

For new integrations that require DeepSeek thinking mode, JSON mode, or function calling, use OpenAI Chat Completions instead.

## 1. Request endpoint

```text
POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/messages
```

Request headers:

```http
x-api-key: <API_KEY>
Content-Type: application/json
anthropic-version: 2023-06-01
```

Notes:

- `x-api-key` uses your AI Gateway API key.
- According to TokenHub documentation, the `anthropic-version` header is ignored on the server side. Keep it for compatibility with the Anthropic SDK and common clients.

## 2. Basic call

```bash
curl -X POST "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/messages" \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "deepseek-v4-pro",
    "max_tokens": 1000,
    "system": "You are a professional, accurate, and concise enterprise AI assistant.",
    "messages": [
      {
        "role": "user",
        "content": "Explain the differences between OpenAI Chat Completions and Anthropic Messages."
      }
    ],
    "stream": false
  }'
```

## 3. Python SDK

```python
import anthropic

client = anthropic.Anthropic(
    api_key="<your-api-key>",
    base_url="https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1",
)

message = client.messages.create(
    model="deepseek-v4-pro",
    max_tokens=1000,
    system="You are a professional, accurate, and concise enterprise AI assistant.",
    messages=[
        {"role": "user", "content": "Describe the model routing capability of AI Gateway."}
    ],
)

print(message.content[0].text)
```

## 4. Streaming output

```bash
curl -N -X POST "$AI_GATEWAY_BASE_URL/messages" \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "deepseek-v4-pro",
    "max_tokens": 1000,
    "system": [
      {
        "type": "text",
        "text": "You are a helpful assistant."
      }
    ],
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Hi, how are you?"
          }
        ]
      }
    ],
    "stream": true
  }'
```

Python streaming example:

```python
import anthropic

client = anthropic.Anthropic(
    api_key="<your-api-key>",
    base_url="https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1",
)

with client.messages.stream(
    model="deepseek-v4-pro",
    max_tokens=1000,
    system="You are a helpful assistant.",
    messages=[{"role": "user", "content": "Hi, how are you?"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

## 5. Request fields

| Field | Support | Description |
| --- | --- | --- |
| `model` | Supported | Model name, for example `deepseek-v4-flash` or `deepseek-v4-pro`. |
| `messages` | Supported | Conversation message array. |
| `max_tokens` | Fully supported | Maximum output token count. |
| `system` | Fully supported | System instructions. |
| `stream` | Fully supported | Streaming response. |
| `temperature` | Fully supported | Temperature parameter. Common range: `0.0` to `2.0`. |
| `top_p` | Fully supported | Top-p sampling. |
| `stop_sequences` | Fully supported | Stop sequences. |
| `thinking` | Ignored | Not processed in the TokenHub Anthropic protocol. |
| `top_k` | Ignored | Not processed. |
| `metadata` | Ignored | Not processed. |
| `service_tier` | Ignored | Not processed. |

## 6. Message content field support

| Message content | Support | Description |
| --- | --- | --- |
| `content` as string | Fully supported | Suited for plain text input. |
| `content` as array, `type="text"` | Fully supported | Suited for the Anthropic standard multi-part text structure. |
| `content` as array, `type="image"` | Partial model support | Current DeepSeek text models do not recommend image input. |
| `content` as array, `type="document"` | Not supported | Do not use. |
| `content` as array, `type="search_result"` | Not supported | Do not use. |
| `cache_control` | Ignored | Has no effect when passed. |

## 7. Tool calling

Anthropic Messages tool definitions differ from OpenAI Chat Completions. They use `input_schema`.

```json
{
  "model": "deepseek-v4-pro",
  "max_tokens": 1000,
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

In the TokenHub Anthropic protocol:

- `tools[].name`, `tools[].input_schema`, and `tools[].description` are fully supported.
- Both string format and object format `tool_choice` are supported.
- `disable_parallel_tool_use` is ignored.
- `cache_control`-related fields are ignored.

## 8. Differences from OpenAI Chat Completions

| Item | OpenAI Chat Completions | Anthropic Messages |
| --- | --- | --- |
| Endpoint | `/gateway/v1/chat/completions` | `/gateway/v1/messages` |
| Auth header | `Authorization: Bearer <API_KEY>` | `x-api-key: <API_KEY>` |
| System instructions | `role: system` in `messages` | Top-level `system` field |
| Max output | `max_tokens` | `max_tokens` |
| Stop sequences | `stop` | `stop_sequences` |
| Tool parameter schema | `tools[].function.parameters` | `tools[].input_schema` |
| Thinking mode | Controlled via `thinking` | `thinking` is ignored in the Anthropic protocol |

## 9. Recommendations

- Use OpenAI Chat Completions for new integrations.
- Use the Anthropic Messages compatible interface to reduce migration costs if your workload already uses the Anthropic SDK, Claude Code, or Messages protocol.
- If you need DeepSeek `thinking` control, use OpenAI Chat Completions.
- If the model detail page does not show a Messages example, use Chat Completions.
