# AI Gateway Model Management: cz-cli Command Line Operations

AI Gateway model management is typically handled through the Studio UI, but cz-cli provides a corresponding command-line interface — for creating and configuring virtual Keys, browsing available models, and registering them as cz-cli Agent LLMs. It is well suited for automation scripts and CI/CD pipelines, as well as quickly querying model lists from the terminal.

---

## Commands Overview

| Command | Purpose |
|------|------|
| `cz-cli ai-gateway key list` | List all virtual Keys |
| `cz-cli ai-gateway key create` | Create a virtual Key |
| `cz-cli ai-gateway key upsert` | Create or update a Key (idempotent, recommended) |
| `cz-cli ai-gateway key get` | Retrieve the full Key value |
| `cz-cli ai-gateway key enable/disable` | Enable or disable a Key |
| `cz-cli ai-gateway key delete` | Delete a Key |
| `cz-cli ai-gateway key set-quota` | Set the token quota for a Key |
| `cz-cli ai-gateway model list` | View models accessible with a Key |
| `cz-cli agent llm add ... --provider clickzetta` | Register a Key as an Agent LLM |

---

## Managing Virtual Keys

### List Existing Keys

```bash
cz-cli ai-gateway key list
```

```json
{
  "data": [
    {
      "id": 716,
      "alias": "qiliang",
      "vApiKey": "50db****7f61",
      "status": 1
    }
  ],
  "count": 1,
  "ai_message": "Page 1, showing 1 of 1 virtual keys."
}
```

| Field | Description |
|------|------|
| `id` | Unique ID of the Key |
| `alias` | Key alias, specified at creation time |
| `vApiKey` | Key value, shown masked (first 4 + last 4 characters). The full value is required for all subsequent operations; the masked value and alias cannot be used |
| `status` | 1 = enabled, 0 = disabled |

### Create a Key

```bash
cz-cli ai-gateway key create my_key
```

```json
{
  "data": {
    "id": 736,
    "alias": "my_key",
    "vApiKey": "c081****dae5"
  },
  "ai_message": "Virtual key created. To use it with the agent run: cz-cli agent llm add my_key --provider clickzetta --api-key <vApiKey> --base-url https://... --use"
}
```

> **Note**: `vApiKey` is only returned in full when `key create` is called. In `key list` it is displayed masked (e.g., `a12f****950c`). All subsequent operations (`get`, `disable`, `enable`, `delete`, `set-quota`, `model list`) require the **full vApiKey** — the alias and masked value cannot be used. Save the full Key immediately after creation.

### Create or Update a Key (upsert, recommended)

`upsert` is idempotent — if the Key already exists it updates the configuration, if it does not exist it creates one. Suitable for repeated execution in scripts:

```bash
# Basic creation
cz-cli ai-gateway key upsert prod_key \
  --quota 1000000 --period monthly

# Create and immediately register as an Agent LLM (skip manual add)
cz-cli ai-gateway key upsert my_agent \
  --quota 500000 --period daily \
  --add-to-llm --use
```

**upsert parameter descriptions:**

| Parameter | Description |
|------|------|
| `--quota` | Token quota value |
| `--period` | Quota period: `daily` / `weekly` / `monthly` / `total` (long-term) |
| `--route-type` | Routing rule: `default` (built-in models) / `provider` (specific provider) / `byok` (bring your own key) |
| `--providers` | Specify provider IDs (used when `route-type=provider`) |
| `--provider-sort` | Sorting strategy (used when `route-type=default`): `price` / `throughput` / `latency` |
| `--private-keys` | List of BYOK Key aliases (used when `route-type=byok`) |
| `--add-to-llm` | Automatically register as `[llm.<name>]` in `~/.clickzetta/profiles.toml`, using alias as value |
| `--use` | Also set as the active LLM |

### Update Quota

```bash
cz-cli ai-gateway key set-quota \
  --key "<full vApiKey>" \
  --period daily \
  --quota 2000000
```

```json
{
  "data": {
    "id": 716,
    "period": "daily",
    "quota": 2000000
  }
}
```

### Enable / Disable / Delete

```bash
# Requires the full vApiKey; alias and masked values are not accepted
cz-cli ai-gateway key disable "<full vApiKey>"
cz-cli ai-gateway key enable "<full vApiKey>"
cz-cli ai-gateway key delete "<full vApiKey>"
```

| Operation | Output |
|------|------|
| disable | `{"data": {"id": 738, "status": 0}}` |
| enable | `{"data": {"id": 738, "status": 1}}` |
| delete | `{"data": {"id": 738, "deleted": true}}` |


---

## Browsing Available Models

```bash
cz-cli ai-gateway model list "<full vApiKey>"
```

> **Note**: Passing a masked value (e.g., `a12f****950c`) will silently return `{"data":[],"count":0}` without an error, which can make it appear as though no models are available. You must pass the full value obtained when `key create` was called.

The output is the list of models visible to that Key, in the following format (the actual response returns 42 models):

```json
{
  "data": [
    {"modelIdentifier": "qwen/qwen3.7-max",          "modelName": "Qwen3.7 Max"},
    {"modelIdentifier": "byteplus/dola-seed-2-0-pro", "modelName": "ByteDance Dola Seed 2.0 pro"},
    {"modelIdentifier": "minimax/MiniMax-M2.7",       "modelName": "MiniMax M2.7"},
    {"modelIdentifier": "openai/gpt-4.1",              "modelName": "GPT-4.1"},
    {"modelIdentifier": "deepseek/deepseek-v4-pro",    "modelName": "DeepSeek V4 Pro"}
  ],
  "count": 42
}
```

