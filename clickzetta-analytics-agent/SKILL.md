---
name: clickzetta-analytics-agent
description: |
  Complete guide for managing ClickZetta Analytics Agent domains via cz-cli:
  domain CRUD, table registration, column semantics (types/descriptions/aliases),
  metrics (simple & compound), Answer Builders, Knowledge Bases, and QA testing.
  Wizard-driven workflows with intent classification, routing tables, and
  troubleshooting references.
  Trigger when the user says: "analytics agent", "分析域", "语义层", "指标",
  "answer builder", "知识库", "多别名", "column semantics", "domain prompt",
  "metric create", "AB create", "session run", "domain table add",
  "semantics set", "knowledge space".
  Keywords: analytics agent, domain, semantics, metric, answer builder, knowledge base, alias, cz-cli, data analysis, AI agent, semantic layer
---

# ClickZetta Analytics Agent Manager

**References** (read when you need depth):

| Topic | File |
|---|---|
| Domain lifecycle & table management | [references/domain-manager.md](references/domain-manager.md) |
| Column semantics & multi-aliases | [references/table-semantics.md](references/table-semantics.md) |
| Metrics (simple & compound) | [references/metrics.md](references/metrics.md) |
| Answer Builder DSL & SQL format | [references/answer-builders.md](references/answer-builders.md) |
| Knowledge Base management | [references/knowledge-base.md](references/knowledge-base.md) |
| QA testing & sessions | [references/qa-testing.md](references/qa-testing.md) |
| Quality assessment (scoring, grades, checklists) | [references/quality-assessment.md](references/quality-assessment.md) |
| Best practices & patterns | [references/best-practices.md](references/best-practices.md) |
| Troubleshooting & error reference | [references/troubleshooting.md](references/troubleshooting.md) |

---

## Wizard: Clarify Intent

On receiving an analytics agent request, classify the user's intent:

> **A. Build a new analytics domain** (from schema tables → full domain with semantics, metrics, ABs) → [Domain Setup Wizard](#domain-setup-wizard)
> **B. Modify existing domain** (add/remove tables, update semantics, add metrics or ABs) → [Modification Workflow](#modification-workflow)
> **C. Test / QA a domain** (run natural-language questions, verify results) → [references/qa-testing.md](references/qa-testing.md)
> **D. Assess semantic quality** (evaluate completeness, correctness, coverage of an existing domain) → [references/quality-assessment.md](references/quality-assessment.md)
> **E. Fix configuration issues** (missing descriptions, alias conflicts, duplicate metricNames) → [references/troubleshooting.md](references/troubleshooting.md)
> **F. Improve semantic coverage** (add descriptions, aliases, refine metrics) → [references/table-semantics.md](references/table-semantics.md)

If the user has stated clearly what they want, execute directly without asking.

---

## Core Concepts

### Object Hierarchy

```
Domain (domainId)
  ├── Tables (datasetId) — registered via `domain table add`
  │     └── Columns (attrId) — semantic types, descriptions, aliases
  ├── Metrics — simple or compound (both via `metric create`; classified by expression)
  ├── Answer Builders — multi-table SQL + chart config
  ├── Knowledge Base — uploaded documents bound to domain
  └── Domain Prompt — custom system prompt for QA
```

### Dataset ID Flow

Tables added to a domain generate a **dataset ID** (`datasetId`). The analytics agent creates `v_gpt_*` views for each physical table. **All AB SQL must reference `v_gpt_*` view names, not physical table names.**

```
Physical table:  quickstart_ws.schema.dim_warehouse
Registered as:  quickstart_ws.schema.v_gpt_dim_warehouse  ← use this in AB SQL
datasetId:      1972  ← use this in semantics/metric commands
```

### Metrics vs Answer Builders

| | Simple Metric | Answer Builder |
|---|---|---|
| Scope | Single aggregate over one table | Multi-table JOIN + GROUP BY |
| Create | `metric create` | `answer-builder create` |
| DSL | Just expression | chartParams + outputColumns + SQL |
| Chart | Auto | Explicit chartParams |
| metricName | Auto (name) | **REQUIRED** in outputColumns |

---

## Domain Setup Wizard

Triggered by: "build analytics domain", "create semantic layer", "set up analytics agent for X schema".

### Phase 1: Register Tables

```bash
# For each table in the schema:
cz-cli analytics-agent domain table add <domain-id> \
  --profile <profile> --datasource-id <datasource-id> \
  --table "<workspace>.<schema>.<table>"

# Verify with:
cz-cli analytics-agent domain detail <domain-id> --with-tables --profile <profile>
```

**Critical**: Always pass `--datasource-id` (required). Tables that fail to load should be retried after data is available — the `domain table add` call will fail with a "table or view not found" error if the physical table doesn't exist yet.

### Phase 2: Set Column Semantics

For each registered table, configure column properties. See [references/table-semantics.md](references/table-semantics.md).

Minimum required per column:
- **semanticType**: `CATEGORICAL` (dimension), `CONTINUOUS` (measure), `DATE_AND_TIME` (date)
- **description**: Chinese or English business description
- **dimension**: `true` for filterable/groupable columns, `false` for pure measures

```bash
# Set semantic type + description + dimension flag
cz-cli analytics-agent table semantics set <dataset-id> <attr-id> \
  --profile <profile> \
  --semantic-type "CATEGORICAL" \
  --description "仓库名称" \
  --dimension true

# Add Chinese aliases (repeatable)
cz-cli analytics-agent table semantics set <dataset-id> <attr-id> \
  --profile <profile> \
  --alias "仓库" --alias "仓名" --alias "仓储地点"
```

### Phase 3: Create Metrics

```bash
# Simple metric (single aggregate)
cz-cli analytics-agent metric create \
  --profile <profile> --domain-id <domain-id> --datasource-id <datasource-id> \
  --table-name "<workspace>.<schema>.v_gpt_<table>" \
  --name "出库总金额" \
  --expression "SUM(total_amount)" \
  --alias "出库金额" --alias "发货金额"
```

### Phase 4: Create Answer Builders

See [references/answer-builders.md](references/answer-builders.md) for full DSL format.

Key rules (violating any causes creation failure):
1. **SQL must use `v_gpt_*` view table names**, not physical names
2. **`metricName` is REQUIRED** in every `outputColumn` — and must be unique within the domain
3. **`outputColumn` aliases** must not match any existing metric alias in the domain
4. Shell quote `--sql` with single quotes so `${dims}` and `${filters}` reach the CLI intact

```bash
cz-cli analytics-agent answer-builder create \
  --profile <profile> --domain-id <domain-id> --datasource-id <datasource-id> \
  --analysis-name "各仓库出库金额排名" \
  --analysis-desc "按仓库统计出库总金额排名" \
  --content '{"chartParams":[...],"outputColumns":[...],"relatedTables":[...]}' \
  --sql 'SELECT ${dims}, SUM(total_amount) AS out_amt FROM ... WHERE ${filters} GROUP BY ${dims}'
```

### Phase 5: Knowledge Base & Domain Prompt

```bash
# Create KB space
cz-cli analytics-agent knowledge space create \
  --profile <profile> --name "行业知识库"

# Upload KB file and bind to domain in one step
cz-cli analytics-agent knowledge file upload <space-id> <local-file> \
  --profile <profile> --domain-id <domain-id> \
  --target-path "docs/" --name "数据说明.md"

# Set domain prompt
cz-cli analytics-agent domain prompt set <domain-id> \
  --profile <profile> --prompt "You are a domain expert..."
```

---

## Key Syntax & Constraints

### DATE Literals in SQL

| ❌ Wrong | ✅ Correct |
|---|---|
| `'2025-01-01'` | `DATE '2025-01-01'` |

Implicit string-to-DATE cast is NOT supported. Always use `DATE 'YYYY-MM-DD'`.

### AB DSL Format

```json
{
  "chartParams": [
    {"name":"dims","type":"dimension","allowMulti":false,
     "fromTableRefs":[{"tableName":"cat.schema.v_gpt_table","columns":["col1"]}]},
    {"name":"filters","type":"filter","allowMulti":true,
     "fromTableRefs":[{"tableName":"cat.schema.v_gpt_table","columns":["date_col"]}]}
  ],
  "outputColumns": [
    {"name":"out_col","type":"double","alias":["显示别名"],"metricName":"域内唯一指标名"}
  ],
  "relatedTables": ["cat.schema.v_gpt_table1","cat.schema.v_gpt_table2"]
}
```

### Uniqueness Rules

| Rule | Error Pattern | Fix |
|---|---|---|
| `metricName` unique within domain | DUPLICATE_NAME with conflict source | Choose a globally unique name |
| `outputColumn.alias` ≠ existing metric alias | "重名" pointing to metric ID | Use different alias text |
| `outputColumn.alias` ≠ other AB's alias | "重名" pointing to AB ID | Use different alias text |

---

## Modification Workflow

### Adding a new table to existing domain

```bash
cz-cli analytics-agent domain table add <domain-id> \
  --profile <profile> --datasource-id <datasource-id> \
  --table "<workspace>.<schema>.<table>"
# Then set semantics, aliases, create new metrics as needed
```

### Fixing missing column descriptions

```bash
# List columns for a dataset, find missing descriptions
cz-cli analytics-agent table semantics list <dataset-id> --profile <profile> --format json

# Set description only (faster than full type+dimension reset)
cz-cli analytics-agent table semantics set <dataset-id> <attr-id> \
  --profile <profile> --description "业务含义"
```

### Updating an Answer Builder

```bash
cz-cli analytics-agent answer-builder update <analysis-id> \
  --profile <profile> --analysis-name "<name>" --analysis-desc "<desc>" \
  --datasource-id <datasource-id> --domain-id <domain-id> \
  --content '<json>' --sql '<sql>'
```

---

## QA Testing Quick Start

```bash
# Create named session
cz-cli analytics-agent session create \
  --profile <profile> --domain-id <domain-id> \
  --title "测试会话"

# Run a question (always pass --domain-id even with --session-id)
cz-cli analytics-agent session run \
  --profile <profile> --domain-id <domain-id> --session-id <session-id> \
  --msg "总行驶里程是多少？" \
  --model-name "Qwen3.7 Max" --summary --timeout-ms 180000
```

**QA must be serial** — do not submit the next question before the previous one answers.

**Model name is case-sensitive**: `"Qwen3.7 Max"` works; `"qwen3.7 max"` may silently fail.

---

## Common Pitfalls

| Pitfall | Manifestation | Root Cause |
|---|---|---|
| AB SQL uses physical table name | "domain X missing tables" | Must use `v_gpt_*` view names |
| `metricName` missing from outputColumn | `create` silently accepts it; `detail` shows it missing; `update` can add it | `--help` says REQUIRED but `create` doesn't enforce it; always include `metricName` during `create` |
| AB alias conflicts with metric alias | "重名" error pointing to metric ID | `outputColumn.alias` must be globally unique |
| Missing `--datasource-id` on `domain table add` | "ok" returned but table not added | `--datasource-id` is required; missing it silently fails |
| Shell `${dims}` expanded to empty | `SELECT , ` syntax error | Use single quotes around `--sql` |
| Parallel fact table loading | CZD-13005 DATASET_CREATE_VIEW_FAILED | Load fact tables serially per schema |
| DATE column implicit cast | "cannot write incompatible data" | Use `DATE 'YYYY-MM-DD'` |
| Session QA without `--domain-id` | "USAGE_ERROR" | Always pass `--domain-id` even with `--session-id` |

---

## Related Skills

| User Intent | Load This Skill |
|---|---|
| Data warehouse modeling (ODS/DWD/DWS layers) | `clickzetta-dw-modeling` |
| Studio task management & scheduling | `clickzetta-studio-task-manager` |
| Data ingestion pipeline selection | `clickzetta-data-ingest-pipeline` |
| dbt project setup & modeling | `clickzetta-dbt-project-setup` |
| Table lineage & dependency analysis | `clickzetta-table-lineage` |
| Comment & annotation management | `clickzetta-manage-comments` |

---

## ⚠️ Always Read `--help` First

Every cz-cli command in this skill has been verified against the current version, but **the `--help` output is the single source of truth**. Parameter names, required flags, and DSL formats can change between versions. Before executing any command for the first time in a session, run:

```bash
cz-cli analytics-agent <subcommand> --help
```

This prevents the most common class of errors: assuming a parameter format from memory that has changed in a newer version. For example, `answer-builder create` in v1.17.20 moved SQL from inline JSON (`content.sql`) to a separate `--sql` parameter — a breaking change immediately visible in `--help`.
