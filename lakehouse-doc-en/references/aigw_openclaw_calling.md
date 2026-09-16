# OpenClaw Integration with AI Gateway: Complete Configuration and Protocol Selection Guide

This document is intended for users setting up a Terminal for the first time, configuring OpenClaw for the first time, or integrating OpenClaw with a third-party AI Gateway.

After completing this guide, you will be able to:

- Install and initialize OpenClaw;
- Securely enter the AI Gateway Base URL and API Key;
- Query the models visible to your API Key;
- Determine whether a model should use OpenAI Chat, OpenAI Responses, or Anthropic Messages;
- Write a tested model into OpenClaw;
- Start the Gateway and confirm the connection with one real message;
- Determine from error messages whether the issue is network, authentication, model routing, or an OpenClaw configuration problem.

This guide uses macOS, zsh, and the following AI Gateway as examples:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1>
~~~

The commands in this guide have been verified against OpenClaw `2026.7.1-2`. A different version number does not necessarily indicate a problem; if command parameters differ, run `--help` for the relevant command first and refer to the official resources in Section 16.

If your address is different, only the Base URL needs to be replaced. Different API Keys may see different models; model IDs must be copied from your own `/models` results.

---

## Summary First: Model Vendor and Request Protocol Are Two Separate Things

OpenClaw does not automatically select a protocol based on the model name. What actually determines the request format is the `api` setting in the OpenClaw provider configuration.

This guide uses three easy-to-identify local provider names:

| Local provider | OpenClaw `api` value | AI Gateway endpoint | When to use |
|---|---|---|---|
| `relay-chat` | `openai-completions` | `/chat/completions` | The model's OpenAI Chat request test succeeded |
| `relay-responses` | `openai-responses` | `/responses` | The model's OpenAI Responses request test succeeded |
| `relay-anthropic` | `anthropic-messages` | `/messages` | The model's Anthropic Messages request test succeeded |

These provider names are local OpenClaw configuration names only — they are not names prescribed by AI Gateway, nor are they vendor names.

If other provider names already exist in OpenClaw (for example `my-relay` or `my-relay-claude`), you do not need to rename them to match the examples in this guide. Continue using the original names and replace `PROVIDER_ID` with your actual provider in Section 10.2; renaming will simultaneously affect the default model and existing session references.

### Selecting a Protocol by Model Vendor

The matrix below is for selecting the first test path — it does not mean every version from a given vendor exposes the same protocol. Specific models must be verified against your directory and the corresponding `curl` results:

| Model vendor or series | OpenAI Chat Completions | OpenAI Responses | Anthropic Messages | OpenClaw configuration recommendation |
|---|---|---|---|---|
| Anthropic Claude | Not the primary choice; only use if the gateway explicitly provides a compatible route and Chat test succeeds | Requires separate testing; cannot be inferred from model name | Native integration path; test first | Use `relay-anthropic` when Messages succeeds |
| OpenAI GPT, Codex series | Common compatible path; requires separate testing | OpenAI native path; requires separate testing | Not the primary choice; only test when the gateway provides a compatible route | Use `relay-chat` if Chat succeeds; use `relay-responses` if Responses succeeds |
| DeepSeek series | Available when the gateway provides a Chat route | Requires separate testing | Available when the gateway provides an Anthropic-compatible route | Use `relay-chat` or `relay-anthropic` based on the successful protocol |
| Qwen series | Available when the gateway provides a Chat route | Requires separate testing | Available when the gateway provides an Anthropic-compatible route | Use `relay-chat` or `relay-anthropic` based on the successful protocol |
| Gemini, Grok, Mistral, Meta, and other series | Available when provided by the gateway; test first | Separate testing when provided by the gateway | Separate testing when provided by the gateway | Use the provider corresponding to the successful protocol |

A vendor's native API may differ from the compatible protocol exposed by the AI Gateway; for example, the same model may appear in both the OpenAI and Anthropic directory views, or only in one of them. Do not choose a provider based solely on a model prefix or vendor name.

The most important rule is:

~~~text
Model vendor
    ≠ Request protocol

Model appears in directory
    ≠ The model is callable

Standard curl succeeds
    ≠ OpenClaw is configured
~~~

You only need to configure providers for the protocols you plan to use. If you only use Claude, you can configure only `relay-anthropic`; if you only use OpenAI Chat, you can configure only `relay-chat`; you do not need to configure all three providers from the start.

---

## 0. Complete Operation Sequence

For a first-time configuration, follow these steps in order:

~~~text
1. Install and initialize OpenClaw
2. Enter Base URL and API Key
3. Query your API Key's model directory
4. Select one model and one target protocol
5. Use the corresponding protocol's curl to obtain final text
6. Configure only this already-successful provider
7. Validate configuration and start Gateway
8. Send a real message with openclaw agent
9. Add other models or protocols as needed
~~~

After completing Step 8, you have basic text conversation capability. See Section 12 for the scope of tool calls, images, files, structured output, and other advanced capabilities.

---

## 1. Prepare Information

