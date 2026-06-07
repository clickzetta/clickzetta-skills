# ZettaPark API — Common Data Science Operations

> Source: https://www.yunqi.tech/documents/ZettaparkQuickStart
> **Python version**: 3.12 recommended (3.10 minimum). Install: `python3.12 -m venv .venv && pip install clickzetta_zettapark_python`

---

## Creating a Session

```python
from clickzetta.zettapark.session import Session
import os
from dotenv import load_dotenv

load_dotenv()

session = Session.builder.configs({
    "service":   os.environ["CLICKZETTA_SERVICE"],
    "instance":  os.environ["CLICKZETTA_INSTANCE"],
    "workspace": os.environ["CLICKZETTA_WORKSPACE"],
    "username":  os.environ["CLICKZETTA_USERNAME"],
    "password":  os.environ["CLICKZETTA_PASSWORD"],
    "vcluster":  os.environ["CLICKZETTA_VCLUSTER"],
    "schema":    os.environ.get("CLICKZETTA_SCHEMA", "public"),
    "hints": {
        "sdk.job.timeout": 300,
        "query_tag": "ds_notebook"
    }
}).create()
```

---

## Reading Data

```python
# Read an entire table
df = session.table("my_schema.orders")

# Execute a SQL query
df = session.sql("SELECT * FROM my_schema.orders WHERE amount > 100")

# Convert to pandas (small datasets)
pandas_df = df.to_pandas()

# Read large tables in batches (avoid OOM)
pandas_df = session.sql("""
    SELECT * FROM my_schema.events
    TABLESAMPLE ROW (1)   -- exact 1% sample
""").to_pandas()

# Get first N rows only
pandas_df = df.limit(10000).to_pandas()
```

---

## DataFrame Transformations

```python
from clickzetta.zettapark.functions import col, when, lit, sum as F_sum, count as F_count, avg as F_avg

# Filter
df_filtered = df.filter(col("amount") > 0)
df_filtered = df.filter((col("status") == "COMPLETED") & (col("amount") > 100))

# Select columns
df_selected = df.select("user_id", "amount", "order_date")

# Add columns
df = df.with_column("log_amount", col("amount").cast("double"))
df = df.with_column("is_high_value", when(col("amount") > 1000, 1).otherwise(0))

# Aggregate
agg_df = df.group_by("user_id").agg(
    F_sum("amount").as_("total_amount"),
    F_count("order_id").as_("order_cnt"),
    F_avg("amount").as_("avg_amount")
)

# JOIN
result = orders.join(users, orders["user_id"] == users["user_id"], "left")

# Sort
df_sorted = df.sort(col("amount").desc())
```

---

## Writing Data Back

```python
# Overwrite (common for feature table updates)
df.write.mode("overwrite").save_as_table("ds_workspace.features_v1")

# Append (common for prediction results)
df.write.mode("append").save_as_table("ds_workspace.predictions")

# Write a pandas DataFrame back
import pandas as pd
local_df = pd.DataFrame({"user_id": [1, 2], "score": [0.8, 0.6]})
session.create_dataframe(local_df).write.mode("overwrite") \
    .save_as_table("ds_workspace.model_scores")
```

---

## Integration with pandas / scikit-learn

```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier

# 1. Pull features from Lakehouse
features_df = session.sql("""
    SELECT user_id, total_amount_30d, order_cnt_30d,
           active_days, avg_amount_30d, label
    FROM ds_workspace.features_final
""").to_pandas()

# 2. Local processing
X = features_df.drop(["user_id", "label"], axis=1)
y = features_df["label"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2)

# 3. Train model
model = GradientBoostingClassifier(n_estimators=100)
model.fit(X_train, y_train)

# 4. Predict and write back
features_df["predicted_score"] = model.predict_proba(X_scaled)[:, 1]
session.create_dataframe(
    features_df[["user_id", "predicted_score"]]
).write.mode("overwrite").save_as_table("ds_workspace.predictions")

# 5. Save model
import joblib
joblib.dump(model, "models/gbm_model.pkl")
joblib.dump(scaler, "models/scaler.pkl")
```

---

## Notes

- `to_pandas()` pulls all data into local memory — always `TABLESAMPLE` or `LIMIT` large tables first
- `collect()` returns a list of Row objects; `to_pandas()` returns a DataFrame — use the latter for data science
- ZettaPark DataFrame operations are lazy — computation only triggers on `to_pandas()` / `collect()` / `show()` / `save_as_table()`
- Write results to a dedicated schema like `ds_workspace` to keep them isolated from production data
