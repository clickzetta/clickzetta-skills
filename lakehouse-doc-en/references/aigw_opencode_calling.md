This guide is intended for users who are using Terminal for the first time, configuring OpenCode for the first time, or need to connect OpenCode to a third-party AI Gateway.

After completing this guide, you will be able to:

- Install and verify OpenCode;
- Securely enter the AI Gateway Base URL and API Key;
- Query the models available to your API Key;
- Determine whether a model should use OpenAI Chat, OpenAI Responses, or Anthropic Messages;
- Write successfully tested models into the correct OpenCode provider;
- Confirm that OpenCode is connected using a real message;
- Diagnose errors as network, authentication, model routing, request protocol, or OpenCode configuration issues.

This guide uses macOS Terminal as the example environment. The example AI Gateway Base URL is:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1>
~~~

If your AI Gateway differs, simply replace the Base URL, API Key, and model ID. The model names in this guide are for demonstration purposes only; the actual model availability depends on your API Key and the relay results. Do not share your real API Key in chats, tickets, screenshots, Git repositories, or public web pages.

The configuration examples in this guide are written for OpenCode `1.18.18`. The OpenCode configuration format changes between versions. If your version differs, run `opencode --version` first and do not mix configuration formats from different versions.

---

## Summary First: Model Vendor and Request Protocol Are Two Different Things

OpenCode does not automatically select a request protocol based on the model name. The actual request format is determined by the AI SDK runtime used by the provider.

This guide uses three easily recognizable provider names:

| OpenCode provider | AI SDK runtime | AI Gateway endpoint | When to use |
|---|---|---|---|
| `my-relay` | `@ai-sdk/openai-compatible` | `/chat/completions` | Model's OpenAI Chat request succeeds |
| `my-relay-responses` | `@ai-sdk/openai` | `/responses` | Model's OpenAI Responses request succeeds |
| `my-relay-anthropic` | `@ai-sdk/anthropic` | `/messages` | Model's Anthropic Messages request succeeds |

If you already have other provider names, you do not need to rename them to match this guide's examples. Keep your existing names and replace the provider IDs in the commands with your actual names. Provider names are local configuration names, not vendor names.

### Choosing the First Test Path by Model Vendor

The table below helps you choose a starting path. It does not mean all models from a given vendor expose the same protocols. Each specific model must be verified using your own `/models` and the corresponding curl results:

| Model vendor or series | OpenAI Chat | OpenAI Responses | Anthropic Messages | OpenCode configuration recommendation |
|---|---|---|---|---|
| Anthropic Claude | Usually not the first choice | Requires separate testing | Native integration path, test first | Use `my-relay-anthropic` |
| OpenAI GPT, Codex series | Common compatible path | OpenAI native path, requires separate testing | Usually not the first choice | Chat success: use `my-relay`; Responses success: use `my-relay-responses` |
| DeepSeek series | Available when provided by gateway | Test per model | Available when provided by gateway | Choose provider based on actual successful protocol |
| Qwen series | Available when provided by gateway | Test per model | Available when provided by gateway | Choose provider based on actual successful protocol |
| Other vendors or custom models | Cannot infer | Cannot infer | Cannot infer | Check the model directory first, then test by protocol |

The most important rules are:

~~~text
Model vendor ≠ Request protocol
Model appears in catalog ≠ Model is callable
Standard curl succeeds ≠ OpenCode is configured correctly
~~~

Only configure providers for protocols you intend to use. If you only use Claude, you only need to configure the Anthropic provider. If you only use OpenAI Chat, you only need to configure the OpenAI Compatible provider. Only configure the Responses provider if the `/responses` test succeeds and you actually need that endpoint.

---

## 0. Complete Operation Sequence

For first-time configuration, follow these steps in order:

~~~text
1. Install or verify OpenCode
2. Prepare Base URL and API Key
3. Query your model directory
4. Select a model and target protocol
5. Get the final text using the corresponding protocol's curl
6. Write the successful model into OpenCode
7. Validate configuration and view provider
8. Send the first message with OpenCode
9. Add other models or protocols as needed
~~~

A truly successful setup must satisfy all of the following at the same time:

1. The model appears in the model directory for the current protocol;
2. The standard curl returns HTTP 200;
3. The response contains actual model text;
4. OpenCode returns actual model text through the correct provider.

Seeing a model name alone does not confirm the model is usable. The model directory, protocol routing, and actual client calls must each be verified separately.

### 0.1 How to Read Model Information

Model information in this guide has three levels with different meanings:

| Information level | Description | Action to take |
|---|---|---|
| API Key live directory | Model IDs visible when querying `/models` with a certain authentication header using your current API Key | Treat as candidates first, then continue with request testing |
| Protocol call result | The actual HTTP result for a model under OpenAI Chat, OpenAI Responses, or Anthropic Messages | Only use under the corresponding protocol, and record success or failure reasons |
| OpenCode configuration result | The actual result of combining the OpenCode provider, AI SDK runtime, and client parameters | Call according to the provider format in this guide; advanced capabilities require separate confirmation |

Therefore, use the following priority order:

~~~text
Your API Key live directory
    ↓
Standard curl for the corresponding protocol
    ↓
Actual call via the corresponding OpenCode provider
    ↓
Only then can you determine whether the model is usable in your environment
~~~

"Usable" in this guide defaults to "a minimal text request returned final text." It does not automatically include tool calling, streaming, multimodal input, structured output, long context, or model-specific parameters.

Whether you can ultimately call a model depends on four conditions being met simultaneously:

~~~text
Whether the product has configured upstream routing for that model
    × Whether the API Key has permission for that model
    × Whether OpenCode uses the correct provider and protocol
    × Whether the features used in this request have been verified
    = Whether this call is truly usable
~~~

Therefore, "the relay can route a model" and "your API Key can currently call that model" are two different questions. The latter is also affected by tenant, subscription plan, permissions, and real-time upstream status.

### 0.2 Expected Results After Configuration

After completing this guide, you should be able to:

- See the providers and models available to your API Key in OpenCode;
- Use `my-relay` to call OpenAI Compatible Chat models;
- Use `my-relay-responses` to call a model when its `/responses` request succeeds;
- Use `my-relay-anthropic` to call Anthropic Messages models, including Claude;
- Choose the correct provider based on vendor and protocol rules, without placing Claude into an OpenAI provider;
- Confirm that a model actually returns final text using a minimal text request;
- Determine which layer (authentication, network, protocol, routing, or client parameter) an error belongs to.

After completing step 8, you have basic text conversation capability. See Section 11.6 and Section 12 for the scope of tool calling, images, files, structured output, and other advanced capabilities.

If you only completed the JSON editing without completing the curl and OpenCode actual calls, the configuration has not been verified.

---

## 1. Gather Required Information

Prepare three items before starting.

### 1.1 Base URL

The Base URL is the AI Gateway endpoint address. This example uses:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1>
~~~

The address already includes `/v1`. Do not manually append another `/v1` to get `/v1/v1`, and do not write it as a specific endpoint such as `/chat/completions` or `/messages`. The OpenCode provider runtime will automatically append the endpoint.

### 1.2 API Key

Create an API Key in the AI Gateway console and confirm:

- The API Key has not expired;
- The API Key has model call permissions;
- No extra spaces or newlines were included when copying;
- The API Key and Base URL belong to the same environment;
- If the relay distinguishes permissions by protocol, the API Key has the OpenAI, Responses, or Anthropic routing permissions you intend to use.

The API Key's permissions may be narrower than the product catalog. Different users, subscription plans, or tenants may see different model ranges. Query both your OpenAI and Anthropic authentication views first, then add the models you actually use to the configuration.

### 1.3 Whether a VPN Is Needed

OpenCode requests the AI Gateway you configured, not Anthropic or OpenAI directly. As long as your machine can access the relay, a VPN is generally not needed.

First run the `/models` from Section 6 and the curl from Section 7:

- If a TLS connection is established but returns `401`, `No upstream candidates`, or `502`: this is usually an API Key, model ID, protocol, or upstream routing issue, not a VPN issue;
- If DNS failure, connection timeout, or TLS handshake failure occurs: then check your network, corporate proxy, firewall, or VPN first.

