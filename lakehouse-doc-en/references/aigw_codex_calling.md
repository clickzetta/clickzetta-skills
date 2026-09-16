This guide is intended for users who are setting up Terminal for the first time, configuring Codex CLI for the first time, or need to use Codex CLI through a third-party AI Gateway.

After completing this guide, you will be able to:

- Install and verify Codex CLI;
- Securely enter the AI Gateway Base URL and API Key;
- Query the models visible to your API Key;
- Determine the appropriate request protocol for models from different vendors;
- Validate the target model using OpenAI Responses;
- Write the validated model into `~/.codex/config.toml`;
- Confirm the connection using `codex doctor` and `codex exec`;
- Diagnose whether errors are caused by network, authentication, protocol, configuration, or upstream issues.

This guide uses macOS, zsh, and the following AI Gateway as examples:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1>
~~~

If your gateway address is different, simply replace the Base URL, API Key, and model ID. Never share your real API Key in chats, support tickets, screenshots, Git repositories, or public web pages.

Example environment and validation scope for this guide:

~~~text
Supported OS: macOS, zsh
Validated version: Codex CLI 0.148.0-alpha.9
Last validated: 2026-08-19 (Asia/Shanghai)
Base protocol: OpenAI Responses
Base acceptance: /models, /responses, and codex exec text calls
~~~

Codex CLI and AI Gateway are continuously updated. This guide focuses on protocol identification, configuration steps, and practical validation — it does not treat any particular model state as a permanent guarantee.

> For a first-time setup, simply complete Sections 2–8 in order, then check the results against Section 18. Sections 9–17 are for understanding protocol boundaries, configuring advanced features, and troubleshooting — they are not required steps for initial onboarding.

## Overview: Model Vendor and Request Protocol Are Two Different Things

When Codex CLI connects to an AI Gateway through a custom provider, the `wire_api` field in the configuration determines the request format. The vendor prefix in a model name does not automatically switch the protocol.

This guide recommends using a single custom provider:

| Codex Config Field | `wire_api` | AI Gateway Endpoint | When to Use |
|---|---|---|---|
| `model_providers.clickzetta` | `responses` | `/responses` | The Responses curl for the target model succeeds and you are ready to use it with Codex |
| OpenAI Chat Completions | Not supported by Codex custom providers | `/chat/completions` | Only for other clients or to diagnose whether a model has a Chat route |
| Anthropic Messages | Not supported by Codex custom providers | `/messages` | Only for other Anthropic clients; Codex requires an additional conversion layer |

In the official configuration, the only valid value for `wire_api` in a custom provider is `responses`. This means:

1. Codex sends `POST /responses` for that provider;
2. Codex does not switch protocols based on `anthropic/`, `deepseek/`, or `qwen/` prefixes;
3. A successful Chat or Anthropic request does not mean the same model can be used with Codex;
4. If Claude only has a `/messages` route, it must be converted to `/responses` through a gateway or local proxy;
5. A model appearing in `/models` only means the current API Key can see it — it does not guarantee a `/responses` upstream exists.

### Choosing a Protocol by Model Vendor

The matrix below is for selecting the validation path — it is not a fixed model catalog. Specific models must be verified using your own `/models` results and endpoint tests:

| Model Vendor or Series | OpenAI Chat Completions | OpenAI Responses | Anthropic Messages | Codex Config Recommendation |
|---|---|---|---|---|
| OpenAI GPT, Codex series | Available when provided by the gateway | Common compatible path, but must be tested separately | Usually not the first choice | Only configure directly if Responses test succeeds |
| Anthropic Claude | Only when the gateway provides a compatible route | Must be tested separately; cannot be inferred from the name | Native access path, usually the first to test | Codex requires a Responses compatibility layer |
| DeepSeek series | Available when provided by the gateway | Must be tested separately | Available when provided by the gateway | Only select models that actually pass the Responses test |
| Qwen series | Available when provided by the gateway | Must be tested separately | Available when provided by the gateway | Validate Responses first, then confirm reasoning parameters |
| Gemini, Grok, Mistral, Meta, and others | Determined by gateway adaptation | Determined by gateway adaptation | Determined by gateway adaptation | Based on actual endpoint test results |

The most important rules are:

~~~text
Model vendor
    ≠ Request protocol

Model appearing in the catalog
    ≠ Model usable through Codex

Responses curl succeeds
    ≠ Files, tools, search, and multimodal all available
~~~

When using Codex only, configuring a single Responses provider is sufficient. There is no need to create non-existent `wire_api` values in `config.toml` just to test Chat or Anthropic protocols.

---

## 0. Full Operation Roadmap

For a first-time setup, follow these steps in order:

~~~text
1. Section 2: Install or verify Codex CLI
2. Section 3: Securely enter the API Key
3. Section 4: Query your model directory and select the full model ID
4. Section 5: Validate the target model using the Responses curl
5. Section 6: Back up and write to ~/.codex/config.toml
6. Section 7: Run strict config and doctor
7. Section 8: Use codex exec to receive the first real text response
8. Section 18: Confirm the result and completion checklist after setup
~~~

After completing step 8, you have Codex's basic text and coding capabilities. Tool calls, file modifications, streaming, multimodal input, and search capabilities are covered in Sections 9, 12, and 13, and need to be validated separately for actual use cases.

If you only need basic text access, go directly to Sections 2–8. You only need to read Sections 9–12 in detail if:

- You want to understand why a specific vendor model cannot be used with Codex;
- You want to use Claude or other Anthropic models;
- You want to use CC Switch or another protocol conversion layer;
- You want to determine whether tool, streaming, search, or multimodal capabilities are compatible.

The most basic acceptance criteria for a completed setup are:

1. The corresponding API Key can see the target model;
2. The request endpoint for the target protocol returns HTTP 200;
3. Final text exists in the response;
4. `codex exec` returns actual model text;
5. If tools or file modification are needed, validate sandbox and tool call permissions separately.

Seeing only a model name does not directly indicate the model can be used in Codex.

### What You Can Do After Completing Setup

After completing Section 8, you will be able to:

- Run `codex` in a project directory to enter an interactive coding session;
- Send tasks using the default model in the configuration;
- Use `codex exec --model YOUR_MODEL_ID` to temporarily switch to another validated model;
- Let Codex read files, modify the workspace, and run commands within the configured approval policy and sandbox scope;
- Use `codex doctor` and standard curl to distinguish between client, network, permission, and upstream issues when needed.

This guide validates "Responses text calls" by default. File modification, tool calls, streaming, multimodal input, and search capabilities are still subject to the combined influence of the model, provider, sandbox, and upstream implementation — a successful first text reply should not automatically be treated as full support for all features.

Codex CLI is a local command-line client, not a persistent Gateway service. This guide applies only to Codex CLI. Provider configurations for OpenClaw, Claude Code, OpenCode, and similar tools cannot be copied directly to Codex.

---

## 1. Preparation

### 1.1 Base URL

This example uses:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1>
~~~

The address already includes `/v1`. Do not write it as:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/v1>
~~~

Codex appends `/responses` after the Base URL, so the final request will look like:

~~~text
<https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/responses>
~~~

Do not write the Base URL all the way to `/responses`, as the client may append the path again.

### 1.2 API Key

Create an API Key in the AI Gateway backend and confirm:

- The API Key has not expired;
- The API Key has permissions for the target model;
- The API Key and Base URL belong to the same environment;
- The API Key has permission for the OpenAI Responses route;
- No extra spaces or line breaks were introduced when copying.

A token that can access the Chat or Anthropic route does not necessarily have Responses route permissions.

### 1.3 Model ID

The model ID must be copied verbatim from the `/models` response for the current API Key. The `YOUR_MODEL_ID` below is only a placeholder and must be replaced with your own full model ID:

~~~text
YOUR_MODEL_ID
~~~

The `--model` parameter in Codex takes the upstream model ID. You do not need to prepend the Codex provider ID.

Correct:

