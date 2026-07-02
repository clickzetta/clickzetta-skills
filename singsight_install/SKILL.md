# Singsight — Install Skill for AI Coding Agents

> **Note for the AI agent reading this file:**
> You are guiding a user through connecting their AI coding agent to **Singsight**, an AI Agent observability platform. After setup, every LLM call, tool execution, token usage, and session will appear in Singsight dashboards automatically via OpenTelemetry.
>
> Work through the steps **in order**. When a step says **ASK THE USER**, stop and ask — do not invent answers. Never echo the API key back to the user; it is sensitive.

---

## Step 1 — Identify the target agent

Determine which agent to instrument:

1. If the user named one explicitly, use that.
2. Else, auto-detect by the runtime you're answering from:
   - If `~/.claude/` exists → **Claude Code**
   - If `~/.hermes/hermes-agent/` exists → **Hermes Agent**
   - If `~/.openclaw/openclaw.json` exists → **OpenClaw**
   - If `~/.config/opencode/opencode.json` exists → **Opencode**
3. Else **ASK THE USER**: "Which agent should I instrument — Claude Code, Hermes Agent, OpenClaw, or Opencode?"

| Target | Status | Section |
|---|---|---|
| **Claude Code** | ✅ | Step 3 |
| **Hermes Agent** | ✅ | Step 4 |
| **OpenClaw** | ✅ | Step 5 |
| **Opencode** | ✅ | Step 6 |

---

## Step 2 — Get Singsight endpoint and API Key

> **Note:** If the target is **OpenClaw**, skip this step — Step 5 has its own guided prompts for API Key and endpoint.

You need two values:
- **Endpoint** — the OTel collector URL shown by the current Singsight project. Do not infer it from the web UI domain; hosted deployments may use a dedicated collector domain.
- **API Key** — created in the Singsight web UI (header name: `x-singsight-apikey`)

### 2a. Probe for existing config

Check if already configured in another agent:

```bash
# Check Claude Code
grep -o 'x-singsight-apikey=[^"]*' "$HOME/.claude/settings.json" 2>/dev/null | head -1

# Check Hermes
grep 'x-singsight-apikey' "$HOME/.hermes/.env" 2>/dev/null | head -1

# Check OpenClaw
python3 -c "
import json
try:
  cfg = json.load(open('$HOME/.openclaw/openclaw.json'))
  h = cfg.get('diagnostics',{}).get('otel',{}).get('headers',{})
  if 'x-singsight-apikey' in h: print(f'FOUND endpoint={cfg[\"diagnostics\"][\"otel\"][\"endpoint\"]}')
except: pass
" 2>/dev/null

# Check Opencode
grep 'x-singsight-apikey' "$HOME/.config/opencode/.env" 2>/dev/null | head -1
```

If found, **ASK THE USER**: "I found existing Singsight config for `<agent>`. Reuse the same endpoint and API Key for `<target>`?"

If reuse confirmed, store as `$ENDPOINT` and `$API_KEY` and skip to Step 3.

### 2b. If not found — proactively prompt the user

**You MUST actively tell the user where to get the values.** Say exactly this:

> I need your Singsight **Endpoint** and **API Key** to complete the setup.
>
> Please open your Singsight web UI and:
> 1. Go to **Settings → OTel Endpoint** or **Settings → Quick Start** tab — copy the **Endpoint** URL shown there
> 2. Go to **Settings → API Keys** tab — click **Create API Key** (the full key is shown only once, copy it immediately)
>
> Paste both values here. I won't echo the API key back.

**Wait for the user to respond.** Do NOT proceed until you have both values.

### 2c. Validate

- Endpoint: must start with `http://` or `https://`; use exactly the URL shown in Singsight Settings
- API Key: non-empty string (Singsight keys are opaque UUIDs)

> **Protocol:** Singsight collector only supports `http/protobuf` (OTLP over HTTP). All agents must use this protocol. Do NOT use gRPC (`:4317`). Set the explicit protocol variable whenever the target agent supports it.

Store as `$ENDPOINT` and `$API_KEY` for the following steps.

---

## Step 3 — Claude Code

Claude Code has built-in OpenTelemetry support. Configuration goes into `~/.claude/settings.json`.

### 3a. Check if already configured

```bash
if grep -q 'CLAUDE_CODE_ENABLE_TELEMETRY' "$HOME/.claude/settings.json" 2>/dev/null; then
  echo "ALREADY_CONFIGURED"
fi
```

If already configured, **ASK THE USER**: "Claude Code already has telemetry configured. Want me to update the endpoint/key, or skip?"

### 3b. Merge into settings.json