### 1.4 Where to Run Commands

All commands are run in macOS Terminal. Press Command + Space, type Terminal, and press Enter to open it.

The terminal prompt may look like:

~~~text
a123@Mac ~ %
~~~

Do not copy the prompt itself — only copy the commands in the code blocks.

**Next step:** Proceed to Section 2 to check the basic tools and OpenCode.

---

## 2. Verify Basic Tools and OpenCode

### 2.1 Check curl, jq, Node.js

In Terminal, run:

~~~bash
command -v curl
command -v jq
node --version
npm --version
~~~

If you see the file paths for `curl` and `jq`, and Node.js and npm return version numbers, you can continue.

If jq is not found:

~~~bash
command -v brew
~~~

If brew exists:

~~~bash
brew install jq
jq --version
~~~

If brew is also not found, install Homebrew first, then install jq. The model directory and response parsing commands later require jq.

**Next step:** Check whether the OpenCode command is already installed.

### 2.2 Install or Verify OpenCode

Run first:

~~~bash
command -v opencode
opencode --version
type -a opencode
~~~

If a path and version number are returned, you can proceed directly to Section 3. If `type -a opencode` shows multiple paths, confirm which version Terminal is using when troubleshooting later.

If not yet installed, you can use npm:

~~~bash
npm install -g opencode-ai
opencode --version
~~~

You can also use the official OpenCode install script:

~~~bash
curl -fsSL --proto '=https' --tlsv1.2 https://opencode.ai/install | bash
opencode --version
~~~

A version number should be returned, for example:

~~~text
1.18.18
~~~

If `opencode: command not found` is displayed, first verify that npm's global bin is in PATH:

~~~bash
NPM_GLOBAL_BIN="$(npm prefix -g)/bin"
printf 'npm global bin: %s\n' "$NPM_GLOBAL_BIN"
test -x "$NPM_GLOBAL_BIN/opencode" && echo 'opencode is installed but the current PATH does not include this directory'
command -v opencode
~~~

If the command is installed but the current Terminal cannot find it, add the actual npm global bin directory to `~/.zshrc`, reopen Terminal, then run `opencode --version`. Do not repeatedly reinstall to work around PATH issues.

**Next step:** After confirming the OpenCode version, proceed to Section 3 to save the API Key.

---

## 3. Securely Enter the API Key in the Current Terminal

Do not write the API Key directly in command-line arguments, as it may end up in Terminal history. In the same Terminal session, run:

~~~bash
export RELAY_BASE_URL='https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1'
RELAY_BASE_URL="${RELAY_BASE_URL%/}"
read -s "RELAY_API_KEY?Paste your AI Gateway API Key, then press Enter: "
echo
export CLICKZETTA_API_KEY="$RELAY_API_KEY"
~~~

The screen will not display characters when pasting the API Key — this is normal. `export` is only valid for the current Terminal session; the variable disappears when the window is closed.

When checking whether the variable exists, do not print the actual value:

~~~bash
if [ -n "$CLICKZETTA_API_KEY" ]; then
  echo 'CLICKZETTA_API_KEY is loaded'
else
  echo 'CLICKZETTA_API_KEY is not loaded'
fi
~~~

### 3.1 Why a New Terminal Requires Reloading

The variables above are only valid in the current Terminal window. After closing the window or restarting the computer, if you see `API Key: missing`, this is usually not an OpenCode configuration failure — it means the new Terminal has not yet loaded the environment variables.

For temporary use, simply re-run the `read -s` command in this section in each new Terminal.

### 3.2 Long-Term Use: Save to macOS Keychain (Recommended)

After completing the `read -s` above, you can save the current variable to macOS Keychain. The API Key in the command below is still passed through the variable — do not write the real value directly into the command:

~~~bash
security add-generic-password \
  -U \
  -a "$USER" \
  -s 'opencode-singdata-api-key' \
  -w "$CLICKZETTA_API_KEY"
~~~

To load in a new Terminal later, run the following command — it will not print the API Key on screen:

~~~bash
export RELAY_BASE_URL='https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1'
export CLICKZETTA_API_KEY="$(security find-generic-password \
  -a "$USER" \
  -s 'opencode-singdata-api-key' \
  -w)"
test -n "$CLICKZETTA_API_KEY" && echo 'API Key loaded from macOS Keychain'
~~~

macOS may prompt you to confirm Keychain access on first read — this is normal. If you no longer need it, you can delete the entry:

~~~bash
security delete-generic-password \
  -a "$USER" \
  -s 'opencode-singdata-api-key'
~~~

If you are not on macOS, use your system's password manager or a permission-restricted local key solution. Do not write the real value into this guide, a Git repository, screenshots, project directories, a publicly accessible `opencode.json`, or shell configuration files that sync to the cloud.

**Next step:** Do not open OpenCode yet. Query the model directory by protocol as described below.

---

## 4. Where Is the OpenCode Configuration File

This section only confirms the location of the configuration file and creates a backup. Do not write all untested models into it yet; the model directory and curl tests are completed in Sections 6 and 7, and the actual configuration writing happens in Section 8.

The default macOS configuration file is:

~~~text
~/.config/opencode/opencode.json
~~~

That is:

~~~text
/Users/your-username/.config/opencode/opencode.json
~~~

Check the directory and file first:

~~~bash
mkdir -p "$HOME/.config/opencode"
ls -la "$HOME/.config/opencode"
~~~

Back up the existing configuration before modifying it for the first time:

~~~bash
if [ -f "$HOME/.config/opencode/opencode.json" ]; then
  cp -p "$HOME/.config/opencode/opencode.json" "$HOME/.config/opencode/opencode.json.bak"
fi
~~~

### 4.1 Important: OpenCode Version Format Differences

This guide is based on OpenCode `1.18.18` and uses the following fields:

~~~text
provider       singular
npm            the AI SDK runtime used by the provider
options        runtime parameters such as baseURL
models         the model dictionary under the provider
~~~

Newer OpenCode documentation may use `providers`, `package`, `settings`, and other fields. Do not mix the two formats in the same file. The most reliable approach is: check your local `opencode --version` first, then write the configuration according to that version's schema.

If your version is not `1.18.18`, run first:

~~~bash
opencode debug config
~~~

If it reports a configuration schema error, migrate to that version's configuration format first. You cannot simply rename `provider` to `providers` or vice versa.

**Next step:** Understand the provider-to-protocol mapping in Section 5 before querying the model directory.

---

## 5. Understanding OpenCode's Three Providers

OpenCode does not automatically select a request protocol based on the model ID. The protocol is determined by the provider's runtime package.

This guide uses three providers:

~~~text
my-relay
  → @ai-sdk/openai-compatible
  → POST /v1/chat/completions
  → Authorization: Bearer API_KEY

my-relay-responses
  → @ai-sdk/openai
  → POST /v1/responses
  → Authorization: Bearer API_KEY

my-relay-anthropic
  → @ai-sdk/anthropic
  → POST /v1/messages
  → x-api-key: API_KEY
  → anthropic-version: 2023-06-01
~~~

The model reference format is:

~~~text
<provider-id>/<model-id>
~~~

For example:

~~~text
my-relay/openai/gpt-5.5
my-relay-anthropic/anthropic/claude-opus-5
~~~

Here, `my-relay-anthropic` is the OpenCode provider ID, and `anthropic/claude-opus-5` is the relay's model ID. The presence of `anthropic/` in the model ID does not automatically switch `my-relay` to the Anthropic protocol.

The following are protocol mismatches:

~~~text
my-relay/anthropic/claude-opus-5
my-relay-anthropic/openai/gpt-5.5
~~~

**Next step:** Proceed to Section 6 to query the model directory by authentication method.

---

## 6. Retrieve the Live Model Directory

The model directory must be queried separately for each protocol. You cannot run `/models` just once and assume the result covers all models in the relay.

### 6.1 OpenAI View

OpenAI Compatible uses Bearer authentication:

~~~bash
curl -sS -o /tmp/opencode-gateway-models-openai.json \
  --max-time 30 \
  -w 'HTTP %{http_code}\n' \
  "$RELAY_BASE_URL/models" \
  -H "Authorization: Bearer $CLICKZETTA_API_KEY" \
  -H 'Accept: application/json'
