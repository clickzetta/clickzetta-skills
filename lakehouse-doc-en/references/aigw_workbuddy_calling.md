This guide is intended for users who are configuring WorkBuddy for the first time, setting up a custom model for the first time, or need to use third-party models through AI Gateway.

After completing this guide, you will be able to:

- Install and launch WorkBuddy;
- Securely enter the AI Gateway Base URL and API Key;
- Query the models visible to your API Key;
- Determine whether a model has the OpenAI Chat Completions route required by WorkBuddy;
- Add and select custom models in the WorkBuddy GUI;
- Confirm connectivity using standard `curl` and actual WorkBuddy messages;
- Understand the applicable boundaries of Claude, multi-protocol models, and the "Custom Protocol" toggle;
- Troubleshoot network, authentication, model routing, or local configuration issues based on error messages.

This guide uses macOS and WorkBuddy 5.3.14 as examples. Example AI Gateway Base URL:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1>
~~~

The standard OpenAI configuration path in this guide has been verified against WorkBuddy 5.3.14. A different version number does not necessarily cause issues; if button names, configuration paths, or CLI parameters differ, prefer using the WorkBuddy GUI and refer to the official resources in Section 18.

If your AI Gateway address is different, you only need to replace the Base URL. Do not share your real API Key in chat, tickets, screenshots, Git repositories, or public web pages.

The Model Catalog is determined jointly by AI Gateway and the permissions of your API Key, and may change with tenant permissions, routing configuration, and upstream status. This guide does not specify a fixed number of models, nor does it treat example models as a complete catalog; always use your own API Key's real-time query results when configuring.

---

## Summary First: Model Vendor and Request Protocol Are Two Different Things

Whether a given model name can be used depends on three conditions: whether the model is visible to the API Key, whether AI Gateway provides a route for that protocol, and whether WorkBuddy can send and parse that protocol. The vendor prefix in a model name does not automatically switch the protocol.

| Model or Vendor Type | Common Protocol | WorkBuddy Custom Model Handling |
|---|---|---|
| OpenAI model series | OpenAI Chat Completions; some services also provide OpenAI Responses | Use Base URL up to `/v1`, disable Custom Protocol, WorkBuddy requests `/chat/completions` |
| Anthropic Claude series | Anthropic Messages, typically using `/messages`, `x-api-key`, and `anthropic-version` | Current WorkBuddy custom models cannot directly switch to Anthropic Messages; cannot be resolved by changing only the model ID or URL |
| DeepSeek, Qwen, and other multi-protocol models | Determined by AI Gateway routing; may appear in both OpenAI and Anthropic catalogs | WorkBuddy still uses only OpenAI Chat; query the OpenAI catalog and verify with `/chat/completions` |
| Gemini, Grok, Mistral, Meta, and similar series | Based on the compatible protocol actually provided by AI Gateway | Can only be configured following this guide when the OpenAI Chat request and response format matches WorkBuddy |
| GLM, Kimi, MiniMax, and others | May be built-in models in WorkBuddy, or provided by AI Gateway as custom models | When configuring via AI Gateway, you must still query the OpenAI catalog and test `/chat/completions`; built-in models are not configured using this guide |

Think of "visible in Model Catalog", "protocol request successful", and "WorkBuddy used successfully" as three separate outcomes: the catalog is for finding the model ID, the protocol request is for confirming gateway routing, and the actual WorkBuddy conversation is for final acceptance. The steps in this guide follow this order.

The most important rules are:

~~~text
Model vendor
    ≠ Request protocol

Model appears in catalog
    ≠ Model is ready to call

Standard curl succeeds
    ≠ WorkBuddy is fully configured
~~~

WorkBuddy custom models use OpenAI Chat Completions for the underlying connection. Even if a model also supports OpenAI Responses or Anthropic Messages, WorkBuddy will not automatically switch protocols based on the model name.

---

## 0. Complete Operation Sequence

For first-time configuration, follow these steps in order:

~~~text
1. Install or confirm WorkBuddy
2. Prepare Base URL and API Key
3. Query the OpenAI Model Catalog for your API Key
4. Copy a target model ID exactly from the catalog
5. Use OpenAI Chat curl to get the final text output
6. Add this model in WorkBuddy settings
7. Select the model in WorkBuddy and send a real message
8. Add more models or use CLI for troubleshooting as needed
~~~

### 0.1 First-Time Use: Complete Only These Five Checkpoints

If your goal is to complete your first conversation as quickly as possible, you do not need to read the entire guide first. Follow the table below in order; only proceed to the next item after the current one succeeds.

| Checkpoint | Where to Operate | What to Do | Expected Output | Next Step |
|---|---|---|---|---|
| 1. Confirm client | macOS Terminal | Check WorkBuddy per Section 2.1 | Returns app name and version number | Proceed to Section 4.1 |
| 2. Get model ID | macOS Terminal | Enter API Key and query OpenAI `/models` per Sections 4.1, 4.2 | HTTP 200, model IDs displayed one per line | Copy a target model ID exactly |
| 3. Verify model | Same Terminal | Request `/chat/completions` per Section 5.2 | HTTP 200, shows `WorkBuddy connection successful` | Go to WorkBuddy settings |
| 4. Save model | WorkBuddy GUI | Fill in Base URL, API Key, and model ID per Section 6.2 | Custom model appears in model list | Select the newly saved model |
| 5. Final acceptance | WorkBuddy conversation or task page | Send a minimal test message per Section 7.3 | Page returns `WorkBuddy connection successful` | Basic text conversation is configured |

For first-time configuration, use only these settings:

| Field | Value for First-Time Configuration |
|---|---|
| Base URL | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1` |
| API Key | Your own AI Gateway API Key |
| Model ID | Copied exactly from OpenAI `/models` results |
| Custom Protocol / Use Custom Protocol | Off |
| Tool Calls | Off |
| Image Input | Off |
| Reasoning Mode | Off |

Do not fill in `/messages`, enable "Custom Protocol", or test tool calls and images simultaneously during first-time configuration. Get basic text conversation working first, then confirm other protocols and advanced capabilities per Sections 11 and 12.

If any checkpoint fails, stop at the current checkpoint and refer to Section 13 based on the HTTP status code returned. Repeatedly reinstalling WorkBuddy typically cannot resolve issues with API Key, model ID, protocol, or upstream routing.

True success requires all of the following simultaneously:

1. The OpenAI protocol Model Catalog shows the target model;
2. Standard `/chat/completions` curl returns HTTP 200;
3. The curl response contains actual final text;
4. WorkBuddy returns actual text after selecting that custom model.

Seeing only the model name, saving only the configuration, or seeing only the custom model option does not directly indicate the model is usable. After completing Step 7, you have basic text conversation capability; the scope of tool calls, image input, reasoning mode, and other advanced capabilities is covered in Section 12.

---

## 1. Prepare Information

### 1.1 Base URL

The Base URL is the root address of the AI Gateway interface. This example uses:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1>
~~~

This address already includes `/v1`. Do not write it as:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/v1>
~~~

WorkBuddy's standard OpenAI mode automatically appends `/chat/completions` after the Base URL, making the final request address:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/chat/completions>
~~~

### 1.2 API Key

Create an API Key in the AI Gateway backend and confirm:

- The API Key has not expired;
- The API Key has model invocation permissions;
- The API Key and Base URL belong to the same environment;
- No extra spaces or newlines were included when copying;
- It is not shared with other users, projects, or production environments.

This guide uses the term "API Key" throughout. Even if a certain interface still displays "Token", enter the API Key provided by AI Gateway into the corresponding secret input field.

### 1.3 Model ID

The model ID is the complete string AI Gateway uses to identify a model. The common format is:

~~~text
vendor-name/model-name
~~~

This guide uses `YOUR_MODEL_ID` as a placeholder for the model you want to configure. It is a placeholder and cannot be submitted directly; you must replace it with the full model ID returned by your OpenAI catalog in actual use.

The model ID must be copied exactly from the live catalog. The following two example formats are not the same model:

~~~text
vendor-name/model-name-4.6
vendor-name/model-name-4-6
~~~

### 1.4 Where to Operate

This guide involves two types of operation locations:

| Operation | Where to Complete |
|---|---|
| Check installation, query models, curl tests, CLI tests | macOS Terminal |
| Add models, select models, send messages | WorkBuddy GUI |

Open Terminal: press `Command + Space`, type `Terminal`, press Enter.

The terminal prompt may look like:

~~~text
user@Mac ~ %
~~~

Do not copy the prompt itself; only copy the commands in the code blocks.

---

## 2. Confirm WorkBuddy Is Installed

### 2.1 Check Application and Version

Run in Terminal:

~~~bash
if [ -d "/Applications/WorkBuddy.app" ]; then
  defaults read "/Applications/WorkBuddy.app/Contents/Info" CFBundleDisplayName
  defaults read "/Applications/WorkBuddy.app/Contents/Info" CFBundleShortVersionString
else
  echo "WorkBuddy.app not found in /Applications"
fi
~~~

Under normal circumstances, this returns the application name and installed version, for example:

~~~text
WorkBuddy
5.3.14
~~~

If "not found" is displayed, first download and install WorkBuddy from the official website, then re-run the commands in this section.

WorkBuddy officially requires macOS 12 or later. Before downloading the installer, run in Terminal:

~~~bash
uname -m
~~~

Choose the installer based on the return value:

| Return Value | Download Version |
|---|---|
| `arm64` | Mac ARM64, for Apple Silicon |
| `x86_64` | Mac X64, for Intel chips |

Official installation guide:

~~~text
<https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Installation-Mac-Guide>
~~~

After downloading the `.dmg`, double-click to open it, drag the WorkBuddy icon into the `Applications` folder, then re-run the check commands in this section.

### 2.2 Launch WorkBuddy

You can double-click the application icon, or run in Terminal:

~~~bash
open -a "/Applications/WorkBuddy.app"
~~~

After WorkBuddy opens normally, if the interface requires login, complete the login process following the on-screen prompts.

### 2.3 Optional: Check the Built-in CLI

WorkBuddy ships with a built-in `codebuddy` CLI, but it may not be automatically added to PATH after installation. Run in Terminal:

~~~bash
WORKBUDDY_CLI="/Applications/WorkBuddy.app/Contents/Resources/app.asar.unpacked/cli/bin/codebuddy"

if [ -x "$WORKBUDDY_CLI" ]; then
  "$WORKBUDDY_CLI" --version
else
  echo "Built-in CLI not found in this version; you can continue using the GUI"
fi
~~~

A returned version number means the CLI is available. The CLI is not a prerequisite for completing GUI configuration; if the CLI is not found, you can still proceed to Section 3.

### 2.4 Whether VPN Is Needed

Whether VPN is needed depends on your network. Complete Section 4.1 first, then run the catalog query in Section 4.2: if you receive an HTTP response, the request has reached the server; HTTP 200 with a returned model ID means VPN is not needed.

If you encounter connection timeouts, DNS resolution failures, or TLS connection failures, check the following in order:

1. Whether your browser can access the internet;
2. Whether the corporate network restricts external HTTPS;
3. DNS, system proxy, or firewall settings;
4. Whether your organization requires a specific VPN or proxy.

VPN should only be considered when there is a network connection failure; HTTP 400, 401, 403, 429, or 502 all indicate the request reached the server and are not VPN issues.

**Next step:** Understand WorkBuddy's protocol limitations before adding models.

---

## 3. Limitations You Must Understand Before Configuration

### 3.1 WorkBuddy Custom Models Use OpenAI Chat Completions

WorkBuddy's current custom models send requests in OpenAI Chat Completions format:

~~~text
POST /chat/completions
Authorization: Bearer API_KEY
Content-Type: application/json
~~~

The request body primarily uses:

~~~json
{
  "model": "YOUR_MODEL_ID",
  "messages": [
    {
      "role": "user",
      "content": "Hello"
    }
  ]
}
~~~

The final response text is typically found at:

~~~text
choices[0].message.content
~~~

### 3.2 "Custom Protocol" Does Not Mean Anthropic Protocol

The "Custom Protocol / Use Custom Protocol" setting in WorkBuddy only controls how the URL is handled:

| Setting | WorkBuddy Behavior |
|---|---|
| Off (default) | Uses standard `/chat/completions`, automatically validates and completes the path |
| On | Directly requests the full URL you entered, skipping path validation and auto-completion |

This toggle does not switch the request format from OpenAI to Anthropic, and does not automatically add:

~~~text
x-api-key: API_KEY
anthropic-version: 2023-06-01
~~~

Therefore, even with "Custom Protocol" enabled, WorkBuddy still cannot directly call Claude interfaces that only accept the Anthropic `/messages` format.

### 3.3 Model Name Does Not Automatically Switch Protocol

The `anthropic/` in a model ID is just part of the string. Entering a model ID with this prefix into WorkBuddy does not cause WorkBuddy to automatically use Anthropic Messages.

Both of the following must be true for a model to work in WorkBuddy:

1. The model can be called via OpenAI `/chat/completions`;
2. WorkBuddy sends requests in OpenAI format.

If a Claude model appears only in the Anthropic `/models` catalog and not in the OpenAI `/models` catalog, it cannot be directly added to the current WorkBuddy custom models.

### 3.4 WorkBuddy Does Not Automatically Import the Entire Live Model Catalog

WorkBuddy's custom model list comes from locally saved configurations, not an automatic mirror of AI Gateway `/models`.

For example, AI Gateway's OpenAI catalog may return multiple models, but if WorkBuddy has only one custom model saved, the dropdown typically shows only that one custom model.

To show more models, you need to add them one by one in WorkBuddy, or maintain multiple models through the correct local configuration file.

### 3.5 Built-in Models and Custom Models Are Different Sources

WorkBuddy's built-in models such as Hy, GLM, Kimi, and DeepSeek are provided by the WorkBuddy product side; models added through AI Gateway are "custom models".

Success with a built-in model does not indicate AI Gateway is configured correctly; failure with a custom model does not indicate a WorkBuddy built-in service failure.

**Next step:** Query the models that AI Gateway provides in real time under the OpenAI protocol.

---

## 4. Retrieve the Live Model Catalog

### 4.1 Securely Enter Connection Information in the Current Terminal

The commands in this section use `jq` to parse JSON. First check if it is installed:

~~~bash
if command -v jq >/dev/null 2>&1; then
  jq --version
elif command -v brew >/dev/null 2>&1; then
  echo "jq not found; run: brew install jq"
else
  echo "jq and Homebrew not found; visit https://brew.sh/ to install Homebrew first"
fi
~~~

If the output shows "jq not found" and Homebrew is installed, run in Terminal:

~~~bash
brew install jq
~~~

After installation, re-run the check above. A Homebrew download failure is a local network or software source issue and does not indicate AI Gateway or model unavailability; switch networks if needed, use your organization's approved VPN/proxy if necessary, then retry the installation.

Run in Terminal:

~~~bash
export WORKBUDDY_BASE_URL='https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1'
WORKBUDDY_BASE_URL="${WORKBUDDY_BASE_URL%/}"

read -s "WORKBUDDY_API_KEY?Paste your AI Gateway API Key and press Enter: "
echo
~~~

It is normal for no characters to appear during input. Paste the API Key and press Enter.

Only check whether the variable exists, without displaying the API Key:

~~~bash
if [ -n "$WORKBUDDY_API_KEY" ]; then
  echo 'API Key loaded into current Terminal'
else
  echo 'API Key is empty, please re-enter'
fi
~~~

Expected output:

~~~text
API Key loaded into current Terminal
~~~

Do not run:

~~~bash
echo "$WORKBUDDY_API_KEY"
~~~

### 4.2 Query the OpenAI Catalog

WorkBuddy uses OpenAI Chat Completions, so this is the catalog you must query. Run in the same Terminal:

~~~bash
curl -sS -o /tmp/workbuddy-models-openai.json \
  --max-time 30 \
  -w 'HTTP %{http_code}\n' \
  "$WORKBUDDY_BASE_URL/models" \
  -H "Authorization: Bearer $WORKBUDDY_API_KEY"
~~~

Return value meanings:

| Return | Meaning | Next Step |
|---|---|---|
| HTTP 200 | Network and Bearer authentication are working | Continue to read the model catalog |
| HTTP 401 | API Key is missing, incorrect, or expired | Re-enter the API Key |
| HTTP 403 | API Key rejected or insufficient permissions | Check account, tenant, and model permissions |
| HTTP 404 | Base URL or `/v1` path is incorrect | Check the address, avoid duplicate `/v1` |
| HTTP 429 | Quota, concurrency, or rate limit | Wait and retry, or check quota |
| HTTP 5xx | AI Gateway or upstream temporary failure | Retry later and save desensitized error |
| HTTP 000, DNS, or connection timeout | Request did not reach AI Gateway normally | Check network, proxy, firewall, or VPN |

After HTTP 200, run:

~~~bash
jq -r '
  if (.data | type) == "array" then
    .data[].id
  else
    .error.message // .message // "Model catalog could not be read"
  end
' /tmp/workbuddy-models-openai.json
~~~

If not HTTP 200, view desensitized error content:

~~~bash
jq '
  if .error then
    {error: .error}
  else
    {message: .message, code: .code}
  end
' /tmp/workbuddy-models-openai.json
~~~

Under normal circumstances, one model ID is displayed per line, for example:

~~~text
vendor-name/model-name
~~~

The actual count and names are determined by the current API Key. Copy the model ID you want to use exactly as shown in the results — do not remove the vendor prefix or modify dots, hyphens, or version numbers. A successful catalog response only means the model ID is visible to the current API Key; you still need to verify actual invocation in Section 5.

If you already received 200, 401, 403, 404, 429, or 5xx, the domain is accessible and this is typically not a VPN issue. VPN is only needed when DNS resolution fails, connection times out, or a network policy blocks the request.


### 4.3 Only When Troubleshooting Claude or Multi-Protocol Models: Query the Anthropic Catalog

This step is not required for WorkBuddy configuration. Skip this section for first-time configuration, if you are only using OpenAI Chat models, or if Section 5.2 has already succeeded. Only use this section to check which models the Anthropic client can see, and why the list may differ from WorkBuddy's list, when troubleshooting Claude or models that support multiple protocols.

Run in the same Terminal:

~~~bash
curl -sS -o /tmp/workbuddy-models-anthropic.json \
  --max-time 30 \
  -w 'HTTP %{http_code}\n' \
  "$WORKBUDDY_BASE_URL/models" \
  -H "x-api-key: $WORKBUDDY_API_KEY" \
  -H 'anthropic-version: 2023-06-01'
~~~

After HTTP 200, run:

~~~bash
jq -r '
  if (.data | type) == "array" then
    .data[].id
  else
    .error.message // .message // "Anthropic model catalog could not be read"
  end
' /tmp/workbuddy-models-anthropic.json
~~~

If Claude, DeepSeek, Qwen, or other models are returned, it only means these models are visible in the Anthropic protocol view. Whether they can also be used in WorkBuddy still requires going back to the OpenAI catalog in Section 4.2 and testing with OpenAI Chat Completions.

> **Do not use directly in WorkBuddy:** Models returned by Anthropic `/models`, or even a successful subsequent `/messages` call, cannot substitute for a successful OpenAI `/chat/completions` required by WorkBuddy.

### 4.4 Why the Same `/models` Returns Different Lists

AI Gateway returns different models based on authentication headers and protocol views:

~~~text
Authorization: Bearer API_KEY
    → OpenAI view
    → WorkBuddy uses this view

x-api-key: API_KEY
anthropic-version: 2023-06-01
    → Anthropic view
    → Clients supporting Anthropic Messages use this view
~~~

Therefore, the same `/models` address may return different lists. This is not missing data in the catalog — the authentication header selects a different protocol view. A model may appear in only one view, or in both; do not merge the two lists and add all of them to WorkBuddy.

### 4.5 Continue Using the Current Terminal

Section 5 will also use `WORKBUDDY_BASE_URL` and `WORKBUDDY_API_KEY`. Do not close the current Terminal or clear the variables. Clean up after completing Section 5.

**Next step:** Copy the target model ID from the OpenAI catalog, then verify actual invocation with standard curl.

---

## 5. Verify the Target Model with Standard curl

### 5.1 Why curl Must Come First

curl separates problems into two categories:

~~~text
curl fails
    → Check AI Gateway, API Key, model, protocol, or upstream first

curl succeeds, WorkBuddy fails
    → Check WorkBuddy URL, model ID, local configuration, and response parsing first
~~~

If curl fails, do not start by repeatedly deleting and reinstalling WorkBuddy.

### 5.2 Test OpenAI Chat Completions

If you have already cleared the Terminal variables, re-run Section 4.1 — do not re-enter only the API Key while omitting the Base URL.

First enter the model ID you want to configure:

~~~bash
read "WORKBUDDY_MODEL_ID?Enter the model ID from the OpenAI catalog: "
~~~

The model ID must come from the OpenAI catalog in Section 4.2. Then run:

~~~bash
curl -sS -o /tmp/workbuddy-test-chat.json \
  --max-time 60 \
  -w 'HTTP %{http_code}\n' \
  "$WORKBUDDY_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $WORKBUDDY_API_KEY" \
  -H 'Content-Type: application/json' \
  -d "$(jq -cn \
    --arg model "$WORKBUDDY_MODEL_ID" \
    '{
      model: $model,
      messages: [{role: "user", content: "Reply only with: WorkBuddy connection successful"}],
      max_tokens: 512,
      stream: false
    }')"
~~~

Extract the final text or error message:

~~~bash
jq -r '
  .choices[0].message.content
  // .error.message
  // .message
  // "HTTP returned, but no final text found"
' /tmp/workbuddy-test-chat.json
~~~

On success you should see:

~~~text
HTTP 200
WorkBuddy connection successful
~~~

Only when both HTTP 200 and the final text appear together can you continue configuring WorkBuddy. If HTTP 200 appears but there is no final text, follow Section 5.6.

### 5.3 Relationship Between Vendor, Model, and Protocol

AI Gateway can provide different protocol endpoints for models from different vendors. The vendor name indicates the model's origin; the protocol determines the request and response format — they are not the same thing.

| Model or Vendor Type | Protocols AI Gateway May Provide | How to Determine for WorkBuddy |
|---|---|---|
| OpenAI series | OpenAI Chat Completions; may also provide OpenAI Responses | Must appear in OpenAI catalog and pass `/chat/completions`; Responses success cannot substitute for Chat success |
| Anthropic Claude series | Usually uses Anthropic Messages; AI Gateway may also provide a separate OpenAI-compatible mapping | Can only be used when the mapped model ID appears in the OpenAI catalog and passes `/chat/completions`; not directly addable if visible only in the Anthropic catalog |
| DeepSeek series | May provide OpenAI Chat; may also provide an Anthropic-compatible endpoint | WorkBuddy uses only OpenAI Chat, so go by the OpenAI catalog and `/chat/completions` results |
| Qwen series | May provide OpenAI Chat; may also provide an Anthropic-compatible endpoint | WorkBuddy uses only OpenAI Chat, so go by the OpenAI catalog and `/chat/completions` results |
| Gemini, Grok, Mistral, Meta, and similar | Determined by AI Gateway's protocol adapters and tenant routing | Do not judge by vendor name; must complete the three-step verification: OpenAI catalog, Chat curl, and actual WorkBuddy conversation |
| GLM, Kimi, MiniMax, and others | May be provided by WorkBuddy built-in, or by AI Gateway providing an OpenAI-compatible route | When using a custom model, must complete the three-step verification: OpenAI catalog, Chat curl, and actual WorkBuddy conversation |

"May provide" here means AI Gateway can expose models in different ways, not that every API Key has the same protocols and models. The final result always depends on the live catalog and actual requests.

### 5.4 Which Protocols Does WorkBuddy Use

| Protocol | Common Endpoint | Used by WorkBuddy Custom Models | Notes |
|---|---|---|---|
| OpenAI Chat Completions | `POST /v1/chat/completions` | Yes | The configuration and acceptance protocol for this guide |
| OpenAI Responses | `POST /v1/responses` | No | Even if a model passes Responses, it does not mean WorkBuddy can use it |
| Anthropic Messages | `POST /v1/messages` | No | The current "Custom Protocol" toggle does not switch the request body and response parsing to Anthropic format |

Therefore, when selecting models for WorkBuddy, follow only this decision path:

~~~text
Visible in OpenAI /models
    ↓
OpenAI /chat/completions returns HTTP 200 and final text
    ↓
Add to WorkBuddy
    ↓
WorkBuddy actual conversation succeeds
~~~

### 5.5 Only When Troubleshooting Claude or Multi-Protocol Models: Verify Anthropic Messages

This step is only for confirming AI Gateway's Anthropic routing, not for configuring WorkBuddy. Skip this section for first-time WorkBuddy configuration; only run it when you need to determine whether a Claude, DeepSeek, Qwen, or other model also has an Anthropic Messages route.

First enter the model ID copied exactly from the Anthropic catalog:

~~~bash
read "ANTHROPIC_MODEL_ID?Enter the model ID from the Anthropic catalog: "
~~~

Then run:

~~~bash
curl -sS -o /tmp/workbuddy-test-anthropic.json \
  --max-time 60 \
  -w 'HTTP %{http_code}\n' \
  "$WORKBUDDY_BASE_URL/messages" \
  -H "x-api-key: $WORKBUDDY_API_KEY" \
  -H 'anthropic-version: 2023-06-01' \
  -H 'Content-Type: application/json' \
  -d "$(jq -cn \
    --arg model "$ANTHROPIC_MODEL_ID" \
    '{
      model: $model,
      max_tokens: 512,
      messages: [{role: "user", content: "Reply only with: Anthropic connection successful"}]
    }')"
~~~

Extract the final text or error message:

~~~bash
jq -r '
  ([.content[]? | select(.type == "text") | .text] | join("\n")) as $text
  | if ($text | length) > 0 then
      $text
    else
      .error.message // .message // "HTTP returned, but no final text found"
    end
' /tmp/workbuddy-test-anthropic.json
~~~

On success you should see HTTP 200 and `Anthropic connection successful`.

> **Result boundary:** This result only proves that Anthropic Messages is available; it does not prove that WorkBuddy can use the model. To add to WorkBuddy, the model must still appear in the OpenAI catalog in Section 4.2 and pass the `/chat/completions` test in Section 5.2.

### 5.6 HTTP 200 But No Final Text

Qwen, DeepSeek, or other reasoning models may first output thinking content. When `max_tokens` is too small, the response may have a reasoning field but no final `content`.

For troubleshooting, it is recommended to:

~~~text
First test: max_tokens = 512
Still no final text: increase to 1024
Success criterion: choices[0].message.content contains final text
~~~

### 5.7 Clear Sensitive Variables After Testing

~~~bash
rm -f \
  /tmp/workbuddy-models-openai.json \
  /tmp/workbuddy-models-anthropic.json \
  /tmp/workbuddy-test-chat.json \
  /tmp/workbuddy-test-anthropic.json

unset WORKBUDDY_API_KEY
unset WORKBUDDY_BASE_URL
unset WORKBUDDY_MODEL_ID
unset ANTHROPIC_MODEL_ID
~~~

**Next step:** Confirm at least one target model succeeds with curl before proceeding to the WorkBuddy GUI to save the configuration.

---

## 6. Add a Model in the WorkBuddy GUI

### 6.1 Open Model Settings

In the WorkBuddy GUI:

~~~text
Open WorkBuddy
    ↓
Go to "Settings"
    ↓
Open "Models" or "Model Configuration"
    ↓
Click "Add Model"
    ↓
Select "Custom API" or "Custom"
~~~

Button positions or names may differ slightly across versions, but the core fields are always URL, API Key, and model name / model ID.

After reaching the correct page, you should see fields with the following meanings. Field order may differ; the interface does not need to match exactly:

~~~text
┌──────────────────────────────────────────────┐
│ Add Custom Model                             │
├──────────────────────────────────────────────┤
│ URL / Base URL      [                      ] │
│ API Key             [••••••••••••••••••••] │
│ Model ID / Name     [                      ] │
│ Custom Protocol     [Off]                    │
│ Tool Calls          [Off]                    │
│ Image Input         [Off]                    │
│ Reasoning Mode      [Off]                    │
│                                  [Save/Add]  │
└──────────────────────────────────────────────┘
~~~

If the current page does not have URL, API Key, or Model ID fields, you have not yet reached the "Custom API/Custom" model configuration page — go back and select it again.

### 6.2 First-Time and Regular Use: Standard OpenAI Mode

This is the configuration method verified in this guide and the only method that needs to be followed for first-time configuration.

Fill in:

| Field | Example Value |
|---|---|
| Provider | Custom API / Custom |
| URL or Base URL | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1` |
| API Key | Your own AI Gateway API Key |
| Model ID or Model Name | Copied exactly from the OpenAI catalog in Section 4.2; do not enter the `YOUR_MODEL_ID` placeholder |
| Custom Protocol | Off |
| Tool Calls | Enable only after completing tool call testing with the model and gateway |
| Image Input | Off until verified |
| Reasoning Mode | Off until verified |

