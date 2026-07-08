# cz-cli-agent + cz-cli-tool Peer Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish `cz-cli-agent` (default router, route-by-complexity) and `cz-cli-tool` (direct operator manual) as public peer skills in the clickzetta-skills registry, retiring reliance on the hidden inner skill.

**Architecture:** Two new skill directories under the registry root. `cz-cli-tool` holds the full operator manual + command references (content moved from the cz-cli repo's hidden inner skill + the outer skill's command detail). `cz-cli-agent` is a slimmed router with a direct-command cheat-sheet and complexity-based escalation to `cz-agent run`. Registry `index.json`, `README.md`, and `CLAUDE.md` are updated. The hidden inner skill is retired in a **separate** cz-cli-repo change (out of scope here — see spec §10).

**Tech Stack:** Markdown (`SKILL.md` + `references/`), YAML frontmatter, JSON (`index.json`). No code runtime. Validation via shell (`python3`, `wc`, `grep`).

**Note on "tests":** This is a content task — there is no unit-test framework. "Validation" steps are concrete shell checks (YAML parse, char-count limits, JSON validity, file-existence, section presence). Treat each validation step as the test: run it, confirm the expected result, then commit.

**Source files (in the sibling cz-cli repo, read-only — absolute paths):**
- `OUTER` = `/Users/robert/workspace/cz-cli/skills/cz-cli/SKILL.md`
- `OUTER_PROF` = `/Users/robert/workspace/cz-cli/skills/cz-cli/references/profile-setup.md`
- `INNER` = `/Users/robert/workspace/cz-cli/.opencode/skills/cz-cli-inner/SKILL.md`
- `CMDREF` = `/Users/robert/workspace/cz-cli/.claude/skills/cz-cli-inner/references/command-reference.md`

**Spec:** `docs/superpowers/specs/2026-07-08-cz-cli-skills-design.md` (on this branch).

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `cz-cli-tool/SKILL.md` | Create | Tool skill frontmatter + 4 rule sections (Core/SQL/Task/Output) |
| `cz-cli-tool/references/command-reference.md` | Create | Expanded command map (from `CMDREF` + integration/CDC moved from `OUTER`) |
| `cz-cli-tool/references/sync-pipelines.md` | Create | New: integration partition/mapping + CDC per-table detail (from `OUTER`) |
| `cz-cli-tool/references/profile-setup.md` | Create | setup/credential/auth.json/LLM/error-JSON (from `OUTER_PROF`, endpoint table trimmed to pointer) |
| `cz-cli-agent/SKILL.md` | Create | Agent skill frontmatter + router body (cheat-sheet + escalation + profile onboarding) |
| `.well-known/skills/index.json` | Modify | Add 2 entries (first-sentence descriptions) |
| `README.md` | Modify | Add "cz-cli" section |
| `CLAUDE.md` | Modify | Add sanctioned-exception note for `cz-cli-*` names |

Order: tool files first (Tasks 1–4), then agent (Task 5), then registry files (Tasks 6–8), then final validation (Task 9). The agent references the tool, and `index.json` references all files — so both must exist before those tasks.

---

## Task 1: Create `cz-cli-tool/SKILL.md`

**Files:**
- Create: `cz-cli-tool/SKILL.md`
- Source: `INNER` (frontmatter + 4 rule sections), lines 6–47

- [ ] **Step 1: Create the file with frontmatter and the four rule sections**

Create `cz-cli-tool/SKILL.md` with this exact content:

````markdown
---
name: cz-cli-tool
description: |
  Drive cz-cli commands directly against ClickZetta Lakehouse — no agent runtime. TRIGGER when the user explicitly wants direct tool execution: 'use cz-cli directly', 'run this cz-cli command', 'without the agent', no LLM configured for cz-agent, or cz-cli-agent not installed. Covers SQL jobs, schemas/tables, Studio tasks (SQL/Python/Shell/Flow/Merge), runs/backfills, datasources, AI Gateway, and full sync/CDC pipeline commands. Prefer cz-cli-agent for generic ClickZetta operations; use this only for direct command execution. Loaded by host agents and by the cz-agent runtime as its operator manual. Keywords: cz-cli command, direct, cli, --write, --async, cz-cli sql, command reference, run directly
---

# cz-cli Tool — Direct Operator Manual

