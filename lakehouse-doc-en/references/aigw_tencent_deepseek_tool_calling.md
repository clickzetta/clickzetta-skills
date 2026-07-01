# DeepSeek Thinking Mode, JSON, and Tool Calling

This guide covers the extended capabilities of Tencent TokenHub DeepSeek models: thinking mode, structured JSON output, and function calling.

## 1. Thinking mode

DeepSeek models support thinking mode control via the `thinking` field.

| Value | Description |
| --- | --- |
| `{"type": "enabled"}` | Enable thinking. Suited for complex reasoning, math, code analysis, and solution design. |
| `{"type": "disabled"}` | Disable thinking. Suited for summarization, classification, and simple Q&A. Reduces token consumption and latency. |

Some DeepSeek calls also support configuring reasoning depth:

```json
{
  "thinking": {
    "type": "enabled",
    "reasoning_effort": "high"
  }
}
```

Increase reasoning depth for complex tasks. Disable thinking for general Q&A, summarization, and classification.

Example:

```bash
curl -X POST "$AI_GATEWAY_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-pro",
    "messages": [
      {
        "role": "user",
        "content": "Analyze potential performance bottlenecks in this system architecture and suggest optimizations."
      }
    ],
    "max_tokens": 2048,
    "thinking": {
      "type": "enabled",
      "reasoning_effort": "high"
    }
  }'
```

When thinking is enabled, the response `message` may contain:

```json
{
  "role": "assistant",
  "reasoning_content": "The model's reasoning process goes here.",
  "content": "The final answer goes here."
}
```

Recommendations:

- For end-user-facing applications, display only `content`.
- `reasoning_content` is useful for debugging, internal analysis, or advanced display modes.
- In normal multi-turn conversations, pass only `content` from the previous turn; do not pass `reasoning_content`.
- If you use complex tool calling with interleaved thinking, handle historical thinking content as described in the model detail page.
- When thinking is enabled, response times are longer. Use `stream=true` to reduce timeout risk.

## 2. Streaming thinking output

When streaming is enabled, the thinking process and the final answer may be returned as separate incremental fields.

```python
from openai import OpenAI

client = OpenAI(
    api_key="<your-api-key>",
    base_url="https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1",
)

stream = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[
        {"role": "user", "content": "Analyze the advantages and challenges of a vector search system."}
    ],
    max_tokens=2048,
    stream=True,
    extra_body={"thinking": {"type": "enabled"}},
)

answer_started = False

for chunk in stream:
    if not chunk.choices:
        continue

    delta = chunk.choices[0].delta

    reasoning_delta = getattr(delta, "reasoning_content", None)
    if reasoning_delta:
        # In production, you may choose not to display the thinking process
        print(reasoning_delta, end="", flush=True)

    if delta.content:
        if not answer_started:
            print("\n\n=== Final Answer ===")
            answer_started = True
        print(delta.content, end="", flush=True)
```

## 3. JSON mode

Use `response_format` to request JSON output when your application needs stable parsing.

```bash
curl -X POST "$AI_GATEWAY_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [
      {
        "role": "system",
        "content": "Output only valid JSON. Do not output Markdown."
      },
      {
        "role": "user",
        "content": "Extract ticket information: customer reports API call error 429, affecting production reports. Fields: priority, category, summary."
      }
    ],
    "max_tokens": 512,
    "response_format": {
      "type": "json_object"
    },
    "thinking": {
      "type": "disabled"
    }
  }'
```

Notes:

- When using JSON mode, explicitly request JSON output in `system` or `user` messages.
- Do not enable both `thinking.type=enabled` and `response_format.type=json_object` at the same time.
- Validate JSON parsing and schema on the application side.
- If thinking mode is enabled, parse only the JSON in the final `content`; do not treat `reasoning_content` as the application result.

## 4. Function calling

Function calling lets the model decide whether to call an external tool, such as checking weather, querying orders, retrieving from a knowledge base, or executing SQL.

```bash
curl -X POST "$AI_GATEWAY_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [
      {
        "role": "user",
        "content": "What is the weather in Beijing today?"
      }
    ],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "get_weather",
          "description": "Query the weather for a city",
          "parameters": {
            "type": "object",
            "properties": {
              "city": {
                "type": "string",
                "description": "City name"
              }
            },
            "required": ["city"]
          }
        }
      }
    ],
    "tool_choice": "auto",
    "thinking": {
      "type": "disabled"
    }
  }'
```

If the model decides to call a tool, it returns `tool_calls`:

```json
{
  "role": "assistant",
  "content": null,
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"city\":\"Beijing\"}"
      }
    }
  ]
}
```

After the application executes the tool, pass the result back as a `role: "tool"` message:

```json
{
  "model": "deepseek-v4-flash",
  "messages": [
    {
      "role": "user",
      "content": "What is the weather in Beijing today?"
    },
    {
      "role": "assistant",
      "content": null,
      "tool_calls": [
        {
          "id": "call_abc123",
          "type": "function",
          "function": {
            "name": "get_weather",
            "arguments": "{\"city\":\"Beijing\"}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "tool_call_id": "call_abc123",
      "content": "{\"temperature\":22,\"weather\":\"sunny\",\"humidity\":45}"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Query the weather for a city",
        "parameters": {
          "type": "object",
          "properties": {
            "city": {
              "type": "string"
            }
          },
          "required": ["city"]
        }
      }
    }
  ],
  "thinking": {
    "type": "disabled"
  }
}
```

## 5. Tool calling fields

| Field | Type | Description |
| --- | --- | --- |
| `tools` | array | Tool definition list. |
| `tools[].type` | string | Tool type, typically `function`. |
| `tools[].function.name` | string | Function name. |
| `tools[].function.description` | string | Function description. Helps the model decide when to call it. |
| `tools[].function.parameters` | object | JSON Schema parameter definition. |
| `tool_choice` | string / object | Tool selection strategy. |
| `parallel_tool_calls` | boolean | Whether to allow calling multiple tools in parallel in a single response. |

Common `tool_choice` values:

| Value | Description |
| --- | --- |
| `auto` | The model decides whether to call a tool. |
| `none` | Disable tool calling. |
| `required` | Force the model to call a tool. |
| `{"type":"function","function":{"name":"xxx"}}` | Force calling the specified tool. |

## 6. Recommendations

- Disable thinking for simple Q&A, classification, and summarization to reduce cost and latency.
- Enable thinking for complex reasoning, code analysis, and solution design. Increase `max_tokens` accordingly.
- Make tool descriptions and parameter schemas as clear as possible to prevent the model from generating invalid arguments.
- When passing back tool results, `tool_call_id` must match the tool call ID returned by the model.
- Do not let the model directly execute high-risk write operations. Apply permission checks and human confirmation on the application side for sensitive tools.
