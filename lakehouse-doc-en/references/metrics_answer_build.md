# Metrics and Answer Builder

When AI answers questions involving calculation logic, without pre-defined formulas, the model may generate different SQL each time, resulting in inconsistent metric definitions. Metrics and Answer Builder solve exactly this problem — they lock in the calculation logic so the model can reference it directly instead of inferring it on the fly.

**When to use Metrics vs Answer Builder**?

| Scenario                                                      | Recommended    | Reason                                                                  |
| ------------------------------------------------------------- | -------------- | ----------------------------------------------------------------------- |
| Single-table aggregation, e.g., SUM, AVG, COUNT               | Metrics        | Simple to configure; supports aliases and period-over-period comparison |
| Requires multi-table JOIN                                     | Answer Builder | Metrics do not support multiple tables; a full SQL template is needed   |
| Has complex filter conditions (e.g., count only valid orders) | Answer Builder | Filter logic goes in the WHERE clause of the SQL template               |
| Detail query (non-aggregate, returns row-level data)          | Answer Builder | Metrics only support aggregate calculations                             |

***

## Creating Metrics

In the left navigation bar, go to **Data** -> **Metrics** and click + **New Metric**. Both aggregation and custom code methods are supported.

![](.topwrite/assets/b.jpg =558)

^

A single metric template can define multiple metrics, and each metric can have multiple aliases, allowing the model to understand different names for the same concept (e.g., "average order value" and "spend per customer").

> ⚠️ **Note**: In the Default Domain, duplicate metric names and aliases are allowed. In other user-created Domains, metric names (including aliases) must be unique.

### Analysis Method

Each metric must specify an analysis method, which affects the period-over-period calculation logic:

| Analysis Method     | Period-over-Period Algorithm                                               | Applicable Scenario                                     |
| ------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------- |
| Additive metric     | (Current period value - Previous period value) / \|Previous period value\| | Absolute numeric metrics, e.g., revenue, order count    |
| Proportional metric | Current period value - Previous period value                               | Percentage metrics, e.g., market share, conversion rate |

Example: If market share is 30% this year and 20% last year, the proportional method gives a year-over-year result of +10% (not +50%).

***

## Creating an Answer Builder

In the left navigation bar, go to **Data** -> **Answer Builder** and click + **New Answer Builder**.

The core of an Answer Builder is a SQL template. `${dims}` and `${filters}` are fixed placeholders representing dimensions and filter conditions respectively; they are dynamically filled in by the AI when answering questions.

```sql
SELECT  
  ${dims},
  sum(op.payment_value) as total_sales_bz,
  avg(op.payment_value) as avg_sales_bz
FROM datagpt_ws.public.v_gpt_orders AS o  
LEFT JOIN datagpt_ws.public.v_gpt_order_items AS oi 
    ON o.order_id = oi.order_id
LEFT JOIN datagpt_ws.public.v_gpt_products AS p
    ON oi.product_id = p.product_id
LEFT JOIN datagpt_ws.public.v_gpt_customers AS c
    ON o.customer_id = c.customer_id
LEFT JOIN datagpt_ws.public.v_gpt_payments AS op
    ON o.order_id = op.order_id
LEFT JOIN datagpt_ws.public.v_gpt_sellers AS os
    ON oi.seller_id = os.seller_id
WHERE ${filters}
GROUP BY ${dims}
```

### Configuring Filters and Dims

Below the SQL template, you need to define which columns can be used as filter conditions (Filters) and dimensions (Dims). Columns not selected here will not be used as filter conditions or dimensions for questions.

:-: ![](/.topwrite/assets/image_1780906414361.png =686)

> 💡 **Tip**: In the column configuration under **Data** -> **Tables**, setting a column's **Usage** field to FILTER or DIM will cause it to be selected by default here. The final configuration is governed by the settings on the Answer Builder page.

## Related Documentation

* [Answer Accuracy Improvement](answer-accuracy-improve.md) — The role of Metrics and Answer Builder in the overall accuracy improvement strategy
* [Data Source Management](datagpt_data_source.md) — Configure the data table sources that metrics depend on
* [Row-Level Permissions](row_level_permission.md) — Control the data range accessible to different users
* [Conversational Data Analytics (Analytics Agent)](datagpt_introduction.md) — Return to feature overview

^
