# Studio Python Task Development Guide (Python Connector)

Studio Python tasks have `clickzetta-connector` built in. By calling `get_active_lakehouse_engine().raw_connection()`, you get a PEP 249-compliant connection object and can directly use cursor/executemany to execute SQL and perform bulk writes.

This article uses **user behavior event writing + funnel analysis** as an example to demonstrate the complete development workflow, including how to use task parameters. The script is self-contained — paste it directly into a Studio task and run it without any additional setup. All code has been verified through actual `cz-cli task execute` execution.

---

## Core Mechanism

Getting a connector connection in a Python task takes just two lines:

```python
from clickzetta_dbutils import get_active_lakehouse_engine

engine = get_active_lakehouse_engine(schema="your_schema")
conn = engine.raw_connection()   # underlying clickzetta connector connection
cursor = conn.cursor()
```

`get_active_lakehouse_engine()` automatically builds an engine from the connection information injected by the Studio runtime — no need to hardcode usernames or passwords. `raw_connection()` returns the underlying clickzetta connector connection, which supports the full PEP 249 interface: `execute()`, `executemany()`, `fetchall()`, `fetchmany()`, `cursor.description`, etc.

> ⚠️ **Note**: Singdata Lakehouse does not support transactions. The `commit()` and `rollback()` interfaces are no-ops; each SQL statement is auto-committed.

**Task parameters**: Studio supports referencing parameters in scripts using `'${param_name}'`, which are automatically replaced with actual values at runtime. String parameters use quotes; numeric parameters do not:

```python
biz_date = '${biz_date}'    # string, replaced with 2024-12-01 at runtime
limit    = ${limit}         # numeric, replaced with 100 at runtime
```

**There are two ways to configure parameter values**:

- **Studio UI**: Click the **Parameters** button on the right side of the task editor; the system automatically detects `${biz_date}` and assigns it a value (e.g., `$[yyyy-MM-dd, -1d]`)
- **cz-cli**: Pass a JSON object via `--params` in `save-content`:

```bash
cz-cli task save-content my_task --file task.py \
  --params '{"biz_date": "$[yyyy-MM-dd, -1d]"}' \
  --profile <your-profile>
```

**Runtime parameter substitution rules**:
- **Scheduled run**: The system automatically computes and substitutes based on the configured expression, e.g., `$[yyyy-MM-dd, -1d]` is replaced with yesterday's date
- **Ad-hoc execution**: The configured expression does not take effect; you must specify the value manually via `--param`, or enter it in the Studio UI dialog

```bash
# Manually specify parameter values for ad-hoc execution
cz-cli task execute my_task --param "biz_date=2024-12-01" --profile <your-profile>
```

---

## Scenario: User Behavior Funnel Analysis (with Task Parameters)

Process the previous day's user behavior data every morning, using the task parameter `biz_date` to control which day's data is processed, and write results to a summary table.

### Complete Script