~~~text
--model YOUR_MODEL_ID
~~~

Do not write:

~~~text
--model clickzetta/YOUR_MODEL_ID
~~~

`clickzetta` is the local provider ID; `YOUR_MODEL_ID` is the model ID sent to the AI Gateway.

### 1.4 Where to Run Commands

All commands in this guide are run in macOS Terminal.

Press Command + Space, type Terminal, and press Enter to open it.

The terminal prompt may look like:

~~~text
a123@Mac ~ %
~~~

Do not copy the prompt. Copy only the commands in the code blocks.

### 1.5 Whether VPN Is Required

Whether the AI Gateway itself requires a VPN depends on your local network. Run:

~~~bash
curl -I --connect-timeout 10 \
  https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/models
~~~

As long as you receive an HTTP response, the domain and network path are basically reachable. A 401 or 403 also indicates network connectivity — it just means authentication has not been set up correctly yet.

The following situations require checking proxy, VPN, firewall, or DNS settings:

- `Could not resolve host`;
- `Connection timed out`;
- Persistent TLS handshake failures;
- Corporate network blocking the install script or login page.

If the check above receives an HTTP response, no additional VPN is needed for Codex to reach the gateway. Whether the official ChatGPT login page and install sources are directly accessible depends on your network and region.

---

## 2. Install or Verify Codex CLI

### 2.1 Check Basic Tools

Run:

~~~bash
command -v curl
command -v jq
~~~

If you see two file paths, you are good to continue.

If `jq` is not installed on macOS and Homebrew is already installed:

~~~bash
brew install jq
jq --version
~~~

### 2.2 Check Codex CLI

Run:

~~~bash
command -v codex
codex --version
~~~

A normal response looks like:

~~~text
/path/to/codex
codex-cli 0.148.0-alpha.9
~~~

A different version is not necessarily a problem, as long as the command executes. Configuration fields change across versions — check `codex --help` for the current version before making config changes.

### 2.3 Check for Multiple Codex Installations

Run:

~~~bash
type -a codex
~~~

If multiple paths are returned, Terminal actually uses the version listed first.

Common sources include:

~~~text
Standalone Codex CLI installation
Codex CLI installed via npm or Homebrew
Codex CLI bundled inside the ChatGPT/Codex desktop app
~~~

The path for the desktop app's bundled version may look like:

~~~text
/Applications/ChatGPT.app/Contents/Resources/codex
~~~

If "the same command behaves differently in two Terminal windows," start by running `type -a codex` and `codex --version` to confirm which binary is actually running.

### 2.4 If Codex Is Not Installed

The official documentation provides a macOS/Linux standalone install script example:

~~~bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
~~~

After installation, close Terminal, reopen it, then run:

~~~bash
codex --version
~~~

The official install and update method may change — refer to the [Codex CLI official documentation](https://developers.openai.com/codex/cli/) for the latest instructions.

### 2.5 Update Codex

For the standalone CLI, try:

~~~bash
codex update
~~~

If you are using the version bundled inside the desktop app, update the desktop app instead. After updating, run:

~~~bash
command -v codex
codex --version
~~~

---

## 3. Understanding Codex Authentication

### 3.1 Official OpenAI/ChatGPT Login

When using the official OpenAI service directly, run:

~~~bash
codex login
~~~

Then complete the login in your browser.

When using an official OpenAI API Key, run:

~~~bash
printenv OPENAI_API_KEY | codex login --with-api-key
~~~

Check the current login status:

~~~bash
codex login status
~~~

Clear login credentials:

~~~bash
codex logout
~~~

### 3.2 Recommended: Use `env_key` for Gateways

Third-party AI Gateways are better served by using a custom provider's `env_key`:

~~~toml
[model_providers.clickzetta]
env_key = "CLICKZETTA_API_KEY"
~~~

This tells Codex to read the token from the environment variable named `CLICKZETTA_API_KEY`, rather than writing the token in plain text inside `config.toml`.

### 3.3 Securely Enter the API Key in the Current Terminal

In zsh, run:

~~~bash
read -s "CLICKZETTA_API_KEY?Enter API Key: "
echo
export CLICKZETTA_API_KEY
~~~

No characters will appear on screen while typing — this is normal. Press Enter when done.

Confirm the variable exists without printing the token:

~~~bash
if [ -n "${CLICKZETTA_API_KEY:-}" ]; then
  echo "API Key loaded"
else
  echo "API Key not loaded"
fi
~~~

Do not run:

~~~bash
echo "$CLICKZETTA_API_KEY"
~~~

### 3.4 Difference Between Temporary and Persistent Variables

Variables set with `read` and `export` are only valid in the current Terminal session. They must be re-entered after the Terminal is closed.

For production environments, it is recommended to store tokens in:

- macOS Keychain;
- Enterprise secret management services;
- CI/CD secrets;
- Permission-controlled startup environments.

Never commit real tokens directly to `.zshrc`, `config.toml`, or a Git repository.

### 3.5 macOS Keychain Example (Optional)

Write the token to Keychain. The `-w` flag is placed at the end of the command so that Terminal will prompt for input — the token does not need to be written directly in the command:

~~~bash
security add-generic-password \
  -U \
  -a "$USER" \
  -s "clickzetta-codex-api-key" \
  -w
~~~

Test that the value can be read, but do not print the result to a public terminal log:

~~~bash
CLICKZETTA_API_KEY="$(security find-generic-password \
  -a "$USER" \
  -s "clickzetta-codex-api-key" \
  -w)"
export CLICKZETTA_API_KEY
~~~

To load automatically each time you open Terminal, add the read command to your personal shell startup configuration. In enterprise environments, prefer the company's unified secret management solution.

### 3.6 Do Not Mix Two Authentication Methods

This guide recommends using only:

~~~text
env_key = "CLICKZETTA_API_KEY"
~~~

Do not also configure:

~~~toml
requires_openai_auth = true
experimental_bearer_token = "..."
~~~

`requires_openai_auth = true` is more appropriate when reusing Codex's saved OpenAI login credentials. When using a gateway with an independent token, `env_key` is clearer and easier to troubleshoot.

---

## 4. Query Models and Determine Protocol

### 4.1 Query Your Model Directory

The model directory confirms the permissions scope of your API Key and the full model IDs. It is not proof of protocol capability and is not a fixed Codex model catalog.

Make sure `CLICKZETTA_API_KEY` is set in the current Terminal, then run:

~~~bash
export CLICKZETTA_BASE_URL="https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1"

curl -sS -o /tmp/codex-models-openai.json \
  --max-time 30 \
  -w 'HTTP %{http_code}\n' \
  "$CLICKZETTA_BASE_URL/models" \
  -H "Authorization: Bearer $CLICKZETTA_API_KEY"

jq -r '
  if (.data | type) == "array" then
    .data[]?.id
  else
    .error.message // .message // "Could not read model directory"
  end
' /tmp/codex-models-openai.json
~~~

Decide on the next step based on the HTTP status in the output:

| Result | Description | Next Step |
|---|---|---|
| `HTTP 200` | Model directory is accessible | Copy the target model ID verbatim from the results and proceed to Section 5 |
| `HTTP 000` or curl connection error | Network, DNS, proxy, or VPN path issue | Go back to Section 1.5 to check the network; do not start by changing the model ID |
| `HTTP 401` / `403` | API Key, auth header, or permission issue | Go back to Sections 1.2 and 3.3 to check the token and current Terminal |
| `HTTP 404` | Base URL or path is incorrect | Check whether `/v1` is duplicated or missing in the Base URL |
| `HTTP 429` | Current API Key or upstream is rate-limited | Wait and retry, or contact the AI Gateway support team to confirm quotas |
| `HTTP 5xx` | Gateway or upstream temporary error | Record the time, model, and request ID, then retry |

If your gateway also provides an Anthropic-compatible endpoint, query it using the Anthropic auth header:

~~~bash
curl -sS -o /tmp/codex-models-anthropic.json \
  --max-time 30 \
  -w 'HTTP %{http_code}\n' \
  "$CLICKZETTA_BASE_URL/models" \
  -H "x-api-key: $CLICKZETTA_API_KEY" \
  -H 'anthropic-version: 2023-06-01'

jq -r '
  if (.data | type) == "array" then
    .data[]?.id
  else
    .error.message // .message // "Could not read Anthropic model directory"
  end
' /tmp/codex-models-anthropic.json
~~~

When configuring a model, the full ID must be copied verbatim from the results. For example, `openai/...`, `anthropic/...`, `deepseek/...`, or `qwen/...` are just naming conventions for model IDs — they are not protocol switches in Codex.

### 4.2 Protocol Boundaries for Models from Different Vendors

A vendor's native API and the compatible protocols exposed by an AI Gateway may differ. The same model may appear in multiple protocol directories, or only in one of them.

Evaluation has three layers:

~~~text
Directory visibility: API Key can list the full model ID
Protocol availability: The specified endpoint returns HTTP 200 and final text
Codex availability: Responses succeeds, and codex exec can parse the response
~~~

For example, Claude may succeed in Anthropic Messages, but if `/responses` has no upstream, it still cannot be used directly with Codex. Similarly, you cannot automatically infer that Responses will succeed for DeepSeek or Qwen just because Chat succeeds.

Tool calls, streaming, images, files, search, structured output, and long context are higher-level capabilities that need to be validated separately after basic text succeeds.

### 4.3 Practical Rules for Selecting a Model

If the target is Codex CLI, follow these rules:

~~~text
1. The model appears in your own directory;
2. The gateway provides an OpenAI Responses /responses route for that model;
3. Use the Responses curl in Section 5 to get HTTP 200 and final text;
4. Then validate with codex exec in Section 8;
5. Only validate sandbox and tool calls if file or tool use is needed.
~~~

If a model only succeeds with Chat Completions, it cannot be used directly with Codex. If a model only succeeds with Anthropic Messages, it also cannot be used directly with Codex. In those cases, use a client that supports the corresponding protocol, or use a proxy layer that converts Responses to the target protocol.

### 4.4 Why Different Protocols See Different Models

A gateway may return different model views based on request headers and endpoints:

~~~text
Authorization: Bearer ...
    → OpenAI-compatible view

x-api-key: ...
anthropic-version: 2023-06-01
    → Anthropic-compatible view
~~~

Therefore, a model being visible in an Anthropic query does not mean it will necessarily appear in an OpenAI Responses query, and vice versa. When determining whether Codex can use a model, only the actual `/responses` result matters.

---

## 5. Validate the Model with a Standard Responses Curl First

### 5.1 Why Use curl First

curl separates the problem into two layers:

~~~text
curl fails
→ Base URL, token, model, protocol, or upstream routing issue

curl succeeds but Codex fails
→ Codex configuration, reasoning parameters, streaming response, model metadata, or tool call issue
~~~

Do not skip curl and go straight to modifying the Codex configuration — this makes it very hard to distinguish client-side problems from gateway problems.

### 5.2 Minimal Responses Request

Run:

~~~bash
export CLICKZETTA_MODEL="YOUR_MODEL_ID"

curl -sS -o /tmp/codex-test-responses.json \
  --max-time 60 \
  -w 'HTTP %{http_code}\n' \
  "$CLICKZETTA_BASE_URL/responses" \
  -H "Authorization: Bearer $CLICKZETTA_API_KEY" \
  -H 'Content-Type: application/json' \
  -d "$(jq -nc \
    --arg model "$CLICKZETTA_MODEL" \
    '{
      model: $model,
      input: "Reply with only: OK",
      max_output_tokens: 512,
      store: false
    }')"
