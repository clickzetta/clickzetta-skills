# AI Gateway: Six Tool Integration Capability Summary

Last updated: 2026-08-20 (Asia/Shanghai)

## 1. Overview

This document summarizes the protocol capabilities, verification requirements, and known limitations when integrating the following six AI coding tools with AI Gateway:

- WorkBuddy
- OpenCode
- TRAE International
- OpenClaw
- Kilo Code
- Codex CLI

This document helps you confirm:

1. Which API protocols each tool can be configured for;
2. How to determine whether a model is usable when selecting one;
3. The confirmed baseline capabilities and known compatibility limitations for each tool.

This document provides a capability overview. For actual installation, configuration, and troubleshooting, refer to the configuration guide for the corresponding tool.

Example AI Gateway Base URL:

```text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1>
```

## 2. Required Reading Before Use

The model catalog in AI Gateway may change based on API key permissions, subscription plan, routing, and upstream status. Always use the real-time query result for the current API key — do not treat historical model lists as a long-term valid catalog.

For a model to be usable, all of the following conditions must be met simultaneously:

```text
Model appears in the current API key's catalog for the target protocol
    ↓
A standard request using the same protocol returns HTTP 200 and final text
    ↓
The target tool uses the correct provider or API format
    ↓
The target tool's actual message returns final text
```

Therefore:

- A model appearing in `/models` only means the current API key can see it;
- A successful Chat request does not mean Responses will succeed;
- A successful Anthropic Messages request does not mean OpenAI Chat will succeed;
- A successful standard request does not mean the tool is fully configured;
- One model succeeding does not mean other models in the same catalog or from the same vendor will succeed;
- Successful basic text does not mean streaming, tool calling, multimodal, and long-context are all available.

## 3. Protocol Capability Summary for All Six Tools

| Tool | OpenAI Chat Completions | OpenAI Responses | Anthropic Messages | Most Important Current Limitation |
|---|---|---|---|---|
| WorkBuddy | Supported; is the base protocol for custom model configuration | Custom model configuration not supported | Custom model configuration not supported | "Custom protocol" only changes URL handling, it does not transform the request format; Claude can only be used if AI Gateway provides an OpenAI Chat-compatible route |
| OpenCode | Supported; uses OpenAI Compatible provider | Supported; requires a separately configured Responses provider | Supported; uses Anthropic provider | The three providers are independent; a successful one protocol does not automatically fall back to another |
| TRAE International | Supported; can be selected in custom model configuration | Custom configuration not supported | Supported; can be selected in custom model configuration | The custom model page only has Chat and Anthropic API formats; a successful Responses request cannot be added directly to TRAE |
| OpenClaw | Supported; uses `openai-completions` provider | Supported; uses `openai-responses` provider | Supported; uses `anthropic-messages` provider | A separate provider must be created for each protocol that passes standard request testing; a model ID prefix does not automatically select a protocol |
| Kilo Code | Supported; uses OpenAI Compatible provider | Tool supports it, but a known streaming event compatibility issue currently exists | Supported; uses Anthropic provider | Tested with Kilo Code CLI 7.4.22: Responses standard request succeeds, but actual client messages fail due to `SSE-Keep-Alive` event parsing failure |
| Codex CLI | Custom provider not supported | Supported; also the only native wire protocol | Custom provider not supported | Models must have a Responses route to connect natively; models that only support Chat or Anthropic require a translation layer or a different client |

## 4. How to Choose a Tool Based on Model Type

This table is a recommendation for the first test path to try, not a fixed model list. The final determination is always based on the real-time catalog of the current API key and actual requests.

