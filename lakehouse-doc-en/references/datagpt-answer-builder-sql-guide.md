# Answer Builder SQL Template Guide

Answer Builder is the mechanism in Analytics Agent's semantic layer for handling complex analysis — you write a SQL analysis template with parameter placeholders, and the system turns it into an **interactive, reusable** analysis asset: end users can switch dimensions and check filter conditions when querying, getting structured multi-column results.

It complements metrics (created with the `metric` command):

| | Metric `metric` | Answer Builder `answer-builder` |
| --- | --- | --- |
| Nature | Single table + single aggregate expression | Parameterized complex analysis SQL template |
| Can express | Single calculation definitions like `SUM(amount)`, `COUNT(*)` | Multi-derived ratios, rankings/share, cross-table joins, time-series comparisons, multi-dimensional subtotals |
| Interaction | None | `${dims}` to switch dimensions, `${filters}` to add filters |
| Output | Single value | Multi-column result, each column a named metric |

In short: **if a single aggregate expression covers it, use `metric`; if you need multi-step calculations, window functions, cross-table joins, time-series comparisons, or interactive drill-down, use `answer-builder`.**

> All operations in this document are performed via the command-line tool **cz-cli** (`cz-cli analytics-agent answer-builder ...`), suitable for batch creation, scripting, and version-managing Answer Builders. The same configuration can also be done in the DataGPT Studio interface. All example commands in this document have been validated with cz-cli's `validate` syntax check. For cz-cli installation and connection configuration, see [cz-cli Installation and Usage Guide](setup_cz_cli.md).

## When to Use Answer Builder

The following analyses cannot be done with ordinary metrics and require Answer Builder:

* **Multiple interrelated derived ratios**: Average order value, discount ratio, new customer ratio — all need to be calculated together in one result
* **Rankings and cumulative share**: Pareto analysis (how much sales revenue do the top products contribute?) — requires window functions
* **Cross-table join analysis**: How does after-sales satisfaction compare for best-selling products? — joining the sales table with the after-sales table
* **Time-series comparison**: Month-over-month growth — requires `LAG` to reference the previous row
* **Multi-dimensional subtotals**: Sales amounts broken down by region and product + subtotals at each level in one pass (`ROLLUP`)
* **Interactive analysis**: Same template, users select their own dimensions and filter conditions at runtime

## Commands

All commands use `cz-cli analytics-agent` as the prefix (e.g., `cz-cli analytics-agent answer-builder validate ...`):

| Command | Purpose | When to use |
| --- | --- | --- |
| `answer-builder validate` | Validate DSL (dry-run, no persistence) | Verify syntax and configuration before creating |
| `answer-builder create` | Create an Answer Builder | Persist after validation passes |
| `answer-builder list` | List Answer Builders in an Analysis domain | View existing assets |
| `answer-builder detail <id>` | View full definition | Copy an existing one as a template to modify |
| `answer-builder update <id>` | Update definition | Modify SQL / dimensions / metric names |
| `answer-builder enable/disable <id>` | Enable/disable | Go live / take offline |

> ⚠️ **Note**: All commands require `--domain-id` and `--datasource-id` to specify the Analysis domain and data source.

## DSL Structure (`--content`)

The core of an Answer Builder is a DSL JSON (passed via `--content`) containing four top-level fields:

```Plain
{
  "chartParams": [        // Interactive input parameters, referenced in SQL with ${name}
    {"name":"dims","type":"dimension","allowMulti":true,       // -> GROUP BY ${dims}
     "fromTableRefs":[{"tableName":"cat.schema.table","columns":["region"]}]},
    {"name":"filters","type":"filter","allowMulti":true,       // -> WHERE ${filters}
     "fromTableRefs":[{"tableName":"cat.schema.table","columns":["channel"]}]}
  ],
  "outputColumns": [      // One entry per SELECT output column
    {"name":"total_amount",           // Must match the AS alias in SQL
     "metricName":"Regional Sales Amount",         // Required, must be unique within the Analysis domain
     "type":"decimal","stdTypeName":"double",   // type required, stdTypeName optional
     "alias":["Sales"],               // Optional display alias
     "description":"Total sales amount aggregated by region"}         // Optional
  ],
  "relatedTables": ["cat.schema.table"],   // All tables referenced in the SQL
  "sql": "SELECT ${dims}, SUM(final_amount) AS total_amount FROM ... GROUP BY ${dims}"
}
```