~~~

Then run:

~~~bash
jq . /tmp/codex-test-responses.json
~~~

A normal result must satisfy all of the following:

- HTTP 200;
- `status` is a completion state;
- `output_text` exists in `output`;
- The final text is the actual content returned by the model.

### 5.3 Extract Only the Final Text

Run:

~~~bash
jq -r '
  ([.output[]?.content[]?
    | select(.type == "output_text" or .type == "text")
    | .text] | join("\n")) as $text
  | if ($text | length) > 0 then
      $text
    else
      .error.message // .message // "HTTP returned, but no final text found"
    end
' /tmp/codex-test-responses.json
~~~

Expected final text:

~~~text
OK
~~~

### 5.4 HTTP 200 Still Requires Checking for Final Text

Reasoning models may produce reasoning content first. If the output budget is too small, the HTTP status may be 200 but the response may contain no final text.

Acceptance validation must check:

~~~text
HTTP status
Completion state
Final output_text
~~~

Checking HTTP 200 alone is not sufficient.

---

## 6. Write the Validated Model to Codex CLI

### 6.1 Codex Configuration File Location

User-level configuration file:

~~~text
~/.codex/config.toml
~~~

Custom providers, authentication sources, and Base URLs should be written in the user-level configuration.

A project directory can also have:

~~~text
<project directory>/.codex/config.toml
~~~

However, the official documentation explicitly restricts this: project-level configuration cannot override machine-level provider configuration such as `model_provider` and `model_providers`. Even if the project is trusted, gateway providers should be written to `~/.codex/config.toml`.

### 6.2 Back Up Before Modifying

Run:

~~~bash
mkdir -p "$HOME/.codex"

if [ -f "$HOME/.codex/config.toml" ]; then
  cp "$HOME/.codex/config.toml" \
    "$HOME/.codex/config.toml.bak.$(date +%Y%m%d-%H%M%S)"
fi
~~~

View the backup:

~~~bash
ls -lt "$HOME/.codex"/config.toml*
~~~

Note the full name of the most recent backup file. If the configuration fails to load later, use that file to restore. Replace `full path to backup file` below with the actual file shown by `ls -lt`:

~~~bash
cp "full path to backup file" "$HOME/.codex/config.toml"
chmod 600 "$HOME/.codex/config.toml"

codex --strict-config doctor \
  --summary \
  --no-color \
  --ascii
~~~

Restoring the configuration only restores the file content — it does not restore environment variables that were cleared via `unset`, closing Terminal, or restarting the computer. After restoring, confirm `CLICKZETTA_API_KEY` is loaded again as described in Section 3.3.

### 6.3 Recommended Configuration for New Users

If `~/.codex/config.toml` does not exist or is empty, run:

~~~bash
nano "$HOME/.codex/config.toml"
~~~

Paste the following content:

~~~toml
model_provider = "clickzetta"
model = "YOUR_MODEL_ID"
model_reasoning_effort = "medium"
model_verbosity = "low"
model_reasoning_summary = "auto"

approval_policy = "on-request"
sandbox_mode = "workspace-write"

[model_providers.clickzetta]
name = "Singdata AI Gateway"
base_url = "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1"
env_key = "CLICKZETTA_API_KEY"
wire_api = "responses"
request_max_retries = 4
stream_max_retries = 5
stream_idle_timeout_ms = 300000
~~~

Before saving, replace `YOUR_MODEL_ID` with the full model ID queried in Section 4. Do not prepend a local provider name like `clickzetta/` to the model ID.

The configuration above includes both basic connection fields and a set of conservative runtime parameters: `model_reasoning_effort = "medium"`, `model_verbosity = "low"`, and `model_reasoning_summary = "auto"`. The fields that are truly required for basic access are the provider, model ID, Base URL, `env_key`, and `wire_api = "responses"`. If the Section 5 curl succeeded but a particular model rejects reasoning or verbosity-related parameters, you can temporarily remove `model_reasoning_summary` and `model_verbosity` and retry. Do not remove or change `wire_api`.

In nano:

1. Press Control + O to save;
2. Press Enter to confirm the file name;
3. Press Control + X to exit.

After saving the configuration file, at minimum confirm the following fields are present:

~~~text
model_provider = "clickzetta"
model = "your full model ID"
wire_api = "responses"
env_key = "CLICKZETTA_API_KEY"
~~~

