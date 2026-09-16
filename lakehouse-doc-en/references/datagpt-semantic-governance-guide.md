# Metrics Definition System and Validation Operations Guide

This document is intended for Analytics Agent semantic governance and operations personnel. It explains how the three mechanisms — metrics, Answer Builders, and the knowledge base — work together, and covers the validation and operations work required before delivery.

Analytics Agent provides three definition mechanisms — **Metrics**, **Answer Builder**, and **Knowledge Base** — which together form the context that the LLM uses to understand business semantics. This document explains the applicable boundaries of each, how they work together, and the validation and operations work required before delivery.

## Overview

All three are DSLs (domain-specific languages) for the LLM. The LLM reads them to understand business semantics and then generates SQL on its own. They are not executable instructions for the database — this is the prerequisite for understanding all the rules that follow.

| Mechanism | Form | Role |
|---|---|---|
| Metrics | Single-table aggregation expression | Definition — fixes single-table metric calculation logic using aggregation expressions, and tells the LLM "this domain has this metric" |
| Answer Builder | Multi-table SQL template + dimension declarations | Analysis template — fixes cross-table JOIN paths and aggregation definitions using SQL templates, and tells the LLM "this concept supports drilling down by these dimensions" |
| Knowledge Base | Markdown documents | Free text — supplements business rules, formula descriptions, and analysis scenarios |

> **Tip**: Examples in this document use a retail coffee sales domain, demonstrated with `v_gpt_*` views under the `sales_demo` schema. Replace `<domain-id>` and `<datasource-id>` in commands with your own domain's actual values (query with `cz-cli analytics-agent domain list`).

## Metrics

### When to Use

Use metrics (rather than Answer Builder) when **all** of the following conditions are met:

- All fields come from a single table
- The expression is a pure aggregation (SUM/COUNT/AVG/MAX/MIN) — no subqueries, no window functions
- String comparison values in the expression are directly available on the GPT view (no dependency on virtual columns)
- No programmatic time-series API calls needed (`metric_calculate`)

### Creating

```bash
cz-cli analytics-agent metric create \
  --domain-id <domain-id> --datasource-id <datasource-id> \
  --table-name "sales_demo.v_gpt_fact_order" \
  --name "GMV" \
  --expression "ROUND(SUM(CASE WHEN order_status = 'completed' THEN gross_amount ELSE 0 END), 2)" \
  --alias "Total Revenue" --alias "Revenue" \
  --description "Total listed price of completed orders (gross_amount, before discounts)"
```

### Notes

**Do not reference virtual columns.** Virtual columns (`column virtual set`) are not persisted to the GPT view — the following will throw an error:

```sql
-- Incorrect: virtual column is_completed_flag cannot be resolved in the GPT view
SUM(is_completed_flag)

-- Correct: inline CASE WHEN
SUM(CASE WHEN order_status = 'completed' THEN 1 ELSE 0 END)
```

**Do not use correlated subqueries.** GPT views do not support outer references in correlated subqueries, causing silent errors:

```sql
-- Incorrect: outer reference is lost in GPT view, returns wrong value without error
CASE WHEN (SELECT COUNT(*) FROM v_gpt_fact_order fo2
           WHERE fo2.member_key = v.member_key) = 1 THEN ...

-- Correct: use Answer Builder with GROUP BY instead
```

> **Note**: Rule of thumb — if you find yourself writing a subquery or window function inside a metric expression, stop and use an Answer Builder instead.

### Complete Examples

The following metrics represent typical best-practice usage:

```
GMV
  Expression: ROUND(SUM(CASE WHEN order_status='completed' THEN gross_amount ELSE 0 END), 2)
  Aliases: "Total Revenue", "Revenue", "Listed GMV"
  Description: Total listed price of completed orders. Single table (fact_order), pure aggregation, no subqueries.

Average Order Value
  Expression: ROUND(SUM(CASE WHEN order_status='completed' THEN net_amount ELSE 0 END)
              / NULLIF(SUM(CASE WHEN order_status='completed' THEN 1 ELSE 0 END), 0), 2)
  Description: Both numerator and denominator have filters applied. NULLIF prevents division by zero.

Average Delivery Cost per Order
  Expression: ROUND(SUM(CASE WHEN fulfillment_type='delivery' AND order_status='completed'
              THEN delivery_fee_cost ELSE 0 END)
              / NULLIF(SUM(CASE WHEN fulfillment_type='delivery' AND order_status='completed'
              THEN 1 ELSE 0 END), 0), 2)
  Description: Filters on both fulfillment_type and order_status simultaneously.
```