### Field Reference

| Field | Purpose | Key Notes |
| --- | --- | --- |
| `chartParams[].name` | Placeholder name, referenced in SQL as `${name}` | Every SQL placeholder must have a corresponding entry here |
| `chartParams[].type` | `dimension` (grouping dimension) / `filter` (filter condition) | dimension → GROUP BY; filter → WHERE |
| `chartParams[].allowMulti` | Whether multiple selections are allowed | Multi-select dimensions enable drill-down; multi-select filters enable combinations |
| `chartParams[].fromTableRefs` | Tables and columns available for this parameter | Users select from these columns during interaction |
| `outputColumns[].name` | Output column name | **Must** equal the `AS` alias in SQL |
| `outputColumns[].metricName` | Metric name (shown in the interface) | **Required, and must be unique within the Analysis domain** |
| `outputColumns[].type` | Data type (`bigint`/`decimal`…) | Required |
| `outputColumns[].alias` | Display alias (array) | Optional |
| `outputColumns[].description` | Metric description | Optional |
| `relatedTables` | All tables referenced in SQL | Include dimension tables too when JOINing |
| `sql` | Analysis SQL template | Recommended to pass separately via `--sql` to avoid quote escaping |

### Separating SQL with `--sql`

SQL often contains single quotes (e.g., `WHERE status='completed'`), and embedding them in `--content` JSON requires multiple layers of escaping — very error-prone. Use the separate `--sql` parameter to pass SQL; the CLI will automatically inject it into the `sql` field of the content. At least one of `--content` and `--sql` must be provided.

> ⚠️ **Note**: The `${dims}`/`${filters}` placeholders in `--sql` have a shell quoting trap — if placed inside **double quotes** `"..."` without escaping, the shell (bash/zsh) treats them as variables and expands them to **empty strings**. The CLI then receives `SELECT , ... WHERE  GROUP BY`, and reports `CZLH-42000: Syntax error at or near ','` — it looks like a SQL syntax error but the placeholders were already gone before reaching the CLI. Two correct approaches:
>
> ```bash
> # Recommended: single quotes, shell leaves $ completely alone
> --sql 'SELECT ${dims}, COUNT(*) AS c FROM t WHERE ${filters} GROUP BY ${dims}'
>
> # Or: escape $ inside double quotes
> --sql "SELECT \${dims}, COUNT(*) AS c FROM t WHERE \${filters} GROUP BY \${dims}"
> ```

## Five Essential Rules

These five rules are the most common pitfalls in practice and have the greatest impact on success.

**Rule 1: Every `${name}` placeholder must have a corresponding entry in chartParams**

If you write `${dims}` in SQL, chartParams must have an entry with `name:"dims"`. Otherwise the placeholder will not be replaced, the bare `$` will remain in the SQL, and it will error:

```Plain
CZLH-42000: Syntax error at or near '$'
```

**Rule 2: `outputColumns[].metricName` is required and must be unique within the Analysis domain**

Every output column must have a `metricName` (the "metric name" shown in the interface). **Missing it** causes the interface to show "Please enter a metric name" and prevents saving. **Duplicate names within the same Analysis domain** will error:

```Plain
CZD-99999: The output metric name [Total Sales] of the Answer Builder conflicts with an existing metric name in the Analysis domain
```

> ⚠️ **Note**: Generic names (Sales Amount, Order Count, Satisfaction) are very likely to conflict within a Analysis domain. Add a business context prefix to distinguish them, e.g., `Regional Sales Amount` / `Industry Sales Amount` / `Tiered Sales Amount`.

**Rule 3: When window functions / ROLLUP reference columns from `${dims}`, wrap in a subquery**

When `RANK() OVER (PARTITION BY ...)`, `LAG(...) OVER (ORDER BY ...)`, or `ROLLUP(${dims})` reference columns that are part of the `${dims}` expansion, placeholder substitution conflicts with the window/grouping column references, causing a semantic error.

The workaround: **use fixed column names in an inner subquery to complete the window/aggregate calculations, then `SELECT ${dims}` in the outer query**.

