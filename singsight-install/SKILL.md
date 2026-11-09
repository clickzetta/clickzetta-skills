---
name: singsight-install
description: |
  Guide users to connect their AI coding agents (Codex, Claude Code, Hermes Agent, OpenClaw, Opencode)
  to the Singsight AI Agent observability platform. Configure OpenTelemetry and verify
  the sessions, calls and usage supported by the selected agent.
  Triggered when the user says "connect Singsight", "install Singsight", "configure Singsight",
  "Agent observability", "OTel integration", "report token usage", "monitor AI Agent", "singsight install".
  Keywords: singsight, install, observability, opentelemetry, otel, agent telemetry, codex, claude code, hermes, openclaw, opencode
---

# Singsight — Install Skill for AI Coding Agents

> **Note for the AI agent reading this file:**
> You are guiding a user through connecting their AI coding agent to **Singsight**, an AI Agent observability platform. Use the selected agent’s verification steps to check which signals actually appear in the project.
>
> Work through the steps **in order**. When a step says **ASK THE USER**, stop and ask — do not invent answers. Never echo the API key back to the user; it is sensitive.

---

## Step 1 — Identify the target agent

Determine which agent to instrument:

1. If the user named one explicitly, use that. For **Codex**, go to **Step 6D** directly; it collects its own credentials and verifies dashboard metrics. Do not probe another agent’s secrets.
2. Else, auto-detect by the runtime you're answering from:
   - If running inside Codex (e.g. `CODEX_THREAD_ID` is set) → **Codex**, Step 6D
   - If `~/.claude/` exists → **Claude Code**
   - If `~/.hermes/hermes-agent/` exists → **Hermes Agent**
   - If `~/.openclaw/openclaw.json` exists → **OpenClaw**
   - If `~/.config/opencode/opencode.json` exists → **Opencode**
3. Else **ASK THE USER**: "Which agent should I instrument — Codex, Claude Code, Hermes Agent, OpenClaw, or Opencode?"

| Target | Status | Section |
|---|---|---|
| **Codex** | ✅ (macOS; CLI verified) | Step 6D |
| **Claude Code** | ✅ | Step 3 |
| **Hermes Agent** | ✅ | Step 4 |
| **OpenClaw** | ✅ | Step 5 |
| **Opencode** | ✅ | Step 6 |

---

## Step 2 — Get Singsight endpoint and API Key

> **Note:** If the target is **OpenClaw**, skip this step — Step 5 has its own guided prompts for API Key and endpoint.
>
> **Endpoint format:** store the collector **base URL** in `$ENDPOINT` (e.g. `https://collector.example.com`) with no `/v1/traces` suffix and no trailing slash. Every agent below appends the signal path itself.

You need two values:
- **Endpoint** — the OTel collector URL shown by the current Singsight project. Do not infer it from the web UI domain; hosted deployments may use a dedicated collector domain.
- **API Key** — an **Ingest** type key created in the Singsight web UI (header name: `x-singsight-apikey`). Access-type keys are for the OpenAPI and will be rejected for ingestion.

### 2a. Probe for existing config

Check if already configured in another agent:

```bash
# Check Claude Code (cc-genai-hook)
python3 -c "
import json, os
p=os.path.expanduser('~/.claude/genai-hook.json')
try:
  c=json.load(open(p)); e=c.get('exporter',{})
  if e.get('headers'): print('FOUND endpoint=' + str(e.get('endpoint')))
except Exception: pass
" 2>/dev/null

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

# Check Opencode (config only — opencode does not read ~/.config/opencode/.env)
grep -o 'x-singsight-apikey=[^"]*' "$HOME/.config/opencode/opencode.json" 2>/dev/null | head -1
```

If found, **ASK THE USER**: "I found existing Singsight config for `<agent>`. Reuse the same endpoint and API Key for `<target>`?"

If reuse confirmed, store as `$ENDPOINT` and `$API_KEY` and skip to Step 3.

### 2b. If not found — proactively prompt the user

**You MUST actively tell the user where to get the values.** Say exactly this:

> I need your Singsight **Endpoint** and **API Key** to complete the setup.
>
> Please open your Singsight web UI and:
> 1. Go to **Settings → OTel Endpoint** or **Settings → Quick Start** tab — copy the **Endpoint** URL shown there
> 2. Go to **Settings → API Keys** tab → **Ingest Keys** sub-tab — click **Create Ingest Key** (the full key is shown only once, copy it immediately). Access Keys are for the OpenAPI and cannot be used for telemetry ingestion.
>
> Paste both values here. I won't echo the API key back.

**Wait for the user to respond.** Do NOT proceed until you have both values.

### 2c. Validate

- Endpoint: must start with `http://` or `https://`; use exactly the URL shown in Singsight Settings
- API Key: non-empty string (Singsight keys are opaque UUIDs)

> **Protocol:** Singsight collector only supports `http/protobuf` (OTLP over HTTP). All agents must use this protocol. Do NOT use gRPC (`:4317`). Set the explicit protocol variable whenever the target agent supports it.

Store as `$ENDPOINT` and `$API_KEY` for the following steps.

---

## Step 3 — Claude Code (cc-genai-hook)

Claude Code 使用 **cc-genai-hook** 接入 Singsight，不使用 Claude Code 原生 OTel
telemetry（`CLAUDE_CODE_ENABLE_TELEMETRY` / `OTEL_TRACES_EXPORTER` 那一套）。

cc-genai-hook 通过 Claude Code command hooks 读取 transcript，生成 gen_ai 语义的
`invoke_agent` / `chat` / `execute_tool` / `subagent` spans，再通过 OTLP
http/protobuf 发送到 Singsight。

> 如果当前环境已经有 `cc-genai-hook-install` skill，可以优先使用它完成安装和诊断；
> 否则按下面的步骤执行。

### 3a. 检查是否已经配置

```bash
python3 -c "
import json, os
p=os.path.expanduser('~/.claude/genai-hook.json')
try:
    c=json.load(open(p))
    e=c.get('exporter',{})
    print('FOUND endpoint=' + str(e.get('endpoint')))
    print('headers=' + ','.join((e.get('headers') or {}).keys()))
except FileNotFoundError:
    print('NOT_CONFIGURED')
except Exception as exc:
    print('CONFIG_ERROR', exc)
"
```

如果已有配置，**ASK THE USER**：

> 我发现 Claude Code 已经配置了 cc-genai-hook。要复用同一个 endpoint / API key，
> 还是更新为新的 Singsight 配置？

不要回显 API key。

### 3b. 安装 cc-genai-hook

先检查 CLI：

```bash
command -v cc-genai-hook && cc-genai-hook --version
```

如果没有，安装到稳定目录。**不要**把 venv 放到临时目录，因为 Claude Code hooks
会引用这个 Python。

```bash
CCGH_HOME="$HOME/.local/share/cc-genai-hook"
mkdir -p "$CCGH_HOME"

if [ -d "$CCGH_HOME/src/.git" ]; then
  git -C "$CCGH_HOME/src" pull --ff-only
else
  git clone https://github.com/clickzetta/cc-genai-hook.git "$CCGH_HOME/src"
fi

python3 -m venv "$CCGH_HOME/venv"
"$CCGH_HOME/venv/bin/pip" install -U pip setuptools wheel
"$CCGH_HOME/venv/bin/pip" install "$CCGH_HOME/src"
CCG="$CCGH_HOME/venv/bin/cc-genai-hook"
"$CCG" --version
```

如果 CLI 已经在 PATH 中：

```bash
CCG="$(command -v cc-genai-hook)"
```

### 3c. 安装 Singsight hooks

默认使用 **ordered 模式**：Stop 时统一解析 transcript，生成 chat / execute_tool /
subagent，保证顺序。

```bash
"$CCG" install \
  --mode command \
  --endpoint "$ENDPOINT" \
  --header "x-singsight-apikey=$API_KEY" \
  --user "$(whoami)"
```

如果用户提供的 endpoint 已经是完整 `/v1/traces` URL：

```bash
"$CCG" install \
  --mode command \
  --endpoint "$ENDPOINT" \
  --endpoint-kind full \
  --header "x-singsight-apikey=$API_KEY" \
  --user "$(whoami)"
```