Keep tool calls, image input, and reasoning mode all off on the first save. A successful basic text conversation does not automatically mean these advanced capabilities are available; see Section 12 for conditions to enable them.

In standard mode, WorkBuddy automatically requests:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/chat/completions>
~~~

### 6.3 Fallback: When the Interface Explicitly Requires a Full API URL

If Section 6.2 already saves and works normally, skip this section and do not switch to the full URL mode.

Only fill in the full URL when the current WorkBuddy interface explicitly requires a "Full API URL", or when the error log from standard mode clearly shows WorkBuddy did not append `/chat/completions`:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/chat/completions>
~~~

At the same time, enable "Custom Protocol / Use Custom Protocol" so WorkBuddy directly requests this full address.

The "Custom Protocol" here only makes WorkBuddy use the full URL directly; it does not convert the request to Anthropic Messages, nor can it be used with `/messages`. See Section 11 for guidance on Claude and multi-protocol models.

Only one of the two modes can be selected:

| Mode | URL | Custom Protocol |
|---|---|---|
| Recommended standard mode | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1` | Off |
| Fallback full URL mode | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/chat/completions` | On |

Do not configure it as:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/chat/completions/chat/completions>
~~~

### 6.4 Save the Configuration

Click "Save", "Add", or "Confirm". Wait a few seconds after saving.