| Field | Description |
|------|------|
| `modelIdentifier` | Unique model identifier, e.g., `deepseek/deepseek-v4-pro`, used in `AI_COMPLETE()` |
| `modelName` | Display name of the model, e.g., `DeepSeek V4 Pro` |
| `modelInvokeStatus` | 1 = callable |

The model identifier format is `<provider>/<model-name>`, which is the full name used in AI_COMPLETE calls.

---

## Registering as an Agent LLM

The built-in AI Agent in cz-cli requires an LLM backend. A virtual Key from AI Gateway can be used as the Agent LLM.

### Option 1: Complete in One Step with upsert

```bash
cz-cli ai-gateway key upsert my_agent \
  --quota 500000 --period daily \
  --add-to-llm --use
```

```json
{
  "data": {
    "id": 737,
    "alias": "demo-key",
    "vApiKey": "ed42****f942"
  }
}
```

`--add-to-llm` writes the Key into the `[llm.my_agent]` section of `~/.clickzetta/profiles.toml`, and `--use` sets it as the default LLM.

### Option 2: Manual Registration

Retrieve the full Key value with `key get`, then add it manually:

```bash
cz-cli agent llm add my_agent \
  --provider clickzetta \
  --api-key "<full virtual Key>" \
  --base-url "https://cn-shanghai-alicloud-aimesh.api.clickzetta.com/gateway/v1" \
  --use
```

When provider is `clickzetta`, `--base-url` must be set to the AI Gateway Base URL.

AI Gateway Base URL by region:

| Region | Base URL |
|------|----------|
| Alibaba Cloud Shanghai | `https://cn-shanghai-alicloud-aimesh.api.clickzetta.com/gateway/v1` |
| Tencent Cloud Shanghai | `https://ap-shanghai-tencentcloud-aimesh.api.clickzetta.com/gateway/v1` |
| AWS Singapore | `https://ap-southeast-1-aws-aimesh.api.singdata.com/gateway/v1` |

### Test the Connection

```bash
cz-cli agent llm test my_agent
```

```json
{
  "data": {
    "message": "[llm.my_agent] test passed.",
    "name": "my_agent",
    "provider": "clickzetta",
    "url": "https://cn-shanghai-alicloud-aimesh.api.clickzetta.com/gateway/v1/chat/completions",
    "probe": "chat.completions",
    "source": "llm"
  }
}
```

### View and Switch LLMs

```bash
cz-cli agent llm show          # View all LLM configurations
cz-cli agent llm list          # List all [llm.*] entries
cz-cli agent llm use my_agent  # Switch active LLM
```

---

## Usage Examples

### Scenario: Bulk-create AI Gateway Keys for a Development Team

```bash
# Create a Key for each developer
for name in alice bob carol; do
  cz-cli ai-gateway key upsert "dev_${name}" \
    --quota 100000 --period daily \
    --route-type default --provider-sort price
done

# View all Keys
cz-cli ai-gateway key list
```

### Scenario: Query Models from a Specific Provider

```bash
# Get the Key and view available models
cz-cli ai-gateway model list "<full vApiKey>"

# Filter for DeepSeek provider models
cz-cli ai-gateway model list "<full vApiKey>" --format json | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
for m in data['data']:
    if m['modelIdentifier'].startswith('deepseek'):
        print(m['modelIdentifier'], m['modelName'])
"
```

### Scenario: Register an Agent LLM and Switch to It

```bash
# Complete in one step
cz-cli ai-gateway key upsert agent_prod \
  --quota 5000000 --period monthly \
  --add-to-llm --use

# Verify
cz-cli agent llm test agent_prod
```

---

## Notes

| Note | Description |
|--------|------|
| **vApiKey security** | `key list` returns a masked value; `key get` returns the full value. Do not write the full Key into logs or commit it to git |
| **Key naming** | Use `alias` to indicate purpose: `dev_alice`, `prod_agent`, `staging_test` |
| **Quota takes effect immediately** | Quota changes apply right away without restarting any service |
| **model list output** | When the output is large, use `--format json` and pipe for filtering |
| **clickzetta provider** | Requires both `--api-key` and `--base-url`; neither can be omitted. Alternatively, use `--add-to-llm` during upsert for automatic injection |
| **provider options** | `agent llm add` supports `clickzetta` / `openai` / `openai-compatible` / `anthropic` / `bedrock` / `google` / `azure` / `openrouter` |

---

## Related Documentation

- [AI Gateway Quick Start](quickstart.md) — Creating API Keys and routing policies in Studio
- [AI Gateway Product Introduction](introduction.md) — Endpoint management, quotas, monitoring
- [AI Gateway in Practice: Calling LLMs with SQL](lakehouse-ai-sql-analysis.md) — AI_COMPLETE text mode
- [Analyzing Images in SQL](lakehouse-multimodal-ai-pipeline.md) — AI_COMPLETE image mode
- [cz-cli Installation and Setup Guide](setup_cz_cli.md) — Setting up the cz-cli environment