```python
import datetime
from clickzetta_dbutils import get_active_lakehouse_engine

# ── Task parameters ───────────────────────────────────────────────────────
# Studio schedule config: biz_date = $[yyyy-MM-dd, -1d]  (yesterday's date each time)
# cz-cli ad-hoc execution: --param "biz_date=2024-12-01"
biz_date = '${biz_date}'
print(f"Processing date: {biz_date}")

# ── 1. Get connection ─────────────────────────────────────────────────────
engine = get_active_lakehouse_engine(schema="doc_connector_demo")
conn = engine.raw_connection()
cursor = conn.cursor()
print("Connection successful")

# ── 2. Create tables (idempotent, auto-created on first run) ──────────────
cursor.execute("CREATE SCHEMA IF NOT EXISTS doc_connector_demo")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS doc_connector_demo.doc_events (
        event_id   BIGINT,
        user_id    BIGINT,
        event_type STRING,
        page       STRING,
        duration   INT,
        event_time TIMESTAMP
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS doc_connector_demo.doc_funnel_daily (
        biz_date       STRING,
        step1_view     BIGINT,
        step2_cart     BIGINT,
        step3_checkout BIGINT,
        run_time       TIMESTAMP
    )
""")
print("Tables created")

# ── 3. Write event data for the day (simulating upstream push) ────────────
events = [
    (1,  101, 'view',     'home',     30,  datetime.datetime(2024, 12, 1, 10, 0, 0)),
    (2,  101, 'click',    'product',  5,   datetime.datetime(2024, 12, 1, 10, 0, 35)),
    (3,  102, 'view',     'home',     45,  datetime.datetime(2024, 12, 1, 10, 1, 0)),
    (4,  102, 'view',     'product',  120, datetime.datetime(2024, 12, 1, 10, 2, 0)),
    (5,  102, 'click',    'cart',     8,   datetime.datetime(2024, 12, 1, 10, 4, 0)),
    (6,  103, 'view',     'home',     15,  datetime.datetime(2024, 12, 1, 10, 5, 0)),
    (7,  103, 'view',     'product',  200, datetime.datetime(2024, 12, 1, 10, 5, 20)),
    (8,  103, 'click',    'cart',     6,   datetime.datetime(2024, 12, 1, 10, 8, 0)),
    (9,  103, 'click',    'checkout', 12,  datetime.datetime(2024, 12, 1, 10, 8, 10)),
    (10, 104, 'view',     'home',     10,  datetime.datetime(2024, 12, 1, 10, 9, 0)),
]
cursor.executemany(
    "INSERT INTO doc_connector_demo.doc_events VALUES (?, ?, ?, ?, ?, ?)",
    events
)
print(f"Wrote {len(events)} event records")

# ── 4. Query event statistics for the specified date ─────────────────────
cursor.execute(f"""
    SELECT event_type,
           COUNT(*)      AS cnt,
           AVG(duration) AS avg_duration
    FROM doc_connector_demo.doc_events
    WHERE DATE(event_time) = DATE '{biz_date}'
    GROUP BY event_type
    ORDER BY cnt DESC
""")

col_names = [col[0] for col in cursor.description]
rows = cursor.fetchall()
print(f"\n{biz_date} event statistics (columns: {col_names}):")
for row in rows:
    print(f"  {row[0]:10s}  count={row[1]}  avg_duration={row[2]:.1f}s")

# ── 5. Funnel analysis ────────────────────────────────────────────────────
cursor.execute(f"""
    SELECT
        COUNT(DISTINCT CASE WHEN event_type = 'view'                        THEN user_id END) AS step1_view,
        COUNT(DISTINCT CASE WHEN event_type = 'click' AND page = 'cart'     THEN user_id END) AS step2_cart,
        COUNT(DISTINCT CASE WHEN event_type = 'click' AND page = 'checkout' THEN user_id END) AS step3_checkout
    FROM doc_connector_demo.doc_events
    WHERE DATE(event_time) = DATE '{biz_date}'
""")

row = cursor.fetchone()
view, cart, checkout = row[0], row[1], row[2]
print(f"\nFunnel analysis ({biz_date}):")
print(f"  Viewed homepage:  {view} users")
if view > 0:
    print(f"  Added to cart:    {cart} users  (conversion rate {cart/view*100:.0f}%)")
    print(f"  Reached checkout: {checkout} users  (conversion rate {checkout/view*100:.0f}%)")

# ── 6. fetchmany batch reading ────────────────────────────────────────────
cursor.execute(f"""
    SELECT event_id, user_id, event_type, page, duration
    FROM doc_connector_demo.doc_events
    WHERE DATE(event_time) = DATE '{biz_date}'
    ORDER BY event_id
""")
print(f"\nfetchmany batch reading (3 rows per batch):")
while True:
    batch = cursor.fetchmany(3)
    if not batch:
        break
    print(f"  This batch: {len(batch)} rows: event_id {batch[0][0]} ~ {batch[-1][0]}")

# ── 7. Write summary results ──────────────────────────────────────────────
cursor.executemany(
    "INSERT INTO doc_connector_demo.doc_funnel_daily VALUES (?, ?, ?, ?, ?)",
    [(biz_date, view, cart, checkout, datetime.datetime.now())]
)
print(f"\nSummary results written to doc_funnel_daily")

cursor.close()
conn.close()
print("Done")
```

### Creating and Executing the Task

**Studio UI**

