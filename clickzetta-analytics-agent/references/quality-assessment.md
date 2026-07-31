# Semantic Layer Quality Assessment

## Quality Dimensions

A production-ready analytics domain is evaluated across six dimensions. Four are **machine-checkable** from `domain detail` + `semantics list` and make up the 100-point automated score below; two (**Consistency**, **Freshness**) require human judgement and are covered by the manual checklist — they are *not* part of the automated number.

| Dimension | Automated weight | Assessed by | What It Measures |
|---|---|---|---|
| **Completeness** | 30 | Script | Are all columns described? |
| **Correctness** | 25 | Script | Are semantic types (date/numeric) and dimension flags accurate? |
| **Coverage** | 20 | Script | Are all physical tables registered? Are key dimension columns aliased? |
| **Usability** | 25 | Script | Do metrics/ABs exist, and are a KB and domain prompt configured? |
| **Consistency** | manual | Checklist | Are naming conventions, units, and descriptions uniform across tables? |
| **Freshness** | manual | Checklist | Are the domain prompt and KB up to date with the current data? |

The four automated weights sum to **100**, so a fully-configured domain can reach Grade A. Consistency and Freshness stay manual because neither can be reliably inferred from the CLI metadata alone.

## Automated Assessment Script

Run this Python script against any domain to get a quantitative quality score:

```python
import subprocess, json, sys

PROFILE = "<profile>"   # set to your cz-cli profile

def run(cmd, timeout=15):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return (r.returncode == 0, json.loads(r.stdout) if r.stdout.strip() else None)

def assess_domain(did):
    """Assess semantic layer quality for a domain. Returns score 0-100 + breakdown."""
    
    # Get domain detail
    ok, data = run(f"cz-cli analytics-agent domain detail {did} --with-tables --profile {PROFILE} --format json")
    if not ok: return {"error": "Cannot fetch domain"}
    d = data['data']
    tables = d.get('tables', [])
    tc = d.get('targetCounts', {})
    
    metrics = {
        "total_tables": len(tables),
        "registered_tables": 0,
        "total_columns": 0,
        "columns_with_description": 0,
        "columns_with_alias": 0,
        "dimension_columns_aliased": 0,
        "total_dimension_columns": 0,
        "columns_wrong_type": [],
        "date_columns_count": 0,
        "date_columns_correct_type": 0,
        "numeric_columns_count": 0,
        "numeric_columns_correct_type": 0,
    }
    
    # Assess each dataset
    for t in tables:
        ds_id = t['datasetId']
        physical_table = t['physicalTable']
        ok2, cols_data = run(
            f"cz-cli analytics-agent table semantics list {ds_id} --profile {PROFILE} --format json")
        if not ok2: continue
        
        cols = cols_data.get('data', [])
        metrics["registered_tables"] += 1
        
        for c in cols:
            code = c['attrCode']
            stype = c.get('semanticType', '')
            desc = c.get('description', '')
            alias = c.get('alias')
            dim = c.get('dimension', False)
            
            metrics["total_columns"] += 1
            
            # Completeness checks
            if desc:
                metrics["columns_with_description"] += 1
            if alias:
                metrics["columns_with_alias"] += 1
            
            # Correctness checks (type-specific)
            is_date = ('date' in code.lower() or 'time' in code.lower()) and '_id' not in code.lower()
            is_numeric = any(kw in code.lower() for kw in ['amount', 'price', 'cost', 'quantity', 'qty', 'count', 'rate', 'score', 'revenue', 'distance', 'weight', 'volume', 'mileage', 'speed', 'energy'])
            
            if is_date:
                metrics["date_columns_count"] += 1
                if stype == 'DATE_AND_TIME':
                    metrics["date_columns_correct_type"] += 1
                else:
                    metrics["columns_wrong_type"].append(f"{physical_table}.{code}: {stype} should be DATE_AND_TIME")
            
            if is_numeric:
                metrics["numeric_columns_count"] += 1
                if stype == 'CONTINUOUS':
                    metrics["numeric_columns_correct_type"] += 1
                else:
                    metrics["columns_wrong_type"].append(f"{physical_table}.{code}: {stype} should be CONTINUOUS")
            
            # Alias coverage for dimension columns
            if dim:
                metrics["total_dimension_columns"] += 1
                if alias:
                    metrics["dimension_columns_aliased"] += 1
    
    # Calculate scores — automated weights sum to 100 (Grade A is reachable)
    if metrics["total_columns"] == 0:
        return {"error": "No columns found"}

    def ratio(num, den, full_credit_when_absent=True):
        # A category with nothing to check (e.g. a domain with no date columns)
        # should not be penalized — award full credit rather than 0.
        if den == 0:
            return 1.0 if full_credit_when_absent else 0.0
        return num / den

    # Completeness (30): every column described
    completeness = round(ratio(metrics["columns_with_description"], metrics["total_columns"], False) * 30, 1)

    # Correctness (25): date columns typed DATE_AND_TIME (12) + numeric columns CONTINUOUS (13)
    date_correct = round(ratio(metrics["date_columns_correct_type"], metrics["date_columns_count"]) * 12, 1)
    num_correct  = round(ratio(metrics["numeric_columns_correct_type"], metrics["numeric_columns_count"]) * 13, 1)

    # Coverage (20): all physical tables registered (8) + dimension columns aliased (12)
    table_coverage = round(ratio(metrics["registered_tables"], metrics["total_tables"]) * 8, 1)
    alias_score    = round(ratio(metrics["dimension_columns_aliased"], metrics["total_dimension_columns"]) * 12, 1)

    # Usability (25): metrics/ABs exist (20) + KB (3) + domain prompt (2)
    ab_count = tc.get("chart", 0)
    metric_count = tc.get("simple_metric", 0) + tc.get("metric", 0)
    content_score = min(20, (ab_count * 4) + (metric_count * 1))
    kb_score = 3 if tc.get("kb_node", 0) > 0 else 0
    has_prompt = 2 if d.get('domainConfigs', {}).get('metricAnalysisCustomPrompt', '') else 0
    usability = content_score + kb_score + has_prompt

    total_score = round(
        completeness + date_correct + num_correct + table_coverage + alias_score + usability, 1)
    
    return {
        "domain_id": did,
        "domain_name": d['name'],
        "total_score": total_score,
        "grade": "A" if total_score >= 90 else ("B" if total_score >= 75 else ("C" if total_score >= 55 else "D")),
        "breakdown": {
            "completeness_desc": f"{metrics['columns_with_description']}/{metrics['total_columns']} columns described",
            "completeness": completeness,
            "alias_coverage": f"{metrics['dimension_columns_aliased']}/{metrics['total_dimension_columns']} dim columns aliased",
            "alias_score": alias_score,
            "date_type_correct": f"{metrics['date_columns_correct_type']}/{metrics['date_columns_count']} date cols correct",
            "date_score": date_correct,
            "numeric_type_correct": f"{metrics['numeric_columns_correct_type']}/{metrics['numeric_columns_count']} numeric cols correct",
            "numeric_score": num_correct,
            "table_coverage": table_coverage,
            "content_score": content_score,
            "kb_and_prompt": kb_score + has_prompt,
            "usability": usability,
            "wrong_types": metrics["columns_wrong_type"][:10]
        }
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python assess.py <domain-id>")
    result = assess_domain(int(sys.argv[1]))
    print(json.dumps(result, indent=2, ensure_ascii=False))
```