| Model Type | Priority Protocol to Test | Available Tools | Special Notes |
|---|---|---|---|
| OpenAI GPT, Codex, and other OpenAI series | OpenAI Chat or OpenAI Responses | Chat: WorkBuddy, OpenCode, TRAE, OpenClaw, Kilo; Responses: OpenCode, OpenClaw, Kilo, Codex CLI | Each model requires separate testing for Chat and Responses; Kilo Responses has a known compatibility issue |
| Anthropic Claude | Anthropic Messages | OpenCode, TRAE, OpenClaw, Kilo Code | WorkBuddy cannot send Anthropic Messages directly; Codex CLI requires a Responses compatibility layer |
| DeepSeek | Test OpenAI Chat first; if available in the catalog, then test Anthropic Messages or Responses | Chat: the five non-Codex tools; Anthropic: OpenCode, TRAE, OpenClaw, Kilo; Responses: only for tools that support Responses after actual success | Do not assume Responses is available based on the DeepSeek name |
| Qwen | Test OpenAI Chat first; test other protocols one by one based on the catalog | Depends on which protocols actually succeed for that model | One Qwen model succeeding does not mean other Qwen models or other protocols will succeed |
| Gemini, Grok, Mistral, Meta, GLM, Kimi, MiniMax, etc. | Use the compatible protocol that AI Gateway actually provides | Choose tools that support that protocol | Vendor name is not a protocol switch; always query the catalog and make a minimal request |

## 5. Verification Scope and Known Limitations

The table below lists the confirmed protocol integration capabilities for each tool and the acceptance tests that must be completed before use. A model not listed here does not mean it is unavailable; verify each model individually using the real-time catalog for the current API key.

| Tool | Confirmed Integration Capabilities | Must Complete Before Use | Known Limitations or Recommendations |
|---|---|---|---|
| WorkBuddy | OpenAI Chat Completions basic text integration path | Both the standard Chat request for the target model and an actual WorkBuddy message must return final text | Do not enter an Anthropic Messages or Responses URL directly into WorkBuddy's custom model configuration |
| OpenCode | Can configure OpenAI Chat, OpenAI Responses, and Anthropic Messages providers separately | The target model must first pass a standard request for the same protocol, then return final text via the corresponding OpenCode provider | The three providers are independent; a Chat provider cannot substitute for a Responses provider |
| TRAE International | Can configure OpenAI Chat and Anthropic Messages custom models | Complete standard request, TRAE connectivity test, and Agent actual message | Does not provide an OpenAI Responses custom format |
| OpenClaw | Can configure Chat, Responses, and Anthropic providers separately | Complete standard request, provider configuration, Gateway check, and `openclaw agent` actual message | Models must be added to the provider matching the protocol that passed testing |
| Kilo Code CLI | `qwen/qwen3.6-flash` passed OpenAI Chat basic text validation; `anthropic/claude-opus-5` passed Anthropic Messages basic text validation | Other models and protocols still require separate standard requests and `kilo run` verification | `openai/gpt-5.5` Responses standard request succeeds, but Kilo actual messages show `text part SSE-Keep-Alive not found`; this path is not recommended at this time |
| Codex CLI | Supports OpenAI Responses custom provider | Both the Responses standard request for the target model and `codex exec` must return final text | Does not support direct configuration of Chat or Anthropic Messages; when Claude is needed, a Responses compatibility layer must be provided |

## 6. Why the Model List Requires Real-Time Queries

The range of available models is determined by the following factors together:

```text
Number of models and model IDs
    = AI Gateway's current routing
    + current API key permissions
    + tenant or subscription plan
    + upstream real-time status
```

Therefore, under the same Base URL, different API keys may see different catalogs; the same API key may also see different catalogs depending on whether OpenAI or Anthropic authentication is used.

Using historical model lists directly may cause the following issues:

- Decommissioned or unauthorized models remain marked as available;
- Newly added models are not displayed in time;
- Catalog visibility is mistakenly interpreted as protocol availability;
- Success with one protocol is incorrectly assumed to apply to other protocols;
- A successful standard request is mistakenly assumed to mean all clients will succeed.

Therefore, the specific model list must be retrieved in real time using the current API key, and verification must be completed for the target protocol and tool.