Use `cz-cli` from `PATH` to operate ClickZetta Lakehouse and Studio directly. This is the lower-level alternative to `cz-cli-agent` (which delegates to the cz-agent runtime). Prefer `cz-cli-agent` for generic ClickZetta operations; use this skill only when the user explicitly wants direct command execution, has no LLM configured for cz-agent, or `cz-cli-agent` is not installed.

## Core Rules

- Use `cz-cli` from `PATH` for Lakehouse and Studio operations.
- Run `cz-cli <command> --help` when exact flags are unclear.
- Prefer `--format json` for machine-readable output and preserve `ai_message` guidance.
- Use `--profile <name>` when the user names an environment or profile.
- On `NO_PROFILE`, guide the user to run `cz-cli setup` (see `references/profile-setup.md`).
- Stop after the same command fails twice or repeated minor variations make no progress; report what failed and change approach or ask for guidance.
- Never fabricate URLs, task IDs, run IDs, table names, or profile names. Use exact command output.

## SQL Rules

- Current default SQL mode is sync: `cz-cli sql "SELECT ..."` waits for results.
- Use `--async` for large or long-running queries, then inspect with `cz-cli sql status <job-id>` or `cz-cli job status <job-id>`.
- Write operations always require `--write`, including DDL and DML.
- If SQL contains quotes, `$`, backticks, backslashes, or newlines, write it to a file and run `cz-cli sql -f <file>` to avoid shell corruption.
- Use ClickZetta Lakehouse SQL syntax only. Before generating, modifying, validating, explaining, or running non-trivial Lakehouse SQL, load the Lakehouse documentation skill if available.

## Studio Task Rules

- Always pass `--type` when creating tasks.
- Flow tasks use `cz-cli task flow *` commands for nodes; do not use normal task content/deploy commands on flow nodes.
- Confirm intent before destructive or state-changing operations: deploy, undeploy, execute, delete, refill/backfill, stop, rerun, and similar actions.
- For historical reruns or backfills, use `cz-cli runs refill <task> --from YYYY-MM-DD --to YYYY-MM-DD`; this is under `runs`, not `task`.
- For output table JSON flags such as `--output-tables`, pass the JSON array as one shell argument, usually with single quotes.

## Output Handling

- `--format json`: best for parsing.
- `--format toon`: line-per-field output, useful with `grep` or `head`.
- `--format table`, `--format csv`, `--format pretty`: human-readable.
- `--field <name>`: extracts one field as raw text.
- Paginated list commands usually return page 1; check `ai_message` for next-page hints.

## Command Reference

Read `references/command-reference.md` for the full command map (SQL, schemas/tables, tasks, runs, datasources, AI Gateway, integration sync, CDC). Read `references/sync-pipelines.md` for detailed integration/CDC pipeline guidance, and `references/profile-setup.md` for connection onboarding.
````

- [ ] **Step 2: Validate frontmatter and description length**

Run:
```bash
python3 -c "
import yaml
d=yaml.safe_load(open('cz-cli-tool/SKILL.md').read().split('---')[1])
assert d['name']=='cz-cli-tool', d['name']
assert len(d['description'])<=1024, len(d['description'])
print('OK name=%s desclen=%d'%(d['name'],len(d['description'])))
"
```
Expected: `OK name=cz-cli-tool desclen=<n>` where `<n>` ≤ 1024 (informational; ~704). The assertion is the ≤1024 limit, not the exact count.

- [ ] **Step 3: Commit**

```bash
git add cz-cli-tool/SKILL.md
git commit -m "feat: add cz-cli-tool skill (direct operator manual)"
```

---

## Task 2: Create `cz-cli-tool/references/command-reference.md`

**Files:**
- Create: `cz-cli-tool/references/command-reference.md`
- Source: `CMDREF` (full file) + integration/CDC blocks from `OUTER` lines 38–118

- [ ] **Step 1: Copy `CMDREF` verbatim as the starting point**

```bash
cp /Users/robert/workspace/cz-cli/.claude/skills/cz-cli-inner/references/command-reference.md cz-cli-tool/references/command-reference.md
```

- [ ] **Step 2: Append the Integration sync and CDC sections (moved from `OUTER`)**

Append the following two sections to the end of `cz-cli-tool/references/command-reference.md` (these are the `#### Offline integration sync` and `#### Realtime CDC pipeline lifecycle` blocks from `OUTER` lines 38–118, lightly retitled to `##`):