## Quality Grade System

| Score | Grade | Meaning | Action |
|---|---|---|---|
| 90-100 | **A** | Production-ready | Regular monitoring |
| 75-89 | **B** | Good, minor gaps | Fill missing descriptions/aliases |
| 55-74 | **C** | Moderate gaps | Systematic improvement needed |
| 0-54 | **D** | Incomplete | Full rebuild recommended |

Scores cover only the four automated dimensions (Completeness, Correctness, Coverage, Usability). Always pair a high score with the manual **Consistency** and **Freshness** checks below before declaring a domain production-ready.

## Manual Quality Checklist

For domains where automated assessment can't cover all dimensions:

### Completeness
- [ ] Every physical table in the schema is registered in the domain
- [ ] Every column has a non-empty `description`
- [ ] Every column has a correct `semanticType` (not default/unset)
- [ ] All date columns use `DATE_AND_TIME`
- [ ] All numeric measures use `CONTINUOUS`
- [ ] ID, category, and status columns use `CATEGORICAL`

### Correctness
- [ ] `dimension: true` for filterable/groupable columns (IDs, names, categories, statuses)
- [ ] `dimension: false` for pure measures (amounts, quantities, rates)
- [ ] Descriptions are meaningful business terms, not just column name translations
- [ ] DATE columns have `DATE 'YYYY-MM-DD'` format in INSERTs — implicit string-to-date cast disabled

### Coverage
- [ ] Top 3 dimension tables have 80%+ column alias coverage
- [ ] Key fact table measures (amount, quantity, count) have Chinese aliases
- [ ] At least 2-3 aliases per key dimension column (brand name, product, region)

### Consistency
- [ ] Amount/price columns consistently described with currency unit (元)
- [ ] Rate/percentage columns consistently annotated with applicable denominator
- [ ] Date columns consistently use the same description pattern across tables
- [ ] Status columns list all possible values in their descriptions

### Usability
- [ ] Domain prompt describes data scope, field values, and analysis guidance
- [ ] At least one Answer Builder triggers for each major analysis pattern
- [ ] Knowledge Base contains data documentation
- [ ] QA testing achieves 70%+ success rate across question types

### Freshness
- [ ] Domain prompt reflects current data range (not stale dates)
- [ ] KB documentation matches actual schema (not outdated)
- [ ] Metrics and ABs reference existing tables (no dead references)

## Common Quality Issues & Fixes

| Issue | Detection | Fix |
|---|---|---|
| Missing descriptions | `semantics list` scan | Batch `semantics set --description` |
| Wrong dimension flag | Manual review: ID columns marked as measures | `semantics set --dimension true` |
| Stale KB | KB file last-modified vs data date range | Re-upload updated KB file |
| Unused ABs | AB with `matchOutputColumn: unmatched` | Update AB SQL or remove |
| Duplicate metric names | `metric create` fails with DUPLICATE_NAME | Use `metric update` or choose unique name |
| Missing v_gpt_ views | ABs fail with "domain missing tables" | Add table to domain, wait for sync |
| Under-aliased dimensions | Low alias coverage on dimension columns | Batch `--alias` additions |
| Wrong semantic type | DATE column marked CATEGORICAL or vice versa | `semantics set --semantic-type DATE_AND_TIME` |

## Quality Improvement Workflow

1. **Assess**: Run the automated assessment script → get score and breakdown
2. **Prioritize**: Fix wrong types first (correctness > completeness)
3. **Execute**: Batch-fix descriptions, aliases, dimension flags
4. **Verify**: Re-run assessment → confirm score improvement
5. **QA Test**: Run representative natural-language questions → verify usability
6. **Monitor**: Re-assess monthly or after major schema changes