~~~

After HTTP 200, run:

~~~bash
jq -r '
  if (.data | type) == "array" then
    .data[].id
  else
    .error.message // .message // "No model directory found"
  end
' /tmp/opencode-gateway-models-openai.json
~~~

Return value meanings:

| Response | Meaning | Next step |
|---|---|---|
| HTTP 200 | Network and Bearer authentication are working | View the directory and test specific models |
| HTTP 401/403 | API Key is incorrect, expired, or lacks permissions | Check API Key, tenant, and permissions |
| HTTP 404 | Base URL or `/v1` path is incorrect | Check the address; avoid duplicate `/v1` |
| HTTP 429 | Rate limit, quota, or concurrency limit | Wait and retry, or check quota |
| HTTP 5xx | Temporary gateway or upstream error | Retry later and save the sanitized error |
| No HTTP status, DNS failure, or timeout | Request did not reach the gateway | Check network, proxy, firewall, or VPN |

A model appearing in the directory only means the current API Key can see that ID. It does not mean the model is available under all three protocols: Chat, Responses, and Anthropic. Continue with the specific request tests in Section 7.

### 6.2 Anthropic View

Anthropic Messages uses a different authentication header:

~~~bash
curl -sS -o /tmp/opencode-gateway-models-anthropic.json \
  --max-time 30 \
  -w 'HTTP %{http_code}\n' \
  "$RELAY_BASE_URL/models" \
  -H "x-api-key: $CLICKZETTA_API_KEY" \
  -H 'anthropic-version: 2023-06-01' \
  -H 'Accept: application/json'
~~~

After HTTP 200, run:

~~~bash
jq -r '
  if (.data | type) == "array" then
    .data[].id
  else
    .error.message // .message // "No Anthropic model directory found"
  end
' /tmp/opencode-gateway-models-anthropic.json
~~~

If the OpenAI view and Anthropic view differ, this is expected behavior. Different authentication headers and protocol contexts allow the AI Gateway to return different model directories. Query both views using your own API Key — do not copy a static list.

### 6.3 Understanding OpenCode's Built-in Model Directory

If you run:

~~~bash
opencode models
~~~

You will see many providers in OpenCode's built-in directory, such as `amazon-bedrock/anthropic.claude-*`. These entries belong to the AWS Bedrock provider, not this relay. They do not mean you have obtained AWS credentials, and they do not mean OpenCode will automatically call them through the relay.

OpenCode's built-in directory and the relay directory are two separate directories. Only providers written in `opencode.json` will make requests through this relay.

### 6.4 How to Use Your Own Model Directory

You do not need to copy all models from this guide's examples into your configuration file. It is recommended to follow these rules:

1. Save the OpenAI and Anthropic `/models` output for your API Key;
2. Only put model IDs that exist in your own directory into the corresponding provider;
3. For each model you plan to use, run the minimal text request for the corresponding protocol in Section 7;
4. Only models that return HTTP 200 with final text should proceed to actual OpenCode calls;
5. If a model is in the directory but the request returns `No upstream candidates` or `502`, keep a record but do not mark it as usable;
6. If your directory does not match expectations, treat the live directory as the source of truth, then contact relay support to confirm permissions or routing.

The model directory is a live snapshot of permissions and routing, not a "master model list" to be maintained manually. Whether a model can be used depends on verifying the model ID, protocol, provider, and actual call result together.

**Next step:** Copy a complete model ID from the corresponding directory, then run the protocol request in Section 7.

---

## 7. Verify Protocol and Model Using Standard curl

### 7.1 OpenAI Chat Completions

Request endpoint:

~~~text
POST /v1/chat/completions
Authorization: Bearer API_KEY
~~~

Copy a complete model ID from the results in Section 6.1:

~~~bash
read "CHAT_MODEL_ID?Paste the complete model ID for Chat protocol: "
~~~

Run:

~~~bash
curl -sS -o /tmp/opencode-test-chat.json \
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
      messages: [{role: "user", content: "Reply only: Chat connection successful"}]
    }')"
~~~

Extract the final text:

~~~bash
jq -r '
  .choices[0].message.content
  // .error.message
  // .message
  // "HTTP returned, but no final text found"
' /tmp/opencode-test-chat.json
~~~

On success, you should see:

~~~text
HTTP 200
Chat connection successful
~~~

If successful, you only need to configure `my-relay` in Section 8.

### 7.2 OpenAI Responses

Request endpoint:

~~~text
POST /v1/responses
Authorization: Bearer API_KEY
~~~

Copy a complete model ID from the results in Section 6.1:

~~~bash
read "RESPONSES_MODEL_ID?Paste the complete model ID for Responses protocol: "
~~~

Run. Responses uses `input` and `max_output_tokens` — do not directly copy the Chat Completions `messages` request body:

~~~bash
curl -sS -o /tmp/opencode-test-responses.json \
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
      max_output_tokens: 512
    }')"
~~~

Extract the final text:

~~~bash
jq -r '
  ([.output[]?.content[]? | select(.type == "output_text" or .type == "text") | .text] | join("\n")) as $text
  | if ($text | length) > 0 then
      $text
    else
      .error.message // .message // "HTTP returned, but no final text found"
    end
' /tmp/opencode-test-responses.json
~~~

The Responses response structure may differ across gateways or SDKs, typically reading from `output[].content[].text` or `output_text`.

On success, you should see:

~~~text
HTTP 200
Responses connection successful
~~~

Responses results cannot be inferred from Chat results: the upstream routing for the same model at the two endpoints may differ. The `my-relay` in this guide's OpenCode configuration does not configure the Responses runtime, so do not treat a successful curl Responses test as meaning OpenCode has Responses enabled.

Responses is an optional integration path. Only if the same model first passes the `/responses` standard curl in this section, then is configured per Section 8.4 as `my-relay-responses`, and then returns final text via the Section 10.2 `opencode run`, can you conclude that Responses is usable in your environment. This guide provides configuration templates but does not guarantee your API Key or upstream routing has that protocol enabled.

### 7.3 Anthropic Messages

Request endpoint:

~~~text
POST /v1/messages
x-api-key: API_KEY
anthropic-version: 2023-06-01
~~~

Copy a complete model ID from the results in Section 6.2:

~~~bash
read "ANTHROPIC_MODEL_ID?Paste the complete model ID for Anthropic protocol: "
~~~

For this guide's example AI Gateway, the preferred and verified integration path for Claude is currently Anthropic Messages, so use the following request structure:

~~~bash
curl -sS -o /tmp/opencode-test-anthropic.json \
  --max-time 60 \
  -w 'HTTP %{http_code}\n' \
  "$RELAY_BASE_URL/messages" \
  -H "x-api-key: $CLICKZETTA_API_KEY" \
  -H 'anthropic-version: 2023-06-01' \
  -H 'content-type: application/json' \
  -d "$(jq -cn \
    --arg model "$ANTHROPIC_MODEL_ID" \
    '{
      model: $model,
      max_tokens: 1024,
      messages: [{role: "user", content: "Reply only: Anthropic connection successful"}]
    }')"
~~~

Extract the final text:

~~~bash
jq -r '
  ([.content[]? | select(.type == "text") | .text] | join("\n")) as $text
  | if ($text | length) > 0 then
      $text
    else
      .error.message // .message // "HTTP returned, but no final text found"
    end
' /tmp/opencode-test-anthropic.json
~~~

On success, you should see:

~~~text
HTTP 200
Anthropic connection successful
~~~

Do not set `max_tokens` too small during testing; some responses with a thinking process may only return thinking content, leading to a false conclusion of no final text. It is recommended to start with `1024` for the minimal text test.

Below are example model ID formats. In actual use, only substitute model IDs that exist in your own Anthropic directory and have passed the request validation:

~~~text
anthropic/claude-haiku-4.5
anthropic/claude-opus-4.8
anthropic/claude-opus-5
anthropic/claude-sonnet-4.6
anthropic/claude-sonnet-5
~~~

If successful, you only need to configure `my-relay-anthropic` in Section 8.

### 7.4 HTTP 200 But No Final Text

Some reasoning models may first generate thinking or reasoning content. If the output budget is too small, the request may return HTTP 200 but with no final text.

