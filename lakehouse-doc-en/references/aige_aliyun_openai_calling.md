# OpenAI-Compatible Text and Visual Models

This guide shows how to call Alibaba Cloud Bailian text models, reasoning models, third-party text models, and visual understanding models through AI Gateway using OpenAI Chat Completions.

## 1. Applicable models

| Model family | Example models | Typical use cases |
| --- | --- | --- |
| Qwen Max / Plus / Flash | `qwen3.7-max`, `qwen3.6-max-preview`, `qwen3-max`, `qwen3.6-plus`, `qwen3.5-plus`, `qwen3.6-flash`, `qwen3.5-flash` | General Q&A, content generation, code, knowledge base, complex analysis |
| MiniMax | `MiniMax/MiniMax-M2.7`, `MiniMax-M2.5` | Long-form text generation, creative writing, general chat |
| DeepSeek | `deepseek-r1`, `deepseek-v3.2`, `deepseek-v4-flash`, `deepseek-v4-pro` | Reasoning, code, math, complex analysis |
| GLM | `glm-4.7`, `glm-5`, `glm-5.1` | General Q&A, multi-turn conversation, enterprise knowledge base |
| Kimi | `kimi-k2.5`, `kimi-k2.6` | Long context, document understanding, text processing |

## 2. Request endpoint

```text
POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/chat/completions
```

Request headers:

```http
Authorization: Bearer <API_KEY>
Content-Type: application/json
```

## 3. Basic request example

```bash
curl -X POST "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen/qwen3.7-max",
    "messages": [
      {
        "role": "system",
        "content": "You are a professional, accurate, and concise enterprise AI assistant."
      },
      {
        "role": "user",
        "content": "Describe the value of AI Gateway in enterprise model governance."
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
    base_url="https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1",
    api_key="<your-api-key>",
)

completion = client.chat.completions.create(
    model="qwen/qwen3.7-max",
    messages=[
        {"role": "system", "content": "You are a professional, accurate, and concise enterprise AI assistant."},
        {"role": "user", "content": "Describe the value of AI Gateway in enterprise model governance."},
    ],
    temperature=0.7,
    top_p=0.8,
    max_tokens=1024,
)

print(completion.choices[0].message.content)
```

## 4. Request fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | string | Yes | Model name. Use the exact identifier copied from the Model Market detail page, for example `qwen/qwen3.7-max` or `deepseek-v4-pro`. |
| `messages` | array | Yes | Conversation message list in chronological order. Each message contains `role` and `content`. |
| `stream` | boolean | No | Whether to use streaming output. `true` streams incremental content as SSE. |
| `stream_options` | object | No | Streaming output configuration. The common field `include_usage` returns token usage at the end of the stream. |
| `temperature` | number | No | Sampling temperature. Higher values produce more random output; lower values produce more deterministic output. |
| `top_p` | number | No | Nucleus sampling parameter. Do not adjust both `temperature` and `top_p` by large amounts at the same time. |
| `max_tokens` | integer | No | Maximum number of tokens to generate in this response. |
| `stop` | string / array | No | Stop generation when the model produces this string. |
| `presence_penalty` | number | No | Topic repetition penalty. Higher values encourage new topics. |
| `frequency_penalty` | number | No | Word frequency repetition penalty. Higher values reduce repeated phrases. |
| `n` | integer | No | Number of candidate responses. Production environments typically use the default value `1`. |
| `seed` | integer | No | Random seed. Improves reproducibility for the same parameters. Support varies by model. |
| `response_format` | object | No | Structured output configuration. Commonly used to require JSON output. |
| `tools` | array | No | Tool list for function calling and tool use scenarios. |
| `tool_choice` | string / object | No | Tool selection strategy: `auto`, `none`, or a specific tool. |
| `parallel_tool_calls` | boolean | No | Whether to allow parallel tool calls. Effectiveness depends on the model. |
| `logprobs` | boolean | No | Whether to return token log probabilities. Support depends on the model. |
| `top_logprobs` | integer | No | Number of candidate probabilities to return per token. Requires `logprobs` support. |
| `extra_body` | object | No | Pass provider-specific extension fields through the SDK. Supported fields vary by model. |

Recommendations:

- For stable, deterministic output, set `temperature` between `0` and `0.3`.
- For creative generation, set `temperature` between `0.7` and `1.0`.
- Set `max_tokens` explicitly in production to avoid uncontrolled costs and latency from long outputs.
- Fields such as `seed`, `logprobs`, and `parallel_tool_calls` are not supported by all models. Test with your target model before relying on them.

## 5. messages field

`messages` is the conversation context array. Common `role` values:

| role | Description |
| --- | --- |
| `system` | System instructions that define the model's identity, task scope, output format, and safety constraints. |
| `user` | User input. |
| `assistant` | Past model responses. Include these for multi-turn conversation context. |
| `tool` | Tool results. Used to close the loop on tool calls. |

