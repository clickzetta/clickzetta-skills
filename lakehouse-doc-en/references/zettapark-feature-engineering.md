# Zettapark Feature Engineering

Feature engineering is a core step in machine learning. Zettapark translates DataFrame operations into SQL for distributed execution inside the Lakehouse, making it efficient to process large-scale user behavior data and build structured feature tables for model training.

---

## Prerequisites

```python
from clickzetta.zettapark.session import Session
from clickzetta.zettapark import functions as F
from clickzetta.zettapark.window import Window

session = Session.builder.configs({
    "username": "your_username",
    "password": "your_password",
    "service":  "cn-shanghai-alicloud.api.clickzetta.com",
    "instance": "your_instance",
    "workspace": "your_workspace",
    "schema":   "public",
    "vcluster": "DEFAULT"
}).create()
```

Create test data (user behavior events table):

```python
session.sql("""
    CREATE TABLE IF NOT EXISTS user_events (
        user_id    INT,
        event_type STRING,
        amount     DECIMAL(10, 2),
        category   STRING,
        event_date STRING,
        hour       INT
    )
""").collect()

session.sql("""
    INSERT INTO user_events VALUES
    (101, 'purchase', 299.0,  'electronics', '2024-01-10', 14),
    (101, 'purchase',  99.0,  'clothing',    '2024-01-12', 10),
    (101, 'browse',     0.0,  'electronics', '2024-01-13', 20),
    (101, 'purchase', 599.0,  'electronics', '2024-01-15', 15),
    (102, 'purchase',  49.0,  'food',        '2024-01-10', 12),
    (102, 'browse',     0.0,  'clothing',    '2024-01-11', 18),
    (102, 'purchase', 199.0,  'clothing',    '2024-01-14', 11),
    (103, 'purchase', 999.0,  'electronics', '2024-01-08', 16),
    (103, 'purchase',1299.0,  'electronics', '2024-01-15', 14),
    (103, 'browse',     0.0,  'food',        '2024-01-16',  9)
""").collect()

session.sql("""
    CREATE TABLE IF NOT EXISTS users (
        user_id       INT,
        age           INT,
        city          STRING,
        register_date STRING
    )
""").collect()

session.sql("""
    INSERT INTO users VALUES
    (101, 28, 'Beijing',   '2023-06-01'),
    (102, 35, 'Shanghai',  '2023-03-15'),
    (103, 22, 'Guangzhou', '2023-09-20')
""").collect()
```

---

## Feature 1: Statistical Features

Aggregate user purchase behavior to extract statistical features such as purchase frequency and spend distribution:

```python
events = session.table("user_events")

stat_features = events.filter(F.col("event_type") == "purchase") \
    .group_by("user_id") \
    .agg(
        F.count(F.col("user_id")).alias("purchase_count"),
        F.sum(F.col("amount")).alias("total_spend"),
        F.avg(F.col("amount")).alias("avg_order_value"),
        F.max(F.col("amount")).alias("max_order_value"),
        F.min(F.col("amount")).alias("min_order_value"),
        F.count_distinct(F.col("category")).alias("category_diversity"),
    )

stat_features.show()
```

```Plain
+-------+--------------+-----------+---------------+------------------+
|user_id|purchase_count|total_spend|avg_order_value|category_diversity|
+-------+--------------+-----------+---------------+------------------+
|    101|             3|     997.00|     332.333333|                 2|
|    102|             2|     248.00|     124.000000|                 2|
|    103|             2|    2298.00|    1149.000000|                 1|
+-------+--------------+-----------+---------------+------------------+
```

---

## Feature 2: Time-Based Features

Extract time-dimension features such as most recent active date, number of active days, and active time-of-day:

```python
time_features = events.group_by("user_id") \
    .agg(
        F.max(F.to_date(F.col("event_date"))).alias("last_active_date"),
        F.min(F.to_date(F.col("event_date"))).alias("first_active_date"),
        F.datediff(
            F.to_date(F.lit("2024-01-16")),      # reference date for calculation
            F.max(F.to_date(F.col("event_date")))
        ).alias("days_since_last_active"),
        F.avg(F.col("hour")).alias("avg_active_hour"),
    )

time_features.show()
```

```Plain
+-------+----------------+-----------------+----------------------+-----------------+
|user_id|last_active_date|first_active_date|days_since_last_active|  avg_active_hour|
+-------+----------------+-----------------+----------------------+-----------------+
|    101|      2024-01-15|       2024-01-10|                     1|            14.75|
|    102|      2024-01-14|       2024-01-10|                     2|13.67            |
|    103|      2024-01-16|       2024-01-08|                     0|               13|
+-------+----------------+-----------------+----------------------+-----------------+
```

---