You can increase the value in the corresponding request:

~~~text
max_tokens: 512
max_output_tokens: 512
~~~

First raise it to `1024`, and if still insufficient, raise it to `4096`. If after increasing the budget there is still only thinking or reasoning and no final text, view the complete JSON locally only, and verify whether the response structure matches the current protocol. Do not mark the model as usable under this protocol, and do not paste the full unredacted JSON into a chat or ticket.

**Next step:** Only write the models that just succeeded with curl into the corresponding OpenCode provider, then proceed to Section 8.

---

## 8. Write the OpenCode Configuration

Below is the base configuration template for OpenCode `1.18.18`. It uses `my-relay` for OpenAI Compatible Chat and `my-relay-anthropic` for Anthropic Messages. Only add `my-relay-responses` per Section 8.4 if the `/responses` test succeeds. The API Key is not stored in the configuration file; it is injected via the environment variable `CLICKZETTA_API_KEY`.

### 8.1 Before Copying the Configuration, Distinguish "Fixed Parts" from "Variable Parts"

| Configuration content | Can be used as-is | Note |
|---|---:|---|
| `provider` object structure | Yes | OpenCode `1.18.18` uses singular `provider`; do not mix with newer format |
| `@ai-sdk/openai-compatible` | Yes | Only for OpenAI Compatible Chat; does not enable Responses |
| `@ai-sdk/openai` | Use as needed | Only for models that passed the `/responses` test; configure in a separate provider |
| `@ai-sdk/anthropic` | Yes | For Anthropic Messages; Claude in this guide's example gateway uses this provider |
| `baseURL` | Must replace | Use your own relay Base URL, ensuring it contains only one `/v1` |
| `CLICKZETTA_API_KEY` | Must replace | Use your own API Key; do not write into JSON |
| Root-level `model` | Replace as needed | Must point to a `<provider>/<model-id>` you have verified |
| Model IDs under `models` | Replace as needed | Only keep model IDs that exist in your `/models` and have passed the minimal request test |
| `limit.context`, `limit.output` | Adjust as needed | These are OpenCode client budgets, not permanent relay guarantees |

### 8.2 Option A: Write the OpenAI Chat Provider via Terminal

This is the recommended approach. It only modifies the `my-relay` provider and preserves other content in the configuration file. You must have completed Section 7.1 and `CHAT_MODEL_ID` must still exist in the current Terminal.

If you already have a different provider name, you can set `OPENAI_PROVIDER_ID` before running; if not set, it defaults to `my-relay`.

~~~bash
set -e
OPENAI_PROVIDER_ID="${OPENAI_PROVIDER_ID:-my-relay}"
test -n "$CHAT_MODEL_ID" || read "CHAT_MODEL_ID?Paste the successfully tested Chat model ID: "
CONFIG_FILE="$HOME/.config/opencode/opencode.json"
mkdir -p "$(dirname "$CONFIG_FILE")"

if [ -f "$CONFIG_FILE" ]; then
  cp -p "$CONFIG_FILE" "$CONFIG_FILE.backup-$(date +%Y%m%d-%H%M%S)"
else
  printf '%s\n' '{"$schema":"https://opencode.ai/config.json","provider":{}}' > "$CONFIG_FILE"
fi

CHAT_PROVIDER=$(jq -cn \
  --arg base "$RELAY_BASE_URL" \
  --arg model "$CHAT_MODEL_ID" \
  '{
    name: "AI Gateway (OpenAI Chat)",
    env: ["CLICKZETTA_API_KEY"],
    npm: "@ai-sdk/openai-compatible",
    options: {baseURL: $base},
    models: {($model): {name: $model}}
  }')