```bash
SETTINGS="$HOME/.claude/settings.json"
mkdir -p "$(dirname "$SETTINGS")"
[ -f "$SETTINGS" ] || echo '{}' > "$SETTINGS"
cp "$SETTINGS" "$SETTINGS.bak.$(date +%Y%m%d-%H%M%S)"

TMP=$(mktemp)
jq --arg endpoint "$ENDPOINT" --arg key "$API_KEY" '
  .env = (.env // {}) + {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "CLAUDE_CODE_ENHANCED_TELEMETRY_BETA": "1",
    "OTEL_METRICS_EXPORTER": "otlp",
    "OTEL_LOGS_EXPORTER": "otlp",
    "OTEL_TRACES_EXPORTER": "otlp",
    "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
    "OTEL_EXPORTER_OTLP_ENDPOINT": $endpoint,
    "OTEL_EXPORTER_OTLP_HEADERS": ("x-singsight-apikey=" + $key),
    "OTEL_LOG_TOOL_DETAILS": "1"
  }
' "$SETTINGS" > "$TMP" && mv "$TMP" "$SETTINGS"
chmod 600 "$SETTINGS"
```

If `jq` is not installed, **ASK THE USER** how to proceed: `brew install jq` (macOS) or `apt install jq` (Linux).

### 3c. Set user identity (recommended)

For the Users and Retention dashboards to work, set `enduser.id`:

```bash
SETTINGS="$HOME/.claude/settings.json"
TMP=$(mktemp)
jq --arg uid "$(whoami)" '
  .env["OTEL_RESOURCE_ATTRIBUTES"] = ("enduser.id=" + $uid)
' "$SETTINGS" > "$TMP" && mv "$TMP" "$SETTINGS"
```

### 3d. Verify

```bash
python3 -c "
import json
cfg = json.load(open('$HOME/.claude/settings.json'))
env = cfg.get('env', {})
assert env.get('CLAUDE_CODE_ENABLE_TELEMETRY') == '1', 'telemetry not enabled'
assert env.get('OTEL_TRACES_EXPORTER') == 'otlp', 'traces not enabled'
assert 'x-singsight-apikey=' in env.get('OTEL_EXPORTER_OTLP_HEADERS', ''), 'API key missing'
print('✅ Claude Code configured successfully')
print(f'   Endpoint: {env[\"OTEL_EXPORTER_OTLP_ENDPOINT\"]}')
print(f'   Traces: enabled (beta)')
print(f'   Metrics + Logs: enabled')
"
```

Tell the user:

> ✅ Singsight is configured for Claude Code.
>
> **No restart needed** — Claude Code reads settings.json on each session. Your next conversation will appear in the Singsight dashboards within ~5 minutes.
>
> What's being captured:
> - **Traces** (beta): populates Trace Explorer, Agent Performance, Latency, and Error dashboards
> - **Metrics**: populates Token Usage and Overview dashboards
> - **Logs/Events**: populates Users, tool call details
>
> Open the Singsight web UI and check Trace Explorer to see data flow in. Do not use the collector endpoint as the UI URL.

Skip to **Step 7**.

---

## Step 4 — Hermes Agent

Hermes uses the `hermes-plugin-otel-tracing` plugin which exports traces, metrics, and logs via OTLP.

### 4a. Verify Hermes is installed

```bash
command -v hermes >/dev/null 2>&1 || { echo "ERROR: hermes not found"; }
ls -d "$HOME/.hermes/hermes-agent" >/dev/null 2>&1 && echo "HERMES_OK"
```

If not found, tell the user to install Hermes first and STOP.

### 4b. Install the OTel plugin

```bash
pip install hermes-plugin-otel-tracing
```

### 4c. Configure environment

```bash
ENVFILE="$HOME/.hermes/.env"
touch "$ENVFILE"
cp "$ENVFILE" "$ENVFILE.bak.$(date +%Y%m%d-%H%M%S)"

python3 - "$ENVFILE" "$ENDPOINT" "$API_KEY" <<'PY'
import sys
path, endpoint, key = sys.argv[1:]
lines = [l for l in open(path).read().splitlines()
         if not l.startswith(("HERMES_OTEL_", "OTEL_EXPORTER_OTLP_", "OTEL_SERVICE_NAME="))]
if lines and lines[-1].strip():
    lines.append("")
lines.extend([
    "# Singsight observability",
    "HERMES_OTEL_ENABLED=true",
    "HERMES_OTEL_EXPORTER=otlp",
    f"OTEL_EXPORTER_OTLP_ENDPOINT={endpoint}",
    f'OTEL_EXPORTER_OTLP_HEADERS=x-singsight-apikey={key}',
    "OTEL_SERVICE_NAME=hermes-agent",
])
open(path, "w").write("\n".join(lines) + "\n")
print("✅ Hermes .env updated")
PY
chmod 600 "$ENVFILE"
```

### 4d. Restart gateway if running

```bash
if hermes gateway status 2>/dev/null | grep -q "loaded"; then
  hermes gateway restart
  echo "gateway restarted"
fi
```

