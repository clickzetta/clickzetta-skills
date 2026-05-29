---
name: clickzetta-dynamic-table
description: |
  ClickZetta Dynamic Table usage guide and routing hub.

  [Trigger scenarios]
  - General consultation: Dynamic Table introduction, usage, best practices, performance optimization, incremental configuration
  - Creation guidance: DT declaration strategy, SQL support matrix, refresh history queries
  - Modification operations: detected and automatically delegated to the dynamic-table-alter sub-skill
  - SQL conversion: detected and automatically delegated to the sql-to-dt sub-skill

  [Trigger keywords]
  "how to use dynamic table", "DT introduction", "dynamic table best practices", "dynamic table performance optimization",
  "incremental computation configuration", "dimension table JOIN", "dynamic table refresh history", "static partition DT",
  "dynamic partition DT", "state table management", "non-partitioned table risks", "create dynamic table",
  "dynamic table scheduling", "REFRESH INTERVAL", "dynamic table alerts"

  [Non-trigger scenarios]
  Modification operations ("modify dynamic table", "add column", "change interval", etc.) → use dynamic-table-alter
  SQL conversion ("convert to DT", "INSERT OVERWRITE to DT", etc.) → use sql-to-dt
---

# Dynamic Table Usage Guide — Routing & Index

This skill is the **knowledge hub and router** for ClickZetta Dynamic Tables. It provides reference documentation based on user intent, or automatically delegates to specialized operation sub-skills.

---

## Use Case Categories

### 1. General Consultation & Learning (handled by this skill)

**Applicable scenarios:**
- Looking up best practices and performance optimization recommendations
- Finding documentation for specific configuration options
- Learning how to create Dynamic Tables

**Trigger keywords:**
- "how to use dynamic table", "DT introduction", "what is Dynamic Table"
- "dynamic table best practices", "DT performance optimization", "dynamic table performance tuning"
- "incremental computation configuration", "refresh strategy", "state table management"
- "how to configure dimension table JOIN", "non-partitioned table risks"
- "how to query dynamic table refresh history", "REFRESH HISTORY"
- "static partition DT", "dynamic partition DT", "DT declaration strategy"
- "what SQL does dynamic table support", "dynamic table SQL limitations"
- "create dynamic table", "new dynamic table", "CREATE DYNAMIC TABLE"

**Handling:** Provide content and guidance from the relevant reference documents.

---

### 2. Modify an Existing Dynamic Table (automatically delegated to dynamic-table-alter sub-skill)

**Applicable scenarios:**
- Modifying the structure or properties of an existing Dynamic Table
- Suspending/resuming Dynamic Table refresh
- Adding/dropping columns, changing refresh interval, modifying query definition

**Trigger keywords:**
- "modify dynamic table", "add column to dynamic table", "drop column from dynamic table"
- "change refresh interval", "modify REFRESH_INTERVAL"
- "suspend dynamic table", "resume dynamic table", "SUSPEND", "RESUME"
- "rename column", "modify column comment", "modify table comment"
- "ALTER DYNAMIC TABLE", "CREATE OR REPLACE DYNAMIC TABLE"
- "modify DT query definition", "modify AS SELECT"

**Handling:**
> ⚠️ Modification intent detected — immediately load the dynamic-table-alter sub-skill.
> That sub-skill provides a complete workflow for 10 types of modification operations:
> - 5 direct ALTER operations: suspend, resume, set_comment, rename_column, set_column_comment
> - 5 CREATE OR REPLACE operations: add_column, drop_column, alter_column, set_refresh_interval, set_select

---

### 3. Convert SQL to Dynamic Table (automatically delegated to sql-to-dt sub-skill)

**Applicable scenarios:**
- Converting CREATE TABLE + INSERT OVERWRITE from Hive/Spark or any batch processing system to DT
- Bulk migration of traditional ETL to Dynamic Tables
- Auto-generating companion files for refresh, backfill, etc.