The model ID must exactly match the query result from Section 4. Do not only check whether the file was saved successfully — continue to Section 7 and Section 8 for actual validation.

### 6.4 Users with Existing Configuration Should Not Overwrite the Entire File

If you already have plugins, MCP, project trust records, or other settings, do not replace the entire file with the template above.

For migration, you only need to:

1. Set the top-level `model_provider = "clickzetta"` before the first `[table name]`;
2. Set `model = "YOUR_MODEL_ID"` in the same top-level area;
3. Add or modify `[model_providers.clickzetta]`;
4. Keep existing `[plugins]`, `[mcp_servers]`, `[projects]`, and other provider tables;
5. After saving, run the full validation in Sections 7 and 8.

The original provider can be kept as a fallback. For example, you can have both in the file at the same time:

~~~toml
model_provider = "clickzetta"
model = "YOUR_MODEL_ID"

[model_providers.custom]
name = "Existing Provider"
base_url = "https://existing-provider.example/v1"
wire_api = "responses"

[model_providers.clickzetta]
name = "Singdata AI Gateway"
base_url = "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1"
env_key = "CLICKZETTA_API_KEY"
wire_api = "responses"
~~~

The two provider tables above can coexist, but which one is actually used is determined by the `model_provider` field at the top of the file. Do not add `requires_openai_auth = true` inside `[model_providers.clickzetta]`, and do not write real API Keys into that table.

If the old configuration has `model_provider` under `[projects."..."]`, do not treat it as a global setting. Codex ignores project-level configuration for provider overrides. Put the effective `model_provider` at the top level of the user-level `~/.codex/config.toml`.

### 6.5 The Most Common TOML Pitfall: Position of Top-Level Fields

The following fields are top-level:

~~~toml
model_provider = "clickzetta"
model = "YOUR_MODEL_ID"
model_reasoning_effort = "medium"
~~~

They must appear before the first `[table name]`.

Incorrect example:

~~~toml
[projects."/Users/example/project"]
trust_level = "trusted"

model_provider = "clickzetta"
~~~

The `model_provider` above will be parsed by TOML as a field inside the `projects."/Users/example/project"` table — not as a global provider selection — and may have no effect at all.

Correct example:

~~~toml
model_provider = "clickzetta"
model = "YOUR_MODEL_ID"

[projects."/Users/example/project"]
trust_level = "trusted"
~~~

Do not simply append top-level configuration to the end of the file.

### 6.6 Do Not Define the Provider Table Twice

Do not have this appear twice in one file:

~~~toml
[model_providers.clickzetta]
~~~

If it already exists, modify the existing table. Duplicate tables cause TOML parsing to fail.

### 6.7 Reserved Provider ID Names

The following provider IDs are built-in and reserved by the official spec:

~~~text
openai
ollama
lmstudio
~~~

Do not name your custom gateway using these values. This guide uses:

~~~text
clickzetta
~~~

### 6.8 Why `model_reasoning_effort = "medium"` Is Recommended

Different upstreams have varying levels of support for reasoning effort levels.

For third-party models, `high` or `xhigh` may trigger a thinking budget parameter that the upstream does not accept, for example:

~~~text
The thinking_budget parameter must be a positive integer
and not greater than 131072
~~~

Therefore, `medium` is recommended as the universal default when targeting multiple models. Increase the level only after confirming that the specific model supports it.

### 6.9 `model_verbosity` May Be Ignored

Codex uses fallback metadata for third-party models that are not in the built-in model directory.

Some third-party models may produce a warning like:

~~~text
model_verbosity is set but ignored as the model does not support verbosity
~~~

This does not necessarily mean the request failed — it only means the current model metadata does not declare verbosity capability.

### 6.10 Do Not Casually Enable WebSocket and Web Search

Custom providers do not declare Responses WebSocket and standalone Web Search support by default.

Only consider configuring the following when the gateway actually implements the corresponding interface:

~~~toml
supports_websockets = true
supports_standalone_web_search = true
~~~

Setting these to `true` only declares the capability on the client side — it does not automatically give the gateway that interface. The model, provider, gateway, and runtime must all support it simultaneously.

---

## 7. Check That the Configuration Is Correct

### 7.1 Codex Does Not Have `config validate`

Codex CLI does not have a command like OpenClaw's:

~~~text
codex config validate
~~~

Do not copy commands from other tools.

Codex recommends a three-layer validation:

~~~text
Strict config loading
→ doctor check
→ codex exec actual request
~~~

### 7.2 Use Strict Config and Doctor

Run:

~~~bash
codex --strict-config doctor \
  --summary \
  --no-color \
  --ascii
~~~

Focus on:

~~~text
Configuration
  [ok] config
  [ok] auth

Connectivity
  [ok] reachability
~~~

`doctor` also checks Terminal, session history, MCP, Git, and sandbox. Even if some items show warn/fail at the end, it does not necessarily mean the AI Gateway failed.

For example:

- `TERM=dumb` is a current terminal capability issue;
- Missing history thread files are a local session history issue;
- A MCP 403 is a MCP service issue;
- `reachability` succeeding confirms the provider endpoint is reachable.

The final exit code of `doctor` may be non-zero due to history thread, Terminal, MCP, or plugin issues. When determining whether basic gateway access is complete, do not rely solely on the final count or exit code. The following key items must all be checked:

| Check Item | Basic Access Requirement | Description |
|---|---|---|
| `Configuration / config` | `ok` | `config.toml` can be loaded strictly |
| `Configuration / auth` | `ok` | Active provider can obtain authentication information |
| `Connectivity / reachability` | `ok` | Active provider endpoint is reachable |
| Section 8 `codex exec` | Exit code 0 and final text present | This is the final model call acceptance test |

If the first three items are normal but `doctor` returns non-zero due to unrelated checks, proceed to Section 8. Only if `codex exec` also fails should you troubleshoot further per Section 15.

### 7.3 Check Login Status

This is an optional check. When accessing a gateway with `env_key`, the absence of an official OpenAI/ChatGPT login does not affect gateway requests.

Run:

~~~bash
codex login status
~~~

If the provider uses `env_key`, confirm separately that the current Terminal has it loaded:

~~~bash
if [ -n "${CLICKZETTA_API_KEY:-}" ]; then
  echo "CLICKZETTA_API_KEY loaded"
else
  echo "CLICKZETTA_API_KEY not loaded"
fi
~~~

`codex login status` only shows the official login or API Key status saved by Codex — it does not substitute for a custom `env_key` check. Computers that have previously used official Codex may still show the original OpenAI/ChatGPT login status. This does not mean the current gateway request will go through the official interface, nor does it mean the gateway configuration has failed.

For AI Gateway users, validate authentication and actual routing in this order:

~~~text
CLICKZETTA_API_KEY loaded
→ Top-level model_provider = "clickzetta"
→ doctor's auth and reachability are normal
→ codex exec output shows provider: clickzetta
~~~

Environment variables are only effective for the current Terminal and its child processes. After switching terminals, closing the window, or restarting the computer, the API Key must be reloaded unless you have configured persistent loading per Section 3.4 or 3.5.

### 7.4 View Current CLI Parameters

Run:

~~~bash
codex --help
codex exec --help
~~~

Parameter positions may differ across versions. When encountering `unexpected argument`, refer to the current version's help output.

---

## 8. Send the First Message with Codex CLI

### 8.1 Minimal Non-Interactive Test

To test in any directory, run:

~~~bash
codex --ask-for-approval never exec \
  --ephemeral \
  --skip-git-repo-check \
  --sandbox read-only \
  --model YOUR_MODEL_ID \
  -c 'model_reasoning_effort="medium"' \
  -c 'model_verbosity="low"' \
  'Do not call any tools. Reply only with: Codex OK'
~~~

Expected final text:

~~~text
Codex OK
~~~

The current version typically also displays the actual model and provider in the run info. Confirm output similar to:

~~~text
model: YOUR_MODEL_ID
provider: clickzetta
approval: never
sandbox: read-only
~~~

Success is not measured by the process starting, but by:

- Codex actually sending a Responses request;
- `provider` in the run info is `clickzetta`;
- `model` in the run info matches the full model ID specified this time;
- Final exit code is 0;
- Output contains the model's final text;
- No 400/502 returned after retries are exhausted.

### 8.2 Parameter Position Constraint

In the current version, the approval parameter should be placed before `exec`:

Correct:

~~~bash
codex --ask-for-approval never exec ...
~~~

Incorrect:

~~~bash
codex exec --ask-for-approval never ...
~~~

The incorrect form may return:

~~~text
unexpected argument '--ask-for-approval' found
~~~

### 8.3 Why These Test Parameters Are Used

| Parameter | Purpose |
|---|---|
| `--ephemeral` | Does not persist this test session |
| `--skip-git-repo-check` | Allows testing in non-Git directories |
| `--sandbox read-only` | Prevents the model from modifying files during testing |
| `--ask-for-approval never` | No approval prompts for minimal text testing |
| `--model` | Temporarily specifies the model without changing the default config |
| `-c` | Overrides configuration only for this run |

These parameters are suitable for a "text reply only" connectivity test and do not imply that approval should be permanently disabled in daily development.

### 8.4 Interactive Mode

Navigate to the project directory:

~~~bash
cd /your/project/directory
codex
~~~

Common commands in the interactive interface:

~~~text
/status       View current model, directory, and permissions
/model        Select model and reasoning effort level
/permissions  View or adjust permissions
/review       Perform a code review
/init         Create an AGENTS.md project description
~~~

### 8.5 Temporarily Switch the Model

Without modifying the config file:

~~~bash
codex --model YOUR_MODEL_ID
~~~

Non-interactive:

~~~bash
codex exec \
  --model YOUR_MODEL_ID \
  --skip-git-repo-check \
  'Reply only with: OK'
~~~

### 8.6 Temporarily Adjust the Reasoning Effort Level

~~~bash
codex exec \
  --model YOUR_MODEL_ID \
  --skip-git-repo-check \
  -c 'model_reasoning_effort="medium"' \
  'Reply only with: OK'
~~~

---
## 9. Understanding Validation Results and Capability Scope

### 9.1 Why Validate by Protocol

The model directory only answers "which models can this API Key see" — it cannot answer "can this model be used through Codex." To determine whether a model can be used in Codex CLI, the entire protocol chain must be validated:

~~~text
Model directory
→ OpenAI Responses /responses
→ Codex exec
→ Validate tools, streaming, and file permissions when needed
~~~

Codex uses OpenAI Responses. Even if the same model can respond through OpenAI Chat Completions or Anthropic Messages, the Responses validation cannot be skipped.

### 9.2 Recommended Validation Order

| Validation Layer | Recommended Status Name | Pass Criteria | What It Demonstrates |
|---|---|---|---|
| Permissions | Model directory visible | `/models` returns the target model | Current API Key can see the model |
| Protocol | Responses route available | `/responses` returns HTTP 200 | Gateway has a corresponding Responses route |
| Content | Responses text available | Completion state and final text present | The model can complete a basic Responses text request |
| Codex CLI | Codex basic available | `codex exec` exit code is 0 and provider/model is correct | Usable for current Codex basic text and coding tasks |
| Capability | Codex workflow validated | Files, tools, streaming, and other actual features pass one by one | Usable for specifically validated workflows |

Only when all four layers pass can the model be used for Codex basic text tasks. The fifth layer needs to be confirmed separately based on your actual use case.

When describing model status externally, use the status names from the table above. Do not write "model directory visible" as "Codex supported," and do not write a single successful text call as "all advanced features supported."

### 9.3 How to Read Validation Results

| Result | What It Means for You | Next Step |
|---|---|---|
| Responses and Codex both succeed | Can proceed with basic text and coding tasks | Confirm sandbox per Section 13, then begin modifying files |
| Chat or Messages succeeds, Responses fails | The model is available for other protocol clients | Use a client that supports the corresponding protocol, or add a conversion layer |
| Responses returns 400 / `No upstream candidates` | Gateway has no Responses upstream for this model, or insufficient permissions | Verify model ID, permissions, and routing; do not repeatedly modify Codex parameters |
| Responses returns 502 | Upstream call or gateway routing failure | Preserve time, model, protocol, and request ID, then contact the AI Gateway support team |
| HTTP 200 but no final text | Output budget or response conversion is incomplete | Increase output budget and check `status`, `output`, and `incomplete_details` |
| Codex can start but requests fail | Local config, parameters, or streaming parsing may have issues | Compare with Section 5 curl first, then check Sections 6, 7, and 12 |

### 9.4 How to Evaluate Models from Different Vendors in Codex

The table below contains configuration rules, not a model catalog. Model names may change, but the protocol evaluation method remains the same:

| Vendor or Model Type | Typically Available Protocols | Judgment When Configuring for Codex |
|---|---|---|
| OpenAI models | OpenAI Chat or Responses, depending on the gateway | Only configure directly if the Responses route actually succeeds |
| Anthropic Claude | Anthropic Messages | Codex does not automatically send Messages; a Responses compatibility layer is required |
| DeepSeek | Commonly OpenAI Chat; some gateways also provide Anthropic or Responses | Do not infer from the name; must actually validate Responses |
| Qwen | Determined by the gateway; Chat, Responses, or Anthropic-compatible routes may be available | Validate Responses first, then choose reasoning effort based on model support |
| Other vendors or custom aliases | Determined by gateway and upstream adaptation | Only based on the gateway catalog, API documentation, and actual request results |

Different models from the same vendor may use different upstreams. A successful result for one model cannot be applied to other models from the same vendor.

### 9.5 Basic Text Support and Advanced Capabilities Are Two Different Things

A successful Responses text call only means Codex can complete basic conversation. The following capabilities need to be validated separately:

- Streaming output and reconnection on disconnect;
- Tool calls and tool result callbacks;
- Image, file, or other multimodal inputs;
- Web Search, MCP, and external connectors;
- JSON Schema or structured output;
- Long context, compression, and multi-turn sessions;
- Reasoning budget, verbosity, and context window.

When this guide says "available for Codex," it means the Responses text call and Codex basic tasks have passed — it does not automatically include the advanced capabilities listed above.

### 9.6 When curl Succeeds but Codex Fails

Troubleshoot in this order:

1. Confirm `codex --version` and `type -a codex`;
2. Confirm `model_provider` is in the user-level `~/.codex/config.toml`;
3. Confirm the provider's `wire_api` is `responses`;
4. Confirm the model ID is identical to the curl command;
5. Temporarily lower the reasoning effort to `medium`;
6. Retry with the read-only `codex exec` from Section 8;
7. If it still fails, preserve the sanitized error and request ID, then contact the gateway to confirm routing.

---

## 10. Request Protocol Boundaries

### 10.1 Custom Providers Only Use Responses

The official configuration reference specifies that the only valid value for `model_providers.<id>.wire_api` in a custom provider is:

~~~text
responses
~~~

Therefore the following values are not supported:

~~~toml
wire_api = "chat_completions"
wire_api = "openai-completions"
wire_api = "anthropic-messages"
wire_api = "messages"
~~~

This is not a matter of using different field names — Codex's current custom providers simply do not have these protocol options.

### 10.2 The Three Protocols Cannot Be Mixed

| Item | OpenAI Chat Completions | OpenAI Responses | Anthropic Messages |
|---|---|---|---|
| Path | `/chat/completions` | `/responses` | `/messages` |
| Primary input | `messages` | `input` | `messages` + top-level `system` |
| Output budget | `max_tokens` | `max_output_tokens` | `max_tokens` |
| Tool results | `tool_calls` | Responses function/tool items | `tool_use` / `tool_result` |
| Streaming events | Chat SSE | Responses SSE | Anthropic SSE |
| Codex custom provider | Not supported | Supported | Not supported |

