# Singdata CLI (cz-cli)

cz-cli is the command-line tool for Singdata Lakehouse. For human users, it lets data developers query tables, run SQL, manage tasks, and view run logs from the terminal — no browser required. For AI Agents, it provides a high-level operation interface tailored to data warehouse scenarios, letting agents complete full operations with minimal context overhead.

## Why cz-cli?

Lakehouse already offers Studio Web UI, MCP Server, JDBC, REST API, and other access methods — but each has fundamental limitations for AI Agents. cz-cli provides differentiated value for two core scenarios:

### Scenario 1: Agent Calls Commands Directly (Tool-Call Mode)

The agent uses `cz-cli` commands to perform data warehouse operations — one command per complete business action.

**Limitations of other interfaces:**

| Interface | Core limitation |
|------|---------|
| **JDBC / SQL** | Agent must inject the full schema before writing SQL; large warehouse schemas can cost tens of thousands of tokens. Without schema context, hallucinations are severe (fabricated table and column names). Studio task status, run logs, and other operational actions have no SQL interface at all. |
| **REST API** | No unified interface discovery mechanism — agents cannot automatically know which endpoints exist. Even with an OpenAPI spec, the full spec is a context bomb. A single business action requires chaining 3–5 API calls; any intermediate failure silently breaks the flow. |
| **MCP Server** | Each tool description costs ~300–600 tokens; 3 MCP servers can consume 70%+ of the context window. As tool count grows, agent selection accuracy drops significantly — quality degrades noticeably beyond 50 tools. |
| **Studio Web UI** | Requires simulating browser interactions; many steps, unstable state, high agent operation cost, low accuracy. |

**cz-cli advantages:**

- **Self-describing and discoverable**: `cz-cli --help` and `cz-cli <subcommand> --help` are self-describing. Agents query on demand without preloading any documentation. `cz-cli ai-guide` generates a more compact task-oriented command reference.
- **Business-semantic encapsulation**: Each command maps to one complete business action — agents get it done in one step, no multi-step composition, no pagination, authentication, or error code handling.
- **Covers capabilities beyond SQL**: Studio task management, run inspection, backfill, data source browsing — all unreachable via JDBC.
- **Built-in guardrails**: Write operations require `--write`; high-risk operations require `-y` confirmation, reducing agent error risk.
- **Structured output**: JSON by default — agents parse directly without processing natural language or HTML.
- **Headless-friendly**: A plain process, no persistent connection needed. Works directly in CI/CD pipelines, scheduled scripts, and enterprise bots.

### Scenario 2: As a Specialized Sub-Agent (cz-cli agent Mode)

When a primary agent (Claude Code, Cursor, Kiro, etc.) loads too many skills, two problems emerge: **context pollution** — information accumulated from a previous task interferes with reasoning on the next — and **attention dilution** — the more tools available, the higher the probability of choosing the wrong one.

The solution is Anthropic's recommended **orchestrator-subagent pattern**: the primary agent handles planning and coordination, delegating specialized domain problems wholesale to a specialized sub-agent, which completes the work in an isolated, clean context and returns results to the primary agent.

`cz-cli agent` is the specialized sub-agent for data warehouse operations:

```
Primary Agent (Claude Code)
  └─ "Check today's failed scheduled tasks and suggest fixes"
       └─ cz-cli agent run "..." ← isolated context, focused on warehouse ops
            ├─ runs list / detail / logs
            └─ returns structured results to primary agent
```

Anthropic's Research feature uses the same architecture — benchmarks show a 90.2% improvement over single-agent approaches with 90% less research time. Data warehouse operations (checking task status, reading logs, backfilling, diagnosing SQL) are a natural fit for this delegation pattern — tasks are independent, boundaries are clear, and results are verifiable.

## Command Overview

| Command | Description |
|------|------|
| `cz-cli profile` | Manage connection profiles (create, switch, update) |
| `cz-cli status` | Verify the current connection is working |
| `cz-cli sql` | Execute SQL queries and DDL/DML |
| `cz-cli schema` | View and manage schemas |
| `cz-cli table` | View table structure, preview data, count rows |
| `cz-cli workspace` | View and switch workspaces |
| `cz-cli task` | Create, configure, deploy, and execute Studio tasks |
| `cz-cli runs` | View task run records, logs, backfill, rerun |
| `cz-cli attempts` | View retry records and logs for a single run |
| `cz-cli job` | SQL job performance diagnostics |
| `cz-cli datasource` | Manage external data sources, browse source objects |
| `cz-cli agent` | *(Agent)* Start an AI agent session, configure LLM, operate Lakehouse with natural language |
| `cz-cli ai-guide` | *(Agent)* Generate a compact command reference for agents to load |

## Quick Start

```bash
```

Install:

```bash
npm install -g @clickzetta/cz-cli

```

Configure connection:

```bash
cz-cli setup --credential <CLI connection string>

```

Verify connection:

```bash
cz-cli status

```

Run a query:

```bash
cz-cli sql "SELECT current_timestamp()" --sync
```

For detailed installation and configuration steps, see the [Installation and Configuration Guide](setup_cz_cli.md).

## Use Cases

| Scenario | Recommended approach |
|------|---------|
| Daily data queries, viewing table structure, sample data | `cz-cli sql` / `cz-cli table` |
| Managing and debugging Studio tasks, viewing run logs | `cz-cli task` / `cz-cli runs` |
| Automated DDL or task execution in CI/CD pipelines | cz-cli commands + `--write` |
| AI agent performing data warehouse operations | cz-cli tool-call mode |
| AI agent handling complex warehouse operations | `cz-cli agent run` sub-agent mode |
| Visual configuration of data sync or complex task orchestration | Studio Web UI |

## Related Documentation

**cz-cli Documentation**

- [Installation and Configuration Guide](setup_cz_cli.md) — Installation, profile configuration, output formats, upgrades, FAQ
- [SQL Execution and Data Exploration](cz-cli-sql.md) — Full reference for sql, schema, table, job, workspace commands
- [Studio Task Development and Operations](cz-cli-studio-tasks.md) — Task creation, scheduling, runs operations, backfill, task flow
- [Studio External Data Source Management](cz-cli-datasource.md) — Data source browsing, connectivity testing, sample data preview
- [AI Agent Integration](cz-cli-agent.md) — Agent LLM configuration, natural language operations, enterprise bot scenarios

**Lakehouse Documentation**

- [Studio Guide](studio_manual.md) — Complete Studio Web UI operations guide
- [Workspace](workspace-introduction.md) — Workspace concepts, user management, permission model
- [Compute Cluster](virtual-cluster.md) — VCluster types, specs, start/stop management
- [Task Development and Scheduling](task-develop.md) — Studio SQL task development and scheduling configuration
- [Real-time Sync Tasks](realtime_sync.md) — CDC real-time sync configuration and management
- [Batch Sync Tasks](batch_sync.md) — Batch offline sync configuration and management
- [Data Source Management](config-datasource.md) — External data source connection configuration
