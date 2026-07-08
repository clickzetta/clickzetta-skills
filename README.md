# clickzetta-skills

This repository contains AI Agent skills for ClickZetta Lakehouse. The skills are designed for Codex, Claude Code, czcode, and other assistants that can load a `SKILL.md`-based instruction set.

The repository turns ClickZetta operational knowledge into reusable routing rules, workflows, SQL patterns, and reference documents. An assistant can use these skills to select the correct domain workflow, read the minimum required reference material, and generate or execute the right ClickZetta steps for the user's task.

## Repository Contents

The repository currently contains 28 top-level `clickzetta-*` skills, 2 `cz-cli-*` operation skills, one official documentation knowledge base, and one independent skill (`singsight-install`):

- `lakehouse-doc-en`: English ClickZetta Lakehouse official documentation index and reference corpus.
- `clickzetta-*`: task-oriented skills for ingestion, Studio tasks, dbt, modeling, dynamic tables, connectors, external integrations, governance, and operations.

## Skill Catalog

| Category | Skill | Scope |
|---|---|---|
| Official docs | [lakehouse-doc-en](./lakehouse-doc-en/) | Official ClickZetta Lakehouse documentation covering SQL, functions, permissions, VClusters, data sharing, SDKs, BI tools, AI functions, and general platform usage. |
| Foundation and connectivity | [clickzetta-overview](./clickzetta-overview/) | Product overview, object model, architecture, Studio modules, brand naming, and service endpoints. |
| Foundation and connectivity | [clickzetta-sql-migration](./clickzetta-sql-migration/) | SQL migration guidance from Snowflake, Databricks, and Spark SQL to ClickZetta SQL. |
| Data ingestion and pipelines | [clickzetta-data-ingest-pipeline](./clickzetta-data-ingest-pipeline/) | Router for choosing ingestion methods based on source type, latency, sync scope, and whether ingestion is one-time or continuous. |
| Data ingestion and pipelines | [clickzetta-file-import-pipeline](./clickzetta-file-import-pipeline/) | Import data from URLs, local files, or Volume paths using format inference, table creation, and `COPY INTO`. |
| Data ingestion and pipelines | [clickzetta-oss-ingest-pipeline](./clickzetta-oss-ingest-pipeline/) | Batch or continuous ingestion from OSS, S3, or COS through Storage Connections, External Volumes, Pipes, and `COPY INTO`. |
| Data ingestion and pipelines | [clickzetta-kafka-ingest-pipeline](./clickzetta-kafka-ingest-pipeline/) | Kafka ingestion through `READ_KAFKA` Pipes or Kafka External Table plus Table Stream pipelines. |
| Data ingestion and pipelines | [clickzetta-batch-sync-pipeline](./clickzetta-batch-sync-pipeline/) | Studio offline batch sync tasks for single-table sync, multi-table mirrors, and sharded-table merge scenarios. |
| Data ingestion and pipelines | [clickzetta-realtime-sync-pipeline](./clickzetta-realtime-sync-pipeline/) | Studio single-table real-time sync tasks for Kafka, MySQL, PostgreSQL, and related sources. |
| Data ingestion and pipelines | [clickzetta-cdc-sync-pipeline](./clickzetta-cdc-sync-pipeline/) | Studio multi-table CDC sync from MySQL or PostgreSQL into Lakehouse, including full database mirror and sharded-table merge modes. |
| Data ingestion and pipelines | [clickzetta-sql-pipeline-manager](./clickzetta-sql-pipeline-manager/) | SQL-native management for Dynamic Tables, Materialized Views, Table Streams, Pipes, and layered SQL pipelines. |
| Data ingestion and pipelines | [clickzetta-table-stream-pipeline](./clickzetta-table-stream-pipeline/) | Table Stream change data capture workflows, offset handling, preview, consumption, and idempotent downstream writes. |
| Data ingestion and pipelines | [clickzetta-studio-task-manager](./clickzetta-studio-task-manager/) | Studio task creation, folder organization, scheduling, dependencies, deployment, task operations, and engineering conventions. |
| Data ingestion and pipelines | [clickzetta-pipeline-review](./clickzetta-pipeline-review/) | Pipeline review and diagnostics across Studio tasks, Lakehouse objects, pipeline SQL, and run histories. |
| Data ingestion and pipelines | [clickzetta-dbt-studio-pipeline](./clickzetta-dbt-studio-pipeline/) | Publish dbt models into Studio assets and configure scheduled execution from dbt artifacts. |
| Modeling and analytics | [clickzetta-dw-modeling](./clickzetta-dw-modeling/) | Data warehouse modeling for ODS/DWD/DWS/ADS, Medallion architecture, schema design, and pipeline-aware modeling. |
| Modeling and analytics | [clickzetta-dbt-project-setup](./clickzetta-dbt-project-setup/) | dbt-clickzetta project initialization, `profiles.yml`, `dbt_project.yml`, and layered project standards. |
| Modeling and analytics | [clickzetta-dbt-modeling](./clickzetta-dbt-modeling/) | dbt source discovery, model design, incremental materialization, tests, and model generation. |
| Modeling and analytics | [clickzetta-dynamic-table](./clickzetta-dynamic-table/) | Dynamic Table creation, refresh configuration, incremental computation, ALTER workflows, refresh history, and best practices. |
| Modeling and analytics | [clickzetta-data-science](./clickzetta-data-science/) | Data science workflows using SQL, ZettaPark, notebooks, EDA, feature engineering, inference, and vector retrieval. |
| Modeling and analytics | [clickzetta-semantic-view](./clickzetta-semantic-view/) | Semantic View modeling with logical tables, dimensions, metrics, filters, and semantic layer queries. |
| SDK and integrations | [clickzetta-cmt-api](./clickzetta-cmt-api/) | CMT v2 API operations: discover migration sources, plan and start runs, monitor progress, verify outcomes, inspect run logs, and clean up failed runs. |
| SDK and integrations | [clickzetta-zettapark](./clickzetta-zettapark/) | ZettaPark DataFrame API, Session setup, reads, transformations, writes, file operations, and SQL execution. |
| SDK and integrations | [clickzetta-spark-flink-connector](./clickzetta-spark-flink-connector/) | Spark Connector reads/writes and Flink Write Connector CDC or append-only writes. |
| SDK and integrations | [clickzetta-external-function](./clickzetta-external-function/) | External Functions, Python/Java UDF packaging, and cloud function integration. |
| SDK and integrations | [clickzetta-ai-function](./clickzetta-ai-function/) | Built-in AI functions: AI_COMPLETE (call LLMs) and AI_EMBEDDING (text vectors) with API CONNECTION setup. |
| Operations and governance | [clickzetta-volume-manager](./clickzetta-volume-manager/) | External Volume, User Volume, Table Volume, object storage mounting, file operations, import, and export. |
| Operations and governance | [clickzetta-table-lineage](./clickzetta-table-lineage/) | Table lineage and cost visualization based on `information_schema.job_history` and generated HTML artifacts. |
| Productivity | [screen-recording](./screen-recording/) | Screen recording narration workflow: pre-recording hook setup (auto-log user messages with Beijing timestamps) and post-recording footage manifest and shot script generation. |
| Observability | [singsight-install](./singsight-install/) | Connect AI coding agents (Claude Code, Hermes, OpenClaw, Opencode) to the Singsight observability platform via OpenTelemetry. |
| cz-cli operations | [cz-cli-agent](./cz-cli-agent/) | Default router for ClickZetta Lakehouse operations: direct `cz-cli` commands for simple ops, `cz-agent run` for complex/autonomous multi-step work. |
| cz-cli operations | [cz-cli-tool](./cz-cli-tool/) | Direct operator manual for `cz-cli` commands (SQL, tables, schemas, Studio tasks, sync/CDC pipelines, datasources, AI Gateway). Loaded by host agents and the cz-agent runtime. |

