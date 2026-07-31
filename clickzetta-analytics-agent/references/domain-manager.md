# Domain Manager — Domain Lifecycle & Table Management

## Domain CRUD

### Create a Domain

```bash
cz-cli analytics-agent domain create \
  --profile <profile> \
  --name "零售行业分析" \
  --description "基于零售场景的完整分析域，覆盖商品/客户/门店/日期维度及销售/库存事实表" \
  --datasource-id <datasource-id>
# Returns: domainId (e.g., 311)
```

### List Domains

```bash
cz-cli analytics-agent domain list --profile <profile> --format json
```

### Domain Detail (with tables)

```bash
cz-cli analytics-agent domain detail <domain-id> --with-tables --profile <profile> --format json
```

Key fields in detail response:
- `tables[]` — each entry has `datasetId`, `tableName` (v_gpt_ view), `physicalTable`, `displayName`
- `targetCounts` — `metric` (compound), `simple_metric`, `chart` (ABs), `kb_node`

### Domain Prompt

```bash
# Set domain-specific system prompt for QA sessions
cz-cli analytics-agent domain prompt set <domain-id> \
  --profile <profile> \
  --prompt "You are a retail industry data analyst expert. This domain contains..."

# Get current prompt
cz-cli analytics-agent domain detail <domain-id> --profile <profile>
# prompt is in domainConfigs.metricAnalysisCustomPrompt
```

## Table Registration

### Add a Table to Domain

```bash
cz-cli analytics-agent domain table add <domain-id> \
  --profile <profile> \
  --datasource-id <datasource-id> \
  --table "<workspace>.<schema>.<table>" \
  --display-name "自定义展示名"
```

**Note**: The positional argument `<domain-id>` must come before the options. Do not use `--domain-id <id>` for this command.

**Required parameters**: `--datasource-id`, `--table` (both marked REQUIRED in `--help`).

**Response**: Returns `datasetId` (for semantics/metric commands) and `datasetName` (v_gpt_ view name).

### Common Issues

| Issue | Cause | Fix |
|---|---|---|
| "domain X missing tables" in AB create | AB SQL references physical table name instead of v_gpt_ view | Use `v_gpt_*` view names in SQL |
| `domain table add` returns "ok" but table not in domain | `--datasource-id` was omitted | Always include `--datasource-id` |
| "table or view not found" | Physical table not yet created (data loading still running) | Wait for data loading to finish, retry |
| `datasetId` from `domain table add` is `ERR` | Table doesn't exist or schema mismatch | Verify table exists: `SHOW TABLES IN <schema>` |

### Remove a Table

```bash
cz-cli analytics-agent domain table remove <domain-id> <table-id>
```

## Dataset ID

After table registration, use `datasetId` for all column-level operations:

```bash
# List column semantics for a dataset
cz-cli analytics-agent table semantics list <dataset-id> --profile <profile> --format json
```

The `datasetId` is persistent — it stays the same even if you re-add the same physical table.

## Table Update

```bash
# Update display name
cz-cli analytics-agent table update <dataset-id> \
  --profile <profile> --display-name "自定义展示名称"
```

Note: `--display-name` may not take effect if the table was previously added and removed. This is a known issue — the workaround is to keep the first add's dataset intact.