````markdown

## Integration sync (`cz-cli task integration`)

Configure offline data-integration (batch sync) task content. Create the task skeleton first, then configure its content:

```bash
# 1) Create the task skeleton (single-table → INTEGRATION; multi/whole-db → MULTI_DI)
cz-cli task create my_sync --type INTEGRATION
cz-cli task create my_db_sync --type MULTI_DI

# 2) Configure content
#    single-table: creates the sink table from the source DDL + generates a default field mapping
cz-cli task integration setup my_sync --sync-type single \
  --source-datasource my_mysql --source-schema app --source-table orders \
  --sink-datasource lakehouse --sink-schema public --sink-table orders
#    single-table PARTITION (opt-in via --partitioned; default behavior is a plain non-partition table):
#      static  — whole batch to one partition value; auto-creates PARTITIONED BY (dt STRING):
cz-cli task integration setup my_sync --sync-type single \
  --source-datasource my_mysql --source-schema app --source-table orders \
  --sink-datasource lakehouse --sink-schema public --sink-table orders_di \
  --partitioned --partitions 'dt=${bizdate}'
#      dynamic — per-row routing by a source column (must exist in the source table):
cz-cli task integration setup my_sync --sync-type single \
  --source-datasource my_mysql --source-schema app --source-table orders \
  --sink-datasource lakehouse --sink-schema public --sink-table orders_di \
  --partitioned --dynamic-partition 'dt:create_time'
#    multi-table: one job per table (no table creation; the running task creates them)
cz-cli task integration setup my_db_sync --sync-type multi \
  --source-datasource my_mysql --source-schema app --source-tables orders,users,items \
  --sink-datasource lakehouse --sink-schema public
#    whole-db: mirror entire databases
cz-cli task integration setup my_db_sync --sync-type whole_db \
  --source-datasource my_mysql --source-schema app --source-dbs app,inventory \
  --sink-datasource lakehouse --sink-schema public

# 3) Inspect current config (read before editing)
cz-cli task integration show my_sync

# 4) Edit field mapping / sync params (applied & saved immediately — no UI needed)
#    single-table — column-mapping is a FULL replace (include every row to keep):
cz-cli task integration edit my_sync \
  --column-mapping '[{"source":"id","sink":"id"},{"source":"name","sink":"name"}]' \
  --parallelism 4 --error-limit -1 --m-bytes 8 --split-pk id --where "dt = bizdate"
#    multi/whole-db — table mapping + write modes + naming rules + grouping strategy:
cz-cli task integration edit my_db_sync \
  --table-mapping '[{"source":"app.orders","sink":"public.orders"}]' \
  --pk-write-mode OVERWRITE --non-pk-write-mode OVERWRITE \
  --schema-rule '{SOURCE_DATABASE}' --table-rule '{SOURCE_DATABASE}_{SOURCE_TABLE}' \
  --parallelism 4 --batch-size 4 --connections 4
```

Notes:
- `setup` does NOT change field mapping/params on an existing task — use `edit`. `edit` does NOT change source/sink tables — use `setup`.
- Partition tables (single-table) must be declared explicitly via `--partitioned`; see `sync-pipelines.md` for the static vs dynamic partition details.
- Datasource types are auto-resolved from the datasource name/ID; no need to pass type codes.
- `--where` with date/time scheduling params (e.g. `bizdate`, `$[yyyyMMdd]`): look up the correct Studio scheduling-parameter syntax first (`cz-cli ai-guide` / docs). Do NOT invent parameter formats.
- Integration tasks must execute on an INTEGRATION-type vcluster — pick one via the vcluster list, not the default/GENERAL vc.

## CDC pipeline lifecycle (`cz-cli task cdc`)

For multi-table CDC pipelines (MULTI_REALTIME, fileType 281 — created via `cz-cli task create-realtime-sync`). These commands manage the pipeline and its per-table incremental sync. They do NOT apply to single-table Kafka streaming tasks (fileType 14) — use `task start` / `task stop` for those.