## cz-cli skills

Two peer skills operate ClickZetta Lakehouse via the `cz-cli` tool. Both are publicly installable; install either or both.

| Skill | Role |
|---|---|
| `cz-cli-agent` | Default entry. Routes by complexity: direct `cz-cli` commands for simple ops, `cz-agent run` for complex/autonomous multi-step work. |
| `cz-cli-tool` | Direct operator manual. Drives `cz-cli` commands directly with no agent runtime. Loaded by host agents and by the cz-agent runtime. |

**Routing:** if both are installed, `cz-cli-agent` is routed first (the default). `cz-cli-tool` is used when the user explicitly wants direct command execution, has no LLM configured for cz-agent, or `cz-cli-agent` is not installed.

> **Naming note:** `cz-cli-agent` and `cz-cli-tool` use the `cz-cli-` prefix (the `cz-cli` product brand) rather than the registry's usual `clickzetta-` prefix. They are the two sanctioned exceptions — see `CLAUDE.md`.

## Routing Guide

Use the table below when deciding which skill should handle a user request.

| User intent | Recommended entry point |
|---|---|
| Understand ClickZetta concepts, Workspace, Schema, VCluster, object hierarchy, or Studio modules. | `clickzetta-overview` |
| Configure Python, JDBC, SQLAlchemy, ZettaPark, or general Lakehouse connections. | `clickzetta-zettapark` / `lakehouse-doc-en` |
| Choose an ingestion method without knowing whether to use files, object storage, Kafka, batch sync, real-time sync, or CDC. | `clickzetta-data-ingest-pipeline` |
| Import files from a local path, URL, Volume, object storage, or Kafka. | `clickzetta-file-import-pipeline` / `clickzetta-oss-ingest-pipeline` / `clickzetta-kafka-ingest-pipeline` |
| Build Studio offline sync, single-table real-time sync, or multi-table CDC tasks. | `clickzetta-batch-sync-pipeline` / `clickzetta-realtime-sync-pipeline` / `clickzetta-cdc-sync-pipeline` |
| Manage Studio tasks, folders, schedules, dependencies, deployments, and task state. | `clickzetta-studio-task-manager` |
| Initialize a dbt project, build dbt models, or publish dbt models to Studio. | `clickzetta-dbt-project-setup` / `clickzetta-dbt-modeling` / `clickzetta-dbt-studio-pipeline` |
| Design SQL pipelines, Dynamic Tables, Materialized Views, Pipes, or Table Streams. | `clickzetta-sql-pipeline-manager` / `clickzetta-dynamic-table` / `clickzetta-table-stream-pipeline` |
| Review an existing pipeline, diagnose task failures, inspect dependencies, or identify data quality issues. | `clickzetta-pipeline-review` |
| Write native ClickZetta SQL, look up syntax, functions, permissions, VClusters, or official product behavior. | `lakehouse-doc-en` |
| Migrate SQL from Snowflake, Databricks, or Spark SQL. | `clickzetta-sql-migration` |
| Query metadata, table structures, job history, cost attribution, permissions, Time Travel, recovery, or platform operations. | `lakehouse-doc-en` |
| Investigate query performance, `EXPLAIN`, Result Cache, `OPTIMIZE`, small files, or execution plans. | `lakehouse-doc-en` |
| Manage users, roles, grants, masking policy, network policy, lifecycle, data sharing, SDK, BI, or Java/Python application docs. | `lakehouse-doc-en` |
| Manage Volumes, object storage mounts, file upload/download, import, or export. | `clickzetta-volume-manager` |
| Work with Spark, Flink, ZettaPark, External Functions, or External Catalogs. | `clickzetta-spark-flink-connector` / `clickzetta-zettapark` / `clickzetta-external-function` / `lakehouse-doc-en` |
| Operate ClickZetta Lakehouse via the cz-cli tool: run SQL, manage tables/schemas/Studio tasks, build sync or CDC pipelines, or configure profiles. | `cz-cli-agent` (default) / `cz-cli-tool` (direct) |