```sql
-- Directly using ${dims}-expanded columns in the window function causes a conflict error
SELECT ${dims}, RANK() OVER (PARTITION BY region ORDER BY SUM(final_amount) DESC) AS rk
FROM t GROUP BY ${dims}

-- Fixed column names in the inner query; outer query only selects
SELECT ${dims}, amt, rank_in_region FROM (
  SELECT region, channel, SUM(final_amount) AS amt,
         RANK() OVER (PARTITION BY region ORDER BY SUM(final_amount) DESC) AS rank_in_region
  FROM t GROUP BY region, channel
) x
```

**Rule 4: `outputColumns[].name` must equal the SQL `AS` alias**

Output columns are matched to SQL by `name` and `AS` alias. If they differ, the front end cannot retrieve the corresponding value. Column names can use Chinese directly (wrapped in backticks): `SUM(final_amount) AS \`Total Sales\``.

**Rule 5: Always `validate` before `create`**

`validate` is a dry-run that does not persist anything, returning `valid` / `errors` / `warnings`. It checks names, configuration, and the Analysis domain-table relationship, catching placeholder missing, SQL syntax, and duplicate metric name issues before creation. Make "validate before create" a habit to avoid producing incorrect assets.

## Prerequisites

All examples in this document are based on an ICT Sales and After-sales Service Analysis domain, containing the following tables (under `quick_start.ict_industry_demo`):

| Table | Description | Key Columns |
| --- | --- | --- |
| `v_gpt_fact_sales` | Sales order fact table | sale_id, order_no, region, channel, product_type, salesperson, quantity, final_amount, sale_date, customer_id, product_id |
| `v_gpt_fact_service` | After-sales service ticket table | service_id, order_no, service_type, status, satisfaction_score, response_days, cost, customer_id, product_id |
| `v_gpt_dim_customer` | Customer dimension table | customer_id, industry, customer_level, region |
| `v_gpt_dim_product` | Product dimension table | product_id, brand_vendor, category, product_type |
| `v_gpt_ads_monthly_sales_summary` | Monthly sales summary | stat_month, region, channel, product_type, order_count, final_amount, discount_amount, original_amount, customer_count, new_customer_count |

The Analysis domain has JOIN relationships between dimension tables and fact tables (customer/product → sales/after-sales) already configured.

Each scenario below provides a complete `create` command that has been validated with `validate` syntax check. Examples uniformly use `--domain-id <domain-id> --datasource-id <datasource-id>` (replace with your own Analysis domain and data source ID).

## Scenario 1: Single-dimension Aggregation (Beginner)

**Business question**: Order count and total sales amount by region.

```bash
cz-cli analytics-agent answer-builder create \
  --domain-id <domain-id> --datasource-id <datasource-id> \
  --analysis-name "Regional Sales Summary" \
  --content '{"chartParams":[{"name":"dims","type":"dimension","allowMulti":true,"fromTableRefs":[{"tableName":"quick_start.ict_industry_demo.v_gpt_fact_sales","columns":["region"]}]}],"outputColumns":[{"name":"order_count","metricName":"Regional Order Count","type":"bigint","stdTypeName":"int"},{"name":"total_amount","metricName":"Regional Sales Amount","type":"decimal","stdTypeName":"double"}],"relatedTables":["quick_start.ict_industry_demo.v_gpt_fact_sales"]}' \
  --sql "SELECT \${dims}, COUNT(*) AS order_count, SUM(final_amount) AS total_amount FROM quick_start.ict_industry_demo.v_gpt_fact_sales GROUP BY \${dims}"
```

The formatted SQL from `--sql`:

```sql
SELECT ${dims},
       COUNT(*)          AS order_count,
       SUM(final_amount) AS total_amount
FROM   quick_start.ict_industry_demo.v_gpt_fact_sales
GROUP  BY ${dims}
```

**Key points**: The `dims` dimension allows multi-select (`allowMulti:true`), so users can switch to drill down by channel, product_type, etc. at runtime. Both output columns have unique `metricName` values.

## Scenario 2: Filter Parameters + Named Metrics (Recommended Pattern)

**Business question**: View salesperson performance, with the ability to filter by region/channel/product type at runtime.

