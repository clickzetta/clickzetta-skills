# Studio Python Task Development Guide (ZettaPark)

Studio Python tasks let you run Python scripts within the Lakehouse scheduling system, reading and writing Lakehouse data via the ZettaPark DataFrame API. They are suitable for scenarios that are difficult to express in SQL: quantile scoring, complex business rule mapping, and multi-step data processing workflows.

This article uses **RFM customer segmentation + marketing label generation** as an example to demonstrate the complete workflow from table creation to script writing to scheduled execution, including how to use task parameters. The script is self-contained — paste it directly into a Studio task and run it without any additional setup. All code has been verified through actual `cz-cli task execute` execution.

---

## Core Mechanism

**Python Task execution**: Studio runs the script's top-level code directly; it does not automatically call a `main()` function. All top-level statements in the script are executed in order, and `print()` output is written to the task log.

**ZettaPark Session creation**: Python tasks run in a Studio-managed environment where connection information is injected via `clickzetta_dbutils` — no need to hardcode usernames or passwords:

```python
from clickzetta_dbutils import get_active_lakehouse_engine
from clickzetta.zettapark.session import Session
from urllib.parse import urlparse, parse_qs

engine = get_active_lakehouse_engine(schema="your_schema")
url_str = str(engine.url)
parsed = urlparse(url_str.replace('clickzetta://', 'https://'))
params = parse_qs(parsed.query)
parts = parsed.hostname.split('.', 1)

session = Session.builder.configs({
    "service":     parts[1],           # cn-shanghai-alicloud.api.clickzetta.com
    "instance":    parts[0],           # instance ID, automatically extracted from URL
    "magic_token": params['magic_token'][0],
    "workspace":   parsed.path.lstrip('/'),
    "schema":      params.get('schema', ['public'])[0],
    "vcluster":    params.get('virtualcluster', ['default'])[0],
}).getOrCreate()
```

> ⚠️ **Note**: The `Session` object does not have a `get_current_database()` method. Use `get_current_catalog()` and `get_current_schema()` instead.

**Task parameters**: Studio supports referencing parameters in scripts using `'${param_name}'`, which are automatically replaced with actual values at runtime:

```python
base_date = '${base_date}'   # replaced with the actual date at runtime, e.g. 2024-12-31
```

**There are two ways to configure parameter values**:

- **Studio UI**: Click the **Parameters** button on the right side of the task editor; the system automatically detects `${base_date}` and assigns it a value (e.g., `$[yyyy-MM-dd]`)
- **cz-cli**: Pass a JSON object via `--params` in `save-content`:

```bash
cz-cli task save-content my_task --file task.py \
  --params '{"base_date": "$[yyyy-MM-dd]"}' \
  --profile <your-profile>
```

**Runtime parameter substitution rules**:
- **Scheduled run**: The system automatically computes and substitutes based on the configured expression, e.g., `$[yyyy-MM-dd]` is replaced with today's date
- **Ad-hoc execution**: The configured expression does not take effect; you must specify the value manually via `--param`, or enter it in the Studio UI dialog

```bash
# Manually specify parameter values for ad-hoc execution
cz-cli task execute my_task --param "base_date=2024-12-31" --profile <your-profile>
```

---

## Scenario: RFM Customer Segmentation + Marketing Labels

**What is RFM**: The most commonly used customer value segmentation model in e-commerce and retail, based on three dimensions:
- **R (Recency)**: Days since the last purchase — smaller is better
- **F (Frequency)**: Number of purchases — more is better
- **M (Monetary)**: Total spending amount — higher is better

**Why use Python instead of SQL**: Quantile scoring requires first computing global quantiles and then scoring each row. SQL's `NTILE` window function can do this, but the segmentation rule mapping (Champions/Loyal/At Risk, etc.) and marketing copy generation are more intuitive and maintainable in Python.

### Complete Script