可选 realtime 模式（工具 span 实时发送）：

```bash
"$CCG" install \
  --mode command \
  --tool-mode realtime \
  --endpoint "$ENDPOINT" \
  --header "x-singsight-apikey=$API_KEY" \
  --user "$(whoami)"
```

注意：

- ordered 是默认，也是推荐模式
- realtime 会额外注册 `PostToolUse` / `PostToolUseFailure`
- realtime 模式不展开 subagent 子树；subagent 只在 ordered 模式构建
- 当前不支持 `--mode sidecar`

### 3d. 安装器写入了什么

- `~/.claude/genai-hook.json`（权限 `0600`）
- 合并 `~/.claude/settings.json` hooks（自动备份）
- 默认 hooks：
  - `Stop`
  - `SessionEnd`
- realtime 模式额外：
  - `PostToolUse`
  - `PostToolUseFailure`

安装器**不会**写入：

- `CLAUDE_CODE_ENABLE_TELEMETRY`
- `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA`
- `OTEL_TRACES_EXPORTER`
- `OTEL_LOG_*`

### 3e. 验证

```bash
"$CCG" doctor
"$CCG" doctor --send-test
"$CCG" config show
```

预期：

- endpoint 是 Singsight collector + `/v1/traces`
- protocol 是 `http/protobuf`
- headers 只显示 `x-singsight-apikey` 这个名字，不显示值
- hooks 至少包含 `Stop` 和 `SessionEnd`
- `test span sent`

如果用户之前配置过 Claude Code 原生 OTel（旧版 Singsight Skill）：

1. 不要自动删除用户的原生设置。
2. **ASK THE USER** 是否保留。
3. 如果两边同时开启，会出现两套 trace，token / cost 可能重复统计。
4. 建议二选一。

告诉用户：

> ✅ Singsight 已通过 cc-genai-hook 接入 Claude Code。
>
> 不需要重启 Claude Code；hook 进程会在下一次会话/下一轮时读取配置。
> 完成一次新的对话或工具调用后，数据通常会在几分钟内出现在 Singsight。

Skip to **Step 7**.

## Step 4 — Hermes Agent

Hermes uses the `hermes-plugin-otel-tracing` plugin which exports traces, metrics, and logs via OTLP.

### 4a. Verify Hermes and locate its Python environment

Hermes ships in several layouts (Homebrew formula, `~/.hermes/hermes-agent/venv`, pipx). A bare
`pip install` usually lands in a different interpreter and the gateway then never sees the plugin, so
resolve the interpreter that actually runs Hermes before installing anything.

```bash
command -v hermes >/dev/null 2>&1 || { echo "ERROR: hermes not found"; }

HERMES_BIN="$(command -v hermes)"
# The launcher is a Python script; its shebang points at the interpreter Hermes runs under.
HERMES_PY="$(sed -n '1s/^#!//p' "$HERMES_BIN" | awk '{print $1}')"
[ -x "$HERMES_PY" ] || HERMES_PY="$HOME/.hermes/hermes-agent/venv/bin/python"
[ -x "$HERMES_PY" ] || { echo "ERROR: cannot locate the Python that runs Hermes"; }

echo "hermes: $HERMES_BIN"
echo "python: $HERMES_PY"
"$HERMES_PY" -c 'import sys; print("prefix:", sys.prefix)'
```

If neither path resolves, run `hermes --version` — it prints `Project:` and `Python:` — and use the
interpreter it reports. Never fall back to bare `pip`.

### 4b. Install the OTel plugin into that environment

```bash
"$HERMES_PY" -m pip install hermes-plugin-otel-tracing
```

Then confirm the entry point is visible to that same interpreter. Installing into the wrong
environment is the most common reason Hermes produces no telemetry at all:

```bash
"$HERMES_PY" - <<'PY'
from importlib.metadata import entry_points
eps = [e for e in entry_points(group="hermes_agent.plugins") if e.name == "otel_tracing"]
print("entry point:", eps[0].value if eps else "NOT FOUND — installed into the wrong environment")
PY
```

### 4c. Enable the plugin in `config.yaml`

Hermes *discovers* entry-point plugins but does **not** load them unless they are listed in
`plugins.enabled`. Skipping this step leaves the plugin installed and silent.

