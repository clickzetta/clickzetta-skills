# Table Semantics — Column Types, Descriptions & Multi-Aliases

## Column Object

Each column in a registered table is an **attribute** (`attrId`) under a **dataset** (`datasetId`). View with:

```bash
cz-cli analytics-agent table semantics list <dataset-id> --profile <profile> --format json
```

Response fields per column:
```json
{
  "attrId": "51452",
  "datasetId": "1972",
  "attrCode": "warehouse_name",
  "description": "仓库名称",
  "semanticType": "CATEGORICAL",
  "alias": null,
  "intendedTypes": ["FILTER"],
  "hidden": false,
  "dimension": true,
  "index": false
}
```

## Semantic Types

| Type | Use For | Example Columns |
|---|---|---|
| `CATEGORICAL` | Text categories, IDs, enumerations | `brand_name`, `status`, `region` |
| `CONTINUOUS` | Numeric measures | `total_amount`, `quantity`, `price` |
| `DATE_AND_TIME` | Date/timestamp columns | `order_date`, `checkin_date` |

## Setting Column Semantics

### Full Set (type + description + dimension + intended-type)

```bash
cz-cli analytics-agent table semantics set <dataset-id> <attr-id> \
  --profile <profile> \
  --semantic-type "CATEGORICAL" \
  --description "仓库名称（中心仓/中转仓/前置仓）" \
  --dimension true \
  --intended-type "FILTER"
```

### Description-Only Update (Faster)

When only the description is missing, use description-only to avoid resetting type/dimension:

```bash
cz-cli analytics-agent table semantics set <dataset-id> <attr-id> \
  --profile <profile> \
  --description "运输距离（公里）"
```

This is significantly faster than a full reset, especially when batch-fixing hundreds of columns.

### Dimension Flag

- `--dimension true`: Column can be used as a GROUP BY field or filter
- `--dimension false`: Pure measure column (should be aggregated, not grouped)

## Multi-Aliases

Aliases are Chinese natural-language synonyms that the QA agent uses to match user questions to columns.

### Setting Aliases

```bash
cz-cli analytics-agent table semantics set <dataset-id> <attr-id> \
  --profile <profile> \
  --alias "销售额" --alias "营收" --alias "收入"
```

### Best Practices

- **Use 2-4 natural Chinese synonyms** per column, not programmatic identifiers
- Alias what users would naturally say: `"销售额"` not `"total_amount"`
- **Do NOT alias IDs** — `date_id`, `warehouse_id` are internal keys that users don't query
- Focus on: dimension names (brand, product, region), measures (amount, quantity, rate), date fields

### The DATE_AND_TIME Workaround (for `table update`)

When running `table update` on a dataset whose columns include DATE_AND_TIME semantic types, the backend validator may block with:
```
event time of type string set, time format needs to be specified
```

Workaround:
1. Temporarily set the column to `CATEGORICAL`: `--semantic-type "CATEGORICAL"`
2. Run the table update
3. Set it back to `DATE_AND_TIME`: `--semantic-type "DATE_AND_TIME"`

### Semantic Coverage Checklist

For a production-ready domain, ensure:
- **100% of columns have descriptions** — run `table semantics list` and check `description` field
- **100% of columns have correct semanticTypes** — no column should have unset/default type
- **Key dimension columns have aliases** — at least `brand_name`, `product_name`, `region`, `status`-type columns
- **All amount/quantity columns have `dimension: false`** — prevents grouping on raw measures

## Batch Discovery Script

To find all columns missing descriptions across a domain:

```python
import subprocess, json

def check_domain(did, profile):
    r = subprocess.run(
        f"cz-cli analytics-agent domain detail {did} --with-tables --profile {profile} --format json",
        shell=True, capture_output=True, text=True, timeout=15)
    d = json.loads(r.stdout)['data']
    missing = []
    for t in d.get('tables', []):
        ds_id = t['datasetId']
        r2 = subprocess.run(
            f"cz-cli analytics-agent table semantics list {ds_id} --profile {profile} --format json",
            shell=True, capture_output=True, text=True, timeout=10)
        if r2.returncode != 0: continue
        for c in json.loads(r2.stdout).get('data', []):
            if not c.get('description'):
                missing.append((ds_id, c['attrId'], c['attrCode'], t['physicalTable']))
    return missing
```