Changing only the URL or model name cannot make a client automatically switch protocols.

### 10.3 Model Prefix Is Not a Protocol Switch

For example:

~~~text
anthropic/claude-opus-5
~~~

`anthropic/` is just part of the model ID. When given to Codex, it still sends:

~~~text
POST /responses
~~~

It will not automatically send:

~~~text
POST /messages
~~~

### 10.4 Chat Success Does Not Mean Codex Will Succeed

If a DeepSeek or other vendor model shows:

~~~text
OpenAI Chat Completions: Success
Anthropic Messages: Success
OpenAI Responses: No upstream candidates
Codex: Failure
~~~

This is not because Codex does not recognize the DeepSeek name — it is because the Responses route required by Codex does not exist.

### 10.5 Anthropic Success Does Not Mean Codex Will Succeed

If Claude or another Anthropic model shows:

~~~text
anthropic/claude-opus-5
POST /messages  → HTTP 200, returns OK
POST /responses → HTTP 400, No upstream candidates
~~~

This means the model and API Key may be usable through an Anthropic client, but cannot be used directly with Codex through that Responses route.

### 10.6 The Directory View Is Not Proof of Protocol Capability

Record these separately:

~~~text
Whether the model is visible in the directory
Whether the Responses curl succeeds
Whether Codex succeeds
Whether tool calls succeed
~~~

Do not keep just a single "total model list."

---

## 11. Claude, Anthropic, and CC Switch

### 11.1 Why Claude Cannot Be Configured Directly

The following command is syntactically valid:

~~~bash
codex exec \
  --model anthropic/claude-opus-5 \
  --skip-git-repo-check \
  'Reply only with: OK'
~~~

But Codex still sends Responses. If the gateway only has an Anthropic Messages upstream configured for that model, the common response is:

~~~text
GATEWAY_NO_UPSTREAM_CANDIDATES
path=/v1/responses
protocol=open_ai
~~~

### 11.2 Two Solution Directions

Direction 1: The gateway provides a Responses compatibility layer.

~~~text
Codex Responses
→ Gateway protocol conversion
→ Anthropic Messages
→ Claude
~~~

Direction 2: Use a local protocol conversion tool like CC Switch.

~~~text
Codex Responses
→ Local CC Switch
→ Anthropic Messages
→ AI Gateway
→ Claude
~~~

### 11.3 Codex Still Configures Responses When Using a Conversion Layer

Even when going through CC Switch, the Codex side should maintain:

~~~toml
wire_api = "responses"
~~~

What changes is the `base_url` pointing to a local proxy, for example:

~~~text
<http://127.0.0.1:15721/v1>
~~~

The local proxy converts Responses to Anthropic Messages, then converts the Anthropic response back into Responses that Codex can understand.

### 11.4 CC Switch Does Not Mean Models Are Automatically Available

A protocol conversion layer cannot resolve:

- Token has no permissions;
- Model ID does not exist;
- Anthropic upstream returns 5xx;
- Model is rate-limited;
- Upstream context or thinking budget exceeded;
- Tool calls cannot be mapped correctly;
- Incompatibility with images, files, caching, search, and other capabilities.

### 11.5 Advanced Capabilities After Conversion Must Be Validated Individually

After text returns successfully, validate separately:

- Streaming conversion between Responses SSE and Anthropic SSE;
- Mapping between function call and `tool_use/tool_result`;
- System messages and multi-turn context;
- Reasoning/thinking content;
- Image and file inputs;
- Web Search;
- Prompt Cache;
- Interruption, retry, and error code conversion.

Only after the conversion layer has been validated for the same scenario can you determine whether Claude is suitable for the corresponding Codex workflow.

### 11.6 CC Switch May Overwrite Codex Configuration

Back up before using "take over Codex":

~~~bash
cp "$HOME/.codex/config.toml" \
  "$HOME/.codex/config.toml.before-cc-switch.$(date +%Y%m%d-%H%M%S)"
~~~

After takeover, check again:

~~~bash
rg -n '^(model|model_provider|base_url|wire_api|env_key)' \
  "$HOME/.codex/config.toml"
~~~

Pay particular attention to whether the Base URL now points to the local proxy, whether the proxy is running, and whether the original configuration needs to be restored after stopping the proxy.

---

## 12. Reasoning Effort Level, Model Metadata, and Output Limits

### 12.1 Valid Values for `model_reasoning_effort`

The current Codex configuration reference lists:

~~~text
minimal
low
medium
high
xhigh
~~~

However, whether `xhigh` is available depends on the model. The config field allowing it does not mean the upstream model will accept it.

### 12.2 Reasoning Parameters for Third-Party Models

Different vendors and models may map reasoning effort differently. Some models at `high` or `xhigh` will reject the thinking budget, or return only reasoning without final text.

It is recommended to first use `medium` to complete text validation, then gradually increase the level based on the model's API documentation. When `thinking_budget`, incomplete output, or missing final text occurs, lower the effort level and increase the output budget first.

### 12.3 Unknown Model Metadata Warning

Third-party models may show:

~~~text
Unknown model ... is used.
This will use fallback model metadata.
~~~

This means Codex's built-in catalog does not have a full capability description for this model, so fallback values will be used.

Potential impacts:

- Context window estimation;
- Reasoning support determination;
- Verbosity support determination;
- Tool and multimodal capability declarations;
- Token truncation and compression strategy.

This warning by itself does not equal a call failure, but its long-term impact should not be ignored.

### 12.4 Do Not Guess the Context Window

Codex supports manual configuration like:

~~~toml
model_context_window = 128000
~~~

This should only be set after obtaining an accurate value from the gateway or upstream. Setting it larger than the actual value may cause the upstream to reject the request; setting it too small will cause Codex to compress the context too early.

### 12.5 HTTP 200 but No Final Text

In Responses, reasoning items may appear first. If the output budget is insufficient, there may be no `output_text`.

Troubleshoot:

1. Increase `max_output_tokens`;
2. Check `status` and `incomplete_details`;
3. Check if there is only reasoning content;
4. Re-validate using an actual Codex request;
5. Do not only check the HTTP status code.

### 12.6 Capabilities That Cannot Be Inferred from a Single Text Call

The following capabilities cannot be directly inferred from a single text call:

- Long-context stability;
- Image inputs;
- Web Search;
- MCP tools;
- Multi-turn function calls;
- JSON Schema output;
- Prompt Cache;
- Responses WebSocket;
- Disconnect recovery in very long tasks.

Before using these capabilities, validate them one by one per Section 9.5. Do not treat a single successful text call as proof of full feature compatibility.

---

## 13. Sandbox and Approval Restrictions

### 13.1 Model Connectivity and File Permissions Are Two Different Things

AI Gateway handles model requests; the Codex sandbox handles local commands and file operations generated by the model.

When "the model can respond but cannot modify files," check the sandbox — do not suspect the API Key first.

### 13.2 Three Sandbox Modes

| Mode | Primary Behavior | Recommended Use |
|---|---|---|
| `read-only` | Read files only; cannot modify the project normally | Connectivity testing, code review |
| `workspace-write` | Can write to the workspace; some sensitive paths are still protected | Recommended for daily development |
| `danger-full-access` | File system is basically not restricted by the Codex sandbox | Only for environments with external isolation already in place |

Recommended defaults:

~~~toml
sandbox_mode = "workspace-write"
approval_policy = "on-request"
~~~

### 13.3 Approval Policies

| Policy | Meaning |
|---|---|
| `untrusted` | Only trusted commands run directly; others require approval |
| `on-request` | Codex requests approval based on operation risk |
| `never` | No approval requests; failures are returned directly to the model |

`approval_policy` determines when to ask; `sandbox_mode` determines what commands can access. The two are independent of each other.

### 13.4 Risks of `danger-full-access`

Do not use the following as a default configuration:

~~~toml
sandbox_mode = "danger-full-access"
approval_policy = "never"
~~~