```bash
"$HERMES_PY" - "$HOME/.hermes/config.yaml" <<'PY'
import shutil, sys, datetime, os, yaml

path = sys.argv[1]
if os.path.exists(path):
    shutil.copy(path, f"{path}.bak.{datetime.datetime.now():%Y%m%d-%H%M%S}")
    cfg = yaml.safe_load(open(path)) or {}
else:
    cfg = {}

plugins = cfg.get("plugins") if isinstance(cfg.get("plugins"), dict) else {}
enabled = plugins.get("enabled") if isinstance(plugins.get("enabled"), list) else []

if "otel_tracing" in enabled:
    print("already enabled")
    raise SystemExit
if not plugins:
    # No plugins section yet — append text so the user's comments survive.
    with open(path, "a") as f:
        f.write("\nplugins:\n  enabled:\n    - otel_tracing\n")
else:
    enabled.append("otel_tracing")
    plugins["enabled"] = enabled
    cfg["plugins"] = plugins
    with open(path, "w") as f:
        yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False)
print("otel_tracing enabled")
PY
```

### 4d. Configure environment

Where the variables must go depends on how the gateway is started:

| How the gateway runs | Reads env from |
| --- | --- |
| macOS, started by launchd (`~/Library/LaunchAgents/ai.hermes.gateway.plist` exists) | `EnvironmentVariables` in that plist — **launchd does not read `.env`** |
| started by hand (`hermes gateway start`, `hermes chat`) | `~/.hermes/.env` |

Always write `~/.hermes/.env` (it covers direct CLI runs), and additionally write the plist when it
exists:

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
print("Hermes .env updated")
PY
chmod 600 "$ENVFILE"
```

```bash
PLIST="$HOME/Library/LaunchAgents/ai.hermes.gateway.plist"
if [ -f "$PLIST" ]; then
  cp "$PLIST" "$PLIST.bak.$(date +%Y%m%d-%H%M%S)"
  python3 - "$PLIST" "$ENDPOINT" "$API_KEY" <<'PY'
import plistlib, sys
path, endpoint, key = sys.argv[1:]
with open(path, "rb") as f:
    pl = plistlib.load(f)
env = pl.get("EnvironmentVariables") or {}
env.update({
    "HERMES_OTEL_ENABLED": "true",
    "HERMES_OTEL_EXPORTER": "otlp",
    "OTEL_EXPORTER_OTLP_ENDPOINT": endpoint,
    "OTEL_EXPORTER_OTLP_HEADERS": f"x-singsight-apikey={key}",
    "OTEL_SERVICE_NAME": "hermes-agent",
})
pl["EnvironmentVariables"] = env
with open(path, "wb") as f:
    plistlib.dump(pl, f)
print("launchd plist updated:", path)
PY
  chmod 600 "$PLIST"
else
  echo "no launchd plist — .env is enough"
fi
```

### 4e. Restart the gateway

A running gateway keeps its old environment; it must be restarted, not just reconfigured. Under
launchd, restarting is not enough either — `launchctl kickstart` reuses the cached job definition, so
the new `EnvironmentVariables` only take effect after the job is unloaded and loaded again from disk.

```bash
PLIST="$HOME/Library/LaunchAgents/ai.hermes.gateway.plist"
if [ -f "$PLIST" ]; then
  launchctl bootout "gui/$(id -u)/ai.hermes.gateway" 2>/dev/null
  launchctl bootstrap "gui/$(id -u)" "$PLIST" && echo "gateway reloaded from plist"
  launchctl print "gui/$(id -u)/ai.hermes.gateway" 2>/dev/null | grep -i "OTEL_EXPORTER_OTLP_ENDPOINT" \
    && echo "env visible to launchd" || echo "WARNING: env not visible — check the plist"
elif hermes gateway status 2>/dev/null | grep -q "loaded"; then
  hermes gateway restart && echo "gateway restarted"