```python
from clickzetta_dbutils import get_active_lakehouse_engine
from clickzetta.zettapark.session import Session
from clickzetta.zettapark import functions as F
from urllib.parse import urlparse, parse_qs
import datetime

# ── Task parameters ───────────────────────────────────────────────────────
# Studio schedule config: base_date = $[yyyy-MM-dd]  (today's date each time)
# cz-cli ad-hoc execution: --param "base_date=2024-12-31"
base_date = '${base_date}'
print(f"RFM base date: {base_date}")

# ── 1. Create ZettaPark Session ───────────────────────────────────────────
engine = get_active_lakehouse_engine(schema="zettapark_demo")
url_str = str(engine.url)
parsed = urlparse(url_str.replace('clickzetta://', 'https://'))
params = parse_qs(parsed.query)
parts = parsed.hostname.split('.', 1)

session = Session.builder.configs({
    "service":     parts[1],
    "instance":    parts[0],
    "magic_token": params['magic_token'][0],
    "workspace":   parsed.path.lstrip('/'),
    "schema":      params.get('schema', ['public'])[0],
    "vcluster":    params.get('virtualcluster', ['default'])[0],
}).getOrCreate()

print(f"Session ready: {session.get_current_catalog()}.{session.get_current_schema()}")

# ── 2. Create tables and write test data (idempotent, auto-created on first run) ─
session.sql("CREATE SCHEMA IF NOT EXISTS zettapark_demo").collect()
session.sql("""
    CREATE TABLE IF NOT EXISTS zettapark_demo.doc_rfm_orders (
        order_id    BIGINT,
        customer_id BIGINT,
        amount      DOUBLE,
        order_date  DATE
    )
""").collect()

# Use connector to write row data (ZettaPark has no row-level write API)
conn = engine.raw_connection()
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM zettapark_demo.doc_rfm_orders")
if cursor.fetchone()[0] == 0:
    orders_data = [
        (1,  101, 299.00, datetime.date(2024, 11, 1)),
        (2,  101, 150.00, datetime.date(2024, 11, 15)),
        (3,  101,  89.00, datetime.date(2024, 12, 1)),
        (4,  101, 210.00, datetime.date(2024, 12, 20)),
        (5,  102, 450.00, datetime.date(2024, 6, 10)),
        (6,  102, 320.00, datetime.date(2024, 7, 5)),
        (7,  103,  35.00, datetime.date(2024, 12, 28)),
        (8,  104, 180.00, datetime.date(2024, 9, 1)),
        (9,  104, 220.00, datetime.date(2024, 9, 15)),
        (10, 104, 190.00, datetime.date(2024, 10, 1)),
        (11, 104, 250.00, datetime.date(2024, 10, 20)),
        (12, 104, 300.00, datetime.date(2024, 11, 5)),
        (13, 105,  25.00, datetime.date(2024, 1, 10)),
        (14, 106, 500.00, datetime.date(2024, 12, 25)),
        (15, 106, 480.00, datetime.date(2024, 12, 26)),
        (16, 107,  60.00, datetime.date(2024, 8, 1)),
        (17, 107,  55.00, datetime.date(2024, 8, 20)),
        (18, 108, 120.00, datetime.date(2024, 11, 10)),
        (19, 109, 999.00, datetime.date(2024, 12, 30)),
        (20, 110,  40.00, datetime.date(2024, 3, 15)),
    ]
    cursor.executemany(
        "INSERT INTO zettapark_demo.doc_rfm_orders VALUES (?, ?, ?, ?)",
        orders_data
    )
    print(f"Wrote {len(orders_data)} order records")
else:
    print("Order data already exists, skipping write")
cursor.close()
conn.close()

# ── 3. Compute raw RFM metrics ────────────────────────────────────────────
orders = session.table("zettapark_demo.doc_rfm_orders")
print(f"Total order rows: {orders.count()}")

rfm_raw = (
    orders
    .group_by("customer_id")
    .agg(
        F.expr(f"DATEDIFF(DATE '{base_date}', MAX(order_date))").alias("recency"),
        F.count("order_id").alias("frequency"),
        F.sum("amount").alias("monetary"),
    )
)

# Convert to pandas for quantile scoring
df = rfm_raw.to_pandas()
print(f"\nRaw RFM metrics ({len(df)} customers):")
print(df.sort_values('customer_id').to_string(index=False))

# ── 4. Quantile scoring (1-3 points, 3 is best) ───────────────────────────
r_33 = df['recency'].quantile(0.33)
r_66 = df['recency'].quantile(0.66)
f_33 = df['frequency'].quantile(0.33)
f_66 = df['frequency'].quantile(0.66)
m_33 = df['monetary'].quantile(0.33)
m_66 = df['monetary'].quantile(0.66)

def score_r(v):
    # Recency: smaller is better, so quantiles are reversed
    if v <= r_33: return 3
    if v <= r_66: return 2
    return 1

def score_fm(v, p33, p66):
    if v >= p66: return 3
    if v >= p33: return 2
    return 1

df['r_score']   = df['recency'].apply(score_r)
df['f_score']   = df['frequency'].apply(lambda v: score_fm(v, f_33, f_66))
df['m_score']   = df['monetary'].apply(lambda v: score_fm(v, m_33, m_66))
df['rfm_total'] = df['r_score'] + df['f_score'] + df['m_score']

# ── 5. Segmentation rules + marketing labels ──────────────────────────────
def classify(row):
    r, f, m = row['r_score'], row['f_score'], row['m_score']
    if r == 3 and f == 3 and m == 3:
        return 'Champions',     'High-value loyal customers; prioritize new product launches and member-exclusive benefits'
    if r >= 2 and f >= 2 and m >= 2:
        return 'Loyal',         'Loyal customers; push points redemption and repeat purchase offers'
    if r == 3 and f <= 2:
        return 'New Customers', 'New customers; send welcome gift and first-purchase coupon'
    if r <= 1 and f >= 2 and m >= 2:
        return 'At Risk',       'High-value churn warning; send win-back offers and exclusive discounts'
    if r <= 1 and f <= 1:
        return 'Lost',          'Churned customers; low-cost outreach or abandon'
    return 'Potential',         'Potential customers; push bestsellers and limited-time promotions'

df[['segment', 'action']] = df.apply(classify, axis=1, result_type='expand')

print("\nRFM scores and segmentation results:")
print(df[['customer_id', 'recency', 'frequency', 'monetary',
          'r_score', 'f_score', 'm_score', 'segment', 'action']].to_string(index=False))

# ── 6. Write back to Lakehouse ────────────────────────────────────────────
result_df = session.create_dataframe(df[[
    'customer_id', 'recency', 'frequency', 'monetary',
    'r_score', 'f_score', 'm_score', 'rfm_total', 'segment', 'action'
]])
result_df.write.mode("overwrite").save_as_table("zettapark_demo.doc_rfm_result")
print(f"\nResults written to zettapark_demo.doc_rfm_result ({len(df)} rows)")

# ── 7. Segment summary ────────────────────────────────────────────────────
summary = (
    session.table("zettapark_demo.doc_rfm_result")
    .group_by("segment")
    .agg(
        F.count("customer_id").alias("customer_count"),
        F.round(F.avg("monetary"), 2).alias("avg_monetary"),
    )
    .sort(F.col("avg_monetary").desc())
)
print("\nSegment summary:")
summary.show()

session.close()
```

