---
name: cz-cli-agent
description: |
  Delegate ClickZetta Lakehouse operations to the cz-cli agent runtime, or run cz-cli commands directly for simple tasks. TRIGGER when the user mentions ClickZetta/Lakehouse/cz-cli or a known profile AND wants to execute an operation: run SQL, manage tables/schemas, create Studio tasks, set up sync/ingest pipelines, configure profiles. DEFAULT route when cz-cli-tool is also installed. Routes by complexity — direct cz-cli commands for simple ops, cz-agent run only for complex autonomous multi-step work. SKIP when (1) user explicitly wants direct cz-cli execution without the agent → use cz-cli-tool; (2) developing cz-cli itself; (3) host project has its own SQL toolchain. Keywords: clickzetta, lakehouse, cz-cli, sql, table, schema, studio task, sync, cdc, pipeline, profile
---

# cz-cli Agent — ClickZetta Lakehouse Router

You have no direct Lakehouse access. **Route by complexity:** direct `cz-cli` commands for simple ops, `cz-agent run` only for complex/autonomous multi-step work. This is the DEFAULT route when `cz-cli-tool` is also installed.

If the user explicitly requests direct cz-cli command execution without the agent, or needs commands beyond the cheat-sheet below, invoke `cz-cli-tool` instead.

## When to SKIP this skill

- The cwd is the cz-cli source repo and the user is developing/debugging cz-cli itself (build, install, unlink, permissions, CLI source/tests).
- The host project has its own SQL execution toolchain (e.g. its own AGENTS.md or SQL skills) — do not intercept generic "query data" / "run SQL" requests that belong to the host project.

## Direct path — simple ops (default)

For deterministic, single-step operations, run `cz-cli` commands directly. This is far cheaper than spinning up the nested agent.

```bash
cz-cli sql "<statement>"              # sync; add --async for large/long-running
cz-cli sql "<ddl-or-dml>" --write     # --write REQUIRED for DDL/DML
cz-cli sql -f <file>                  # if SQL has quotes, $, backticks, backslashes, newlines
cz-cli sql status <job-id>            # async job status
cz-cli job status <job-id>            # job status + summary
cz-cli job result <job-id>            # fetch result set

cz-cli schema list [--like <pattern>]
cz-cli schema describe <name>

cz-cli table list [--schema <name>]
cz-cli table describe <name>
cz-cli table preview <name>
cz-cli table stats <name>

cz-cli status                         # connection status
cz-cli workspace current

cz-cli task list
cz-cli runs list [--task <name>]
cz-cli runs detail <id>
```

Direct-path rules:
- Prefer `--format json` and preserve `ai_message` guidance.
- Use `--profile <name>` when the user names an environment.
- On `NO_PROFILE`, guide the user to `cz-cli setup` (full mechanics in `cz-cli-tool/references/profile-setup.md`).

For commands beyond this cheat-sheet (integration sync, CDC, flow, merge, datasources, AI Gateway), invoke `cz-cli-tool` — do not improvise flags.

## Autonomous path — complex ops

Escalate to the cz-agent runtime when the request is multi-step, exploratory, error-prone, or "figure it out" (e.g. "build a CDC pipeline mirroring my MySQL db", "diagnose why this task keeps failing").

**Step 1 — lazy + cached LLM check.** Run `cz-agent llm show` only at the moment you decide to escalate, and remember the result for the session. Do NOT run it per request or for simple direct-path ops.

**Step 2 — if an LLM is configured (kind != none), delegate:**

```bash
cz-agent run "<request>" --dangerously-skip-permissions
```

The output includes a `session_id`. Inspect the run:
- `cz-agent session status <session_id>` — `busy`/`retry` (with `progress`), `idle` (with `result`), or `error`.
- `cz-agent export <session_id>` — full conversation (messages, tool calls, reasoning, text). Wait until `status` is `idle` before exporting.