fi
```

### 4f. Verify — in a new session

The plugin builds its span tree from the `on_session_start` hook, which fires only when a session is
created. Sessions that already existed before the install never emit traces — including the one you
may be talking to right now. Start a fresh session:

```bash
hermes chat -q "say hello" 2>&1 | tail -3
```

If a new session still produces nothing:

- `HERMES_OTEL_CAPTURE_CONTENT` defaults to `true`, which attaches messages, tool arguments and tool
  results to every span. Oversized spans can be dropped without an error — set
  `HERMES_OTEL_CAPTURE_CONTENT=false` and retry.
- Read the plugin's own log (override its path with `HERMES_OTEL_LOG_FILE`).
- Re-run the entry-point check from 4b using `$HERMES_PY`, and confirm `otel_tracing` is still in
  `plugins.enabled`.

Tell the user:

> Singsight is configured for Hermes Agent.
>
> The plugin is installed into the interpreter that runs Hermes, enabled in `~/.hermes/config.yaml`,
> and the gateway has been restarted. Traces only appear for sessions started after this setup — open
> a new session to see data.

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
> Please open Singsight web UI → **Settings → API Keys** tab → **Ingest Keys** sub-tab, create a key (or copy an existing one), and paste it here.
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

Opencode requires the `@devtheops/opencode-plugin-otel` plugin to export telemetry — **it must be installed first** before any OTel data will be sent.

> **Do NOT configure this through `~/.config/opencode/.env`.**
> Opencode does not load that file. It reads `opencode.json` / `opencode.jsonc` only, and the plugin reads settings from inline plugin options or from variables that are already in the process environment. A `.env` file next to the config is silently ignored, and the plugin logs `telemetry disabled (set OPENCODE_ENABLE_TELEMETRY to enable)`.
>
> Put everything in `opencode.json` using the **tuple form** (`["<package>", { options }]`) instead. That needs no shell export and no restart discipline beyond starting a new Opencode process.
>
> Inline options require **plugin ≥ 1.3.1**. Earlier versions ignore the options object entirely and fall back to env vars only. A plugin spec without a version (`@devtheops/opencode-plugin-otel`) may resolve from Opencode's package cache rather than npm, so it can install an older build even when a newer one is published — always pin an explicit version.

### 6a. Install the plugin

```bash
opencode plugin -g "@devtheops/opencode-plugin-otel@1.4.0" --force
```

This installs the package and adds it to `~/.config/opencode/opencode.json`. Confirm it landed:

```bash
opencode debug config | python3 -c "import json,sys; print(json.load(sys.stdin).get('plugin'))"
```

A project-level `opencode.json` **merges** with the global one, so a project config that lists other plugins does not remove this one.

### 6b. Configure the plugin in `opencode.json`

Write the endpoint, protocol, and API key as inline plugin options:

```bash
CONFIG="$HOME/.config/opencode/opencode.json"
mkdir -p "$(dirname "$CONFIG")"
[ -f "$CONFIG" ] && cp "$CONFIG" "$CONFIG.bak.$(date +%Y%m%d-%H%M%S)"

python3 - "$CONFIG" "$ENDPOINT" "$API_KEY" <<'PY'
import json, re, sys
path, endpoint, key = sys.argv[1:]

raw = open(path).read() if __import__("os").path.exists(path) else "{}"
# `opencode plugin` writes JSONC (comments + trailing commas) — strip both before parsing.
raw = re.sub(r"^\s*//.*$", "", raw, flags=re.M)
raw = re.sub(r"/\*.*?\*/", "", raw, flags=re.S)
raw = re.sub(r",(\s*[}\]])", r"\1", raw)
cfg = json.loads(raw or "{}")

PKG = "@devtheops/opencode-plugin-otel"
SPEC = f"{PKG}@1.4.0"
options = {
    "enabled": True,
    "endpoint": endpoint.rstrip("/"),   # base URL; plugin appends /v1/traces etc.
    "protocol": "http/protobuf",
    "otlpHeaders": f"x-singsight-apikey={key}",
}

def is_otel(entry):
    spec = entry if isinstance(entry, str) else entry[0]
    # strip any version suffix: "@scope/name@1.4.0" -> "@scope/name"
    return re.sub(r"(?<=.)@[^@/]*$", "", spec) == PKG

