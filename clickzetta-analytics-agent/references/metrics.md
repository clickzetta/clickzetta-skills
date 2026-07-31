# Metrics — Simple & Compound

## Metric Types

Both simple and compound metrics are created the same way — `metric create` with an `--expression`. There is **no `--type` flag**; the backend classifies the metric by the shape of the expression, which is reflected in `domain detail`'s `targetCounts` (`simple_metric` vs `metric`/compound).

| Kind | Expression shape | Example | `targetCounts` bucket |
|---|---|---|---|
| Simple | Single aggregate over one table | `SUM(total_amount)`, `COUNT(*)`, `AVG(score)` | `simple_metric` |
| Compound | Multi-aggregate / arithmetic expression | `SUM(defect)*100/SUM(total)`, `SUM(paid)/SUM(due)*100` | `metric` |

The `--expression` field accepts any valid SQL aggregate expression; you do not declare which kind it is.

## Creation

```bash
cz-cli analytics-agent metric create \
  --profile <profile> \
  --domain-id <domain-id> \
  --datasource-id <datasource-id> \
  --table-name "<workspace>.<schema>.v_gpt_<table>" \
  --name "出库总金额" \
  --expression "SUM(total_amount)" \
  --alias "出库金额" --alias "发货金额"
```

**Required**: `--domain-id`, `--datasource-id`, `--table-name`, `--name`, `--expression`.

**Important**: `--table-name` must use the `v_gpt_` view name, not the physical table name.

## Expressions

| Business Metric | Expression |
|---|---|
| Total | `SUM(total_amount)` |
| Count | `COUNT(*)` or `COUNT(DISTINCT user_id)` |
| Average | `AVG(price)` or `ROUND(AVG(score), 1)` |
| Rate/Percentage | `SUM(CASE WHEN condition THEN 1 ELSE 0 END)*100.0/COUNT(*)` |
| Boolean proportion | `SUM(CASE WHEN is_on_time THEN 1 ELSE 0 END)*100.0/COUNT(*)` |
| Ratio | `SUM(actual_amount)/SUM(promise_amount)` |

### Boolean Expressions

For TRUE/FALSE columns:
```sql
SUM(CASE WHEN is_converted THEN 1 ELSE 0 END)*100.0/COUNT(*)
-- or --
SUM(CASE WHEN is_on_time THEN 1 ELSE 0 END)
```

### Chinese String Comparisons in Expressions

**Avoid single quotes** in expressions when using shell commands (they'll be consumed). For metrics created via Python subprocess, Chinese strings work fine:
```python
expr = "SUM(CASE WHEN decision = '通过' THEN 1 ELSE 0 END)"
```
For shell, use Unicode escapes or double-quote the entire expression.

## Listing & Management

```bash
# List all metrics in a domain
cz-cli analytics-agent metric list --domain-id <domain-id> --profile <profile> --format json

# Enable/disable
cz-cli analytics-agent metric enable <metric-id> --profile <profile>
cz-cli analytics-agent metric disable <metric-id> --profile <profile>
cz-cli analytics-agent metric enable --all --domain-id <domain-id> --profile <profile>

# Detail
cz-cli analytics-agent metric detail <metric-id> --profile <profile>

# Delete
cz-cli analytics-agent metric delete <metric-id> --profile <profile>

# Update
cz-cli analytics-agent metric update <metric-id> --profile <profile> \
  --name "new name" --alias "new alias"
```

## Aliases

Metric aliases serve two purposes:
1. Natural-language matching in QA sessions
2. Display labels in charts

Aliases must be **unique across the domain** — including across metrics AND AB output columns.

```bash
--alias "销售额" --alias "营收" --alias "销售收入"
```

**Warning**: If a metric alias conflicts with an AB output column alias, the AB creation will fail with a "重名" error pointing to the metric ID.

## Metric vs Answer Builder Decision

| Use Case | Use |
|---|---|
| Single aggregate: "total sales" | Simple Metric |
| Ratio from one table: "conversion rate" | Simple Metric |
| Multi-table JOIN + GROUP BY | Answer Builder |
| Same metric with different GROUP BY options | Answer Builder |
| Multi-step calculation across tables | Answer Builder |

## Common Errors

Metric-specific errors below; for the full cross-cutting error catalog see [troubleshooting.md](troubleshooting.md) (canonical).

| Error | Cause |
|---|---|
| `domain X missing tables` | `--table-name` uses physical name — must use `v_gpt_` |
| Expression syntax error | Unsupported function or operator |
| Metric name already exists | Use `metric update <id>` instead of `create` |
| Alias conflicts with AB | AB creation fails; change either metric alias or AB alias |