This combination allows the model to perform extensive local operations without human approval.

Also do not casually use on a regular computer:

~~~text
--dangerously-bypass-approvals-and-sandbox
~~~

### 13.5 Network Restrictions in workspace-write

Codex accessing the model provider and model-generated shell commands accessing the external network are not entirely the same layer.

In `workspace-write`, the default network access for shell tools may be restricted. When you need to allow tool commands to access the external network, you can configure the following after confirming the risks:

~~~toml
[sandbox_workspace_write]
network_access = true
~~~

Do not blindly open tool networking just to make the model API connect. Check `codex doctor`'s provider reachability first.

### 13.6 Protect API Keys from Entering Child Processes

The Codex provider needs to read `CLICKZETTA_API_KEY` from the parent process, but shell commands generated by the model typically do not need to see that variable.

Consider using shell environment filtering:

~~~toml
[shell_environment_policy]
inherit = "core"
ignore_default_excludes = false

[shell_environment_policy.filters]
"CLICKZETTA_API_KEY" = "exclude"
~~~

After this change, run `codex doctor` and an actual model request again to confirm provider authentication is still working.

---

## 14. Using Profiles to Manage Multiple Configurations

### 14.1 Why Use Profiles

When using official OpenAI, a gateway, and a local model at the same time, it is not recommended to frequently overwrite the same `config.toml`.

You can keep shared providers in:

~~~text
~/.codex/config.toml
~~~

And create:

~~~text
~/.codex/clickzetta.config.toml
~~~

### 14.2 Profile Example

Keep the provider in `~/.codex/config.toml`:

~~~toml
[model_providers.clickzetta]
name = "Singdata AI Gateway"
base_url = "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1"
env_key = "CLICKZETTA_API_KEY"
wire_api = "responses"
~~~

Write the selection to `~/.codex/clickzetta.config.toml`:

~~~toml
model_provider = "clickzetta"
model = "YOUR_MODEL_ID"
model_reasoning_effort = "medium"
model_verbosity = "low"
~~~

Start interactive mode:

~~~bash
codex --profile clickzetta
~~~

Non-interactive mode:

~~~bash
codex exec --profile clickzetta \
  --skip-git-repo-check \
  'Reply only with: OK'
~~~

### 14.3 Profiles Cannot Switch the Wire Protocol

Profiles can switch the provider, model, and reasoning effort level, but the wire protocol for Codex custom providers can only be Responses.

A profile is not an Anthropic protocol switch.

---

## 15. Troubleshooting

### 15.1 `codex: command not found`

Run:

~~~bash
type -a codex
echo "$PATH"
~~~

If just installed, close and reopen Terminal. If still not found, re-run the official install steps and check the PATH shown in the installer output.

### 15.2 Different Versions in Two Terminals

Run:

~~~bash
type -a codex
codex --version
~~~

Terminal uses the version listed first in PATH. The desktop app's bundled CLI and the standalone CLI may not be the same version.

### 15.3 `unexpected argument`

First run:

~~~bash
codex --help
codex exec --help
~~~

In the current version, `--ask-for-approval` goes before `exec`:

~~~bash
codex --ask-for-approval never exec ...
~~~

### 15.4 Configuration Fields Not Taking Effect

Key things to check:

1. Whether top-level fields are written before the first `[table name]`;
2. Whether they were accidentally written inside a `[projects."..."]` table;
3. Whether provider is set in the project `.codex/config.toml`;
4. Whether the provider table is defined twice;
5. Whether a different Codex CLI binary is running;
6. Whether it is being temporarily overridden by `--profile` or `-c`.

Run:

~~~bash
codex --strict-config doctor --summary --no-color --ascii
~~~

### 15.5 API Key Environment Variable Not Set

Run:

~~~bash
if [ -n "${CLICKZETTA_API_KEY:-}" ]; then
  echo "Loaded"
else
  echo "Not loaded"
fi
~~~

If not loaded, re-run Section 3.3. Do not print the real token.

### 15.6 HTTP 401/403

Possible causes:

- Token is incorrect or expired;
- `Authorization: Bearer` header is missing;
- Token does not have model permissions;
- Request went to the wrong environment;
- Base URL corresponds to a different gateway.

First validate authentication with the `/models` request from Section 4.

### 15.7 `No upstream candidates`

Common causes:

- Target model has no Responses upstream;
- Model ID is incorrect;
- API Key/tenant does not have that route;
- A model that only supports Chat or Anthropic was given to Codex;
- Upstream has been taken offline.

If a DeepSeek, Claude, or other vendor model only succeeds on Chat or Anthropic routes, this is a protocol routing mismatch — it cannot be resolved by reinstalling Codex.

### 15.8 HTTP 502 `[G2] Upstream failed`

The gateway recognized the model but the upstream request failed.

Handling steps:

1. Record the model ID, protocol, time, and request ID;
2. Wait and retry;
3. Compare with a bare `/responses` curl;
4. Check if Codex automatically retried and succeeded;
5. If failures persist, contact the AI Gateway support team.

If the same model consistently returns 502, treat it as an upstream failure first. Do not consider it stably available just because a single retry succeeded.

### 15.9 `stream disconnected` / `Reconnecting`

When Codex Responses uses streaming by default, the network or upstream may disconnect midway. Codex will automatically retry based on `stream_max_retries`.

Whether to consider it a success depends on:

~~~text
Whether it ultimately completed
Whether the final exit code is 0
Whether final text was received
~~~

A single `Reconnecting` followed by success can be recorded as "succeeded with retry." Persistent retry failures cannot be considered available.

### 15.10 `thinking_budget` Parameter Error

Lower the reasoning effort level to `medium` or below:

~~~bash
codex exec \
  --model YOUR_MODEL_ID \
  --skip-git-repo-check \
  -c 'model_reasoning_effort="medium"' \
  'Reply only with: OK'
~~~

### 15.11 `Unknown model ... fallback metadata`

This means Codex does not have built-in metadata for the third-party model.

If the request still returns successfully, you can continue with basic text testing, but validate context, reasoning, tools, and multimodal capabilities separately.

### 15.12 `model_verbosity is set but ignored`

The current model does not support or has not declared verbosity capability.

You can:

- Ignore the warning and continue testing;
- Temporarily remove `model_verbosity`;
- Create separate profiles for different models.

### 15.13 MCP 403 or Plugin Warnings

MCP, the plugin directory, and the model provider are different chains.

If the model has returned OK but there are then warnings about MCP shutdown, plugin manifest issues, or ChatGPT remote directory warnings, do not misidentify them as model failures.

Record separately when troubleshooting:

~~~text
Model request result
MCP startup result
Plugin loading result
~~~

You may also see the following prompts that do not directly equal model failure:

~~~text
remote plugin bundle sync failed
OutputTextDelta without active item
~~~

`remote plugin bundle sync failed` is common when the local machine has remote plugins that require official ChatGPT login to sync, while the current session uses a Gateway API Key. `OutputTextDelta without active item` may come from streaming event conversion or parsing. If the correct `provider`, model, and final text are still displayed with an exit code of 0, record the warning and monitor it. If it persistently causes missing characters, no final text, or non-zero exit codes, then submit sanitized logs as a streaming compatibility issue.

### 15.14 Cannot Execute in Non-Git Directory

Add this to the minimal test:

~~~text
--skip-git-repo-check
~~~

For production projects, it is recommended to run inside a Git repository so that model changes can be reviewed and reverted.

### 15.15 `doctor` Shows Fail at the End

Do not only look at the final count. Expand to see specific groups:

~~~bash
codex doctor --all --no-color --ascii
~~~

As long as `Configuration`, `auth`, and provider `Connectivity` are normal, Terminal, history thread, MCP, or plugin warnings do not necessarily block model requests.

Do not use only `doctor`'s exit code in scripts to determine whether the Gateway is configured successfully. The final step should be the read-only `codex exec` from Section 8: only when provider/model is correct, final text is received, and exit code is 0 can you confirm the basic model chain is working.