Normal results:

- Custom model appears in the model list;
- Model name shows the full model ID you just entered;
- You can select it in the conversation model dropdown;
- The API Key input box may show only dots or asterisks.

A successful save only means the local configuration has been written; you still need to perform the actual conversation test in Section 7.

### 6.5 Why Only One Custom Model Appears

WorkBuddy does not automatically import all models from `/models`. If you only added one model, the dropdown shows only that one custom model.

To add more models, run the Section 5.2 curl for each target model from the Section 4.2 OpenAI catalog. Only models that return HTTP 200 and final text should continue to the Section 6 add steps. The number, names, and availability of models in the catalog may vary by API Key, so do not directly copy another user's model list.

**Next step:** Select the custom model in WorkBuddy and send your first message.

---

## 7. Use the Model in WorkBuddy

### 7.1 Open a Project

Some WorkBuddy Agent features require opening a project folder first. If there is no existing project, you can select an empty folder.

If the interface prompts "Please open a folder first" or similar, this is not a model invocation failure.

### 7.2 Select the Custom Model

In the model dropdown of the conversation or task interface, find the "Custom Models" group and select:

~~~text
YOUR_MODEL_ID
~~~

Select the model ID actually saved in Section 6; if the interface literally shows `YOUR_MODEL_ID`, the placeholder was not replaced during configuration — return to Section 6 to fix it.

Do not select a same-named built-in Auto mode as a substitute for testing the custom model.

### 7.3 Send a Minimal Test Message

Enter:

~~~text
Reply only with: WorkBuddy connection successful
~~~

Expected output:

~~~text
WorkBuddy connection successful
~~~

