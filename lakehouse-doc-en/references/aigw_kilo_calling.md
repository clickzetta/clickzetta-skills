This guide is for users who are using Terminal for the first time, configuring Kilo Code for the first time, or connecting Kilo Code to a third-party AI Gateway.

After completing this guide, you will be able to:

- Install and verify Kilo Code CLI or Kilo Code for VS Code;
- Securely enter the AI Gateway Base URL and API Key;
- Query the models visible to your API Key;
- Choose between OpenAI Chat, OpenAI Responses, or Anthropic Messages based on the model vendor and actual routing;
- Use standard curl to verify that a model can return final text;
- Write verified models into the Kilo global configuration;
- Send your first message using `kilo run` or the Kilo GUI;
- Add a second protocol or more models;
- Diagnose errors as network, authentication, model routing, Kilo configuration, or advanced capabilities issues.

This guide uses macOS, zsh, and the following AI Gateway as examples:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1>
~~~

The commands in this guide have been verified against Kilo Code CLI 7.4.22. A different version number does not necessarily mean there is a problem; if command parameters or interface fields differ, run the corresponding command with `--help` first and refer to the official resources in Section 16.

~~~text
Last verified date: 2026-08-19
Verification environment: macOS, zsh, Kilo Code CLI 7.4.22
Verification scope: model directory, basic text curl, Kilo configuration loading, and Kilo basic text messages
~~~

If your address is different, simply replace the Base URL. Different API Keys may see different models; model IDs must be copied from your own /models results.

> Security note: Never share your real API Key in chats, tickets, screenshots, Git repositories, or public web pages. This guide uses a separate key file to store the API Key; the Kilo configuration file only stores a file reference, not the token in plain text.

---

## Summary First: Model Vendor and Request Protocol Are Two Different Things

Kilo does not automatically select a protocol based on the model name. What actually determines the request format is the Provider API and npm runtime of the Kilo custom provider.

This guide uses three easily recognizable local provider names:

| Local provider | Kilo Provider API | npm runtime | AI Gateway endpoint | Usage condition |
|---|---|---|---|---|
| relay-chat | OpenAI Compatible | @ai-sdk/openai-compatible | /chat/completions | Both Chat curl and `kilo run` succeed |
| relay-responses | OpenAI Responses | @ai-sdk/openai | /responses | Both Responses curl and `kilo run` succeed |
| relay-anthropic | Anthropic Messages | @ai-sdk/anthropic | /messages | Both Anthropic curl and `kilo run` succeed |

These provider names are only local Kilo configuration names — not names mandated by AI Gateway or model vendors. If other provider names already exist in Kilo, there is no need to rename them to match this guide's examples; keep the original names and replace the provider IDs in this guide's commands with your actual names.

### Choosing a Protocol by Model Vendor

The matrix below is only for determining which protocol to test first. It does not mean all models from that vendor can be called via that protocol. The final determination is based on your own model directory, standard curl, and actual Kilo message test results.

Known compatibility note: In the example gateway in this guide, Kilo Code 7.4.22, and `@ai-sdk/openai` combination, when verifying with `openai/gpt-5.5`, a non-streaming curl request to `/responses` returns HTTP 200, but actual Kilo messages fail with `text part SSE-Keep-Alive not found` because the gateway stream includes `SSE-Keep-Alive` events. When you encounter this message, Responses cannot be considered connected in Kilo; switch to the OpenAI Chat provider already verified with `kilo run`, or wait for a gateway/Kilo version fix and re-run the Section 9 tests. This limitation does not affect the Chat and Anthropic Messages paths on the same gateway that have already passed Kilo live testing.

### Protocol Verification Status for the Current Version

The following results describe the protocol compatibility status between the example gateway in this guide and Kilo Code CLI 7.4.22. They do not limit the range of models available to other API Keys:

| Protocol path | Verified model | Model Catalog | Standard non-streaming curl | Kilo basic text message | Current recommendation |
|---|---|---|---|---|---|
| OpenAI Chat Completions | `qwen/qwen3.6-flash` | Queryable | Success | Success | Can be used for Kilo basic text integration; other models still need individual verification |
| Anthropic Messages | `anthropic/claude-opus-5` | Queryable | Success | Success | Can be used for Kilo basic text integration; other models still need individual verification |
| OpenAI Responses | `openai/gpt-5.5` | Queryable | Success | Failed: `SSE-Keep-Alive` event incompatible | Not recommended for use in Kilo at this time; re-verify after fix |

"Kilo basic text message success" here means `kilo run` can return final text. File editing, command execution, tool calls, and multimodal capabilities still require separate verification per Section 12.

| Model vendor or series | Recommended first-round test protocol | Other protocols to try | Decision criteria when configuring | Kilo provider |
|---|---|---|---|---|
| Anthropic Claude | Anthropic Messages | Test OpenAI Chat or Responses only when AI Gateway explicitly provides a compatible route and standard requests succeed | A model ID containing anthropic/ does not automatically switch protocols | relay-anthropic |
| OpenAI GPT, Codex, o-series | Test OpenAI Chat Completions first in the current example environment | After gateway or Kilo fix, Responses can be re-tested | Do not default to Anthropic Messages; every Responses model must pass a Kilo live message test | relay-chat; relay-responses can also be used after verification |
| DeepSeek | OpenAI Chat Completions | Test Anthropic Messages when AI Gateway provides an Anthropic-compatible route | Responses availability cannot be inferred from the model name alone | relay-chat or relay-anthropic |
| Alibaba Qwen | OpenAI Chat Completions | Test Responses or Anthropic Messages when AI Gateway provides them for a specific model | Cannot infer that the current model supports the same protocol just because another model from the same vendor works | Choose based on successful protocol |
| Google Gemini | The compatible protocol specified by AI Gateway | Both OpenAI and Anthropic compatible routes need separate testing | The three providers in this guide do not call the native Gemini API directly | Choose based on AI Gateway routing |
| xAI Grok | Test the OpenAI Chat-compatible path specified by AI Gateway first in the current example environment | After gateway or Kilo fix, Responses can be re-tested | Do not default to Anthropic Messages; base decisions on curl and Kilo results for specific models | relay-chat; relay-responses can also be used after verification |
| MiniMax | Anthropic Messages | Test OpenAI-compatible routes only when AI Gateway explicitly provides them | Cannot assume all MiniMax models use the same protocol | Prefer relay-anthropic |
| Mistral, Meta Llama, Moonshot/Kimi, Zhipu/GLM, and other series | Usually test OpenAI Chat Completions first | Test Responses or Anthropic Messages only when AI Gateway explicitly provides them | Unspecified protocols are not automatically valid | Usually start with relay-chat |

The most important rules are:

~~~text
Model vendor
    ≠ Request protocol

Model appears in the catalog
    ≠ The model can be called

Standard curl succeeds
    ≠ Kilo is fully configured
~~~