**Trigger keywords:**
- "convert to DT", "sql to dt", "convert to dynamic table"
- "INSERT OVERWRITE to DT", "DDL conversion"
- "Hive SQL to ClickZetta", "Spark SQL to dynamic table"
- "bulk convert ETL", "migrate to dynamic table"
- "create dynamic table", "new dynamic table", "CREATE DYNAMIC TABLE"

**Handling:**
> ⚠️ SQL conversion intent detected — immediately load the sql-to-dt sub-skill.
> If the user says "create dynamic table" but has not provided a DDL and INSERT OVERWRITE, proactively prompt:
> "Please provide the original CREATE TABLE DDL and INSERT OVERWRITE statement, and I can automatically generate the corresponding Dynamic Table DDL along with companion refresh and backfill files."
> That sub-skill provides a 6-step automatic conversion workflow:
> 1. Pre-process input (remove ALTER, ANALYZE, comments)
> 2. Placeholder replacement (convert to SESSION_CONFIGS)
> 3. Self-reference detection
> 4. Core conversion (merge DDL + INSERT into CREATE OR REPLACE)
> 5. Column validation
> 6. Generate companion files (refresh, prev_refresh, backfill)

---

## Knowledge Base Directory

### dt-creator/ — Dynamic Table Creation Reference

**Contents:**
- **dt-declaration-strategy.md** — Declaration strategy and selection between static partition DT and dynamic partition DT
  - Static partition DT: uses SESSION_CONFIGS() to pass partition parameters; each partition refreshes independently
  - Dynamic partition DT: no partition parameters; processes all incremental data in one pass
  - Decision tree: choose the appropriate partition strategy based on data patterns

- **sql-limitations.md** — SQL patterns supported by incremental computation (support status for JOIN, aggregation, window functions, etc., and limitations such as VIEW/external tables not supporting incremental)

- **incremental-config-reference.md** — Complete reference for incremental refresh configuration options
  - Refresh strategy: force full refresh, try incremental with fallback
  - Source table characteristic declarations: dimension tables, append-only tables
  - Full refresh fallback triggers: based on table changes or change volume
  - State table management: enable/disable, lifecycle, rebuild, schema specification
  - DT definition changes: compatibility check for CREATE OR REPLACE
  - Backfill: historical partition data correction
  - Partitioned table write behavior: overwrite vs append mode

- **refresh-history-guide.md** — 3 ways to query refresh history
  - SHOW DYNAMIC TABLE REFRESH HISTORY: job-level info, includes refresh_mode (INCREMENTAL/FULL/NO_DATA)
  - DESC HISTORY: version-level history, includes row count, bytes, operation type
  - information_schema.materialized_view_refresh_history: batch analysis, monitoring, CRU statistics

**Applicable questions:**
- "What is the difference between static partition DT and dynamic partition DT?"
- "What SQL syntax does Dynamic Table support?"
- "What configuration options are available for incremental computation?"
- "How do I view the refresh history of a Dynamic Table?"
- "What triggers a full refresh?"

---

### dynamic-table-alter/ — Dynamic Table Modification Guide

**Contents:**
- Complete Dynamic Table modification workflow (10 operation types)
- 5 direct ALTER operations: suspend, resume, set_comment, rename_column, set_column_comment
- 5 CREATE OR REPLACE operations: add_column, drop_column, alter_column, set_refresh_interval, set_select
- Platform-specific syntax and limitations (CHANGE COLUMN, RENAME COLUMN, DML restrictions, etc.)
- Detailed examples and troubleshooting

> ⚠️ This directory corresponds to the independent **dynamic-table-alter sub-skill**. When the user has a clear modification intent, load that sub-skill directly rather than this guide.

---

### sql-to-dt/ — SQL to DT Automatic Conversion

Fully automatically converts CREATE TABLE DDL + INSERT OVERWRITE from Hive/Spark or any batch processing system into Dynamic Table DDL and companion files (refresh, prev_refresh, backfill).