## 7. Getting the Model Catalog for the Current API Key

First, safely load the API key in Terminal:

```bash
read -s 'AI_GATEWAY_API_KEY?Enter API Key: '
echo
export AI_GATEWAY_API_KEY
export AI_GATEWAY_BASE_URL='https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1'
```

### Query the OpenAI Protocol View

```bash
curl -sS "$AI_GATEWAY_BASE_URL/models" \
  -H "Authorization: Bearer $AI_GATEWAY_API_KEY" \
  | jq -r '.data[]?.id'
```

The models returned here are candidates for OpenAI Chat and OpenAI Responses; this does not mean both endpoints will necessarily succeed.

### Query the Anthropic Protocol View

```bash
curl -sS "$AI_GATEWAY_BASE_URL/models" \
  -H "x-api-key: $AI_GATEWAY_API_KEY" \
  -H 'anthropic-version: 2023-06-01' \
  | jq -r '.data[]?.id'
```

The models returned here are candidates for Anthropic Messages; this does not mean they have been validated with the target tool.

After querying, clean up temporary variables:

```bash
unset AI_GATEWAY_API_KEY
unset AI_GATEWAY_BASE_URL
```

## 8. What Qualifies a Model as "Supported"

It is recommended to use the following standard status names:

| Status | Criteria | How to Describe Externally |
|---|---|---|
| Catalog visible | The corresponding authentication method's `/models` returns the model ID | The current API key can discover this model |
| Protocol text available | The target protocol returns HTTP 200 with final text | A basic text request for this model succeeded on a specific protocol |
| Tool baseline available | The target tool using the correct provider returns final text | This model has passed basic text acceptance on the specified tool |
| Advanced capabilities available | Tool calling, streaming, multimodal, and other specialized tests pass | Only declare capabilities that have been individually validated |
| Stably available | Multiple time points, multiple requests, and actual load tests pass | Stability can be described within the scope of testing |

Do not use the following inferences:

```text
/models lists the model
→ all protocols are supported                   WRONG

curl succeeds
→ all tools are supported                       WRONG

one model succeeds
→ all models from the same vendor succeed        WRONG

basic text succeeds
→ tool calling, streaming, multimodal all work   WRONG
```

## 9. Selecting the Correct Tutorial for Each Tool

| Target Tool | Configuration Guide to Read | Protocol to Confirm First |
|---|---|---|
| WorkBuddy | [WorkBuddy Configuration Guide](aigw_workbuddy_calling.md) | OpenAI Chat Completions |
| OpenClaw | [OpenClaw Configuration Guide](aigw_openclaw_calling.md) | Choose Chat, Responses, or Anthropic based on the model |
| Codex CLI | [Codex CLI Configuration Guide](aigw_codex_calling.md) | OpenAI Responses |
| TRAE International | [TRAE Configuration Guide](aigw_trae_calling.md) | OpenAI Chat or Anthropic Messages |
| Kilo Code | [Kilo Code Configuration Guide](aigw_kilo_calling.md) | Prefer Chat or Anthropic; note known compatibility issue with Responses |
| OpenCode | [OpenCode Configuration Guide](aigw_opencode_calling.md) | Choose Chat, Responses, or Anthropic based on the model |

## 10. Quick Reference

If you only remember six points:

1. WorkBuddy configures custom models using OpenAI Chat only.
2. TRAE custom models support Chat and Anthropic; Responses is not supported.
3. Codex CLI natively uses Responses only.
4. OpenCode and OpenClaw can create separate providers for all three protocols.
5. Kilo Code supports all three providers, but Kilo Code CLI 7.4.22 has a known `SSE-Keep-Alive` compatibility issue with Responses.
6. Every model must go through three layers of validation: real-time catalog → same-protocol curl → actual message in the target tool.

This document covers only basic text connectivity. Streaming output, tool calling, code editing, multimodal, structured output, caching, search, long context, concurrency, and stability must all be tested separately.
