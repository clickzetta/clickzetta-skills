# Data Write, Feature Engineering, and Model Inference Examples

## Data Write

| Scenario | Method |
|------|------|
| ZettaPark available (Python 3.10+) | `save_as_table()` or `create_dataframe().write` |
| Local CSV/pandas write | `session.create_dataframe(df).write.save_as_table()` |
| Python 3.9 / ZettaPark unavailable | cursor batch INSERT (see below) |
| **Forbidden** | `df.to_sql()`, SQLAlchemy `clickzetta://...` |

```python
# Option A: ZettaPark (recommended)
session.sql("""
    SELECT o.*, u.age_group FROM my_schema.orders_raw o
    LEFT JOIN my_schema.users u ON o.user_id = u.user_id
    WHERE o.amount > 0
""").write.mode("overwrite").save_as_table("ds_workspace.orders_clean")

# Option B: pandas → Lakehouse
session.create_dataframe(local_df).write.mode("append").save_as_table("ds_workspace.features_v1")

# Option C: cursor batch INSERT (fallback)
import clickzetta, os
conn = clickzetta.connect(
    service=os.environ["CLICKZETTA_SERVICE"], instance=os.environ["CLICKZETTA_INSTANCE"],
    workspace=os.environ["CLICKZETTA_WORKSPACE"], username=os.environ["CLICKZETTA_USERNAME"],
    password=os.environ["CLICKZETTA_PASSWORD"],
    vcluster=os.environ.get("CLICKZETTA_VCLUSTER", "default_ap"),
    schema=os.environ.get("CLICKZETTA_SCHEMA", "public"),
)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS ds_workspace.my_table (col1 STRING, col2 BIGINT, col3 DOUBLE)")
rows = local_df.values.tolist()
for i in range(0, len(rows), 500):
    batch = rows[i:i+500]
    vals = ",".join(f"({','.join(repr(v) for v in row)})" for row in batch)
    cursor.execute(f"INSERT INTO ds_workspace.my_table VALUES {vals}")
conn.close()
```

```sql
-- Set intermediate table lifecycle (auto-cleanup after 30 days)
ALTER TABLE ds_workspace.orders_clean SET PROPERTIES ('data_lifecycle' = '30');
```

---

## Feature Engineering

```sql
-- SQL side (leverages Lakehouse compute, recommended)
SELECT
    user_id,
    COUNT(*)                                                    AS order_cnt_30d,
    SUM(amount)                                                 AS total_amount_30d,
    AVG(amount)                                                 AS avg_amount_30d,
    STDDEV(amount)                                              AS std_amount_30d,
    DATEDIFF('day', MIN(order_date), MAX(order_date))           AS active_days,
    COUNT(DISTINCT DATE(order_date))                            AS active_day_cnt,
    NTILE(10) OVER (ORDER BY SUM(amount) DESC)                  AS revenue_decile
FROM my_schema.orders
WHERE order_date >= CURRENT_DATE - INTERVAL 30 DAY
GROUP BY user_id;
```

```python
# ZettaPark side (Python logic)
from clickzetta.zettapark.functions import col, when

features = session.table("ds_workspace.orders_clean") \
    .with_column("is_high_value", when(col("amount") > 1000, 1).otherwise(0))

df = features.to_pandas()

from sklearn.preprocessing import StandardScaler
df[['amount_scaled']] = StandardScaler().fit_transform(df[['amount']])

session.create_dataframe(df).write.mode("overwrite").save_as_table("ds_workspace.features_final")
```

---

## Model Inference Deployment

### BITMAP User Profiling

```sql
CREATE TABLE ds_workspace.user_tags AS
SELECT tag_name, group_bitmap_state(user_id) AS user_bitmap
FROM my_schema.user_behavior GROUP BY tag_name;

-- Audience intersection
SELECT bitmap_count(bitmap_and(
    (SELECT user_bitmap FROM ds_workspace.user_tags WHERE tag_name = 'high_value'),
    (SELECT user_bitmap FROM ds_workspace.user_tags WHERE tag_name = 'active_30d')
)) AS target_user_count;
```

### SQL UDF Batch Inference

```sql
-- Call a deployed model UDF (must use full schema path)
INSERT INTO ds_workspace.predictions
SELECT user_id,
       ds_workspace.credit_score_model(total_amount_30d, order_cnt_30d, active_days, avg_amount_30d) AS score,
       CURRENT_TIMESTAMP() AS predict_time
FROM ds_workspace.features_final;
```

### Vector Search

```sql
SELECT candidate_id,
       cosine_distance(
           (SELECT embedding FROM ds_workspace.user_embeddings WHERE user_id = 'target'),
           embedding
       ) AS similarity
FROM ds_workspace.user_embeddings
WHERE user_id != 'target'
ORDER BY similarity LIMIT 10;
```