### 15.16 Need to Restore After Modifying Configuration

First view available backups:

~~~bash
ls -lt "$HOME/.codex"/config.toml*
~~~

Select the backup created before the modification and replace the placeholder text below:

~~~bash
cp "full path to backup file" "$HOME/.codex/config.toml"
chmod 600 "$HOME/.codex/config.toml"
~~~

Then reload the API Key and run again:

~~~bash
codex --strict-config doctor \
  --summary \
  --no-color \
  --ascii
~~~

When restoring, do not delete the entire `~/.codex` directory — doing so may simultaneously lose login status, session history, plugins, MCP, and project configurations.

---

## 16. API Key and Configuration Security

### 16.1 Files That Need Protection

Common sensitive files:

~~~text
~/.codex/auth.json
~/.codex/config.toml
~/.zshrc
CI/CD secret configuration
~~~

Even if `config.toml` does not contain a plain-text token, it still exposes the Base URL, provider, MCP, and local directory information.

### 16.2 Restrict File Permissions

Run:

~~~bash
chmod 600 "$HOME/.codex/config.toml"

if [ -f "$HOME/.codex/auth.json" ]; then
  chmod 600 "$HOME/.codex/auth.json"
fi
~~~

### 16.3 Things Not to Do

- Do not upload the entire `~/.codex` directory;
- Do not send `auth.json` to support;
- Do not run `echo "$CLICKZETTA_API_KEY"` in a public screen recording;
- Do not write real tokens in documentation examples;
- Do not commit API Keys to Git;
- Do not have multiple people share the same token;
- After a token leak, do not just delete the screenshot — revoke and regenerate it immediately.

### 16.4 Clean Up Temporary Variables After Testing

If this was only a temporary test:

~~~bash
unset CLICKZETTA_API_KEY
unset CLICKZETTA_BASE_URL
unset CLICKZETTA_MODEL
~~~

After cleanup, new Codex processes will be unable to obtain the token via `env_key` until the environment variables are set again.

### 16.5 Sanitize Error Information Before Sending Externally

Safe to send:

- Time;
- Model ID;
- HTTP status;
- Request ID;
- Protocol path;
- Sanitized error JSON.

Must remove:

- API Key;
- Authorization header;
- `x-api-key`;
- Contents of private local files;
- Tenant and personal information that should not be disclosed.

---

## 17. Contacting the AI Gateway Support Team

### 17.1 Complete These Three Self-Checks Before Contacting Support

Do not just send a screenshot of a Codex error. Completing the following checks will significantly reduce the time needed to identify the issue:

1. Use Section 4 to confirm the Base URL, API Key, and full model ID;
2. Use the standard `/responses` curl from Section 5 to reproduce the issue;
3. Use the read-only `codex exec` from Section 8 to compare curl and Codex results.

If the target is Claude or another model that only provides Anthropic Messages, also read Section 11 first to confirm whether an available Responses compatibility layer exists. Codex can still only send `/responses` requests to that compatibility layer.

### 17.2 What to Provide When Submitting an Issue

Please provide the following sanitized information:

~~~text
Operating system and Codex CLI version
Request protocol and path
Full model ID (excluding the token)
Error time and timezone
HTTP status code
Request ID (if available)
Whether /models is accessible with the same API Key
Whether the Section 5 Responses curl can be completed with the same model
~~~

Do not provide:

~~~text
API Key
Authorization header
x-api-key
auth.json
Complete configuration file
Local project source code or private files
~~~

### 17.3 What the Support Team Can Help Confirm

The AI Gateway support team can help confirm:

- Whether the API Key has permissions for the target model and protocol;
- Whether the specified endpoint has a corresponding upstream route;
- Whether the model ID requires a full prefix;
- Whether the gateway is returning 400, 401, 403, 429, or 5xx;
- Whether there are known parameter and reasoning budget restrictions.

Codex CLI version behavior, local network conditions, sandbox policies, third-party conversion layers, and advanced model capabilities need to be validated separately in your actual environment.

---

## 18. Completion Checklist

### 18.1 What You Can Actually Use After Setup Is Complete

Once all items in Section 18.2 are checked, you can use this in your project directory:

~~~bash
codex
~~~

To enter an interactive coding session, or use:

~~~bash
codex exec \
  --model YOUR_MODEL_ID \
  'Review the current project and tell me the next recommended steps'
~~~

To run non-interactive tasks.

Within the current sandbox and approval scope, Codex can:

- Read project files and understand code structure;
- Generate modifications based on user instructions;
- Write files to the permitted workspace;
- Run permitted local commands;
- Output modification results, test results, and error messages;
- Use `--model` or `/model` to switch to another supported model.

A successful configuration does not mean all models and advanced capabilities are automatically available. Whether Claude, DeepSeek, or other vendor models can be used depends on whether they have a Responses route. Web Search, MCP, tool calls, images, files, caching, and long context also need to be validated separately for actual use cases.

### 18.2 Final Success Checklist

Check each item before confirming Codex CLI onboarding is complete:

~~~text
[ ] curl and jq can be executed
[ ] command -v codex returns a path
[ ] codex --version returns a version
[ ] type -a codex confirmed no version confusion
[ ] Base URL is correct, /v1 is not duplicated
[ ] API Key is securely loaded and not exposed
[ ] provider uses env_key, no plain-text token
[ ] /models query succeeded
[ ] Model ID copied verbatim from the directory
[ ] Standard /responses curl returns HTTP 200
[ ] Final output_text exists in the Responses response
[ ] model_provider top-level field is in the correct position
[ ] [model_providers.clickzetta] is not defined twice
[ ] wire_api = "responses"
[ ] codex --strict-config doctor can load the configuration
[ ] doctor's config and auth are normal
[ ] doctor's provider reachability is normal
[ ] Did not judge failure based solely on doctor's final count or exit code
[ ] codex exec returns final text
[ ] codex exec shows provider: clickzetta
[ ] codex exec shows the expected full model ID
[ ] Codex process final exit code is 0
[ ] Reasoning effort level has been validated per model
[ ] Streaming retry results have been recorded
[ ] Sandbox and approval policy matches the actual use environment
[ ] Tool calls have been validated separately if they are needed
[ ] If an Anthropic model is chosen, confirmed a Responses compatibility layer exists
[ ] Error logs have been sanitized
[ ] Validation time and Codex CLI version have been recorded
~~~

Once all items are checked, you can confirm that Codex CLI has completed basic text onboarding. File modification, tool calls, and other advanced capabilities should still be validated separately as needed.

If only `/models` succeeded, the model cannot be considered available. If curl succeeded but Codex failed, focus on checking config file position, reasoning effort level, streaming response, model metadata, and the actual provider path.

---

## 19. References

When looking up configuration details, refer to the following official OpenAI documentation:

- [Codex CLI](https://developers.openai.com/codex/cli/)
- [Codex Authentication](https://developers.openai.com/codex/auth/)
- [Codex Config Basics](https://developers.openai.com/codex/config-basic/)
- [Codex Advanced Configuration](https://developers.openai.com/codex/config-advanced/)
- [Codex Configuration Reference](https://developers.openai.com/codex/config-reference/)
- [Codex CLI Reference](https://developers.openai.com/codex/cli/reference/)

Key restrictions confirmed by the official documentation:

1. User-level configuration is located at `~/.codex/config.toml`;
2. Custom providers can set Base URL, authentication source, and additional request headers;
3. The `wire_api` for custom providers currently only supports `responses`;
4. Project-level configuration cannot override machine-level provider and authentication settings;
5. Whether reasoning effort is available depends on the model;
6. Web Search and WebSocket capabilities for custom providers are not enabled by default;
7. API Key login and ChatGPT login have different feature scopes.

Model names in this guide are used only to illustrate model ID format and protocol evaluation methods. Actual configuration should be based on your API Key, the model directory provided by your AI Gateway, the target endpoint, and the Codex CLI version in use.
