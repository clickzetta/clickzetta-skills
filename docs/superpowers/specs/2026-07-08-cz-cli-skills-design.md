# Design: `cz-cli-agent` + `cz-cli-tool` public peer skills

- **Date:** 2026-07-08
- **Status:** Approved (pending spec review)
- **Owner:** robert
- **Related:** `cz-cli/skills/cz-cli/` (outer), `cz-cli/.opencode/skills/cz-cli-inner/` (inner)

## 1. Background & motivation

Today the cz-cli tooling ships two skills with an asymmetric, hidden-inner architecture:

- **Outer skill** (`cz-cli/skills/cz-cli/`) — publicly installable. A monolithic router that delegates ClickZetta Lakehouse operations to the cz-agent runtime (`cz-agent run`), and also (in its no-LLM fallback) drives `cz-cli` commands directly. It is bloated with exact command detail (integration `setup`/`edit`, CDC `*-table` lifecycle) that duplicates the inner skill's command reference.
- **Inner skill** (`cz-cli/.opencode/skills/cz-cli-inner/`, synced to `.agents/.claude/.codex/.kiro`) — **hidden**. Bundled inside the cz-cli repo as the operator manual loaded by the cz-agent runtime. End users cannot install it; it is not in any public registry.

Two problems follow:

1. **No choice / hidden skill.** End users can install the outer skill (to use cz-cli *as an agent*) or nothing. They cannot install cz-cli *as a direct tool*, because the inner skill is hidden.
2. **Bloated outer + duplication.** The outer skill carries command detail that is the inner skill's job, creating two sources of truth that drift.

### Goal

Make both skills **publicly available peers** in the clickzetta-skills registry (installable via `npx skills add`). The end user chooses which to install/enable. **If both are installed, `cz-cli-agent` is routed first (the default).** No hidden skills: the cz-agent runtime loads the public `cz-cli-tool` as its operator manual.

A third concern surfaced during design and is addressed in §6: naively delegating every interaction to `cz-agent run` (a nested LLM) wastes tokens and latency. The design routes by complexity so simple ops stay cheap.

## 2. Goals / non-goals

**Goals**
- Publish `cz-cli-agent` and `cz-cli-tool` in the clickzetta-skills registry.
- Agent-first routing when both are installed, with no hard priority flag (description-driven).
- Simple ops are cheap (direct `cz-cli` commands); `cz-agent run` only for complex/autonomous work.
- One source of truth for command detail (lives in `cz-cli-tool`).
- Retire the hidden inner skill; cz-agent runtime loads the public `cz-cli-tool`.

**Non-goals**
- Splitting either skill by domain (sync, tasks, etc. as separate skills). The two-skill set is the deliverable; domain splits are a possible future phase.
- Extracting profile onboarding into a third skill. It stays as a `references/` doc.
- Changing the cz-cli tool itself or the cz-agent runtime's implementation — only its skill-loading pointer.
- Hardening routing with a `settings.json` hook (considered, rejected as brittle).

## 3. Architecture