## Answer Builder

### When to Use

Use Answer Builder when **any** of the following conditions are met:

1. **Cross-table**: The metric calculation or dimensions involve multiple tables
2. **Dimension drill-down needed**: Users need "see Y by X" type analysis
3. **Subqueries/window functions needed**: The expression exceeds pure aggregation capability
4. **Lock JOIN path needed**: Eliminate ambiguity in multi-table scenarios

### Creating

An Answer Builder contains a DSL (`--content`) and a SQL template (`--sql`):

```bash
cz-cli analytics-agent answer-builder create \
  --domain-id <domain-id> --datasource-id <datasource-id> \
  --analysis-name "Store-Level Profit Proxy" \
  --analysis-desc "Net revenue minus (delivery + commission) aggregated by store" \
  --content '{...}' \
  --sql "SELECT \${dims}, ... GROUP BY \${dims}"
```

### DSL Field Reference

| Field | Required | Description |
|---|---|---|
| `chartParams[].name` | Yes | Placeholder name, referenced in SQL as `${name}`. Convention: `dims` and `filters` |
| `chartParams[].type` | Yes | `dimension` or `filter` |
| `chartParams[].fromTableRefs[].tableName` | Yes | Full GPT view path |
| `chartParams[].fromTableRefs[].columns` | Yes | Available dimension/filter columns. Must match actual column names in the GPT view and be resolvable in the SQL template FROM/JOIN |
| `outputColumns[].name` | Yes | Must exactly match the `AS` alias in SQL |
| `outputColumns[].metricName` | Yes | Unique within the domain. Recommend `ab_` prefix to avoid conflicts with metric names |
| `outputColumns[].type` | Yes | Singdata data type |
| `outputColumns[].stdTypeName` | Yes | Standard type (int / double / string) |
| `relatedTables` | Yes | Full paths of all GPT views used in the SQL |

### SQL Template Writing Rules

**String constants: use chr() concatenation**

Due to shell quote conflicts, string constants must be concatenated using `chr()`:

```sql
-- Incorrect: single quotes conflict with shell quotes
WHERE order_status = 'completed'

-- Correct
WHERE order_status = chr(99)||chr(111)||chr(109)||chr(112)||chr(108)||chr(101)||chr(116)||chr(101)||chr(100)
```

Common ASCII codes: c=99, o=111, m=109, p=112, l=108, e=101, t=116, d=100, '=39, -=45

**`${dims}` placement rules**

```
Correct: SELECT ${dims}, agg1, agg2 FROM ... GROUP BY ${dims}

Correct: SELECT * FROM (SELECT ${dims}, agg1 FROM ... GROUP BY ${dims}) t

Incorrect: SELECT ${dims}, total FROM (SELECT ch AS channel, COUNT(*) AS total FROM ...) t
   → Column renamed across subquery boundary causes resolution failure
```

**Window functions**: place inside a subquery, wrap with outer `SELECT *`:

```sql
SELECT * FROM (
  SELECT ${dims}, COUNT(*) AS cnt,
         ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS rnk
  FROM ... GROUP BY ${dims}
) t
```

**CTEs**:

```sql
WITH t AS (
  SELECT ${dims}, COUNT(*) AS cnt FROM ... GROUP BY ${dims}
) SELECT * FROM t
```

### SQL Template Examples

The following examples cover common complexity levels from single-table to multi-table JOIN.

**Example 1: Single table + filter (simplest pattern)**

Scenario: Count orders and GMV by channel and fulfillment type, with optional order status filter.

```sql
SELECT ${dims},
       COUNT(DISTINCT fo.order_id) AS orders,
       ROUND(SUM(CASE WHEN fo.order_status =
             chr(99)||chr(111)||chr(109)||chr(112)||chr(108)||chr(101)||chr(116)||chr(101)||chr(100)
             THEN fo.net_amount ELSE 0 END), 2) AS gmv
  FROM sales_demo.v_gpt_fact_order fo
 WHERE ${filters}
 GROUP BY ${dims}
```

Corresponding chartParams: dims can be `channel`, `fulfillment_type`, `pay_method`; filters can be `order_status`, `channel`.

**Example 2: Two-table JOIN + dimension drill-down**