plugins = [p for p in cfg.get("plugin", []) if not is_otel(p)]
plugins.append([SPEC, options])
cfg["plugin"] = plugins
cfg.setdefault("$schema", "https://opencode.ai/config.json")

json.dump(cfg, open(path, "w"), indent=2)
print("✅ Opencode plugin options written (endpoint + protocol + API key)")
PY
chmod 600 "$CONFIG"
```

If a previous run of this skill created `~/.config/opencode/.env`, delete the Singsight lines from it so it cannot mislead later debugging:

```bash
ENVFILE="$HOME/.config/opencode/.env"
[ -f "$ENVFILE" ] && python3 - "$ENVFILE" <<'PY'
import sys
path = sys.argv[1]
keep = [l for l in open(path).read().splitlines()
        if not l.startswith(("OPENCODE_ENABLE_TELEMETRY=", "OPENCODE_OTLP_", "OTEL_EXPORTER_OTLP_HEADERS="))
        and l.strip() != "# Singsight observability"]
open(path, "w").write("\n".join(keep) + ("\n" if keep else ""))
print("cleaned stale Singsight vars from .env (opencode never read them)")
PY
```

### 6c. Verify the plugin actually starts up

Start a **new** Opencode process with logs on and check for the startup line:

```bash
opencode run --print-logs "hello" 2>&1 | grep -iE "telemetry|starting up"
```

Expected — telemetry on, with your endpoint and `version=1.4.0` or later:

```text
level=INFO message="starting up" version=1.4.0 endpoint=<your endpoint> protocol=http/protobuf ...
level=INFO message="OTel SDK initialized"
```

If you instead see:

```text
level=INFO message="telemetry disabled (set OPENCODE_ENABLE_TELEMETRY to enable)"
```

then the options were not applied. Check, in order:

1. `opencode debug config | python3 -c "import json,sys; print(json.load(sys.stdin).get('plugin'))"` — the entry must be a **two-element array** (`["@devtheops/...@1.4.0", {...}]`), not a bare string.
2. The version in that entry must be ≥ 1.3.1. A bare package name may resolve to a cached older build that ignores inline options — re-run 6a with `--force`.
3. `"enabled": true` must be present in the options object.

**Fallback if the plugin cannot be upgraded to ≥ 1.3.1**: inline options will not work, so the variables must be in the environment of the process that launches Opencode. Add them to the user's shell profile (not a `.env` file Opencode will never read) and have them open a new terminal:

```bash
# append to ~/.zshrc (or ~/.bashrc / ~/.config/fish/config.fish)
export OPENCODE_ENABLE_TELEMETRY=1
export OPENCODE_OTLP_ENDPOINT="$ENDPOINT"
export OPENCODE_OTLP_PROTOCOL=http/protobuf
export OPENCODE_OTLP_HEADERS="x-singsight-apikey=$API_KEY"
```

Then re-run the 6c check from a **new shell** — a shell that was already open will not have the variables.

Tell the user:

> ✅ Singsight is configured for Opencode.
>
> Everything lives in `~/.config/opencode/opencode.json` as inline plugin options — no `.env` file and no shell exports needed. Start a new Opencode session and the plugin exports traces, metrics, and logs automatically.
>
> Your API key is in that config file. Keep it out of version control (`chmod 600` is applied; do not commit `opencode.json` with the key in it). If you need the key elsewhere, use `"otlpHeaders": "{env:SINGSIGHT_OTEL_HEADERS}"` and export that variable from your shell profile instead.

---

## Step 6D — Codex

The Quick Start prompt works with just the agent name changed:

> 帮我给 Codex 接入 SingSight：OTLP endpoint 是 https://cn-shanghai-alicloud-otel.api.clickzetta.com，Ingest Key 我稍后提供。接入步骤见 https://raw.githubusercontent.com/clickzetta/clickzetta-skills/refs/heads/main/singsight-install/SKILL.md

Use the endpoint supplied by the user. Wait for the project's **Ingest Key** if missing; never print it. Follow [the Codex installation and verification steps](codex/README.md). When reading this file from a raw GitHub URL, resolve `codex/README.md` relative to that URL, using the same revision.

Codex's native OTLP exporter produces real traces even when Overview reports zero sessions and tokens. The bundled relay annotates native usage spans in place. Complete the real-turn reconciliation in the Codex guide **before reporting success**. A reachable endpoint, nonzero trace count, or successful configuration write is insufficient. If dashboard access is unavailable, report exactly which checks are still unverified. Proceed to Step 8.

## Step 7 — Verify data in Singsight

> **Important — Restart required for most agents:**
> Hermes, OpenClaw, and Opencode only load OTel plugin configuration at process startup. Enabling telemetry or changing OTel environment variables will **not** take effect in an already-running session. After completing setup, you must **start a new process** (or restart the gateway/CLI) before traces will appear in Singsight. Claude Code is the exception — cc-genai-hook reads `~/.claude/genai-hook.json` per hook process, so a new Claude Code session picks up the configuration.
>
> A good verification pattern: start a fresh session (e.g. `hermes chat -q "hello"`), then search Singsight Trace Explorer by the new session's timestamp.

After the user runs their agent for at least one turn, optionally verify that the collector endpoint is reachable:

```bash
# Probe the ingest path itself. An empty body is expected to be rejected — the status code is
# what matters here, not the response.
code=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 5 \
  -X POST "$ENDPOINT/v1/traces" \
  -H "content-type: application/x-protobuf" \
  -H "x-singsight-apikey: $API_KEY" \
  --data-binary "" 2>/dev/null)