Text message example:

```json
{
  "role": "user",
  "content": "Rewrite the following text as a formal announcement."
}
```

Multi-turn conversation example:

```json
{
  "model": "qwen/qwen3.7-max",
  "messages": [
    {"role": "system", "content": "You are an enterprise knowledge base assistant. Answers must cite known information."},
    {"role": "user", "content": "What routing strategies does AI Gateway support?"},
    {"role": "assistant", "content": "Supports price priority, throughput priority, and latency priority strategies."},
    {"role": "user", "content": "Please add the fallback logic when BYOK is unavailable."}
  ]
}
```

## 6. Streaming output

Streaming suits chat, long-form text generation, and code generation, and reduces time-to-first-token.

```bash
curl -N -X POST "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen/qwen3.7-max",
    "messages": [
      {"role": "user", "content": "Explain step by step how to design a model call gradual rollout strategy."}
    ],
    "stream": true,
    "stream_options": {
      "include_usage": true
    }
  }'
```

Streaming responses return multiple `data:` events. The client reads SSE data line by line and closes the connection when it receives the end event.

Python streaming example:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1",
    api_key="<your-api-key>",
)

stream = client.chat.completions.create(
    model="qwen/qwen3.7-max",
    messages=[{"role": "user", "content": "Write a model routing policy description."}],
    stream=True,
    stream_options={"include_usage": True},
)

for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## 7. JSON structured output

Use `response_format` to request JSON when your application needs stable parsing of model output.

```bash
curl -X POST "$AI_GATEWAY_OPENAI_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen/qwen3.7-max",
    "messages": [
      {
        "role": "system",
        "content": "Output only valid JSON. Do not output Markdown."
      },
      {
        "role": "user",
        "content": "Extract the priority, issue type, and one-line summary from this ticket: database query timeout affecting production reports."
      }
    ],
    "response_format": {
      "type": "json_object"
    }
  }'
```

Notes:

- Even when using `response_format`, specify the expected fields explicitly in `system` or `user`.
- JSON mode availability depends on the model. If the target model does not support it, use a prompt constraint and validate JSON on the application side.

## 8. Tool calling

Tool calling lets the model decide whether to call an external function, such as checking inventory, querying orders, retrieving from a knowledge base, or executing SQL.

Request example:

```json
{
  "model": "qwen/qwen3.7-max",
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

Typical flow:

1. The client sends the user question and tool definitions.
2. The model returns `tool_calls` with the function name and arguments.
3. The application executes the real function.
4. The application sends the tool result back to the model as a `role: "tool"` message.
5. The model generates the final answer based on the tool result.

Not all models support tool calling. Check the model detail page before using this feature.

## 9. Visual understanding

Models that support visual input accept both text and images in `messages.content`.

```bash
curl -X POST "$AI_GATEWAY_OPENAI_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen/qwen3.6-plus",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Identify the product in the image and output JSON: product type, color, and whether it contains text."
          },
          {
            "type": "image_url",
            "image_url": {
              "url": "https://example.com/product.png"
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

Image input fields:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | string | Yes | Fixed as `image_url`. |
| `image_url.url` | string | Yes | Image URL. Public URLs work; Base64 Data URL support depends on the model. |
| `image_url.detail` | string | No | Image detail level. Support depends on the model. |

Notes:

- The image URL must be accessible by the model service.
- Do not pass local paths such as `/Users/a123/image.png`.
- Visual understanding models have different names from pure text models. Confirm on the model detail page that the model supports image input.
- Image count, size, and format limits are defined on the model detail page.

## 10. Response fields

Typical non-streaming response structure:

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1710000000,
  "model": "qwen/qwen3.7-max",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "AI Gateway centrally manages multi-model access, routing, authentication, and usage statistics."
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
| `id` | Request ID. Provide this to support when investigating issues. |
| `choices` | Candidate response list. Typically read `choices[0].message.content`. |
| `finish_reason` | Stop reason: normal completion, length limit, tool call triggered, and so on. |
| `usage.prompt_tokens` | Input token count. |
| `usage.completion_tokens` | Output token count. |
| `usage.total_tokens` | Total input and output token count. |

## 11. FAQ

### Why does the same request sometimes return different results?

LLMs have inherent sampling randomness. To get more deterministic output, lower `temperature` and set `seed` if the model supports it.

### Why does JSON parsing fail even with JSON output enabled?

Also explicitly instruct the model in the prompt to "output only valid JSON," and validate the JSON on the application side. Some models may not support strict JSON mode.

### Why is the model response truncated?

This is usually because `max_tokens` is too small or the context is too long. Increase `max_tokens` or reduce the history message length.

### Why is tool calling not working?

Confirm the target model supports tool calling, and verify that the `tools` JSON Schema is complete and `tool_choice` is correct.