```bash
# List CDC pipeline tasks
cz-cli task cdc list --name my_pipeline

# List the tables in a pipeline — returns the per-table ids used by the *-table ops below
cz-cli task cdc tables my_pipeline

# Per-table incremental sync control (--table-ids is comma-separated ids from 'task cdc tables')
cz-cli task cdc start-table my_pipeline --table-ids 101,102
cz-cli task cdc stop-table my_pipeline --table-ids 101
cz-cli task cdc resync-table my_pipeline --table-ids 101   # re-snapshot
cz-cli task cdc pause-table my_pipeline --table-ids 101
cz-cli task cdc recover-table my_pipeline --table-ids 101

# Take the whole pipeline offline (back to draft)
cz-cli task cdc offline my_pipeline
```

Notes:
- All `task cdc` commands validate the task is fileType 281; running them on any other type returns a `NOT_A_CDC_PIPELINE` error with guidance.
- Get table ids from `task cdc tables` first — the `*-table` ops require them.
````

- [ ] **Step 3: Validate the new sections are present**

Run:
```bash
grep -c "## Integration sync" cz-cli-tool/references/command-reference.md
grep -c "## CDC pipeline lifecycle" cz-cli-tool/references/command-reference.md
```
Expected: both print `1`.

- [ ] **Step 4: Commit**

```bash
git add cz-cli-tool/references/command-reference.md
git commit -m "feat: add cz-cli-tool command-reference (expanded with integration + CDC)"
```

---

## Task 3: Create `cz-cli-tool/references/sync-pipelines.md`

**Files:**
- Create: `cz-cli-tool/references/sync-pipelines.md`
- Source: detail distilled from `OUTER` lines 38–118 (the partition/mapping/write-mode/CDC semantics)

- [ ] **Step 1: Create the file with this exact content**

````markdown
# Sync Pipelines — Integration & CDC Detail

Deeper guidance for offline integration (batch) sync and multi-table CDC pipelines. The command skeletons live in `command-reference.md`; this file covers the semantics and gotchas.

## Single-table integration: partition modes

The user must declare a partitioned sink explicitly with `--partitioned`; without it the sink is a plain non-partition table. `--partitioned` auto-creates a `PARTITIONED BY (dt STRING)` sink table. Two mutually-exclusive modes:

- **Static** — `--partitions 'dt=${bizdate}'`: the whole batch is written to one partition value (typically the scheduling date). Use for daily snapshots.
- **Dynamic** — `--dynamic-partition 'dt:source_col'`: each row is routed to a partition by a source column value. The source column must exist in the source table; if it is missing, confirm the correct column with the user before proceeding.

Partition column defaults to `dt`.

## `setup` vs `edit` — what each changes

- `setup` configures source/sink tables (and creates the sink table for single-table). It does NOT change field mapping or sync params on an existing task.
- `edit` changes field mapping / sync params and is applied & saved immediately. It does NOT change source/sink tables.

So: change tables → `setup`; change mapping/params → `edit`.

## Single-table field mapping

`--column-mapping` is a **FULL replace** — include every column row you want to keep. Example:

```bash
cz-cli task integration edit my_sync \
  --column-mapping '[{"source":"id","sink":"id"},{"source":"name","sink":"name"}]' \
  --parallelism 4 --error-limit -1 --m-bytes 8 --split-pk id --where "dt = bizdate"
```

## Multi-table / whole-db mapping and write modes

Multi-table and whole-db modes do not create tables; the running task creates them. Configure via `edit`:

```bash
cz-cli task integration edit my_db_sync \
  --table-mapping '[{"source":"app.orders","sink":"public.orders"}]' \
  --pk-write-mode OVERWRITE --non-pk-write-mode OVERWRITE \
  --schema-rule '{SOURCE_DATABASE}' --table-rule '{SOURCE_DATABASE}_{SOURCE_TABLE}' \
  --parallelism 4 --batch-size 4 --connections 4
```

- `--table-mapping`: maps source `db.table` to sink `schema.table`.
- `--pk-write-mode` / `--non-pk-write-mode`: write strategy for tables with / without a primary key (`OVERWRITE`, etc.).
- `--schema-rule` / `--table-rule`: naming templates for auto-created sink objects. Placeholders: `{SOURCE_DATABASE}`, `{SOURCE_TABLE}`.
- Tuning: `--parallelism`, `--batch-size`, `--connections`.

## CDC per-table operations

For multi-table CDC pipelines (fileType 281, created via `cz-cli task create-realtime-sync`). Get table ids first:

```bash
cz-cli task cdc tables my_pipeline     # returns per-table ids
```

Then operate per-table (`--table-ids` is comma-separated):

