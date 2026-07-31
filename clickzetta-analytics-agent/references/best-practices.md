# Best Practices & Patterns

## ⚠️ Always Consult `--help`

Every analytics-agent command changes across versions. Always run `--help` before executing an unfamiliar command. Common version-sensitive areas:
- `answer-builder create`: DSL format, SQL separation, `metricName` requirements
- `domain table add`: positional vs flag arguments
- `session create` / `session run`: parameter requirements

## Domain Building Workflow (Efficient Order)

1. **Create domain** → get domainId
2. **Create schemas + load data** (background)
3. **Register dim tables first** (they load faster, enable fact table JOINs)
4. **Set dim table semantics and aliases**
5. **Register fact tables** (after data loading completes)
6. **Set fact table semantics and aliases**
7. **Create metrics** (from simple fact table aggregates)
8. **Create Answer Builders** (multi-table JOINs with v_gpt_ views)
9. **Upload Knowledge Base, set Domain Prompt**
10. **QA testing** (serial, single session)

## Naming Conventions

### Metrics
- Use business-domain Chinese names: `"出库总金额"`, `"试听转化率"`
- Avoid generic names that will conflict across domains: `"总金额"` → `"物流出库总金额"`
- Add `--alias` for natural-language synonyms users might ask: `"销售额"`, `"营收"`

### Answer Builders
- Name should match the question it answers: `"各仓库出库金额排名"`
- `outputColumn.name` should be a short SQL-friendly alias: `out_amt`, `ch_visitors`
- `outputColumn.metricName` must be domain-unique: `"各渠道访客数"` not `"访客数"`
- `outputColumn.alias` must not conflict with any metric alias in the domain

### Aliases
- 2-4 natural Chinese synonyms per key column
- What users actually say: `"品牌"` = `"汽车品牌"`, `"牌子"`
- Do NOT alias ID columns (`date_id`, `warehouse_id`)

## API Ergonomic Mistakes to Avoid

| Mistake | Correct |
|---|---|
| `domain table add --domain-id 315 --table "..."` | `domain table add 315 --table "..."` (positional, not flag) |
| Forgetting `--datasource-id <datasource-id>` on `domain table add` | Always include it; it's REQUIRED |
| AB SQL with physical table names | Use `v_gpt_*` view names |
| `--sql "${dims}"` (double-quoted) | `--sql '${dims}'` (single-quoted) |
| Creating AB without `metricName` | Include `metricName` in every `outputColumn` |
| Running QA in parallel (multiple simultaneous `session run`) | Serial only: wait for each answer before next question |

## Performance

### Parallelism Rules
- **Dim data loading**: can run in parallel across schemas
- **Fact data loading**: serial within a schema; parallel across schemas
- **`domain table add`**: serial within a schema (CZD-13005 conflict)
- **`semantics set`**: can batch in Python but expect 8-20s per call under load
- **Description-only updates** are 30-50% faster than full type+dimension resets

### Large Fact Tables
- 5000+ rows per table: use `cz-cli sql --write -f <file>` in background processes
- Total 58K rows (edu+ecom+hotel) took ~40 minutes via background loading
- Monitor with `SELECT COUNT(*)` periodically

## Semantic Coverage Targets

For a production-quality analytics domain:

| Metric | Target |
|---|---|
| Column description coverage | 100% (every column has a `description`) |
| Semantic type coverage | 100% (no column has unset/default type) |
| Key column alias coverage | 80%+ (dimension names, measures, dates have Chinese aliases) |
| Table count match | All physical tables in schema are registered |
| AB answer quality | 70%+ success rate on natural-language QA |

## Multi-Alias Strategy

Priority order for assigning aliases:
1. **Dimension names** (table/reference names): `brand_name`, `product_name`, `city`
2. **Status/category columns**: `status`, `order_status`, `book_status`
3. **Date columns**: `order_date`, `checkin_date`
4. **Measure columns**: `total_amount`, `quantity`, `price`
5. **Skip**: ID columns, internal keys, system columns

## AB Troubleshooting Pattern

When AB creation fails:

1. **Check the error message for exact conflict** — it names the conflicting object and its ID
2. **Check domain detail** for existing metric names and aliases
3. **Use `validate` command** before `create` to catch issues early
4. **If `domain missing tables`**, verify your SQL uses `v_gpt_*` view names
5. **If `${dims}` syntax error**, check shell quoting (single quotes around `--sql`)
6. **If HTTP 408 timeout**, reduce query complexity or wait for data to fully load

## Shell Quoting Reference

| Scenario | Correct |
|---|---|
| `--sql` with `${dims}` | Single quotes: `--sql 'SELECT ${dims}...'` |
| `--content` with JSON | Single quotes: `--content '{"chartParams":...}'` |
| `--prompt` with Chinese text | Python `shlex.quote()` for subprocess; single quotes for bash |
| `--description` with spaces | Double quotes: `--description "仓库名称"` |

## Session Configuration

```bash
# Optimal session setup for QA testing
MODEL="Qwen3.7 Max"            # Best for Chinese analytical queries
TIMEOUT_MS=180000               # 3 minutes for complex queries
SUMMARY=true                     # Get final answer, not poll payload
```
