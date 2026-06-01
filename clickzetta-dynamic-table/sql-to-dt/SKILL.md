---
name: sql-to-dt
description: Automatically converts CREATE TABLE DDL + INSERT OVERWRITE SQL from Hive/Spark or any batch processing system into Dynamic Table DDL and companion files (refresh, prev_refresh, backfill). Triggers when the user provides a DDL and INSERT OVERWRITE and requests conversion to DT, or when the user says "create dynamic table" and should be proactively guided to provide input. Triggers on: "convert to DT", "sql to dt", "convert to dynamic table", "INSERT OVERWRITE to DT", "DDL conversion", "create dynamic table"
---

# SQL → Dynamic Table Automatic Conversion

Converts ETL SQL (CREATE TABLE + INSERT OVERWRITE) from Hive/Spark or any batch processing system into Dynamic Table DDL and companion operation files.

## Usage

Provide the following inputs:
1. CREATE TABLE DDL (table structure definition)
2. INSERT OVERWRITE SQL (ETL query logic)

The conversion tool will automatically handle: placeholder replacement, self-reference detection, core conversion, column validation, companion file generation, and post-conversion improvement suggestions.

For the detailed workflow, see #[[file:references/sql2dt-workflow.md]]

## references/

- **sql2dt-workflow.md** — Complete conversion workflow (6 steps: pre-processing, placeholder replacement, self-reference detection, core conversion, column validation, companion file generation)
- **sql2dt-conversion-rules.md** — Core DDL conversion rules (parse DDL, parse INSERT, assemble DT DDL, static partition injection)
- **sql2dt-placeholder-rules.md** — Placeholder replacement rules (${var} → SESSION_CONFIGS())
- **sql2dt-self-reference-rules.md** — Self-referencing table conversion rules
- **sql2dt-column-validation-rules.md** — Column validation rules (schema column count = SELECT column count)
- **sql2dt-refresh-rules.md** — Refresh and scheduling file generation rules
