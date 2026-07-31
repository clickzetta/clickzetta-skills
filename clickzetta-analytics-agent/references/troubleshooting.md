# Troubleshooting & Error Reference

## Common Errors by Phase

### Table Registration

| Error | Full Message Pattern | Cause | Fix |
|---|---|---|---|
| Table not found | `table or view not found - quickstart_ws.schema.table` | Physical table doesn't exist (data not loaded yet) | Wait for data loading, retry |
| Silent failure | Command returns "ok" but table not in domain detail | `--datasource-id` was omitted from `domain table add` | Always include `--datasource-id <datasource-id>` |
| View creation conflict | `CZD-13005 DATASET_CREATE_VIEW_FAILED` | Parallel table loading conflicts on shared schema | Load fact tables serially per schema |
| Invalid control char | Python JSON parse error on response | Table doesn't exist, cz-cli output contains error text not JSON | Check table existence first with `SHOW TABLES` |

### Column Semantics

| Error | Cause | Fix |
|---|---|---|
| `implicit cast not allowed for 'col1': string not null to date` | DATE column received string literal instead of DATE literal | Always use `DATE 'YYYY-MM-DD'` in INSERTs |
| `event time of type string set, time format needs to be specified` | Backend validator blocks table update with DATE_AND_TIME columns | Workaround: temp switch to CATEGORICAL → update → back to DATE_AND_TIME |
| `semantics set` timeout (>15s) | Backend slow under load or large number of pending operations | Use description-only updates (`--description` without re-setting type), or batch in background |
| Description not saved | Only set `--alias` or `--semantic-type` without `--description` | All four fields are independent; setting one doesn't affect others |

### Metrics

| Error | Cause | Fix |
|---|---|---|
| `domain X missing tables: [table_name]` | `--table-name` uses physical name instead of v_gpt_ view name | Use `v_gpt_` prefixed name |
| Metric "ok" but not showing in domain detail | Domain detail counters are eventually consistent | Wait 10-30 seconds, re-check |
| Metric with same name exists | DUPLICATE_NAME error | Use unique name or update existing metric: `metric update <metric-id>` |

### Answer Builders

| Error | Cause | Fix |
|---|---|---|
| `domain X missing tables` with v_gpt_ names in SQL | Table just added, not yet synced | Wait 30-60s after `domain table add`, retry |
| `${dims}` expanded to empty | Shell double-quote or no-quote on `--sql` | Always single-quote `--sql` |
| DUPLICATE_NAME on metricName | `metricName` matches existing metric or AB | Check domain detail for existing metric names, choose unique name |
| `重名` on output alias | AB alias matches existing metric alias | Error message identifies conflicting object ID — choose different alias |
| `Cannot invoke "String.trim()" because "sql" is null` | `--sql` omitted or shell-expanded to empty | Verify `--sql` is passed and `${...}` intact |
| HTTP 408 timeout | Server-side 30s timeout; SQL execution too slow | Wait for data loading to complete, retry; reduce query complexity |

### Knowledge Base

| Error | Cause | Fix |
|---|---|---|
| "A knowledge base with the name 'X' already exists" | Duplicate KB space name | Use `knowledge space list` to find existing space, or use a different name |
| KB upload succeeds but `kb_node=0` in domain detail | Domain binding didn't complete | Re-upload with `--domain-id` flag |

### Sessions & QA

| Error | Cause | Fix |
|---|---|---|
| `--domain-id is required` even with `--session-id` | Both are required for `session run` | Always pass `--domain-id` alongside `--session-id` |
| `Task execution failed` (~3s response) | Agent query planning failed (bad JOIN, unsupported aggregation) | Simplify question, check column names match schema |
| Session timeout | Default timeout too short for complex queries | Use `--timeout-ms 180000` (3 min) for complex analytical queries |
| Consecutive failures after working queries | Session state corruption or rate limiting | Create a fresh session |
| QA partial results (timeout) | Backend 30s hard limit | Reduce query scope, use more specific date ranges |

## Delivery Checklist

After building a domain, verify:

- [ ] All tables registered (`domain detail --with-tables` shows expected count)
- [ ] All columns have descriptions (`semantics list` for each dataset, check `description` field)
- [ ] All columns have correct `semanticType` (no unset/default type columns)
- [ ] Key columns have Chinese aliases (dimension names, measures, status fields)
- [ ] Metrics return correct values (run a `session run` query for each)
- [ ] Answer Builders are enabled and match (`validate` before `create`)
- [ ] Domain prompt describes data coverage, field values, and analysis guidance
- [ ] Knowledge Base is uploaded and domain-bound (`kb_node >= 1`)
- [ ] At least one successful QA session with 3+ question types (single value, ranking, trend, comparison)

## Debugging Tools

```bash
# Get full domain state
cz-cli analytics-agent domain detail <id> --with-tables --profile <p> --format json

# Check column semantics coverage
cz-cli analytics-agent table semantics list <dataset-id> --profile <p> --format json \
  | python3 -c "import sys,json; cols=json.load(sys.stdin)['data']; \
    print(f'Total: {len(cols)}, Desc: {sum(1 for c in cols if c.get(\"description\"))}, Aliased: {sum(1 for c in cols if c.get(\"alias\"))}')"

# List all ABs
cz-cli analytics-agent answer-builder list --domain-id <id> --profile <p> --format json

# Validate AB before creation
cz-cli analytics-agent answer-builder validate \
  --profile <p> --domain-id <id> --datasource-id <datasource-id> \
  --analysis-name "test" --content '<json>' --sql '<sql>'
```