## Feature 3: Window Behavior Features

Use window functions to extract the most recent purchase information and cumulative spend:

```python
w_time = Window.partition_by("user_id").order_by(F.col("event_date").desc())
w_cumulative = Window.partition_by("user_id").order_by("event_date")

behavior_features = events.filter(F.col("event_type") == "purchase") \
    .with_column("purchase_rank",    F.rank().over(w_time)) \
    .with_column("cumulative_spend", F.sum("amount").over(w_cumulative)) \
    .filter(F.col("purchase_rank") == 1) \
    .select("user_id", "amount", "category", "cumulative_spend")

behavior_features.show()
```

```Plain
+-------+-------+-----------+----------------+
|user_id| amount|   category|cumulative_spend|
+-------+-------+-----------+----------------+
|    101| 599.00|electronics|          997.00|
|    102| 199.00|   clothing|          248.00|
|    103|1299.00|electronics|         2298.00|
+-------+-------+-----------+----------------+
```

---

## Feature 4: Categorical Feature Encoding

Convert categorical features (product category) into numeric values (spend amount per category):

```python
category_features = events.filter(F.col("event_type") == "purchase") \
    .group_by("user_id") \
    .agg(
        F.sum(F.iff(F.col("category") == "electronics",
                    F.col("amount"), F.lit(0))).alias("electronics_spend"),
        F.sum(F.iff(F.col("category") == "clothing",
                    F.col("amount"), F.lit(0))).alias("clothing_spend"),
        F.sum(F.iff(F.col("category") == "food",
                    F.col("amount"), F.lit(0))).alias("food_spend"),
    )

category_features.show()
```

```Plain
+-------+-----------------+--------------+----------+
|user_id|electronics_spend|clothing_spend|food_spend|
+-------+-----------------+--------------+----------+
|    101|           898.00|         99.00|      0.00|
|    102|             0.00|        199.00|     49.00|
|    103|          2298.00|          0.00|      0.00|
+-------+-----------------+--------------+----------+
```

---

## Feature 5: Merge Feature Tables

Join all feature dimensions into a single wide table:

```python
users = session.table("users")

all_features = stat_features \
    .join(time_features,    "user_id") \
    .join(category_features, "user_id") \
    .join(users.select("user_id", "age", "city"), "user_id")

all_features.show()
```

---

## Feature 6: Normalization (Min-Max Scaling)

Scale numeric features to the [0, 1] range.

First, compute the global min and max:

```python
stats = all_features.select(
    F.min("total_spend").alias("min_spend"),
    F.max("total_spend").alias("max_spend"),
).collect()[0]

min_val = float(stats["min_spend"])
max_val = float(stats["max_spend"])
```

Apply normalization:

```python
normalized = all_features.with_column(
    "total_spend_normalized",
    F.round(
        (F.col("total_spend") - F.lit(min_val)) / F.lit(max_val - min_val),
        4
    )
)

normalized.select("user_id", "total_spend", "total_spend_normalized").show()
```

```Plain
+-------+-----------+----------------------+
|user_id|total_spend|total_spend_normalized|
+-------+-----------+----------------------+
|    101|     997.00|                0.3654|
|    102|     248.00|                0.0000|
|    103|    2298.00|                1.0000|
+-------+-----------+----------------------+
```

---

## Write to Feature Store

After feature engineering is complete, write the results to a feature table for training:

```python
all_features.write.save_as_table("user_features", mode="overwrite")
print(f"Feature table row count: {session.table('user_features').count()}")
```

You can also create a Dynamic Table so that features refresh automatically as the source data changes:

```python
all_features.create_or_replace_dynamic_table(
    "user_features_auto",
    lag="1 hour",
    warehouse="default"
)
```

---

## Export Features for Model Training

Once the feature table is written, convert it to a pandas DataFrame for direct use in model training.

Read features from the Lakehouse:

```python
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier

df = session.table("user_features").to_pandas()
```

Select numeric feature columns:

```python
feature_cols = [
    "purchase_count", "total_spend", "avg_order_value",
    "days_since_last_active", "electronics_spend", "clothing_spend",
    "food_spend", "age"
]
X = df[feature_cols].fillna(0)
```

The target variable `y` requires a label column you prepare separately (e.g., `df["label"]`).

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [Zettapark DataFrame API Guide](zettapark-dataframe-guide.md) | Basic DataFrame operations |
| [Zettapark Functions Reference](zettapark-functions-guide.md) | Window functions and aggregation functions in detail |
| [Zettapark Dynamic Table Guide](zettapark-dynamic-table-guide.md) | Automatic feature refresh |
| [Credit Scoring with Zettapark and Python ML Libraries](credit-scoring-with-zettapark.md) | End-to-end ML scenario example |