### 4e. Verify

```bash
hermes chat -q "say hello" 2>&1 | tail -3
echo "✅ Hermes Agent configured. Check Singsight dashboards in ~5 minutes."
```

Tell the user:

> ✅ Singsight is configured for Hermes Agent.
>
> The OTel plugin auto-discovers via entry points. All traces, metrics, and logs are exported automatically on every turn.

Skip to **Step 7**.

---

## Step 5 — OpenClaw

OpenClaw has a built-in `diagnostics-otel` plugin that exports traces, metrics, and logs over OTLP.

### 5a. Verify OpenClaw is installed

```bash
command -v openclaw >/dev/null 2>&1 || { echo "ERROR: openclaw not found"; }
```

If not found, tell the user to install OpenClaw first and STOP.

### 5b. Install and enable the diagnostics-otel plugin

The plugin must be installed before it can be enabled:

```bash
openclaw plugins install @openclaw/diagnostics-otel
openclaw plugins enable diagnostics-otel
```

If `openclaw plugins install` fails (e.g. network issue), tell the user and STOP.

### 5c. Prompt user for API Key

**You MUST proactively ask the user to copy the API Key.** Say exactly this:

> **Step 1 of 2 — API Key**
>
> Please open Singsight web UI → **Settings → API Keys** tab, create a key (or copy an existing one), and paste it here.
>
> (The full key is shown only once after creation — copy it immediately. I won't echo it back.)

**Wait for the user to respond with the API Key.** Do NOT proceed until you have it. Store as `$API_KEY`.

### 5d. Prompt user for config snippet

Once you have the API Key, **ask the user to copy the config snippet.** Say exactly this:

> **Step 2 of 2 — Config snippet**
>
> Now open **Settings → Quick Start** tab, select **Openclaw → Config File**, and copy the JSON config shown there. Paste it here, or just confirm and I'll write the config using the endpoint shown on that page.
>
> Alternatively, tell me the Singsight endpoint URL shown in Settings and I'll generate the config.

**Wait for the user to respond.** They may paste the full config, or just give you the endpoint. Store endpoint as `$ENDPOINT`.

### 5e. Write config

Merge OTel config into `~/.openclaw/openclaw.json`:

```bash
CONFIG="$HOME/.openclaw/openclaw.json"
mkdir -p "$(dirname "$CONFIG")"
[ -f "$CONFIG" ] || echo '{}' > "$CONFIG"
cp "$CONFIG" "$CONFIG.bak.$(date +%Y%m%d-%H%M%S)"

TMP=$(mktemp)
python3 - "$CONFIG" "$ENDPOINT" "$API_KEY" <<'PY'
import json, sys
path, endpoint, key = sys.argv[1:]
cfg = json.load(open(path))
diag = cfg.setdefault("diagnostics", {})
diag["enabled"] = True
otel = diag.setdefault("otel", {})
otel.update({
    "enabled": True,
    "endpoint": endpoint,
    "protocol": "http/protobuf",
    "serviceName": "openclaw-gateway",
    "headers": {"x-singsight-apikey": key},
    "traces": True,
    "metrics": True,
    "logs": True,
    "captureContent": {
        "enabled": True,
        "inputMessages": True,
        "outputMessages": True,
        "toolInputs": True,
        "toolOutputs": True,
        "systemPrompt": True,
    },
})
plugins = cfg.setdefault("plugins", {})
allow = plugins.setdefault("allow", [])
if "diagnostics-otel" not in allow:
    allow.append("diagnostics-otel")
entries = plugins.setdefault("entries", {})
entries.setdefault("diagnostics-otel", {})["enabled"] = True
json.dump(cfg, open(path, "w"), indent=2)
print("✅ OpenClaw config updated")
PY
chmod 600 "$CONFIG"
```

### 5f. Restart gateway

```bash
openclaw gateway restart 2>/dev/null || echo "gateway not running (will pick up config on next start)"
```

### 5g. Verify

```bash
openclaw status 2>&1 | grep -i "diagnostics-otel"
openclaw health 2>&1 | head -3
```

If `openclaw status` shows `diagnostics-otel` as not installed or not loaded, the install in 5b may have failed — re-run `openclaw plugins install @openclaw/diagnostics-otel` and restart again.

Tell the user:

> ✅ Singsight is configured for OpenClaw.
>
> **What's uploaded:** diagnostic metadata (provider, model, duration, token counts, cost, tool names, status codes, error categories) **plus conversation content** (input/output messages, tool I/O, system prompts) via `captureContent`.
>
> To **disable** conversation content capture, remove the `captureContent` block from the config and restart.

Skip to **Step 7**.

---

## Step 6 — Opencode

Opencode requires the `@devtheops/opencode-plugin-otel` plugin to export telemetry — **it must be installed first** before any OTel data will be sent. Configure OTLP over HTTP explicitly, and set both the Opencode-specific header variable and the generic OTel header variable so different plugin versions can read the API key consistently.

### 6a. Install the plugin

Add to `~/.config/opencode/opencode.json`:

```bash
CONFIG="$HOME/.config/opencode/opencode.json"
mkdir -p "$(dirname "$CONFIG")"
[ -f "$CONFIG" ] || echo '{}' > "$CONFIG"
cp "$CONFIG" "$CONFIG.bak.$(date +%Y%m%d-%H%M%S)"

TMP=$(mktemp)
jq '.plugin = (.plugin // []) | if (.plugin | index("@devtheops/opencode-plugin-otel")) then . else .plugin += ["@devtheops/opencode-plugin-otel"] end' "$CONFIG" > "$TMP" && mv "$TMP" "$CONFIG"
```

### 6b. Configure environment

Create or update `~/.config/opencode/.env`:

```bash
ENVFILE="$HOME/.config/opencode/.env"
mkdir -p "$(dirname "$ENVFILE")"
touch "$ENVFILE"

python3 - "$ENVFILE" "$ENDPOINT" "$API_KEY" <<'PY'
import sys
path, endpoint, key = sys.argv[1:]
lines = [l for l in open(path).read().splitlines()
         if not l.startswith(("OPENCODE_ENABLE_TELEMETRY=", "OPENCODE_OTLP_", "OTEL_EXPORTER_OTLP_HEADERS="))]
if lines and lines[-1].strip():
    lines.append("")
lines.extend([
    "# Singsight observability",
    "OPENCODE_ENABLE_TELEMETRY=1",
    f"OPENCODE_OTLP_ENDPOINT={endpoint}",
    "OPENCODE_OTLP_PROTOCOL=http/protobuf",
    f"OPENCODE_OTLP_HEADERS=x-singsight-apikey={key}",
    f"OTEL_EXPORTER_OTLP_HEADERS=x-singsight-apikey={key}",
])
open(path, "w").write("\n".join(lines) + "\n")
print("✅ Opencode env updated")
PY
chmod 600 "$ENVFILE"
```

### 6c. Verify

```bash
echo "✅ Opencode configured. Run 'opencode' and check Singsight dashboards in ~5 minutes."
```

Tell the user:

> ✅ Singsight is configured for Opencode.
>
> The plugin exports traces, metrics, and logs automatically on every session.

---

## Step 7 — Verify data in Singsight

> **Important — Restart required for most agents:**
> Hermes, OpenClaw, and Opencode only load OTel plugin configuration at process startup. Enabling telemetry or changing OTel environment variables will **not** take effect in an already-running session. After completing setup, you must **start a new process** (or restart the gateway/CLI) before traces will appear in Singsight. Claude Code is the exception — it re-reads `settings.json` on each new session automatically.
>
> A good verification pattern: start a fresh session (e.g. `hermes chat -q "hello"`), then search Singsight Trace Explorer by the new session's timestamp.

After the user runs their agent for at least one turn, optionally verify that the collector endpoint is reachable:

```bash
# Check if the endpoint exposes the health endpoint in this deployment
curl -sS -o /dev/null -w "%{http_code}" "$ENDPOINT/actuator/health"
# Expect: 200
```

Tell the user:

> Your agent is now connected to Singsight. After your next conversation:
>
> 1. Open the Singsight web UI for the current project
> 2. Go to **Trace Explorer** — you should see traces appear within ~5 minutes
> 3. **Overview** dashboard will populate as data accumulates
>
> If no data appears after 5 minutes:
> - Check that your agent actually ran (at least one LLM call)
> - Make sure you **started a new session** after setup (Hermes/OpenClaw/Opencode do not hot-reload OTel config)
> - Verify the endpoint is reachable from your machine
> - Check the API key is valid (Settings → API Keys in Singsight UI)

---

## Step 8 — Report what changed

Summarize for the user (never echo the API key):

**Claude Code:**
- `~/.claude/settings.json`: added `env` block with OTel + telemetry variables
- Signals: traces (beta) + metrics + logs
- No restart needed

**Hermes Agent:**
- `~/.hermes/.env`: added OTLP exporter variables
- Installed: `hermes-plugin-otel-tracing`
- Signals: traces + metrics + logs
- Gateway restarted if running

**OpenClaw:**
- `~/.openclaw/openclaw.json`: enabled `diagnostics-otel` plugin with endpoint/key
- Signals: traces + metrics + logs
- Gateway restarted if running

**Opencode:**
- `~/.config/opencode/opencode.json`: added OTel plugin
- `~/.config/opencode/.env`: added OTLP endpoint/key
- Signals: traces + metrics + logs

End with: "Your API key is stored in the config file listed above. Keep it readable only by you (`chmod 600`)."