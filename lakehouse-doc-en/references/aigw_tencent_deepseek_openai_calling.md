# DeepSeek OpenAI Chat Completions

This guide shows how to call Tencent TokenHub DeepSeek models through AI Gateway using OpenAI Chat Completions. Tencent TokenHub currently supports only DeepSeek models, so all examples use `deepseek-v4-flash` and `deepseek-v4-pro`.

OpenAI Chat Completions is the recommended default integration path for DeepSeek. It covers general conversation, complex reasoning, streaming output, JSON output, and tool calling.

## 1. Request endpoint

```text
POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/chat/completions
```

Request headers:

```http
Authorization: Bearer <API_KEY>
Content-Type: application/json
```

## 2. Basic conversation

```bash
curl -X POST "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [
      {
        "role": "user",
        "content": "Introduce large language models."
      }
    ],
    "max_tokens": 1024,
    "thinking": {
      "type": "disabled"
    }
  }'
```

## 3. System prompt

Use the `system` role to set model behavior, response boundaries, and output format.

```bash
curl -X POST "$AI_GATEWAY_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-pro",
    "messages": [
      {
        "role": "system",
        "content": "You are a rigorous technical analysis assistant. Give the conclusion first, then the reasoning."
      },
      {
        "role": "user",
        "content": "Analyze the impact of AI Gateway routing strategies on stability."
      }
    ],
    "temperature": 0.3,
    "max_tokens": 2048,
    "thinking": {
      "type": "enabled"
    }
  }'
```

## 4. Multi-turn conversation

Pass all history messages in `messages` for multi-turn conversations.

```json
{
  "model": "deepseek-v4-flash",
  "messages": [
    {
      "role": "system",
      "content": "You are a friendly AI assistant."
    },
    {
      "role": "user",
      "content": "My name is Alex and I like basketball."
    },
    {
      "role": "assistant",
      "content": "Nice to meet you, Alex! Basketball is a great sport."
    },
    {
      "role": "user",
      "content": "Do you remember my name and hobby?"
    }
  ],
  "max_tokens": 1024,
  "thinking": {
    "type": "disabled"
  }
}
```

In normal multi-turn conversations, when replaying the previous `assistant` message, include only `content`. You do not need to include `reasoning_content`.

## 5. Request fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | string | Yes | Model name, for example `deepseek-v4-flash` or `deepseek-v4-pro`. |
| `messages` | array | Yes | Conversation message array in chronological order. |
| `stream` | boolean | No | Whether to enable SSE streaming output. Default is `false`. |
| `stream_options` | object | No | Streaming output options. Common usage: `{"include_usage": true}`. Valid only when `stream=true`. |
| `temperature` | number | No | Sampling temperature. TokenHub common range: `0.0` to `2.0`. Higher values produce more random output. |
| `top_p` | number | No | Nucleus sampling. TokenHub common range: `0.0` to `1.0`. Adjust either `temperature` or `top_p`, not both at once. |
| `max_tokens` | integer | No | Maximum output token count. For reasoning models, this budget is shared between the thinking process and the final answer. Increase it when thinking is enabled. |
| `n` | integer | No | Number of candidate responses. Use default `1` in production. `n > 1` is billed by total token count. |
| `stop` | string / array | No | Stop generation sequences. |
| `presence_penalty` | number | No | Deprecated for DeepSeek calls. Passing this field typically has no effect. |
| `frequency_penalty` | number | No | Deprecated for DeepSeek calls. Passing this field typically has no effect. |
| `response_format` | object | No | Structured output configuration, for example `{"type": "json_object"}`. |
| `tools` | array | No | Tool definition list. |
| `tool_choice` | string / object | No | Tool selection strategy: `auto`, `none`, `required`, or a specific tool. |
| `parallel_tool_calls` | boolean | No | Whether to allow parallel tool calls. Default is typically `true`. |
| `thinking` | object | No | DeepSeek thinking mode control. Common values: `{"type": "enabled"}` or `{"type": "disabled"}`. |
| `thinking.reasoning_effort` | string | No | Reasoning depth. Set to `high` for complex tasks. Supported values depend on the model detail page. |

DeepSeek parameter notes:

- Do not enable both `thinking.type=enabled` and `response_format.type=json_object` at the same time.
- When thinking is enabled, response time increases. Use `stream=true` to avoid timeouts.
- `max_tokens` limits both the thinking process and the final answer. Increase it when thinking is enabled.
- `frequency_penalty` and `presence_penalty` are deprecated for DeepSeek and typically have no effect.

## 6. Streaming output

Enable streaming for reasoning model output, which tends to be long.

```bash
curl -N -X POST "$AI_GATEWAY_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-pro",
    "messages": [
      {
        "role": "user",
        "content": "Analyze the retrieval pipeline of a RAG system step by step."
      }
    ],
    "max_tokens": 2048,
    "stream": true,
    "stream_options": {
      "include_usage": true
    },
    "thinking": {
      "type": "enabled",
      "reasoning_effort": "high"
    }
  }'
```

Notes:

- Streaming responses are returned as SSE. The client reads them incrementally.
- When thinking is enabled, the incremental stream may contain both `reasoning_content` and `content`.
- If your application does not display the thinking process, render only the final answer content.

## 7. Python SDK

```python
from openai import OpenAI

client = OpenAI(
    api_key="<your-api-key>",
    base_url="https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1",
)

response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[
        {"role": "user", "content": "Explain the difference between gateway retry and application retry."}
    ],
    max_tokens=1024,
    temperature=0.3,
    extra_body={"thinking": {"type": "disabled"}},
)

print(response.choices[0].message.content)
```

Streaming example:

```python
from openai import OpenAI

client = OpenAI(
    api_key="<your-api-key>",
    base_url="https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1",
)

stream = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[{"role": "user", "content": "Analyze the value of AI Gateway."}],
    max_tokens=2048,
    stream=True,
    extra_body={"thinking": {"type": "enabled"}},
)

for chunk in stream:
    if not chunk.choices:
        continue
    delta = chunk.choices[0].delta
    content = getattr(delta, "content", None)
    if content:
        print(content, end="", flush=True)
```

## 8. Node.js SDK

```javascript
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.API_KEY,
  baseURL: "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1",
});

const completion = await client.chat.completions.create({
  model: "deepseek-v4-flash",
  messages: [
    {
      role: "user",
      content: "Explain the difference between API Gateway and AI Gateway in three sentences.",
    },
  ],
  max_tokens: 1024,
  temperature: 0.3,
  thinking: { type: "disabled" },
});

console.log(completion.choices[0].message.content);
```

## 9. Response fields

Typical non-streaming response:

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1710000000,
  "model": "deepseek-v4-flash",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "AI Gateway centrally manages model calls, authentication, routing, and usage statistics."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 32,
    "completion_tokens": 24,
    "total_tokens": 56
  }
}
```

| Field | Description |
| --- | --- |
| `choices[0].message.content` | Final answer content. |
| `choices[0].message.reasoning_content` | Thinking process, returned when thinking mode is enabled. |
| `finish_reason` | Stop reason: `stop`, `length`, `tool_calls`. |
| `usage.prompt_tokens` | Input token count. |
| `usage.completion_tokens` | Output token count. May include thinking tokens. |
| `usage.total_tokens` | Total token count. |