```bash
cz-cli task cdc start-table    my_pipeline --table-ids 101,102
cz-cli task cdc stop-table     my_pipeline --table-ids 101
cz-cli task cdc resync-table   my_pipeline --table-ids 101   # re-snapshot
cz-cli task cdc pause-table    my_pipeline --table-ids 101
cz-cli task cdc recover-table  my_pipeline --table-ids 101
cz-cli task cdc offline        my_pipeline                   # whole pipeline → draft
```

- All `task cdc` commands validate fileType 281; other types return `NOT_A_CDC_PIPELINE`.
- These do NOT apply to single-table Kafka streaming tasks (fileType 14) — use `task start` / `task stop` for those.

## Vcluster and scheduling gotchas

- Integration tasks must run on an **INTEGRATION-type vcluster** — pick one from the vcluster list, not the default/GENERAL vc.
- `--where` with date/time scheduling params (e.g. `bizdate`, `$[yyyyMMdd]`, monthly partitions): look up the correct Studio scheduling-parameter syntax first (`cz-cli ai-guide` / docs). Do NOT invent parameter formats.
- Datasource types are auto-resolved from the datasource name/ID; no need to pass type codes.
````

- [ ] **Step 2: Validate the topics are covered**

Run:
```bash
grep -c "Static" cz-cli-tool/references/sync-pipelines.md
grep -c "Dynamic" cz-cli-tool/references/sync-pipelines.md
grep -c "table-mapping" cz-cli-tool/references/sync-pipelines.md
grep -c "start-table" cz-cli-tool/references/sync-pipelines.md
```
Expected: each prints `1` (or more).

- [ ] **Step 3: Commit**

```bash
git add cz-cli-tool/references/sync-pipelines.md
git commit -m "feat: add cz-cli-tool sync-pipelines reference (integration + CDC detail)"
```

---

## Task 4: Create `cz-cli-tool/references/profile-setup.md`

**Files:**
- Create: `cz-cli-tool/references/profile-setup.md`
- Source: `OUTER_PROF` (full file) — trim the service-endpoint table to a pointer (the authoritative table lives in `cz-cli-agent`)

- [ ] **Step 1: Copy `OUTER_PROF` as the starting point**

```bash
cp /Users/robert/workspace/cz-cli/skills/cz-cli/references/profile-setup.md cz-cli-tool/references/profile-setup.md
```

- [ ] **Step 2: Replace the duplicated service-endpoint table with a pointer**

In `cz-cli-tool/references/profile-setup.md`, find the "Common service endpoints" table (under "Alternative: username/password profile (no credential required)") and the cloud-region rows. Replace that table block with:

````markdown
**Common service endpoints:** the authoritative service-endpoint → region → suggested-profile-prefix table lives in `cz-cli-agent`'s profile-onboarding section (it is the onboarding entry point). When onboarding from this skill, ask the user for the cloud region and resolve the `service` host from that table; if `cz-cli-agent` is not available, request the `service` endpoint directly.
````

(Rationale: avoid two copies of the endpoint table drifting. The agent skill owns it because it runs the guided Q&A.)

- [ ] **Step 3: Validate the duplicate table is gone and the pointer is present**

Run:
```bash
grep -c "cn-shanghai-alicloud.api.clickzetta.com" cz-cli-tool/references/profile-setup.md
grep -c "authoritative service-endpoint" cz-cli-tool/references/profile-setup.md
```
Expected: first prints `0` (the table rows are removed); second prints `1` (the pointer is present). If the first is non-zero, the endpoint table was not fully removed — re-edit.

- [ ] **Step 4: Commit**

```bash
git add cz-cli-tool/references/profile-setup.md
git commit -m "feat: add cz-cli-tool profile-setup reference (endpoint table → pointer)"
```

---

## Task 5: Create `cz-cli-agent/SKILL.md`

**Files:**
- Create: `cz-cli-agent/SKILL.md`
- Source: `OUTER` (routing/async/profile sections, slimmed) + new cheat-sheet + new complexity-routing language

- [ ] **Step 1: Create the file with this exact content**

````markdown
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
````

- [ ] **Step 2: Validate frontmatter and description length**

