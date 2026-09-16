This is an operations guide for TRAE International Edition users. After completing the steps in order, you will be able to add Custom Models from AI Gateway to TRAE and confirm that the TRAE Agent is actually using the model you selected.

After completing this guide, you will be able to:

- Confirm that TRAE International Edition is installed and complete login;
- Securely enter the AI Gateway Base URL and API Key;
- Query the models visible to your API Key under both the OpenAI and Anthropic protocol views;
- Choose between OpenAI Chat or Anthropic Messages based on the model and protocol boundary;
- Verify that a model can return a final text response using standard `curl`;
- Add a Custom Model in TRAE and complete the connectivity test;
- Disable Auto Mode and send the first real message via the TRAE Agent;
- Diagnose whether an error is a network, authentication, path, protocol, permission, or upstream issue.

Example AI Gateway Base URL:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1>
~~~

If your relay address is different, replace the Base URL, API Key, and model ID accordingly. Never share your real API Key in chat, support tickets, screenshots, Git repositories, or public web pages.

Official links:

- TRAE International Edition download: [https://www.trae.ai/download](https://www.trae.ai/download)
- TRAE changelog: [https://www.trae.ai/changelog](https://www.trae.ai/changelog)

---

## Summary First

TRAE International Edition's "Custom Model" supports two API formats:

| Format | Supported by TRAE Custom Model | Request endpoint |
|---|---:|---|
| OpenAI Chat Completions | Supported | `/chat/completions` |
| Anthropic Messages | Supported | `/v1/messages` |
| OpenAI Responses | Not supported | `/responses` |

Whether configuration succeeds depends on four things:

1. Whether the API Key can see the model in the target protocol's model directory;
2. Whether the model can return text via a standard HTTP request under that protocol;
3. Whether the API format, URL, and model ID in TRAE are filled in correctly;
4. Whether the TRAE Agent has explicitly selected the Custom Model and returns text.

A model name prefix does not automatically switch protocols. Writing the model ID as `anthropic/claude-opus-5` does not mean TRAE will automatically use Anthropic Messages — you must explicitly select Anthropic Messages in TRAE's API format setting.

---

## 0. Configuration Flow

~~~text
Install and log in to TRAE International Edition
    ↓
Prepare Base URL, API Key, and model ID
    ↓
Query the model directory for the target protocol
    ↓
Verify with a standard curl using the same protocol
    ↓
Add a Custom Model in TRAE
    ↓
Pass the TRAE connectivity test
    ↓
Open a project and disable Auto Mode
    ↓
Select the Custom Model and send an Agent message
~~~

Do not skip the standard `curl` verification step. It lets you distinguish "network/authentication/path/upstream issues" from "TRAE page configuration issues" early, making troubleshooting faster.

---

## 1. Prepare TRAE International Edition

### 1.1 Distinguish Between the China Edition and the International Edition

The UI language cannot be used as a differentiator — the International Edition can also display Simplified Chinese. Use the application Bundle ID instead:

| Item | China Edition | International Edition |
|---|---|---|
| Common app name | `Trae CN.app` | `Trae.app` |
| Bundle ID | `cn.trae.app` | `com.trae.app` |
| Website | `trae.com.cn` | `trae.ai` |

### 1.2 Check the Version in Terminal

Press `Command + Space`, type `Terminal`, and press Enter to open a terminal.

If TRAE is installed in the current user's Applications directory, run:

~~~bash
TRAE_APP="$HOME/Applications/Trae.app"

if [ -d "$TRAE_APP" ]; then
  defaults read "$TRAE_APP/Contents/Info" CFBundleIdentifier
  defaults read "$TRAE_APP/Contents/Info" CFBundleShortVersionString
else
  echo 'Trae.app not found in ~/Applications'
fi
~~~

The International Edition must output:

~~~text
com.trae.app
~~~

If installed in the system Applications directory, run:

~~~bash
defaults read "/Applications/Trae.app/Contents/Info" CFBundleIdentifier
defaults read "/Applications/Trae.app/Contents/Info" CFBundleShortVersionString
~~~

### 1.3 If the China Edition Is Installed

Quit TRAE first, then download the International Edition from the [TRAE International Edition download page](https://www.trae.ai/download). Do not delete the user data directory directly, to avoid losing login state or local configuration.

After installation, re-run Section 1.2 to confirm the Bundle ID is `com.trae.app`.

TRAE IDE requires the macOS system version listed on the download page. For Apple Silicon Macs, select the `macOS (Apple Silicon)` installer.

### 1.4 Log In and Confirm the Custom Model Entry Point

Launch `Trae.app`, complete the International Edition account login, then confirm:

1. The TRAE main interface opens normally;
2. The account menu in the lower-left corner displays the current account;
3. Settings can navigate to `Models`;
4. The page contains `Add Custom Model`, `Custom Models`, or the corresponding entry point.

If you cannot see the Custom Model entry, first confirm the app version, login state, and whether you accidentally installed the China Edition.

### 1.5 Check Terminal Tools

The commands below use `curl` to send HTTP requests and `jq` to build JSON and read responses.

Run:

~~~bash
command -v curl
command -v jq
~~~

Under normal circumstances, two command paths are output, for example:

~~~text
/usr/bin/curl
/opt/homebrew/bin/jq
~~~

macOS ships with `curl` by default. If `jq` is missing and Homebrew is installed, run:

~~~bash
brew install jq
~~~

### 1.6 Do You Need a VPN?

Whether a VPN is needed depends on your network, not on the OpenAI or Anthropic protocol.

Only check your network proxy or VPN if:

- The `trae.ai` download page cannot be opened;
- `curl` reports `Could not resolve host`;
- `curl` connection times out or cannot be established;
- The TRAE login page fails to load.

If you have already received HTTP 200, 401, 403, 404, 429, or 5xx, the request has generally reached the server. Troubleshoot the API Key, URL, permissions, rate limiting, or upstream issues by status code first — do not assume it is a VPN problem.

---

## 2. Prepare Relay Information

### 2.1 Base URL

Example Base URL:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1>
~~~

This address already includes `/v1`. When configuring OpenAI Chat, do not manually append `/v1` or `/chat/completions` again, unless you have enabled TRAE's "Full URL" option.

The URL rules for Anthropic Messages are different; Section 8 covers both correct approaches.

### 2.2 API Key

Confirm:

- The API Key has not expired;
- The API Key has call permissions for the target model;
- The API Key and Base URL belong to the same environment;
- No extra spaces or line breaks were included when copying;
- The API Key has not been exposed.

### 2.3 Model ID

The model ID is the routing key and must be copied exactly from your own model directory.

Correct examples:

~~~text
openai/gpt-5.5
anthropic/claude-opus-5
deepseek/deepseek-v4-pro
qwen/qwen3.6-flash
~~~

Incorrect examples:

~~~text
gpt-5.5
anthropic/claude-opus-4-8
anthropic/claude-sonnet-4-6
~~~

Do not omit the vendor prefix, and do not modify dots, hyphens, or version numbers.

---

## 3. Vendor and Protocol Boundaries

### 3.1 Protocols Supported by TRAE

The TRAE Custom Model page supports:

| API Format | Authentication | TRAE Custom Model |
|---|---|---:|
| OpenAI Chat Completions | `Authorization: Bearer API_KEY` | Supported |
| Anthropic Messages | `x-api-key` plus `anthropic-version: 2023-06-01` | Supported |
| OpenAI Responses | `Authorization: Bearer API_KEY` | Not supported |

TRAE cannot automatically change the request format based on a model name or vendor prefix. The protocol must be manually selected on the model configuration page.

### 3.2 Protocol Selection Principles by Vendor

| Model Category | Preferred Protocol | Other Protocols | TRAE Configuration | Notes |
|---|---|---|---|---|
| OpenAI models | OpenAI Chat Completions | Some models or gateways may also offer Responses | OpenAI Chat Completions | TRAE Custom Model cannot select Responses; confirm Chat routing is available |
| Anthropic Claude | Anthropic Messages | Usually no OpenAI Chat or Responses routing | Anthropic Messages | Do not skip API format selection just because the model ID contains `anthropic/` |
| DeepSeek models | Determined by the specific model and gateway routing | Some models may offer both OpenAI Chat and Anthropic Messages | Use whichever protocol succeeds in curl | Do not assume all DeepSeek models support the same protocol based on vendor name |
| Qwen models | Determined by the specific model and gateway routing | Some models may offer OpenAI Chat, Responses, or Anthropic Messages | Use whichever protocol succeeds in curl | Even if Responses is available, it cannot be selected in TRAE Custom Model |
| Other vendor models | Follow the protocol directory and standard requests | Follow the protocol directory and standard requests | Only configure verified formats | Vendor name does not equal protocol capability |

"Vendor" here only helps you determine the direction for troubleshooting — it cannot replace model-level verification. The final result depends on the combination of "model ID + API Key + protocol + gateway routing".

### 3.3 When the Same Model Supports Two Protocols

If the same model appears in both the OpenAI and Anthropic directories and both standard `curl` calls return HTTP 200, you can create two separate configurations in TRAE:

~~~text
Same model + OpenAI Chat Completions
Same model + Anthropic Messages
~~~

These two configurations have different API formats, authentication headers, URLs, and response parsing — they cannot be copied from each other. Success with one protocol does not imply success with the other.

### 3.4 The Boundary of OpenAI Responses

Even if a Responses request for a model succeeds, it cannot be directly added to TRAE Custom Models, because TRAE currently has no OpenAI Responses custom format.

Therefore:

- Models that succeed with Chat Completions can be added in OpenAI format;
- Models that succeed with Anthropic Messages can be added in Anthropic format;
- Models that only support Responses cannot be integrated directly through TRAE Custom Models;
- Other tool configurations using Responses cannot be directly copied to TRAE.

### 3.5 The Model Directory Is Not a Fixed List

The model directory is determined by the API Key's tenant, permissions, subscription, quota, region, and upstream publishing status. Different users may see different models.

When configuring, only use the `/models` results returned for your own API Key:

~~~text
Your own model directory
  → Select model ID
Same-protocol curl succeeds
  → Select TRAE API format
TRAE connectivity test succeeds
  → Proceed to Agent real-world verification
~~~

If a model is not in your protocol directory, do not guess the model ID manually and do not just modify the URL. To add model permissions, contact AI Gateway service support.

---

## 4. Securely Enter the API Key in Terminal

Do not write the API Key directly into command history. In the same Terminal, run:

~~~bash
export RELAY_BASE_URL='https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1'
read -s "RELAY_API_KEY?Paste your AI Gateway API Key, then press Enter: "
echo
~~~

It is normal that no characters appear on screen when pasting.

Only check whether the variable is empty — do not display the API Key:

~~~bash
if [ -n "$RELAY_API_KEY" ]; then
  echo 'API Key loaded into current Terminal'
else
  echo 'API Key is empty, please re-enter'
fi
~~~

Do not close this Terminal until verification is complete. Closing it will clear the variables.

---

## 5. Query Your Model Directory

TRAE does not automatically import all models from AI Gateway. Query the directory first, then select a model.

### 5.1 Query the OpenAI Protocol Directory

Run:

~~~bash
curl -sS -o /tmp/trae-openai-models.json \
  --max-time 60 \
  -w 'HTTP %{http_code}\n' \
  "$RELAY_BASE_URL/models" \
  -H "Authorization: Bearer $RELAY_API_KEY"

jq -r '.data[]?.id' /tmp/trae-openai-models.json
~~~

This command queries the OpenAI protocol view. It only shows models visible to the current API Key under that protocol.

### 5.2 Query the Anthropic Protocol Directory

Run:

~~~bash
curl -sS -o /tmp/trae-anthropic-models.json \
  --max-time 60 \
  -w 'HTTP %{http_code}\n' \
  "$RELAY_BASE_URL/models" \
  -H "x-api-key: $RELAY_API_KEY" \
  -H 'anthropic-version: 2023-06-01'

jq -r '.data[]?.id' /tmp/trae-anthropic-models.json
~~~

This command queries the Anthropic protocol view. Whether Claude, DeepSeek, Qwen, or other vendor models appear depends on the actual output of the current API Key.

### 5.3 What the Directory, curl, and TRAE Each Indicate

These three results correspond to three different stages — do not treat them as the same "success" marker:

| Result | What it indicates | Next step |
|---|---|---|
| Model present in `/models` | The current API Key can see the full model ID in that protocol view | Run a same-protocol `curl` |
| Same-protocol `curl` returns HTTP 200 and final text | The AI Gateway model route can complete a basic text request | Select the same API format in TRAE |
| TRAE connectivity test succeeds | TRAE's URL, API format, and API Key are basically matched | Open a project and complete Agent real-world verification |
| TRAE Agent returns final text | The basic text chain through TRAE, AI Gateway, protocol, and model is connected | Start using or verify advanced capabilities as needed |

### 5.4 Why the Two Directories May Differ

The relay determines the protocol based on the request headers:

~~~text
Authorization: Bearer
  → OpenAI protocol directory

x-api-key + anthropic-version
  → Anthropic protocol directory
~~~

Therefore:

- Claude not appearing in the OpenAI directory does not necessarily mean Claude is unavailable;
- OpenAI models not appearing in the Anthropic directory does not necessarily mean OpenAI is unavailable;
- A model appearing in the directory only means it is discoverable, not that requests will succeed;
- If a model is not in the directory, do not manually add or modify the model name.

### 5.5 Directory Request Status Codes

| Status Code | Meaning | Action |
|---|---|---|
| HTTP 200 | Network and basic authentication are normal | Continue verifying the model |
| HTTP 401 | API Key missing, incorrect, or expired | Re-enter the API Key |
| HTTP 403 | API Key has no access permission | Check tenant, subscription, and model permissions |
| HTTP 404 | Base URL or path error | Check that the path ends at `/gateway/v1` |
| HTTP 429 | Rate limited or quota exceeded | Wait and retry, or use a different quota |
| HTTP 5xx | Gateway or upstream failure | Save the error information and retry later |
| DNS failure or connection timeout | Network, proxy, or VPN issue | Check the network environment |

---

## 6. Verify the Model with Standard curl

After selecting a model, you must verify using the same protocol that TRAE will use. Only open the TRAE configuration page after the standard request succeeds.

### 6.1 Verify OpenAI Chat Completions

Replace the model ID with your own:

~~~bash
export RELAY_MODEL='openai/gpt-5.5'
~~~

Run:

~~~bash
curl -sS -o /tmp/trae-openai-test.json \
  --max-time 60 \
  -w 'HTTP %{http_code}\n' \
  "$RELAY_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $RELAY_API_KEY" \
  -H 'Content-Type: application/json' \
  -d "$(jq -cn \
    --arg model "$RELAY_MODEL" \
    '{model:$model,max_tokens:256,messages:[{role:"user",content:"Reply only: OpenAI test succeeded"}]}')"

jq -r '.choices[0].message.content // .error.message // "Final text not found, please check the full response"' \
  /tmp/trae-openai-test.json
~~~

Success criteria:

~~~text
HTTP 200
OpenAI test succeeded
~~~

### 6.2 Verify Anthropic Messages

Replace the model ID with your own Anthropic protocol model:

~~~bash
export RELAY_MODEL='anthropic/claude-opus-5'
~~~

Run:

~~~bash
curl -sS -o /tmp/trae-anthropic-test.json \
  --max-time 60 \
  -w 'HTTP %{http_code}\n' \
  "$RELAY_BASE_URL/messages" \
  -H "x-api-key: $RELAY_API_KEY" \
  -H 'anthropic-version: 2023-06-01' \
  -H 'Content-Type: application/json' \
  -d "$(jq -cn \
    --arg model "$RELAY_MODEL" \
    '{model:$model,max_tokens:256,messages:[{role:"user",content:"Reply only: Anthropic test succeeded"}]}')"

jq -r '([.content[]? | select(.type=="text") | .text] | join("\n")) as $text | if ($text | length) > 0 then $text else (.error.message // "Final text not found, please check the full response") end' \
  /tmp/trae-anthropic-test.json
~~~

Success criteria:

~~~text
HTTP 200
Anthropic test succeeded
~~~

### 6.3 HTTP 200 but No Final Text

Some reasoning models consume a large portion of the output budget. If you only see thinking/reasoning with no final text, try increasing:

~~~text
max_tokens: 256
~~~

to:

~~~text
max_tokens: 1024
~~~

or:

~~~text
max_tokens: 4096
~~~

Only "HTTP 200 + normal completion + final text" counts as a successful verification.

---

## 7. Configure an OpenAI Chat Model in TRAE

### 7.1 Open the Custom Model Page

In TRAE International Edition, navigate to:

~~~text
Settings (top right)
  → Models
  → Add Model
  → Custom Model
~~~

Do not select the built-in OpenAI provider preset in TRAE. When using your own AI Gateway, you must select "Custom Model".

### 7.2 Recommended Approach: Full URL Disabled

Fill in:

| Field | Value |
|---|---|
| API Format | `OpenAI Chat Completions` |
| Full URL | Disabled |
| Custom request URL | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1` |
| Model ID | Copied exactly from your OpenAI directory |
| Model display name | Can be left blank, or enter a recognizable name |
| API Key | Your AI Gateway API Key |

With "Full URL" disabled, TRAE automatically appends:

~~~text
/chat/completions
~~~

The final request URL will be:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/chat/completions>
~~~

### 7.3 OpenAI Full URL Approach

You can also enable "Full URL" and enter directly:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/chat/completions>
~~~

Only one of these two approaches can be used. Do not enter an address containing `/chat/completions` when "Full URL" is already disabled — this will result in double concatenation.

### 7.4 Save and Test

Click "Add Model" or "Save". TRAE will initiate a real connectivity test, which may consume a small number of tokens.

After the connectivity test succeeds:

- The Custom Model appears in the model list;
- The model toggle can be enabled;
- No 401, 403, 404, or upstream errors appear.

Saving successfully only means the connectivity test passed. You still need to complete the Agent real-world verification in Section 9.

---

## 8. Configure an Anthropic Messages Model in TRAE

### 8.1 Recommended Approach: Full URL Enabled

Navigate to:

~~~text
Settings
  → Models
  → Add Model
  → Custom Model
~~~

Fill in:

| Field | Value |
|---|---|
| API Format | `Anthropic Messages` |
| Full URL | Enabled |
| Custom request URL | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/messages` |
| Model ID | Copied exactly from your Anthropic directory |
| Model display name | Can be left blank |
| API Key | Your AI Gateway API Key |

With "Full URL" enabled, TRAE will not append any additional path. The final request URL is:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/messages>
~~~

### 8.2 Approach with Full URL Disabled

If "Full URL" is disabled, the base address must end at:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway>
~~~

TRAE will automatically append:

~~~text
/v1/messages
~~~

The final address will still be:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/messages>
~~~

Do not enter `.../gateway/v1` with "Full URL" disabled — this will result in:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/v1/messages>
~~~

This address will typically return 404.

### 8.3 Save and Test

Click "Add Model" or "Save". If the connectivity test succeeds, the Custom Model will appear in the model list.

If `No upstream candidates` is returned, check in priority order:

1. Whether the model ID was copied exactly from the Anthropic directory;
2. Whether the API format is actually set to Anthropic Messages;
3. Whether the URL is `/gateway/v1/messages`;
4. Whether the API Key has permission for this model.

---

## 9. Real-World Verification with TRAE Agent

After the connectivity test succeeds, you still need to confirm the model selection and returned results in a real Agent session.

### 9.1 Open a Project Folder

Click:

~~~text
Open Folder
~~~

You can open an existing code project or create a new empty folder for testing.

If no project is open, TRAE may prompt:

~~~text
Please open a folder first to save files in the project
~~~

This indicates missing project context — it does not mean the API connection failed.

### 9.2 Disable Auto Mode

If the model selector shows `Auto`, disable Auto Mode first. Auto Mode may select a TRAE built-in model, making it impossible to confirm whether requests are going through your AI Gateway.

### 9.3 Select the Custom Model

Open the model selector at the bottom of the Agent input box and select the Custom Model you just added.

Confirm the selector shows the target Custom Model, not:

~~~text
Auto
GPT-5.4
Other TRAE built-in models
~~~

### 9.4 Send a Minimal Message

OpenAI Chat test:

~~~text
Reply only: TRAE relay working
~~~

Anthropic Messages test:

~~~text
Reply only: TRAE Claude working
~~~

Success criteria:

1. The user message appears in the session;
2. The Agent exits the analyzing state;
3. The expected text is returned;
4. No 401, 403, 404, 429, 502, or other upstream errors;
5. The model selector still shows the target Custom Model.

---

## 10. Adding a Second Protocol or More Models

### 10.1 Adding a Second Protocol

If you have already configured and verified OpenAI Chat and also want to use Claude or other Anthropic protocol models, you do not need to reinstall TRAE or delete existing models:

1. Run Section 5.2 to query the Anthropic protocol directory;
2. Run Section 6.2 to send an Anthropic Messages request using the target model;
3. Run Section 8 to add a new Anthropic Custom Model;
4. Run Section 9 to open a project, disable Auto Mode, and select the new model;
5. Send an Anthropic test message and confirm the new model returns final text.

OpenAI Chat and Anthropic Messages are two independent configurations. Keeping the existing model does not affect adding a new one.

### 10.2 Adding More Models

For each additional model, verify in the order: "directory → same-protocol `curl` → TRAE connectivity → Agent message".

If the same model supports two protocols, you can add two separate records:

~~~text
Same model + OpenAI Chat Completions
Same model + Anthropic Messages
~~~

The API format, URL, authentication method, and request structure of the two records cannot be mixed. It is recommended to first add a model that has passed the complete workflow, then add other models one by one to make issues easier to locate.

If a new model does not appear in your protocol directory, or the same-protocol `curl` returns 400, 401, 403, 429, or 5xx, stop the TRAE configuration and confirm the API Key permissions and upstream routing first.

---

## 11. Product Support Boundaries

### 11.1 Capabilities That Can Be Completed

Through TRAE Custom Models and AI Gateway, you can:

- Configure a custom Base URL in TRAE;
- Use your own API Key;
- Use OpenAI Chat models verified through the protocol;
- Use Anthropic Messages models verified through the protocol;
- Conduct text conversations and coding tasks in Agent/SOLO sessions;
- Select the corresponding protocol and model ID based on different models.

### 11.2 Capabilities That Should Not Be Directly Assumed

Successful text conversation verification does not mean the following capabilities are necessarily available:

- OpenAI Responses;
- CUE or code completion;
- Code Review;
- Git commit message generation;
- Streaming SSE;
- Tool calls and multi-turn tool results;
- Multimodal inputs such as images, PDFs, or audio;
- JSON Schema or structured output;
- Prompt Cache;
- Extended Thinking;
- Extra-long context;
- Parallel Agent, Max Mode, or other TRAE-exclusive features.

These capabilities require simultaneous support from TRAE, the gateway, the model upstream, and request parameters — they should be verified separately.

### 11.3 Built-in Models, Custom Models, and Auto Mode

These three are not the same type of configuration:

| Type | Description |
|---|---|
| TRAE built-in models | Determined by TRAE account, region, subscription, and server-side configuration |
| Provider presets | Use the official interface fields of the corresponding provider |
| Custom Models | Use the AI Gateway address, API Key, and model ID you entered |
| Auto Mode | TRAE automatically selects the model; cannot be used to confirm a specified Custom Model |

When selecting a Custom Model, do not rely on Auto Mode at the same time.

### 11.4 Successful Configuration Does Not Mean Permanent Stability

Model upstreams may experience rate limiting, insufficient quota, transient 5xx errors, resource constraints, long-context limits, or parameter incompatibilities.

When an intermittent failure occurs, re-run the same-protocol `curl` first. If `curl` also fails, the issue is outside of TRAE; if `curl` succeeds but TRAE fails, then check the TRAE API format, URL, project folder, and model selection.

---

## 12. Troubleshooting

### 12.1 Cannot Find Anthropic Messages

Confirm in order:

1. You are using TRAE International Edition;
2. The Bundle ID is `com.trae.app`;
3. You are logged into the International Edition account;
4. You entered "Add Model → Custom Model";
5. The TRAE version supports Anthropic Messages.

### 12.2 Connectivity Test Returns 404

First check whether the path is being double-concatenated.

Incorrect OpenAI address:

~~~text
/gateway/v1/chat/completions/chat/completions
~~~

Incorrect Anthropic address:

~~~text
/gateway/v1/v1/messages
~~~

Correct approach:

- OpenAI: Disable Full URL, fill in up to `/gateway/v1`;
- Anthropic: Recommended to enable Full URL and enter the full path `/gateway/v1/messages`.

### 12.3 HTTP 401 or 403

Possible causes:

- API Key is incorrect or expired;
- API Key does not have model permissions;
- Base URL and API Key do not belong to the same environment;
- Wrong protocol's authentication header was used.

Re-run the commands from Sections 5 and 6 in Terminal first.

### 12.4 No upstream candidates

Common causes:

- Model ID is misspelled;
- Wrong API format selected;
- Current API Key does not have permission for this model;
- Current protocol has no routing for this model.

Resolution order:

1. Query `/models` for the corresponding protocol;
2. Copy the model ID exactly;
3. Use a standard `curl` with the same protocol;
4. Check the TRAE API format;
5. Check the Full URL setting and auto-concatenation rules.

### 12.5 HTTP 429

HTTP 429 typically means rate limiting, insufficient quota, or concurrency limits.

Actions:

1. Wait and retry;
2. Check account quota and model permissions;
3. Reduce request frequency;
4. Do not test by repeatedly clicking "Add Model".

### 12.6 HTTP 5xx

HTTP 5xx indicates a gateway or upstream call failure. Common causes include temporary upstream unavailability, insufficient provider resources, model parameter incompatibility, or a gateway fault.

Save the following information before contacting AI Gateway service support:

- Model ID;
- Request protocol;
- HTTP status code;
- Error message;
- Time of occurrence;
- Request ID or trace ID.

Remove the API Key, Authorization header, and `x-api-key` before sending.

### 12.7 Model Added but Agent Does Not Respond

Check in order:

1. Whether a project folder is open;
2. Whether Auto Mode is disabled;
3. Whether the Custom Model is explicitly selected;
4. Whether the Custom Model toggle is enabled;
5. Whether the standard `curl` still succeeds;
6. Whether 401, 404, 429, or 5xx errors appear.

### 12.8 TRAE Is Actually Using a Built-in Model

If the output does not look like the target model, or the request is not reaching AI Gateway:

1. Disable Auto Mode;
2. Reselect the Custom Model at the bottom of the input box;
3. Start a new session;
4. Retry with a minimal test message.

### 12.9 HTTP 200 but No Final Text

The output budget may have been consumed by thinking/reasoning, or the request format and response parsing do not match.

First increase `max_tokens`, then confirm:

- OpenAI reads `.choices[0].message.content`;
- Anthropic reads `.text` from items with `type=text` in `.content[]`;
- The request is not sending an Anthropic body to an OpenAI endpoint, or vice versa.

---

## 13. API Key Security

Please follow these rules:

- Do not write the API Key into documents, scripts, or public repositories;
- Do not share configuration screenshots containing the API Key;
- Do not run `echo "$RELAY_API_KEY"`;
- Do not share screenshots of debug commands with authentication headers;
- Immediately revoke and regenerate the API Key if it is leaked;
- Use different API Keys for different customers, projects, and environments.

After testing, clean up the variables:

~~~bash
unset RELAY_API_KEY
unset RELAY_BASE_URL
unset RELAY_MODEL
~~~

If you pasted the API Key via clipboard, you can clear the macOS clipboard:

~~~bash
pbcopy </dev/null
~~~

---

## 14. Completion Checklist

### Installation and Login

~~~text
[ ] TRAE International Edition installed
[ ] Bundle ID is com.trae.app
[ ] macOS version meets requirements
[ ] International Edition account login completed
[ ] Custom Model page accessible from Settings
~~~

### AI Gateway

~~~text
[ ] Base URL is correct
[ ] API Key is not expired and has not been exposed
[ ] Queried /models for the target protocol using your own API Key
[ ] Model ID copied exactly from the directory
[ ] Selected the same API protocol used for curl
[ ] Same-protocol curl returned HTTP 200
[ ] curl response contains final text
~~~

### TRAE

~~~text
[ ] OpenAI uses Chat Completions format
[ ] Anthropic uses Messages format
[ ] OpenAI Responses not selected in TRAE
[ ] OpenAI URL does not duplicate /chat/completions
[ ] Anthropic URL does not duplicate /v1/messages
[ ] Custom Model saved successfully
[ ] TRAE connectivity test succeeded
~~~

### Agent

~~~text
[ ] Project folder is open
[ ] Auto Mode is disabled
[ ] Current session explicitly selects the Custom Model
[ ] Agent returns expected text
[ ] No 401, 403, 404, 429, or 5xx errors
[ ] Advanced capabilities verified separately and documented separately
~~~

When all items are complete, TRAE has connected to the specified model through AI Gateway and completed a real text call.

If only the directory is visible, write "model discoverable"; if standard `curl` succeeds, write "protocol call succeeded"; only if both TRAE connectivity and Agent messages also succeed can you write "TRAE verified working".

---

## 15. References

- [TRAE International Edition download](https://www.trae.ai/download)
- [TRAE changelog](https://www.trae.ai/changelog)

Both TRAE and AI Gateway may be updated. When page fields or command output do not exactly match this document, first confirm the TRAE version, API format, Full URL setting, and target protocol, then troubleshoot by following the status code order in Section 12.