## Repository Layout

Each top-level skill is stored in one directory:

```text
clickzetta-<domain>/
├── SKILL.md
└── references/
    └── *.md
```

`SKILL.md` is the routing and workflow entry point. It should define:

- the skill name and trigger description in front matter;
- when the skill should and should not be used;
- the minimal workflow the agent should follow;
- which reference files to read for detailed syntax, examples, or troubleshooting.

`references/` contains detailed technical material, SQL snippets, operational playbooks, API notes, and examples. Agents should load only the specific reference files needed for the current task.

Some skills contain additional sub-skill or best-practice directories. For example:

```text
clickzetta-dynamic-table/
├── dt-creator/
├── sql-to-dt/
└── best-practices/
```

## Official Documentation Skill

`lakehouse-doc-en` is the authoritative fallback for native ClickZetta behavior. Use it when:

- a topic has been consolidated into official documentation rather than a dedicated operational skill;
- the user asks for SQL syntax, functions, permissions, VCluster behavior, data sharing, Time Travel, SDK, BI, AI functions, or other official product capabilities;
- a workflow skill needs product-level confirmation from the docs.

## Maintenance Notes

When adding, renaming, or deleting a skill:

1. Update the top-level skill directory.
2. Update `.well-known/skills/index.json`.
3. Update this `README.md` catalog and routing table.
4. Search the repository for stale skill references.

For deleted or consolidated topics, route users to `lakehouse-doc-en` unless there is another active task-specific skill that clearly owns the workflow.

## Usage

Install or expose this repository's skill directories to an AI coding assistant that supports `SKILL.md`-based skills. Users can then describe ClickZetta tasks directly, for example:

```text
Import CSV files from OSS into public.orders on a schedule.
```

```text
Build a CDC pipeline from MySQL to Lakehouse and publish it as a Studio task.
```

```text
Create a Dynamic Table for the DWS order summary layer and configure refresh behavior.
```

The assistant should route the request through the appropriate `SKILL.md`, read only the required references, and generate the concrete SQL, cz-cli commands, Studio workflow, or troubleshooting steps for the task.