Prepare three items before starting.

### 1.1 Base URL

This guide uses:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1>
~~~

This address already includes `/v1`. Do not write it as:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/v1>
~~~

### 1.2 API Key

Create or copy the API Key from the AI Gateway backend and confirm:

- The API Key has not expired;
- The API Key has model call permissions;
- The Base URL and API Key belong to the same environment;
- No extra spaces or line breaks were included when copying.

Do not share your real API Key in chat, support tickets, screenshots, Git repositories, or public web pages.

### 1.3 Terminal

All commands in this guide are run in macOS Terminal.

To open it: press Command + Space, type `Terminal`, and press Enter.

You may see a prompt similar to:

~~~text
user@Mac ~ %
~~~

Do not copy the prompt itself — only copy the commands from the code blocks in this guide.

---

## 2. Install or Confirm OpenClaw

### 2.1 Check Basic Tools

Run:

~~~bash
command -v curl
command -v jq
~~~

If both commands return file paths, you can continue.

If `jq` is missing and Homebrew is installed:

~~~bash
brew install jq
jq --version
~~~

### 2.2 Check OpenClaw

Run:

~~~bash
command -v openclaw
openclaw --version
type -a openclaw
~~~

`command -v` should return the OpenClaw path, and `openclaw --version` should return the version number.

If `type -a openclaw` shows multiple paths, confirm during later troubleshooting that the Terminal and the Gateway service are using the same version.

### 2.3 If Not Installed

On macOS, Linux, or WSL, use the official OpenClaw installation script:

~~~bash
curl -fsSL --proto '=https' --tlsv1.2 \
  https://openclaw.ai/install.sh | bash
~~~

After installation, close Terminal, reopen it, then run:

~~~bash
openclaw --version
~~~

If installation succeeded but `openclaw: command not found` still appears, check:

~~~bash
node -v
npm prefix -g
echo "$PATH"
~~~

Add the `bin` directory corresponding to `npm prefix -g` to your PATH, then reopen Terminal.

---

## 3. Initialize OpenClaw

### 3.1 Existing Configuration

Run first:

~~~bash
openclaw config validate
~~~

If you see:

~~~text
Config valid: ~/.openclaw/openclaw.json
~~~

The existing configuration can be read. Proceed directly to Section 4.

### 3.2 First Time Use

Run:

~~~bash
openclaw onboard
~~~

During the wizard, it is recommended to:

1. Select local mode `local`;
2. Accept the security risk notice;
3. Skip model authentication for now — Section 7 of this guide will configure AI Gateway directly;
4. Skip channel configuration if no chat channel is available yet;
5. Choose to install the Gateway as a local service;
6. Skip search, skills, and plugins if unsure; configure them after the basic connection is established.

After the wizard completes, run:

~~~bash
openclaw config validate
openclaw config get gateway.mode
openclaw agents list
~~~

Under normal circumstances, config validation passes, `gateway.mode` returns `local`, and at least the default agent is visible:

~~~text
main
~~~

If `gateway.mode` does not return `local`, run:

~~~bash
openclaw config set gateway.mode local
openclaw config validate
~~~

`gateway.mode=local` means OpenClaw uses the local Gateway. Without this configuration, the Gateway may refuse to start even if the provider configuration itself is valid.

If you previously created a `custom` Token provider or authentication profile in the wizard, you can keep it. An authentication profile does not automatically populate the Base URL, protocol, and model list — you still need to complete the provider configuration in the rest of this guide.

---

## 4. Securely Enter Connection Information in the Current Terminal

Run the following in the same Terminal:

~~~bash
export RELAY_BASE_URL='https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1'
RELAY_BASE_URL="${RELAY_BASE_URL%/}"

read -s "RELAY_API_KEY?Paste your AI Gateway API Key, then press Enter: "
echo
~~~

It is normal that no characters appear on screen when pasting the API Key.

Only check whether the variable exists — do not display the API Key:

~~~bash
if [ -n "$RELAY_API_KEY" ]; then
  echo 'API Key loaded into current Terminal'
else
  echo 'API Key is empty, please re-enter'
fi
~~~

Normal output:

~~~text
API Key loaded into current Terminal
~~~

To allow a restarted background Gateway to also read the token, save it to the environment file in the OpenClaw user directory. This file is stored only on the local machine with permissions restricted to the current user:

~~~bash
mkdir -p "$HOME/.openclaw"
(umask 077; printf 'RELAY_API_KEY=%s\n' "$RELAY_API_KEY" > "$HOME/.openclaw/.env")
chmod 600 "$HOME/.openclaw/.env"
~~~

If this file already exists, the command above will overwrite the old content with the current API Key input. Run this before starting or restarting the Gateway — do not skip it.

The provider configuration below uses SecretRef, so the token is not written in plaintext to `openclaw.json`. If authentication errors appear after a restart, follow Section 13.13 to confirm whether the Gateway service can read `~/.openclaw/.env`.

Variables will disappear after closing Terminal. Continue using the current window until Section 7 is complete.

---