```bash
cz-cli analytics-agent answer-builder create \
  --domain-id <domain-id> --datasource-id <datasource-id> \
  --analysis-name "Salesperson Performance (filterable by region, channel, product)" \
  --content '{"chartParams":[{"name":"filters","type":"filter","allowMulti":true,"fromTableRefs":[{"tableName":"quick_start.ict_industry_demo.v_gpt_fact_sales","columns":["region","channel","product_type"]}]},{"name":"dims","type":"dimension","allowMulti":true,"fromTableRefs":[{"tableName":"quick_start.ict_industry_demo.v_gpt_fact_sales","columns":["salesperson"]}]}],"outputColumns":[{"name":"order_count","metricName":"Salesperson Order Count","type":"bigint","stdTypeName":"int"},{"name":"total_sales","metricName":"Salesperson Total Sales","type":"decimal","stdTypeName":"double"},{"name":"avg_order_value","metricName":"Salesperson Average Order Value","type":"decimal","stdTypeName":"double"}],"relatedTables":["quick_start.ict_industry_demo.v_gpt_fact_sales"]}' \
  --sql "SELECT \${dims}, COUNT(*) AS order_count, SUM(final_amount) AS total_sales, ROUND(AVG(final_amount),2) AS avg_order_value FROM quick_start.ict_industry_demo.v_gpt_fact_sales WHERE \${filters} GROUP BY \${dims}"
```

The formatted SQL from `--sql`:

```sql
SELECT ${dims},
       COUNT(*)                    AS order_count,
       SUM(final_amount)           AS total_sales,
       ROUND(AVG(final_amount), 2) AS avg_order_value
FROM   quick_start.ict_industry_demo.v_gpt_fact_sales
WHERE  ${filters}
GROUP  BY ${dims}
```

**Key points**: `filters` lists three filterable columns; SQL uses `WHERE ${filters}` so users can select filter values at runtime. The `metricName` values are prefixed with "Salesperson" to ensure uniqueness within the Analysis domain.

## Scenario 3: Cross-table JOIN Analysis

**Business question**: For the best-selling products, what are the after-sales satisfaction and ticket rates? — joining the sales table with the after-sales table; ordinary metrics are single-table only and cannot do this.

```bash
cz-cli analytics-agent answer-builder create \
  --domain-id <domain-id> --datasource-id <datasource-id> \
  --analysis-name "Product Sales and After-sales Quality Correlation" \
  --content '{"chartParams":[{"name":"dims","type":"dimension","allowMulti":true,"fromTableRefs":[{"tableName":"quick_start.ict_industry_demo.v_gpt_fact_sales","columns":["product_type"]}]}],"outputColumns":[{"name":"sales_amount","metricName":"Product Sales Amount (with After-sales)","type":"decimal","stdTypeName":"double"},{"name":"service_count","metricName":"Product After-sales Ticket Count","type":"bigint","stdTypeName":"int"},{"name":"avg_satisfaction","metricName":"Product After-sales Satisfaction","type":"decimal","stdTypeName":"double"},{"name":"service_per_order","metricName":"Product Tickets per Order","type":"decimal","stdTypeName":"double"}],"relatedTables":["quick_start.ict_industry_demo.v_gpt_fact_sales","quick_start.ict_industry_demo.v_gpt_fact_service"]}' \
  --sql "SELECT \${dims}, SUM(s.final_amount) AS sales_amount, COUNT(DISTINCT sv.service_id) AS service_count, ROUND(AVG(sv.satisfaction_score),2) AS avg_satisfaction, ROUND(COUNT(DISTINCT sv.service_id)*1.0/COUNT(DISTINCT s.sale_id),3) AS service_per_order FROM quick_start.ict_industry_demo.v_gpt_fact_sales s LEFT JOIN quick_start.ict_industry_demo.v_gpt_fact_service sv ON s.order_no=sv.order_no GROUP BY \${dims}"
```

The formatted SQL from `--sql`:

```sql
SELECT ${dims},
       SUM(s.final_amount)                                             AS sales_amount,
       COUNT(DISTINCT sv.service_id)                                   AS service_count,
       ROUND(AVG(sv.satisfaction_score), 2)                            AS avg_satisfaction,
       ROUND(COUNT(DISTINCT sv.service_id) * 1.0
             / COUNT(DISTINCT s.sale_id), 3)                           AS service_per_order
FROM   quick_start.ict_industry_demo.v_gpt_fact_sales   s
LEFT JOIN quick_start.ict_industry_demo.v_gpt_fact_service sv
       ON s.order_no = sv.order_no
GROUP  BY ${dims}
```