You only need to configure providers for the protocols you plan to use. If you only use Claude, you can configure only relay-anthropic; if you only use OpenAI Chat, you can configure only relay-chat. You do not need to configure all three providers from the start.

---

## 0. Complete Operation Roadmap

For first-time configuration, follow these steps in order:

~~~text
1. Install or verify Kilo Code
2. Prepare Base URL, API Key, and Terminal
3. Initialize or verify Kilo global configuration
4. Securely save the API Key
5. Query your model directory
6. Select a model and a target protocol
7. Use the corresponding protocol's curl to get final text
8. Write the verified model into Kilo
9. Check configuration and model list
10. Send a real message with kilo run
11. Add a second protocol or more models when needed
~~~

After completing Step 10, you have basic text conversation capability. See Section 12 for the scope of tool calls, images, files, structured output, streaming, and other advanced capabilities.

---

## 1. Prepare Information

Prepare three items before starting.

### 1.1 Base URL

This guide uses:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1>
~~~

This address already includes /v1. Do not write it as:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/v1>
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/chat/completions>
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/responses>
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/messages>
~~~

Kilo's AI SDK runtime automatically appends the specific endpoint based on the provider.

### 1.2 API Key

Create or copy an API Key from the AI Gateway backend and confirm:

- The API Key has not expired;
- The API Key has model call permissions;
- The Base URL and API Key belong to the same environment and tenant;
- No extra spaces or line breaks were included when copying;
- Account balance, quota, and concurrency limits meet the call requirements.

Never share your real API Key in chats, tickets, screenshots, Git repositories, or public web pages.

### 1.3 Model ID

The model ID is the routing key for the AI Gateway and must be copied in full from your model directory, for example:

~~~text
vendor/model-name
~~~

Version numbers, dots, hyphens, slashes, and vendor prefixes may all be part of the ID. Do not handwrite a model ID based on display names from a webpage, and do not change the case yourself.

This guide uses the following placeholder:

~~~text
YOUR_MODEL_ID
~~~

Before running a command or saving a configuration, you must replace it with the actual model ID. Angle brackets or uppercase placeholders cannot be entered as-is.

### 1.4 Terminal

All commands in this guide are run in macOS Terminal.

To open it: press Command + Space, type Terminal, and press Enter.

You may see a prompt like:

~~~text
user@Mac ~ %
~~~

Do not copy the prompt itself; only copy the commands from the code blocks in this guide.

---

## 2. Install or Verify Kilo Code

### 2.1 Check Basic Tools

Run:

~~~bash
command -v curl
command -v jq
node --version
npm --version
~~~

Under normal conditions, each command returns a file path or version number.

If jq is missing and Homebrew is already installed:

~~~bash
brew install jq
jq --version
~~~

If Node.js or npm is missing, first install the current LTS version from the official Node.js channel, then reopen Terminal.

### 2.2 Check Kilo CLI

Run:

~~~bash
command -v kilo
kilo --version
type -a kilo
~~~

`command -v` should return the Kilo path, and `kilo --version` should return a version number.

If `type -a kilo` shows multiple paths, confirm that Terminal, VS Code, and scripts all use the same version when troubleshooting later.

### 2.3 If Not Installed

Run:

~~~bash
npm install -g @kilocode/cli
kilo --version
~~~

If installation succeeds but `kilo: command not found` still appears, check:

~~~bash
npm prefix -g
echo "$PATH"
~~~

Add the bin directory corresponding to `npm prefix -g` to PATH, then reopen Terminal.

### 2.4 Install Kilo Code for VS Code (Optional)

If using VS Code:

1. Open VS Code;
2. Open Extensions;
3. Search for Kilo Code;
4. Install the recommended version per the official Kilo installation page;
5. Reload VS Code after installation.

This guide prioritizes using the CLI for connectivity verification because Terminal displays configuration checks and error messages in full. After CLI succeeds, use the VS Code interface per Section 9.5.

### 2.5 Confirm Current CLI Capabilities

Run:

~~~bash
kilo --help
kilo config --help
kilo models --help
kilo run --help
kilo debug paths
~~~

This guide uses the following commands:

~~~text
kilo config check       Check configuration
kilo models             View models
kilo run                Send a message
kilo debug paths        View configuration directory
~~~

---

## 3. Initialize Kilo Configuration

Kilo's custom provider configuration is saved in the user-level global configuration. The global configuration can safely resolve `{file:...}` key references; project-level configurations are not suitable for storing credentials.

### 3.1 View Configuration Directory

Run:

~~~bash
kilo debug paths
~~~

The default configuration directory on macOS is typically:

~~~text
~/.config/kilo
~~~

Kilo defaults to one of the following files:

~~~text
~/.config/kilo/kilo.json
~/.config/kilo/kilo.jsonc
~~~

Check the current file and record the configuration path to use in the current Terminal:

~~~bash
mkdir -p "$HOME/.config/kilo"

if [ -f "$HOME/.config/kilo/kilo.json" ] \
  && [ -f "$HOME/.config/kilo/kilo.jsonc" ]; then
  echo 'Both kilo.json and kilo.jsonc found. Confirm which one Kilo actually uses before continuing configuration.'
  unset KILO_CONFIG_FILE
elif [ -f "$HOME/.config/kilo/kilo.jsonc" ]; then
  export KILO_CONFIG_FILE="$HOME/.config/kilo/kilo.jsonc"
else
  export KILO_CONFIG_FILE="$HOME/.config/kilo/kilo.json"
fi

if [ -n "${KILO_CONFIG_FILE:-}" ]; then
  echo "Configuration file for this session: $KILO_CONFIG_FILE"
fi
~~~

If neither file exists, the command sets `KILO_CONFIG_FILE` to `~/.config/kilo/kilo.json`. If you are already using `kilo.jsonc`, subsequent commands will continue operating on the original file. Complete this guide's steps in the same Terminal window; reopening Terminal requires re-running this section to restore the variable.

When both `kilo.json` and `kilo.jsonc` exist, this guide stops selecting a file to avoid editing and validating different configurations. Back up both files first, then use `kilo debug config` to confirm the effective settings and merge them into one file. If unsure, contact your administrator rather than deleting either file directly.

### 3.2 Existing Configuration

If you have already configured other providers, models, plugins, or permissions, back up the file selected above:

~~~bash
if [ -z "${KILO_CONFIG_FILE:-}" ]; then
  echo 'No configuration file selected. Please complete Section 3.1 first.'
elif [ -f "$KILO_CONFIG_FILE" ]; then
  cp "$KILO_CONFIG_FILE" \
    "$KILO_CONFIG_FILE.backup-$(date +%Y%m%d-%H%M%S)"
  echo "Backed up $KILO_CONFIG_FILE"
else
  echo 'No existing configuration file found. Will be created in the next step.'
fi
~~~

With an existing configuration, only add or update this guide's providers; do not overwrite the entire file or delete other team or project settings.

### 3.3 First-Time Configuration