Scenario: Count GMV and orders by store dimensions (name/city/trade zone/format).

```sql
SELECT ${dims},
       COUNT(DISTINCT fo.order_id) AS orders,
       ROUND(SUM(CASE WHEN fo.order_status =
             chr(99)||chr(111)||chr(109)||chr(112)||chr(108)||chr(101)||chr(116)||chr(101)||chr(100)
             THEN fo.net_amount ELSE 0 END), 2) AS gmv
  FROM sales_demo.v_gpt_dim_store ds
  JOIN sales_demo.v_gpt_fact_order fo
    ON ds.store_key = fo.store_key
 GROUP BY ${dims}
```

Corresponding chartParams: dims can be `store_name`, `city`, `city_tier`, `trade_zone_type`, `store_format`.

Key point: dimension columns come from dim_store, measures come from fact_order — the typical pattern for cross-table dimension drill-down.

**Example 3: Three-table JOIN (order → item → product)**

Scenario: Count sales volume and GMV by product category and date.

```sql
SELECT ${dims},
       SUM(foi.quantity) AS cups,
       ROUND(SUM(foi.item_gross_amount - foi.item_discount_amount), 2) AS revenue
  FROM sales_demo.v_gpt_fact_order fo
  JOIN sales_demo.v_gpt_fact_order_item foi
    ON fo.order_id = foi.order_id
  JOIN sales_demo.v_gpt_dim_sku ds
    ON foi.sku_key = ds.sku_key
 WHERE fo.order_status =
       chr(99)||chr(111)||chr(109)||chr(112)||chr(108)||chr(101)||chr(116)||chr(101)||chr(100)
 GROUP BY ${dims}
```

Corresponding chartParams: dims can be `category_l1`, `category_l2`, `sku_name`, `year`, `month`.

Key point: three-table chain JOIN (fact_order → fact_order_item → dim_sku), aggregation on the item table.

**Example 4: Subquery + ROW_NUMBER ranking**

Scenario: Count orders by channel and rank them. Because `${dims}` cannot share the same column with ROW_NUMBER's PARTITION BY, the window function is placed in the inner subquery and the outer level uses `SELECT *` to wrap it.

```sql
SELECT * FROM (
  SELECT ${dims},
         COUNT(DISTINCT order_id) AS orders,
         ROW_NUMBER() OVER (ORDER BY COUNT(DISTINCT order_id) DESC) AS rank
    FROM sales_demo.v_gpt_fact_order fo
   GROUP BY ${dims}
) t
```

Corresponding chartParams: dims can be `channel`, `fulfillment_type`, `order_status`.

Key points: (1) Window function placed in the inner subquery, outer `SELECT *` wraps it — this is the only reliable pattern for using window functions in an AB; (2) `${dims}` is used directly in the inner layer for GROUP BY and SELECT, in the same scope as ROW_NUMBER.

> **Note**: If you need PARTITION BY on a column outside `${dims}` (e.g., "store ranking within city tiers"), where the PARTITION BY column cannot simultaneously appear in `${dims}`'s GROUP BY, this scenario exceeds current AB template capability. Consider splitting into two ABs (one for aggregation, one for ranking), or letting the LLM generate the SQL on its own in an Agent conversation.

**Example 5: INNER JOIN subquery — member pre-aggregation**

Scenario: Analyze repurchase rate by membership tier — first use a subquery to count orders per member, then JOIN to the member dimension.

```sql
SELECT ${dims},
       COUNT(DISTINCT m.member_key) AS total_members,
       COUNT(DISTINCT CASE WHEN o.order_cnt >= 2
             THEN m.member_key END) AS repurchase_members,
       ROUND(COUNT(DISTINCT CASE WHEN o.order_cnt >= 2
             THEN m.member_key END) * 100.0
             / NULLIF(COUNT(DISTINCT m.member_key), 0), 2) AS repurchase_rate
  FROM sales_demo.v_gpt_dim_member m
  JOIN (SELECT member_key,
               COUNT(*) AS order_cnt
          FROM sales_demo.v_gpt_fact_order
         WHERE order_status =
               chr(99)||chr(111)||chr(109)||chr(112)||chr(108)||chr(101)||chr(116)||chr(101)||chr(100)
         GROUP BY member_key) o
    ON m.member_key = o.member_key
 GROUP BY ${dims}
```

