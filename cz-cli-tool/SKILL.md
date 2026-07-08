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
