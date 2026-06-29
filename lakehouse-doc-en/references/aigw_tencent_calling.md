# Tencent TokenHub DeepSeek: Overview

This guide shows how to call Tencent Cloud TokenHub DeepSeek models through AI Gateway. AI Gateway currently supports only the DeepSeek series under Tencent TokenHub, so this section focuses on `deepseek-v4-flash` and `deepseek-v4-pro`.

TokenHub officially supports both OpenAI Chat Completions and Anthropic Messages protocols. When calling through AI Gateway, use the AI Gateway endpoint and API key; you do not need the raw Tencent TokenHub API key.

## 1. Applicable models

Tencent TokenHub currently supports the following DeepSeek models in AI Gateway:

| Model | Type | Recommended use cases |
| --- | --- | --- |
| `deepseek-v4-flash` | Text / reasoning | High-frequency Q&A, summarization, classification, code explanation, low-latency inference |
| `deepseek-v4-pro` | Text / reasoning | Complex reasoning, code analysis, solution design, long document processing |

Model names are authoritative as shown on the **Model Market** detail page.

## 2. Endpoint overview

| Protocol | Endpoint | Auth | Use cases |
| --- | --- | --- | --- |
| OpenAI Chat Completions | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/chat/completions` | `Authorization: Bearer <API_KEY>` | Default choice. Covers most DeepSeek text, reasoning, JSON, and tool calling scenarios. |
| Anthropic Messages | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/messages` | `x-api-key: <API_KEY>` | For workloads already using the Anthropic SDK, Claude Code, or Messages protocol. |

Notes:

- Tencent TokenHub text models use `/gateway/v1/...`.
- Do not use `/gateway/api/v1/chat/completions` for Tencent text models.
- Volcengine models use `/gateway/api/v3/...`. Do not mix them.
- The API key is the one created in AI Gateway, not the raw Tencent TokenHub key.
- For controlling DeepSeek thinking mode, reading `reasoning_content`, using JSON mode, or tool calling, use OpenAI Chat Completions.

## 3. Environment variables

```bash
export AI_GATEWAY_BASE_URL="https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1"
export API_KEY="<your-api-key>"
```

## 4. Minimal call example

```bash
curl -X POST "$AI_GATEWAY_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [
      {
        "role": "user",
        "content": "Describe AI Gateway in one sentence."
      }
    ],
    "max_tokens": 512,
    "thinking": {
      "type": "disabled"
    }
  }'
```

## 5. Model selection guidance

| Scenario | Recommended model | Notes |
| --- | --- | --- |
| High-frequency Q&A, summarization, classification | `deepseek-v4-flash` | Lighter response, better for high-concurrency and low-latency workloads |
| Complex reasoning, code analysis, solution design | `deepseek-v4-pro` | Better suited for high-quality reasoning tasks |
| Cost-sensitive workloads | Test `deepseek-v4-flash` first | Use flash if it meets quality requirements |
| Quality-first workloads | Test `deepseek-v4-pro` first | Suited for complex tasks; evaluate cost and latency |

## 6. DeepSeek call guidelines

| Capability | Guidance |
| --- | --- |
| General Q&A | Use `deepseek-v4-flash` with `thinking: {"type": "disabled"}`. |
| Complex reasoning | Use `deepseek-v4-pro` with `thinking: {"type": "enabled"}`. Set `reasoning_effort` if needed. |
| Long output / reasoning tasks | Enable `stream: true` to avoid timeout from long waits. |
| JSON output | Use `response_format: {"type": "json_object"}` and disable thinking mode. |
| Tool calling | Use `tools` / `tool_choice` in OpenAI Chat Completions. |
| Multi-turn conversation | When replaying the previous `assistant` message, include only `content`, not `reasoning_content`. |

## 7. BYOK and routing

When using BYOK to bind a Tencent TokenHub key:

- API requests still use the AI Gateway API key.
- The raw TokenHub key is used only on the AI Gateway backend to call the upstream.
- In default and specified provider modes, BYOK takes priority. If BYOK fails, the system falls back to the platform built-in provider.
- In BYOK Only mode, there is no fallback to the platform built-in provider.

## 8. Section guide

| Section | Content |
| --- | --- |
| DeepSeek OpenAI Chat Completions | Request fields, streaming output, Python and Node.js SDK examples |
| DeepSeek thinking mode, JSON, and tool calling | `thinking`, `reasoning_content`, JSON mode, function calling |
| DeepSeek Anthropic Messages compatible calls | Anthropic headers, field differences, tool calling, and SDK examples |