## 5. Check Network and Query Model Directory

### 5.1 Check OpenAI-Style Connection First

Run:

~~~bash
curl -sS -o /tmp/openclaw-gateway-models-openai.json \
  --max-time 30 \
  -w 'HTTP %{http_code}\n' \
  "$RELAY_BASE_URL/models" \
  -H "Authorization: Bearer $RELAY_API_KEY"
~~~

Return value meanings:

| Return | Meaning | Next step |
|---|---|---|
| HTTP 200 | Network and Bearer authentication are normal | View model directory |
| HTTP 401 | API Key missing, incorrect, or expired | Re-enter API Key |
| HTTP 403 | API Key rejected or insufficient current permissions | Check account, tenant, and permissions |
| HTTP 404 | Base URL or `/v1` path error | Check address, avoid duplicate `/v1` |
| HTTP 429 | Quota, concurrency, or rate limiting | Wait and retry, or check quota |
| HTTP 5xx | AI Gateway or upstream temporarily unavailable | Retry later and save sanitized error |
| No HTTP status, DNS, or connection timeout | Request did not reach AI Gateway normally | Check network, proxy, firewall, or VPN |

If you have already received 200, 401, 403, 404, 429, or 5xx, the domain is reachable, and this is generally not a problem that requires a VPN to solve. Only check proxy or VPN when DNS resolution fails, connection times out, or network policy blocks the connection.

### 5.2 View the OpenAI View

After HTTP 200, run:

~~~bash
jq -r '
  if (.data | type) == "array" then
    .data[].id
  else
    .error.message // .message // "No model directory found"
  end
' /tmp/openclaw-gateway-models-openai.json
~~~

This list is used to select candidate models for OpenAI Chat or OpenAI Responses. The list only means the current API Key can see these models — the specific endpoints still need to be tested.

### 5.3 View the Anthropic View

Only run this if you plan to use Anthropic Messages or Claude:

~~~bash
curl -sS -o /tmp/openclaw-gateway-models-anthropic.json \
  --max-time 30 \
  -w 'HTTP %{http_code}\n' \
  "$RELAY_BASE_URL/models" \
  -H "x-api-key: $RELAY_API_KEY" \
  -H 'anthropic-version: 2023-06-01'

jq -r '
  if (.data | type) == "array" then
    .data[].id
  else
    .error.message // .message // "No Anthropic model directory found"
  end
' /tmp/openclaw-gateway-models-anthropic.json
~~~

If the OpenAI view and Anthropic view differ, this is normal. Different request headers and protocol context can cause AI Gateway to return different model directories.

### 5.4 Model IDs Must Be Copied Exactly

The model ID is the routing key for AI Gateway. Version numbers, dots, hyphens, and vendor prefixes may all be part of the ID.

Do not:

- Write a model ID by hand based on display names found online;
- Remove the vendor prefix from a model ID;
- Change dots to hyphens;
- Assume another version is available just because one version of the same series works.

If the target model is not in your directory, confirm API Key permissions first — do not proceed with forced configuration.

---

## 6. Verify the Target Model with the Corresponding Protocol

Only test the protocols you plan to use. Each test must satisfy both: HTTP 200, and a final text response in the response body.

### 6.1 OpenAI Chat Completions

Copy a complete model ID from the results in Section 5.2:

~~~bash
read "CHAT_MODEL_ID?Paste the complete model ID you plan to use with Chat protocol: "
~~~

Run:

~~~bash
curl -sS -o /tmp/openclaw-test-chat.json \
  --max-time 60 \
  -w 'HTTP %{http_code}\n' \
  "$RELAY_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $RELAY_API_KEY" \
  -H 'Content-Type: application/json' \
  -d "$(jq -cn \
    --arg model "$CHAT_MODEL_ID" \
    '{
      model: $model,
      max_tokens: 512,
      messages: [{role: "user", content: "Reply only: Chat connection succeeded"}]
    }')"

jq -r '
  .choices[0].message.content
  // .error.message
  // .message
  // "HTTP returned, but no final text found"
' /tmp/openclaw-test-chat.json
~~~

On success you should see:

~~~text
HTTP 200
Chat connection succeeded
~~~

If successful, you can use the `relay-chat` configuration in Section 7.2.

### 6.2 OpenAI Responses

Copy a complete model ID from the results in Section 5.2:

~~~bash
read "RESPONSES_MODEL_ID?Paste the complete model ID you plan to use with Responses protocol: "
~~~

Run:

~~~bash
curl -sS -o /tmp/openclaw-test-responses.json \
  --max-time 60 \
  -w 'HTTP %{http_code}\n' \
  "$RELAY_BASE_URL/responses" \
  -H "Authorization: Bearer $RELAY_API_KEY" \
  -H 'Content-Type: application/json' \
  -d "$(jq -cn \
    --arg model "$RESPONSES_MODEL_ID" \
    '{
      model: $model,
      input: "Reply only: Responses connection succeeded",
      max_output_tokens: 512
    }')"