With session continuity for follow-ups on the same topic:
```bash
cz-agent run "<follow-up>" --dangerously-skip-permissions --session <session_id>
```

**Step 3 — no-LLM fallback.** If `cz-agent llm show` reports `none`: do NOT spawn the nested agent. Autonomous/multi-step work is not possible without an LLM (`cz-cli-tool` is also direct-mode, not autonomous). Either:
- guide the user to configure an LLM: `cz-agent llm add <name> --provider <p> --api-key <k> --use`, then retry; or
- if the op can be decomposed into deterministic commands, handle it via the direct path above, or hand off to `cz-cli-tool` for fuller direct coverage.

Anything genuinely requiring autonomy requires a configured LLM.

## Multi-environment (profiles)

When the user specifies an environment or profile:
```bash
cz-cli <cmd> --profile <name>                      # direct path
cz-agent run "<request>" --profile <name> --dangerously-skip-permissions   # autonomous path
```
Available profiles: `cz-cli profile list` or `~/.clickzetta/profiles.toml`.

## Adding a new profile

**Trigger:** user says "configure new environment", "add profile", "can't connect", mentions an unknown profile name, or provides credentials.

**Step 1 — Collect information (guided Q&A).** If all required fields are already provided, skip to Step 2. Required fields:

| Field | Question | Example |
|-------|----------|---------|
| `service` | Which cloud region? (see table below, or provide the service endpoint) | `cn-shanghai-alicloud.api.clickzetta.com` |
| `instance` | Instance name? | `billingsh` |
| `workspace` | Workspace name? | `meter_n_bill` |
| `username` | Username? | `billing_admin` |
| `password` | Password? | — |
| `name` | Profile name? (suggested format below) | `cn-shanghai-billingsh` |

**Common service endpoints (authoritative copy — this skill owns onboarding):**

| Region | service | Suggested prefix |
|--------|---------|------------------|
| Alibaba Cloud East China 2 (Shanghai) | `cn-shanghai-alicloud.api.clickzetta.com` | `cn-shanghai` |
| Tencent Cloud East China (Shanghai) | `ap-shanghai-tencentcloud.api.clickzetta.com` | `ap-shanghai` |
| Tencent Cloud North China (Beijing) | `ap-beijing-tencentcloud.api.clickzetta.com` | `ap-beijing` |
| Tencent Cloud South China (Guangzhou) | `ap-guangzhou-tencentcloud.api.clickzetta.com` | `ap-guangzhou` |
| AWS China (Beijing) | `cn-north-1-aws.api.clickzetta.com` | `cn-north-1` |

Inference rules (reduce questions):
- If the user describes a region in natural language ("Alibaba Cloud Shanghai", "阿里云上海"), resolve the `service` endpoint from the table — do NOT ask again.
- If no profile name given, suggest `<prefix>-<instance>` and confirm or proceed.

**Step 2 — Create the profile** (direct path):
```bash
cz-cli profile create <name> \
  --username <username> --password <password> \
  --instance <instance> --workspace <workspace> \
  --service <service> --schema public --vcluster default
```

**Step 3 — Verify:**
```bash
cz-cli status --profile <name>
```
Success: `{"data": {"connected": true, ...}}`. On failure, report the error and ask the user to double-check credentials/endpoint.

For the `cz-cli setup --credential` flow, `auth.json`, LLM configuration, and the `NO_PROFILE` error-JSON shapes, see `cz-cli-tool/references/profile-setup.md`.

## Error handling

All errors in non-TTY mode output JSON to stdout, e.g.:
```json
{"ok": false, "error": "NO_PROFILE", "next_steps": ["cz-cli setup --credential <base64>"]}
```
On `NO_PROFILE`: check whether a profile can be configured via username/password (above). If the user has a base64 credential, guide them to `cz-cli setup --credential <base64>` (see `cz-cli-tool/references/profile-setup.md`).