### Creating and Executing the Task

**Studio UI**

1. Go to **Data Development → New Task**, select **Python** type, and enter a task name
2. Paste the script above into the editor
3. Click the **Parameters** button on the right; the system automatically detects `${base_date}` and assigns it the value `$[yyyy-MM-dd]` (today's date)
4. Click the **Schedule** button, configure the VCluster (select general-purpose `DEFAULT`) and Cron expression (e.g., `0 2 * * *`)
5. Click **Publish**, then click **Run** → enter `base_date=2024-12-31` in the dialog to verify

**cz-cli** (suitable for CI/CD or bulk management scenarios; see [Studio Task Development and Operations](cz-cli-studio-tasks.md))

```bash
# Create the task
cz-cli task create rfm_segmentation --type python --profile <your-profile>

# Upload the script and configure parameters (base_date takes today's date)
cz-cli task save-content rfm_segmentation --file rfm_task.py \
  --params '{"base_date": "$[yyyy-MM-dd]"}' \
  --profile <your-profile>

# Configure scheduling (run at 2 AM every day)
cz-cli task save-config rfm_segmentation --vcluster default --retry-count 1 --profile <your-profile>
cz-cli task save-cron rfm_segmentation --cron "0 2 * * *" --profile <your-profile>

# Publish and run a one-time execution to verify
cz-cli task online rfm_segmentation -y --profile <your-profile>
cz-cli task execute rfm_segmentation --param "base_date=2024-12-31" --profile <your-profile>
```

### Execution Results

```
RFM base date: 2024-12-31
Session ready: quick_start.zettapark_demo
Wrote 20 order records
Total order rows: 20

Raw RFM metrics (10 customers):
 customer_id  recency  frequency  monetary
         101       11          4     748.0
         102      179          2     770.0
         103        3          1      35.0
         104       56          5    1140.0
         105      356          1      25.0
         106        5          2     980.0
         107      133          2     115.0
         108       51          1     120.0
         109        1          1     999.0
         110      291          1      40.0

RFM scores and segmentation results:
 customer_id  recency  frequency  monetary  r_score  f_score  m_score        segment                          action
         101       11          4     748.0        2        3        2          Loyal          Loyal customers; push points redemption and repeat purchase offers
         102      179          2     770.0        1        3        3        At Risk    High-value churn warning; send win-back offers and exclusive discounts
         103        3          1      35.0        3        2        1  New Customers        New customers; send welcome gift and first-purchase coupon
         104       56          5    1140.0        2        3        3          Loyal          Loyal customers; push points redemption and repeat purchase offers
         105      356          1      25.0        1        2        1      Potential      Potential customers; push bestsellers and limited-time promotions
         106        5          2     980.0        3        3        3      Champions  High-value loyal customers; prioritize new product launches and member-exclusive benefits
         107      133          2     115.0        1        3        2        At Risk    High-value churn warning; send win-back offers and exclusive discounts
         108       51          1     120.0        2        2        2          Loyal          Loyal customers; push points redemption and repeat purchase offers
         109        1          1     999.0        3        2        3          Loyal          Loyal customers; push points redemption and repeat purchase offers
         110      291          1      40.0        1        2        1      Potential      Potential customers; push bestsellers and limited-time promotions

Results written to zettapark_demo.doc_rfm_result (10 rows)

Segment summary:
---------------------------------------------------------------------------
|"SEGMENT"      |"CUSTOMER_COUNT"|"AVG_MONETARY"|
---------------------------------------------------------------------------
|Champions      |1               |980.0         |
|Loyal          |4               |751.75        |
|At Risk        |2               |442.5         |
|New Customers  |1               |35.0          |
|Potential      |2               |32.5          |
---------------------------------------------------------------------------
```

Verify the written results:

```sql
SELECT segment, customer_count, avg_monetary
FROM (
    SELECT segment,
           COUNT(*) AS customer_count,
           ROUND(AVG(monetary), 2) AS avg_monetary
    FROM zettapark_demo.doc_rfm_result
    GROUP BY segment
)
ORDER BY avg_monetary DESC;
```

```
segment        customer_count  avg_monetary
Champions      1               980.00
Loyal          4               751.75
At Risk        2               442.50
New Customers  1               35.00
Potential      2               32.50
```

---

## Common Issues

**`AttributeError: 'Session' object has no attribute 'get_current_database'`**

`Session` does not have a `get_current_database()` method. Use `get_current_catalog()` instead.

**`python process interrupted exception`**

This is a Python task runtime error. The error message is in the Studio task instance log, not in `information_schema.job_history` (Python runtime errors do not go through the SQL engine). Open the task instance details in the Studio UI to view the full traceback.

**Memory exhaustion when `to_pandas()` is used with large data volumes**

`to_pandas()` pulls data into the Python process memory. For large data volumes (millions of rows or more), compute quantile scoring using SQL `PERCENTILE_CONT` or `NTILE` window functions on the Lakehouse side, and only write the scoring results back using `create_dataframe()`.

---

## Related Documentation

- [ZettaPark Python Library Usage Guide](lakehousepython-zettapark.md)
- [Task Parameter Syntax Reference](task_param_reference.md)
- [Studio Python Task Development Guide (Python Connector)](studio-python-task-connector.md)
- [Studio Task Development and Operations (cz-cli)](cz-cli-studio-tasks.md)