See the sql-to-dt sub-skill for detailed conversion rules.

---

### best-practices/ — Best Practices & Pitfall Guide

**Contents:**

- **performance-optimization.md** — Performance optimization strategies
  - Core principles: change ratio (< 5% is suitable for incremental), operator types (INNER JOIN faster than OUTER JOIN), data locality
  - SQL optimization tips: prefer INNER JOIN, reduce DISTINCT, window functions must have PARTITION BY, use partition conditions to limit data range
  - Pipeline splitting: break complex DTs into multiple stages

- **dimension-table-join-guide.md** — Dimension table JOIN scenarios in detail
  - Core mechanism: dimension table changes are ignored; only fact table changes trigger incremental computation
  - Configuration: TBLPROPERTIES('mv_const_tables'='dim1,dim2') or Session configuration
  - Recommended scenarios: lookup/dictionary tables, T+1 dimension + real-time fact table, large fact JOIN small dimension
  - Not recommended: frequently updated dimensions requiring real-time consistency
  - Data correction: must use full refresh after dimension table changes

- **non-partitioned-merge-into-warning.md** — Non-partitioned DT + continuous write risk alert
  - Trigger conditions: DT is non-partitioned + source table has continuous writes + SQL contains ROW_NUMBER() deduplication
  - Three risks: unbounded storage growth, archiving causes performance disaster, cannot filter archive-generated deletes
  - Recommended alternative: MERGE INTO + Table Stream (archive-immune, independent lifecycle management)

- **scheduling-guide.md** — Scheduling method selection guide
  - Comparison of two methods: DDL built-in scheduling (REFRESH INTERVAL) vs Studio Task scheduling
  - Always recommend Studio Task when Studio is available: supports upstream/downstream dependencies, unified alerts, visual monitoring
  - Drawbacks of DDL built-in scheduling: no alerts, no dependency orchestration, refresh status can only be checked via manual SQL
  - Studio Task configuration: must enable self-dependency, configure failure/timeout alerts, configure upstream dependencies as needed
  - Scheduling orchestration for multi-level DT pipelines

**Applicable questions:**
- "How do I optimize Dynamic Table performance?"
- "How do I configure dimension table JOIN?"
- "What are the risks of non-partitioned Dynamic Tables?"
- "When should I not use Dynamic Tables?"
- "Should I use REFRESH INTERVAL or Studio Task for Dynamic Table scheduling?"
- "How do I receive alerts when a Dynamic Table refresh fails?"

---

## Routing Decision Tree

```
User question
    │
    ├─ Contains modification keywords?
    │   ("modify dynamic table", "add column", "change interval", "suspend", "ALTER DYNAMIC TABLE")
    │   └─ Yes → immediately load dynamic-table-alter sub-skill
    │
    ├─ Contains SQL conversion keywords?
    │   ("convert to DT", "sql to dt", "INSERT OVERWRITE to DT", "DDL conversion", "create dynamic table")
    │   └─ Yes → immediately load sql-to-dt sub-skill
    │
    └─ General consultation/learning?
        ("how to use dynamic table", "best practices", "performance optimization", "incremental config")
        └─ Yes → provide reference documents from this guide
```

---

## Usage Recommendations

1. **First-time learning**: start with dt-creator/ to understand DT declaration strategies and configuration options
2. **Migration scenarios**: use the sql-to-dt sub-skill to bulk-convert existing ETL
3. **Day-to-day operations**: use the dynamic-table-alter sub-skill to modify DT structure
4. **Performance tuning**: refer to optimization recommendations and pitfall guides in best-practices/
5. **Scheduling configuration**: always use Studio Task scheduling when Studio is available; refer to best-practices/scheduling-guide.md

---

## Related Skills

- **dynamic-table-alter** — Operational sub-skill for modifying Dynamic Tables (10 modification operation types)
- **sql-to-dt** — Conversion sub-skill for SQL to DT (6-step automatic conversion workflow)