**Key points**: `relatedTables` includes both the sales table and the after-sales table. `LEFT JOIN` ensures products with no after-sales records still appear (sales amount present, ticket count is 0).

## Scenario 4: Window Functions — Rankings and Cumulative Share (Pareto Analysis)

**Business question**: Which product types contribute the most to total sales? (Cumulative share of top products.) Requires window functions — ordinary metrics cannot do this.

```bash
cz-cli analytics-agent answer-builder create \
  --domain-id <domain-id> --datasource-id <datasource-id> \
  --analysis-name "Product Sales Ranking and Cumulative Share (Pareto)" \
  --content '{"chartParams":[{"name":"dims","type":"dimension","allowMulti":true,"fromTableRefs":[{"tableName":"quick_start.ict_industry_demo.v_gpt_fact_sales","columns":["product_type"]}]}],"outputColumns":[{"name":"total_amount","metricName":"Product Sales Amount (Pareto)","type":"decimal","stdTypeName":"double"},{"name":"sales_rank","metricName":"Product Sales Rank","type":"bigint","stdTypeName":"int"},{"name":"cum_ratio","metricName":"Product Cumulative Share","type":"decimal","stdTypeName":"double"}],"relatedTables":["quick_start.ict_industry_demo.v_gpt_fact_sales"]}' \
  --sql "SELECT \${dims}, SUM(final_amount) AS total_amount, RANK() OVER (ORDER BY SUM(final_amount) DESC) AS sales_rank, ROUND(SUM(SUM(final_amount)) OVER (ORDER BY SUM(final_amount) DESC)*100.0/SUM(SUM(final_amount)) OVER (),2) AS cum_ratio FROM quick_start.ict_industry_demo.v_gpt_fact_sales GROUP BY \${dims}"
```

The formatted SQL from `--sql`:

```sql
SELECT ${dims},
       SUM(final_amount)                                     AS total_amount,
       RANK() OVER (ORDER BY SUM(final_amount) DESC)         AS sales_rank,
       ROUND(SUM(SUM(final_amount)) OVER (ORDER BY SUM(final_amount) DESC)
             * 100.0
             / SUM(SUM(final_amount)) OVER (), 2)            AS cum_ratio
FROM   quick_start.ict_industry_demo.v_gpt_fact_sales
GROUP  BY ${dims}
```

**Key points**: `RANK()` for ranking, `SUM(...) OVER (ORDER BY ...)` for cumulative calculation. Here `${dims}` is in the outermost SELECT and does not enter PARTITION BY, so Rule 3's conflict is not triggered.

## Scenario 5: Time-series Comparison — Region-Channel Rankings Require a Subquery Wrapper

**Business question**: Within each region, rank the sales channels by sales amount. Here `RANK() OVER (PARTITION BY region ...)` uses `region`, which is exactly a column expanded from `${dims}`. Writing it directly causes a conflict, so Rule 3 requires wrapping in a subquery.

```bash
cz-cli analytics-agent answer-builder create \
  --domain-id <domain-id> --datasource-id <datasource-id> \
  --analysis-name "Regional Channel Effectiveness Matrix" \
  --content '{"chartParams":[{"name":"dims","type":"dimension","allowMulti":true,"fromTableRefs":[{"tableName":"quick_start.ict_industry_demo.v_gpt_ads_monthly_sales_summary","columns":["region","channel"]}]}],"outputColumns":[{"name":"amt","metricName":"Regional Channel Sales Amount","type":"decimal","stdTypeName":"double"},{"name":"rank_in_region","metricName":"Channel Rank within Region","type":"bigint","stdTypeName":"int"}],"relatedTables":["quick_start.ict_industry_demo.v_gpt_ads_monthly_sales_summary"]}' \
  --sql "SELECT \${dims}, amt, rank_in_region FROM (SELECT region, channel, SUM(final_amount) AS amt, RANK() OVER (PARTITION BY region ORDER BY SUM(final_amount) DESC) AS rank_in_region FROM quick_start.ict_industry_demo.v_gpt_ads_monthly_sales_summary GROUP BY region, channel) t"
```

The formatted SQL from `--sql` (note the two-layer structure):

```sql
SELECT ${dims}, amt, rank_in_region
FROM (
    SELECT region,
           channel,
           SUM(final_amount) AS amt,
           RANK() OVER (PARTITION BY region
                        ORDER BY SUM(final_amount) DESC) AS rank_in_region
    FROM   quick_start.ict_industry_demo.v_gpt_ads_monthly_sales_summary
    GROUP  BY region, channel
) t
```