If the configuration file does not yet exist, create an empty JSON configuration file:

~~~bash
mkdir -p "$HOME/.config/kilo"

if [ -z "${KILO_CONFIG_FILE:-}" ]; then
  echo 'No configuration file selected. Please complete Section 3.1 first.'
elif [ ! -e "$KILO_CONFIG_FILE" ]; then
  printf '%s\n' '{}' > "$KILO_CONFIG_FILE"
  chmod 600 "$KILO_CONFIG_FILE"
  echo "Created $KILO_CONFIG_FILE"
else
  echo "Configuration file already exists, will not overwrite: $KILO_CONFIG_FILE"
fi
~~~

Open the configuration file:

~~~bash
open -e "$KILO_CONFIG_FILE"
~~~

You can also use VS Code:

~~~bash
code "$KILO_CONFIG_FILE"
~~~

If the `code` command does not exist, use `open -e`.

---

## 4. Securely Enter Connection Information in the Current Terminal

### 4.1 Temporarily Load Base URL and API Key

Run in the same Terminal. If the file already exists, the command reads it directly; if it does not exist, the command securely prompts for the API Key in the current Terminal and creates the file:

~~~bash
export RELAY_BASE_URL='https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1'

if [ ! -s "$HOME/.config/kilo/singdata-api-key" ]; then
  mkdir -p "$HOME/.config/kilo"
  read -s "RELAY_API_KEY?Paste the AI Gateway API Key, then press Enter: "
  echo
  (umask 077; printf '%s' "$RELAY_API_KEY" > "$HOME/.config/kilo/singdata-api-key")
  unset RELAY_API_KEY
  chmod 600 "$HOME/.config/kilo/singdata-api-key"
fi

export CLICKZETTA_API_KEY="$(< "$HOME/.config/kilo/singdata-api-key")"
~~~

Check that the variable exists without printing the token value:

~~~bash
if [ -n "$CLICKZETTA_API_KEY" ]; then
  echo 'API Key loaded into the current Terminal'
else
  echo 'API Key not loaded. Please re-run Section 4.2'
fi
~~~

After closing Terminal, exported variables disappear; the key file does not. Continue using the current window until completing Section 7.

### 4.2 Manually Recreate the Key File

If you need to replace or recreate the API Key, run:

~~~bash
mkdir -p "$HOME/.config/kilo"
read -s "RELAY_API_KEY?Paste the AI Gateway API Key, then press Enter: "
echo
(umask 077; printf '%s' "$RELAY_API_KEY" > "$HOME/.config/kilo/singdata-api-key")
unset RELAY_API_KEY
chmod 600 "$HOME/.config/kilo/singdata-api-key"
~~~

It is normal for no characters to appear on screen when pasting the API Key.

Confirm the file exists and permissions are correct without displaying the file contents:

~~~bash
test -s "$HOME/.config/kilo/singdata-api-key" \
  && echo 'API Key file created' \
  || echo 'API Key file is empty or does not exist'

ls -l "$HOME/.config/kilo/singdata-api-key"
~~~

Permissions should allow only the current user to read and write, typically shown as:

~~~text
-rw-------
~~~

### 4.3 Key Reference in Kilo Configuration

Kilo's global configuration reads the key file using the following reference:

~~~text
{file:~/.config/kilo/singdata-api-key}
~~~

Do not replace the real API Key into the JSON. `{file:...}` should only be placed in Kilo's trusted global configuration; do not put it in project configurations committed to Git.

---

## 5. Check Network and Query the Model Catalog

### 5.1 Check OpenAI-Style Connection First

Run:

~~~bash
curl -sS -o /tmp/kilo-gateway-models-openai.json \
  --max-time 30 \
  -w 'HTTP %{http_code}\n' \
  "$RELAY_BASE_URL/models" \
  -H "Authorization: Bearer $CLICKZETTA_API_KEY" \
  -H 'Content-Type: application/json'
~~~

Return value meanings:

| Return | Meaning | Next step |
|---|---|---|
| HTTP 200 | Network and Bearer authentication are working | View model catalog |
| HTTP 401 | API Key is missing, incorrect, or expired | Re-enter the API Key |
| HTTP 403 | API Key is rejected or current permissions are insufficient | Check account, tenant, and permissions |
| HTTP 404 | Base URL or /v1 path is incorrect | Check the address, avoid duplicating /v1 |
| HTTP 429 | Quota, concurrency, or rate limiting | Wait and retry, or check quota |
| HTTP 5xx | AI Gateway or upstream is temporarily unavailable | Retry later and save the sanitized error |
| No HTTP status, DNS, or connection timeout | Request did not reach the AI Gateway | Check network, proxy, firewall, or VPN |

If you have already received HTTP 200, 401, 403, 404, 429, or 5xx, the domain is generally reachable and you should not immediately assume "VPN is required." Only when DNS resolution fails, connection times out, or a network policy blocks traffic should you check proxy or VPN settings.

### 5.2 View the OpenAI Model List

After HTTP 200, run:

~~~bash
jq -r '
  if (.data | type) == "array" then
    .data[].id
  else
    .error.message // .message // "Could not read model catalog"
  end
' /tmp/kilo-gateway-models-openai.json
~~~

This list is used to select candidate models for OpenAI Chat or OpenAI Responses. The list only means the current API Key can see these models; you still need to test each specific endpoint separately.

### 5.3 View the Anthropic Model List

Only run this if you plan to use Anthropic Messages or Claude:

~~~bash
curl -sS -o /tmp/kilo-gateway-models-anthropic.json \
  --max-time 30 \
  -w 'HTTP %{http_code}\n' \
  "$RELAY_BASE_URL/models" \
  -H "x-api-key: $CLICKZETTA_API_KEY" \
  -H 'anthropic-version: 2023-06-01' \
  -H 'Content-Type: application/json'

jq -r '
  if (.data | type) == "array" then
    .data[].id
  else
    .error.message // .message // "Could not read Anthropic model catalog"
  end
' /tmp/kilo-gateway-models-anthropic.json
~~~

If the OpenAI model list and the Anthropic model list differ, that is normal. With different request headers and protocol context, AI Gateway can return different model catalogs.

### 5.4 Model IDs Must Be Copied Exactly

Do not:

- Handwrite model IDs based on display names from the web;
- Remove vendor prefixes from model IDs;
- Change dots to hyphens;
- Assume other versions work just because one version of the same series does;
- Treat the `/` in a model ID as a character to be removed.

If the target model is not in your catalog, confirm API Key permissions first; do not force configuration.

---

## 6. Verify the Target Model with the Corresponding Protocol

Only test the protocols you plan to use. Each test must satisfy both conditions simultaneously: HTTP 200, and final text in the response.

### 6.1 OpenAI Chat Completions

Copy a complete model ID from the results in Section 5.2:

~~~bash
read "CHAT_MODEL_ID?Paste the complete model ID you plan to use with the Chat protocol: "
~~~

Run:

~~~bash
curl -sS -o /tmp/kilo-test-chat.json \
  --max-time 60 \
  -w 'HTTP %{http_code}\n' \
  "$RELAY_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $CLICKZETTA_API_KEY" \
  -H 'Content-Type: application/json' \
  -d "$(jq -cn \
    --arg model "$CHAT_MODEL_ID" \
    '{
      model: $model,
      max_tokens: 512,
      messages: [{role: "user", content: "Reply only: Chat connection successful"}],
      stream: false
    }')"

jq -r '
  .choices[0].message.content
  // .error.message
  // .message
  // "HTTP returned but no final text found"
' /tmp/kilo-test-chat.json
~~~

On success you should see:

~~~text
HTTP 200
Chat connection successful
~~~

If successful, you can use the relay-chat configuration in Section 7.2.

### 6.2 OpenAI Responses

Copy a complete model ID from the results in Section 5.2:

~~~bash
read "RESPONSES_MODEL_ID?Paste the complete model ID you plan to use with the Responses protocol: "
~~~

Run:

~~~bash
curl -sS -o /tmp/kilo-test-responses.json \
  --max-time 60 \
  -w 'HTTP %{http_code}\n' \
  "$RELAY_BASE_URL/responses" \
  -H "Authorization: Bearer $CLICKZETTA_API_KEY" \
  -H 'Content-Type: application/json' \
  -d "$(jq -cn \
    --arg model "$RESPONSES_MODEL_ID" \
    '{
      model: $model,
      input: "Reply only: Responses connection successful",
      max_output_tokens: 512,
      stream: false
    }')"

jq -r '
  ([.output[]?.content[]? | select(.type == "output_text" or .type == "text") | .text] | join("\n")) as $text
  | if ($text | length) > 0 then
      $text
    else
      .output_text // .error.message // .message // "HTTP returned but no final text found"
    end
' /tmp/kilo-test-responses.json
~~~

On success you should see:

~~~text
HTTP 200
Responses connection successful
~~~

A successful curl only means the gateway's non-streaming Responses request works. Continue to the Kilo live message test in Section 9; only use the relay-responses configuration in Section 7.3 when `kilo run` can also return final text normally. If Kilo reports `text part SSE-Keep-Alive not found`, see the compatibility note at the beginning of this section and switch to a protocol that has passed Kilo live testing.

### 6.3 Anthropic Messages

Copy a complete model ID from the results in Section 5.3:

~~~bash
read "ANTHROPIC_MODEL_ID?Paste the complete model ID you plan to use with the Anthropic protocol: "
~~~

Run:

~~~bash
curl -sS -o /tmp/kilo-test-anthropic.json \
  --max-time 60 \
  -w 'HTTP %{http_code}\n' \
  "$RELAY_BASE_URL/messages" \
  -H "x-api-key: $CLICKZETTA_API_KEY" \
  -H 'anthropic-version: 2023-06-01' \
  -H 'Content-Type: application/json' \
  -d "$(jq -cn \
    --arg model "$ANTHROPIC_MODEL_ID" \
    '{
      model: $model,
      max_tokens: 1024,
      messages: [{role: "user", content: "Reply only: Anthropic connection successful"}],
      stream: false
    }')"

jq -r '
  ([.content[]? | select(.type == "text") | .text] | join("\n")) as $text
  | if ($text | length) > 0 then
      $text
    else
      .error.message // .message // "HTTP returned but no final text found"
    end
' /tmp/kilo-test-anthropic.json
~~~

On success you should see:

~~~text
HTTP 200
Anthropic connection successful
~~~

If successful, you can use the relay-anthropic configuration in Section 7.4.

### 6.4 HTTP 200 but No Final Text

Some reasoning models may generate thinking or reasoning content first. When the output budget is too small, a request may return HTTP 200 but contain no final text.

You can increase the following fields in the corresponding request:

~~~text
max_tokens: 512
max_output_tokens: 512
~~~

Raise them to 1024 or 4096 and test again. The final value cannot exceed the real limits of the model and the AI Gateway.

If there is still no final text after raising the budget, examine the full JSON and confirm whether the response structure matches the current protocol.

---

## 7. Write Verified Models into Kilo

This section provides three independent options. Choose the one that matches the standard curl and the Kilo protocol you plan to use for the initial configuration; do not copy all three options at once. Responses must also meet the additional compatibility requirements of Section 6.2.

> Before writing, assess your situation: if the configuration file currently only contains `{}`, you can replace `{}` with the complete JSON of your chosen option. If the configuration file already contains providers, plugins, permissions, or other settings, do not copy the entire code block to overwrite the original file — only merge the new provider entry into the existing top-level `provider` object. If you are unfamiliar with JSON merging, keep your backup and ask an administrator for help.

### 7.1 Back Up Configuration First

If you have not yet backed up, run:

~~~bash
if [ -z "${KILO_CONFIG_FILE:-}" ]; then
  echo 'No configuration file selected. Please complete Section 3.1 first.'
elif [ -f "$KILO_CONFIG_FILE" ]; then
  cp "$KILO_CONFIG_FILE" \
    "$KILO_CONFIG_FILE.backup-$(date +%Y%m%d-%H%M%S)"
  echo 'Kilo configuration backup created'
else
  echo 'Configuration file does not exist. Please complete Section 3.3 first.'
fi
~~~

### 7.2 Option A: Configure OpenAI Chat

Use this option only if Section 6.1 succeeded.

If the configuration file currently only contains `{}`, you can use the following complete configuration. If other configurations already exist, only merge the `relay-chat` entry into the existing top-level `provider` object; do not overwrite the entire file:

~~~json
{
  "$schema": "https://app.kilo.ai/config.json",
  "model": "relay-chat/YOUR_MODEL_ID",
  "provider": {
    "relay-chat": {
      "name": "AI Gateway - OpenAI Chat",
      "npm": "@ai-sdk/openai-compatible",
      "options": {
        "apiKey": "{file:~/.config/kilo/singdata-api-key}",
        "baseURL": "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1"
      },
      "models": {
        "YOUR_MODEL_ID": {
          "name": "AI Gateway Model"
        }
      }
    }
  }
}
~~~

Replace both instances of YOUR_MODEL_ID with the complete model ID that passed testing in Section 6.1.

### 7.3 Option B: Configure OpenAI Responses

This provider can be temporarily written in for Kilo validation only after the curl in Section 6.2 succeeds; it can be kept and used officially only after the Kilo live message test in Section 9.2 also succeeds.

Since `kilo run` requires a provider configuration to exist first, the correct order for this option is: write the configuration, run the Section 8 checks, then immediately run the Section 9.2 test. If a `SSE-Keep-Alive` error occurs, restore the backup or stop using this provider; do not set it as the default model.