Two public skills in the clickzetta-skills registry, both `cz-cli-*` named (intentional exceptions to the registry's `clickzetta-` prefix rule — the product brand is `cz-cli`; documented in README and CLAUDE.md so contributors do not "fix" them).

| Skill | Role | Loaded by | Default? |
|---|---|---|---|
| `cz-cli-agent` | Default entry. Routes by complexity: direct commands for simple ops, `cz-agent run` for complex/autonomous. Carries a minimal command cheat-sheet. | Host agents (Claude Code, etc.) | Yes — routed first when both present |
| `cz-cli-tool` | Full operator manual + all command detail. Direct mode. | Host agents (direct use) **and** the cz-agent runtime (replaces hidden inner) | Fallback / explicit-direct |

**Source material mapping**

| New skill content | Sourced from |
|---|---|
| `cz-cli-agent` routing, async polling, multi-env, profile Q&A | `cz-cli/skills/cz-cli/SKILL.md` (outer), slimmed |
| `cz-cli-agent` direct-path cheat-sheet | New, distilled from `cz-cli/.claude/skills/cz-cli-inner/references/command-reference.md` |
| `cz-cli-tool` body (Core/SQL/Task/Output rules) | `cz-cli/.opencode/skills/cz-cli-inner/SKILL.md` |
| `cz-cli-tool/references/command-reference.md` | `.claude/skills/cz-cli-inner/references/command-reference.md`, **expanded** with integration + CDC |
| `cz-cli-tool/references/sync-pipelines.md` (new) | Integration + CDC sections moved out of the outer `cz-cli/skills/cz-cli/SKILL.md` |
| `cz-cli-tool/references/profile-setup.md` | `cz-cli/skills/cz-cli/references/profile-setup.md` |

## 4. `cz-cli-agent` specification

### 4.1 Frontmatter

- `name`: `cz-cli-agent` (matches directory; `[a-z0-9-]`; 12 chars).
- `description`: ≤ 1024 chars (verified: 862 chars). Draft:

> Delegate ClickZetta Lakehouse operations to the cz-cli agent runtime, or run cz-cli commands directly for simple tasks. TRIGGER when the user mentions ClickZetta/Lakehouse/cz-cli or a known profile AND wants to execute an operation: run SQL, manage tables/schemas, create Studio tasks, set up sync/ingest pipelines, configure profiles. DEFAULT route when cz-cli-tool is also installed. Routes by operation type — read-only lookups run direct via cz-cli; all other operations (writes, creates, configs, deploys, multi-step, diagnostics) delegate to cz-agent run when an LLM is configured. SKIP when (1) user explicitly wants direct cz-cli execution without the agent → use cz-cli-tool; (2) developing cz-cli itself; (3) host project has its own SQL toolchain. Keywords: clickzetta, lakehouse, cz-cli, sql, table, schema, studio task, sync, cdc, pipeline, profile

### 4.2 Body structure

1. **One-liner.** "Route by operation type: read-only lookups run direct via `cz-cli`; everything else delegates to the `cz-agent` runtime when an LLM is configured."
2. **Direct path — read-only lookups only.** A minimal set of read-only `cz-cli` commands for quick lookups, plus the rules to run them safely:
   - `cz-cli sql "<select>"` (run a SELECT the user gave verbatim; use `cz-cli sql -f <file>` if it has quotes/`$`/backticks/newlines) / `cz-cli sql status <job-id>` / `cz-cli job status <job-id>` / `cz-cli job result <job-id>`
   - `cz-cli schema list [--like <p>]` / `cz-cli schema describe <n>`
   - `cz-cli table list [--schema <s>]` / `cz-cli table describe <n>` / `cz-cli table preview <n>` / `cz-cli table stats <n>`
   - `cz-cli status` / `cz-cli workspace current`
   - `cz-cli task list` / `cz-cli runs list [--task <n>]` / `cz-cli runs detail <id>`
   - Rules: `--format json` + preserve `ai_message`; `--profile <name>` for a named environment; READ-ONLY — any DDL/DML/write/create/configure/deploy/multi-step op delegates (item 3); on `NO_PROFILE` guide to `cz-cli setup` (full mechanics in `cz-cli-tool/references/profile-setup.md`).
   - Write commands (`--write`, DDL/DML) are intentionally NOT in this list, so the host cannot easily short-circuit. Heavy detail (integration, CDC, flow, merge, flags) lives in `cz-cli-tool`.
3. **Delegate path — all other operations.** Anything that is NOT a read-only lookup — writes (DDL/DML), creating/configuring/deploying objects, building pipelines, composing SQL, multi-step workflows, diagnosing failures — **MUST delegate to `cz-agent run`** when an LLM is configured. Do not execute these directly via the cheat-sheet.
   - **Once per session (cached):** at the first ClickZetta op, run `cz-agent llm show` and remember the result for the session. Not lazy (the host must know cz-agent is available in order to delegate) and not per-request (once is enough).
   - If an LLM is configured (kind != none): `cz-agent run "<request>" --dangerously-skip-permissions`. Poll `cz-agent session status <session_id>` (or `--wait`); when `idle`, read `.result`; for full detail `cz-agent export <session_id>`. Reuse `--session <id>` for follow-ups on the same topic.
4. **No-LLM fallback.** If `cz-agent llm show` reports `none`: do **not** spawn the nested agent. Autonomous/multi-step work is **not possible without an LLM** — `cz-cli-tool` is also direct-mode, not autonomous. So either (a) guide the user to configure an LLM (`cz-agent llm add <name> --provider <p> --api-key <k> --use`) and retry, or (b) do read-only lookups directly; for writes/creates, hand off to `cz-cli-tool` and tell the user cz-agent is unavailable. Anything genuinely requiring autonomy requires a configured LLM.
5. **Multi-environment.** `--profile <name>` on direct lookups; `cz-agent run "<req>" --profile <name> --dangerously-skip-permissions` on the delegate path. Profiles: `cz-cli profile list` or `~/.clickzetta/profiles.toml`.
6. **Profile onboarding.** Guided Q&A collecting `service`/`instance`/`workspace`/`username`/`password`/`name`, with the service-endpoint inference table (cloud region → service host → suggested prefix). Then run `cz-cli profile create <name> ...` (direct — profile creation is local config, not Lakehouse work) and verify with `cz-cli status --profile <name>`. The full `cz-cli setup`/credential/`auth.json`/error-JSON mechanics live in `cz-cli-tool/references/profile-setup.md`; this skill keeps only the Q&A + endpoint table (it is the onboarding entry point).
7. **Hand-off rule.** If the user explicitly wants direct tool use for something beyond the lookups, invoke `cz-cli-tool` rather than delegating to `cz-agent`.
8. **SKIP reminders.** Do not intercept when (a) the cwd is the cz-cli source repo and the user is developing/debugging cz-cli itself, or (b) the host project has its own SQL execution toolchain (e.g. its own AGENTS.md / SQL skills).

## 5. `cz-cli-tool` specification

### 5.1 Frontmatter

- `name`: `cz-cli-tool` (matches directory; 12 chars).
- `description`: ≤ 1024 chars (verified: 704 chars / 706 bytes). Draft:

> Drive cz-cli commands directly against ClickZetta Lakehouse — no agent runtime. TRIGGER when the user explicitly wants direct tool execution: 'use cz-cli directly', 'run this cz-cli command', 'without the agent', no LLM configured for cz-agent, or cz-cli-agent not installed. Covers SQL jobs, schemas/tables, Studio tasks (SQL/Python/Shell/Flow/Merge), runs/backfills, datasources, AI Gateway, and full sync/CDC pipeline commands. Prefer cz-cli-agent for generic ClickZetta operations; use this only for direct command execution. Loaded by host agents and by the cz-agent runtime as its operator manual. Keywords: cz-cli command, direct, cli, --write, --async, cz-cli sql, command reference, run directly

### 5.2 Body structure (lean — rules, not command dumps)

1. **Core Rules** (from current inner): use `cz-cli` from PATH; run `cz-cli <command> --help` when flags are unclear; prefer `--format json` and preserve `ai_message`; `--profile <name>` for a named environment; on `NO_PROFILE` guide to `cz-cli setup`; stop after the same command fails twice — report and change approach; never fabricate URLs/IDs/names — use exact command output.
2. **SQL Rules** (from current inner): sync default; `--async` for large/long-running then `cz-cli sql status`/`cz-cli job status`; `--write` always required for DDL/DML; file-based (`cz-cli sql -f <file>`) for quotes/`$`/backticks/newlines; ClickZetta Lakehouse SQL syntax only — load `lakehouse-doc-en` before generating/modifying non-trivial SQL.
3. **Studio Task Rules** (from current inner): always pass `--type`; flow tasks use `cz-cli task flow *` (not normal content/deploy on flow nodes); confirm before destructive/state-changing ops (deploy, undeploy, execute, delete, refill/backfill, stop, rerun); backfills use `cz-cli runs refill <task> --from D --to D` (under `runs`, not `task`); JSON array flags (e.g. `--output-tables`) passed as one shell argument.
4. **Output Handling** (from current inner): `--format json` (parse), `toon` (line-per-field, grep/head), `table`/`csv`/`pretty` (human), `--field <name>` (raw text); paginated lists return page 1 — check `ai_message` for next-page hints.

### 5.3 `references/`

- **`command-reference.md`** — the existing compact command map, **expanded** to include the integration `setup`/`edit` and CDC `*-table` lifecycle commands (moved out of the outer skill). Sections: SQL & Jobs, Schemas & Tables, Workspaces & Profiles, Studio Tasks (incl. flow/merge), Runs & Attempts, Datasources, AI Gateway, **Integration sync** (new), **CDC pipeline** (new).
- **`sync-pipelines.md`** *(new)* — the richer guidance currently bloating the outer skill: single-table partition modes (static `--partitions 'dt=${bizdate}'` vs dynamic `--dynamic-partition 'dt:source_col'`; `--partitioned` auto-creates `PARTITIONED BY (dt STRING)`); `setup` vs `edit` semantics (setup changes source/sink tables, edit changes mapping/params); multi/whole-db table-mapping + write modes (`--pk-write-mode`/`--non-pk-write-mode`) + naming rules (`--schema-rule`/`--table-rule`) + grouping; CDC per-table ops (`task cdc tables` → `start-table`/`stop-table`/`resync-table`/`pause-table`/`recover-table` by `--table-ids`); INTEGRATION-type vcluster requirement; `--where` scheduling-parameter caution.
- **`profile-setup.md`** — `cz-cli setup --credential`; what setup writes (`profiles.toml`, `auth.json`); `cz-cli profile` subcommands forwarded to `cz-tool`; LLM configuration (`cz-agent llm add/use/show/reset`, supported providers); the three `NO_PROFILE` error-JSON shapes; the `cz-cli profile create` username/password alternative; registration URLs. The service-endpoint table authoritative copy lives in `cz-cli-agent` (onboarding entry); this file carries a one-line pointer to avoid full duplication.

## 6. Routing priority (agent-first)

Skill frontmatter has no priority field; selection is description-driven (the model sees `name` + `description` at selection time; the body is read only after a skill is picked). Agent-first is achieved with four reinforcing mechanisms plus a safety net:

1. **Trigger by task vs mechanism.** `cz-cli-agent` triggers on the *task* (run SQL, create a table, set up CDC). `cz-cli-tool` triggers on the *mechanism* ("use cz-cli directly", "without the agent"). Generic requests match agent broadly and tool narrowly → agent.
2. **Default-preference in the description.** `cz-cli-agent`: "DEFAULT route when cz-cli-tool is also installed." `cz-cli-tool`: "Prefer cz-cli-agent for generic ClickZetta operations; use this only for direct command execution." The tool's deferral is read at selection time, biasing ambiguous cases to agent.
3. **Mutual SKIP.** Agent SKIPs on explicit-direct-tool intent; tool SKIPs on generic ops. The space is partitioned so both do not fire on the same query.
4. **Keyword asymmetry.** Agent Keywords are operation-oriented (`sql, table, schema, studio task, sync, cdc, pipeline, profile`); tool Keywords are mechanism-oriented (`cz-cli command, direct, --write, --async, cz-cli sql`). Low overlap by design.
5. **Safety net (body-level).** `cz-cli-agent` body: "If the user explicitly wants direct cz-cli execution, invoke `cz-cli-tool`." `cz-cli-tool` body: "If this is a generic operation and the user didn't ask for direct tool use, hand off to `cz-cli-agent`."

**Edge case (correct behavior).** A request like "run `cz-cli sql 'SELECT 1'`" names both task and mechanism; the model may pick `cz-cli-tool`. That is correct — the user was explicit about the tool. "Agent is default" means default for ambiguous/generic ops, not "always agent even when the user names the tool."

## 7. Route-by-operation-type (delegation model)

> **Revised 2026-07-08** after observing that the original "route-by-complexity" model never escalated to `cz-agent run`. Root cause: the host LLM, given a direct cheat-sheet, a subjective "is this complex?" trigger, and a *lazy* LLM-check (so it never discovered cz-agent was available), always did the work directly and never reached the escalation branch. The model now routes by **operation type** (concrete, not subjective), checks LLM availability **once per session** (not lazy), makes delegation **imperative** for non-lookup ops, strips write commands from the cheat-sheet, and states **why** to delegate.

The two costs are unequal:
- `cz-agent llm show` — cheap (local config read, no LLM call).
- `cz-agent run "<request>"` — expensive: spawns a nested agent (its own LLM context + tool loop), then requires polling `session status` and `export` to retrieve the result.

`cz-cli-agent` routes by **operation type**, not subjective complexity:

| Operation | Path | Cost |
|---|---|---|
| Read-only lookups (list/describe/preview/stats/status/runs list, a user-provided SELECT) | direct `cz-cli` command | one CLI call, no nested LLM |
| Everything else (writes/DDL/DML, create/configure/deploy, build pipelines, compose SQL, multi-step, diagnose) | `cz-agent run` (when LLM configured) | nested agent — worth it |

- `cz-agent llm show` runs **once per session (cached)** — not lazy (the host must know cz-agent is available in order to delegate) and not per-request (once is enough). This breaks the discovery deadlock that caused the original model to never escalate.
- Delegation is **imperative** for non-lookup ops ("you MUST delegate; do not execute writes/creates directly via the cheat-sheet"). The cheat-sheet intentionally contains **no write commands**, so the host cannot easily short-circuit.
- **Why delegate** is stated in the body: `cz-agent` runs on a ClickZetta-optimized LLM with the full operator manual (`cz-cli-tool`) loaded → better Lakehouse reasoning, iteration/error handling, context isolation.
- "Agent is default" = `cz-cli-agent` is the default *entry point*; within it, non-trivial work delegates to `cz-agent run`, while trivial lookups stay cheap and direct.

The pure-delegator alternative (cz-cli-agent always delegates; cz-cli-tool for direct) was considered and rejected in favor of the hybrid, because trivial lookups ("list my tables") should not spawn a nested agent.

## 8. Description length constraint

The clickzetta-skills registry requires `description` ≤ 1024 chars; excess is truncated by the platform. The current outer `cz-cli` description is ~1150 chars and would be truncated. Both new descriptions (drafts in §4.1 and §5.1) have been char-count-validated: `cz-cli-agent` = 779 chars / 783 bytes; `cz-cli-tool` = 704 chars / 706 bytes — both under the 1024 limit. If a future edit pushes a draft over, trim trigger scenarios first, then keywords — never drop the Keywords line or the DEFAULT/prefer routing language.

## 9. Registry integration (clickzetta-skills repo)

- **`.well-known/skills/index.json`** — add two entries:
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
  Per registry convention, the index `description` is the **first sentence** of the SKILL.md frontmatter description (≤ 250 bytes — see commits `a770b9a`/`c36c3cc` and the existing `clickzetta-overview` entry). The index descriptions above are the first sentences of §4.1/§5.1 (119 and 81 bytes respectively). The full trigger/keyword description lives in each SKILL.md frontmatter.
- **`README.md`** — add a "cz-cli" section explaining the agent/tool peer model, agent-default routing, and that `cz-cli-*` naming is an intentional brand exception to the `clickzetta-` prefix.
- **`CLAUDE.md`** — add a note that `cz-cli-agent` and `cz-cli-tool` are the two sanctioned non-`clickzetta-` entries (so the naming rule's exception is explicit, not accidental).

## 10. cz-cli repo cleanup (follow-up dependency)

These changes live in the **cz-cli repo**, not clickzetta-skills. They are required for "no hidden skills" to be real, but are a separate PR:

- Delete `.opencode/skills/cz-cli-inner/` and the synced copies in `.agents/skills/cz-cli-inner/`, `.claude/skills/cz-cli-inner/`, `.codex/skills/cz-cli-inner/`, `.kiro/skills/cz-cli-inner/`.
- Point the cz-agent runtime's skill loader at the public `cz-cli-tool` (registry path) instead of the bundled inner copy.
- Update any cz-cli docs/readmes that reference the inner skill.

Scope of *this* spec (clickzetta-skills repo): the two skills + `index.json` + `README.md` + `CLAUDE.md` note. The cz-cli repo cleanup is listed here so the dependency is visible.

## 11. Assumptions (to verify during implementation)

1. The cz-agent runtime can load a skill from the public registry (the user confirmed "load public, retire hidden"). Implementation must confirm the loader path/mechanism.
2. The two `cz-cli-*` names are accepted by the registry despite violating the `clickzetta-` prefix rule (user-approved exception; documented in CLAUDE.md).
3. Host agents can invoke one skill from another's body (e.g. `cz-cli-agent` → `cz-cli-tool`) via the Skill tool. This is standard in Claude Code; confirm for other host agents if relevant.

## 12. Out of scope

- Domain-split skills (cz-cli-sync, cz-cli-tasks, etc.).
- A third `cz-cli-profile` skill.
- A `settings.json` hook to hard-enforce agent-first routing.
- Changes to cz-cli or cz-agent source code (only the skill-loading pointer).
- Migrating the existing globally-installed `cz-cli` skill identity (the outer skill is renamed `cz-cli-agent`; existing installs may need re-install — noted as a migration comms item, not a code change here).