Corresponding chartParams: dims can be `member_tier`, `register_channel`, `city`.

Key points: (1) Use INNER JOIN (not LEFT JOIN) to ensure the denominator is "members with purchase history"; (2) the subquery only does pre-aggregation and does not reference `${dims}` — dims in the outer layer come directly from dim_member; (3) this is the standard pattern for replacing correlated subqueries on GPT views.

**Example 6: Fact table + multiple dimension table join — stockout analysis**

Scenario: Analyze stockout days, stockout rate, and out-of-stock duration by product and month.

```sql
SELECT ${dims},
       SUM(CASE WHEN fss.stockout_flag = 1
           THEN 1 ELSE 0 END) AS stockout_days,
       ROUND(SUM(CASE WHEN fss.stockout_flag = 1
             THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 2) AS stockout_rate,
       SUM(CASE WHEN fss.stockout_flag = 1
           THEN fss.stockout_hours ELSE 0 END) AS stockout_hours
  FROM sales_demo.v_gpt_fact_store_stockout fss
  JOIN sales_demo.v_gpt_dim_sku ds
    ON fss.sku_key = ds.sku_key
  JOIN sales_demo.v_gpt_dim_date dd
    ON fss.date_key = dd.date_key
 GROUP BY ${dims}
```

Corresponding chartParams: dims can be `sku_name`, `category_l1`, `category_l2`, `year`, `month`, `stockout_reason`.

Key points: (1) Fact table (stockout) JOINs two dimension tables simultaneously (dim_sku + dim_date); (2) `stockout_flag` serves both as a filter condition and a count object inside the aggregation function.

### Validate Before Creating

```bash
cz-cli analytics-agent answer-builder validate \
  --domain-id <domain-id> --datasource-id <datasource-id> \
  --analysis-name "..." --content '...' --sql '...'
```

> **Note**: Passing validation does not mean the LLM will execute that template. Validation only checks syntax and column reference validity. Whether the Agent actually uses it must be confirmed through bypass testing (see "Testing and Validation" below).

## Metrics and Answer Builder Coexistence

### When You Need Both

| Scenario | Metric provides | Answer Builder provides |
|---|---|---|
| Coupon redemption rate | Global single value (Dashboard) | Drill-down by campaign/channel/time |
| Store profit | Global average profit (summary) | Comparison by store/city/format |
| Repurchase rate | Global repurchase rate (single value) | Breakdown by membership tier/channel/city |

### Calculation Definition Consistency

When both coexist, the calculation definitions must stay consistent. Recommend noting the source in AB's outputColumns:

```
description: "Same calculation definition as the 'Repurchase Rate' metric — members with >= 2 completed purchases as a percentage"
```

## Knowledge Base

### Recommended Content

| Document | Content |
|---|---|
| metric-definitions.md | Calculation formulas, filter conditions, and units for all metrics |
| business-rules.md | Enumeration value meanings, membership tiers, order statuses |
| analysis-scenarios.md | SQL templates for 3–5 typical analysis scenarios |
| data-model.md | Table structure, JOIN relationship diagram, core fields |

### Three-Source Consistency Rule

Recommended workflow:

1. First define the calculation definition in KB (as documentation)
2. Then create the metric (register as a calculation object)
3. If dimension drill-down is needed, create an Answer Builder (declare dimensions)
4. In the AB's description, back-reference the KB section
5. When there is a conflict between the three sources, KB takes precedence — update metric and AB accordingly

## Testing and Validation

### Bypass Validation Method

The Agent may rewrite expressions or ignore AB templates. The only reliable validation is SQL bypass testing:

1. Ask the Agent a question and get a response
2. Extract key values from the Agent's response
3. Write equivalent SQL using the same data source, JOIN path, and filter conditions
4. Compare values — accurate to two decimal places

```sql
-- Validate Agent's "Average Gross Profit per Order: ¥29.84"
SELECT ROUND(SUM(CASE WHEN order_status='completed'
  THEN net_amount - delivery_fee_cost - platform_commission + platform_subsidy
  ELSE 0 END) / NULLIF(SUM(CASE WHEN order_status='completed' THEN 1 ELSE 0 END), 0), 2)
FROM fact_order;
```

### Unreliable Validation Methods

- Agent returned no error → may return a plausible but incorrect value
- Value is within a reasonable range → a 2% deviation is invisible to the naked eye
- Agent referenced KB text → may have referenced it but calculated using a different formula
- AB validation passed → validation only checks syntax; the Agent may not execute it