~~~json
{
  "$schema": "https://app.kilo.ai/config.json",
  "model": "relay-responses/YOUR_MODEL_ID",
  "provider": {
    "relay-responses": {
      "name": "AI Gateway - OpenAI Responses",
      "npm": "@ai-sdk/openai",
      "options": {
        "apiKey": "{file:~/.config/kilo/singdata-api-key}",
        "baseURL": "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1"
      },
      "models": {
        "YOUR_MODEL_ID": {
          "name": "AI Gateway Model"
        }
      }
    }
  }
}
~~~

Replace both instances of YOUR_MODEL_ID with the complete model ID that passed testing in Section 6.2.

### 7.4 Option C: Configure Anthropic Messages

Use this option only if Section 6.3 succeeded.

~~~json
{
  "$schema": "https://app.kilo.ai/config.json",
  "model": "relay-anthropic/YOUR_MODEL_ID",
  "provider": {
    "relay-anthropic": {
      "name": "AI Gateway - Anthropic Messages",
      "npm": "@ai-sdk/anthropic",
      "options": {
        "apiKey": "{file:~/.config/kilo/singdata-api-key}",
        "baseURL": "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1"
      },
      "models": {
        "YOUR_MODEL_ID": {
          "name": "AI Gateway Model"
        }
      }
    }
  }
}
~~~

Replace both instances of YOUR_MODEL_ID with the complete model ID that passed testing in Section 6.3.

Claude should preferably use this provider. Writing a Claude model ID into relay-chat does not automatically switch to Anthropic Messages.

### 7.5 Configuring Multiple Protocols Simultaneously

If multiple protocols have each passed both standard curl and Kilo live message testing, you can merge multiple providers into the same top-level provider object. Each provider must remain independent:

~~~text
relay-chat       → @ai-sdk/openai-compatible → /chat/completions
relay-responses  → @ai-sdk/openai             → /responses
relay-anthropic  → @ai-sdk/anthropic          → /messages
~~~

When there is an existing configuration, follow these rules:

1. Keep existing $schema, other providers, plugins, themes, and project settings;
2. Add new providers inside the top-level provider object;
3. Each provider must be an object, not a single string;
4. Do not merge models from three protocols into the same provider;
5. The top-level model must reference a provider_id/model_id that actually exists;
6. After saving, run the JSON and Kilo configuration checks in Section 8.

Incorrect format (shown only to identify errors, do not use):

~~~json
{
  "provider": {
    "relay-anthropic": "@ai-sdk/anthropic"
  }
}
~~~

This causes a configuration validation error similar to `expected object, received string`.

### 7.6 Expected Result

After writing the configuration, do not stop at confirming the file saved successfully. You must continue with the configuration and model list checks in Section 8 and the live message test in Section 9.

This guide does not write `tool_call`, `reasoning`, `attachment`, `modalities`, or fixed token limits for all models universally. These fields require explicit documentation from the corresponding model or AI Gateway; arbitrarily copying uniform values may cause truncation, parameter errors, or incorrect feature display.

---

## 8. Check Kilo Configuration and Model List

### 8.1 Check JSON and Configuration Warnings

Run:

~~~bash
if [[ "$KILO_CONFIG_FILE" == *.json ]]; then
  jq empty "$KILO_CONFIG_FILE"
else
  echo 'Currently using JSONC, skipping jq; Kilo will check the configuration.'
fi

kilo config check
~~~

Under normal conditions, `kilo config check` should return:

~~~text
No config warnings.
~~~

If jq reports a syntax error, check commas, quotes, braces, and provider nesting. JSONC may contain comments and cannot be checked directly with jq, so `kilo config check` takes precedence. If warnings or errors appear, do not proceed to run models.

### 8.2 View the Newly Configured Provider

Based on your actual configuration, run only the corresponding command or commands:

~~~bash
kilo models relay-chat
kilo models relay-responses
kilo models relay-anthropic
~~~

You should see a structure similar to:

~~~text
relay-chat/<model ID copied from catalog>
relay-responses/<model ID copied from catalog>
relay-anthropic/<model ID copied from catalog>
~~~

The text in angle brackets is descriptive only; do not enter it literally. `kilo models` showing the model only means the local provider and model catalog have been loaded; it does not guarantee that the remote call will succeed.

### 8.3 View Effective Configuration (Optional)

To confirm which configuration file Kilo is ultimately reading, run:

~~~bash
kilo debug config
~~~

The output may contain resolved API Key values or other sensitive fields. View only on your local machine; remove or redact API Keys, Authorization headers, tokens, organization IDs, and account information before sharing.

---

## 9. Send Your First Message with Kilo

### 9.1 Test the Default Model

If the top-level `model` in the configuration file is already set to the complete model reference that passed testing, run:

~~~bash
kilo run 'Reply only: Kilo connection successful'
~~~

Expected final text:

~~~text
Kilo connection successful
~~~

The success criterion is the command ultimately returning model text — not just seeing the configuration check pass or the model appear in the list.

### 9.2 Test a Specific Model

To bypass the default model, use the complete Kilo model reference:

~~~bash
kilo run \
  --model 'relay-chat/YOUR_MODEL_ID' \
  'Reply only: Specific model connection successful'
~~~

If the configured protocol is Responses or Anthropic, change `--model` to:

~~~text
relay-responses/<model ID>
relay-anthropic/<model ID>
~~~

If the model ID contains `/`, a complete reference containing multiple `/` characters is normal. Do not omit the provider ID and write only the model ID.

### 9.3 Troubleshoot Completion Reason with JSON Events

If output is incomplete or retrying for a long time, you can view the raw events:

~~~bash
kilo run \
  --model 'PROVIDER_ID/YOUR_MODEL_ID' \
  --format json \
  'Reply only: OK'
~~~

Replace PROVIDER_ID with relay-chat, relay-responses, or relay-anthropic, and replace the model placeholder with the real model ID.

On success, the output should contain the final text and a normal end event. If only thinking/reasoning content appears, return to Section 6.4 to check the output budget.

### 9.4 Use the Interactive Interface

Navigate to the project directory you want to work with:

~~~bash
cd /path/to/your/project
kilo
~~~

In the Kilo TUI, use `/models` to select the complete model reference you have configured. When making file modifications or running commands for the first time, read the permission prompts and only approve operations you understand.

### 9.5 Use Kilo Code for VS Code

If you have already completed verification in the CLI, configure it in VS Code:

1. Open the Kilo Code panel;
2. Click Settings;
3. Go to Providers;
4. Scroll to the bottom of the provider list;
5. Click Custom provider.

Field correspondence:

| Interface field | OpenAI Chat | OpenAI Responses | Anthropic Messages |
|---|---|---|---|
| Provider ID | relay-chat | relay-responses | relay-anthropic |
| Provider API | OpenAI Compatible | OpenAI Responses | Anthropic Messages |
| Base URL | Example Base URL, up to /v1 only | Same | Same |
| API key | Current API Key | Current API Key | Current API Key |
| Model ID | Original ID that succeeded in both Chat curl and Kilo | Original ID that succeeded in both Responses curl and Kilo | Original ID that succeeded in both Messages curl and Kilo |