**Key points**: The inner subquery uses fixed column names `region, channel` for the PARTITION BY ranking. The outer `SELECT ${dims}` only selects — this is the standard pattern for window/time-series analyses.

## Scenario 6: Multi-dimensional Subtotals (ROLLUP) and Risk Flagging (Conditional Aggregation + Subquery)

**Multi-dimensional subtotals** — sales amount broken down by region and product with subtotals at each level in one pass:

```bash
cz-cli analytics-agent answer-builder create \
  --domain-id <domain-id> --datasource-id <datasource-id> \
  --analysis-name "Multi-dimensional Sales Subtotal Report" \
  --content '{"chartParams":[{"name":"dims","type":"dimension","allowMulti":true,"fromTableRefs":[{"tableName":"quick_start.ict_industry_demo.v_gpt_fact_sales","columns":["region","product_type"]}]}],"outputColumns":[{"name":"total_amount","metricName":"Multi-dimensional Subtotal Sales Amount","type":"decimal","stdTypeName":"double"},{"name":"order_cnt","metricName":"Multi-dimensional Subtotal Order Count","type":"bigint","stdTypeName":"int"}],"relatedTables":["quick_start.ict_industry_demo.v_gpt_fact_sales"]}' \
  --sql "SELECT \${dims}, SUM(final_amount) AS total_amount, COUNT(*) AS order_cnt FROM quick_start.ict_industry_demo.v_gpt_fact_sales GROUP BY ROLLUP(\${dims})"
```

The formatted SQL from `--sql`:

```sql
SELECT ${dims},
       SUM(final_amount) AS total_amount,
       COUNT(*)          AS order_cnt
FROM   quick_start.ict_industry_demo.v_gpt_fact_sales
GROUP  BY ROLLUP(${dims})
```

**Risk quadrant** — flag "high sales but low satisfaction" high-risk products using `CASE WHEN` + a correlated subquery to compute the global threshold:

```bash
cz-cli analytics-agent answer-builder create \
  --domain-id <domain-id> --datasource-id <datasource-id> \
  --analysis-name "Product Reputation Risk Alert Quadrant" \
  --content '{"chartParams":[{"name":"dims","type":"dimension","allowMulti":true,"fromTableRefs":[{"tableName":"quick_start.ict_industry_demo.v_gpt_dim_product","columns":["brand_vendor","category"]}]}],"outputColumns":[{"name":"sales_amt","metricName":"Brand Sales Amount","type":"decimal","stdTypeName":"double"},{"name":"avg_sat","metricName":"Brand Satisfaction","type":"decimal","stdTypeName":"double"},{"name":"complaint_rate","metricName":"Brand Ticket Rate","type":"decimal","stdTypeName":"double"},{"name":"risk_flag","metricName":"Brand Reputation Risk Flag","type":"bigint","stdTypeName":"int"}],"relatedTables":["quick_start.ict_industry_demo.v_gpt_fact_sales","quick_start.ict_industry_demo.v_gpt_fact_service","quick_start.ict_industry_demo.v_gpt_dim_product"]}' \
  --sql "SELECT \${dims}, SUM(s.final_amount) AS sales_amt, ROUND(AVG(sv.satisfaction_score),2) AS avg_sat, ROUND(COUNT(DISTINCT sv.service_id)*100.0/COUNT(DISTINCT s.sale_id),2) AS complaint_rate, CASE WHEN AVG(sv.satisfaction_score)<3 AND SUM(s.final_amount)>(SELECT AVG(final_amount) FROM quick_start.ict_industry_demo.v_gpt_fact_sales) THEN 1 ELSE 0 END AS risk_flag FROM quick_start.ict_industry_demo.v_gpt_fact_sales s JOIN quick_start.ict_industry_demo.v_gpt_dim_product p ON s.product_id=p.product_id LEFT JOIN quick_start.ict_industry_demo.v_gpt_fact_service sv ON s.order_no=sv.order_no GROUP BY \${dims}"
```

The formatted SQL from `--sql`:

```sql
SELECT ${dims},
       SUM(s.final_amount)                    AS sales_amt,
       ROUND(AVG(sv.satisfaction_score), 2)   AS avg_sat,
       ROUND(COUNT(DISTINCT sv.service_id) * 100.0
             / COUNT(DISTINCT s.sale_id), 2)  AS complaint_rate,
       CASE
           WHEN AVG(sv.satisfaction_score) < 3
            AND SUM(s.final_amount) > (SELECT AVG(final_amount)
                                       FROM quick_start.ict_industry_demo.v_gpt_fact_sales)
           THEN 1 ELSE 0
       END                                    AS risk_flag
FROM   quick_start.ict_industry_demo.v_gpt_fact_sales   s
JOIN   quick_start.ict_industry_demo.v_gpt_dim_product  p  ON s.product_id = p.product_id
LEFT JOIN quick_start.ict_industry_demo.v_gpt_fact_service sv ON s.order_no = sv.order_no
GROUP  BY ${dims}
```

**Key points**: `risk_flag` uses `CASE WHEN satisfaction < 3 AND sales > global average THEN 1 ELSE 0` to embed complex business logic into a directly filterable flag column — this type of "embedded business rule" is the core value of Answer Builder over ordinary metrics.

## SQL Capability Boundaries

The following advanced SQL features have all been confirmed as supported via `validate` syntax checks. Answer Builder can express virtually any analytical SQL:

| Feature | Supported | Typical use |
| --- | --- | --- |
| Conditional aggregation `CASE WHEN` | Yes | Ratios, risk flags |
| Window functions `RANK/SUM OVER` | Yes | Rankings, cumulative, Pareto |
| `PARTITION BY` grouped window | Yes (requires subquery wrapper) | In-group ranking |
| `LAG/LEAD` time-series | Yes (requires subquery wrapper) | Month-over-month, year-over-year |
| CTE (`WITH`) | Yes | Multi-step calculations |
| Multi-table JOIN (up to 4 tables) | Yes | Cross-topic joins |
| Correlated subquery | Yes | Ratios against global/parent set |
| `ROLLUP` / `GROUPING SETS` | Yes | Multi-dimensional subtotals |
| `NTILE` bucketing | Yes | Tiering, quantiles |
| `PERCENTILE` | Yes | Median, percentile |
| `HAVING` | Yes | Post-aggregation filtering |

## Common Error Reference

| Error | Cause | Solution |
| --- | --- | --- |
| `CZLH-42000: Syntax error at or near ','` | `--sql` uses double quotes without escaping; `${dims}`/`${filters}` are expanded to empty strings by the shell, becoming `SELECT ,` | Switch `--sql` to single quotes, or escape `$` as `\$` inside double quotes (see the shell quoting trap in "Separating SQL with `--sql`") |
| `CZLH-42000: Syntax error at or near '$'` | `${name}` in SQL has no corresponding entry in chartParams | Add the corresponding chartParams entry (Rule 1) |
| `CZLH-42000: Semantic analysis exception` | Window/ROLLUP references columns expanded from `${dims}` | Wrap in a subquery (Rule 3) |
| `CZD-99999: Output metric name [X] conflicts` | `metricName` is duplicated within the Analysis domain | Add a business context prefix to ensure uniqueness within the Analysis domain (Rule 2) |
| Interface shows "Please enter a metric name" | `outputColumns` is missing `metricName` | Add `metricName` to each output column (Rule 2) |

## Recommended Workflow

1. **Confirm necessity**: Can this analysis be expressed with an ordinary metric (`metric`)? If yes, use metric. If not (multi-derived ratios / window functions / cross-table / time-series / interactive), use Answer Builder.
2. **Reuse templates**: Run `answer-builder detail <existing-id>` to export a similar definition and modify it — faster and less error-prone than starting from scratch.
3. **Validate first**: `answer-builder validate ...` dry-run; confirm `valid:true`, `errors:[]`.
4. **Then create**: `answer-builder create ...`.
5. **Check metric names**: Confirm every output column's `metricName` is filled in and unique within the Analysis domain.

## Related Documentation

* [Analytics Agent Metric Specification Design Guide](dataagent-metric-design-guide.md) — Design methodology for metrics (`metric`)
* [DataGPT Conversational Analytics](conversational_analytics_datagpt.md) — How the semantic layer is used by natural language Q&A
* [cz-cli Installation and Usage Guide](setup_cz_cli.md) — Installation, connection configuration, and Agent integration