jq -r '
  ([.output[]?.content[]? | select(.type == "output_text" or .type == "text") | .text] | join("\n")) as $text
  | if ($text | length) > 0 then
      $text
    else
      .error.message // .message // "HTTP returned, but no final text found"
    end
' /tmp/openclaw-test-responses.json
~~~

On success you should see:

~~~text
HTTP 200
Responses connection succeeded
~~~

If successful, you can use the `relay-responses` configuration in Section 7.3.

### 6.3 Anthropic Messages

Copy a complete model ID from the results in Section 5.3:

~~~bash
read "ANTHROPIC_MODEL_ID?Paste the complete model ID you plan to use with Anthropic protocol: "
~~~

Run:

~~~bash
curl -sS -o /tmp/openclaw-test-anthropic.json \
  --max-time 60 \
  -w 'HTTP %{http_code}\n' \
  "$RELAY_BASE_URL/messages" \
  -H "x-api-key: $RELAY_API_KEY" \
  -H 'anthropic-version: 2023-06-01' \
  -H 'Content-Type: application/json' \
  -d "$(jq -cn \
    --arg model "$ANTHROPIC_MODEL_ID" \
    '{
      model: $model,
      max_tokens: 1024,
      messages: [{role: "user", content: "Reply only: Anthropic connection succeeded"}]
    }')"

jq -r '
  ([.content[]? | select(.type == "text") | .text] | join("\n")) as $text
  | if ($text | length) > 0 then
      $text
    else
      .error.message // .message // "HTTP returned, but no final text found"
    end
' /tmp/openclaw-test-anthropic.json
~~~

On success you should see:

~~~text
HTTP 200
Anthropic connection succeeded
~~~

If successful, you can use the `relay-anthropic` configuration in Section 7.4.

### 6.4 HTTP 200 but No Final Text

Some reasoning models may generate thinking or reasoning content first. When the output budget is too small, the request may return HTTP 200 but no final text.

Try increasing:

~~~text
max_tokens: 512
max_output_tokens: 512
~~~

to 1024 or 4096, then test again.

If there is still no final text after increasing the budget, inspect the full JSON and confirm whether the response structure matches the current protocol.

---

## 7. Write the Tested Model into OpenClaw

This section provides three independent options. Select the one whose curl succeeded for your first configuration — do not copy all three options at once.

### 7.1 Back Up Configuration First

Run:

~~~bash
CONFIG_FILE="$HOME/.openclaw/openclaw.json"

if [ -f "$CONFIG_FILE" ]; then
  cp "$CONFIG_FILE" \
    "$CONFIG_FILE.backup-$(date +%Y%m%d-%H%M%S)"
  echo 'OpenClaw configuration backup created'
else
  echo 'No configuration file found; OpenClaw will create a new one'
fi
~~~

### 7.2 Option A: Configure OpenAI Chat

Only run this if Section 6.1 succeeded:

~~~bash
CHAT_PROVIDER=$(jq -cn \
  --arg base "$RELAY_BASE_URL" \
  --arg model "$CHAT_MODEL_ID" \
  '{
    baseUrl: $base,
    apiKey: {source: "env", provider: "default", id: "RELAY_API_KEY"},
    api: "openai-completions",
    models: [{id: $model, name: $model}]
  }')

openclaw config set \
  models.providers.relay-chat \
  "$CHAT_PROVIDER" \
  --strict-json

CHAT_MODEL_REF="relay-chat/$CHAT_MODEL_ID"
CHAT_CATALOG_ENTRY=$(jq -cn \
  --arg ref "$CHAT_MODEL_REF" \
  '{($ref): {}}')

openclaw config set \
  agents.defaults.models \
  "$CHAT_CATALOG_ENTRY" \
  --strict-json \
  --merge

openclaw models set "$CHAT_MODEL_REF"
openclaw config validate
~~~

### 7.3 Option B: Configure OpenAI Responses

Only run this if Section 6.2 succeeded:

~~~bash
RESPONSES_PROVIDER=$(jq -cn \
  --arg base "$RELAY_BASE_URL" \
  --arg model "$RESPONSES_MODEL_ID" \
  '{
    baseUrl: $base,
    apiKey: {source: "env", provider: "default", id: "RELAY_API_KEY"},
    api: "openai-responses",
    models: [{id: $model, name: $model}]
  }')

openclaw config set \
  models.providers.relay-responses \
  "$RESPONSES_PROVIDER" \
  --strict-json

RESPONSES_MODEL_REF="relay-responses/$RESPONSES_MODEL_ID"
RESPONSES_CATALOG_ENTRY=$(jq -cn \
  --arg ref "$RESPONSES_MODEL_REF" \
  '{($ref): {}}')

openclaw config set \
  agents.defaults.models \
  "$RESPONSES_CATALOG_ENTRY" \
  --strict-json \
  --merge

openclaw models set "$RESPONSES_MODEL_REF"
openclaw config validate
~~~

### 7.4 Option C: Configure Anthropic Messages

Only run this if Section 6.3 succeeded:

~~~bash
ANTHROPIC_PROVIDER=$(jq -cn \
  --arg base "$RELAY_BASE_URL" \
  --arg model "$ANTHROPIC_MODEL_ID" \
  '{
    baseUrl: $base,
    apiKey: {source: "env", provider: "default", id: "RELAY_API_KEY"},
    api: "anthropic-messages",
    models: [{id: $model, name: $model}]
  }')

openclaw config set \
  models.providers.relay-anthropic \
  "$ANTHROPIC_PROVIDER" \
  --strict-json

ANTHROPIC_MODEL_REF="relay-anthropic/$ANTHROPIC_MODEL_ID"
ANTHROPIC_CATALOG_ENTRY=$(jq -cn \
  --arg ref "$ANTHROPIC_MODEL_REF" \
  '{($ref): {}}')

openclaw config set \
  agents.defaults.models \
  "$ANTHROPIC_CATALOG_ENTRY" \
  --strict-json \
  --merge

openclaw models set "$ANTHROPIC_MODEL_REF"
openclaw config validate
~~~

### 7.5 Expected Result

You must see at the end:

~~~text
Config valid: ~/.openclaw/openclaw.json
~~~

The commands above only modify the selected provider and add the model catalog entry using `--merge` — they will not delete models from other providers.

`openclaw models set` sets the just-configured model as the default. If you only want to add a model without changing the current default, skip this line and specify the full model reference later using `--model`.

This guide does not write `contextWindow`, `maxTokens`, `reasoning`, or multimodal capability fields uniformly for all models. These values must have explicit documentation from the corresponding model or AI Gateway; copying uniform values arbitrarily may cause truncation, parameter errors, or incorrect capability display.

---

## 8. Start the Gateway and Check Models

### 8.1 Restart the Gateway

Run:

~~~bash
openclaw gateway restart
~~~

If prompted that the Gateway service is not installed:

~~~bash
openclaw gateway install
openclaw gateway start
~~~

After modifying `~/.openclaw/.env`, run `openclaw gateway restart` to let the Gateway re-read the API Key.

If you modified the Gateway port or other service installation parameters, regenerate the background service configuration:

~~~bash
openclaw gateway install --force
openclaw gateway restart
~~~

### 8.2 Check Running Status

Run:

~~~bash
openclaw gateway status
~~~

Look for:

~~~text
Runtime: running
Connectivity probe: ok
~~~

If the CLI and Gateway versions are inconsistent in the version info, restart the Gateway first. If they are still inconsistent, check `type -a openclaw` to confirm whether multiple versions are installed.

### 8.3 View the Just-Configured Provider

Based on your actual selection, run only the corresponding command.

Configured OpenAI Chat:

~~~bash
openclaw models list --provider relay-chat --plain
~~~

Configured OpenAI Responses:

~~~bash
openclaw models list --provider relay-responses --plain
~~~

Configured Anthropic Messages:

~~~bash
openclaw models list --provider relay-anthropic --plain
~~~

You should see a structure similar to:

~~~text
relay-chat/<model ID copied from directory>
relay-responses/<model ID copied from directory>
relay-anthropic/<model ID copied from directory>
~~~

The text in angle brackets is explanatory — do not enter it literally.

View the default model:

~~~bash
openclaw models status --plain
~~~

---

## 9. Send the First Message with OpenClaw

### 9.1 Test the Default Model

This section requires that you ran `openclaw models set` in Section 7. If you skipped that command to preserve the original default model, go directly to Section 9.2 and specify the full model reference using `--model`.

Run:

~~~bash
openclaw agent \
  --agent main \
  --message 'Reply only: OpenClaw connection succeeded'
~~~

Expected final text:

~~~text
OpenClaw connection succeeded
~~~

The success criterion is that the command ultimately returns model text — not just seeing the Gateway started or the model appearing in a list.

### 9.2 Test a Specific Model

To bypass the default model, use the full OpenClaw model reference:

~~~bash
openclaw agent \
  --agent main \
  --model "relay-chat/$CHAT_MODEL_ID" \
  --message 'Reply only: Specified model connection succeeded'
~~~

If Responses or Anthropic is configured, change `--model` to:

~~~text
relay-responses/<model ID>
relay-anthropic/<model ID>
~~~

### 9.3 Why `--agent main` Is Required

If you run only:

~~~bash
openclaw agent --message 'Hello'
~~~

You may see:

~~~text
Error: No target session selected.
~~~

Adding `--agent main` tells OpenClaw which agent to use.

### 9.4 Plugin Warnings Are Not Necessarily Model Errors

If before the reply you see:

~~~text
plugins.allow is empty
discovered non-bundled plugins may auto-load
~~~

This is a plugin trust notice. As long as the expected model text is returned at the end, the AI Gateway connection has succeeded. Whether to enable plugins should be handled separately based on the plugin source.

---

## 10. Adding a Second Protocol or More Models

### 10.1 Adding a Second Protocol

For example, `relay-chat` is already configured and you now want to use Claude:

1. Run Section 5.3 to query the Anthropic directory;
2. Run Section 6.3 to test the target model;
3. Run Section 7.4 to add `relay-anthropic`;
4. Restart the Gateway;
5. Send a test message using `--model relay-anthropic/<model ID>`.

Adding a second provider does not require re-running `openclaw onboard`.

### 10.2 Adding a Model to an Existing Provider

First test the new model with the corresponding protocol from Section 6. After success, set:

~~~bash
PROVIDER_ID='relay-chat'
read "NEW_MODEL_ID?Paste the new model ID that has already passed the same-protocol test: "
~~~

`PROVIDER_ID` must correspond to the test protocol:

| Protocol | `PROVIDER_ID` |
|---|---|
| OpenAI Chat | `relay-chat` |
| OpenAI Responses | `relay-responses` |
| Anthropic Messages | `relay-anthropic` |

Run:

~~~bash
CURRENT_PROVIDER_MODELS=$(openclaw config get \
  "models.providers.$PROVIDER_ID.models")

UPDATED_PROVIDER_MODELS=$(printf '%s' "$CURRENT_PROVIDER_MODELS" | jq \
  --arg id "$NEW_MODEL_ID" \
  '. + [{id: $id, name: $id}] | unique_by(.id)')

openclaw config set \
  "models.providers.$PROVIDER_ID.models" \
  "$UPDATED_PROVIDER_MODELS" \
  --strict-json \
  --replace

NEW_MODEL_REF="$PROVIDER_ID/$NEW_MODEL_ID"
NEW_CATALOG_ENTRY=$(jq -cn \
  --arg ref "$NEW_MODEL_REF" \
  '{($ref): {}}')

openclaw config set \
  agents.defaults.models \
  "$NEW_CATALOG_ENTRY" \
  --strict-json \
  --merge

openclaw config validate
openclaw gateway restart
~~~

Test the new model:

~~~bash
openclaw agent \
  --agent main \
  --model "$NEW_MODEL_REF" \
  --message 'Reply only: New model connection succeeded'
~~~

To set it as the default model:

~~~bash
openclaw models set "$NEW_MODEL_REF"
~~~

---

## 11. Request Protocol and Configuration Boundaries

### 11.1 The Three Protocols Cannot Be Mixed

| Item | OpenAI Chat Completions | OpenAI Responses | Anthropic Messages |
|---|---|---|---|
| Request path | `/chat/completions` | `/responses` | `/messages` |
| Authentication header | `Authorization: Bearer` | `Authorization: Bearer` | `x-api-key` + `anthropic-version` |
| Primary input field | `messages` | `input` | `messages`, system prompt typically uses top-level `system` |
| Common output limit | `max_tokens` | `max_output_tokens` | `max_tokens` |
| Final text location | `choices[].message.content` | `output[].content[].text` | `type=text` items in `content[]` |
| OpenClaw `api` | `openai-completions` | `openai-responses` | `anthropic-messages` |

Changing only the URL or model name cannot convert one protocol into another. The endpoint, authentication header, request body, streaming events, and tool call structure must all match together.

### 11.2 Model ID Prefixes Do Not Switch the Protocol

Suppose a model ID starts with `anthropic/`:

~~~text
relay-chat/anthropic/<model name>
~~~

It will still use OpenAI Chat, because the local provider is `relay-chat`.

Only:

~~~text
relay-anthropic/anthropic/<model name>
~~~

will use Anthropic Messages as configured in this guide.

Similarly, `openai/`, `deepseek/`, `qwen/`, or other prefixes are simply parts of the AI Gateway model ID.

### 11.3 The Same Model May Support Multiple Protocols

If the same model passes both the Chat and Anthropic Messages tests, it can be added to both providers:

~~~text
relay-chat/<same model ID>
relay-anthropic/<same model ID>
~~~

These are two different OpenClaw model references. They use different request formats, and errors and capability behavior may differ.

### 11.4 Success with One Protocol Does Not Imply Success with Another

Any of the following situations may occur:

~~~text
Chat succeeds, Responses fails
Responses succeeds, Chat fails
Anthropic succeeds, OpenAI protocol fails
Same model succeeds in both protocols, but tool call behavior differs
~~~

Therefore, each provider must first run the corresponding curl, then run an actual OpenClaw message test.

### 11.5 What the Directory, curl, and OpenClaw Each Indicate

| What you see | What it indicates | Next step |
|---|---|---|
| Model present in `/models` | The current API Key can see the model ID in this directory view | Test the target protocol |
| Same-protocol curl returns HTTP 200 and final text | The AI Gateway model route can complete a basic text request | Configure the corresponding provider |
| `openclaw models list` shows the model | The local provider and model catalog entry have been written | Restart Gateway and send a message |
| `openclaw agent` returns final text | OpenClaw, Gateway, provider, model, and the basic text chain are all connected | Start using or continue testing advanced capabilities |

### 11.6 Do Not Guess Context Window and Output Limits

`contextWindow`, `contextTokens`, `maxTokens`, `reasoning`, and input types are model capability information — they are not fixed values that apply universally to all models.