Run:
```bash
python3 -c "
import yaml
d=yaml.safe_load(open('cz-cli-agent/SKILL.md').read().split('---')[1])
assert d['name']=='cz-cli-agent', d['name']
assert len(d['description'])<=1024, len(d['description'])
print('OK name=%s desclen=%d'%(d['name'],len(d['description'])))
"
```
Expected: `OK name=cz-cli-agent desclen=<n>` where `<n>` ≤ 1024 (informational; ~779). The assertion is the ≤1024 limit, not the exact count.

- [ ] **Step 3: Commit**

```bash
git add cz-cli-agent/SKILL.md
git commit -m "feat: add cz-cli-agent skill (default router, route-by-complexity)"
```

---

## Task 6: Update `.well-known/skills/index.json`

**Files:**
- Modify: `.well-known/skills/index.json`

- [ ] **Step 1: Read the current file to confirm its top-level shape**

Run:
```bash
python3 -c "
import json
d=json.load(open('.well-known/skills/index.json'))
print(type(d).__name__, list(d.keys()) if isinstance(d,dict) else 'list len=%d'%len(d))
"
```
Expected: `<class 'dict'> ['skills']` — the file is a JSON object with a `skills` array (verified). Step 2 appends to that array.

- [ ] **Step 2: Add the two new entries**

Append these two objects to the `skills` array (insert after the last existing entry, preserving trailing comma/JSON validity). The `description` is the **first sentence** of each SKILL.md frontmatter description (registry convention, ≤250 bytes):

```json
{
  "name": "cz-cli-agent",
  "description": "Delegate ClickZetta Lakehouse operations to the cz-cli agent runtime, or run cz-cli commands directly for simple tasks.",
  "files": ["SKILL.md"]
},
{
  "name": "cz-cli-tool",
  "description": "Drive cz-cli commands directly against ClickZetta Lakehouse — no agent runtime.",
  "files": ["SKILL.md", "references/command-reference.md", "references/sync-pipelines.md", "references/profile-setup.md"]
}
```

- [ ] **Step 3: Validate JSON, entries, first-sentence length, and file existence**

Run:
```bash
python3 -c "
import json,os
d=json.load(open('.well-known/skills/index.json'))
s=d['skills'] if isinstance(d,dict) else d
names=[x['name'] for x in s]
assert 'cz-cli-agent' in names and 'cz-cli-tool' in names, names
for e in s:
    if e['name'] in ('cz-cli-agent','cz-cli-tool'):
        assert len(e['description'])<=250, (e['name'],len(e['description']))
        for f in e['files']:
            p=os.path.join(e['name'],f)
            assert os.path.exists(p), p
print('OK entries=%d cz-cli-agent/cz-cli-tool present, files exist, descs<=250'%(len(s)))
"
```
Expected: `OK entries=29 ...` (27 existing + 2 new). If it fails on a missing file, the corresponding Task 1–4 file was not created — go back and create it.

- [ ] **Step 4: Commit**

```bash
git add .well-known/skills/index.json
git commit -m "feat: register cz-cli-agent and cz-cli-tool in skills index"
```

---

## Task 7: Update `README.md`

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Read README to find the skills overview table/section**

Run:
```bash
grep -n -iE "skill|clickzetta-" README.md | head -30
```
Note the location of the skills overview table (the spec says README has a "Skills overview table" organized by category).

- [ ] **Step 2: Add a "cz-cli" section**

Add a new subsection (after the existing skills table, or in a sensible spot) explaining the peer model. Use this content:

````markdown
## cz-cli skills

Two peer skills for operating ClickZetta Lakehouse via the `cz-cli` tool. Both are publicly installable (`npx skills add`); the user may install either or both.

| Skill | Role |
|---|---|
| `cz-cli-agent` | Default entry. Routes by complexity: direct `cz-cli` commands for simple ops, `cz-agent run` for complex/autonomous multi-step work. |
| `cz-cli-tool` | Direct operator manual. Drives `cz-cli` commands directly with no agent runtime. Loaded by host agents and by the cz-agent runtime. |

**Routing:** if both are installed, `cz-cli-agent` is routed first (the default). `cz-cli-tool` is used when the user explicitly wants direct command execution, has no LLM configured for cz-agent, or `cz-cli-agent` is not installed.

> **Naming note:** `cz-cli-agent` and `cz-cli-tool` use the `cz-cli-` prefix (the product brand) rather than the registry's usual `clickzetta-` prefix. They are the two sanctioned exceptions — see `CLAUDE.md`.
````

- [ ] **Step 3: Validate the section is present**

