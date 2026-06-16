# ClickZetta Skills Development Specification

This document provides Skill development guidelines for AI Agents (Claude Code, cz-cli, etc.) and human developers.

## Repository Structure

```
clickzetta-skills/
├── .well-known/skills/index.json   ← Skill registry (must be kept in sync)
├── clickzetta-<name>/              ← One directory per Skill
│   ├── SKILL.md                    ← Main entry point (required)
│   └── references/                 ← Reference documents (optional)
│       └── *.md
├── CLAUDE.md                       ← This file (development spec)
└── README.md                       ← Repository README
```

## Skill Directory Naming

- Unified prefix: `clickzetta-<feature-name>`
- Use lowercase + hyphens: `clickzetta-dynamic-table`, `clickzetta-volume-manager`
- Names should reflect the functional domain, not be overly specific

## SKILL.md Specification

### Front-matter (Required)

```yaml
---
name: clickzetta-<name>
description: |
  One paragraph describing the Skill's scope (≤ 1024 chars).
  Triggered when the user says "keyword1", "keyword2".
  Keywords: english, keywords, for, LLM, matching
---
```

**Field Specification:**

| Field | Constraint | Description |
|---|---|---|
| `name` | ≤ 64 chars, required | Must match directory name; lowercase letters, digits, hyphens only |
| `description` | ≤ 1024 chars, required | Includes summary + trigger scenarios + Keywords line |

**name rules:**
- Format: `clickzetta-<feature-name>` (unified prefix)
- Only `[a-z0-9-]` allowed — no underscores or uppercase letters
- Length includes the prefix, e.g. `clickzetta-dynamic-table` = 25 chars
- If the feature name is too long, shorten it rather than omitting the prefix

**description rules:**
- **≤ 1024 characters** (including newlines and spaces); excess will be truncated by the platform
- Three-section structure, separated by blank lines:
  1. **Summary** (1-3 sentences): what this Skill does and its scope
  2. **Trigger scenarios** (optional): `Trigger when the user says: "..."` or `当用户说"…"时触发`
  3. **Keywords line** (required): `Keywords: comma, separated, english, words` — for LLM semantic matching
- Cover various user phrasings in triggers, but don't list so many that you exceed the limit
- When space is tight, prioritize the Keywords line and summary; trim trigger scenarios first

### Content Structure (Recommended)

1. **Quick Start** — 3-5 most common SQL examples
2. **Core Concepts** — brief explanations of key concepts
3. **Detailed Reference** — placed in `references/` subdirectory
4. **FAQ** — troubleshooting table (Issue | Cause | Solution)

## SQL Example Guidelines

### Must Follow

1. **All SQL must be verified in an actual environment** — do not write SQL from memory or inference
2. **Use ClickZetta-specific syntax** — do not use Snowflake/Spark/MySQL syntax
3. **Use `default` for VCluster names** — do not use `default_ap` (AP type doesn't support small-file merging)
4. **REFRESH syntax**: `REFRESH INTERVAL 10 MINUTE vcluster default` (not TARGET_LAG)
5. **COMMENT syntax**: Use `COMMENT '...'` in CREATE VCLUSTER (no equals sign)
6. **COPY INTO VOLUME export**: Use `FILE_FORMAT = (TYPE = CSV)` (not `USING CSV`)
7. **SHOW commands do not support**: ORDER BY, subqueries, SHOW TBLPROPERTIES
8. **SHOW TABLES column name**: `table_name` (not `name`)
9. **information_schema.columns**: has no `ordinal_position` column

### Formatting Requirements

```sql
-- Comment describing the purpose
CREATE DYNAMIC TABLE my_schema.my_dt
REFRESH INTERVAL 10 MINUTE vcluster default
AS
SELECT col1, col2
FROM source_table;
```

- SQL keywords in uppercase: `CREATE`, `SELECT`, `FROM`, `WHERE`
- Table/column names in lowercase
- Add a comment before each example describing its purpose
- Do not add LIMIT after SHOW/DESC commands (some don't support it)

## Adding a New Skill

1. Create directory `clickzetta-<name>/SKILL.md`
2. Write content, ensuring all SQL is verified
3. **Validate front-matter**:
   - `name` ≤ 64 chars and matches directory name
   - `description` ≤ 1024 chars and includes a Keywords line
   - Quick check command: `head -20 clickzetta-<name>/SKILL.md | grep -c "^---"`
4. Update `.well-known/skills/index.json` with a new entry:
   ```json
   {
     "name": "clickzetta-<name>",
     "description": "Brief description (matching SKILL.md description)",
     "files": ["SKILL.md", "references/xxx.md"]
   }
   ```
5. Update `README.md` Skills overview table, adding the new Skill to the appropriate category
6. Commit and push

## Modifying an Existing Skill

- Ensure no incorrect syntax is introduced after modification
- If unsure whether syntax is correct, verify in the Lakehouse environment first
- Include the reason for the change in the commit message (reference issue number)

## Common Error Patterns (Avoid)

| ❌ Wrong | ✅ Correct | Note |
|---|---|---|
| `REFRESH AUTO EVERY '1 hours'` | `REFRESH INTERVAL 60 MINUTE vcluster default` | MV/DT refresh syntax |
| `USING CSV` (in COPY INTO) | `FILE_FORMAT = (TYPE = CSV)` | USING is only for SELECT FROM VOLUME |
| `COMMENT = '...'` (in CREATE VCLUSTER) | `COMMENT '...'` | VCLUSTER doesn't use equals sign |
| `SHOW TBLPROPERTIES table` | `SHOW CREATE TABLE table` | SHOW TBLPROPERTIES doesn't exist |
| `WHERE name = 'x'` (in SHOW TABLES) | `WHERE table_name = 'x'` | Column name is table_name |
| `ORDER BY ordinal_position` | `ORDER BY column_name` | ordinal_position doesn't exist |
| `SHOW ... ORDER BY ...` | Not supported | SHOW commands don't support ORDER BY |
| `SELECT FROM (SHOW ...)` | Not supported | SHOW cannot be used as a subquery |
| `ALTER DYNAMIC TABLE ... SET REFRESH` | `CREATE OR REPLACE DYNAMIC TABLE ...` | Changing refresh requires rebuild |
| `vcluster default_ap` | `vcluster default` | General-purpose VC default name is default |