After filling in the fields, click Submit, then select the model in the model selector. If the interface cannot automatically fetch models, manually copy the model ID per Section 5 and confirm that the Provider API matches the protocol used in the standard curl.

VS Code extension menu names and field positions may change with version updates. The CLI's `kilo config check` and `kilo run` are the final authority. If interface names differ from this guide, fill in the fields by matching the semantics of Provider API, Base URL, API Key, and Model ID. The current Responses compatibility limitation also applies to VS Code and does not disappear when switching to the graphical interface.

---

## 10. Add a Second Protocol or More Models

### 10.1 Add a Second Protocol

For example, if relay-chat is already configured and you now want to use Claude:

1. Run Section 5.3 to query the Anthropic catalog;
2. Run Section 6.3 to test the target model;
3. Run Section 7.4 to add relay-anthropic;
4. Run Section 8 to check configuration and model list;
5. Send a test message using `--model relay-anthropic/<model ID>`.

Adding a second provider does not require reinstalling Kilo or removing the first provider.

### 10.2 Add a Model to an Existing Provider

First test the new model with the corresponding protocol from Section 6. After success, add a new entry to the `models` object of the target provider:

~~~json
{
  "models": {
    "vendor/existing-model": {
      "name": "Existing Model"
    },
    "vendor/new-model": {
      "name": "New Model"
    }
  }
}
~~~

After adding, run:

~~~bash
if [[ "$KILO_CONFIG_FILE" == *.json ]]; then
  jq empty "$KILO_CONFIG_FILE"
fi
kilo config check
kilo models PROVIDER_ID
kilo run --model 'PROVIDER_ID/vendor/new-model' 'Reply only: New model connection successful'
~~~

Replace PROVIDER_ID and the model ID with actual values.

To make the new model the default, change the top-level `model` in the configuration file to the new complete model reference. You can also use `--model` only in commands without changing the default.

### 10.3 Adding the Same Model to Multiple Protocols

If the same model has passed both Chat and Anthropic Messages testing, you can add it once to each provider:

~~~text
relay-chat/<same model ID>
relay-anthropic/<same model ID>
~~~

These are two different Kilo model references. They use different request formats, and errors, response fields, and tool call behavior may also differ.

---

## 11. Request Protocol and Configuration Boundaries

### 11.1 The Three Protocols Cannot Be Mixed

| Item | OpenAI Chat Completions | OpenAI Responses | Anthropic Messages |
|---|---|---|---|
| Request path | /chat/completions | /responses | /messages |
| Auth header | Authorization: Bearer | Authorization: Bearer | x-api-key + anthropic-version |
| Main input field | messages | input | messages; system prompt typically uses top-level system |
| Output limit field | max_tokens | max_output_tokens | max_tokens |
| Final text location | choices[].message.content | output[].content[].text or output_text | content[] entries where type=text |
| Kilo runtime | @ai-sdk/openai-compatible | @ai-sdk/openai | @ai-sdk/anthropic |

Modifying only the URL or model name cannot convert one protocol to another. The endpoint, auth header, request body, streaming events, and tool call structure must all match together.

### 11.2 Model ID Prefix Does Not Switch Protocol

Suppose a model ID starts with `anthropic/`:

~~~text
relay-chat/anthropic/<model name>
~~~

This still uses OpenAI Chat, because the local provider is relay-chat.

Only:

~~~text
relay-anthropic/anthropic/<model name>
~~~

uses Anthropic Messages as configured in this guide.

Similarly, `openai/`, `deepseek/`, `qwen/`, or other prefixes are just parts of the AI Gateway model ID.

### 11.3 Kilo Does Not Automatically Fall Back to Another Protocol

A single Kilo call uses only the provider specified in the complete model reference. A Chat failure does not automatically switch to Responses, and a Responses failure does not automatically switch to Anthropic.

When a fallback protocol is needed, you must create providers separately, test them separately, and explicitly switch provider IDs and model IDs when using them.

### 11.4 The Same Model May Support Multiple Protocols

If the same model has passed both Chat and Anthropic Messages testing, you can add it to both providers. This does not mean the two references are completely equivalent; they may have different parameters, response events, tool calls, and billing behavior.

### 11.5 What Catalog, curl, and Kilo Each Tell You

| Result you see | What it confirms | Next step |
|---|---|---|
| Model appears in /models | The current API Key can see the model ID in this protocol view | Test the target protocol |
| Same-protocol curl returns HTTP 200 and final text | AI Gateway's routing for this model can complete a basic text request | Configure the corresponding provider, then run the Kilo message test |
| kilo models shows the model | The local provider and model catalog have been written | Send a Kilo message |
| kilo run returns final text and ends normally | Kilo, provider, model, and basic text pipeline are connected | Start using basic text, or continue testing Agent capabilities |
| Kilo completes a read-only tool test in a temp directory | The current model and protocol can complete at least this read-only tool call | Test file modification, command execution, and other capabilities as needed |

### 11.6 Do Not Guess Context Window and Output Limits

Kilo custom models can configure `limit.context`, `limit.output`, `tool_call`, `reasoning`, `attachment`, and `modalities`, but these are not universal fixed values for all models.

The minimal provider configuration in this guide only writes the model name. Other fields should only be added after the AI Gateway or model documentation explicitly provides values and those values have been validated in practice.

---

## 12. What Capabilities Are Available After Configuration

Completing Section 9 only means the basic text pipeline has succeeded: you can send text to Kilo and receive the model's final text reply. It does not automatically prove that Kilo's Agent tools, file modification, or command execution capabilities are available.

Whether the following capabilities are available also depends on the combined implementation of the model, request protocol, AI Gateway, and Kilo provider:

- Streaming output and mid-stream cancellation;
- Tool calls and multi-turn tool result returns;
- File editing, command execution, and other agent tools;
- JSON Schema or structured output;
- Image, PDF, audio, and other multimodal inputs;
- Prompt Cache or other caching capabilities;
- Extended Thinking, reasoning effort level, or other reasoning parameters;
- Extra-long context and automatic compaction;
- Concurrency, rate limiting, timeouts, and retries;
- Automatic failover and fallback models.

If you only need basic text conversation, you can start using it after Section 9 succeeds. If you need the above capabilities, run dedicated tests for the model and protocol you plan to use.

Do not declare a capability in your Kilo configuration simply because the model supports it via the native vendor API. Protocol conversion may change fields, events, or limits.

### 12.1 Optional: Run a Read-Only Agent Smoke Test

If you plan to have Kilo read project files, you can first verify read-only tool capabilities in a temporary directory. Replace `PROVIDER_ID/YOUR_MODEL_ID` with the complete model reference that passed Section 9:

~~~bash
KILO_SMOKE_DIR="$(mktemp -d)"
printf '%s\n' 'KILO_AGENT_SMOKE_20260819' \
  > "$KILO_SMOKE_DIR/kilo-agent-smoke.txt"

