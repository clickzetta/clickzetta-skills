# Metrics and Answer Builder Configuration

## Constructing Metrics:&#x20;

In **Left Navigation Bar: Data** -> **Metrics**, you can click "+ **New Metric**" to add new metrics. Metrics can be generated using aggregation or custom code methods.

![](.topwrite/assets/b.jpg =558)

^

## Creating Answer Builder:&#x20;

The Answer Builder is used to define metrics with complex calculation logic and to provide SQL templates for detailed queries. In **Left Navigation Bar: Data** -> **Answer Builder**, you can click "+ **New Answer Builder**" and follow the steps to fill in the code.

* SQL Template for Answer Builder: `${dims}` and `${filters}` are fixed syntax representing dimension and filter condition variables. The selectable columns for these variables are defined in the **Filters** and **Dims** sections below the template.

```SQL
SELECT  
  ${dims},
  sum(op.payment_value) as total_sales_bz,
  avg(op.payment_value) as avg_sales_bz
FROM datagpt_ws.public.v_gpt_orders AS o  
LEFT JOIN datagpt_ws.public.v_gpt_order_items AS oi 
    ON o.order_id = oi.order_id  LEFT JOIN datagpt_ws.public.v_gpt_products AS p
    ON oi.product_id = p.product_id  LEFT JOIN datagpt_ws.public.v_gpt_customers AS c
    ON o.customer_id = c.customer_id  LEFT JOIN datagpt_ws.public.v_gpt_payments AS op
    ON o.order_id = op.order_id  LEFT JOIN datagpt_ws.public.v_gpt_sellers AS os ON oi.seller_id = os.seller_id
where ${filters}
group by ${dims}
```

* **Filters and Dims Variable Definition**: Note: Columns not appearing in Filter and Dims here will not be used as filter conditions and dimensions for the issue. (This is related to the **Usage** field configuration of the table columns in **Data** -> **Tables**: columns configured as FILTER and DIM in the **Usage** field will be selected by default here, and the final configuration will be based on this page)![](.topwrite/assets/20250219-115158.jpeg =736)

### Configure Metric Aliases and Analysis Methods:

In a metric template, multiple metrics can be defined. Each metric can specify multiple aliases.

> Note: In the system Default Domain, duplicate metrics and aliases are allowed; in other user-created Domains, duplicate metric names (including aliases) are not allowed.

### **Analysis Methods**:

* **Additive Metrics**: The algorithm for period-over-period comparison is: (current period value - previous period value) / absolute value of previous period value.
* **Proportional Metrics**: The algorithm for period-over-period comparison is: current period value - previous period value. For example, if this year's market share is 30% and last year's was 20%, then the year-over-year growth is 10%.

![](.topwrite/assets/20250219-115256.jpeg)