The minimal provider configuration in this guide only writes:

~~~text
id
name
~~~

Other fields should only be added when explicitly provided by AI Gateway or model documentation and verified through actual testing.

---

## 12. What Capabilities Are Available After Configuration

Completing Section 9 means the basic text chain is working: you can send text to OpenClaw and receive the model's final text reply.

Whether the following capabilities are available also depends on the combined implementation of the model, request protocol, AI Gateway, and OpenClaw provider:

- Streaming output and mid-stream cancellation;
- Tool calls and multi-turn tool result callbacks;
- JSON Schema or structured output;
- Image, PDF, audio, and other multimodal inputs;
- Prompt Cache or other caching capabilities;
- Web Search;
- Extended Thinking, reasoning effort, or other reasoning parameters;
- Extra-long context;
- Automatic failover and fallback models.

If you only need ordinary text conversation, you can start using after Section 9 succeeds. If you need the above capabilities, test each one separately for the models and protocols you plan to use.

OpenClaw's agent may also have permissions to read files, run commands, or call tools. Before enabling such capabilities, also check the agent, workspace, sandbox, tool permissions, and chat channel access controls — a successful model connection does not mean all local permissions should be opened.

---

## 13. Troubleshooting

### 13.1 No Characters Appear When Pasting API Key

This is normal. `read -s` hides input. Paste and press Enter.

### 13.2 `expected object, received string`

This typically means an ellipsis or plain string was written into the provider object. For example:

~~~bash
openclaw config set models.providers.relay-anthropic ...
~~~

`...` is only a shorthand in documentation and cannot be run literally. Re-run the complete JSON configuration commands from Section 7.

### 13.3 `No target session selected`

Add to the agent command:

~~~text
--agent main
~~~

If `main` does not exist, run:

~~~bash
openclaw agents list
~~~

and replace `main` with the actual agent ID.

### 13.4 `Model ... is not allowed` or `model not found`

Check in order:

1. Run `openclaw models list --provider <provider> --plain`;
2. Confirm you are using the full OpenClaw reference: `provider/AI-Gateway-model-ID`;
3. Confirm the model has been added to `models.providers.<provider>.models`;
4. Confirm the model has been added to `agents.defaults.models` using `--merge`;
5. Run `openclaw config validate`;
6. Restart the Gateway and try again.

### 13.5 HTTP 401 or 403

Common causes:

- API Key is incorrect, expired, or has no permissions;
- Chat/Responses request incorrectly uses `x-api-key`;
- Anthropic request is missing `x-api-key` or `anthropic-version`;
- Base URL and API Key do not belong to the same environment.

Return to Section 5 to recheck authentication headers and directory requests.

### 13.6 `No upstream candidates`

Means the combination of "model ID + protocol + API Key/tenant" has no available upstream. Common causes:

- Model ID is misspelled;
- Provider uses the wrong protocol;
- API Key does not have permission for the corresponding model;
- AI Gateway has no model route configured for this protocol;
- Upstream is temporarily offline.

Resolution: re-query the corresponding directory, copy the model ID exactly, then test with the same-protocol curl from Section 6.

### 13.7 HTTP 502 or 503 `Upstream failed`

The request reached AI Gateway but the upstream model call failed. Retry later. If failures persist, save the following information:

- Time of occurrence and timezone;
- Full model ID;
- Request protocol and path;
- HTTP status code;
- Error JSON with the API Key removed.

Do not try to resolve upstream 5xx errors by modifying the OpenClaw provider name.

### 13.8 HTTP 200 but No Final Text

Increase the output budget and check the correct text field for the current protocol:

~~~text
Chat       → choices[].message.content
Responses  → output[].content[].text
Anthropic  → type=text items in content[]
~~~

If the JSON contains only thinking or reasoning content, the output budget may have been consumed by the reasoning process.

### 13.9 curl Succeeds but OpenClaw Fails

Run:

~~~bash
openclaw config validate
openclaw gateway status
openclaw models status --plain
openclaw agents list
~~~

Check:

- Whether the provider's `api` matches the curl protocol;
- Whether the provider's `baseUrl` matches the address used in curl;
- Whether the full model reference contains the correct local provider;
- Whether the Gateway was restarted after the configuration was modified;
- Whether `--agent` uses the actual agent ID.

### 13.10 Gateway Is Not `running`

Run:

~~~bash
openclaw gateway install
openclaw gateway start
openclaw gateway status
~~~

If still failing, run:

~~~bash
openclaw config validate
openclaw doctor
~~~

### 13.11 CLI and Gateway Versions Differ

Run:

~~~bash
type -a openclaw
openclaw --version
openclaw gateway status
~~~

If multiple OpenClaw installations exist on the system, unify PATH first, then reinstall or restart the Gateway service.

### 13.12 Restore a Configuration Backup

View backups:

~~~bash
ls -lt "$HOME/.openclaw"/openclaw.json.backup-* 2>/dev/null \
  | sed -n '1,5p'
~~~

Copy the exact backup filename, then restore:

~~~bash
cp "$HOME/.openclaw/openclaw.json.backup-actual-timestamp" \
  "$HOME/.openclaw/openclaw.json"

openclaw config validate
openclaw gateway restart
~~~

Do not enter "actual-timestamp" literally — replace it with the filename shown by the previous command.

### 13.13 Authentication Failure After Restart

If curl in the current Terminal succeeds but OpenClaw reports 401, 403, or missing API Key after restarting the Gateway, the background service typically cannot read the user-level environment file. Check in order:

1. Confirm the file exists and has correct permissions:

~~~bash
ls -l "$HOME/.openclaw/.env"
~~~

The file should belong to the current user and its permissions should not allow other users to read it.

2. Re-write the environment file (will not display the token on screen):

~~~bash
read -s "RELAY_API_KEY?Re-paste your AI Gateway API Key, then press Enter: "
echo
(umask 077; printf 'RELAY_API_KEY=%s\n' "$RELAY_API_KEY" > "$HOME/.openclaw/.env")
chmod 600 "$HOME/.openclaw/.env"
~~~

3. Restart the service and recheck:

~~~bash
openclaw gateway restart
openclaw gateway status
~~~

If still failing, run:

~~~bash
openclaw doctor
openclaw gateway diagnostics export
~~~

`openclaw gateway diagnostics export` generates a diagnostic archive for troubleshooting. Before submitting to service support, check the file contents to confirm it does not contain the API Key or other sensitive information. You can also run `openclaw gateway diagnostics --help` to view the diagnostic parameters available in the current version.

---

## 14. API Key and Local Security

The OpenClaw configuration file is typically located at:

~~~text
~/.openclaw/openclaw.json
~~~

The provider configuration in this guide uses SecretRef. `openclaw.json` stores provider information and token references; the API Key is read from `~/.openclaw/.env`. Restrict permissions on both files:

~~~bash
chmod 600 "$HOME/.openclaw/openclaw.json"
chmod 600 "$HOME/.openclaw/.env"

find "$HOME/.openclaw" -maxdepth 1 \
  -name 'openclaw.json.backup-*' \
  -exec chmod 600 {} \;
~~~

Historical configuration backups may contain old API Keys and therefore need the same protection.

Do not:

- Upload `openclaw.json`;
- Screenshot the full configuration;
- Run `echo "$RELAY_API_KEY"`;
- Paste full request headers into public support tickets;
- Write API Keys into project repositories;
- Share long-lived high-privilege API Keys with others.

After configuration is complete, clear the temporary variables in the current Terminal:

~~~bash
unset RELAY_API_KEY
unset RELAY_BASE_URL
unset CHAT_MODEL_ID
unset RESPONSES_MODEL_ID
unset ANTHROPIC_MODEL_ID
~~~

If the API Key has appeared in a public screenshot, chat message, or command output, immediately revoke it in the AI Gateway backend and create a new one.

OpenClaw Gateway is recommended to bind to the local loopback by default. Unless remote access is explicitly needed and authentication, firewall, and access controls are configured, do not expose the Gateway directly to the local network or the internet.

---

## 15. Completion Checklist

Confirm each item after configuration is complete:

~~~text
[ ] curl and jq are executable
[ ] openclaw --version returns a version number
[ ] openclaw config validate returns Config valid
[ ] Base URL is correct, /v1 is not duplicated
[ ] API Key has been securely entered and not exposed
[ ] Queried the model directory for the target protocol
[ ] Model ID copied exactly from your own directory
[ ] Target protocol curl returned HTTP 200
[ ] curl response contains final text
[ ] OpenClaw provider api matches the curl protocol
[ ] agents.defaults.models has model added using --merge
[ ] openclaw gateway status shows Runtime: running
[ ] Connectivity probe shows ok
[ ] openclaw models list shows full provider/model reference
[ ] openclaw agent --agent main returns final text
[ ] Advanced capabilities tested individually as needed
[ ] openclaw.json file permissions are restricted
[ ] ~/.openclaw/.env and configuration backup file permissions are restricted
~~~

Once all items are complete, OpenClaw has successfully integrated with AI Gateway.

If `/models` succeeds but curl fails, start troubleshooting from the protocol and upstream routing. If curl succeeds but OpenClaw fails, start troubleshooting from the provider `api`, full model reference, Gateway status, and agent ID.

---

## 16. References

- [OpenClaw Installation Guide](https://docs.openclaw.ai/install)
- [OpenClaw Model Providers](https://docs.openclaw.ai/concepts/model-providers)
- [OpenClaw Models CLI](https://docs.openclaw.ai/models)
- [OpenClaw Agent CLI](https://docs.openclaw.ai/cli/agent)
- [OpenClaw Gateway CLI](https://docs.openclaw.ai/cli/gateway)

Both OpenClaw and AI Gateway may be upgraded. When command parameter differences are encountered, run first:

~~~bash
openclaw --version
openclaw config set --help
openclaw agent --help
openclaw gateway --help
~~~

Use the parameters shown by the currently installed version as the reference.
