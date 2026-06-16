# Using SQL Tasks to Calculate Customer Retention Metrics

Retention rate is an important metric used by enterprises to measure their product/service. The level of retention rate represents the user's satisfaction with the product/service and is also one of the most commonly used analysis models in the field of data analysis.

This article introduces how to create a retention analysis query using SQL tasks.

In this tutorial, we will analyze the retention rate based on the "E-commerce Dataset".

```sql
DROP TABLE if exists eCommerce_Retention_Week_Number;
CREATE TABLE eCommerce_Retention_Week_Number 
AS
SELECT a.user_id,
       a.event_week,
       b.first_week AS first_week,
       a.event_week-first_week as week_number 
FROM (SELECT user_id,
             weekofyear(event_date) AS event_week
      FROM clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore
      GROUP BY user_id,
               event_week) a,
     (SELECT user_id,
             MIN(weekofyear (event_date)) AS first_week
      FROM clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore
      GROUP BY user_id) b
WHERE a.user_id = b.user_id;
```

## Related Documentation

* [Retention and Cohort Analysis](sql_retention_cohort_guide.md) — Complete retention analysis guide (N-day retention, cohort matrix, consecutive active users, churn analysis)