kilo run \
  --dir "$KILO_SMOKE_DIR" \
  --model 'PROVIDER_ID/YOUR_MODEL_ID' \
  --format json \
  'Read kilo-agent-smoke.txt and reply with its complete contents. Do not modify any files.'
~~~

On success, the final text should contain:

~~~text
KILO_AGENT_SMOKE_20260819
~~~

Also check the JSON events for the presence of a file-reading tool call. If the model did not call a tool but instead guessed or directly restated the prompt, this result cannot be considered a successful verification of tool capability.

After testing, delete the test file created by this guide first, then delete the now-empty temporary directory:

~~~bash
if [ -f "$KILO_SMOKE_DIR/kilo-agent-smoke.txt" ]; then
  rm -- "$KILO_SMOKE_DIR/kilo-agent-smoke.txt"
  rmdir -- "$KILO_SMOKE_DIR"
  unset KILO_SMOKE_DIR
else
  echo 'Test file created by this guide not found; deletion skipped.'
fi
~~~

This guide does not use `--auto` automatically and does not allow testing to modify real projects. File writing, code modification, and command execution must each be verified in a separate test project, with the user reading and approving permission prompts.

### 12.2 How to State Capability Conclusions

When determining whether a capability is available, use conclusions that match the actual tests performed:

| Test completed | What it confirms | Cannot promise based on this |
|---|---|---|
| curl basic text succeeded | The gateway endpoint and model route can complete this basic text request | Kilo is ready to use |
| `kilo run` basic text succeeded | Kilo basic text pipeline is available | File editing, command execution, tools, and multimodal are all available |
| Read-only Agent smoke test succeeded | This combination of model, protocol, and Kilo can complete a read-only file tool call | All tools, all models, and all projects work |
| A specific capability test succeeded | The model and protocol support that capability under these test conditions | Other models from the same vendor automatically support the same capability |

---

## 13. Troubleshooting

### 13.1 No Characters Appear When Pasting API Key

Normal. `read -s` hides input. Paste and press Enter.

### 13.2 kilo: command not found

The cause is usually that Kilo is not installed, or the npm global bin is not in PATH.

Run:

~~~bash
npm install -g @kilocode/cli
npm prefix -g
echo "$PATH"
kilo --version
~~~

### 13.3 expected object, received string

This usually means a provider was written as a string. For example:

~~~json
{
  "provider": {
    "relay-anthropic": "@ai-sdk/anthropic"
  }
}
~~~

A provider must be an object and must include at least the correct `npm`, `options`, and `models`. Restore the backup and re-merge using the complete object structure from Section 7.

### 13.4 Model Not in kilo models

Check in order:

1. The file being edited is the global configuration file that Kilo actually uses;
2. The provider ID matches `kilo models PROVIDER_ID`;
3. The model ID is inside the target provider's `models` object;
4. The top-level `model` or `--model` in the command uses the complete reference;
5. Both `jq empty` and `kilo config check` pass;
6. There is no conflicting pair of kilo.json and kilo.jsonc.

### 13.5 HTTP 401 or 403

Common causes:

- API Key is incorrect, expired, or lacks permissions;
- OpenAI request incorrectly uses x-api-key;
- Anthropic request is missing x-api-key or anthropic-version;
- Base URL and API Key do not belong to the same environment;
- VS Code interface has no API Key filled in, while CLI uses a local file.

Return to Section 5 to recheck auth headers and catalog requests.

### 13.6 No upstream candidates

This means there is no available upstream for the current "model ID + protocol + API Key/tenant" combination. Common causes:

- Model ID is incorrect;
- Provider is using the wrong protocol;
- API Key lacks permissions for the corresponding model;
- AI Gateway has no model route configured for this protocol;
- Upstream is temporarily offline.

Resolution order: re-query the corresponding catalog, copy the model ID exactly, then test with the same-protocol curl from Section 6. Do not attribute this to a Kilo installation problem first.

### 13.7 HTTP 404, 502, or 503

HTTP 404 usually means the Base URL, /v1, or specific endpoint is incorrect; HTTP 502/503 usually means the request reached AI Gateway but the upstream model call failed.

Save the following sanitized information:

- Time of occurrence and timezone;
- Complete model ID;
- Request protocol and path;
- HTTP status code;
- Error JSON with API Key removed.

Do not try to resolve upstream 5xx errors by renaming Kilo provider names.

### 13.8 HTTP 200 but No Final Text

Increase the output budget and check the correct text field for the current protocol:

~~~text
Chat       → choices[].message.content
Responses  → output[].content[].text or output_text
Anthropic  → content[] where type=text
~~~

If the JSON contains only thinking or reasoning content, the output budget may have been consumed by the reasoning process. Return to Section 6.4 and gradually increase the budget.

### 13.9 Claude Access Fails

First confirm the complete reference uses the Anthropic provider:

~~~text
relay-anthropic/complete model ID
~~~

The following format uses Chat Completions and will not automatically switch just because the model ID contains `anthropic`:

~~~text
relay-chat/anthropic/your-model-id
~~~

Continue checking:

1. Whether the Anthropic catalog shows the model;
2. Whether the /messages standard request succeeds;
3. Whether the Kilo runtime is @ai-sdk/anthropic;
4. Whether the Base URL ends at /v1 only;
5. Whether the model ID fully retains the vendor prefix.

### 13.10 OpenAI Model Access Fails

Do not treat Chat Completions and Responses as the same protocol:

- When /chat/completions succeeds, use relay-chat;
- After /responses succeeds, still run the `kilo run` test for relay-responses;
- When both endpoints and corresponding Kilo tests succeed, keep both providers separately;
- When only one protocol passes the Kilo live message test, use only the corresponding provider.

The current example gateway may have Responses streaming event compatibility issues with Kilo Code CLI 7.4.22. When a `SSE-Keep-Alive` error occurs, prefer the relay-chat that has already passed Kilo live testing; do not determine Kilo availability based solely on HTTP 200 from `/responses`.

### 13.11 DeepSeek or Qwen Succeeds on One Protocol but Fails on Another

This is a compatibility routing difference, not necessarily a model ID prefix error. Keep the provider for the successful protocol and delete or disable the configuration for the failed protocol.

Kilo does not automatically fall back among Chat, Responses, and Anthropic.

### 13.12 CLI Succeeds but VS Code Fails

Check in order:

- Whether Kilo Code in VS Code is the current recommended version;
- Whether VS Code loads the same user's global Kilo configuration;
- Whether the Base URL in the interface has duplicate endpoint appended;
- Whether Provider API matches the CLI provider;
- Whether VS Code needs to reload the window;
- The CLI uses a key file — check whether the API Key is missing from the interface;
- Whether the Kilo Code log in the VS Code Output panel has a clear error.

### 13.13 Responses Returns "text part SSE-Keep-Alive not found"

If the non-streaming curl request to `/responses` returns HTTP 200, but `kilo run` reports:

~~~text
text part SSE-Keep-Alive not found
~~~

This means the API Key, Base URL, and non-streaming Responses route are generally connected, but the streaming events returned by the gateway are incompatible with the current Kilo `@ai-sdk/openai` runtime. This error cannot be resolved by model catalog success, HTTP 200, or switching VPN.

Handle in this order:

1. Do not set relay-responses as the default model;
2. Switch to the relay-chat already verified in Section 9;
3. Keep the sanitized error text, Kilo version, time of occurrence, model ID, and protocol path;
4. After a gateway or Kilo upgrade, re-run Sections 6.2 and 9.2;
5. Only mark Responses as Kilo-ready after `kilo run` returns final text and ends normally.

### 13.14 kilo config check Fails

First run:

~~~bash
if [[ "$KILO_CONFIG_FILE" == *.json ]]; then
  jq empty "$KILO_CONFIG_FILE"
fi
kilo config check
~~~

Common causes:

- JSON is missing a comma, quote, or brace;
- Provider is written as a string;
- `models` is written outside the provider;
- npm runtime name is incorrect;
- `{file:...}` file does not exist or path is incorrect;
- Conflicting kilo.json and kilo.jsonc both exist.

### 13.15 Restore Configuration Backup

View backups:

~~~bash
find "$HOME/.config/kilo" -maxdepth 1 -type f \
  \( -name 'kilo.json.backup-*' -o -name 'kilo.jsonc.backup-*' \) -print \
  | sort -r \
  | sed -n '1,5p'
~~~

Copy the exact backup file path, then run:

~~~bash
read "KILO_BACKUP_FILE?Paste the full path of the backup file to restore: "

if [ -f "$KILO_BACKUP_FILE" ] \
  && [[ "$KILO_BACKUP_FILE" == "$HOME/.config/kilo/"*.backup-* ]]; then
  cp "$KILO_BACKUP_FILE" "$KILO_CONFIG_FILE"
  echo "Restored to $KILO_CONFIG_FILE"
else
  echo 'Backup file does not exist or path is unexpected; restoration skipped.'
fi
unset KILO_BACKUP_FILE

if [[ "$KILO_CONFIG_FILE" == *.json ]]; then
  jq empty "$KILO_CONFIG_FILE"
fi
kilo config check
~~~

The restore target always uses `$KILO_CONFIG_FILE` selected in Section 3.1. Only continue calling models after `kilo config check` passes.

---

## 14. API Key and Local Security

Kilo's global configuration file is typically one of:

~~~text
~/.config/kilo/kilo.json
~/.config/kilo/kilo.jsonc
~~~

The actual file to operate on is determined by `$KILO_CONFIG_FILE` selected in Section 3.1; do not maintain two files with different content simultaneously.

The provider configuration in this guide uses a file reference; the API Key is stored in:

~~~text
~/.config/kilo/singdata-api-key
~~~

Restrict permissions for the configuration file, key file, and historical backups simultaneously:

~~~bash
chmod 600 "$HOME/.config/kilo/singdata-api-key"
chmod 600 "$KILO_CONFIG_FILE" 2>/dev/null || true

find "$HOME/.config/kilo" -maxdepth 1 -type f \
  \( -name 'kilo.json.backup-*' -o -name 'kilo.jsonc.backup-*' \) \
  -exec chmod 600 {} \;
~~~

Do not:

- Upload kilo.json or the key file;
- Take screenshots of the full configuration;
- Run `echo "$CLICKZETTA_API_KEY"`;
- Paste full request headers into public tickets;
- Write the API Key into project repositories;
- Store real tokens in project-level configuration;
- Share a long-lived, high-privilege API Key with others.

After completing configuration, clear the temporary variables from the current Terminal:

~~~bash
unset CLICKZETTA_API_KEY
unset RELAY_BASE_URL
unset CHAT_MODEL_ID
unset RESPONSES_MODEL_ID
unset ANTHROPIC_MODEL_ID
unset KILO_CONFIG_FILE
~~~

If the API Key has already appeared in a public screenshot, chat, or command output, immediately revoke it and create a new one in the AI Gateway backend.

Kilo's tool capabilities can read files, modify code, and run commands. Before enabling automatic execution or relaxing permissions, confirm the project directory, sandbox, and permission settings. Do not equate model connection success with full local permission access.

---

## 15. Completion Checklist

Confirm each item after completing configuration:

~~~text
[ ] curl, jq, node, npm can execute
[ ] kilo --version returns a version
[ ] kilo debug paths can find the Kilo configuration directory
[ ] KILO_CONFIG_FILE points to the configuration file actually edited this session
[ ] No conflicting kilo.json and kilo.jsonc maintained simultaneously
[ ] Existing Kilo configuration has been backed up
[ ] Base URL is correct, /v1 is not duplicated
[ ] API Key is securely saved and not exposed
[ ] Model catalog for the target protocol has been queried
[ ] Model ID is copied exactly from your own catalog
[ ] Target protocol curl returns HTTP 200
[ ] curl response contains final text
[ ] Kilo provider npm runtime matches the curl protocol
[ ] Provider is an object, not a string
[ ] No YOUR_ or actual placeholders remain in the configuration file
[ ] When using JSON, jq empty check passes; when using JSONC, jq was skipped
[ ] kilo config check returns No config warnings
[ ] kilo models shows the complete provider/model reference
[ ] kilo run returns final text and ends normally
[ ] When a second protocol is needed, it has been tested and configured separately
[ ] Tool, reasoning, streaming, and multimodal capabilities are individually verified as needed
[ ] If limit.context or limit.output are configured manually, values come from real model specifications
[ ] Permissions for configuration file, key file, and backup files have been restricted
~~~

After `kilo run` returns final text and ends normally, you can confirm that the Kilo basic text pipeline for this model and protocol has been connected through AI Gateway. Only after the corresponding dedicated tests in Section 12 succeed can you further declare that read-only tools, file editing, command execution, streaming output, or multimodal capabilities are available.

If /models succeeds but curl fails, start troubleshooting from the protocol and upstream routing; if curl succeeds but Kilo fails, start from the provider runtime, complete model reference, configuration path, and version.

---

## 16. Related Resources

- [Kilo Code Custom Models](https://kilo.ai/docs/code-with-ai/agents/custom-models)
- [Kilo Code CLI](https://kilo.ai/docs/code-with-ai/platforms/cli)
- [Kilo Code CLI Command Reference](https://kilo.ai/docs/code-with-ai/platforms/cli-reference)
- [Kilo Code Installation](https://kilo.ai/docs/getting-started/installing)

Both Kilo and AI Gateway may be upgraded. When command parameters or interface fields differ, first run:

~~~bash
kilo --version
kilo config --help
kilo models --help
kilo run --help
~~~

Use the parameters shown by the currently installed version as the reference. The core flow — protocol selection, exact model ID copying, standard curl verification, and Kilo live message verification — remains unchanged.