1. Go to **Data Development → New Task**, select **Python** type, and enter a task name
2. Paste the script above into the editor
3. Click the **Parameters** button on the right; the system automatically detects `${biz_date}` and assigns it the value `$[yyyy-MM-dd, -1d]` (yesterday's date)
4. Click the **Schedule** button, configure the VCluster (select general-purpose `DEFAULT`) and Cron expression (e.g., `0 3 * * *`)
5. Click **Publish**, then click **Run** → enter `biz_date=2024-12-01` in the dialog to verify

**cz-cli** (suitable for CI/CD or bulk management scenarios; see [Studio Task Development and Operations](cz-cli-studio-tasks.md))

```bash
# Create the task
cz-cli task create connector_funnel --type python --profile <your-profile>

# Upload the script and configure parameters (biz_date takes yesterday's date)
cz-cli task save-content connector_funnel --file connector_funnel.py \
  --params '{"biz_date": "$[yyyy-MM-dd, -1d]"}' \
  --profile <your-profile>

# Configure scheduling (run at 3 AM every day)
cz-cli task save-config connector_funnel --vcluster default --retry-count 1 --profile <your-profile>
cz-cli task save-cron connector_funnel --cron "0 3 * * *" --profile <your-profile>

# Publish and run a one-time execution to verify
cz-cli task online connector_funnel -y --profile <your-profile>
cz-cli task execute connector_funnel --param "biz_date=2024-12-01" --profile <your-profile>
```

### Execution Results

```
Processing date: 2024-12-01
Connection successful
Tables created
Wrote 10 event records

2024-12-01 event statistics (columns: ['event_type', 'cnt', 'avg_duration']):
  view        count=6  avg_duration=70.0s
  click       count=4  avg_duration=7.8s

Funnel analysis (2024-12-01):
  Viewed homepage:  4 users
  Added to cart:    2 users  (conversion rate 50%)
  Reached checkout: 1 users  (conversion rate 25%)

fetchmany batch reading (3 rows per batch):
  This batch: 3 rows: event_id 1 ~ 3
  This batch: 3 rows: event_id 4 ~ 6
  This batch: 3 rows: event_id 7 ~ 9
  This batch: 1 rows: event_id 10 ~ 10

Summary results written to doc_funnel_daily
Done
```

Verify the written results:

```sql
SELECT biz_date, step1_view, step2_cart, step3_checkout
FROM doc_connector_demo.doc_funnel_daily
ORDER BY biz_date DESC
LIMIT 5;
```

```
biz_date    step1_view  step2_cart  step3_checkout
2024-12-01  4           2           1
```

---

## Quick Reference for Common Interfaces

| Interface | Description |
|---|---|
| `cursor.execute(sql)` | Execute a single SQL statement |
| `cursor.executemany(sql, data)` | Bulk write; `data` is a list of tuples |
| `cursor.fetchall()` | Fetch all result rows |
| `cursor.fetchone()` | Fetch a single row |
| `cursor.fetchmany(n)` | Fetch in batches of n rows; returns `[]` when results are exhausted |
| `cursor.description` | Column metadata; `col[0]` is the column name |

**`executemany` placeholder**: Use `?` to indicate parameter positions, bound to tuple values in order. Pass `datetime.datetime` objects for TIMESTAMP columns and `datetime.date` objects for DATE columns.

---

## Comparison with ZettaPark

| | Python Connector | ZettaPark |
|---|---|---|
| Interface style | PEP 249 cursor/SQL | DataFrame chained operations |
| Suitable for | Bulk writes, precise SQL control | Data processing, aggregation, pandas integration |
| Write method | `executemany()` | `create_dataframe().write.save_as_table()` |
| Read method | `fetchall()` / `fetchmany()` | `to_pandas()` / `show()` |
| Dependency | `clickzetta-connector` (built-in) | `clickzetta-zettapark-python` (built-in) |

The two can be mixed in the same Python task: use the connector to write raw data, and use ZettaPark for aggregation analysis.

---

## Related Documentation

- [Python Connector SDK](python_reference/connector.md)
- [Task Parameter Syntax Reference](task_param_reference.md)
- [Studio Python Task Development Guide (ZettaPark)](studio-python-task-zettapark.md)
- [Studio Task Development and Operations (cz-cli)](cz-cli-studio-tasks.md)