Run:
```bash
grep -c "## cz-cli skills" README.md
grep -c "sanctioned exceptions" README.md
```
Expected: both print `1`.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: add cz-cli peer-skills section to README"
```

---

## Task 8: Update `CLAUDE.md`

**Files:**
- Modify: `CLAUDE.md` (the "Skill Directory Naming" section)

- [ ] **Step 1: Locate the naming rule section**

Run:
```bash
grep -n "Unified prefix" CLAUDE.md
```
Expected: a line like `- Unified prefix: \`clickzetta-<feature-name>\``.

- [ ] **Step 2: Add the sanctioned-exception note**

Immediately after the `Unified prefix` bullet (or at the end of the "Skill Directory Naming" section), add:

````markdown
- **Sanctioned exceptions:** `cz-cli-agent` and `cz-cli-tool` use the `cz-cli-` prefix (the `cz-cli` product brand) instead of `clickzetta-`. They are the only two non-`clickzetta-` skills in the registry and are intentional — do not rename them to `clickzetta-*`.
````

- [ ] **Step 3: Validate the note is present**

Run:
```bash
grep -c "Sanctioned exceptions" CLAUDE.md
```
Expected: `1`.

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: document cz-cli-* naming exception in CLAUDE.md"
```

---

## Task 9: Final validation suite

**Files:** none (validation only)

- [ ] **Step 1: Validate all frontmatter (name matches dir, description ≤1024, name format `[a-z0-9-]+`)**

Run:
```bash
python3 -c "
import yaml,re,os
for sk in ['cz-cli-agent','cz-cli-tool']:
    p='%s/SKILL.md'%sk
    d=yaml.safe_load(open(p).read().split('---')[1])
    assert d['name']==sk, (sk,d['name'])
    assert re.fullmatch(r'[a-z0-9-]+',d['name']), d['name']
    assert len(d['description'])<=1024, (sk,len(d['description']))
print('OK both skills: name matches dir, format valid, desc<=1024')
"
```
Expected: `OK both skills: ...`.

- [ ] **Step 2: Validate index.json is well-formed and every listed file exists**

Run:
```bash
python3 -c "
import json,os
d=json.load(open('.well-known/skills/index.json'))
s=d['skills'] if isinstance(d,dict) else d
for e in s:
    for f in e['files']:
        assert os.path.exists(os.path.join(e['name'],f)), os.path.join(e['name'],f)
print('OK index.json valid; all %d skills files exist'%len(s))
"
```
Expected: `OK index.json valid; all 29 skills files exist`.

- [ ] **Step 3: Confirm only the two sanctioned non-`clickzetta-` names exist**

Run:
```bash
python3 -c "
import json
d=json.load(open('.well-known/skills/index.json'))
s=d['skills'] if isinstance(d,dict) else d
non=[x['name'] for x in s if not x['name'].startswith('clickzetta-')]
assert non==['cz-cli-agent','cz-cli-tool'], non
print('OK sanctioned exceptions:', non)
"
```
Expected: `OK sanctioned exceptions: ['cz-cli-agent', 'cz-cli-tool']`.

- [ ] **Step 4: Confirm cross-references resolve (agent references tool files; tool references its own references)**

Run:
```bash
test -f cz-cli-tool/references/command-reference.md && test -f cz-cli-tool/references/sync-pipelines.md && test -f cz-cli-tool/references/profile-setup.md && grep -q "cz-cli-tool/references/profile-setup.md" cz-cli-agent/SKILL.md && echo "OK cross-refs resolve"
```
Expected: `OK cross-refs resolve`.

- [ ] **Step 5: Final commit if anything was touched (otherwise skip)**

```bash
git status --porcelain
# If empty, nothing to commit. If files changed, stage and commit:
# git add -A && git commit -m "chore: final validation fixes"
```

---

## Out of scope (separate work, do NOT do here)

- **cz-cli repo cleanup** (spec §10): delete `.opencode/skills/cz-cli-inner/` and the `.agents/.claude/.codex/.kiro` syncs; repoint the cz-agent runtime skill loader at the public `cz-cli-tool`. This is a separate PR in the cz-cli repo.
- Domain-split skills (cz-cli-sync, cz-cli-tasks, etc.).
- A `settings.json` hook to hard-enforce agent-first routing.
- Migrating existing global installs of the old `cz-cli` skill (comms item only).