### 7.4 How to Determine Success

Success requires all of the following simultaneously:

1. The currently selected model is indeed the custom model;
2. WorkBuddy has not automatically fallen back to a built-in model;
3. The interface returns actual text;
4. No 400, 401, 502, or model-not-found errors are displayed.

If you get a 502 on the first try, do a short retry 2 to 3 times; if it succeeds afterward, record it as "intermittent" rather than "stable success".

**Next step:** Use the WorkBuddy CLI in Section 8 when further eliminating interface-side factors is needed.

---

## 8. Optional: Further Verification with WorkBuddy CLI

### 8.1 CLI Uses the Same Custom Model Configuration

WorkBuddy CLI can directly select the custom model saved in the GUI. Custom model IDs need the `custom-local:` prefix in the CLI.

GUI model ID:

~~~text
YOUR_MODEL_ID
~~~

CLI model ID:

~~~text
custom-local:YOUR_MODEL_ID
~~~

`custom-local:` is WorkBuddy's local selector prefix, not the AI Gateway model ID. The request body WorkBuddy sends to AI Gateway still uses your original saved model ID.

### 8.2 Check Whether CLI Recognizes the Model

Run in Terminal:

~~~bash
WORKBUDDY_CLI="/Applications/WorkBuddy.app/Contents/Resources/app.asar.unpacked/cli/bin/codebuddy"

"$WORKBUDDY_CLI" --help | sed -n '/--model/,+1p'
~~~

If the output contains an entry similar to the following, the CLI has recognized the custom model:

~~~text
custom-local:YOUR_MODEL_ID
~~~

Some versions may have cached `--help` output. If it does not appear, do not conclude the configuration failed based on this alone — proceed to Section 8.3; only return to Section 6 to check save status and reload WorkBuddy per Section 9.8 if an actual request reports the model does not exist.

### 8.3 Send a Minimal CLI Request

First enter the full model ID already saved in the GUI:

~~~bash
read "WORKBUDDY_MODEL_ID?Enter the saved custom model ID: "
~~~

Then run in the same Terminal:

~~~bash
WORKBUDDY_CLI="/Applications/WorkBuddy.app/Contents/Resources/app.asar.unpacked/cli/bin/codebuddy"

"$WORKBUDDY_CLI" \
  -p 'Reply only with: WorkBuddy connection successful' \
  --model "custom-local:$WORKBUDDY_MODEL_ID" \
  --tools '' \
  --output-format text \
  --max-turns 1 \
  --no-session-persistence
~~~

Parameter meanings:

| Parameter | Purpose |
|---|---|
| `-p` | Execute one request non-interactively and print the result |
| `--model` | Select the local custom model |
| `--tools ''` | Disable tool calls, test text model only |
| `--output-format text` | Output text only |
| `--max-turns 1` | Limit to minimal conversation turns |
| `--no-session-persistence` | Do not save this test session |

Expected output:

~~~text
WorkBuddy connection successful
~~~

### 8.4 How to Interpret CLI Results

| CLI Result | Meaning | Next Step |
|---|---|---|
| Returns `WorkBuddy connection successful` | WorkBuddy has loaded the configuration and completed a text invocation | Can start normal use; other capabilities still need separate verification |
| Reports model does not exist | CLI has not loaded the corresponding custom model, or `custom-local:` prefix is missing | Return to Sections 6 and 8.2 to check model ID and configuration loading |
| Returns 401 or 403 | API Key is invalid, expired, or has insufficient permissions | Re-obtain the API Key and update it in WorkBuddy |
| Returns 400 or model routing error | Model ID, protocol, or URL mismatch | Re-run Sections 4.2 and 5.2 |
| Returns 502 | AI Gateway received the request but the upstream call failed | Retry after a few seconds; if it continues, contact AI Gateway support |

### 8.5 curl Succeeds But CLI Fails

Check in order:

1. Whether CLI selected the correct model starting with `custom-local:`;
2. Whether the WorkBuddy local URL is correct;
3. Whether WorkBuddy has read the latest configuration;
4. Whether it is a transient 502;
5. Whether the GUI and CLI use the same WorkBuddy data directory;
6. Whether an Anthropic model was incorrectly added to the OpenAI custom configuration.

---

## 9. Advanced Troubleshooting: Local Configuration File Notes

### 9.1 Prefer the GUI

WorkBuddy officially supports adding, editing, and deleting custom models in the settings page. The GUI automatically saves API Key, URL, and capability flags.

> **Skip this section for first-time configuration.** Unless the interface cannot open, the model never appears after saving, you need to maintain models in bulk, or customer support explicitly asks you to check the file — do not directly modify the JSON. Regular users can complete Sections 6 and 7.

### 9.2 Why Two Configuration Paths May Appear

Different WorkBuddy / CodeBuddy versions and product forms may use different locations:

~~~text
~/.workbuddy/models.json
~/.codebuddy/models.json
~~~

Some WorkBuddy desktop versions use:

~~~text
~/.workbuddy/models.json
~~~

The official CodeBuddy `models.json` documentation also specifies:

~~~text
User-level: ~/.codebuddy/models.json
Project-level: <project-directory>/.codebuddy/models.json
~~~

Do not guess the path based on online examples; check which files actually exist on your current machine. When the GUI can save and use models normally, you do not need to manually modify these files.

### 9.3 Safely View Configuration Without Showing API Key

Run in Terminal:

~~~bash
for file in "$HOME/.workbuddy/models.json" "$HOME/.codebuddy/models.json"; do
  if [ -f "$file" ]; then
    echo "Found: $file"
    jq '
      if type == "array" then
        map(.apiKey = "<hidden>")
      elif .models then
        .models |= map(.apiKey = "<hidden>")
      else
        .
      end
    ' "$file"
  fi
done
~~~

The normal output should only show:

~~~text
"apiKey": "<hidden>"
~~~

Do not run `cat ~/.workbuddy/models.json` directly, as the file may contain the real API Key.

### 9.4 Back Up Before Modifying

Run in Terminal. The command only backs up files that actually exist:

~~~bash
for models_file in \
  "$HOME/.workbuddy/models.json" \
  "$HOME/.codebuddy/models.json"; do
  if [ -f "$models_file" ]; then
    backup_file="$models_file.backup-$(date +%Y%m%d-%H%M%S)"
    cp "$models_file" "$backup_file"
    echo "Backed up: $backup_file"
  fi
done
~~~

List recent backups:

~~~bash
find "$HOME/.workbuddy" "$HOME/.codebuddy" \
  -maxdepth 1 \
  -type f \
  -name 'models.json.backup-*' \
  -print 2>/dev/null \
  | sort \
  | tail -10
~~~

### 9.5 WorkBuddy Top-Level Array Format Example

If the first character of the existing `~/.workbuddy/models.json` is `[`, it uses the top-level array format. Standard OpenAI mode example:

~~~json
[
  {
    "id": "YOUR_MODEL_ID",
    "name": "YOUR_MODEL_ID",
    "vendor": "Custom",
    "url": "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1",
    "apiKey": "PASTE_YOUR_API_KEY_HERE",
    "supportsToolCall": false,
    "supportsImages": false,
    "supportsReasoning": false,
    "useCustomProtocol": false
  }
]
~~~

Where:

- `url` goes up to `/v1`;
- `useCustomProtocol` is `false`;
- WorkBuddy automatically appends `/chat/completions`;
- Fields like `supportsToolCall` are client capability declarations, not auto-detected results;
- Should be set to `false` until capability testing is complete.

If you already have a working `models.json`, do not overwrite the entire file with the example above. Back up first, then only modify the target model's `id`, `name`, `url`, `apiKey`, and `useCustomProtocol`; leave the other models and capability fields unchanged. This prevents accidentally deleting existing models or changing how they currently work.

When using the example manually, you must replace all `YOUR_MODEL_ID` with the full model ID from the OpenAI catalog, and replace `PASTE_YOUR_API_KEY_HERE` with your own API Key. Leaving the placeholders causes model-not-found or authentication failures.

### 9.6 Full URL Array Format

If you must use the full URL directly:

~~~json
[
  {
    "id": "YOUR_MODEL_ID",
    "name": "YOUR_MODEL_ID",
    "vendor": "Custom",
    "url": "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/chat/completions",
    "apiKey": "PASTE_YOUR_API_KEY_HERE",
    "supportsToolCall": false,
    "supportsImages": false,
    "supportsReasoning": false,
    "useCustomProtocol": true
  }
]
~~~

### 9.7 Do Not Mix Two JSON Structures

Another structure from the official CodeBuddy documentation is:

~~~json
{
  "models": [
    {
      "id": "YOUR_MODEL_ID",
      "name": "YOUR_MODEL_ID",
      "vendor": "Custom",
      "url": "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/chat/completions",
      "apiKey": "PASTE_YOUR_API_KEY_HERE",
      "supportsToolCall": false,
      "supportsImages": false
    }
  ],
  "availableModels": [
    "YOUR_MODEL_ID"
  ]
}
~~~

This object format mainly corresponds to the `~/.codebuddy/models.json` documentation. Do not overwrite it directly into `~/.workbuddy/models.json` that already uses a top-level array, unless the current version explicitly supports it.

### 9.8 Configuration Reload

Official documentation states that the model file supports hot reload, but different WorkBuddy desktop versions may have caching. If the model does not appear after saving:

1. Wait 2 to 3 seconds;
2. Switch to another settings page and return to the model page;
3. Fully quit WorkBuddy;
4. Reopen the application.

Terminal restart method:

~~~bash
osascript -e 'tell application "WorkBuddy" to quit' 2>/dev/null || true
open -a "/Applications/WorkBuddy.app"
~~~

### 9.9 Restrict Configuration File Permissions

~~~bash
chmod 600 "$HOME/.workbuddy/models.json"
~~~

If you are actually using `~/.codebuddy/models.json`, run:

~~~bash
chmod 600 "$HOME/.codebuddy/models.json"
~~~

---

## 10. Adding and Switching Multiple Models

### 10.1 Recommended: Add One by One in the GUI

Repeat the operations in Section 6 for each model, using the same Base URL and API Key, changing only the model ID.

Model IDs must come from your own OpenAI catalog query results, and each model must pass Section 5.2 individually. Do not bulk-copy model IDs from documentation, screenshots, or other users' configurations, as different API Keys may have different model scopes.

### 10.2 Probe Each Model Before Adding

One model succeeding does not mean other models in the same catalog will succeed. When troubleshooting multiple models, it is recommended to record for each:

~~~text
Model ID
Protocol
HTTP status
Whether final text exists
Test time
API Key / tenant scope
~~~

### 10.3 Switch Models

Select the target custom model in the model dropdown on the WorkBuddy conversation interface, then send a minimal message.

Switching models does not automatically switch protocols. All models added through this guide still use OpenAI Chat Completions.

---

## 11. Request Protocols and Configuration Boundaries

### 11.1 Three Protocols Cannot Be Mixed

| Item | OpenAI Chat Completions | OpenAI Responses | Anthropic Messages |
|---|---|---|---|
| Request path | `/chat/completions` | `/responses` | `/messages` |
| Authentication header | `Authorization: Bearer` | `Authorization: Bearer` | `x-api-key` + `anthropic-version` |
| Main input field | `messages` | `input` | `messages`; system prompt usually uses top-level `system` |
| Common output limit | `max_tokens` | `max_output_tokens` | `max_tokens` |
| Final text location | `choices[].message.content` | `output[].content[].text` | Content with `type=text` in `content[]` |
| WorkBuddy custom models | Used | Not used | Not used |

Changing only the URL or model name cannot convert one protocol into another. Endpoints, authentication headers, request bodies, streaming events, response structures, and tool call formats must all match together.

### 11.2 First Confirm Which Protocol Catalog Claude Appears In

Claude's native interface typically uses Anthropic Messages:

~~~text
POST /messages
x-api-key: API_KEY
anthropic-version: 2023-06-01
~~~

WorkBuddy's current custom models use OpenAI Chat Completions:

~~~text
POST /chat/completions
Authorization: Bearer API_KEY
~~~

Therefore, whether Claude or other models can be used in WorkBuddy is not determined by the model name, but by whether they have an OpenAI Chat-compatible route:

| Catalog and Test Result | WorkBuddy Handling |
|---|---|
| Appears only in Anthropic catalog, `/messages` succeeds | Cannot be directly added to current WorkBuddy custom models |
| Also appears in OpenAI catalog, and `/chat/completions` succeeds | Can be configured per Section 6 using the full model ID from the OpenAI catalog |
| Appears in OpenAI catalog but `/chat/completions` fails | Do not add yet; first troubleshoot permissions, routing, or upstream status |

### 11.3 Why a Full `/messages` URL Cannot Switch Protocols

WorkBuddy's "Custom Protocol / Use Custom Protocol" name is easily misunderstood. This toggle only decides whether WorkBuddy auto-completes the URL; it does not automatically perform any of the following conversions:

- Convert OpenAI `messages` request body to Anthropic Messages request body;
- Add `anthropic-version`;
- Convert OpenAI system messages to Anthropic top-level `system`;
- Convert Anthropic `content[]` responses to OpenAI `choices[]`;
- Convert streaming events, tool calls, and tool results.

Therefore, do not use the following combination to try to enable the Anthropic protocol:

~~~text
URL: https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/messages
Model: Claude model ID from the Anthropic catalog
Custom Protocol: On
~~~

This combination only makes WorkBuddy request the `/messages` address; the request body and response parsing may still be in OpenAI format, with no guarantee of a successful call.

### 11.4 Correct Conditions for Using Claude in WorkBuddy

If you need to use Claude in WorkBuddy, first confirm whether AI Gateway provides an "OpenAI Chat Completions-compatible Claude mapping". The verification method is exactly the same as for other models:

1. Query OpenAI `/models` using `Authorization: Bearer API_KEY`;
2. Copy the corresponding model ID from the results;
3. Use that ID to request `/chat/completions`;
4. Confirm HTTP 200 and that `choices[0].message.content` contains final text;
5. Configure using standard mode per Section 6.

If AI Gateway only provides Anthropic Messages, use a client that natively supports the Anthropic provider instead. Do not copy model IDs from the Anthropic catalog directly into WorkBuddy.

### 11.5 Multi-Protocol Models Such as DeepSeek and Qwen

Some models may appear in both OpenAI and Anthropic catalogs. They can use different protocols in different clients, but WorkBuddy does not automatically select protocols based on model names.

Always use the following in WorkBuddy:

~~~text
Model ID from OpenAI catalog
Base URL: https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1
Custom Protocol: Off
Verification endpoint: /chat/completions
~~~

Success results from the Anthropic catalog only indicate the model is also available for Anthropic clients; they do not change how WorkBuddy is configured.

### 11.6 What Catalog, curl, and WorkBuddy Each Confirm

| Result You See | What It Confirms | Next Step |
|---|---|---|
| Model appears in OpenAI `/models` | Current API Key can see the model ID in the OpenAI catalog view | Test `/chat/completions` |
| Chat curl returns HTTP 200 and final text | AI Gateway's route for that model can complete a basic text request | Add to WorkBuddy |
| Model appears in WorkBuddy model list | Local custom model configuration has been saved and loaded | Select the model on the conversation or task page |
| WorkBuddy returns final text | WorkBuddy, AI Gateway, model, and basic text pipeline are connected | Start using or continue testing advanced capabilities |

Success at one stage cannot substitute for the next. When the catalog succeeds but curl fails, troubleshoot protocol, permissions, or upstream routing; when curl succeeds but WorkBuddy fails, troubleshoot URL mode, model ID, and local configuration loading.

---

## 12. WorkBuddy Capability Boundaries

### 12.1 What You Can Do After Basic Configuration

Completing the verification in Sections 4 through 7 means the following pipeline is working:

~~~text
WorkBuddy
    → OpenAI Chat Completions request
    → AI Gateway
    → Target model
    → Returns text result
~~~

This is sufficient to confirm that basic text conversation works, but does not automatically mean tool calls, image input, or other advanced capabilities are also available.

### 12.2 Advanced Capabilities Require Separate Verification