echo "HTTP $code"
```

Read it as:

| Status | Meaning |
| --- | --- |
| `200` / `202` / `400` / `415` | Endpoint reachable and the key was accepted (`400`/`415` is just the empty body) |
| `401` / `403` | API key rejected — create a new **Ingest** key in Singsight (Access keys cannot ingest) |
| `404` | Wrong path or wrong host — check the endpoint value, do not assume ingestion is broken |
| `000` | No response at all: DNS, firewall, or wrong host/port |

Do not probe `$ENDPOINT/actuator/health`. Not every deployment exposes it, so a 404 there says
nothing about whether ingestion works and only makes the report look broken.

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
- Opencode only: run `opencode run --print-logs "hi" 2>&1 | grep -i telemetry`. If it says `telemetry disabled`, the plugin options were not applied — see Step 6c
> - Verify the endpoint is reachable from your machine
> - Check the API key is valid (Settings → API Keys in Singsight UI)

---

## Step 8 — Report what changed

Summarize for the user (never echo the API key):

**Codex:** Report the relay and config locations, whether a fresh CLI or desktop process was tested, and the session, LLM call and exact token totals verified.

**Claude Code:**
- `~/.claude/genai-hook.json`: cc-genai-hook endpoint/header/tool_mode
- `~/.claude/settings.json`: merged `Stop` / `SessionEnd` hooks (and `PostToolUse` / `PostToolUseFailure` in realtime mode)
- Signals: gen_ai traces (`invoke_agent` / `chat` / `execute_tool` / `subagent`)
- No native Claude Code telemetry variables were written
- No restart needed; a new session picks up the hooks

**Hermes Agent:**
- `~/.hermes/.env`: added OTLP exporter variables
- `~/Library/LaunchAgents/ai.hermes.gateway.plist` (macOS launchd only): same variables under `EnvironmentVariables`
- `~/.hermes/config.yaml`: added `otel_tracing` to `plugins.enabled`
- Installed: `hermes-plugin-otel-tracing`, into the interpreter that runs Hermes
- Signals: traces + metrics + logs
- Gateway restarted; **a new session is required** — pre-existing sessions never emit traces

**OpenClaw:**
- `~/.openclaw/openclaw.json`: enabled `diagnostics-otel` plugin with endpoint/key
- Signals: traces + metrics + logs
- Gateway restarted if running

**Opencode:**
- `~/.config/opencode/opencode.json`: added `@devtheops/opencode-plugin-otel@1.4.0` with inline options (`enabled`, `endpoint`, `protocol`, `otlpHeaders`)
- No `.env` file and no shell exports — opencode does not load `~/.config/opencode/.env`
- Signals: traces + metrics + logs
- New opencode process required

End with: "Your API key is stored in the config file listed above. Keep it readable only by you (`chmod 600`)."