TMP_FILE=$(mktemp)
jq \
  --argjson provider "$CHAT_PROVIDER" \
  --arg provider_id "$OPENAI_PROVIDER_ID" \
  --arg model "$CHAT_MODEL_ID" \
  '.provider = (.provider // {})
   | .provider[$provider_id] as $existing
   | .provider[$provider_id] = (($existing // {}) * $provider)
   | .provider[$provider_id].models = (($existing.models? // {}) + $provider.models)
   | .model = ($provider_id + "/" + $model)' \
  "$CONFIG_FILE" > "$TMP_FILE" && mv "$TMP_FILE" "$CONFIG_FILE"

jq empty "$CONFIG_FILE"
opencode debug config >/dev/null && echo 'OpenAI Chat provider configured successfully'
~~~

### 8.3 Option B: Write the Anthropic Provider via Terminal

This is the recommended approach for Claude. You must have completed Section 7.3 and `ANTHROPIC_MODEL_ID` must still exist in the current Terminal.

If you already have a different provider name, you can set `ANTHROPIC_PROVIDER_ID` before running; if not set, it defaults to `my-relay-anthropic`.

~~~bash
set -e
ANTHROPIC_PROVIDER_ID="${ANTHROPIC_PROVIDER_ID:-my-relay-anthropic}"
test -n "$ANTHROPIC_MODEL_ID" || read "ANTHROPIC_MODEL_ID?Paste the successfully tested Anthropic model ID: "
CONFIG_FILE="$HOME/.config/opencode/opencode.json"
mkdir -p "$(dirname "$CONFIG_FILE")"

if [ -f "$CONFIG_FILE" ]; then
  cp -p "$CONFIG_FILE" "$CONFIG_FILE.backup-$(date +%Y%m%d-%H%M%S)"
else
  printf '%s\n' '{"$schema":"https://opencode.ai/config.json","provider":{}}' > "$CONFIG_FILE"
fi

ANTHROPIC_PROVIDER=$(jq -cn \
  --arg base "$RELAY_BASE_URL" \
  --arg model "$ANTHROPIC_MODEL_ID" \
  '{
    name: "AI Gateway (Anthropic Messages)",
    env: ["CLICKZETTA_API_KEY"],
    npm: "@ai-sdk/anthropic",
    options: {baseURL: $base},
    models: {($model): {name: $model}}
  }')

TMP_FILE=$(mktemp)
jq \
  --argjson provider "$ANTHROPIC_PROVIDER" \
  --arg provider_id "$ANTHROPIC_PROVIDER_ID" \
  --arg model "$ANTHROPIC_MODEL_ID" \
  '.provider = (.provider // {})
   | .provider[$provider_id] as $existing
   | .provider[$provider_id] = (($existing // {}) * $provider)
   | .provider[$provider_id].models = (($existing.models? // {}) + $provider.models)
   | .model = ($provider_id + "/" + $model)' \
  "$CONFIG_FILE" > "$TMP_FILE" && mv "$TMP_FILE" "$CONFIG_FILE"

jq empty "$CONFIG_FILE"
opencode debug config >/dev/null && echo 'Anthropic provider configured successfully'
~~~

If you need multiple protocols, run each option separately after passing the curl test. Each command writes an independent provider, without placing Claude into the OpenAI provider or mistaking Responses models for Chat models. The last option run will set the corresponding model as the default model; you can still use `--model` to switch temporarily.

### 8.4 Option C: Write the OpenAI Responses Provider via Terminal (Optional)

Only run this section if Section 7.2 returned HTTP `200` and the final text was extracted. Do not skip the Responses test just because the model name contains `openai` or `gpt`.

If you already have a different provider name, you can set `RESPONSES_PROVIDER_ID` before running; if not set, it defaults to `my-relay-responses`.

~~~bash
set -e
RESPONSES_PROVIDER_ID="${RESPONSES_PROVIDER_ID:-my-relay-responses}"
test -n "$RESPONSES_MODEL_ID" || read "RESPONSES_MODEL_ID?Paste the successfully tested Responses model ID: "
CONFIG_FILE="$HOME/.config/opencode/opencode.json"
mkdir -p "$(dirname "$CONFIG_FILE")"

if [ -f "$CONFIG_FILE" ]; then
  cp -p "$CONFIG_FILE" "$CONFIG_FILE.backup-$(date +%Y%m%d-%H%M%S)"
else
  printf '%s\n' '{"$schema":"https://opencode.ai/config.json","provider":{}}' > "$CONFIG_FILE"
fi

RESPONSES_PROVIDER=$(jq -cn \
  --arg base "$RELAY_BASE_URL" \
  --arg model "$RESPONSES_MODEL_ID" \
  '{
    name: "AI Gateway (OpenAI Responses)",
    env: ["CLICKZETTA_API_KEY"],
    npm: "@ai-sdk/openai",
    options: {baseURL: $base},
    models: {($model): {name: $model}}
  }')

TMP_FILE=$(mktemp)
jq \
  --argjson provider "$RESPONSES_PROVIDER" \
  --arg provider_id "$RESPONSES_PROVIDER_ID" \
  --arg model "$RESPONSES_MODEL_ID" \
  '.provider = (.provider // {})
   | .provider[$provider_id] as $existing
   | .provider[$provider_id] = (($existing // {}) * $provider)
   | .provider[$provider_id].models = (($existing.models? // {}) + $provider.models)
   | .model = ($provider_id + "/" + $model)' \
  "$CONFIG_FILE" > "$TMP_FILE" && mv "$TMP_FILE" "$CONFIG_FILE"

jq empty "$CONFIG_FILE"
opencode debug config >/dev/null && echo 'OpenAI Responses provider configured successfully'
~~~

`@ai-sdk/openai` and `@ai-sdk/openai-compatible` can share the same model ID, but they are not the same runtime. The Responses provider does not replace the Chat provider. If the same model succeeds under both protocols, you can keep both providers simultaneously.

### 8.5 Manual Configuration File Editing

If you prefer not to use the Terminal write commands, you can open the configuration file in an editor:

~~~bash
open -e "$HOME/.config/opencode/opencode.json"
~~~

The JSON below is a minimal manual editing example. Before saving, replace the example model IDs with models that passed testing in Section 7. Do not copy model IDs that do not exist in your own directory.

~~~json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "my-relay/openai/gpt-5.5",
  "provider": {
    "my-relay": {
      "name": "AI Gateway (OpenAI Chat)",
      "env": ["CLICKZETTA_API_KEY"],
      "npm": "@ai-sdk/openai-compatible",
      "options": {
        "baseURL": "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1"
      },
      "models": {
        "openai/gpt-5.5": {
          "name": "OpenAI model example"
        }
      }
    },
    "my-relay-anthropic": {
      "name": "AI Gateway (Anthropic Messages)",
      "env": ["CLICKZETTA_API_KEY"],
      "npm": "@ai-sdk/anthropic",
      "options": {
        "baseURL": "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1"
      },
      "models": {
        "anthropic/claude-opus-5": {
          "name": "Anthropic model example"
        }
      }
    }
  }
}
~~~

The API Key is not stored in the configuration file; OpenCode reads the token from the environment variable `CLICKZETTA_API_KEY`.

If you need to manually add a Responses provider, use the `my-relay-responses` object from Section 8.4 as a third `provider` entry. Do not change the `npm` of the existing `my-relay` to `@ai-sdk/openai`.

### 8.6 Models That Appear in the Directory but Fail Requests

Some models may appear in `/models` but actual requests may still return `No upstream candidates`, `model_not_found`, or HTTP `502`. This usually means the model's permissions, protocol routing, or upstream status is not yet ready — it is not an OpenCode configuration file syntax error.

In this situation, do not keep the model in the configuration just to make it appear in the OpenCode list. Record the model ID, request protocol, HTTP status code, and sanitized error, contact the relay to confirm routing, and only add it to the configuration once the corresponding protocol returns final text.

### 8.7 Adjusting Models to Match Your Own Directory

When your model directory differs from this guide's example configuration, only modify the `models` object — do not arbitrarily change the provider runtime:

1. Remove models from `my-relay.models` that are not in your OpenAI directory;
2. Remove models from `my-relay-anthropic.models` that are not in your Anthropic directory;
3. If the same Qwen or DeepSeek ID succeeds under multiple protocols, you can add it to each corresponding provider;
4. For this guide's example gateway, Claude goes into `my-relay-anthropic.models`. Do not put it into `my-relay` just because its ID contains `anthropic/`. Only if Claude also appears in the OpenAI authentication view, and both the Chat curl and OpenCode call return final text, can you additionally configure an OpenAI Chat path;
5. Before adding a new model, you must first run the curl for the corresponding protocol and confirm the response contains final text;
6. Do not fabricate model IDs to make them appear in the OpenCode list — list visibility does not equal actual usability.

**Next step:** After saving the JSON, validate the syntax and OpenCode configuration.

---

## 9. Validate the OpenCode Configuration

### 9.1 Validate JSON Syntax

~~~bash
jq empty "$HOME/.config/opencode/opencode.json"
~~~

No output and an exit code of 0 means the JSON syntax is correct.

### 9.2 Validate OpenCode Schema

~~~bash
opencode debug config
~~~

Under normal circumstances, the parsed configuration is output. Errors such as `Config validation failed`, `expected object`, or `unknown key` must not appear.

If you see:

~~~text
Invalid input: expected object, received string
~~~

This usually means the provider object was written as a string, or the new-version `providers` format was mixed with the current-version `provider` format. Check that both `provider.my-relay` and `provider.my-relay-anthropic` are JSON objects.

### 9.3 View Models for Configured Providers

If you used a custom provider ID in Section 8, replace the names in the commands below with your actual IDs.

~~~bash
opencode models my-relay
opencode models my-relay-anthropic
# Only run if the Responses provider was configured in Section 8.4:
# opencode models my-relay-responses
~~~

If a Responses provider was configured, remove the leading `# ` from the last line and run it separately.

These commands list the models you wrote into the configuration file. Models appearing here only means they are registered in the configuration — it does not mean every request will succeed. You still need to run the actual calls in Section 10.

**Next step:** Use `opencode run` in Section 10 to send the first message.

---

## 10. Making Actual Calls in OpenCode

For the first verification, it is recommended to use an isolated temporary directory to prevent OpenCode from reading the current project's code, instruction files, or session context. In Terminal, run:

~~~bash
TEST_DIR="$(mktemp -d "${TMPDIR:-/tmp}/opencode-gateway-test.XXXXXX")"
printf 'Test directory: %s\n' "$TEST_DIR"
~~~

The first test commands below all use `--dir "$TEST_DIR"`. This only changes the test working directory; it does not change OpenCode's global provider configuration.

### 10.1 Call the OpenAI Chat Provider

If you used a custom provider ID, replace `my-relay` in the command with your actual ID.

The example below uses `openai/gpt-5.5`. If that ID is not in your API Key's OpenAI directory, replace it with an OpenAI Chat model that exists in your directory and was validated in Section 7. The provider syntax remains the same.

~~~bash
opencode run \
  --dir "$TEST_DIR" \
  --model my-relay/openai/gpt-5.5 \
  --format json \
  'Reply only: OK'
~~~

On success, the JSON should contain model output text.

If you need to test DeepSeek, and the model exists in your directory, first add it to `my-relay.models`, then use the same provider syntax:

~~~bash
opencode run \
  --dir "$TEST_DIR" \
  --model my-relay/deepseek/deepseek-v4-pro \
  --format json \
  'Reply only: OK'
~~~

### 10.2 Call the OpenAI Responses Provider (Optional)

Only run this command if you have already completed Sections 7.2 and 8.4. Replace the example ID with the model ID that returned final text under `/responses`.

~~~bash
opencode run \
  --dir "$TEST_DIR" \
  --model my-relay-responses/openai/gpt-5.5 \
  --format json \
  'Reply only: OK'
~~~

If this command succeeds, it means OpenCode has called the model through `/responses` using `@ai-sdk/openai`. If curl succeeded but this fails, return to Section 12.2 to confirm you are not mistakenly using the Chat provider.

### 10.3 Call the Anthropic Provider

If you used a custom provider ID, replace `my-relay-anthropic` in the command with your actual ID.

The example below uses `anthropic/claude-opus-5`. If your API Key does not have permission for that Claude model, replace it with a Claude ID that exists in your Anthropic directory and was validated in Section 7. Continue using `my-relay-anthropic` per the already-verified path in this guide.

~~~bash
opencode run \
  --dir "$TEST_DIR" \
  --model my-relay-anthropic/anthropic/claude-opus-5 \
  --format json \
  'Reply only: OK'
~~~

If your Anthropic directory has Sonnet or Haiku, first add the corresponding IDs to `my-relay-anthropic.models`, then test them separately:

~~~bash
opencode run --dir "$TEST_DIR" --model my-relay-anthropic/anthropic/claude-sonnet-5 --format json 'Reply only: OK'
opencode run --dir "$TEST_DIR" --model my-relay-anthropic/anthropic/claude-haiku-4.5 --format json 'Reply only: OK'
~~~

### 10.4 Default Model

The following in the configuration file:

~~~json
{
  "model": "my-relay/openai/gpt-5.5"
}
~~~

means GPT-5.5 is used when `--model` is not specified. If you prefer Claude as the default, change it to:

~~~json
{
  "model": "my-relay-anthropic/anthropic/claude-sonnet-5"
}
~~~

After making the change, re-run `opencode debug config`, then re-run the command.

### 10.5 Results and Criteria After Configuration

After completing the configuration, you should see at least one model for which you have permission returning final text. If your API Key has both OpenAI and Anthropic model permissions, check the following results separately:

~~~text
OpenAI Chat provider: returns OK
  my-relay/openai/gpt-5.5

Anthropic Messages provider: returns OK
  my-relay-anthropic/anthropic/claude-opus-5
~~~

If both types of calls succeed, it means:

- OpenCode can read the configuration file;
- The API Key has been passed through the environment variable;
- OpenAI Compatible Chat routing is available;
- Anthropic Messages routing is available;
- At least one OpenAI model and one Claude model have completed an end-to-end call.

If your API Key has no Claude permissions, only check OpenAI Chat. If you have no OpenAI models, only check the Anthropic provider. Do not add models that do not exist in your directory just to satisfy the examples.

This does not mean all models are usable or all advanced capabilities are available. Other models must follow the vendor and protocol rules in Section 11 to choose a provider, and must be individually checked using the commands in Section 7 and this section.

**Next step:** Select models according to the vendor and protocol rules in Section 11 — do not guess the protocol based solely on the model name.

---

## 11. Selecting Models by Vendor and Protocol

Model IDs are returned by the relay; the vendor name or ID prefix alone cannot determine the request protocol. When configuring, first confirm which vendor type the model belongs to, then select the provider based on what your directory and test results show.

The information below helps you complete the configuration; it is not a fixed model list. The number of models, versions, and permissions may vary by API Key, subscription plan, and upstream routing.

### 11.1 How to Interpret Directory and Request Results

| Status | Meaning | Next step |
|---|---|---:|
| Success | HTTP 200, and the response contains final model text | Can configure under this protocol |
| No upstream | HTTP 400, returns `No upstream candidates` | Check model ID, protocol, permissions, and routing |
| Upstream failed | HTTP 502, returns `UPSTREAM_ALL_FAILED` or `Upstream failed` | Retry later; if still failing, contact the relay |
| Client waiting | OpenCode keeps waiting or retrying with no final model text returned | First reproduce with curl, then check the provider |
| Not in directory | The model is not in `/models` for the current authentication method | Do not configure under this protocol |

"Success" requires both HTTP 200 and final text. If HTTP 200 is returned but only a thinking block is present with no final text, continue checking the output budget and response parsing.

### 11.2 Vendor Types and Protocol Selection

| Vendor or model type | OpenAI Chat | OpenAI Responses | Anthropic Messages | OpenCode provider | Configuration principle |
|---|---|---|---|---|---|
| OpenAI, Codex, and other OpenAI series | Typically used | Only when explicitly provided by the model and gateway | Typically not used | Chat: `my-relay`; Responses: `my-relay-responses` | Choose based on actual successful endpoint; do not put OpenAI models into the Anthropic provider |
| Anthropic Claude series | Only when gateway explicitly provides a compatible route and it is verified in testing | Requires separate testing | Preferred and verified path for this guide's example gateway | `my-relay-anthropic` | Test Anthropic Messages first; `anthropic/` in the ID does not automatically switch protocols |
| DeepSeek series | May be available | Confirm by model and gateway routing | May be available | Choose based on actual successful protocol | Chat success does not imply Responses success; if both protocols succeed, you can configure both |
| Qwen series | May be available | Confirm by model and gateway routing | May be available | Choose based on actual successful protocol | Base decisions on your own `/models` and minimal request results |
| Other vendors or custom models | Cannot infer | Cannot infer | Cannot infer | Configure by protocol separately | Do not guess the protocol based on vendor name or model prefix |

"Typically" here refers to common adaptation patterns, not automatic routing rules. Each model still needs to be verified using your own directory, protocol request, and OpenCode call results.

### 11.3 OpenCode Configuration Syntax

Model references always use the following format:

~~~text
<provider-id>/<model-id>
~~~

Common examples:

~~~text
my-relay/openai/gpt-5.5
my-relay-responses/openai/gpt-5.5
my-relay-anthropic/anthropic/claude-opus-5
my-relay/deepseek/deepseek-v4-pro
my-relay-anthropic/deepseek/deepseek-v4-pro
~~~

The last two examples are only valid simultaneously if DeepSeek has passed both OpenAI Chat and Anthropic Messages. The following do not automatically change the protocol:

~~~text
my-relay/anthropic/claude-opus-5
my-relay-anthropic/openai/gpt-5.5
~~~

### 11.4 Actual Steps for Selecting a Model

For each model you plan to use, follow these steps in order:

1. Confirm the model ID appears in `/models` for the corresponding authentication method;
2. Test using the OpenAI Chat, Responses, or Anthropic Messages request from Section 7;
3. Only place the model into the corresponding provider when HTTP 200 with final text is returned;
4. Use `opencode run` from Section 10 for an actual call;
5. If OpenCode fails, first compare using a curl with the same model and same protocol to determine whether it is a gateway issue or a client configuration issue.

### 11.5 Claude Model ID Format

Claude version numbers and punctuation are part of the routing key and must be copied exactly:

The examples below show formatting only — Claude is not limited to these versions. Use the values returned by your own Anthropic `/models`.

~~~text
Correct: anthropic/claude-opus-4.8
Incorrect: anthropic/claude-opus-4-8

Correct: anthropic/claude-sonnet-4.6
Incorrect: anthropic/claude-sonnet-4-6

Correct: anthropic/claude-haiku-4.5
Incorrect: anthropic/claude-haiku-4-5
~~~

The incorrect hyphen version will return `No upstream candidates`, not a missing Claude feature in OpenCode.

### 11.6 OpenCode Capability Boundaries

This guide covers three request methods, with Responses being optional:

| Capability | Configuration | Note |
|---|---|---|
| OpenAI Compatible Chat | `my-relay` + `@ai-sdk/openai-compatible` | Requests `/v1/chat/completions` |
| OpenAI Responses | `my-relay-responses` + `@ai-sdk/openai` | Requests `/v1/responses`; only use after completing both Sections 7.2 and 8.4 |
| Anthropic Messages | `my-relay-anthropic` + `@ai-sdk/anthropic` | Requests `/v1/messages`; Claude uses this method |

Model usability should be understood as follows:

1. "Appears in the directory" means the API Key can see the model ID;
2. "Protocol call succeeded" means the model returned final text under a specific protocol;
3. "OpenCode call succeeded" means the provider, model ID, and client parameter combination worked;
4. The above conclusions apply only to the corresponding protocol and do not automatically extend to other protocols;
5. A successful text call does not mean tool calling, streaming, multimodal input, structured output, caching, long context, or thinking parameters are also supported.

For this guide's example gateway, Claude should preferably use `my-relay-anthropic`. For OpenAI series configuration, use `my-relay` for Chat and `my-relay-responses` for Responses. For DeepSeek, Qwen, or other models, select the provider based on Section 11.2 and actual test results. If the gateway adds other protocol routes for Claude in the future, the three-layer verification of directory, curl, and OpenCode must be completed again.

**Next step:** Read Section 12 for details on protocol fields; go to Section 13 if you encounter errors.

---

## 12. OpenCode Request Protocol Constraints

### 12.1 Hard Differences Between the Three Protocols

Protocols cannot simply change the URL and continue using another protocol's request body. The client must match the endpoint, authentication header, request structure, and response parsing method simultaneously.

| Item | OpenAI Chat Completions | OpenAI Responses | Anthropic Messages |
|---|---|---|---|
| Endpoint | `POST /v1/chat/completions` | `POST /v1/responses` | `POST /v1/messages` |
| Authentication header | `Authorization: Bearer API_KEY` | `Authorization: Bearer API_KEY` | `x-api-key: API_KEY` |
| Required version header | None | None | `anthropic-version: 2023-06-01` |
| Input fields | `messages`, `max_tokens` | `input`, `max_output_tokens` | `messages`, `max_tokens`; system prompt usually in top-level `system` |
| Common final text location | `choices[0].message.content` | `output[].content[].text` or `output_text` | `text` in `content[]` where `type=text` |
| OpenCode provider in this guide | `my-relay` | `my-relay-responses`, configured per Section 8.4 | `my-relay-anthropic` uses Messages |

Required rules:

1. `anthropic/` in `anthropic/claude-opus-5` is only part of the model ID and does not automatically select the Anthropic runtime;
2. `my-relay/anthropic/claude-opus-5` still uses OpenAI Chat; do not use this syntax if the model has not passed Chat validation;
3. `my-relay-anthropic/anthropic/claude-opus-5` uses the Anthropic Messages path already verified in this guide;
4. `Authorization: Bearer` and `x-api-key + anthropic-version` will return different model views; do not query `/models` only once;
5. Chat success does not imply Responses success; the same model needs to be tested separately;
6. Anthropic Messages success does not imply OpenAI Chat success; Claude should generally use the Anthropic provider;
7. The AI Gateway does not guarantee automatic conversion of OpenAI `tool_calls` to Anthropic `tool_use`, nor the reverse.

### 12.2 Responses Must Use an Independent Provider

`my-relay` uses:

~~~text
@ai-sdk/openai-compatible
→ OpenAI Compatible Chat Completions
~~~

It will not automatically switch to Responses just because a model succeeded at `/v1/responses`. To use Responses, you must first complete the standard curl in Section 7.2, then configure `my-relay-responses` and `@ai-sdk/openai` per Section 8.4. The existing `my-relay` cannot be used as a Responses provider.

### 12.3 OpenCode Does Not Auto-Fallback

Once a provider is selected for a call, the request protocol is fixed:

~~~text
Chat failure
    ≠ Automatically switch to Responses
    ≠ Automatically switch to Anthropic Messages
    ≠ Automatically switch to another model
~~~

To switch protocols, you must explicitly select another provider. To switch models, you must explicitly provide another exact ID.

### 12.4 SDK May Alter Request Parameters

OpenCode assembles requests through the AI SDK runtime. Even if a bare curl succeeds, the client may still produce differences due to automatically adding thinking, tool, structured output, or streaming-related fields.

This guide only requires the minimal text request to succeed, which does not mean the following capabilities have been confirmed:

- Streaming output;
- Tool calling / function calling;
- JSON schema or strict structured output;
- Image, file, and multimodal input;
- Prompt caching;
- Behavior when long context approaches the limit;
- Model-specific thinking budget fields.

For example, some clients may add a `thinking_budget` field not accepted by the relay, causing parameter validation errors. For such issues, first reproduce with the minimal curl in Section 7, then reduce client advanced parameters one by one.

### 12.5 Configuration Limits Are Not Service Guarantees

The following in the example:

~~~json
{
  "limit": {
    "context": 200000,
    "output": 8192
  }
}
~~~

only tells OpenCode how to estimate context and output budgets. It cannot expand the model's actual capability, account quota, or relay limits. It also cannot guarantee that all models support the same tools, images, or thinking capabilities.

**Next step:** If requests fail, troubleshoot layer by layer from network, authentication, protocol, model, and provider per Section 13.

---

## 13. Common Errors and Troubleshooting Order

### 13.1 Identify Which Layer the Error Belongs To

Recommended troubleshooting order:

~~~text
Network connection
  ↓
Authentication header and API Key
  ↓
Endpoint and request protocol
  ↓
Model ID and protocol routing
  ↓
OpenCode provider runtime
  ↓
Advanced parameters, tools, or streaming capabilities
~~~

### 13.2 Error Reference Table

| Symptom | Common cause | Resolution |
|---|---|---|
| `Could not resolve host`, connection timeout | DNS, network, proxy, or VPN | Access the Base URL first; check corporate network and VPN — this is not a model routing conclusion |
| HTTP `401` or `403` | API Key is wrong, expired, or lacks permissions | Regenerate the Key; confirm the current Terminal is using the same Key; do not share the Key |
| `No upstream candidates` | Model ID does not exist, protocol mismatch, or account lacks upstream permissions | Re-run `/models` for the corresponding protocol; verify provider and exact ID |
| `model_not_found` | ID spelling error or dot/hyphen error | Copy the complete ID from the live directory; Claude uses `4.8`, `4.6` — do not change to `4-8`, `4-6` |
| HTTP `502`, `503`, or `upstream failed` | Temporary upstream failure, no gateway candidates, or model not routed | First retry with another known-working model; provide error time and request ID to the relay |
| OpenAI Chat success, Responses failure | The two endpoints have different upstream routing | Do not treat the Chat provider as a Responses provider in OpenCode; validate and configure separately |
| Anthropic success, OpenAI failure | The model only has or was only validated for an Anthropic route | Use `my-relay-anthropic`; do not use `my-relay` before Chat is validated |
| Configuration reports `expected object, received string` | Provider was written as a string or formats were mixed | Check that `provider` is an object; OpenCode `1.18.18` uses singular `provider` |
| Model appears in OpenCode list but call fails | List is only registration info, or provider/runtime mismatch | Run the standard curl first, then do a minimal OpenCode call with the same provider |
| HTTP 200 but no final text visible | Output budget too small, only a thinking block returned, or wrong parsing field | First raise to `1024`, if necessary raise to `4096`; if still no final text, do not mark as usable |
| `database is locked` | Multiple OpenCode processes accessing the local state database simultaneously | Wait for the running OpenCode command to finish, then retry serially — this is not a gateway or model error |

### 13.3 How to Diagnose `No upstream candidates`

Run in this order:

~~~bash
opencode models my-relay
opencode models my-relay-anthropic
~~~

Then test the same model using the requests from Section 7:

~~~text
OpenAI model → /chat/completions + Bearer
Claude model → /messages + x-api-key + anthropic-version
~~~

If the correct model ID under the correct protocol still fails, only then should you ask the relay to check upstream candidates, account permissions, and routing configuration. Do not try to "guess" by repeatedly changing provider names or adding suffixes to model IDs.

### 13.4 How to Distinguish VPN Issues from Model Issues

~~~text
Cannot connect to domain / TLS timeout
    → Network, proxy, firewall, or VPN

HTTP 401 / 403
    → API Key or permissions

HTTP 400 No upstream candidates
    → Model, protocol, or upstream routing

HTTP 502 upstream failed
    → Temporary upstream failure or model not routed

HTTP 200 with text
    → Minimal call succeeded for this protocol, model, and API Key
~~~

**Next step:** After identifying the problem layer, read Section 14 for usage boundaries and information needed for submitting issues.

---

## 14. How to Determine Product Support Scope

Whether a model can be used in OpenCode depends not only on the model name, but also on API Key permissions, request protocol, provider configuration, and upstream routing. When encountering different models, you can determine usability using the following approach:

### 14.1 What Each Result Means

| Result seen | What it means | Next step |
|---|---|---|
| Model not in `/models` | Current API Key or protocol view does not provide that model | Check authentication header, permissions, and model ID; do not force-add to configuration |
| Model in `/models` | Current API Key can see that model ID | Continue running the curl for the corresponding protocol |
| curl returns HTTP 200 with final text | That model can make a minimal text call under this protocol | Use the OpenCode provider corresponding to the same protocol |
| curl succeeds but OpenCode fails | Client provider, SDK parameters, or model registration method mismatch | Check the provider and request parameters per Section 12 |

### 14.2 Boundaries to Observe When Using the Product

1. The Base URL must use the address provided by the relay, and confirm whether `/v1` is already included;
2. OpenAI and Anthropic authentication headers are different and cannot be mixed;
3. `my-relay` represents OpenAI Compatible Chat, `my-relay-responses` represents OpenAI Responses, `my-relay-anthropic` represents Anthropic Messages;
4. For this guide's example gateway, Claude preferably uses Anthropic Messages; `anthropic/` in the model ID does not automatically switch the protocol;
5. Responses must be configured with an independent provider per Section 8.4; the Chat provider cannot be used as the Responses provider;
6. A model succeeding under one protocol does not mean it succeeds under other protocols;
7. A successful minimal text call does not mean tool calling, streaming, multimodal input, structured output, caching, long context, or thinking parameters are all supported;
8. Model names, version numbers, and punctuation must exactly match the values returned by `/models`.

### 14.3 What to Provide When Submitting an Issue

If you still fail after following this guide, an API Key is not needed. Provide the following sanitized information:

- OpenCode version: `opencode --version`;
- Provider ID used: for example `my-relay` or `my-relay-anthropic`;
- Model ID;
- Protocol used: OpenAI Chat, Responses, or Anthropic Messages;
- HTTP status code;
- Request time and request ID;
- Sanitized error summary;
- Whether `opencode debug config` passed.

Do not paste the complete `opencode run --format json` error output directly. In addition to the full `Authorization`, `x-api-key`, Cookie, request body, and real tokens, also delete or replace the following:

- `virtualApiKeyAlias`, `tenantId`, and other tenant information;
- Upstream vendor name, upstream Base URL, and account alias;
- `endpoint_id`, internal routing numbers, and complete retry history;
- The complete `responseBody`, which may again contain the above information nested within it.

The request ID can usually be kept to allow support staff to query server-side logs. Support staff will assess the network, permissions, or upstream routing issue based on version, time, model, protocol, HTTP status, and request ID.

**Next step:** Complete the security check in Section 15, then verify each item in the checklist in Section 16.

---

## 15. Security and Day-to-Day Operations

### 15.1 API Key Security

- Do not write the Key into `opencode.json`;
- Do not write the Key in command arguments, chat logs, tickets, screenshots, or Git;
- Do not run `env`, `set`, or `echo "$CLICKZETTA_API_KEY"` during troubleshooting;
- Before sharing logs, remove `Authorization`, `x-api-key`, Cookie, tenant information, upstream addresses, internal endpoint numbers, complete retry history, and sensitive fields in the request body;
- Do not share the complete `opencode run --format json` error event directly; first organize it into a sanitized summary per Section 14.3;
- If you suspect a leak, immediately revoke and regenerate the Key in the relay console.

**Next step:** Complete the final success checklist in Section 16.

### 15.2 Configuration Backup and Recovery

Back up before modifying:

~~~bash
cp -p "$HOME/.config/opencode/opencode.json" \
  "$HOME/.config/opencode/opencode.json.$(date +%Y%m%d-%H%M%S).bak"
~~~

When recovering, confirm the target file path before overwriting the current configuration. After recovery, you must re-run:

~~~bash
jq empty "$HOME/.config/opencode/opencode.json"
opencode debug config
~~~

### 15.3 When to Re-Validate

After any of the following, you should re-run the `/models`, curl, and OpenCode minimal text tests:

- The relay changes its Base URL or gateway version;
- API Key permissions, subscription plan, or upstream account changes;
- Model version number or model ID changes;
- OpenCode or AI SDK runtime upgrades;
- Persistent `502`, `No upstream candidates`, or abnormal output format.

---

## 16. Final Checklist

Verify each item:

- [ ] `opencode --version` returns a version number;
- [ ] `CLICKZETTA_API_KEY` is loaded but not written into the configuration file;
- [ ] `RELAY_BASE_URL` contains only one `/v1`;
- [ ] You have queried your own OpenAI and Anthropic `/models` without blindly copying example models from this guide;
- [ ] The OpenAI `/models` view has been confirmed with your API Key for OpenAI/DeepSeek/Qwen;
- [ ] The Anthropic `/models` view has been confirmed with your API Key for the Qwen, DeepSeek, and Claude permission scope;
- [ ] `my-relay` uses `@ai-sdk/openai-compatible`;
- [ ] If using Responses, `my-relay-responses` uses `@ai-sdk/openai`;
- [ ] `my-relay-anthropic` uses `@ai-sdk/anthropic`;
- [ ] `jq empty` passes;
- [ ] `opencode debug config` passes;
- [ ] Each configured provider can list models via `opencode models <provider-id>`;
- [ ] The first actual call used an isolated temporary directory and was not tested directly in a production project directory;
- [ ] At least one OpenAI Chat model in your own directory has made a successful actual call;
- [ ] If using Responses, at least one Responses model has made a successful actual call through `my-relay-responses`;
- [ ] If your API Key has Claude permissions, at least one Claude model has made a successful actual call through `my-relay-anthropic`;
- [ ] Each model you plan to use exists in your corresponding protocol directory and has completed a minimal text request;
- [ ] Claude uses dot-notation version IDs, not hyphen-notation version IDs;
- [ ] You have not mistaken the OpenCode Chat provider for the Responses provider;
- [ ] Minimal text testing succeeded; you have not assumed unverified tool calling, streaming, or multimodal capabilities are supported.

---

## 17. Quick Diagnostic Commands

The following commands will not print the API Key; run them in sequence when troubleshooting:

~~~bash
echo "OpenCode: $(opencode --version)"
echo "Config: $HOME/.config/opencode/opencode.json"
test -n "$CLICKZETTA_API_KEY" && echo 'API Key: loaded' || echo 'API Key: missing'
jq empty "$HOME/.config/opencode/opencode.json" && echo 'JSON: valid'
opencode debug config >/dev/null && echo 'OpenCode config: valid'
opencode models my-relay
opencode models my-relay-anthropic
# Only run if the Responses provider is configured:
# opencode models my-relay-responses
~~~

Minimal actual calls:

The commands below use example models. If your live directory does not have the corresponding IDs, replace them with models in the same protocol that have been verified successfully. Do not change the provider runtime just because the model ID differs. The third command should only be run if you have configured and verified the Responses provider.

~~~bash
if [ -z "${TEST_DIR:-}" ]; then
  TEST_DIR="$(mktemp -d "${TMPDIR:-/tmp}/opencode-gateway-test.XXXXXX")"
fi
printf 'Test directory: %s\n' "$TEST_DIR"

opencode run --dir "$TEST_DIR" --model my-relay/openai/gpt-5.5 --format json 'Reply only: OK'
opencode run --dir "$TEST_DIR" --model my-relay-anthropic/anthropic/claude-opus-5 --format json 'Reply only: OK'
# opencode run --dir "$TEST_DIR" --model my-relay-responses/openai/gpt-5.5 --format json 'Reply only: OK'
~~~

If all configured models return actual text, OpenCode has connected to the relay through the corresponding protocols. Other models should still follow the vendor and protocol rules in Section 11 to select the provider.

---

## 18. Conclusion

The core of connecting OpenCode to a relay is not simply "filling in the Base URL," but satisfying all of the following relationships simultaneously:

~~~text
Model ID
  + Provider ID
  + AI SDK runtime
  + Request endpoint
  + Authentication header
  + Upstream protocol routing
  = Actually usable call
~~~

Three rules to remember when configuring:

~~~text
OpenAI, DeepSeek, Qwen (Chat)
  → my-relay/<model-id>

OpenAI Responses
  → my-relay-responses/<model-id>

Claude, and Qwen/DeepSeek called via Anthropic method
  → my-relay-anthropic/<model-id>
~~~

Claude generally uses Anthropic Messages. For OpenAI series, use the corresponding runtime when using Chat or Responses. DeepSeek, Qwen, and other vendor models need to select the provider based on your directory and protocol test results. Any new model or new protocol should go through the three-layer check of `/models`, standard curl, and OpenCode actual call before being put into use.

---

## 19. Related Resources

- [OpenCode Providers Official Documentation](https://opencode.ai/docs/providers): Custom OpenAI Compatible provider, Anthropic provider, `baseURL`, and model configuration.
- [OpenCode Config Official Documentation](https://opencode.ai/docs/config): Configuration file, default model, and provider configuration options.
- [OpenCode Official Download Page](https://opencode.ai/download): Install script, npm, Homebrew, and other installation methods.
