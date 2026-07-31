# Answer Builders — DSL Format & Creation

## Overview

Answer Builders (ABs) are complex multi-table analytics with chart configuration. They require:
- `--content`: JSON DSL with chartParams, outputColumns, relatedTables
- `--sql`: SQL body with `${dims}` and `${filters}` placeholders

## DSL Structure

```json
{
  "chartParams": [
    {
      "name": "dims",
      "type": "dimension",
      "allowMulti": false,
      "fromTableRefs": [
        {
          "tableName": "workspace.schema.v_gpt_dim_table",
          "columns": ["group_col1", "group_col2"]
        }
      ]
    },
    {
      "name": "filters",
      "type": "filter",
      "allowMulti": true,
      "fromTableRefs": [
        {
          "tableName": "workspace.schema.v_gpt_fact_table",
          "columns": ["date_col", "status_col"]
        }
      ]
    }
  ],
  "outputColumns": [
    {
      "name": "output_alias",
      "type": "double",
      "alias": ["显示别名1", "显示别名2"],
      "metricName": "域内唯一指标名称"
    }
  ],
  "relatedTables": [
    "workspace.schema.v_gpt_table1",
    "workspace.schema.v_gpt_table2"
  ]
}
```

### chartParams

| Field | Required | Description |
|---|---|---|
| `name` | ✅ | `"dims"` or `"filters"` — referenced in SQL as `${name}` |
| `type` | ✅ | `"dimension"` (GROUP BY) or `"filter"` (WHERE) |
| `allowMulti` | ✅ | `true` for multi-select, `false` for single |
| `fromTableRefs` | ✅ | Array of table references with `tableName` and `columns` |

### outputColumns

| Field | Required | Description |
|---|---|---|
| `name` | ✅ | MUST match the SQL `AS` alias exactly |
| `type` | ✅ | `"bigint"`, `"double"`, `"decimal"` |
| `metricName` | ✅ **REQUIRED** | Unique display name within the domain |
| `alias` | No | Array of display aliases (must not conflict with existing metric aliases) |

### relatedTables

Array of all `v_gpt_*` view names referenced in the SQL. Every table the SQL touches must be listed.

## SQL Format

```sql
-- Correct: use v_gpt_ view names and alias JOINs with short prefixes
SELECT ${dims}, 
       SUM(total_amount) AS out_amt, 
       COUNT(*) AS out_cnt
FROM workspace.schema.v_gpt_fact_table f
JOIN workspace.schema.v_gpt_dim_table d
  ON f.fk_id = d.pk_id
WHERE ${filters}
GROUP BY ${dims}
ORDER BY out_amt DESC
```

Note: When using `v_gpt_*` table names in JOINs, you can reference them by their full name or use short aliases. The `v_gpt_` prefix is enough — do not add extra `v_gpt_` wrappers.

### Critical Rules

1. **Use `v_gpt_*` view names** in SQL — physical table names cause "domain missing tables" error
2. **`${dims}` goes in SELECT and GROUP BY**; **`${filters}` goes in WHERE**
3. **Every `${name}` in SQL must have a matching chartParams entry**
4. **Shell quoting**: wrap `--sql` in single quotes so `${...}` placeholders reach the CLI intact. Double quotes cause shell expansion to empty strings.

## Creation

```bash
cz-cli analytics-agent answer-builder create \
  --profile <profile> \
  --domain-id <domain-id> \
  --datasource-id <datasource-id> \
  --analysis-name "各仓库出库金额排名" \
  --analysis-desc "按仓库统计出库总金额排名" \
  --content '{"chartParams":[...],"outputColumns":[...],"relatedTables":[...]}' \
  --sql 'SELECT ${dims}, SUM(total_amount) AS out_amt FROM ... WHERE ${filters} GROUP BY ${dims}'
```

## Update

```bash
cz-cli analytics-agent answer-builder update <analysis-id> \
  --profile <profile> \
  --analysis-name "<name>" \
  --analysis-desc "<desc>" \
  --datasource-id <datasource-id> \
  --domain-id <domain-id> \
  --content '<json>' \
  --sql '<sql>'
```

Update requires all parameters: `--analysis-name`, `--datasource-id`, `--domain-id`, `--content`, `--sql`.

## Validation

```bash
cz-cli analytics-agent answer-builder validate \
  --profile <profile> \
  --domain-id <domain-id> \
  --datasource-id <datasource-id> \
  --analysis-name "测试AB" \
  --content '<json>' \
  --sql '<sql>'
```

Returns `{"valid": true/false, "errors": [...]}`.

## Uniqueness Constraints

When creating an AB, the backend validates:

| Constraint | Error Message | Resolution |
|---|---|---|
| `metricName` is unique | `DUPLICATE_NAME` | Choose a different `metricName` |
| `outputColumn.alias` ≠ any metric alias | "重名" + metric ID | Remove/change conflicting alias |
| `outputColumn.alias` ≠ any other AB alias | "重名" + AB ID | Remove/change conflicting alias |

**Strategy**: If you hit a duplicate name error, the error message tells you exactly which existing object (metric or AB) conflicts. Use that information to craft a non-conflicting alias.

## Listing & Detail

```bash
# List all ABs in a domain
cz-cli analytics-agent answer-builder list \
  --profile <profile> --domain-id <domain-id> --format json

# Show full detail including content JSON and SQL
cz-cli analytics-agent answer-builder detail <analysis-id> --profile <profile>
```

## Enable/Disable

```bash
cz-cli analytics-agent answer-builder enable <analysis-id> --profile <profile>
cz-cli analytics-agent answer-builder disable <analysis-id> --profile <profile>
cz-cli analytics-agent answer-builder enable --all --domain-id <domain-id> --profile <profile>
```

## Common Errors

AB-specific errors below; for the full cross-cutting error catalog see [troubleshooting.md](troubleshooting.md) (canonical).

| Error | Cause | Fix |
|---|---|---|
| `domain X missing tables: [table1, table2]` | SQL references physical table names | Use `v_gpt_*` view names |
| `Cannot invoke "String.trim()" because "sql" is null` | `--sql` not passed or shell-expanded | Use single quotes: `'SELECT ${dims}...'` |
| `CZLH-42000 syntax error at ','` | `${dims}` expanded to empty by shell | Use single quotes around `--sql` |
| `答案构建器输出指标别名...重名` | AB alias conflicts with existing metric alias | Change `outputColumn.alias` to unique text |
| `domain X missing tables` with correct v_gpt_ names | Table not yet synced to domain | Wait ~30s after `domain table add`, retry |