### Testing Checklist

| Validation item | Method |
|---|---|
| Expression correctness | SQL bypass comparison value by value |
| JOIN path correctness | Query both paths with same-name columns separately; confirm Agent chose the right table |
| Filter condition completeness | Boundary test: "including cancelled" vs "completed only" |
| Dimension drill-down availability | Ask Agent "see Y by X" |
| Period-over-period baseline | Cross-period comparison to validate time window |

## Operations Best Practices

This chapter describes the standardized operational process for disambiguation, latent issue elimination, and bypass testing of analysis domains using CZ-CLI. In all command examples, replace `<domain-id>`, `<datasource-id>`, and table IDs with your own domain's actual values.

### Disambiguation

Ambiguity occurs when the same symbol maps to multiple different meanings in the system. A typical example: a same-named column represents different concepts across tables (e.g., `city` means both store city and member's home city), and the Agent may choose the wrong JOIN path without reporting an error.

**Full column semantic scan**

```bash
# Iterate over all table columns in the domain
for dsid in $(cz-cli analytics-agent domain detail <domain-id> --with-tables --format json | \
  python3 -c "import sys,json; [print(t['datasetId']) for t in json.load(sys.stdin)['data']['tables']]"); do
  cz-cli analytics-agent table columns $dsid --format json
done
```

Extract key fields for each column: `attrCode` (column name), `semanticType` (type), `description` (description), `intendedTypes` (intended uses).

**Cross-table duplicate column name detection**

Deduplicate all column names and find those appearing in more than one table:

```python
columns_by_table = {table: {col['attrCode'] for col in cols} for table, cols in scan_result}
all_cols = set.union(*columns_by_table.values())
duplicates = {c for c in all_cols if sum(1 for cols in columns_by_table.values() if c in cols) > 1}
```

**Compare semantics group by group**

For each group of duplicate-named columns, compare their `description` to determine whether they are synonymous (used for JOIN) or have different meanings (need disambiguation):

| Judgment | Example | Action |
|---|---|---|
| Synonymous (JOIN key) | `member_key` in dim_member and fact_order | No action needed |
| Different meanings (different business concepts) | `city` in dim_store (store city) vs dim_member (member's home city) | Needs disambiguation |
| Granularity confusion | `discount_amount` in fact_order (order level) vs order_item (SKU level) | Needs annotation |

**Data validation**

For columns with different meanings, query whether different JOIN paths produce different results:

```sql
-- Path A: store city (correct)
SELECT ROUND(SUM(CASE WHEN fo.order_status='completed' THEN fo.net_amount ELSE 0 END),0) AS gmv
FROM fact_order fo JOIN dim_store ds ON fo.store_key = ds.store_key
WHERE ds.city = 'Shanghai';

-- Path B: member city (incorrect)
SELECT ROUND(SUM(CASE WHEN fo.order_status='completed' THEN fo.net_amount ELSE 0 END),0) AS gmv
FROM fact_order fo JOIN dim_member dm ON fo.member_key = dm.member_key
WHERE dm.city = 'Shanghai';

-- If the two values differ and the gap > 1%, confirm the risk
```

**Execute disambiguation**: Update column descriptions to annotate JOIN paths and usage differences:

```bash
cz-cli analytics-agent table semantics set <table-id> <col-id> \
  --description "City where the store is located (JOIN path: fact_order→dim_store. Use this column to analyze consumption location or store performance; use dim_member.city for member domicile analysis)"

cz-cli analytics-agent table semantics set <table-id> <col-id> \
  --description "Member's home city (JOIN path: fact_order→dim_member. This column represents the member's domicile/residence, not where the transaction occurred. Use dim_store.city for store/regional performance analysis)"
```

### Latent Issue Elimination

Latent issues are defects where the system currently reports no error, but will produce systematically wrong results under certain conditions. Unlike ambiguity — ambiguity is "the Agent doesn't know which path to take" — latent issues are "the Agent thinks it chose correctly, but the result is wrong."

**Metric expression audit**

Check each metric's expression for the following defects:

| Defect | Detection method | Fix |
|---|---|---|
| Missing order_status filter | Check expression for WHERE completed or equivalent CASE WHEN | Add status filter to both numerator and denominator |
| Virtual column reference | Query the column; if it reports "cannot resolve," the virtual column is not persisted | Change to inline CASE WHEN |
| No division-by-zero protection | Division expression has no NULLIF on denominator | Add NULLIF(..., 0) |
| Correlated subquery | Expression contains (SELECT ... WHERE outer.col = inner.col) | Correlated subqueries are unreliable on GPT views — use Answer Builder with GROUP BY instead |

```bash
# Check each metric
cz-cli analytics-agent metric list --domain-id <domain-id> --format json | \
  python3 -c "import sys,json; [print(m['id'], m['names'][0], m['aggExpr']) for m in json.load(sys.stdin)['data']]"
```

**Semantic type consistency check**: Detect whether the same type of columns (Boolean/flag) are consistently labeled. Check items include `semanticType` (CATEGORICAL/CONTINUOUS), `dimension` (true/false), `intendedTypes` (DIM/FILTER/MEASURE). A common issue is flag columns being mislabeled as MEASURE instead of DIM — cross-compare and standardize.

**Dead dimension detection**: For columns labeled as CATEGORICAL DIM, check the actual value distribution. Dimensions with NULL rate > 90% or distinct values <= 1 should be hidden:

```sql
-- Detect dead dimensions
SELECT 'product_family' AS col,
       COUNT(DISTINCT product_family) AS distinct_vals,
       ROUND(SUM(CASE WHEN product_family IS NULL THEN 1.0 ELSE 0 END)/COUNT(*)*100, 0) AS null_pct
FROM dim_sku;
-- If distinct=1 and null_pct=95 → dead dimension, should be hidden=true
```

```bash
# Hide dead dimensions
cz-cli analytics-agent table semantics set <table-id> <col-id> --hidden true
```

**Cross-table data consistency check**: Verify that enumeration values for the same business concept are consistent across different tables (e.g., channel names). Inconsistency causes cross-table aggregation mismatches:

```sql
SELECT channel, COUNT(*) FROM fact_order GROUP BY channel;
SELECT issue_channel, COUNT(*) FROM fact_coupon GROUP BY issue_channel;
-- If fact_order has "Douyin Group Buy Redemption" and fact_coupon has "Douyin Live Group Buy" → enumeration values need to be unified
```

**GPT view correlated subquery validation**: For metrics containing subqueries, execute them against both the physical table and the GPT view and compare whether results are consistent:

```sql
-- Physical table validation (expected correct)
SELECT ROUND(100.0 - COUNT(DISTINCT CASE WHEN
  (SELECT COUNT(*) FROM fact_order fo2 WHERE fo2.member_key = fo.member_key
   AND fo2.order_status = 'completed') = 1 THEN fo.member_key END)
  * 100.0 / NULLIF(COUNT(DISTINCT fo.member_key), 0), 2) AS rate
FROM fact_order fo;
-- → 92.25%

-- GPT view validation (outer reference may be lost, returns wrong value without error)
SELECT ROUND(100.0 - COUNT(DISTINCT CASE WHEN
  (SELECT COUNT(*) FROM sales_demo.v_gpt_fact_order fo2 WHERE fo2.member_key = v.member_key
   AND fo2.order_status = 'completed') = 1 THEN v.member_key END)
  * 100.0 / NULLIF(COUNT(DISTINCT v.member_key), 0), 2) AS rate
FROM sales_demo.v_gpt_fact_order v;
-- → 100.00% (wrong! GPT view correlated subquery lost outer reference)
```

### Bypass Testing

Bypass Testing means building an independent SQL validation channel outside the Agent's output path — recalculating results using the same data source and calculation logic, then comparing each value. This is the only reliable validation method — no errors from the Agent does not mean the results are correct.

**Ask the Agent and record key values**

```bash
cz-cli analytics-agent session create --domain-id <domain-id> --title "test" --format json
cz-cli analytics-agent session run --session-id <sid> --domain-id <domain-id> \
  --msg "What is the repurchase rate by membership tier" --summary --format json
```

Extract verifiable value assertions from the Agent's response, for example: Standard member repurchase rate 90.32%, Gold member repurchase rate 97.33%, Overall repurchase rate 92.19%.

**Write equivalent SQL**

Use the same calculation definition the Agent claims to use (if stated) or one consistent with the domain definition:

```sql
-- Corresponding to Agent's answer "Overall repurchase rate 92.19%"
WITH member_orders AS (
  SELECT m.member_key, m.member_tier,
         COUNT(fo.order_id) AS order_cnt
    FROM dim_member m
    JOIN fact_order fo ON m.member_key = fo.member_key
     AND fo.order_status = 'completed'
   GROUP BY m.member_key, m.member_tier
)
SELECT member_tier,
       COUNT(DISTINCT member_key) AS total,
       COUNT(DISTINCT CASE WHEN order_cnt >= 2 THEN member_key END) AS repurchase,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN order_cnt >= 2 THEN member_key END)
             / NULLIF(COUNT(DISTINCT member_key), 0), 2) AS rate
  FROM member_orders
 GROUP BY member_tier
 ORDER BY rate;
```

**Compare values one by one**

| Tier | Agent | SQL | Deviation | Judgment |
|---|---|---|---|---|
| Standard | 90.32% | 90.32% | 0 | Pass |
| Gold | 97.33% | 97.33% | 0 | Pass |
| Overall | 92.19% | 92.19% | 0 | Pass |

**Deviation classification**

| Deviation range | Classification | Action |
|---|---|---|
| = 0 | Exact match | Pass |
| 0 < <= 1% | Rounding or minor calculation definition difference | Record reason |
| 1% < <= 5% | Calculation definition difference | Annotate and evaluate acceptability |
| > 5% | Likely error | Investigate Agent SQL generation path |

## Common Pitfalls

| Pitfall | Description | How to avoid |
|---|---|---|
| GPT view correlated subquery silent error | Metrics with correlated subqueries lose outer references in GPT views, returning wrong values without errors | Do not use subqueries in metrics |
| Virtual columns not persisted | Columns created with `column virtual set` are not available in GPT views | Use inline CASE WHEN in metric expressions |
| Ambiguous columns | Same-named columns with different meanings (e.g., city) cause the Agent to follow the wrong JOIN path | Annotate JOIN path in column descriptions; use AB to lock JOIN for cross-table metrics |
| Three-source conflict | Metrics, AB, and KB may define different calculation definitions; the LLM decides freely which one to use | Write calculation definitions in only one place (KB); the other two reference KB |

## Pre-Creation Checklist

**Metrics**

- Single table, pure aggregation, no subqueries, no window functions
- No virtual column references
- Chinese aliases added
- Description explains calculation definition and filter conditions
- SQL bypass validation confirms values are correct

**Answer Builder**

- analysis-name clearly describes the business concept
- chartParams.fromTableRefs column names match the GPT view
- outputColumns.name exactly matches the SQL AS alias
- outputColumns.metricName uses `ab_` prefix and is unique within the domain
- relatedTables includes all tables
- SQL string constants use chr() concatenation
- ${dims} and ${filters} are positioned correctly
- NULLIF division-by-zero protection is in place
- validate passes
- Agent question + SQL bypass validation completed

**Knowledge Base**

- Calculation definition documentation covers all metrics in the domain
- Business rules documentation covers all enumeration values
- Analysis scenario documentation includes 3–5 SQL templates
- KB formulas are consistent with metric/AB
- Correct usage of ambiguous columns is annotated

## Known Limitations and Workarounds

| Limitation | Workaround |
|---|---|
| GPT views do not support correlated subqueries | Use Answer Builder with GROUP BY instead |
| Virtual columns not persisted | Use inline CASE WHEN in metric expressions |
| Agent may not execute AB SQL templates | Write AB SQL to standard; verify with bypass testing |
| String constants require chr() concatenation | Memorize common ASCII codes |
| ${dims} column name fails across subquery boundaries | Wrap with `SELECT * FROM (subquery)` |
| metric rule cannot be configured via CLI | Use Answer Builder for dimension drill-down |
| No priority rules among three sources | KB as single source of truth; metric/AB reference KB |

## Related Documents

- [Answer Builder SQL Template Guide](datagpt-answer-builder-sql-guide.md): In-depth guide on Answer Builder DSL structure, scenario patterns, and error reference
- [Driving Agent Analysis Domain Modeling with CZ-CLI](datagpt-domain-modeling-by-czcli-guide.md): Complete workflow for automated analysis domain modeling with CZ-CLI
- [Configure Knowledge](datagpt-knowledge-config-best-practices.md): Knowledge Base configuration best practices
- [Troubleshooting Q&A Accuracy Issues](datagpt-qa-accuracy-troubleshooting-guide.md): Systematic troubleshooting for Q&A accuracy problems