| Capability | What Not to Rely On Alone | What to Confirm Before Enabling |
|---|---|---|
| Streaming output | Non-streaming text success | AI Gateway and model return correct OpenAI SSE; WorkBuddy displays content continuously |
| Tool calls | Model description says "supports Agent" | Requests and responses correctly handle `tools`, `tool_calls`, and tool result callbacks |
| Image input | Model name contains Vision or multimodal | WorkBuddy, AI Gateway, and model all accept the corresponding image content format |
| Reasoning mode | Model itself has reasoning capability | Reasoning fields, final text, and token counts can be correctly returned and parsed |
| Structured output | Plain JSON text success | Required JSON Schema or response format parameters can be fully forwarded |
| Long context | Vendor-published maximum context | AI Gateway plan, model routing, and WorkBuddy all allow the target input length |
| Concurrency and stability | Single request success | Sustained testing under actual concurrency, frequency, and usage periods |

### 12.3 Capability Toggles Are Declarations Only

In local configuration:

~~~text
"supportsToolCall": true
"supportsImages": true
"supportsReasoning": true
~~~

These only tell WorkBuddy to expose the corresponding capabilities in the UI; they do not automatically prove that AI Gateway and the model truly support them.

Correct process:

~~~text
First verify the capability with a standard request
    ↓
Confirm model and gateway response format is correct
    ↓
Then enable the WorkBuddy capability toggle
~~~

### 12.4 How to Determine Current Support Status

| Status | Meaning |
|---|---|
| Visible in catalog | `/models` returned the model ID |
| Invocation successful | An actual request returned HTTP 200 and final text |
| WorkBuddy usable | WorkBuddy GUI or CLI using that custom model returned correct text |
| Advanced capability available | Target capability has been separately end-to-end verified in WorkBuddy |
| Stably available | Verified across multiple attempts, multiple time points, and actual usage load |

If a model has only reached "visible in catalog", continue running curl; if curl succeeds but WorkBuddy fails, check WorkBuddy configuration; if it succeeds intermittently with occasional 502s, treat it as upstream instability — a single success cannot be recorded as stable.

WorkBuddy tasks may also read project files, run tools, or access connectors. A successful model connection does not mean all local permissions should be opened. Before enabling these capabilities, also review project scope, tool permissions, default permissions, security sandbox, and the data accessible in connectors.

---

## 13. Troubleshooting

### 13.1 No Characters Appear When Pasting API Key

This is normal. Section 4.1 uses `read -s` to hide input. Paste and press Enter; do not use `echo` to display the API Key.

### 13.2 WorkBuddy Shows Only One Custom Model

Cause: WorkBuddy displays locally saved models and does not automatically import the full `/models` catalog.

Resolution: Return to Section 6 and add the required models one by one.

### 13.3 Cannot See Claude

Cause: The Claude for your current API Key may appear only in the Anthropic protocol view, while WorkBuddy custom models use OpenAI Chat Completions.

Resolution: Check per Section 11.4 whether AI Gateway provides an OpenAI Chat-compatible Claude mapping. If not, use a client that supports the Anthropic provider.

### 13.4 curl Shows HTTP 000 or Connection Timeout

`HTTP 000` is not a server status code; it means curl received no HTTP response. Common causes include DNS, TLS, proxy, corporate firewall, or unreachable network.

Resolution:

1. Confirm your browser can access the internet normally;
2. Run `nslookup cn-shanghai-alicloud-aimesh.api.singdata.com` to check DNS resolution;
3. Check system proxy and corporate firewall;
4. If your organization requires a VPN or proxy, connect and retest;
5. Re-run Section 4.2 after network is restored.

### 13.5 HTTP 400, Path Is `/v1`

Cause: The request did not reach `/chat/completions`.

Resolution:

- In standard mode, fill Base URL up to `/v1` and disable Custom Protocol;
- In full URL mode, fill in to `/v1/chat/completions` and enable Custom Protocol.

### 13.6 HTTP 404 or Duplicate Path

Check whether the error message contains:

~~~text
/chat/completions/chat/completions
/v1/v1/chat/completions
~~~

If duplicated, keep only one URL mode per Section 6.3.

### 13.7 HTTP 401 or 403

Possible causes:

- Incorrect API Key;
- Expired API Key;
- API Key and Base URL do not belong to the same environment;
- API Key has no model permissions;
- Spaces or newlines included during copy.

Resolution: Rotate the API Key in the AI Gateway backend and re-paste it in WorkBuddy.

### 13.8 HTTP 400 No upstream candidates

Possible causes:

- Incorrect model ID;
- Dot written as hyphen;
- Model exists only in the Anthropic view;
- Current API Key has no permission for this model;
- No upstream candidates for the current protocol.

Troubleshooting order:

1. Re-query OpenAI `/models`;
2. Copy the model ID exactly;
3. Run the curl in Section 5;
4. Confirm you have not directly added a Claude model visible only in the Anthropic catalog to WorkBuddy;
5. Contact the AI Gateway administrator to check tenant routing.

### 13.9 HTTP 429 Too Many Requests

Indicates request frequency, concurrency, account quota, or upstream limits have been reached.

Resolution:

1. Reduce request frequency and concurrency;
2. Wait the retry time specified in the error response or response headers;
3. Check AI Gateway account quota and rate limiting policies;
4. Do not immediately perform high-frequency consecutive retries.

### 13.10 HTTP 502 Upstream failed

Indicates AI Gateway received the request but the upstream model call failed.

Resolution:

1. Retry 2 to 3 times with a few seconds between retries;
2. Switch to another verified model;
3. Record request ID and test time;
4. Contact AI Gateway administrator to check upstream;
5. Continue WorkBuddy configuration only after curl returns HTTP 200 with final text.

### 13.11 HTTP 200 But No Text

Resolution:

1. Increase `max_tokens` from 512 to 1024; increase to 4096 if still no final text;
2. Check `choices[0].message.content`;
3. Check if only `reasoning_content` is present;
4. Disable tool calls and redo a pure text test;
5. Confirm the response is indeed in OpenAI Chat format.

### 13.12 CLI Reports Model Does Not Exist

CLI custom models must include:

~~~text
custom-local:
~~~

Correct example:

~~~text
custom-local:YOUR_MODEL_ID
~~~

Replace `YOUR_MODEL_ID` with the full model ID saved in the GUI.

If it still does not exist, check whether WorkBuddy has loaded the local model configuration.

### 13.13 Model Does Not Appear After Saving

Resolve in order:

1. Wait 2 to 3 seconds;
2. Check that the model ID is not empty;
3. Check JSON format;
4. Check if `availableModels` is filtering out the model;
5. Fully quit and reopen WorkBuddy;
6. View Section 14 logs.

### 13.14 No Project Open

Some WorkBuddy Agent features require project context. Open a folder first, then send a model test message.

This type of prompt is not an AI Gateway request failure.

### 13.15 curl Succeeds But WorkBuddy Fails

This indicates AI Gateway's basic model routing is available; the issue is more likely in WorkBuddy's local configuration or model selection. Check in order:

1. The currently selected model is from the "Custom Models" group, not a same-named built-in model;
2. The standard mode URL is `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1`;
3. "Custom Protocol" remains off in standard mode;
4. The model ID in WorkBuddy exactly matches the ID used in curl;
5. Temporarily disable tool calls, images, and reasoning mode, and test with plain text only;
6. Reload WorkBuddy per Section 9.8;
7. Use the Section 8 CLI test on the same model for further diagnosis.

### 13.16 Restore After Misconfiguration

List backups:

~~~bash
find "$HOME/.workbuddy" "$HOME/.codebuddy" \
  -maxdepth 1 \
  -type f \
  -name 'models.json.backup-*' \
  -print 2>/dev/null \
  | sort \
  | tail -10
~~~

If you are currently using `~/.workbuddy/models.json`, confirm the target filename and restore:

~~~bash
cp \
  "$HOME/.workbuddy/models.json.backup-actual-timestamp" \
  "$HOME/.workbuddy/models.json"
~~~

If you are currently using `~/.codebuddy/models.json`:

~~~bash
cp \
  "$HOME/.codebuddy/models.json.backup-actual-timestamp" \
  "$HOME/.codebuddy/models.json"
~~~

Run only the command that matches your current configuration path. Do not enter "actual-timestamp" literally — replace it with the exact filename listed by the previous command. After restoring, reload WorkBuddy per Section 9.8.

### 13.17 Information to Prepare Before Contacting Customer Support

If the issue cannot be resolved following this section, submit the information below through the official private support channel. The more complete the information, the easier it is to determine whether the issue is in local configuration, AI Gateway, or the upstream model:

~~~text
Issue time: YYYY-MM-DD HH:MM (please specify time zone)
WorkBuddy version:
macOS version:
Configuration method: Standard Base URL / Fallback full URL
Base URL: https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1
Model ID:
OpenAI /models HTTP status code:
OpenAI /chat/completions HTTP status code:
WorkBuddy GUI error summary:
WorkBuddy CLI reproduced: Yes / No / Not tested
Intermittent success: Yes / No
Desensitized request ID (if available):
Troubleshooting steps already taken:
~~~

You can get version information in Terminal:

~~~bash
defaults read "/Applications/WorkBuddy.app/Contents/Info" CFBundleShortVersionString
sw_vers -productVersion
~~~

Before submitting, you must remove or redact:

- API Key, `Authorization`, and `x-api-key` values;
- The full `models.json`;
- Conversation content, project code, file paths, and personal information;
- Full logs unrelated to the issue.

A request ID can help official support staff locate the same request, but should only be submitted through trusted private support channels — do not post it on public web pages, group chats, or screenshots. Do not expose, repeatedly print, or re-send the API Key just to reproduce the issue.

---

## 14. Protect API Key When Viewing Logs

### 14.1 Log Locations

Prefer operating within the WorkBuddy GUI:

~~~text
Top menu "Help"
    ↓
Open log folder
~~~

This is the method least affected by version and filename changes.

Common WorkBuddy log locations on macOS:

~~~text
~/Library/Logs/WorkBuddy/main.log
~/Library/Logs/WorkBuddy/renderer.log
~~~

Log filenames may differ across versions. View existing log files:

~~~bash
find "$HOME/Library/Logs/WorkBuddy" \
  -maxdepth 1 \
  -type f \
  -print 2>/dev/null
~~~

If the directory exists, you can view recent errors:

~~~bash
for log_file in "$HOME/Library/Logs/WorkBuddy"/*.log(N); do
  if [ -f "$log_file" ]; then
    echo "Log: $log_file"
    rg -i \
      'error|failed|model|completion|401|403|400|404|429|502' \
      "$log_file" \
      | tail -100
  fi
done
~~~

### 14.2 Desensitize Before Sharing Logs

Logs may contain:

- API Keys;
- Authorization request headers;
- Local paths;
- User IDs;
- Request IDs;
- Conversation content;
- Third-party connector credentials.

Do not upload the full log to a ticket or post it in a group chat. Before sharing, remove at minimum:

~~~text
Authorization
Value after Bearer
x-api-key
apiKey
token
secret
password
Personal directory paths and conversation content
~~~

---

## 15. API Key and Configuration Security

### 15.1 API Key Is Stored Locally

WorkBuddy officially states that the API Key for custom models is saved to the local model configuration file. Therefore, local accounts, file backups, and logs should all be treated as sensitive data.

### 15.2 Security Rules to Follow

- Do not upload `models.json` to Git;
- Do not screenshot the full configuration;
- Do not run `echo "$WORKBUDDY_API_KEY"` in the command line;
- Do not enter a real API Key in documentation;
- Immediately revoke and rotate the API Key if it is leaked;
- Use different API Keys for different users, projects, and environments where possible;
- Clean up local API Keys when leaving the organization, decommissioning a device, or stopping use;
- Regularly check AI Gateway usage volume and costs.

### 15.3 Check Whether the File Is Tracked by Git

If using project-level configuration in a project directory, run:

~~~bash
git status --short
git ls-files | rg 'models\.json$' || true
~~~

If a file containing a real API Key is found to be tracked, first remove it from Git history and the remote repository, then immediately rotate the API Key. Deleting the file only in the latest commit may not clear the historical leak.

---

## 16. What You Will See After Configuration Is Complete

### 16.1 Model Settings Page

After a successful save, the custom model appears in WorkBuddy's model list. The number of models depends on how many configurations you have manually added, not the total count returned by AI Gateway `/models`.

### 16.2 Conversation or Task Page

After selecting a custom model in the model selector and sending a message, it is processed via the following path:

~~~text
Your input
    ↓
WorkBuddy custom model
    ↓
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/chat/completions>
    ↓
AI Gateway routes to target model
    ↓
WorkBuddy displays the model's returned result
~~~

### 16.3 Costs and Content Handling

Usage quota and costs for custom models are charged to your AI Gateway account. Prompts, project context, and attachments sent to custom models may be transmitted to the configured AI Gateway and its upstream models; confirm your organization's data security and compliance requirements before use.

### 16.4 Successful Configuration Does Not Mean All Features Are Enabled

After basic text conversation succeeds, you can start using text tasks normally. Capabilities such as tool calls, image input, reasoning mode, and long context should each be verified per Section 12 before deciding whether to enable the corresponding options.

---

## 17. Completion Checklist

Confirm each item before completing WorkBuddy configuration. The first group is required for basic text conversation; the second group should only be checked when using the corresponding feature or encountering the corresponding issue.

~~~text
Basic configuration required:
[ ] /Applications/WorkBuddy.app exists and can be launched
[ ] curl and jq can be executed
[ ] WorkBuddy version check returns a version number
[ ] WorkBuddy is logged in and can open a project
[ ] Base URL is https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1
[ ] API Key is entered and has not been exposed
[ ] Using OpenAI Chat Completions protocol
[ ] "Custom Protocol" remains off in standard mode
[ ] Target model is visible in OpenAI /models
[ ] Model ID is copied exactly from the OpenAI catalog
[ ] Vendor and protocol boundaries in Sections 5.3 and 5.4 are understood
[ ] curl request ultimately reaches /gateway/v1/chat/completions
[ ] curl returns HTTP 200
[ ] choices[0].message.content contains final text
[ ] WorkBuddy custom model is saved
[ ] Correct custom model is selected in WorkBuddy dropdown
[ ] GUI actual message returns expected text
[ ] Tool calls, streaming, and multimodal capabilities remain off until verified
[ ] Models visible only in the Anthropic catalog have not been directly added to WorkBuddy
[ ] models.json permissions are restricted and API Key has not entered Git

Check as needed:
[ ] If using CLI, CLI also returns expected text
[ ] If using fallback full URL, address goes to /chat/completions and "Custom Protocol" is enabled
[ ] If 502 occurred, curl and WorkBuddy verification have been redone after recovery
[ ] If Claude or multi-protocol models are needed, OpenAI and Anthropic protocol results have been confirmed separately
[ ] If tool calls, image input, or reasoning mode are needed, end-to-end capability verification has been completed separately
~~~

After completing all "Basic configuration required" items, WorkBuddy has completed basic text model configuration through AI Gateway and is ready to use. "Check as needed" items can be left blank when not applicable to the current scenario and do not affect basic text conversation acceptance.

If only the catalog query succeeded, the model cannot be considered available; if curl succeeds but WorkBuddy fails, prioritize checking URL mode, local model ID, configuration loading, and WorkBuddy logs; if both curl and WorkBuddy intermittently 502, record as upstream instability.

---

## 18. Official References

- WorkBuddy official website: <https://www.workbuddy.cn/>
- WorkBuddy Mac installation guide: <https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Installation-Mac-Guide>
- WorkBuddy model configuration: <https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Model>
- WorkBuddy FAQ: <https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/FAQ>
- CodeBuddy `models.json` configuration guide: <https://www.workbuddy.cn/docs/ide/Features/models>

When using official documentation, note version differences: `~/.codebuddy/models.json` and `~/.workbuddy/models.json` may both exist. Prefer the WorkBuddy GUI; when troubleshooting files, go by the configuration that the current version actually generates and loads.
